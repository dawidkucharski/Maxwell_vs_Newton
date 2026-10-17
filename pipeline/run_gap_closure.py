#!/usr/bin/env python3
"""
Generator for the 432-point gap-closure sweep (Round-2 fix R9/R10).

grid N=256, baseline parameters otherwise; sweeps NA x noise_multiplier x
wavelength (4 x 9 x 12 = 432 combos), computing the 3 dB equivalence fraction
and reconstructability indices, and writes
pipeline/outputs/iter01/gap_closure/gap_closure_sweep.json.

Full run: ~432 x (simulation + discovery). For validation use --limit K.

Usage:
    python run_gap_closure.py            # full sweep (long)
    python run_gap_closure.py --limit 2  # 2 combos, writes to *_preview.json
"""
import argparse
import json
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import SimulationParams, run_simulation   # noqa: E402
from block5_discovery_engine import run_discovery                      # noqa: E402

N = 256


def params_for(na, wavelength_nm, noise_mult):
    return SimulationParams(
        grid_size=N, physical_size=100e-6,
        hurst_exponent=0.7, rms_roughness=50e-9,
        correlation_length=5e-6, roll_off_wavelength=10e-6,
        tip_radius=2e-6, sampling_interval=0.2e-6,
        cone_angle=45.0, wavelength=wavelength_nm * 1e-9, na=na,
        magnification=50.0, camera_noise_std=1e-3 * noise_mult,
        unwrapping_error_prob=0.01,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='only run first K combos (preview)')
    args = ap.parse_args()

    nas = [0.3, 0.55, 0.8, 0.9]
    wavs = [400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0, 850.0, 900.0, 950.0]
    noises = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]

    combos = [(na, w, nm) for na in nas for w in wavs for nm in noises]
    if args.limit:
        combos = combos[:args.limit]

    rows = []
    for k, (na, w, nm) in enumerate(combos):
        print(f"combo {k+1}/{len(combos)}: NA={na}, lam={w:.0f}nm, noise={nm} ...", flush=True)
        p = params_for(na, w, nm)
        result = run_simulation(p, seed=42)
        disc = run_discovery(result)
        rows.append(dict(
            NA=na, noise_mult=nm, wavelength_nm=w,
            f_c_opt_mm=float(2 * na / (w * 1e-9) * 1e-3),
            eq_fraction=float(disc.crossover_analysis['equivalence_fraction_vs_threshold']['3dB']),
        ))

    out_dir = os.path.join(PIPE, 'outputs', 'iter01', 'gap_closure')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'gap_closure_sweep_preview.json' if args.limit else 'gap_closure_sweep.json')
    with open(out, 'w') as f:
        json.dump({'results': rows}, f, indent=2)
    print(f'wrote {out} ({len(rows)} combos)')


if __name__ == '__main__':
    main()
