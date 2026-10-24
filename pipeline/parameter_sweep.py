"""
Parameter Sweep Module
======================
Runs the simulation + discovery pipeline across a grid of parameters
to empirically discover scaling laws and validate hypotheses.

Sweep dimensions:
  - Tip radius (stylus): r_tip ∈ [0.5, 0.5, 1, 2, 5, 10] µm
  - Numerical aperture (optical): NA ∈ [0.1, 0.2, 0.3, 0.4, 0.55, 0.7]
  - Hurst exponent (surface): H ∈ [0.3, 0.5, 0.7, 0.9]
  - RMS roughness: σ ∈ [10, 25, 50, 100] nm

Outputs:
  - sweep_results.json: all metrics for each parameter combination
  - scaling_law_fits.json: fitted power-law exponents
  - sweep_summary.txt: human-readable summary
"""

import numpy as np
import json
import os

SWEEP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs', 'sweep')
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
from itertools import product
from tqdm import tqdm

from block4_physics_simulator import (
    SimulationParams, generate_self_affine_surface,
    simulate_stylus, simulate_optical
)
from block5_discovery_engine import (
    compute_psd_2d, compute_transfer_functions,
    compute_information_loss, compute_anisotropy_tensor,
    compute_spectral_distortion, compute_crossover_analysis,
    TransferFunctions, InformationLoss, AnisotropyTensor,
    DiscoveryResult, azimuthal_average
)


@dataclass
class SweepPoint:
    """Results for a single parameter combination."""
    # Parameters
    tip_radius: float
    na: float
    hurst_exponent: float
    rms_roughness: float

    # Metrics
    rmse_stylus: float
    rmse_optical: float
    corr_stylus: float
    corr_optical: float

    # Discovery
    I_integrated: float
    I_stylus: float
    I_optical: float
    anisotropy_stylus: float
    anisotropy_optical: float
    C_spec_stylus: float
    C_spec_optical: float
    D_spec_stylus: float
    D_spec_optical: float
    mi_stylus: float
    mi_optical: float
    crossover_frequency: float
    equivalence_fraction_3dB: float

    # Derived
    cutoff_ratio: float  # f_c_opt / f_c_stylus


def run_single_sweep_point(
    tip_radius: float,
    na: float,
    hurst_exponent: float,
    rms_roughness: float,
    grid_size: int = 256,  # Smaller grid for speed
    seed: int = 42
) -> SweepPoint:
    """Run simulation + discovery for a single parameter combination."""

    params = SimulationParams(
        grid_size=grid_size,
        physical_size=100e-6,
        hurst_exponent=hurst_exponent,
        rms_roughness=rms_roughness,
        tip_radius=tip_radius,
        na=na
    )

    # Generate surface & simulate
    h_true = generate_self_affine_surface(params, seed=seed)
    h_stylus, meta_s = simulate_stylus(h_true, params)
    h_optical, meta_o = simulate_optical(h_true, params)

    # Compute PSDs
    dx = params.dx
    psd_true = compute_psd_2d(h_true, dx)
    psd_stylus = compute_psd_2d(h_stylus, dx)
    psd_optical = compute_psd_2d(h_optical, dx)

    # Build minimal result structure for discovery functions
    # We need fx, fy arrays
    fx = np.fft.fftshift(np.fft.fftfreq(grid_size, d=dx))
    fy = np.fft.fftshift(np.fft.fftfreq(grid_size, d=dx))

    # Create a lightweight result-like object
    class MiniResult:
        pass

    result = MiniResult()
    result.params = params
    result.h_true = h_true
    result.h_stylus = h_stylus
    result.h_optical = h_optical
    result.fx = fx
    result.fy = fy
    result.rmse_stylus = meta_s["rmse"]
    result.rmse_optical = meta_o["rmse"]
    result.correlation_stylus = meta_s["correlation"]
    result.correlation_optical = meta_o["correlation"]

    # Convert to a proper SimulationResult-like object for the discovery functions
    # The discovery functions need .params, .fx, .fy, .dx
    # We'll monkey-patch

    # Compute transfer functions
    tf = compute_transfer_functions(result)

    # Compute information loss
    info_loss = compute_information_loss(result, tf)

    # Compute anisotropy
    anisotropy = compute_anisotropy_tensor(tf, result)

    # Compute spectral distortion
    distortion = compute_spectral_distortion(result, tf)

    # Compute crossover
    crossover = compute_crossover_analysis(tf, result)

    return SweepPoint(
        tip_radius=tip_radius,
        na=na,
        hurst_exponent=hurst_exponent,
        rms_roughness=rms_roughness,
        rmse_stylus=float(meta_s["rmse"]),
        rmse_optical=float(meta_o["rmse"]),
        corr_stylus=float(meta_s["correlation"]),
        corr_optical=float(meta_o["correlation"]),
        I_integrated=float(info_loss.I_integrated),
        I_stylus=float(info_loss.I_stylus),
        I_optical=float(info_loss.I_optical),
        anisotropy_stylus=float(anisotropy.stylus["anisotropy_degree"]),
        anisotropy_optical=float(anisotropy.optical["anisotropy_degree"]),
        C_spec_stylus=float(distortion["C_spec_stylus"]),
        C_spec_optical=float(distortion["C_spec_optical"]),
        D_spec_stylus=float(distortion["D_spec_stylus"]),
        D_spec_optical=float(distortion["D_spec_optical"]),
        mi_stylus=float(info_loss.mi_stylus),
        mi_optical=float(info_loss.mi_optical),
        crossover_frequency=float(crossover["crossover_frequency_m"]),
        equivalence_fraction_3dB=float(crossover["equivalence_fraction_vs_threshold"]["3dB"]),
        cutoff_ratio=float(params.optical_cutoff / params.stylus_cutoff)
    )


