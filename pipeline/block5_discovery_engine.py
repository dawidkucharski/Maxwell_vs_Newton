"""
Block 5 — Discovery Engine
===========================
Computes key discovery quantities from simulated measurements:

1. Transfer functions: H_stylus(f_x, f_y), H_optical(f_x, f_y)
2. Information loss: I(f_x, f_y) = log(PSD_true / PSD_measured)
3. Anisotropy tensor: A_ij = ∫ f_i f_j H(f) df
4. Spectral distortion metric
5. Cross-over analysis

Input:  SimulationResult from Block 4
Output: Discovery data (arrays + metrics)
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftshift, fftfreq
from scipy.signal import windows
from scipy.ndimage import uniform_filter
from dataclasses import dataclass, field, asdict
from typing import Dict, Tuple, Optional
import json
import os

from block4_physics_simulator import SimulationResult, SimulationParams


@dataclass
class TransferFunctions:
    """Instrument transfer functions in k-space."""
    fx: np.ndarray = field(default=None, repr=False)
    fy: np.ndarray = field(default=None, repr=False)
    H_stylus: np.ndarray = field(default=None, repr=False)     # 2D
    H_optical: np.ndarray = field(default=None, repr=False)    # 2D
    H_ratio: np.ndarray = field(default=None, repr=False)      # H_opt / H_stylus

    # Azimuthally averaged 1D profiles
    f_radial: np.ndarray = field(default=None, repr=False)
    H_stylus_1d: np.ndarray = field(default=None, repr=False)
    H_optical_1d: np.ndarray = field(default=None, repr=False)

    # Radial profiles along x and y axes
    H_stylus_x: np.ndarray = field(default=None, repr=False)
    H_stylus_y: np.ndarray = field(default=None, repr=False)
    H_optical_x: np.ndarray = field(default=None, repr=False)
    H_optical_y: np.ndarray = field(default=None, repr=False)


@dataclass
class InformationLoss:
    """Information-theoretic analysis of measurement."""
    I_field: np.ndarray = field(default=None, repr=False)     # I(f_x, f_y) 2D
    I_radial: np.ndarray = field(default=None, repr=False)    # Azimuthally averaged
    I_integrated: float = 0.0                                  # Total integrated loss
    I_stylus: float = 0.0                                      # Total loss for stylus
    I_optical: float = 0.0                                     # Total loss for optical
    I_per_band: Dict[str, float] = field(default_factory=dict)

    # Mutual information proxy
    mi_stylus: float = 0.0
    mi_optical: float = 0.0


@dataclass
class AnisotropyTensor:
    """Measurement system anisotropy tensor."""
    A_ij: np.ndarray = field(default=None, repr=False)        # 2×2 tensor
    eigenvalues: np.ndarray = field(default=None, repr=False)  # λ_1, λ_2
    eigenvectors: np.ndarray = field(default=None, repr=False) # 2×2
    anisotropy_degree: float = 0.0                              # α ∈ [0,1]
    principal_angle: float = 0.0                               # radians

    # Per-modality
    stylus: Dict = field(default_factory=dict)
    optical: Dict = field(default_factory=dict)


@dataclass
class DiscoveryResult:
    """All discovery outputs combined."""
    transfer_functions: TransferFunctions
    information_loss: InformationLoss
    anisotropy: AnisotropyTensor
    spectral_distortion: Dict[str, float]
    crossover_analysis: Dict


# ============================================================
# PSD Computation
# ============================================================

def compute_psd_2d(h: np.ndarray, dx: float, window: str = 'hann',
                   averaging: int = 1) -> np.ndarray:
    """
    Compute 2D power spectral density.

    PSD(f_x, f_y) = |FFT[h(x,y)]|² · dx² / N²
    """
    N = h.shape[0]

    # Apply window
    if window == 'hann':
        win = np.outer(windows.hann(N), windows.hann(N))
    elif window == 'none':
        win = np.ones((N, N))
    else:
        win = np.outer(windows.hann(N), windows.hann(N))

    # Windowing normalisation
    win_norm = np.mean(win**2)

    # FFT with window
    H_f = fftshift(fft2(h * win))
    psd = np.abs(H_f)**2 * dx**2 / (N**2 * win_norm)

    return psd


def azimuthal_average(psd_2d: np.ndarray, fx: np.ndarray, fy: np.ndarray,
                      n_bins: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute azimuthally averaged 1D PSD from 2D PSD.

    Returns (f_radial, psd_1d).
    """
    FX, FY = np.meshgrid(fx, fy)
    f_radial = np.sqrt(FX**2 + FY**2)

    f_max = np.max(f_radial) * 0.95  # Exclude corners
    f_bins = np.linspace(0, f_max, n_bins + 1)
    f_centers = 0.5 * (f_bins[:-1] + f_bins[1:])

    psd_1d = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (f_radial >= f_bins[i]) & (f_radial < f_bins[i+1])
        if mask.sum() > 0:
            psd_1d[i] = np.mean(psd_2d[mask])

    return f_centers, psd_1d


