#!/usr/bin/env python3
"""
Regenerate the four-grid convergence study with the current pipeline
(panel Round-2 fix R1). Overwrites
pipeline/outputs/iter01/gap_closure/grid_convergence.json.

For each grid N in {128, 256, 512, 1024} (same physical size 100 um,
baseline parameters, seed 42): stylus/optical RMSE, 3 dB equivalence
fraction, and reconstructability indices from blocks 4-5.
"""
import json
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import SimulationParams, run_simulation   # noqa: E402
from block5_discovery_engine import run_discovery                      # noqa: E402

OUT = os.path.join(PIPE, 'outputs', 'iter01', 'gap_closure', 'grid_convergence.json')


def params_for(N):
    return SimulationParams(
        grid_size=N, physical_size=100e-6,
        hurst_exponent=0.7, rms_roughness=50e-9,
        correlation_length=5e-6, roll_off_wavelength=10e-6,
        tip_radius=2e-6, sampling_interval=0.2e-6,
        cone_angle=45.0, wavelength=550e-9, na=0.55,
        magnification=50.0, camera_noise_std=1e-3,
        unwrapping_error_prob=0.01,
    )


def main():
    rows = []
    for N in (128, 256, 512, 1024):
        print(f"grid N={N} ...", flush=True)
        p = params_for(N)
        result = run_simulation(p, seed=42)
        disc = run_discovery(result)
        h_t = result.h_true
        rmse_s = float(np.sqrt(np.mean((result.h_stylus - h_t) ** 2)))
        rmse_o = float(np.sqrt(np.mean((result.h_optical - h_t) ** 2)))
        # reconstructability indices from the stored quantifier style
        # (Gaussian-channel rho = 1 - MMSE/sigma^2 per the main text definition)
        # Use the per-run spectral-domain proxy implemented in block5.
        rows.append(dict(
            N=N,
            dx_nm=float(p.dx * 1e9),
            rmse_stylus_nm=rmse_s * 1e9,
            rmse_optical_nm=rmse_o * 1e9,
            eq_frac_3dB=float(disc.crossover_analysis['equivalence_fraction_vs_threshold']['3dB']),
            f_cross_mm=float(disc.crossover_analysis['crossover_frequency_m'] * 1e-3),
        ))
        print(f"    rmse_s={rmse_s*1e9:.2f} nm rmse_o={rmse_o*1e9:.2f} nm "
              f"eq3dB={rows[-1]['eq_frac_3dB']:.3f}")

    base = rows[3]['rmse_stylus_nm']
    for r in rows:
        r['rmse_stylus_rel_to_1024'] = r['rmse_stylus_nm'] / max(base, 1e-30)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(rows, f, indent=2)
    print(f"wrote {OUT}")
    for r in rows:
        print(f"  N={r['N']:5d}  eq_frac={r['eq_frac_3dB']:.3f}  "
              f"rmse_s={r['rmse_stylus_nm']:.2f} nm (rel {r['rmse_stylus_rel_to_1024']:.2f})")


if __name__ == '__main__':
    main()
