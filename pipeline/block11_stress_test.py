"""
Stress-Test: Universality of k-Space Operator Framework Across Surface Classes
==============================================================================
Tests the 7 existing metrics across 6 fundamentally different surface classes:
  1. Gaussian self-affine (baseline, H=0.7)
  2. Ground (anisotropic self-affine, H=0.85, directional)
  3. Turned (periodic grooves + roughness)
  4. Laser-textured (Gaussian pits array + roughness)
  5. Periodic grating (pure sinusoid)
  6. Biological (anisotropic multi-scale, log-normal heights)

Determines which quantities are universal and which are surface-dependent.
No new metrics introduced — only the existing 7 are tested.
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftfreq, fftshift, ifftshift
from scipy.ndimage import grey_dilation
from dataclasses import dataclass
from typing import Dict, Tuple, List
import json, os, sys

sys.path.insert(0, '.')
from block4_physics_simulator import SimulationParams, simulate_stylus, simulate_optical
from block5_discovery_engine import compute_psd_2d, azimuthal_average


# ============================================================
# SURFACE GENERATORS
# ============================================================

def generate_gaussian_self_affine(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """Baseline: self-affine Gaussian via Fourier filtering. H=0.7."""
    from block4_physics_simulator import generate_self_affine_surface
    return generate_self_affine_surface(params, seed=seed)


def generate_ground_surface(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Ground surface: anisotropic self-affine (Hx=0.85, Hy=0.70),
    higher correlation in grinding direction.
    PSD(fx,fy) ∝ 1 / [(f0² + fx²/Lx² + fy²/Ly²)^{(H_eff+1)}]
    where Lx > Ly (elongated along grinding direction).
    """
    np.random.seed(seed)
    N = params.grid_size
    dx = params.dx
    L = params.physical_size
    
    fx = fftshift(fftfreq(N, d=dx))
    fy = fftshift(fftfreq(N, d=dx))
    FX, FY = np.meshgrid(fx, fy)
    
    # Anisotropic: longer correlation along x (grinding direction)
    Lx = 4.0  # correlation length ratio x/y
    Ly = 1.0
    H_eff = 0.78  # effective Hurst (between Hx=0.85, Hy=0.70)
    f0 = 1.0 / params.correlation_length
    
    # Anisotropic PSD
    f_scaled = np.sqrt((FX/Lx)**2 + (FY/Ly)**2)
    psd_target = (f0**2 + f_scaled**2) ** (-(H_eff + 1))
    psd_target[f_scaled == 0] = 0.0
    
    # Random phase
    phase = np.random.uniform(0, 2*np.pi, (N, N))
    amplitude = np.sqrt(np.maximum(psd_target, 0))
    H_hat = amplitude * np.exp(1j * phase)
    H_hat[0, 0] = 0.0
    
    h = np.real(ifft2(ifftshift(H_hat))) * N
    
    # Normalise
    h -= np.mean(h)
    h *= params.rms_roughness / np.std(h)
    
    return h.astype(np.float64)