# ============================================================
# Transfer Function Computation
# ============================================================

def compute_transfer_functions(result: SimulationResult,
                                smooth_sigma: int = 3) -> TransferFunctions:
    """
    Compute instrument transfer functions.

    H_sensor(f_x, f_y) = PSD_measured(f) / PSD_true(f)
    """
    dx = result.params.dx
    N = result.params.grid_size

    # Compute PSDs
    psd_true = compute_psd_2d(result.h_true, dx)
    psd_stylus = compute_psd_2d(result.h_stylus, dx)
    psd_optical = compute_psd_2d(result.h_optical, dx)

    # Regularise to avoid division by zero
    eps = 1e-30
    psd_true_safe = np.maximum(psd_true, eps * np.max(psd_true))

    # Transfer functions
    H_stylus = psd_stylus / psd_true_safe
    H_optical = psd_optical / psd_true_safe
    H_ratio = np.where(H_stylus > eps, H_optical / (H_stylus + eps), 0.0)

    # Clip to reasonable range (±10 dB)
    H_stylus = np.clip(H_stylus, 0.001, 10.0)
    H_optical = np.clip(H_optical, 0.001, 10.0)
    H_ratio = np.clip(H_ratio, 0.001, 10.0)

    # Smooth for visualisation
    if smooth_sigma > 0:
        H_stylus = uniform_filter(H_stylus, size=smooth_sigma)
        H_optical = uniform_filter(H_optical, size=smooth_sigma)
        H_ratio = uniform_filter(H_ratio, size=smooth_sigma)

    # Azimuthal averages
    f_radial, H_s_1d = azimuthal_average(H_stylus, result.fx, result.fy)
    _, H_o_1d = azimuthal_average(H_optical, result.fx, result.fy)

    # Profiles along axes
    center = N // 2
    H_stylus_x = H_stylus[center, :]
    H_stylus_y = H_stylus[:, center]
    H_optical_x = H_optical[center, :]
    H_optical_y = H_optical[:, center]

    return TransferFunctions(
        fx=result.fx,
        fy=result.fy,
        H_stylus=H_stylus,
        H_optical=H_optical,
        H_ratio=H_ratio,
        f_radial=f_radial,
        H_stylus_1d=H_s_1d,
        H_optical_1d=H_o_1d,
        H_stylus_x=H_stylus_x,
        H_stylus_y=H_stylus_y,
        H_optical_x=H_optical_x,
        H_optical_y=H_optical_y
    )


# ============================================================
# Information Loss Computation
# ============================================================

