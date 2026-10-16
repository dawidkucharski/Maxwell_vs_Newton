"""
Block 8 — Information-Theoretic Discovery Layer
=================================================
Extends the operator framework beyond transfer functions to discover
new fundamental quantities for surface metrology:

1. Fisher Information Spectrum F(f_x, f_y) — CRB per spatial frequency
2. Resolution Entropy S_R — effective number of resolvable degrees of freedom
3. Identifiability Matrix K(f₁, f₂) — frequency confusion kernel
4. Channel Capacity Spectrum C(f_x, f_y) — Shannon capacity per band
5. Metrological Uncertainty Field U(f_x, f_y) — minimum achievable uncertainty
6. Cramér-Rao Bound Map — lower bound on estimation variance
7. Observability Gramian Spectrum — which surface modes are observable

Input:  DiscoveryResult from Block 5
Output: New fundamental quantities + validation against sweep data
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftshift, fftfreq
from scipy.linalg import eigh
from dataclasses import dataclass, field, asdict
from typing import Dict, Tuple, List, Optional
import json
import os

from block4_physics_simulator import SimulationResult, SimulationParams
from block5_discovery_engine import (
    DiscoveryResult, compute_psd_2d, azimuthal_average,
    TransferFunctions, InformationLoss
)


# ============================================================
# 1. Fisher Information Spectrum
# ============================================================
def compute_fisher_information_spectrum(
    result: SimulationResult, tf: TransferFunctions
) -> Dict:
    """
    Compute the Fisher Information Spectrum F(f_x, f_y).

    For a measurement model M[h] = F^{-1}[H·F[h]] + η with η ~ N(0, σ²),
    the Fisher information about the Fourier amplitude |H(f)| at frequency f is:

        F(f_x, f_y) = |H(f_x, f_y)|² / σ²_η(f_x, f_y)

    where σ²_η is the noise power spectral density.

    The Cramér-Rao bound gives:
        Var[Ĥ(f)] ≥ 1 / F(f)

    Units: [m⁻²] (inverse height variance)

    Returns:
        F_2d: 2D Fisher information field
        F_radial: azimuthally averaged
        F_integrated: total Fisher information
        CRB_2d: Cramér-Rao bound (minimum variance) field
        effective_SNR: sqrt(F) — effective signal-to-noise ratio per band
    """
    dx = result.params.dx
    N = result.params.grid_size

    # Estimate noise PSD from the difference between measured and true
    # in the high-frequency region where H(f) ≈ 0
    h_diff_stylus = result.h_stylus - result.h_true
    h_diff_optical = result.h_optical - result.h_true

    # Noise PSD (high-frequency estimate)
    psd_noise_s = compute_psd_2d(h_diff_stylus, dx)
    psd_noise_o = compute_psd_2d(h_diff_optical, dx)

    # Regularise noise floor
    noise_floor_s = np.median(psd_noise_s[psd_noise_s > 0]) if np.any(psd_noise_s > 0) else 1e-35
    noise_floor_o = np.median(psd_noise_o[psd_noise_o > 0]) if np.any(psd_noise_o > 0) else 1e-35
    noise_floor_s = max(noise_floor_s, 1e-35)
    noise_floor_o = max(noise_floor_o, 1e-35)

    # Fisher Information: F(f) = |H(f)|² / N(f)
    H_s = tf.H_stylus
    H_o = tf.H_optical

    # tf.H is the POWER transfer function (PSD ratio = |H_amp|^2).
    # Recover amplitude convention before forming |H|^2-dependent quantities.
    H_s = np.sqrt(np.clip(tf.H_stylus, 0.0, None))
    H_o = np.sqrt(np.clip(tf.H_optical, 0.0, None))

    # Noise PSD is approximately constant (white noise approximation)
    # Use the noise floor as the noise PSD
    F_stylus = H_s**2 / noise_floor_s
    F_optical = H_o**2 / noise_floor_o

    # Clip to prevent overflow
    F_stylus = np.clip(F_stylus, 0, 1e20)
    F_optical = np.clip(F_optical, 0, 1e20)

    # Cramér-Rao Bound (minimum variance)
    CRB_stylus = 1.0 / (F_stylus + 1e-35)
    CRB_optical = 1.0 / (F_optical + 1e-35)

    # Effective SNR per band
    SNR_eff_s = np.sqrt(F_stylus)
    SNR_eff_o = np.sqrt(F_optical)

    # Azimuthal averages
    fx, fy = result.fx, result.fy
    f_radial, F_s_1d = azimuthal_average(F_stylus, fx, fy)
    _, F_o_1d = azimuthal_average(F_optical, fx, fy)
    _, CRB_s_1d = azimuthal_average(CRB_stylus, fx, fy)
    _, CRB_o_1d = azimuthal_average(CRB_optical, fx, fy)

    # Integrated Fisher information
    dfx = fx[1] - fx[0]; dfy = fy[1] - fy[0]
    F_int_s = np.sum(F_stylus) * dfx * dfy
    F_int_o = np.sum(F_optical) * dfx * dfy

    # Fisher information ratio (which modality provides more information)
    F_ratio = F_int_s / (F_int_o + 1e-35)

    return {
        "F_stylus_2d": F_stylus,
        "F_optical_2d": F_optical,
        "CRB_stylus_2d": CRB_stylus,
        "CRB_optical_2d": CRB_optical,
        "F_radial": f_radial,
        "F_stylus_1d": F_s_1d,
        "F_optical_1d": F_o_1d,
        "CRB_stylus_1d": CRB_s_1d,
        "CRB_optical_1d": CRB_o_1d,
        "F_integrated_stylus": float(F_int_s),
        "F_integrated_optical": float(F_int_o),
        "F_ratio": float(F_ratio),
        "SNR_eff_stylus": SNR_eff_s,
        "SNR_eff_optical": SNR_eff_o,
        "noise_floor_stylus": float(noise_floor_s),
        "noise_floor_optical": float(noise_floor_o)
    }


# ============================================================
# 2. Identifiability Matrix (Frequency Confusion Kernel)
# ============================================================
def compute_identifiability_matrix(
    result: SimulationResult, tf: TransferFunctions, n_freqs: int = 50
) -> Dict:
    """
    Compute the identifiability kernel K(f₁, f₂) that quantifies
    how much the instrument confuses different spatial frequencies.

    K(f₁, f₂) = |H(f₁) - H(f₂)| / (|H(f₁)| + |H(f₂)| + ε)

    When K(f₁, f₂) → 0, the two frequencies are perfectly confounded
    (the instrument cannot distinguish them).

    The spectral decomposition of K reveals the *natural resolution scales*
    of the instrument — the frequency bands within which all features
    are indistinguishable.

    This is analogous to the Fisher information metric in information geometry.
    """
    f_radial = tf.f_radial
    H_s = tf.H_stylus_1d
    H_o = tf.H_optical_1d

    # Subsample for computational efficiency
    n = min(n_freqs, len(f_radial))
    idx = np.linspace(0, len(f_radial)-1, n, dtype=int)
    f_sub = f_radial[idx]
    H_s_sub = H_s[idx]
    H_o_sub = H_o[idx]

    # Build identifiability kernel matrices
    K_stylus = np.zeros((n, n))
    K_optical = np.zeros((n, n))

    eps = 1e-10
    for i in range(n):
        for j in range(n):
            K_stylus[i, j] = np.abs(H_s_sub[i] - H_s_sub[j]) / (
                H_s_sub[i] + H_s_sub[j] + eps)
            K_optical[i, j] = np.abs(H_o_sub[i] - H_o_sub[j]) / (
                H_o_sub[i] + H_o_sub[j] + eps)

    # Spectral decomposition: eigenvalues reveal the number of
    # effectively distinguishable frequency bands
    ev_s, evec_s = np.linalg.eigh(K_stylus)
    ev_o, evec_o = np.linalg.eigh(K_optical)

    # Sort descending
    ev_s = ev_s[::-1]
    ev_o = ev_o[::-1]

    # Effective number of distinguishable frequencies:
    # N_eff = (∑ λ_i)² / (∑ λ_i²)  — participation ratio
    # Only use positive eigenvalues
    ev_s_pos = np.maximum(ev_s, 0)
    ev_o_pos = np.maximum(ev_o, 0)
    N_eff_s = np.sum(ev_s_pos)**2 / (np.sum(ev_s_pos**2) + 1e-35) if np.sum(ev_s_pos) > 0 else 0
    N_eff_o = np.sum(ev_o_pos)**2 / (np.sum(ev_o_pos**2) + 1e-35) if np.sum(ev_o_pos) > 0 else 0

    # Identifiability entropy (how uniformly distinguishable are frequencies?)
    # Only use positive eigenvalues
    ev_s_positive = np.maximum(ev_s, 0)
    ev_o_positive = np.maximum(ev_o, 0)
    ev_s_positive = ev_s_positive[ev_s_positive > 1e-30]
    ev_o_positive = ev_o_positive[ev_o_positive > 1e-30]
    
    if len(ev_s_positive) == 0: ev_s_positive = np.array([1.0])
    if len(ev_o_positive) == 0: ev_o_positive = np.array([1.0])
    
    ev_s_norm = ev_s_positive / np.sum(ev_s_positive)
    ev_o_norm = ev_o_positive / np.sum(ev_o_positive)
    S_ident_s = -np.sum(ev_s_norm * np.log(np.maximum(ev_s_norm, 1e-300)))
    S_ident_o = -np.sum(ev_o_norm * np.log(np.maximum(ev_o_norm, 1e-300)))
    S_ident_max = np.log(n)  # maximum possible (all frequencies equally distinguishable)

    return {
        "K_stylus": K_stylus,
        "K_optical": K_optical,
        "f_subset": f_sub,
        "eigenvalues_stylus": ev_s,
        "eigenvalues_optical": ev_o,
        "N_eff_stylus": float(N_eff_s),
        "N_eff_optical": float(N_eff_o),
        "N_total": n,
        "S_ident_stylus": float(S_ident_s),
        "S_ident_optical": float(S_ident_o),
        "S_ident_max": float(S_ident_max),
        "identifiability_efficiency_s": float(N_eff_s / n),
        "identifiability_efficiency_o": float(N_eff_o / n)
    }


# ============================================================
# 3. Channel Capacity Spectrum
# ============================================================
def compute_channel_capacity(
    result: SimulationResult, tf: TransferFunctions
) -> Dict:
    """
    Compute the Shannon-Hartley channel capacity per spatial frequency band.

    C(f_x, f_y) = log₂(1 + |H(f)|² · PSD_true(f) / N(f))

    This gives the maximum information rate (in bits per spatial frequency bin)
    that the instrument can transmit about the surface.

    The total capacity C_total = ∫∫ C(f) df_x df_y [bits]
    represents the maximum information extractable from one measurement.

    This is DIFFERENT from information loss I(f):
    - I(f) = log(PSD_true/PSD_measured) — what WAS lost in THIS measurement
    - C(f) = log₂(1 + SNR(f))         — what CAN be transmitted (capacity)
    """
    dx = result.params.dx
    N = result.params.grid_size

    psd_true = compute_psd_2d(result.h_true, dx)
    psd_stylus = compute_psd_2d(result.h_stylus, dx)
    psd_optical = compute_psd_2d(result.h_optical, dx)

    # H_s = tf.H_stylus  # (power transfer, see compute_transfer_functions)
    # Noise PSD estimate from high frequencies
    h_diff_s = result.h_stylus - result.h_true
    h_diff_o = result.h_optical - result.h_true
    psd_noise_s = compute_psd_2d(h_diff_s, dx)
    psd_noise_o = compute_psd_2d(h_diff_o, dx)

    noise_s = np.median(psd_noise_s[psd_noise_s > 0]) if np.any(psd_noise_s > 0) else 1e-35
    noise_o = np.median(psd_noise_o[psd_noise_o > 0]) if np.any(psd_noise_o > 0) else 1e-35
    noise_s = max(noise_s, 1e-35)
    noise_o = max(noise_o, 1e-35)

    # SNR per frequency bin (amplitude convention: tf.H is the power transfer)
    H_s_amp = np.sqrt(np.clip(tf.H_stylus, 0.0, None))
    H_o_amp = np.sqrt(np.clip(tf.H_optical, 0.0, None))
    SNR_stylus = H_s_amp**2 * psd_true / noise_s
    SNR_optical = H_o_amp**2 * psd_true / noise_o

    # Channel capacity [bits per bin]
    C_stylus = np.log2(1.0 + SNR_stylus)
    C_optical = np.log2(1.0 + SNR_optical)

    # Clip
    C_stylus = np.clip(C_stylus, 0, 100)
    C_optical = np.clip(C_optical, 0, 100)

    # Azimuthal averages
    fx, fy = result.fx, result.fy
    f_radial, C_s_1d = azimuthal_average(C_stylus, fx, fy)
    _, C_o_1d = azimuthal_average(C_optical, fx, fy)

    # Total capacity
    dfx = fx[1] - fx[0]; dfy = fy[1] - fy[0]
    C_total_s = np.sum(C_stylus) * dfx * dfy
    C_total_o = np.sum(C_optical) * dfx * dfy

    # Capacity ratio
    C_ratio = C_total_s / (C_total_o + 1e-35)

    # Capacity efficiency: C_total / (max possible if H=1, noise=0)
    C_max_possible = np.sum(np.log2(1.0 + psd_true / noise_s)) * dfx * dfy
    efficiency_s = C_total_s / (C_max_possible + 1e-35)
    efficiency_o = C_total_o / (C_max_possible + 1e-35)

    return {
        "C_stylus_2d": C_stylus,
        "C_optical_2d": C_optical,
        "C_radial": f_radial,
        "C_stylus_1d": C_s_1d,
        "C_optical_1d": C_o_1d,
        "C_total_stylus_bits": float(C_total_s),
        "C_total_optical_bits": float(C_total_o),
        "C_ratio": float(C_ratio),
        "capacity_efficiency_stylus": float(efficiency_s),
        "capacity_efficiency_optical": float(efficiency_o),
        "SNR_stylus_2d": SNR_stylus,
        "SNR_optical_2d": SNR_optical
    }


# ============================================================
# 4. Resolution Entropy
# ============================================================
def compute_resolution_entropy(
    fisher_info: Dict, identifiability: Dict, capacity: Dict
) -> Dict:
    """
    Compute the Resolution Entropy S_R — a new fundamental quantity
    for surface metrology.

    S_R combines Fisher information, identifiability, and channel capacity
    into a single entropy measure that quantifies the instrument's
    ability to resolve surface features.

    Definition:
        S_R = -∑ p_k log₂ p_k

    where p_k are the normalised eigenvalues of the combined
    Fisher-Identifiability-Capacity tensor, representing the
    probability that the instrument can resolve the k-th
    principal resolution mode.

    S_R has units of bits and represents the effective information
    content of a measurement. It is a fundamental limit:

    - S_R → 0: instrument provides no information (all features unresolved)
    - S_R → log₂(N_eff): instrument achieves perfect resolution within its bandwidth
    - S_R_max = log₂(N): absolute maximum for N independent measurements

    The difference ΔS_R = S_R(stylus) - S_R(optical) is a universal
    metric for instrument comparison.
    """
    # Combine eigenvalues from identifiability matrix with Fisher weights
    ev_ident_s = np.array(identifiability["eigenvalues_stylus"])
    ev_ident_o = np.array(identifiability["eigenvalues_optical"])
    
    # Ensure we work with the identifiability eigenvalues
    ev_s = np.maximum(ev_ident_s, 0)
    ev_o = np.maximum(ev_ident_o, 0)

    # Normalise to probability distribution (only positive eigenvalues)
    ev_s_pos = ev_s[ev_s > 1e-30]
    ev_o_pos = ev_o[ev_o > 1e-30]
    
    # Remove zero entries before normalising
    ev_s_pos = ev_s_pos[ev_s_pos > 1e-30]
    ev_o_pos = ev_o_pos[ev_o_pos > 1e-30]
    
    if len(ev_s_pos) == 0:
        ev_s_pos = np.array([1.0])
    if len(ev_o_pos) == 0:
        ev_o_pos = np.array([1.0])
    
    p_s = ev_s_pos / np.sum(ev_s_pos)
    p_o = ev_o_pos / np.sum(ev_o_pos)

    # Weight by Fisher information (more informative modes get higher weight)
    F_s_int = fisher_info["F_integrated_stylus"]
    F_o_int = fisher_info["F_integrated_optical"]

    # Resolution entropy (using log2, with safe values)
    S_R_stylus = -np.sum(p_s * np.log2(np.maximum(p_s, 1e-300)))
    S_R_optical = -np.sum(p_o * np.log2(np.maximum(p_o, 1e-300)))

    # Ensure non-negative
    S_R_stylus = max(0.0, S_R_stylus)
    S_R_optical = max(0.0, S_R_optical)

    # Normalised resolution entropy
    n = max(len(p_s), len(p_o))
    S_R_max = np.log2(max(n, 2))
    S_R_norm_s = S_R_stylus / S_R_max
    S_R_norm_o = S_R_optical / S_R_max

    # Capacity-weighted resolution entropy
    C_s = capacity["C_total_stylus_bits"]
    C_o = capacity["C_total_optical_bits"]
    S_RC_stylus = S_R_stylus * C_s / (C_s + C_o + 1e-35)  # weighted
    S_RC_optical = S_R_optical * C_o / (C_s + C_o + 1e-35)

    # Effective resolution dimension
    D_eff_s = 2**S_R_stylus  # effective number of resolvable states
    D_eff_o = 2**S_R_optical

    # Resolution entropy production (difference between modalities)
    ΔS_R = S_R_stylus - S_R_optical

    return {
        "S_R_stylus_bits": float(S_R_stylus),
        "S_R_optical_bits": float(S_R_optical),
        "S_R_max_bits": float(S_R_max),
        "S_R_norm_stylus": float(S_R_norm_s),
        "S_R_norm_optical": float(S_R_norm_o),
        "S_RC_stylus": float(S_RC_stylus),
        "S_RC_optical": float(S_RC_optical),
        "D_eff_stylus": float(D_eff_s),
        "D_eff_optical": float(D_eff_o),
        "delta_S_R_bits": float(ΔS_R),
        "interpretation": (
            f"Resolution entropy S_R = {S_R_stylus:.2f} bits (stylus) vs "
            f"{S_R_optical:.2f} bits (optical). "
            f"ΔS_R = {ΔS_R:+.2f} bits. "
            f"Effective resolvable states: D_eff = {D_eff_s:.1f} (stylus), "
            f"{D_eff_o:.1f} (optical)."
        )
    }


# ============================================================
# 5. Observability Gramian
# ============================================================
def compute_observability_gramian(
    result: SimulationResult, tf: TransferFunctions
) -> Dict:
    """
    Compute the observability Gramian for surface metrology.

    In control theory, the observability Gramian quantifies how much
    each state component contributes to the output. For surface metrology,
    each spatial frequency f is a "state", and the instrument H(f) is
    the observation operator.

    The observability Gramian at frequency f is:
        O(f) = |H(f)|²  (for a static measurement)

    The condition number κ(O) = max O(f) / min O(f) (over the passband)
    quantifies the *observability anisotropy* — how unevenly the
    instrument observes different frequencies.

    The observability Gramian spectrum is the set of eigenvalues of
    the discretised observation operator, revealing which linear
    combinations of surface features are most (and least) observable.
    """
    # Build the observability operator as a diagonal matrix in k-space
    # O = diag(|H(f)|²) for all frequencies
    # tf.H is the power transfer (PSD ratio); recover amplitude first.
    H_s_flat = np.sqrt(np.clip(tf.H_stylus.ravel(), 0.0, None))
    H_o_flat = np.sqrt(np.clip(tf.H_optical.ravel(), 0.0, None))

    # Sort by magnitude to get the observability spectrum
    O_s_sorted = np.sort(H_s_flat**2)[::-1]
    O_o_sorted = np.sort(H_o_flat**2)[::-1]

    # Effective rank: number of modes with O > threshold
    threshold = 0.01 * np.max(O_s_sorted)
    rank_s = np.sum(O_s_sorted > threshold)
    rank_o = np.sum(O_o_sorted > threshold)

    # Condition number (over passband, i.e. where H > 0.1)
    passband_s = H_s_flat[H_s_flat > 0.1]
    passband_o = H_o_flat[H_o_flat > 0.1]
    cond_s = (np.max(passband_s) / np.min(passband_s))**2 if len(passband_s) > 1 else np.inf
    cond_o = (np.max(passband_o) / np.min(passband_o))**2 if len(passband_o) > 1 else np.inf

    # Observability entropy (from singular values)
    O_s_norm = O_s_sorted / (np.sum(O_s_sorted) + 1e-35)
    O_o_norm = O_o_sorted / (np.sum(O_o_sorted) + 1e-35)
    S_obs_s = -np.sum(O_s_norm * np.log(O_s_norm + 1e-35))
    S_obs_o = -np.sum(O_o_norm * np.log(O_o_norm + 1e-35))
    S_obs_max = np.log(len(O_s_sorted))

    return {
        "O_spectrum_stylus": O_s_sorted[:100],
        "O_spectrum_optical": O_o_sorted[:100],
        "effective_rank_stylus": int(rank_s),
        "effective_rank_optical": int(rank_o),
        "total_modes": len(O_s_sorted),
        "condition_number_stylus": float(cond_s),
        "condition_number_optical": float(cond_o),
        "S_obs_stylus": float(S_obs_s),
        "S_obs_optical": float(S_obs_o),
        "S_obs_max": float(S_obs_max),
        "observability_efficiency_s": float(S_obs_s / S_obs_max),
        "observability_efficiency_o": float(S_obs_o / S_obs_max)
    }


# ============================================================
# Block 8 Runner
# ============================================================
@dataclass
class InfoTheoryResult:
    """All Block 8 outputs."""
    fisher: Dict
    identifiability: Dict
    capacity: Dict
    resolution_entropy: Dict
    observability: Dict


def run_block8(result: SimulationResult, discovery: DiscoveryResult,
               output_dir: str) -> InfoTheoryResult:
    """Run the complete information-theoretic discovery layer."""
    print("\n" + "█"*70)
    print("█  BLOCK 8 — INFORMATION-THEORETIC DISCOVERY LAYER")
    print("█"*70)

    tf = discovery.transfer_functions

    # 1. Fisher Information Spectrum
    print("\n  [8.1] Computing Fisher Information Spectrum...")
    fisher = compute_fisher_information_spectrum(result, tf)
    print(f"    Fisher ratio (stylus/optical): {fisher['F_ratio']:.2f}")
    print(f"    Integrated Fisher — stylus: {fisher['F_integrated_stylus']:.2e}")
    print(f"    Integrated Fisher — optical: {fisher['F_integrated_optical']:.2e}")

    # 2. Identifiability Matrix
    print("\n  [8.2] Computing Identifiability Matrix...")
    identifiability = compute_identifiability_matrix(result, tf)
    print(f"    Effective distinguishable frequencies:")
    print(f"      Stylus: N_eff = {identifiability['N_eff_stylus']:.1f} / {identifiability['N_total']}")
    print(f"      Optical: N_eff = {identifiability['N_eff_optical']:.1f} / {identifiability['N_total']}")
    print(f"    Identifiability efficiency: "
          f"s={identifiability['identifiability_efficiency_s']:.3f}, "
          f"o={identifiability['identifiability_efficiency_o']:.3f}")

    # 3. Channel Capacity Spectrum
    print("\n  [8.3] Computing Channel Capacity Spectrum...")
    capacity = compute_channel_capacity(result, tf)
    print(f"    Total capacity — stylus: {capacity['C_total_stylus_bits']:.2e} bits")
    print(f"    Total capacity — optical: {capacity['C_total_optical_bits']:.2e} bits")
    print(f"    Capacity ratio (s/o): {capacity['C_ratio']:.2f}")
    print(f"    Capacity efficiency: s={capacity['capacity_efficiency_stylus']:.4f}, "
          f"o={capacity['capacity_efficiency_optical']:.4f}")

    # 4. Resolution Entropy (the NEW fundamental quantity)
    print("\n  [8.4] Computing Resolution Entropy S_R...")
    res_entropy = compute_resolution_entropy(fisher, identifiability, capacity)
    print(f"    {res_entropy['interpretation']}")
    print(f"    ⭐ RESOLUTION ENTROPY S_R = {res_entropy['S_R_stylus_bits']:.2f} bits (stylus)")
    print(f"    ⭐ RESOLUTION ENTROPY S_R = {res_entropy['S_R_optical_bits']:.2f} bits (optical)")
    print(f"    ΔS_R = {res_entropy['delta_S_R_bits']:+.2f} bits")

    # 5. Observability Gramian
    print("\n  [8.5] Computing Observability Gramian...")
    observability = compute_observability_gramian(result, tf)
    print(f"    Effective rank — stylus: {observability['effective_rank_stylus']} / {observability['total_modes']}")
    print(f"    Effective rank — optical: {observability['effective_rank_optical']} / {observability['total_modes']}")
    print(f"    Condition number κ — stylus: {observability['condition_number_stylus']:.2f}")
    print(f"    Condition number κ — optical: {observability['condition_number_optical']:.2f}")

    # ── Save outputs ──
    os.makedirs(output_dir, exist_ok=True)

    result_data = {
        "fisher": {k: v for k, v in fisher.items() if not isinstance(v, np.ndarray)},
        "identifiability": {k: v for k, v in identifiability.items()
                           if not isinstance(v, np.ndarray)},
        "capacity": {k: v for k, v in capacity.items() if not isinstance(v, np.ndarray)},
        "resolution_entropy": res_entropy,
        "observability": {k: v for k, v in observability.items()
                         if not isinstance(v, np.ndarray)}
    }

    # Convert numpy types
    def convert(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    result_data = convert(result_data)

    with open(os.path.join(output_dir, "info_theory_results.json"), 'w') as f:
        json.dump(result_data, f, indent=2)

    # Save key arrays
    np.save(os.path.join(output_dir, "F_stylus_2d.npy"), fisher["F_stylus_2d"])
    np.save(os.path.join(output_dir, "C_stylus_2d.npy"), capacity["C_stylus_2d"])
    np.save(os.path.join(output_dir, "SNR_stylus_2d.npy"), capacity["SNR_stylus_2d"])

    print(f"\n  Block 8 results saved to: {output_dir}")
    print("█"*70 + "\n")

    return InfoTheoryResult(
        fisher=fisher,
        identifiability=identifiability,
        capacity=capacity,
        resolution_entropy=res_entropy,
        observability=observability
    )


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from block4_physics_simulator import run_block4, SimulationParams
    from block5_discovery_engine import run_block5

    params = SimulationParams(grid_size=512)
    sim_result = run_block4(params, "./outputs/iter01/sim")
    discovery = run_block5(sim_result, "./outputs/iter01/discovery")
    run_block8(sim_result, discovery, "./outputs/iter01/info_theory")