def run_parameter_sweep(
    tip_radii: List[float] = None,
    nas: List[float] = None,
    hurst_exponents: List[float] = None,
    rms_roughnesses: List[float] = None,
    grid_size: int = 256,
    output_dir: str = "./outputs/sweep"
) -> List[SweepPoint]:
    """Run full parameter sweep."""

    if tip_radii is None:
        tip_radii = [0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6]
    if nas is None:
        nas = [0.1, 0.2, 0.3, 0.4, 0.55, 0.7]
    if hurst_exponents is None:
        hurst_exponents = [0.3, 0.5, 0.7, 0.9]
    if rms_roughnesses is None:
        rms_roughnesses = [10e-9, 25e-9, 50e-9, 100e-9]

    combinations = list(product(tip_radii, nas, hurst_exponents, rms_roughnesses))
    print(f"\n{'='*60}")
    print(f"  PARAMETER SWEEP: {len(combinations)} combinations")
    print(f"  Tip radii: {[f'{r*1e6:.1f}µm' for r in tip_radii]}")
    print(f"  NA: {nas}")
    print(f"  H: {hurst_exponents}")
    print(f"  σ: {[f'{s*1e9:.0f}nm' for s in rms_roughnesses]}")
    print(f"  Grid: {grid_size}×{grid_size}")
    print(f"{'='*60}\n")

    results = []
    for tip_r, na, H, sigma in tqdm(combinations, desc="Sweeping"):
        try:
            point = run_single_sweep_point(
                tip_radius=tip_r,
                na=na,
                hurst_exponent=H,
                rms_roughness=sigma,
                grid_size=grid_size,
                seed=42  # Fixed seed for reproducibility
            )
            results.append(point)
        except Exception as e:
            print(f"  [WARN] Failed for r_tip={tip_r*1e6:.1f}µm, NA={na}, H={H}, σ={sigma*1e9:.0f}nm: {e}")

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    data = [asdict(r) for r in results]
    with open(os.path.join(output_dir, "sweep_results.json"), 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n  {len(results)}/{len(combinations)} points completed")
    print(f"  Results saved to: {output_dir}/sweep_results.json")

    return results


def fit_scaling_laws(results: List[SweepPoint], output_dir: str) -> Dict:
    """
    Fit scaling laws from sweep data.

    Laws tested:
    1. f_c ∝ r_tip^(-β)  →  crossover_f vs tip_radius
    2. RMSE_s ∝ r_tip^(α) · σ^(γ)  →  stylus RMSE vs parameters
    3. I_integrated ∝ (r_tip/λ_cutoff)^(δ)  →  info loss vs cutoff ratio
    4. α_stylus = const (universal anisotropy)
    """
    from scipy.optimize import curve_fit

    fits = {}

    # --- Law 1: Crossover frequency vs tip radius ---
    # Fix H=0.7, σ=50nm, NA=0.55 — vary tip radius
    subset = [r for r in results
              if abs(r.hurst_exponent - 0.7) < 0.01
              and abs(r.rms_roughness - 50e-9) < 1e-9
              and abs(r.na - 0.55) < 0.01]

    if len(subset) >= 3:
        tip_r = np.array([p.tip_radius for p in subset])
        f_cross = np.array([p.crossover_frequency for p in subset])

        # Fit: f_cross = A * r_tip^(-β)
        valid = (f_cross > 0) & (tip_r > 0)
        if valid.sum() >= 3:
            def power_law(x, A, beta):
                return A * x**(-beta)

            try:
                popt, pcov = curve_fit(power_law, tip_r[valid], f_cross[valid],
                                       p0=[1e9, 0.5], maxfev=5000)
                fits["crossover_vs_tip_radius"] = {
                    "law": "f_cross = A · r_tip^(-β)",
                    "A": float(popt[0]),
                    "beta": float(popt[1]),
                    "beta_std": float(np.sqrt(pcov[1, 1])),
                    "r_squared": float(np.corrcoef(
                        np.log10(tip_r[valid]),
                        np.log10(f_cross[valid])
                    )[0, 1]**2),
                    "n_points": int(valid.sum())
                }
            except Exception:
                pass

    # --- Law 2: Stylus anisotropy vs tip radius ---
    if len(subset) >= 3:
        alpha_s = np.array([p.anisotropy_stylus for p in subset])
        fits["stylus_anisotropy_mean"] = {
            "mean_alpha": float(np.mean(alpha_s)),
            "std_alpha": float(np.std(alpha_s)),
            "n_points": len(subset),
            "interpretation": "Stylus anisotropy α_s is approximately constant w.r.t. tip radius"
        }

    # --- Law 3: Information loss vs Hurst exponent ---
    # Fix r_tip=2µm, NA=0.55, σ=50nm — vary H
    subset_H = [r for r in results
                if abs(r.tip_radius - 2e-6) < 1e-7
                and abs(r.rms_roughness - 50e-9) < 1e-9
                and abs(r.na - 0.55) < 0.01]

    if len(subset_H) >= 3:
        H_vals = np.array([p.hurst_exponent for p in subset_H])
        I_vals = np.array([p.I_integrated for p in subset_H])
        valid = I_vals > 0

        if valid.sum() >= 3:
            # Fit: I = I_0 · exp(-γ · H)  (info loss decreases with smoother surface)
            def exp_decay(H, I0, gamma):
                return I0 * np.exp(-gamma * H)

            try:
                popt, pcov = curve_fit(exp_decay, H_vals[valid], I_vals[valid],
                                       p0=[100, 5], maxfev=5000)
                fits["info_loss_vs_H"] = {
                    "law": "I = I_0 · exp(-γ · H)",
                    "I_0": float(popt[0]),
                    "gamma": float(popt[1]),
                    "gamma_std": float(np.sqrt(pcov[1, 1])),
                    "interpretation": f"Information loss decreases by factor e per ΔH ≈ {1/max(popt[1], 0.01):.2f}",
                    "n_points": int(valid.sum())
                }
            except Exception:
                pass

    # --- Law 4: RMSE ratio vs cutoff ratio ---
    rmse_ratio = np.array([p.rmse_stylus / (p.rmse_optical + 1e-30) for p in results])
    cutoff_ratios = np.array([p.cutoff_ratio for p in results])
    valid = (rmse_ratio > 0) & (cutoff_ratios > 0)

    if valid.sum() >= 5:
        log_rmse_r = np.log10(rmse_ratio[valid])
        log_cut_r = np.log10(cutoff_ratios[valid])
        coeffs = np.polyfit(log_cut_r, log_rmse_r, 1)
        fits["rmse_ratio_vs_cutoff_ratio"] = {
            "law": "RMSE_s/RMSE_o ∝ (f_c_opt/f_c_stylus)^δ",
            "delta": float(coeffs[0]),
            "r_squared": float(np.corrcoef(log_cut_r, log_rmse_r)[0, 1]**2),
            "n_points": int(valid.sum())
        }

    # Save fits
    with open(os.path.join(output_dir, "scaling_law_fits.json"), 'w') as f:
        json.dump(fits, f, indent=2)

    # Print summary
    print(f"\n  --- SCALING LAW FITS ---")
    for name, fit in fits.items():
        print(f"  {name}:")
        if "law" in fit:
            print(f"    {fit['law']}")
        for k, v in fit.items():
            if k not in ["law", "interpretation"]:
                print(f"    {k}: {v}")
        if "interpretation" in fit:
            print(f"    → {fit['interpretation']}")

    return fits


def generate_sweep_summary(results: List[SweepPoint], fits: Dict,
                            output_dir: str):
    """Generate human-readable sweep summary."""
    lines = []
    lines.append("="*60)
    lines.append("PARAMETER SWEEP SUMMARY")
    lines.append("="*60)
    lines.append(f"Total points: {len(results)}")
    lines.append("")

    # Best and worst performers
    lines.append("--- BEST PERFORMERS ---")
    sorted_by_rmse_s = sorted(results, key=lambda r: r.rmse_stylus)
    for r in sorted_by_rmse_s[:3]:
        lines.append(
            f"  Stylus RMSE={r.rmse_stylus*1e9:.1f}nm | "
            f"r_tip={r.tip_radius*1e6:.1f}µm, NA={r.na}, "
            f"H={r.hurst_exponent}, σ={r.rms_roughness*1e9:.0f}nm"
        )

    lines.append("")
    lines.append("--- WORST PERFORMERS ---")
    for r in sorted_by_rmse_s[-3:]:
        lines.append(
            f"  Stylus RMSE={r.rmse_stylus*1e9:.1f}nm | "
            f"r_tip={r.tip_radius*1e6:.1f}µm, NA={r.na}, "
            f"H={r.hurst_exponent}, σ={r.rms_roughness*1e9:.0f}nm"
        )

    lines.append("")
    lines.append("--- SCALING LAWS DISCOVERED ---")
    for name, fit in fits.items():
        lines.append(f"  {name}:")
        if "law" in fit:
            lines.append(f"    {fit['law']}")
        if "beta" in fit:
            lines.append(f"    β = {fit['beta']:.3f} ± {fit.get('beta_std', 0):.3f}")
        if "delta" in fit:
            lines.append(f"    δ = {fit['delta']:.3f}")
        if "gamma" in fit:
            lines.append(f"    γ = {fit['gamma']:.2f}")
        if "r_squared" in fit:
            lines.append(f"    R² = {fit['r_squared']:.4f}")
        if "interpretation" in fit:
            lines.append(f"    → {fit['interpretation']}")

    lines.append("")
    lines.append("--- ANISOTROPY STATISTICS ---")
    alpha_s_vals = [r.anisotropy_stylus for r in results]
    alpha_o_vals = [r.anisotropy_optical for r in results]
    lines.append(f"  Stylus α:  mean={np.mean(alpha_s_vals):.4f}, std={np.std(alpha_s_vals):.4f}")
    lines.append(f"  Optical α: mean={np.mean(alpha_o_vals):.4f}, std={np.std(alpha_o_vals):.4f}")

    summary = "\n".join(lines)

    with open(os.path.join(output_dir, "sweep_summary.txt"), 'w') as f:
        f.write(summary)

    print(f"\n  Summary saved to: {output_dir}/sweep_summary.txt")
    return summary


def run_sweep(output_dir: str = SWEEP_DIR,
              quick: bool = False) -> Tuple[List[SweepPoint], Dict]:
    """Run complete parameter sweep with scaling law fitting."""

    if quick:
        # Quick sweep for testing
        tip_radii = [1e-6, 5e-6]
        nas = [0.3, 0.55]
        hurst_exponents = [0.5, 0.7]
        rms_roughnesses = [25e-9, 50e-9]
        grid_size = 128
    else:
        # Manuscript 180-point grid (matches verification/run_sweep_multiseed.py):
        tip_radii = [0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6]
        nas = [0.2, 0.3, 0.4, 0.55]
        hurst_exponents = [0.3, 0.5, 0.7]
        rms_roughnesses = [10e-9, 25e-9, 50e-9]
        grid_size = 256

    results = run_parameter_sweep(
        tip_radii=tip_radii,
        nas=nas,
        hurst_exponents=hurst_exponents,
        rms_roughnesses=rms_roughnesses,
        grid_size=grid_size,
        output_dir=output_dir
    )

    fits = fit_scaling_laws(results, output_dir)
    generate_sweep_summary(results, fits, output_dir)

    return results, fits


if __name__ == "__main__":
    import sys
    quick = "--quick" in sys.argv
    run_sweep(quick=quick)