def compute_information_loss(result: SimulationResult,
                              tf: TransferFunctions) -> InformationLoss:
    """
    Compute spectral information loss with proper noise-floor regularisation.

    I(f_x, f_y) = log10(PSD_true / PSD_measured)  [in decades = 10*dB]

    Positive I means information loss (measured PSD < true PSD).
    Only computed where true PSD is above the noise floor to avoid
    numerical instability at high frequencies.

    The noise floor is estimated from the high-frequency tail of PSD_true
    where the signal is dominated by discretisation noise.
    """
    dx = result.params.dx
    N = result.params.grid_size

    psd_true = compute_psd_2d(result.h_true, dx)
    psd_stylus = compute_psd_2d(result.h_stylus, dx)
    psd_optical = compute_psd_2d(result.h_optical, dx)

    # ---- Estimate noise floor from high-frequency PSD tail ----
    FX, FY = np.meshgrid(result.fx, result.fy)
    f_radial_2d = np.sqrt(FX**2 + FY**2)
    f_max = np.max(result.fx) * 0.95

    # Noise floor: median PSD in the highest 10% of frequencies
    high_f_mask = f_radial_2d > 0.85 * f_max
    noise_floor_true = np.median(psd_true[high_f_mask]) if high_f_mask.sum() > 10 else 1e-35
    noise_floor_true = max(noise_floor_true, 1e-35)

    # Signal mask: only analyse where true PSD is significantly above noise
    signal_mask = psd_true > (10.0 * noise_floor_true)

    # ---- Regularised information loss ----
    # Use Tikhonov-style regularisation: I = log10(PSD_true / (PSD_measured + ε))
    # where ε is the noise floor, preventing division by zero
    eps_reg = noise_floor_true

    psd_s_reg = psd_stylus + eps_reg
    psd_o_reg = psd_optical + eps_reg
    psd_t_reg = psd_true + eps_reg

    # Information loss fields (in decades, 1 decade = 10 dB)
    I_stylus_field = np.zeros_like(psd_true)
    I_optical_field = np.zeros_like(psd_true)

    I_stylus_field[signal_mask] = np.log10(
        psd_t_reg[signal_mask] / psd_s_reg[signal_mask]
    )
    I_optical_field[signal_mask] = np.log10(
        psd_t_reg[signal_mask] / psd_o_reg[signal_mask]
    )

    # Clip negative values (measured > true = no loss, or noise fluctuation)
    I_stylus_field = np.maximum(I_stylus_field, 0)
    I_optical_field = np.maximum(I_optical_field, 0)

    # Combined information loss (mean of both in linear ratio, then log)
    # Actually use average of the two log fields
    I_field = 0.5 * (I_stylus_field + I_optical_field)

    # ---- Azimuthal average (only over signal region) ----
    f_radial, I_radial = azimuthal_average(I_field, result.fx, result.fy)

    # ---- Integrated loss (over signal region only) ----
    dfx = result.fx[1] - result.fx[0]
    dfy = result.fy[1] - result.fy[0]
    I_integrated = np.sum(I_field[signal_mask]) * dfx * dfy
    I_stylus_total = np.sum(I_stylus_field[signal_mask]) * dfx * dfy
    I_optical_total = np.sum(I_optical_field[signal_mask]) * dfx * dfy

    # Normalise by k-space area of signal region for a density metric
    signal_area = signal_mask.sum() * dfx * dfy
    I_density = I_integrated / (signal_area + 1e-30)  # avg loss per unit k-space

    # ---- Per-band loss ----
    bands = {
        "low": (0, 0.1 * f_max),
        "mid": (0.1 * f_max, 0.5 * f_max),
        "high": (0.5 * f_max, f_max)
    }

    I_per_band = {}
    for band_name, (f_low, f_high) in bands.items():
        mask = (f_radial_2d >= f_low) & (f_radial_2d < f_high) & signal_mask
        if mask.sum() > 0:
            I_per_band[band_name] = float(np.mean(I_field[mask]))
        else:
            I_per_band[band_name] = 0.0

    # ---- Mutual information proxy ----
    # Only on signal region to avoid noise-dominated correlations
    psd_t_flat = psd_true[signal_mask]
    psd_s_flat = psd_stylus[signal_mask]
    psd_o_flat = psd_optical[signal_mask]

    if len(psd_t_flat) > 10:
        eps_mi = noise_floor_true
        mi_s = np.corrcoef(
            np.log10(psd_t_flat + eps_mi),
            np.log10(psd_s_flat + eps_mi)
        )[0, 1]
        mi_o = np.corrcoef(
            np.log10(psd_t_flat + eps_mi),
            np.log10(psd_o_flat + eps_mi)
        )[0, 1]
    else:
        mi_s, mi_o = 0.0, 0.0

    return InformationLoss(
        I_field=I_field,
        I_radial=I_radial,
        I_integrated=float(I_integrated),
        I_stylus=float(I_stylus_total),
        I_optical=float(I_optical_total),
        I_per_band=I_per_band,
        mi_stylus=float(max(mi_s, 0)),
        mi_optical=float(max(mi_o, 0))
    )


