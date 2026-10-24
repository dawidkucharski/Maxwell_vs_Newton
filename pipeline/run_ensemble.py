#!/usr/bin/env python3
"""
Regenerate ensemble_stats.json from code (panel fix T4).

30 baseline simulations (grid 512, seed = 100 + i) -> block5 discovery per seed.
Aggregates the same scalar/array statistics as the committed file:
f_radial, H_stylus_mean/std, H_optical_mean/std, I_mean/std, rmse means/stds,
corr means/stds, alpha means/stds, f_cross mean/std, eq_frac mean/std, N_ensemble.

Runtime: ~30 x (simulation + discovery) on a 512^2 grid.
"""
import json
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import SimulationParams, run_simulation   # noqa: E402
from block5_discovery_engine import run_discovery, azimuthal_average     # noqa: E402
from variant_simulations import psd2d                                    # noqa: E402

N = 30
SEED0 = 100
OUT = os.path.join(PIPE, 'outputs', 'iter01', 'ensemble')


def baseline_params():
    return SimulationParams(
        grid_size=512, physical_size=100e-6,
        hurst_exponent=0.7, rms_roughness=50e-9,
        correlation_length=5e-6, roll_off_wavelength=10e-6,
        tip_radius=2e-6, sampling_interval=0.2e-6,
        cone_angle=45.0, wavelength=550e-9, na=0.55,
        magnification=50.0, camera_noise_std=1e-3,
        unwrapping_error_prob=0.01,
    )


