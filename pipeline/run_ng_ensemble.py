#!/usr/bin/env python3
"""Generator for the non-Gaussian manufactured-surface ensemble (SI S5).

Three manufactured surface classes (the block11 stress-test generators),
n = 20 realisations each (seeds 42 + 100*r, matching the stress-test
seed scheme), stylus and optical channels simulated at baseline
parameters (N = 512), metrics computed with
block11.compute_all_metrics (the same estimator set as the six-class
stress test; reconstructability rho and information efficiency eta
follow the stress-test conventions).

Per class reports mean +/- std / CV of: stylus RMSE, information
efficiency eta, reconstructability rho, mutual information I_s, and the
stylus anisotropy degree alpha_s (block5 anisotropy-tensor convention).

Writes: pipeline/outputs/iter01/ensemble_non_gaussian/ng_ensemble.json
"""
import json
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import (SimulationParams, SimulationResult,
                                      simulate_stylus, simulate_optical)
from block5_discovery_engine import (compute_transfer_functions,
                                     compute_anisotropy_tensor)
from block11_stress_test import (generate_ground_surface,
                                 generate_turned_surface,
                                 generate_laser_textured_surface,
                                 compute_all_metrics)

OUT_DIR = os.path.join(PIPE, 'outputs', 'iter01', 'ensemble_non_gaussian')
BASE = SimulationParams(grid_size=512)
N_RUNS = 20


def class_metrics(generator):
    keys = ['rmse_stylus_nm', 'eta_stylus', 'rho_stylus', 'I_stylus_bits']
    vals = {k: [] for k in keys}
    alphas = []
    for r in range(N_RUNS):
        seed = 42 + 100 * r
        h_true = generator(BASE, seed=seed)
        h_s, _ = simulate_stylus(h_true, BASE)
        h_o, _ = simulate_optical(h_true, BASE)
        m = compute_all_metrics(h_true, h_s, h_o, BASE)
        for k in keys:
            vals[k].append(m[k])

        # stylus anisotropy degree (block5 tensor convention)
        fx = np.fft.fftshift(np.fft.fftfreq(BASE.grid_size, d=BASE.dx))
        res = SimulationResult(params=BASE, h_true=h_true, h_stylus=h_s,
                               h_optical=h_o, fx=fx, fy=fx)
        tf = compute_transfer_functions(res, smooth_sigma=0)
        alpha = compute_anisotropy_tensor(tf, res).stylus['anisotropy_degree']
        alphas.append(alpha)

    out = {'N': N_RUNS, 'seed_scheme': '42 + 100*r', 'grid': BASE.grid_size}
    for k in keys:
        a = np.array(vals[k])
        tag = {'rmse_stylus_nm': 'rmse_s', 'eta_stylus': 'eta',
               'rho_stylus': 'rho', 'I_stylus_bits': 'I_s'}[k]
        out[f'{tag}_mean'] = float(a.mean())
        out[f'{tag}_std'] = float(a.std(ddof=1))
        out[f'{tag}_cv'] = float(a.std(ddof=1) / a.mean())
    a = np.array(alphas)
    out['alpha_mean'] = float(a.mean())
    out['alpha_std'] = float(a.std(ddof=1))
    out['alpha_cv'] = float(a.std(ddof=1) / a.mean())
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = {}
    for name, generator in [
        ('ground', generate_ground_surface),
        ('turned', generate_turned_surface),
        ('laser_textured', generate_laser_textured_surface),
    ]:
        print(f'class {name}: {N_RUNS} realisations ...', flush=True)
        results[name] = class_metrics(generator)
        print(f"  rho = {results[name]['rho_mean']:.4f} +/- "
              f"{results[name]['rho_std']:.4f} | eta = "
              f"{results[name]['eta_mean']:.4f} +/- "
              f"{results[name]['eta_std']:.4f} | alpha_s = "
              f"{results[name]['alpha_mean']:.4f} +/- "
              f"{results[name]['alpha_std']:.4f}")

    out = {
        'method': ('block11 stress-test generators; block11.compute_all_metrics '
                   '(rho = fraction of azimuthal bins with SNR > 1, eta = '
                   'I/I_perfect); alpha_s = block5 anisotropy-tensor degree; '
                   'N=512, seeds 42+100r, r=0..19.'),
        **results,
    }
    with open(os.path.join(OUT_DIR, 'ng_ensemble.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print('wrote', os.path.join(OUT_DIR, 'ng_ensemble.json'))


if __name__ == '__main__':
    main()
