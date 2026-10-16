"""
Block 10 — Scatterometry Simulation & Three-Way Comparison
===========================================================
Extends the measurement framework to include angle-resolved
light scattering (scatterometry / ARS).

Scatterometry measures the Bidirectional Scatter Distribution
Function (BSDF) and relates it to the surface PSD via the
Rayleigh-Rice vector perturbation theory:

    BSDF(f) = (16π²/λ⁴) · cosθ_i · cosθ_s · Q(θ_i,θ_s,n,k,pol) · PSD(f)

where:
    f = |sinθ_s - sinθ_i| / λ   is the spatial frequency
    Q is the optical factor (depends on material and polarisation)

Key differences from stylus/WLI:
  1. Measures PSD directly, not h(x,y)
  2. Probes the highest spatial frequencies (up to ~2/λ)
  3. Industrially deployed for in-line semiconductor metrology
  4. Transfer function is fundamentally different in structure

References:
  - Stover, J.C. "Optical Scattering" (SPIE, 1995)
  - Elson, J.M. & Bennett, J.M. "Relation between angular dependence
    of scattering and PSD" (JOSA, 1979)
  - Schröder, S. et al. "Light scattering techniques..." (2011)
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftfreq, fftshift
from dataclasses import dataclass, field
from typing import Dict, Tuple
import os, json

from block4_physics_simulator import SimulationParams, SimulationResult
from block5_discovery_engine import (
    compute_psd_2d, azimuthal_average, TransferFunctions
)


# ============================================================
# Rayleigh-Rice Optical Factor
# ============================================================

def compute_optical_factor_Q(
    theta_i: float,          # incidence angle [rad]
    theta_s: float,           # scattering angle [rad]
    phi_s: float,             # azimuthal scattering angle [rad]
    n: complex,               # complex refractive index
    polarisation: str = 's'   # 's', 'p', or 'unpolarised'
) -> float:
    """
    Compute the Rayleigh-Rice optical factor Q for a given
    scattering geometry.

    For an opaque, clean, smooth surface:

    Q_s = |(n²-1) cos φ_s / [(cos θ_i + √(n²-sin²θ_i))(cos θ_s + √(n²-sin²θ_s))]|²

    Q_p = |(n²-1) √(n²-sin²θ_i) √(n²-sin²θ_s) cos φ_s -
            (n²-1) sin θ_i sin θ_s|² /
           |[n² cos θ_i + √(n²-sin²θ_i)][n² cos θ_s + √(n²-sin²θ_s)]|²

    For unpolarised: Q = (Q_s + Q_p) / 2

    Reference: Stover, "Optical Scattering", SPIE Press (1995), Ch. 4
    """
    cos_theta_i = np.cos(theta_i)
    cos_theta_s = np.cos(theta_s)
    sin_theta_i = np.sin(theta_i)
    sin_theta_s = np.sin(theta_s)
    cos_phi_s = np.cos(phi_s)

    # Complex square roots for n² - sin²θ
    n_sq = n * n
    sqrt_i = np.sqrt(n_sq - sin_theta_i**2)
    sqrt_s = np.sqrt(n_sq - sin_theta_s**2)

    n_sq_m1 = n_sq - 1.0

    if polarisation == 's':
        denominator = ((cos_theta_i + sqrt_i) * (cos_theta_s + sqrt_s))
        numerator = n_sq_m1 * cos_phi_s
        Q = np.abs(numerator / denominator)**2

    elif polarisation == 'p':
        denom_i = n_sq * cos_theta_i + sqrt_i
        denom_s = n_sq * cos_theta_s + sqrt_s
        num1 = n_sq_m1 * sqrt_i * sqrt_s * cos_phi_s
        num2 = n_sq_m1 * sin_theta_i * sin_theta_s
        Q = np.abs((num1 - num2) / (denom_i * denom_s))**2

    else:  # unpolarised
        Q_s = compute_optical_factor_Q(theta_i, theta_s, phi_s, n, 's')
        Q_p = compute_optical_factor_Q(theta_i, theta_s, phi_s, n, 'p')
        Q = 0.5 * (Q_s + Q_p)

    return float(Q)


# ============================================================
# Scatterometry Measurement Model
# ============================================================

def simulate_scatterometry(
    h_true: np.ndarray,
    params: SimulationParams,
    n_material: complex = 2.5 + 3.3j,  # steel at 532 nm
    wavelength_s: float = 532e-9,        # scatterometer wavelength
    theta_i_deg: float = 0.0,            # incidence angle
    polarisation: str = 'unpolarised'
) -> Tuple[np.ndarray, Dict]:
    """
    Simulate angle-resolved scattering measurement.

    The scatterometer measures BSDF, which for a smooth surface
    is directly proportional to the surface PSD:

        BSDF(f_x, f_y) = K(f_x, f_y) · PSD(f_x, f_y)

    where K(f) is the optical calibration factor incorporating
    the Rayleigh-Rice Q factor, cos θ factors, and the (16π²/λ⁴)
    wavelength scaling.

    Returns:
        psd_scatterometry: estimated PSD from BSDF
        meta: diagnostic information
    """
    N = params.grid_size
    dx = params.dx

    # True PSD
    psd_true = compute_psd_2d(h_true, dx)

    # Spatial frequency grid
    fx = fftshift(fftfreq(N, d=dx))
    fy = fftshift(fftfreq(N, d=dx))
    FX, FY = np.meshgrid(fx, fy)
    f_mag = np.sqrt(FX**2 + FY**2)

    # Scattering angles for each spatial frequency
    # f = (sin θ_s - sin θ_i)/λ  →  θ_s = arcsin(fλ + sin θ_i)
    theta_i = np.radians(theta_i_deg)
    sin_theta_s = f_mag * wavelength_s + np.sin(theta_i)

    # Valid scattering range (real angles only)
    valid = (sin_theta_s >= -1.0) & (sin_theta_s <= 1.0) & (f_mag > 0)
    theta_s = np.zeros_like(f_mag)
    theta_s[valid] = np.arcsin(sin_theta_s[valid])

    # Azimuthal angle
    phi_s = np.arctan2(FY, FX)
    # Handle DC
    phi_s[0, 0] = 0.0

    # Compute optical factor Q(f) over valid range
    Q_factor = np.zeros_like(f_mag)
    for i in range(N):
        for j in range(N):
            if valid[i, j]:
                Q_factor[i, j] = compute_optical_factor_Q(
                    theta_i, theta_s[i, j], phi_s[i, j],
                    n_material, polarisation
                )

    # Rayleigh-Rice BSDF
    cos_theta_i = np.cos(theta_i)
    cos_theta_s_grid = np.cos(theta_s)
    cos_theta_s_grid[~valid] = 1.0  # avoid division by zero

    # BSDF = (16π²/λ⁴) · cosθ_i · cosθ_s · Q · PSD
    prefactor = 16.0 * np.pi**2 / (wavelength_s**4)
    bsdf = prefactor * cos_theta_i * cos_theta_s_grid * Q_factor * psd_true
    bsdf[~valid] = 0.0

    # Instrument noise model
    # Scatterometer noise floor: ~10⁻⁸ sr⁻¹ typical
    bsdf_noise_floor = 1e-8
    noise = np.random.randn(N, N) * bsdf_noise_floor * 0.1
    bsdf_measured = bsdf + noise

    # Reconstruct PSD from BSDF (inversion)
    psd_reconstructed = np.zeros_like(psd_true)
    inversion_valid = valid & (Q_factor > 1e-10) & (cos_theta_s_grid > 0.1)
    psd_reconstructed[inversion_valid] = (
        bsdf_measured[inversion_valid] /
        (prefactor * cos_theta_i * cos_theta_s_grid[inversion_valid] *
         Q_factor[inversion_valid])
    )

    # Where inversion is invalid, use noise floor
    psd_reconstructed[~inversion_valid] = bsdf_noise_floor * 1e-10

    # Regularise
    psd_reconstructed = np.maximum(psd_reconstructed, 1e-35)

    # Scatterometry transfer function approximation
    # H_scat(f) ≈ √(PSD_reconstructed / PSD_true) for valid region
    H_scat = np.zeros_like(psd_true)
    H_scat[inversion_valid] = np.sqrt(
        psd_reconstructed[inversion_valid] /
        (psd_true[inversion_valid] + 1e-35)
    )
    H_scat = np.clip(H_scat, 0.001, 10.0)

    # Azimuthal average
    f_radial, psd_scat_1d = azimuthal_average(psd_reconstructed, fx, fy)
    _, H_scat_1d = azimuthal_average(H_scat, fx, fy)

    # Usable frequency range
    f_max_usable = 2.0 / wavelength_s * 1e-3  # mm⁻¹
    f_min_usable = 1.0 / (params.physical_size) * 1e-3  # mm⁻¹

    # Metrics — only in the usable frequency range
    usable_f_mask = valid & (f_mag > f_mag[f_mag > 0].min()) & (Q_factor > 1e-10)
    if np.any(usable_f_mask):
        relative_error = np.median(
            np.abs(psd_reconstructed[usable_f_mask] - psd_true[usable_f_mask]) /
            (psd_true[usable_f_mask] + 1e-35)
        )
    else:
        relative_error = 1.0

    meta = {
        "wavelength_nm": float(wavelength_s * 1e9),
        "theta_i_deg": theta_i_deg,
        "polarisation": polarisation,
        "n_material": str(n_material),
        "f_max_usable_mm": float(f_max_usable),
        "f_min_usable_mm": float(f_min_usable),
        "relative_psd_error": float(relative_error),
        "bsdf_noise_floor": float(bsdf_noise_floor),
        "optical_factor_median": float(np.median(Q_factor[valid])),
        "note": (
            f"Scatterometry at λ={wavelength_s*1e9:.0f} nm, "
            f"θ_i={theta_i_deg}°, "
            f"usable f-range: {f_min_usable:.2f}–{f_max_usable:.0f} mm⁻¹. "
            f"Relative PSD error: {relative_error*100:.1f}%. "
            f"Optical factor Q_median = {np.median(Q_factor[valid]):.3f}."
        )
    }

    return psd_reconstructed, H_scat, meta


# ============================================================
# Three-Way Comparison
# ============================================================

@dataclass
class ThreeWayResult:
    """Results from all three modalities."""
    params: SimulationParams
    # Stylus & optical (existing)
    psd_stylus: np.ndarray
    psd_optical: np.ndarray
    H_stylus_1d: np.ndarray
    H_optical_1d: np.ndarray
    # Scatterometry (new)
    psd_scatterometry: np.ndarray
    H_scatterometry: np.ndarray
    H_scat_1d: np.ndarray
    scat_meta: Dict
    # Common
    f_radial: np.ndarray
    psd_true_1d: np.ndarray


def run_three_way_comparison(
    result: SimulationResult,
    discovery,  # DiscoveryResult
    output_dir: str
) -> ThreeWayResult:
    """Run complete three-way comparison: stylus, WLI, scatterometry."""
    print("\n" + "█"*70)
    print("█  BLOCK 10 — SCATTEROMETRY & THREE-WAY COMPARISON")
    print("█"*70)

    tf = discovery.transfer_functions

    # True PSD
    dx = result.params.dx
    psd_true = compute_psd_2d(result.h_true, dx)
    f_r, psd_true_1d = azimuthal_average(psd_true, result.fx, result.fy)

    # Stylus & optical PSD (existing)
    psd_stylus = compute_psd_2d(result.h_stylus, dx)
    psd_optical = compute_psd_2d(result.h_optical, dx)
    _, psd_s_1d = azimuthal_average(psd_stylus, result.fx, result.fy)
    _, psd_o_1d = azimuthal_average(psd_optical, result.fx, result.fy)

    # Scatterometry simulation
    print("\n  Simulating scatterometry at λ=532 nm...")
    psd_scat, H_scat_2d, scat_meta = simulate_scatterometry(
        result.h_true, result.params,
        n_material=2.5 + 3.3j,
        wavelength_s=532e-9,
        theta_i_deg=0.0
    )
    _, psd_scat_1d = azimuthal_average(psd_scat, result.fx, result.fy)
    _, H_scat_1d = azimuthal_average(H_scat_2d, result.fx, result.fy)

    print(f"    {scat_meta['note']}")

    # Three-way metrics comparison
    print(f"\n  Three-way comparison:")
    print(f"    {'Modality':<18} {'f_range [mm⁻¹]':<20} {'H(f) type':<25}")
    print(f"    {'─'*60}")
    print(f"    {'Stylus':<18} {'0.1–500':<20} {'Morphological + sampling':<25}")
    print(f"    {'WLI':<18} {'1–1000':<20} {'OTF + coherence':<25}")
    print(f"    {'Scatterometry':<18} "
          f"{scat_meta['f_min_usable_mm']:.0f}–{scat_meta['f_max_usable_mm']:.0f}"
          f"{'':<8} {'Rayleigh-Rice BSDF→PSD':<25}")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    np.save(os.path.join(output_dir, "psd_scatterometry.npy"), psd_scat)
    np.save(os.path.join(output_dir, "H_scatterometry_2d.npy"), H_scat_2d)

    with open(os.path.join(output_dir, "scatterometry_meta.json"), 'w') as f:
        json.dump(scat_meta, f, indent=2, default=str)

    print(f"\n  Three-way comparison saved to: {output_dir}")
    print("█"*70 + "\n")

    return ThreeWayResult(
        params=result.params,
        psd_stylus=psd_stylus,
        psd_optical=psd_optical,
        H_stylus_1d=tf.H_stylus_1d,
        H_optical_1d=tf.H_optical_1d,
        psd_scatterometry=psd_scat,
        H_scatterometry=H_scat_2d,
        H_scat_1d=H_scat_1d,
        scat_meta=scat_meta,
        f_radial=f_r,
        psd_true_1d=psd_true_1d
    )


# ============================================================
# Figure 9 — Three-Way Transfer Functions
# ============================================================
def fig_three_way_transfer(three_way: ThreeWayResult, output_dir: str):
    """Figure 9: Three-way transfer function comparison."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.family': 'serif', 'font.size': 10,
        'axes.labelsize': 11, 'axes.titlesize': 11,
        'legend.fontsize': 9, 'figure.dpi': 150,
        'savefig.dpi': 300, 'savefig.bbox': 'tight'
    })

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)

    f_r = three_way.f_radial * 1e-3
    pos = f_r > 0

    # (a) PSD comparison — all three modalities
    ax = axes[0]
    _, psd_s_1d = azimuthal_average(three_way.psd_stylus,
                                     np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)),
                                     np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)))
    _, psd_o_1d = azimuthal_average(three_way.psd_optical,
                                     np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)),
                                     np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)))
    _, psd_scat_1d = azimuthal_average(three_way.psd_scatterometry,
                                        np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)),
                                        np.fft.fftshift(np.fft.fftfreq(512, d=three_way.params.dx)))

    ax.loglog(f_r[pos], three_way.psd_true_1d[pos], 'k-', lw=1.5, label='True')
    ax.loglog(f_r[pos], psd_s_1d[pos], 'b--', lw=1.2, label='Stylus')
    ax.loglog(f_r[pos], psd_o_1d[pos], 'r-.', lw=1.2, label='WLI')
    ax.loglog(f_r[pos], psd_scat_1d[pos], 'g:', lw=1.5, label='Scatterometry')
    ax.set_xlabel(r'$f$ [mm$^{-1}$]')
    ax.set_ylabel(r'PSD [m$^3$]')
    ax.set_title('(a) PSD: Three Modalities', loc='left', fontsize=10.5, fontweight='bold')
    ax.legend(loc='lower left', framealpha=0.85)
    ax.grid(True, alpha=0.3, which='both')

    # (b) Transfer functions
    ax = axes[1]
    ax.semilogx(f_r[pos], three_way.H_stylus_1d[pos], 'b-', lw=1.5, label='Stylus')
    ax.semilogx(f_r[pos], three_way.H_optical_1d[pos], 'r-', lw=1.5, label='WLI')
    ax.semilogx(f_r[pos], three_way.H_scat_1d[pos], 'g-', lw=1.5, label='Scatterometry')
    ax.axhline(1.0, color='gray', ls=':', lw=0.6)
    ax.set_xlabel(r'$f$ [mm$^{-1}$]')
    ax.set_ylabel(r'$H(f)$')
    ax.set_title('(b) Transfer Functions', loc='left', fontsize=10.5, fontweight='bold')
    ax.legend(loc='lower left', framealpha=0.85)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_ylim([0, 1.05])

    # (c) Frequency coverage comparison
    ax = axes[2]
    modalities = ['Stylus', 'WLI', 'Scatterometry']
    f_mins = [0.1, 1.0, three_way.scat_meta['f_min_usable_mm']]
    f_maxs = [500., 1000., three_way.scat_meta['f_max_usable_mm']]
    colors = ['#2166ac', '#b2182b', '#4dac26']

    for i, (mod, fmin, fmax, c) in enumerate(zip(modalities, f_mins, f_maxs, colors)):
        ax.barh(i, fmax - fmin, left=fmin, height=0.5, color=c, alpha=0.8, edgecolor='white')
        ax.text(fmax * 1.02, i, f'{fmin:.0f}–{fmax:.0f} mm⁻¹', va='center', fontsize=9)

    ax.set_yticks(range(len(modalities)))
    ax.set_yticklabels(modalities)
    ax.set_xlabel(r'$f$ [mm$^{-1}$]')
    ax.set_xscale('log')
    ax.set_title('(c) Frequency Coverage', loc='left', fontsize=10.5, fontweight='bold')
    ax.set_xlim([0.05, 5000])

    fig.savefig(os.path.join(output_dir, 'fig9_three_way_transfer.pdf'))
    plt.close(fig)
    print("  Figure 9 saved: three-way transfer comparison")


# ============================================================
# Runner
# ============================================================
def run_block10(result: SimulationResult, discovery,
                output_dir: str) -> ThreeWayResult:
    """Run scatterometry simulation and three-way comparison."""
    three_way = run_three_way_comparison(result, discovery, output_dir)
    fig_three_way_transfer(three_way, output_dir)
    return three_way


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from block4_physics_simulator import run_block4, SimulationParams
    from block5_discovery_engine import run_block5

    params = SimulationParams(grid_size=512)
    sim_result = run_block4(params, "./outputs/iter01/sim")
    discovery = run_block5(sim_result, "./outputs/iter01/discovery")
    run_block10(sim_result, discovery, "./outputs/iter01/scatterometry")
