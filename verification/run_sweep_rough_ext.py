#!/usr/bin/env python3
"""Acceptance pass, Tier 1b: rough-surface extension of the parameter sweep.

The decision matrix 'rough' row (sigma > 50 nm -> optical recommended) currently
extrapolates from the sigma <= 50 nm sweep. This script extends the comparison
to sigma = 75/100/150/200 nm on a focused grid (tip x H x NA), so the row can be
grounded in data rather than extrapolation.

Grid: tips {0.5, 2, 5} um x NA {0.3, 0.55} x H {0.3, 0.5} x sigma {75,100,150,200} nm
N = 256 (same grid as the committed sweep, for comparability).
Seeds: 42 and 43 (two independent realisations).

Writes reports/rough_extension_audit.json
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')
sys.path.insert(0, PIPE)

from parameter_sweep import run_single_sweep_point  # noqa: E402

TIPS = [0.5e-6, 2e-6, 5e-6]
NAS = [0.3, 0.55]
HS = [0.3, 0.5]
SIGMAS = [75e-9, 100e-9, 150e-9, 200e-9]
SEEDS = [42, 43]


def main():
    rows = []
    total = len(TIPS) * len(NAS) * len(HS) * len(SIGMAS) * len(SEEDS)
    i = 0
    for seed in SEEDS:
        for tip in TIPS:
            for na in NAS:
                for h in HS:
                    for sig in SIGMAS:
                        p = run_single_sweep_point(tip, na, h, sig, grid_size=256, seed=seed)
                        rows.append({
                            'seed': seed, 'tip_um': tip * 1e6, 'na': na, 'H': h,
                            'sigma_nm': sig * 1e9,
                            'rmse_stylus_nm': p.rmse_stylus * 1e9,
                            'rmse_optical_nm': p.rmse_optical * 1e9,
                            'ratio_s_o': p.rmse_stylus / max(p.rmse_optical, 1e-30),
                            'eq_frac_3dB': p.equivalence_fraction_3dB,
                            'f_cross_mm': p.crossover_frequency * 1e-3,
                        })
                        i += 1
                        if i % 24 == 0:
                            print(f'  {i}/{total}', flush=True)

    r = rows
    rough = [x for x in r if x['sigma_nm'] >= 100]
    opt_wins = sum(1 for x in rough if x['ratio_s_o'] > 1.0)
    sty_wins = sum(1 for x in rough if x['ratio_s_o'] <= 1.0)
    ratios = np.array([x['ratio_s_o'] for x in rough])

    # stylus RMSE growth with sigma (super-linearity check), baseline tip 2um NA 0.55
    sub = sorted([x for x in r if abs(x['tip_um'] - 2.0) < 1e-9 and abs(x['na'] - 0.55) < 1e-9
                  and abs(x['H'] - 0.3) < 1e-9 and x['seed'] == 42], key=lambda x: x['sigma_nm'])
    sig_ = np.array([x['sigma_nm'] for x in sub])
    rms_s = np.array([x['rmse_stylus_nm'] for x in sub])
    rms_o = np.array([x['rmse_optical_nm'] for x in sub])
    growth = None
    if len(sig_) >= 4:
        A = np.polyfit(np.log10(sig_), np.log10(rms_s), 1)
        growth = {'stylus_rmse_sigma_exponent': float(A[0]), 'r2': float(np.corrcoef(np.log10(sig_), np.log10(rms_s))[0, 1] ** 2)}

    by_sigma = {}
    for s in SIGMAS:
        sub = [x for x in r if abs(x['sigma_nm'] - s * 1e9) < 1e-6]
        by_sigma[f"{s*1e9:.0f}nm"] = {
            'n': len(sub),
            'optical_wins_fraction': float(np.mean([1.0 if x['ratio_s_o'] > 1 else 0.0 for x in sub])),
            'ratio_s_o_median': float(np.median([x['ratio_s_o'] for x in sub])),
            'ratio_s_o_min': float(np.min([x['ratio_s_o'] for x in sub])),
            'ratio_s_o_max': float(np.max([x['ratio_s_o'] for x in sub])),
        }

    audit = {
        'grid_note': 'tips {0.5,2,5} um x NA {0.3,0.55} x H {0.3,0.5} x sigma {75,100,150,200} nm, N=256, seeds 42+43',
        'n_total': len(r),
        'sigma_ge_100nm': {
            'n': len(rough),
            'optical_wins': int(opt_wins),
            'stylus_wins': int(sty_wins),
            'optical_wins_fraction': float(opt_wins / max(len(rough), 1)),
            'ratio_s_o_median': float(np.median(ratios)),
            'ratio_s_o_p10': float(np.percentile(ratios, 10)),
            'ratio_s_o_p90': float(np.percentile(ratios, 90)),
        },
        'by_sigma': by_sigma,
        'stylus_growth': growth,
        'interpretation': ('"optical wins" = RMSE_s/RMSE_o > 1 (stylus RMSE larger). '
                           'If optical_wins_fraction is high for sigma >= 100 nm, the '
                           'decision-matrix rough row is grounded in data over 100-200 nm, '
                           'not extrapolated.'),
    }
    os.makedirs(REP, exist_ok=True)
    with open(os.path.join(REP, 'rough_extension_audit.json'), 'w') as f:
        json.dump(audit, f, indent=2)
    print(json.dumps(audit['sigma_ge_100nm'], indent=2))
    print(json.dumps(by_sigma, indent=2))
    print('growth:', growth)


if __name__ == '__main__':
    main()