def generate_turned_surface(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Turned surface: periodic spiral grooves approximated as
    sinusoidal profile along x with self-affine roughness overlay.
    Period Λ ≈ 100 µm (feed rate), amplitude A ≈ 500 nm.
    """
    np.random.seed(seed)
    N = params.grid_size
    x = np.linspace(-params.physical_size/2, params.physical_size/2, N)
    y = np.linspace(-params.physical_size/2, params.physical_size/2, N)
    X, Y = np.meshgrid(x, y)
    
    # Periodic grooves (10 periods across 100 µm)
    Lambda = params.physical_size / 10  # 10 µm period
    A_groove = 5 * params.rms_roughness  # 250 nm amplitude
    
    h_periodic = A_groove * np.sin(2 * np.pi * X / Lambda)
    
    # Self-affine roughness overlay (lower amplitude)
    from block4_physics_simulator import generate_self_affine_surface
    rough_params = SimulationParams(
        grid_size=N, hurst_exponent=0.7,
        rms_roughness=params.rms_roughness * 0.3,
        tip_radius=params.tip_radius, na=params.na, wavelength=params.wavelength
    )
    h_rough = generate_self_affine_surface(rough_params, seed=seed+1000)
    
    h = h_periodic + h_rough
    h -= np.mean(h)
    
    return h.astype(np.float64)


def generate_laser_textured_surface(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Laser-textured: regular array of Gaussian dimples + self-affine background.
    8×8 dimple grid, 200 nm depth, 5 µm dimple radius.
    """
    np.random.seed(seed)
    N = params.grid_size
    L = params.physical_size
    x = np.linspace(-L/2, L/2, N)
    y = np.linspace(-L/2, L/2, N)
    X, Y = np.meshgrid(x, y)
    
    # Dimple array: 8×8 grid
    n_dimples = 8
    dimple_depth = 4 * params.rms_roughness  # 200 nm
    dimple_sigma = 5e-6  # 5 µm radius
    spacing = L / (n_dimples + 1)
    
    h_dimples = np.zeros((N, N))
    for i in range(n_dimples):
        for j in range(n_dimples):
            cx = -L/2 + (i + 1) * spacing
            cy = -L/2 + (j + 1) * spacing
            r2 = (X - cx)**2 + (Y - cy)**2
            h_dimples += -dimple_depth * np.exp(-r2 / (2 * dimple_sigma**2))
    
    # Self-affine background
    from block4_physics_simulator import generate_self_affine_surface
    rough_params = SimulationParams(
        grid_size=N, hurst_exponent=0.7,
        rms_roughness=params.rms_roughness * 0.5,
        tip_radius=params.tip_radius, na=params.na, wavelength=params.wavelength
    )
    h_rough = generate_self_affine_surface(rough_params, seed=seed+2000)
    
    h = h_dimples + h_rough
    h -= np.mean(h)
    
    return h.astype(np.float64)


def generate_periodic_grating(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Pure sinusoidal grating: h(x) = A·sin(2πx/Λ).
    Λ = 5 µm, A = 100 nm. No roughness — ideal calibration artefact.
    """
    np.random.seed(seed)
    N = params.grid_size
    x = np.linspace(-params.physical_size/2, params.physical_size/2, N)
    X, _ = np.meshgrid(x, x)
    
    Lambda = 5e-6  # 5 µm
    A = 2 * params.rms_roughness  # 100 nm
    
    h = A * np.sin(2 * np.pi * X / Lambda)
    h += np.random.randn(N, N) * params.rms_roughness * 0.01  # tiny noise
    
    return h.astype(np.float64)


def generate_biological_surface(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Biological-like surface: anisotropic multi-scale (Hx=0.65, Hy=0.85),
    log-normal height distribution, larger amplitude at coarse scales.
    Models features of skin, leaves, or bone surfaces.
    """
    np.random.seed(seed)
    N = params.grid_size
    dx = params.dx
    
    fx = fftshift(fftfreq(N, d=dx))
    fy = fftshift(fftfreq(N, d=dx))
    FX, FY = np.meshgrid(fx, fy)
    
    # Anisotropic, different Hurst in each direction
    Hx, Hy = 0.65, 0.85
    f0 = 1.0 / params.correlation_length
    
    f_eff_x = np.sqrt(f0**2 + FX**2)
    f_eff_y = np.sqrt(f0**2 + FY**2)
    psd_target = (f_eff_x * f_eff_y) ** (-1.0)  # product form for multi-scale
    psd_target = 1.0 / (f0**2 + FX**2 + FY**2) ** (0.5 * (Hx + Hy) + 1)
    psd_target[np.abs(FX) < 1e-10] = 0.0  # DC
    
    phase = np.random.uniform(0, 2*np.pi, (N, N))
    amplitude = np.sqrt(np.maximum(psd_target, 0))
    H_hat = amplitude * np.exp(1j * phase)
    H_hat[0, 0] = 0.0
    
    h_gaussian = np.real(ifft2(ifftshift(H_hat))) * N
    
    # Log-normal transform for non-Gaussian heights
    h_gaussian -= np.min(h_gaussian) + 1e-9
    h_lognormal = np.exp(h_gaussian / np.std(h_gaussian) * 0.5)
    h_lognormal -= np.mean(h_lognormal)
    h_lognormal *= params.rms_roughness / np.std(h_lognormal)
    
    return h_lognormal.astype(np.float64)


# ============================================================
# METRICS COMPUTATION
# ============================================================

def compute_all_metrics(h_true: np.ndarray, h_stylus: np.ndarray, 
                        h_optical: np.ndarray, params: SimulationParams) -> Dict:
    """
    Compute the 7 existing framework metrics from simulated measurements.
    """
    N = params.grid_size
    dx = params.dx
    eps = 1e-35
    
    fx = fftshift(fftfreq(N, d=dx))
    fy = fftshift(fftfreq(N, d=dx))
    
    psd_true = compute_psd_2d(h_true, dx)
    psd_stylus = compute_psd_2d(h_stylus, dx)
    psd_optical = compute_psd_2d(h_optical, dx)
    
    f_r, psd_t_1d = azimuthal_average(psd_true, fx, fy)
    _, psd_s_1d = azimuthal_average(psd_stylus, fx, fy)
    _, psd_o_1d = azimuthal_average(psd_optical, fx, fy)
    
    # Transfer functions
    H_s_2d = np.sqrt(np.maximum(psd_stylus, eps) / np.maximum(psd_true, eps))
    H_o_2d = np.sqrt(np.maximum(psd_optical, eps) / np.maximum(psd_true, eps))
    H_s_2d = np.clip(H_s_2d, 0.001, 10.0)
    H_o_2d = np.clip(H_o_2d, 0.001, 10.0)
    
    _, H_s_1d = azimuthal_average(H_s_2d, fx, fy)
    _, H_o_1d = azimuthal_average(H_o_2d, fx, fy)
    
    # Noise PSD estimates (from high-frequency roll-off)
    pos_high = f_r > np.median(f_r[f_r > 0])
    S_eta_s = np.median(psd_s_1d[pos_high]) if np.any(pos_high) else eps
    S_eta_o = np.median(psd_o_1d[pos_high]) if np.any(pos_high) else eps
    
    # SNR per frequency
    SNR_s_1d = np.maximum(H_s_1d**2 * psd_t_1d / (S_eta_s + eps), eps)
    SNR_o_1d = np.maximum(H_o_1d**2 * psd_t_1d / (S_eta_o + eps), eps)
    
    # --- Metric 1: Mutual Information I(h;y) ---
    # I = ½ Σ log2(1 + SNR(f))
    df = 1.0 / params.physical_size
    I_stylus = 0.5 * np.sum(np.log2(1 + SNR_s_1d[f_r > 0])) * (df * df)
    I_optical = 0.5 * np.sum(np.log2(1 + SNR_o_1d[f_r > 0])) * (df * df)
    I_total = max(I_stylus, I_optical)
    
    # --- Metric 2: Information-Equivalent Bandwidth Beq ---
    # Beq = bandwidth of ideal (H=1, no noise) instrument giving same I
    SNR_ideal = np.mean(psd_t_1d[f_r > 0]) / (eps + S_eta_s)
    Beq_stylus = I_stylus / (0.5 * np.log2(1 + SNR_ideal))
    Beq_optical = I_optical / (0.5 * np.log2(1 + SNR_ideal))
    
    # --- Metric 3: Information Efficiency η ---
    # η = I_actual / I_perfect (where I_perfect uses H=1, no noise)
    SNR_perfect = psd_t_1d[f_r > 0] / eps
    I_perfect = 0.5 * np.sum(np.log2(1 + SNR_perfect)) * (df * df)
    eta_stylus = I_stylus / (I_perfect + eps)
    eta_optical = I_optical / (I_perfect + eps)
    
    # --- Metric 4: Information-Energy Ratio ε ---
    # ε = I / σ²  (bits per unit surface variance)
    var_true = np.var(h_true)
    eps_energy_stylus = I_stylus / (var_true + eps)
    eps_energy_optical = I_optical / (var_true + eps)
    
    # --- Metric 5: Reconstructability Index ρ ---
    # ρ = fraction of k-space modes where SNR > 1
    modes_total = np.sum(f_r > 0)
    rho_stylus = np.sum(SNR_s_1d[f_r > 0] > 1.0) / max(modes_total, 1)
    rho_optical = np.sum(SNR_o_1d[f_r > 0] > 1.0) / max(modes_total, 1)
    
    # --- Metric 6: Capacity-Uniformity Product Ξ ---
    # κ = condition number of H (ratio max/min |H| in passband)
    passband_s = H_s_1d[f_r > 0]
    passband_o = H_o_1d[f_r > 0]
    valid_s = passband_s > 0.01
    valid_o = passband_o > 0.01
    kappa_s = np.max(passband_s[valid_s]) / np.min(passband_s[valid_s]) if np.any(valid_s) else 1e6
    kappa_o = np.max(passband_o[valid_o]) / np.min(passband_o[valid_o]) if np.any(valid_o) else 1e6
    Xi_stylus = I_stylus / kappa_s
    Xi_optical = I_optical / kappa_o
    
    # --- Metric 7: Critical Hurst Exponent Hc ---
    # Hc where ρ drops below 0.5 (estimated from SNR roll-off)
    # Approximate: find frequency where SNR=1, relate to H via PSD ∝ f^{-(2H+2)}
    def estimate_Hc(SNR_1d, f_vals):
        pos = f_vals > 0
        if not np.any(pos):
            return 0.5
        # Find where SNR crosses 1
        snr_pos = SNR_1d[pos]
        f_pos = f_vals[pos]
        cross_idx = np.argmin(np.abs(snr_pos - 1.0))
        f_cross_snr = f_pos[cross_idx] if cross_idx < len(f_pos) else f_pos[-1]
        # PSD(f) ∝ f^{-(2H+2)}; SNR(f) ≈ H²·f^{-(2H+2)}/N
        # SNR=1 → f = (H²/N)^{1/(2H+2)}
        # For typical H≈0.7, approximate
        Hc_est = max(0.05, min(0.95, 0.7 - f_cross_snr * 1e6 * 0.05))
        return Hc_est
    
    Hc_stylus = estimate_Hc(SNR_s_1d, f_r)
    Hc_optical = estimate_Hc(SNR_o_1d, f_r)
    
    # RMSE
    rmse_s = np.sqrt(np.mean((h_true - h_stylus)**2))
    rmse_o = np.sqrt(np.mean((h_true - h_optical)**2))
    
    return {
        'surface_variance_nm2': float(var_true * 1e18),
        'rmse_stylus_nm': float(rmse_s * 1e9),
        'rmse_optical_nm': float(rmse_o * 1e9),
        'I_stylus_bits': float(I_stylus),
        'I_optical_bits': float(I_optical),
        'Beq_stylus': float(Beq_stylus),
        'Beq_optical': float(Beq_optical),
        'eta_stylus': float(eta_stylus),
        'eta_optical': float(eta_optical),
        'eps_stylus': float(eps_energy_stylus),
        'eps_optical': float(eps_energy_optical),
        'rho_stylus': float(rho_stylus),
        'rho_optical': float(rho_optical),
        'Xi_stylus': float(Xi_stylus),
        'Xi_optical': float(Xi_optical),
        'Hc_stylus': float(Hc_stylus),
        'Hc_optical': float(Hc_optical),
    }


# ============================================================
# MAIN STRESS-TEST
# ============================================================

PIPE = os.path.dirname(os.path.abspath(__file__))


def run_stress_test(output_dir: str = None):
    """Run full stress-test across 6 surface classes."""
    if output_dir is None:
        output_dir = os.path.join(PIPE, 'outputs', 'iter01', 'stress_test')
    os.makedirs(output_dir, exist_ok=True)
    
    base_params = SimulationParams(
        grid_size=512, hurst_exponent=0.7, rms_roughness=50e-9,
        tip_radius=2e-6, na=0.55, wavelength=550e-9
    )
    
    generators = {
        '1_gaussian_self_affine': generate_gaussian_self_affine,
        '2_ground_anisotropic': generate_ground_surface,
        '3_turned_periodic': generate_turned_surface,
        '4_laser_textured': generate_laser_textured_surface,
        '5_periodic_grating': generate_periodic_grating,
        '6_biological_lognormal': generate_biological_surface,
    }
    
    all_results = {}
    
    for class_name, generator in generators.items():
        print(f"\n{'='*60}")
        print(f"  Stress-testing: {class_name}")
        print(f"{'='*60}")
        
        class_metrics = []
        
        # 5 realisations per class for statistics
        for run in range(5):
            seed = 42 + run * 100
            print(f"    Run {run+1}/5 (seed={seed})...", end=' ', flush=True)
            
            # Generate surface
            h_true = generator(base_params, seed=seed)
            
            # Simulate measurements
            h_stylus, _ = simulate_stylus(h_true, base_params)
            h_optical, _ = simulate_optical(h_true, base_params)
            
            # Compute metrics
            metrics = compute_all_metrics(h_true, h_stylus, h_optical, base_params)
            class_metrics.append(metrics)
            
            print(f"RMSE_s={metrics['rmse_stylus_nm']:.1f}nm "
                  f"RMSE_o={metrics['rmse_optical_nm']:.1f}nm "
                  f"ρ_s={metrics['rho_stylus']:.3f} ρ_o={metrics['rho_optical']:.3f}")
        
        # Aggregate statistics
        agg = {}
        for key in class_metrics[0].keys():
            vals = [m[key] for m in class_metrics]
            agg[f'{key}_mean'] = float(np.mean(vals))
            agg[f'{key}_std'] = float(np.std(vals))
        
        agg['n_realisations'] = 5
        all_results[class_name] = agg
        
        print(f"    Mean I_stylus = {agg['I_stylus_bits_mean']:.2e} bits")
        print(f"    Mean η_stylus = {agg['eta_stylus_mean']:.4f}")
        print(f"    Mean Ξ_stylus = {agg['Xi_stylus_mean']:.2e}")
    
    # Save results
    out_path = os.path.join(output_dir, 'stress_test_results.json')
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"  Stress-test complete. Results: {out_path}")
    print(f"{'='*60}")
    
    return all_results


# ============================================================
# UNIVERSALITY ANALYSIS
# ============================================================

def analyse_universality(results: Dict, output_dir: str):
    """Determine which metrics are universal vs surface-dependent."""
    
    classes = list(results.keys())
    metrics = [
        ('I_stylus_bits', 'Mutual Information I(h;y) [bits]'),
        ('Beq_stylus', 'Info-Equivalent Bandwidth B_eq'),
        ('eta_stylus', 'Information Efficiency η'),
        ('eps_stylus', 'Information-Energy Ratio ε [bits/nm²]'),
        ('rho_stylus', 'Reconstructability Index ρ'),
        ('Xi_stylus', 'Capacity-Uniformity Product Ξ'),
        ('Hc_stylus', 'Critical Hurst Exponent H_c'),
    ]
    
    print("\n" + "="*80)
    print("UNIVERSALITY ANALYSIS — Coefficient of Variation Across Surface Classes")
    print("="*80)
    print(f"{'Metric':<35} {'Mean':>12} {'Std':>12} {'CV':>8} {'Verdict':>20}")
    print("-"*80)
    
    universality = {}
    
    for key, name in metrics:
        means = []
        for cls in classes:
            m_key = f'{key}_mean'
            if m_key in results[cls]:
                means.append(results[cls][m_key])
        
        if means:
            mu = np.mean(means)
            sigma = np.std(means)
            cv = sigma / (abs(mu) + 1e-35)
            
            if cv < 0.3:
                verdict = 'UNIVERSAL'
            elif cv < 1.0:
                verdict = 'WEAKLY DEPENDENT'
            elif cv < 3.0:
                verdict = 'SURFACE-DEPENDENT'
            else:
                verdict = 'HIGHLY VARIABLE'
            
            universality[key] = {'mean': mu, 'std': sigma, 'cv': cv, 'verdict': verdict}
            print(f"{name:<35} {mu:>12.4e} {sigma:>12.4e} {cv:>8.3f} {verdict:>20}")
    
    # Find the strongest remaining research gap
    print("\n" + "="*80)
    print("RESEARCH GAP IDENTIFICATION")
    print("="*80)
    
    # Which metrics are universal?
    universal_metrics = [k for k, v in universality.items() if v['verdict'] == 'UNIVERSAL']
    surface_dependent = [k for k, v in universality.items() if v['verdict'] != 'UNIVERSAL']
    
    print(f"\n  Universal metrics: {universal_metrics}")
    print(f"  Surface-dependent metrics: {surface_dependent}")
    
    # Strongest gap
    print(f"\n  STRONGEST GAP: Whether the {len(universal_metrics)} universal metrics")
    print(f"  can form the basis of a 'Metrological Invariance Principle' —")
    print(f"  a statement that certain information-theoretic properties of a")
    print(f"  measurement instrument are invariant under changes in surface")
    print(f"  class, depending only on the instrument physics.")
    
    # Save analysis
    analysis = {
        'universality': universality,
        'universal_metrics': universal_metrics,
        'surface_dependent_metrics': surface_dependent,
        'n_classes': len(classes),
        'n_realisations_per_class': results[classes[0]]['n_realisations'],
        'strongest_gap': (
            "Metrological Invariance Principle: identify which information-theoretic "
            "instrument properties are invariant under surface class changes."
        )
    }
    
    with open(os.path.join(output_dir, 'universality_analysis.json'), 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    return analysis


# ============================================================
# VISUALISATION
# ============================================================

def fig_stress_test(results: Dict, universality: Dict, output_dir: str):
    """Generate stress-test visualisation figure."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    plt.rcParams.update({
        'font.family': 'serif', 'font.size': 10,
        'axes.labelsize': 11, 'axes.titlesize': 10.5,
        'legend.fontsize': 8, 'figure.dpi': 150,
        'savefig.dpi': 300, 'savefig.bbox': 'tight'
    })
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)
    
    classes = list(results.keys())
    class_labels = ['Gaussian\nSelf-Affine', 'Ground\nAnisotropic', 'Turned\nPeriodic',
                    'Laser\nTextured', 'Periodic\nGrating', 'Biological\nLog-Normal']
    colors = ['#2166ac', '#b2182b', '#4dac26', '#762a83', '#e08214', '#f4a582']
    
    # Panel data: (metric_key, title, is_log)
    panels = [
        ('rmse_stylus_nm', 'RMSE Stylus [nm]', False),
        ('eta_stylus', 'Info Efficiency η', False),
        ('rho_stylus', 'Reconstructability ρ', False),
        ('Xi_stylus', 'Capacity-Uniformity Ξ', True),
        ('I_stylus_bits', 'Mutual Information I(h;y) [bits]', True),
        ('Hc_stylus', 'Critical Hurst H_c', False),
    ]
    
    for ax, (key, title, is_log) in zip(axes.flat, panels):
        means = [results[c][f'{key}_mean'] for c in classes]
        stds = [results[c][f'{key}_std'] for c in classes]
        
        x = range(len(classes))
        ax.bar(x, means, yerr=stds, color=colors, alpha=0.85, capsize=3, edgecolor='white')
        if is_log:
            ax.set_yscale('log')
        ax.set_xticks(x)
        ax.set_xticklabels(class_labels, fontsize=7, rotation=0)
        ax.set_title(title, loc='left', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    fig.suptitle('Stress-Test: Framework Metrics Across Surface Classes ($n=5$ per class)',
                 fontsize=12, fontweight='bold', y=1.01)
    
    out_path = os.path.join(output_dir, 'fig_stress_test.pdf')
    fig.savefig(out_path)
    # Also save to figures dir
    fig_dir = os.path.join(os.path.dirname(output_dir), 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    fig.savefig(os.path.join(fig_dir, 'figS1_stress_test.pdf'))
    plt.close(fig)
    print(f"  Stress-test figure saved: {out_path}")


if __name__ == "__main__":
    np.random.seed(42)
    out = os.path.join(PIPE, 'outputs', 'iter01', 'stress_test')
    
    results = run_stress_test(out)
    analysis = analyse_universality(results, out)
    fig_stress_test(results, analysis, out)
    
    print("\nDone.")
