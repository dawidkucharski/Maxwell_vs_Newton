#!/usr/bin/env python3
"""Held-out check of the k-space fusion demonstration (Priority-6 follow-up).

Replicates the figS2 fusion exactly (same weights and noise floors) on the
tuning surface (seed 42) and on independent realisations (seeds 777, 999),
and reports band-averaged |log10(PSD_est/PSD_true)| for each modality and
the fused estimate. Writes reports/fusion_holdout_audit.json.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
from block4_physics_simulator import (SimulationParams,
                                      generate_self_affine_surface,
                                      simulate_stylus, simulate_optical)
from block10_scatterometry import simulate_scatterometry
from block5_discovery_engine import compute_psd_2d, azimuthal_average

REP = os.path.join(ROOT, 'reports')
os.makedirs(REP, exist_ok=True)


def band_accuracy(psd_est_1d, psd_true_1d, f_1d):
    m = (f_1d > 10e3) & (f_1d < 3.76e6) & (psd_true_1d > 0) & (psd_est_1d > 0)
    return float(np.mean(np.abs(np.log10(psd_est_1d[m] / psd_true_1d[m]))))


def run(seed):
    p = SimulationParams()
    h_true = generate_self_affine_surface(p, seed=seed)
    h_s, _ = simulate_stylus(h_true, p)
    h_o, _ = simulate_optical(h_true, p)
    psd_sc, _, _ = simulate_scatterometry(h_true, p)

    Pt = compute_psd_2d(h_true, p.dx)
    Ps = compute_psd_2d(h_s, p.dx)
    Po = compute_psd_2d(h_o, p.dx)
    f_r, pt = azimuthal_average(Pt, p.fx if hasattr(p, 'fx') else np.fft.fftfreq(p.grid_size, p.dx),
                                np.fft.fftfreq(p.grid_size, p.dx))
    _, ps = azimuthal_average(Ps, np.fft.fftfreq(p.grid_size, p.dx), np.fft.fftfreq(p.grid_size, p.dx))
    _, po = azimuthal_average(Po, np.fft.fftfreq(p.grid_size, p.dx), np.fft.fftfreq(p.grid_size, p.dx))
    _, psc = azimuthal_average(psd_sc, np.fft.fftfreq(p.grid_size, p.dx), np.fft.fftfreq(p.grid_size, p.dx))

    H_s = ps / np.maximum(pt, 1e-35)
    H_o = po / np.maximum(pt, 1e-35)
    H_sc = psc / np.maximum(pt, 1e-35)

    def nf(x):
        return np.quantile(x[x > 0], 0.05) if np.any(x > 0) else 1e-35
    n_s, n_o, n_sc = nf(ps), nf(po), nf(psc)
    w_s = np.clip(H_s, 0, 10) ** 2 / max(n_s, 1e-35)
    w_o = np.clip(H_o, 0, 10) ** 2 / max(n_o, 1e-35)
    w_sc = np.clip(H_sc, 0, 10) ** 2 / max(n_sc, 1e-35)
    fused = (ps * w_s + po * w_o + psc * w_sc) / np.maximum(w_s + w_o + w_sc, 1e-35)

    return {
        'seed': seed,
        'mean_abs_log10_error': {
            'stylus': band_accuracy(ps, pt, f_r),
            'wli': band_accuracy(po, pt, f_r),
            'scatterometry': band_accuracy(psc, pt, f_r),
            'fused': band_accuracy(fused, pt, f_r),
        },
    }

out = {'tuning': run(42), 'held_out': [run(777), run(999)]}
with open(os.path.join(REP, 'fusion_holdout_audit.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