# ============================================================
# Anisotropy Tensor Computation
# ============================================================

def compute_anisotropy_tensor(tf: TransferFunctions,
                               result: SimulationResult) -> AnisotropyTensor:
    """
    Compute measurement anisotropy tensor.

    A_ij = ∫ f_i f_j H_sensor(f) df / ∫ H_sensor(f) df

    where f_1 = f_x, f_2 = f_y.
    """
    FX, FY = np.meshgrid(tf.fx, tf.fy)
    dfx = tf.fx[1] - tf.fx[0]
    dfy = tf.fy[1] - tf.fy[0]

    def compute_tensor(H):
        """Compute A_ij for a given transfer function H."""
        norm = np.sum(H) * dfx * dfy
        if norm < 1e-30:
            return np.eye(2), np.array([0, 0]), np.eye(2), 0.0, 0.0

        A_xx = np.sum(FX * FX * H) * dfx * dfy / norm
        A_yy = np.sum(FY * FY * H) * dfx * dfy / norm
        A_xy = np.sum(FX * FY * H) * dfx * dfy / norm

        A = np.array([[A_xx, A_xy], [A_xy, A_yy]])

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(A)

        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Anisotropy degree
        if eigenvalues[0] + eigenvalues[1] > 0:
            alpha = np.abs(eigenvalues[0] - eigenvalues[1]) / (eigenvalues[0] + eigenvalues[1])
        else:
            alpha = 0.0

        # Principal angle
        theta = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

        return A, eigenvalues, eigenvectors, alpha, theta

    A_s, ev_s, evec_s, alpha_s, theta_s = compute_tensor(tf.H_stylus)
    A_o, ev_o, evec_o, alpha_o, theta_o = compute_tensor(tf.H_optical)

    # Combined (average tensor)
    A_combined = (A_s + A_o) / 2.0
    ev_combined, evec_combined = np.linalg.eigh(A_combined)
    idx = np.argsort(ev_combined)[::-1]
    ev_combined = ev_combined[idx]
    evec_combined = evec_combined[:, idx]

    if ev_combined[0] + ev_combined[1] > 0:
        alpha_combined = np.abs(ev_combined[0] - ev_combined[1]) / (ev_combined[0] + ev_combined[1])
    else:
        alpha_combined = 0.0
    theta_combined = np.arctan2(evec_combined[1, 0], evec_combined[0, 0])

    tensor = AnisotropyTensor(
        A_ij=A_combined,
        eigenvalues=ev_combined,
        eigenvectors=evec_combined,
        anisotropy_degree=float(alpha_combined),
        principal_angle=float(theta_combined),
        stylus={
            "A_ij": A_s.tolist(),
            "eigenvalues": ev_s.tolist(),
            "anisotropy_degree": float(alpha_s),
            "principal_angle_deg": float(np.degrees(theta_s))
        },
        optical={
            "A_ij": A_o.tolist(),
            "eigenvalues": ev_o.tolist(),
            "anisotropy_degree": float(alpha_o),
            "principal_angle_deg": float(np.degrees(theta_o))
        }
    )

    return tensor


# ============================================================
# Spectral Distortion & Cross-over
# ============================================================

