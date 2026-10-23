#!/usr/bin/env python3
"""Acceptance pass, Tier 1a: multi-realisation (multi-seed) parameter sweep.

Re-runs the exact 180-point sweep grid of parameter_sweep.py with independent
surface realisations (seeds 43 and 44; the committed baseline used seed 42) and
recomputes, per seed, the log--log scaling-law statistics:
  - exponent (slope), SE, in-sample R2
  - random 80/20 out-of-sample R2 (seed 0 split, manuscript convention)
  - blocked leave-one-(tip,NA)-group-out R2
  - median / 90th-percentile relative prediction error
  - crossover-vs-tip-radius exponent (f_cross ~ r_tip^-beta)
  - stylus / optical anisotropy means over the grid

Also reports across-seed spread for the headline quantities, so the manuscript
can replace the single-realisation caveat with a realised-generalisation
statement.

Writes:
  pipeline/outputs/sweep/sweep_results_seed43.json
  pipeline/outputs/sweep/sweep_results_seed44.json
  reports/sweep_multiseed_audit.json
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

TIPS = [0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6]
NAS = [0.2, 0.3, 0.4, 0.55]
HS = [0.3, 0.5, 0.7]
SIGMAS = [10e-9, 25e-9, 50e-9]
SEEDS = [42, 43, 44]  # 42 = committed baseline, re-run for identical stats code


def grid():
    for tip in TIPS:
        for na in NAS:
            for h in HS:
                for sig in SIGMAS:
                    yield tip, na, h, sig


def load_or_run(seed):
    """Run the grid for `seed`, cache to JSON, return list of dicts."""
    out = os.path.join(PIPE, 'outputs', 'sweep', f'sweep_results_seed{seed}.json')
    if seed == 42 and os.path.exists(os.path.join(PIPE, 'outputs', 'sweep', 'sweep_results.json')):
        with open(os.path.join(PIPE, 'outputs', 'sweep', 'sweep_results.json')) as f:
            data = json.load(f)
        return data
    if os.path.exists(out):
        with open(out) as f:
            return json.load(f)
    rows = []
    n = len(TIPS) * len(NAS) * len(HS) * len(SIGMAS)
    for i, (tip, na, h, sig) in enumerate(grid()):
        p = run_single_sweep_point(tip, na, h, sig, grid_size=256, seed=seed)
        rows.append({
            'tip_radius': p.tip_radius, 'na': p.na,
            'hurst_exponent': p.hurst_exponent, 'rms_roughness': p.rms_roughness,
            'rmse_stylus': p.rmse_stylus, 'rmse_optical': p.rmse_optical,
            'I_integrated': p.I_integrated,
            'anisotropy_stylus': p.anisotropy_stylus,
            'anisotropy_optical': p.anisotropy_optical,
            'crossover_frequency': p.crossover_frequency,
            'equivalence_fraction_3dB': p.equivalence_fraction_3dB,
            'cutoff_ratio': p.cutoff_ratio,
        })
        if (i + 1) % 30 == 0:
            print(f'  seed {seed}: {i+1}/{n}', flush=True)
    with open(out, 'w') as f:
        json.dump(rows, f, indent=2)
    return rows


def lsq(xx, yy):
    A = np.polyfit(xx, yy, 1)
    resid = yy - np.polyval(A, xx)
    s2 = np.sum(resid ** 2) / max(len(yy) - 2, 1)
    X = np.vstack([np.ones(len(xx)), xx]).T
    cov = s2 * np.linalg.inv(X.T @ X)
    r2 = np.corrcoef(xx, yy)[0, 1] ** 2
    return A[0], np.sqrt(cov[1, 1]), A[1], np.sqrt(cov[0, 0]), r2


def r2_pred(yy, pp):
    return 1 - np.sum((yy - pp) ** 2) / np.sum((yy - yy.mean()) ** 2)


def stats(rows):
    cr = np.array([r['cutoff_ratio'] for r in rows])
    rr = np.array([r['rmse_stylus'] / r['rmse_optical'] for r in rows])
    tip = np.array([r['tip_radius'] for r in rows])
    na = np.array([r['na'] for r in rows])
    mask = (cr > 0) & (rr > 0) & np.isfinite(rr)
    x = np.log10(cr[mask]); y = np.log10(rr[mask])
    slope, se, b, seb, r2_in = lsq(x, y)

    rng = np.random.RandomState(0)
    idx = np.where(mask)[0]; rng.shuffle(idx)
    ntr = int(0.8 * len(idx)); tr, te = idx[:ntr], idx[ntr:]
    A = np.polyfit(x[tr], y[tr], 1)
    r2_out = r2_pred(y[te], np.polyval(A, x[te]))

    groups = {}
    for i in np.where(mask)[0]:
        groups.setdefault((tip[i], na[i]), []).append(i)
    yb, pb = [], []
    for key, members in groups.items():
        tr_g = [j for g, mem in groups.items() if g != key for j in mem]
        if not tr_g:
            continue
        Ab = np.polyfit(x[tr_g], y[tr_g], 1)
        yb.append(y[members]); pb.append(np.polyval(Ab, x[members]))
    yb = np.concatenate(yb); pb = np.concatenate(pb)
    r2_blocked = r2_pred(yb, pb)

    A_full = np.polyfit(x, y, 1)
    ratio_err = np.abs(rr[mask] / 10 ** np.polyval(A_full, x) - 1)
    med = np.median(ratio_err); p90 = np.percentile(ratio_err, 90)

    # crossover vs tip radius (H=0.7, sigma=50nm, NA=0.55 subset)
    sub = [r for r in rows
           if abs(r['hurst_exponent'] - 0.7) < 1e-9
           and abs(r['rms_roughness'] - 50e-9) < 1e-12
           and abs(r['na'] - 0.55) < 1e-9]
    tr_ = np.array([r['tip_radius'] for r in sub])
    fc = np.array([r['crossover_frequency'] for r in sub])
    beta, bse, _, _, r2_beta = lsq(np.log10(tr_), np.log10(fc))
    beta = -beta

    alpha_s = np.array([r['anisotropy_stylus'] for r in rows])
    alpha_o = np.array([r['anisotropy_optical'] for r in rows])
    eq = np.array([r['equivalence_fraction_3dB'] for r in rows])
    fc_all = np.array([r['crossover_frequency'] for r in rows])

    return {
        'n_points': int(mask.sum()),
        'slope': float(slope), 'slope_se': float(se),
        'intercept_log10': float(b), 'intercept_se': float(seb),
        'r2_in': float(r2_in), 'r2_out_8020': float(r2_out),
        'r2_blocked': float(r2_blocked),
        'median_rel_error_ratio': float(med), 'p90_rel_error_ratio': float(p90),
        'beta_tip': float(beta), 'beta_tip_se': float(bse), 'r2_beta_tip': float(r2_beta),
        'alpha_stylus_mean': float(alpha_s.mean()), 'alpha_stylus_std': float(alpha_s.std()),
        'alpha_optical_mean': float(alpha_o.mean()), 'alpha_optical_std': float(alpha_o.std()),
        'eq_frac_3dB_mean': float(eq.mean()), 'eq_frac_3dB_std': float(eq.std()),
        'f_cross_mean_mm': float(fc_all.mean() * 1e-3), 'f_cross_std_mm': float(fc_all.std() * 1e-3),
    }


def main():
    per_seed = {}
    for seed in SEEDS:
        rows = load_or_run(seed)
        per_seed[str(seed)] = stats(rows)

    slopes = [per_seed[str(s)]['slope'] for s in SEEDS]
    r2ins = [per_seed[str(s)]['r2_in'] for s in SEEDS]
    r2outs = [per_seed[str(s)]['r2_out_8020'] for s in SEEDS]
    r2blk = [per_seed[str(s)]['r2_blocked'] for s in SEEDS]
    audit = {
        'grid': {'tips_um': [t * 1e6 for t in TIPS], 'na': NAS,
                 'H': HS, 'sigma_nm': [s * 1e9 for s in SIGMAS]},
        'per_seed': per_seed,
        'across_seeds': {
            'slope_mean': float(np.mean(slopes)), 'slope_std': float(np.std(slopes)),
            'slope_min': float(np.min(slopes)), 'slope_max': float(np.max(slopes)),
            'r2_in_range': [float(np.min(r2ins)), float(np.max(r2ins))],
            'r2_out_range': [float(np.min(r2outs)), float(np.max(r2outs))],
            'r2_blocked_range': [float(np.min(r2blk)), float(np.max(r2blk))],
            'conclusion': ('slope std across independent realisations vs the '
                           'within-fit SE decides whether the law generalises '
                           'across surfaces, not only across parameters'),
        },
        'design_note': ('same 180-combination grid, N=256, per-combination one '
                        'realisation; seeds 43/44 are new independent surfaces'),
    }
    os.makedirs(REP, exist_ok=True)
    with open(os.path.join(REP, 'sweep_multiseed_audit.json'), 'w') as f:
        json.dump(audit, f, indent=2)
    print(json.dumps(audit['across_seeds'], indent=2))
    print('per-seed slope/SE:', {str(s): (round(per_seed[str(s)]['slope'], 3), round(per_seed[str(s)]['slope_se'], 3)) for s in SEEDS})


if __name__ == '__main__':
    main()