def main():
    params = baseline_params()
    f_radial = None
    H_s = []  # H_stylus_1d per run
    H_o = []  # H_optical_1d per run
    I_1d = []
    rmse_s, rmse_o, corr_s, corr_o = [], [], [], []
    alpha_s, alpha_o = [], []
    f_cross, eq_frac = [], []
    mi_s, mi_o = [], []
    I_s, I_o = [], []
    I_band = {}

    for i in range(N):
        seed = SEED0 + i
        print(f"ensemble run {i+1}/{N} (seed={seed}) ...", flush=True)
        result = run_simulation(params, seed=seed)
        disc = run_discovery(result)

        tf = disc.transfer_functions
        if f_radial is None:
            f_radial = np.array(tf.f_radial)
        # Manuscript-consistent estimator (T10): ratio of azimuthal means of
        # Hanning-windowed periodograms, on the same radial grid as block5.
        Pt = psd2d(result.h_true, result.params.dx)
        Ps = psd2d(result.h_stylus, result.params.dx)
        Po = psd2d(result.h_optical, result.params.dx)
        _, Pta = azimuthal_average(Pt, result.fx, result.fy)
        _, Psa = azimuthal_average(Ps, result.fx, result.fy)
        _, Poa = azimuthal_average(Po, result.fx, result.fy)
        H_s.append(Psa / np.maximum(Pta, 1e-30))
        H_o.append(Poa / np.maximum(Pta, 1e-30))
        I_1d.append(np.array(disc.information_loss.I_radial))

        h_t = result.h_true
        rmse_s.append(np.sqrt(np.mean((result.h_stylus - h_t) ** 2)))
        rmse_o.append(np.sqrt(np.mean((result.h_optical - h_t) ** 2)))
        corr_s.append(np.corrcoef(result.h_stylus.ravel(), h_t.ravel())[0, 1])
        corr_o.append(np.corrcoef(result.h_optical.ravel(), h_t.ravel())[0, 1])
        alpha_s.append(disc.anisotropy.stylus['anisotropy_degree'])
        alpha_o.append(disc.anisotropy.optical['anisotropy_degree'])
        f_cross.append(disc.crossover_analysis['crossover_frequency_m'])
        eq_frac.append(disc.crossover_analysis['equivalence_fraction_vs_threshold']['3dB'])
        il = disc.information_loss
        mi_s.append(il.mi_stylus)
        mi_o.append(il.mi_optical)
        I_s.append(il.I_stylus)
        I_o.append(il.I_optical)
        for band, val in il.I_per_band.items():
            I_band.setdefault(band, []).append(val)

    def arr(x):
        return np.asarray(x)

    stats = {
        'f_radial': f_radial.tolist(),
        'H_stylus_mean': arr(H_s).mean(axis=0).tolist(),
        'H_stylus_std': arr(H_s).std(axis=0).tolist(),
        'H_optical_mean': arr(H_o).mean(axis=0).tolist(),
        'H_optical_std': arr(H_o).std(axis=0).tolist(),
        'I_mean': arr(I_1d).mean(axis=0).tolist(),
        'I_std': arr(I_1d).std(axis=0).tolist(),
        'rmse_stylus_mean': float(arr(rmse_s).mean()),
        'rmse_stylus_std': float(arr(rmse_s).std()),
        'rmse_optical_mean': float(arr(rmse_o).mean()),
        'rmse_optical_std': float(arr(rmse_o).std()),
        'corr_stylus_mean': float(arr(corr_s).mean()),
        'corr_stylus_std': float(arr(corr_s).std()),
        'corr_optical_mean': float(arr(corr_o).mean()),
        'corr_optical_std': float(arr(corr_o).std()),
        'alpha_stylus_mean': float(arr(alpha_s).mean()),
        'alpha_stylus_std': float(arr(alpha_s).std()),
        'alpha_optical_mean': float(arr(alpha_o).mean()),
        'alpha_optical_std': float(arr(alpha_o).std()),
        'f_cross_mean': float(arr(f_cross).mean()),
        'f_cross_std': float(arr(f_cross).std()),
        'eq_frac_mean': float(arr(eq_frac).mean()),
        'eq_frac_std': float(arr(eq_frac).std()),
        'mi_stylus_mean': float(arr(mi_s).mean()),
        'mi_stylus_std': float(arr(mi_s).std()),
        'mi_optical_mean': float(arr(mi_o).mean()),
        'mi_optical_std': float(arr(mi_o).std()),
        'I_stylus_mean': float(arr(I_s).mean()),
        'I_stylus_std': float(arr(I_s).std()),
        'I_optical_mean': float(arr(I_o).mean()),
        'I_optical_std': float(arr(I_o).std()),
        'I_per_band': {b: [float(np.mean(v)), float(np.std(v))] for b, v in I_band.items()},
        'N_ensemble': N,
        'seeds': list(range(SEED0, SEED0 + N)),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'ensemble_stats.json'), 'w') as f:
        json.dump(stats, f, indent=2)

    print("\nENSEMBLE STATS (n=30, seeds 100-129)")
    print(f"  alpha_s = {stats['alpha_stylus_mean']:.4f} +/- {stats['alpha_stylus_std']:.4f}")
    print(f"  alpha_o = {stats['alpha_optical_mean']:.4f} +/- {stats['alpha_optical_std']:.4f}")
    print(f"  f_cross = {stats['f_cross_mean']*1e-3:.1f} +/- {stats['f_cross_std']*1e-3:.1f} mm-1")
    print(f"  eq_frac(3dB) = {stats['eq_frac_mean']:.4f} +/- {stats['eq_frac_std']:.4f}")
    print(f"  rmse_s = {stats['rmse_stylus_mean']*1e9:.1f} +/- {stats['rmse_stylus_std']*1e9:.1f} nm")
    print(f"  rmse_o = {stats['rmse_optical_mean']*1e9:.1f} +/- {stats['rmse_optical_std']*1e9:.1f} nm")
    print(f"  corr_s = {stats['corr_stylus_mean']:.4f}, corr_o = {stats['corr_optical_mean']:.4f}")
    print(f"  MI proxy: s = {stats['mi_stylus_mean']:.3f} +/- {stats['mi_stylus_std']:.3f}, "
          f"o = {stats['mi_optical_mean']:.3f} +/- {stats['mi_optical_std']:.3f}")
    print(f"  I integrated: s = {stats['I_stylus_mean']:.3e} +/- {stats['I_stylus_std']:.3e}, "
          f"o = {stats['I_optical_mean']:.3e} +/- {stats['I_optical_std']:.3e}")
    print(f"  I per band: {stats['I_per_band']}")


if __name__ == '__main__':
    main()