def compute_spectral_distortion(result: SimulationResult,
                                 tf: TransferFunctions) -> Dict[str, float]:
    """
    Compute spectral distortion metrics.

    Returns:
        D_spec: Normalised RMS spectral distortion
        C_spec: Spectral correlation
        D_wasserstein_proxy: Proxy for Wasserstein distance between PSDs
    """
    dx = result.params.dx

    psd_true = compute_psd_2d(result.h_true, dx)
    psd_stylus = compute_psd_2d(result.h_stylus, dx)
    psd_optical = compute_psd_2d(result.h_optical, dx)

    # Normalise PSDs
    psd_t_norm = psd_true / (np.sum(psd_true) + 1e-30)
    psd_s_norm = psd_stylus / (np.sum(psd_stylus) + 1e-30)
    psd_o_norm = psd_optical / (np.sum(psd_optical) + 1e-30)

    # D_spec: RMS normalised distortion
    D_s = np.sqrt(np.mean((psd_s_norm - psd_t_norm)**2))
    D_o = np.sqrt(np.mean((psd_o_norm - psd_t_norm)**2))

    # C_spec: Spectral correlation
    C_s = np.sum(psd_t_norm * psd_s_norm) / (
        np.sqrt(np.sum(psd_t_norm**2)) * np.sqrt(np.sum(psd_s_norm**2)) + 1e-30
    )
    C_o = np.sum(psd_t_norm * psd_o_norm) / (
        np.sqrt(np.sum(psd_t_norm**2)) * np.sqrt(np.sum(psd_o_norm**2)) + 1e-30
    )

    # Wasserstein proxy: cumulative difference
    psd_t_cum = np.cumsum(np.sort(psd_t_norm.ravel()))
    psd_s_cum = np.cumsum(np.sort(psd_s_norm.ravel()))
    psd_o_cum = np.cumsum(np.sort(psd_o_norm.ravel()))
    W_s = np.mean(np.abs(psd_s_cum - psd_t_cum))
    W_o = np.mean(np.abs(psd_o_cum - psd_t_cum))

    return {
        "D_spec_stylus": float(D_s),
        "D_spec_optical": float(D_o),
        "C_spec_stylus": float(C_s),
        "C_spec_optical": float(C_o),
        "W_proxy_stylus": float(W_s),
        "W_proxy_optical": float(W_o),
        "D_spec_ratio": float(D_s / (D_o + 1e-30)),
        "C_spec_ratio": float(C_s / (C_o + 1e-30))
    }


def compute_crossover_analysis(tf: TransferFunctions,
                                result: SimulationResult) -> Dict:
    """
    Find k-space crossover between stylus and optical transfer functions.

    The crossover region is where |H_stylus - H_optical| < threshold.
    This defines the equivalence regime.
    """
    H_diff = np.abs(tf.H_stylus - tf.H_optical)

    # Find regions where difference < 3 dB (factor of 2 in linear units)
    # Use log scale for threshold
    H_s_db = 10.0 * np.log10(np.maximum(tf.H_stylus, 1e-10))
    H_o_db = 10.0 * np.log10(np.maximum(tf.H_optical, 1e-10))
    diff_db = np.abs(H_s_db - H_o_db)

    thresholds_db = [1.0, 2.0, 3.0, 6.0]
    equivalence_fraction = {}

    FX, FY = np.meshgrid(tf.fx, tf.fy)
    total_pixels = FX.size

    for thresh in thresholds_db:
        mask = diff_db < thresh
        equivalence_fraction[f"{thresh:.0f}dB"] = float(mask.sum() / total_pixels)

    # Crossover frequency (where H_s ≈ H_o in azimuthal average)
    f_radial = tf.f_radial
    h_diff_1d = np.abs(tf.H_stylus_1d - tf.H_optical_1d)

    # Find frequency where difference is minimal
    crossover_idx = np.argmin(h_diff_1d[1:]) + 1  # Skip DC
    crossover_f = float(f_radial[crossover_idx])
    crossover_diff = float(h_diff_1d[crossover_idx])

    # Find k-space regions where one modality clearly dominates
    stylus_better = tf.H_stylus_1d > (tf.H_optical_1d * 2.0)  # 3 dB better
    optical_better = tf.H_optical_1d > (tf.H_stylus_1d * 2.0)

    # Find transition points
    stylus_dominant_frac = float(np.sum(stylus_better) / len(stylus_better))
    optical_dominant_frac = float(np.sum(optical_better) / len(optical_better))

    return {
        "crossover_frequency_m": crossover_f,
        "crossover_wavelength_m": float(1.0 / crossover_f) if crossover_f > 0 else np.inf,
        "crossover_diff_db": float(crossover_diff),
        "equivalence_fraction_vs_threshold": equivalence_fraction,
        "stylus_dominant_fraction": stylus_dominant_frac,
        "optical_dominant_fraction": optical_dominant_frac,
        "optical_cutoff_m": result.params.optical_cutoff,
        "stylus_cutoff_m": result.params.stylus_cutoff,
        "cutoff_ratio": result.params.optical_cutoff / result.params.stylus_cutoff
    }


# ============================================================
# Main Discovery Runner
# ============================================================

def run_discovery(result: SimulationResult) -> DiscoveryResult:
    """Run complete discovery engine on simulation results."""
    print("\n" + "─"*70)
    print("  BLOCK 5 — DISCOVERY ENGINE")
    print("─"*70)

    # 1. Transfer functions
    print("  Computing transfer functions...")
    tf = compute_transfer_functions(result)

    # 2. Information loss
    print("  Computing information loss...")
    info_loss = compute_information_loss(result, tf)

    # 3. Anisotropy tensor
    print("  Computing anisotropy tensor...")
    anisotropy = compute_anisotropy_tensor(tf, result)

    # 4. Spectral distortion
    print("  Computing spectral distortion metrics...")
    distortion = compute_spectral_distortion(result, tf)

    # 5. Crossover analysis
    print("  Computing crossover analysis...")
    crossover = compute_crossover_analysis(tf, result)

    print(f"\n  Key findings:")
    print(f"    Integrated info loss: {info_loss.I_integrated:.4f}")
    print(f"    Stylus anisotropy α = {anisotropy.stylus['anisotropy_degree']:.4f}")
    print(f"    Optical anisotropy α = {anisotropy.optical['anisotropy_degree']:.4f}")
    print(f"    Crossover frequency: {crossover['crossover_frequency_m']*1e-3:.2f} mm⁻¹")
    print(f"      → wavelength: {crossover['crossover_wavelength_m']*1e6:.2f} µm")
    print(f"    Spectral correlation C_s: {distortion['C_spec_stylus']:.4f}")
    print(f"    Spectral correlation C_o: {distortion['C_spec_optical']:.4f}")
    print(f"    Equivalence (3dB): {crossover['equivalence_fraction_vs_threshold']['3dB']*100:.1f}%")

    return DiscoveryResult(
        transfer_functions=tf,
        information_loss=info_loss,
        anisotropy=anisotropy,
        spectral_distortion=distortion,
        crossover_analysis=crossover
    )


def save_discovery_results(discovery: DiscoveryResult, output_dir: str):
    """Save discovery results."""
    os.makedirs(output_dir, exist_ok=True)

    # Save arrays
    np.save(os.path.join(output_dir, "H_stylus_2d.npy"), discovery.transfer_functions.H_stylus)
    np.save(os.path.join(output_dir, "H_optical_2d.npy"), discovery.transfer_functions.H_optical)
    np.save(os.path.join(output_dir, "H_ratio_2d.npy"), discovery.transfer_functions.H_ratio)
    np.save(os.path.join(output_dir, "I_field_2d.npy"), discovery.information_loss.I_field)

    # Save metrics JSON
    metrics = {
        "information_loss": {
            "I_integrated": discovery.information_loss.I_integrated,
            "I_stylus": discovery.information_loss.I_stylus,
            "I_optical": discovery.information_loss.I_optical,
            "I_per_band": discovery.information_loss.I_per_band,
            "MI_stylus": discovery.information_loss.mi_stylus,
            "MI_optical": discovery.information_loss.mi_optical
        },
        "anisotropy": asdict(discovery.anisotropy),
        "spectral_distortion": discovery.spectral_distortion,
        "crossover_analysis": discovery.crossover_analysis
    }

    # Convert numpy values
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    metrics = convert(metrics)

    with open(os.path.join(output_dir, "discovery_metrics.json"), 'w') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"  Discovery results saved to: {output_dir}")


def run_block5(result: SimulationResult, output_dir: str) -> DiscoveryResult:
    """Run Block 5: Discovery Engine."""
    discovery = run_discovery(result)
    save_discovery_results(discovery, output_dir)
    return discovery


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from block4_physics_simulator import run_block4, SimulationParams

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./outputs"
    params = SimulationParams()
    result = run_block4(params, os.path.join(output_dir, "sim"))
    run_block5(result, os.path.join(output_dir, "discovery"))
