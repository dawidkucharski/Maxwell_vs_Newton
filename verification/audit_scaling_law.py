#!/usr/bin/env python3
"""Priority-9 audit: re-test the empirical scaling law.

RMSE_s/RMSE_o vs (f_c_opt/f_c_stylus)^delta over the 180-point sweep.

Checks:
- slope, SE, in-sample R2 (plain log-log LSQ)
- out-of-sample R2: random 80/20 (seed 0, as manuscript) AND blocked CV
  (leave-one-(tip,NA)-group-out, leave-one-tip-out, leave-one-NA-out)
- constant-ratio baseline (R2 of null model)
- residual structure vs each parameter (confounding)
- predictive error in original units (multiplicative RMSE ratio error)
- cutoff convention: NA/lambda vs 2NA/lambda (slope invariance)

Writes reports/scaling_law_audit.json.
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')

with open(os.path.join(PIPE, 'outputs', 'sweep', 'sweep_results.json')) as f:
    res = json.load(f)

cr = np.array([p['cutoff_ratio'] for p in res])
rr = np.array([p['rmse_stylus'] / p['rmse_optical'] for p in res])
tip = np.array([p['tip_radius'] for p in res])
na = np.array([p['na'] for p in res])
H = np.array([p['hurst_exponent'] for p in res])
sig = np.array([p['rms_roughness'] for p in res])
mask = (cr > 0) & (rr > 0) & np.isfinite(rr)
x = np.log10(cr[mask]); y = np.log10(rr[mask])

def lsq(xx, yy):
    A = np.polyfit(xx, yy, 1)
    resid = yy - np.polyval(A, xx)
    s2 = np.sum(resid ** 2) / max(len(yy) - 2, 1)
    X = np.vstack([np.ones(len(xx)), xx]).T
    cov = s2 * np.linalg.inv(X.T @ X)
    r2 = np.corrcoef(xx, yy)[0, 1] ** 2
    return A[0], np.sqrt(cov[1, 1]), r2

def r2_pred(yy, pp):
    return 1 - np.sum((yy - pp) ** 2) / np.sum((yy - yy.mean()) ** 2)

slope, se, r2_in = lsq(x, y)

# --- random 80/20 (manuscript convention, seed 0) ---------------------------
rng = np.random.RandomState(0)
idx = np.where(mask)[0]
rng.shuffle(idx)
ntr = int(0.8 * len(idx))
At = np.polyfit(x[idx[:ntr]], y[idx[:ntr]], 1)
r2_rand_out = r2_pred(y[idx[ntr:]], np.polyval(At, x[idx[ntr:]]))

# --- blocked CV: leave-one-(tip,NA)-group-out --------------------------------
groups = {}
for i in np.where(mask)[0]:
    groups.setdefault((tip[i], na[i]), []).append(i)
r2_block, preds = [], []
for key, members in groups.items():
    tr = [j for g, mem in groups.items() if g != key for j in mem]
    te = members
    if not tr:
        continue
    Ab = np.polyfit(x[tr], y[tr], 1)
    pp = np.polyval(Ab, x[te])
    r2_block.append((y[te], pp))
yb = np.concatenate([v[0] for v in r2_block]); pb = np.concatenate([v[1] for v in r2_block])
r2_blocked = r2_pred(yb, pb)

# --- leave-one-tip-out -------------------------------------------------------
r2_tip = []
for t in set(tip[mask]):
    tr = [j for j in np.where(mask)[0] if tip[j] != t]
    te = [j for j in np.where(mask)[0] if tip[j] == t]
    Ab = np.polyfit(x[tr], y[tr], 1)
    r2_tip.append((y[te], np.polyval(Ab, x[te])))
yb = np.concatenate([v[0] for v in r2_tip]); pb = np.concatenate([v[1] for v in r2_tip])
r2_leave_tip = r2_pred(yb, pb)

# --- leave-one-NA-out --------------------------------------------------------
r2_na = []
for a in set(na[mask]):
    tr = [j for j in np.where(mask)[0] if na[j] != a]
    te = [j for j in np.where(mask)[0] if na[j] == a]
    Ab = np.polyfit(x[tr], y[tr], 1)
    r2_na.append((y[te], np.polyval(Ab, x[te])))
yb = np.concatenate([v[0] for v in r2_na]); pb = np.concatenate([v[1] for v in r2_na])
r2_leave_na = r2_pred(yb, pb)

# --- constant-ratio baseline --------------------------------------------------
r2_null = r2_pred(y, np.full_like(y, y.mean()))

# --- predictive error in original units --------------------------------------
A_full = np.polyfit(x, y, 1)
ratio_err = np.abs(rr[mask] / 10 ** np.polyval(A_full, x) - 1)
med_err = np.median(ratio_err)
p90_err = np.percentile(ratio_err, 90)

# --- residual correlation with parameters (confounding) ----------------------
resid = y - np.polyval(A_full, x)
def corr_p(v):
    return float(np.corrcoef(resid, np.log10(v[mask]))[0, 1])
confound = {
    'resid_vs_tip': corr_p(tip),
    'resid_vs_na': corr_p(na),
    'resid_vs_H': corr_p(H),
    'resid_vs_sigma': corr_p(sig),
}

# --- slope invariance to cutoff convention (NA/lambda vs 2NA/lambda) ---------
slope2, se2, r2_in2 = lsq(np.log10(2 * cr[mask]), y)

audit = {
    'n_points': int(mask.sum()),
    'slope': float(slope), 'slope_se': float(se), 'r2_in': float(r2_in),
    'r2_random_8020': float(r2_rand_out),
    'r2_blocked_leave_group_out': float(r2_blocked),
    'r2_leave_tip_out': float(r2_leave_tip),
    'r2_leave_na_out': float(r2_leave_na),
    'r2_constant_baseline': float(r2_null),
    'median_relative_error_ratio': float(med_err),
    'p90_relative_error_ratio': float(p90_err),
    'residual_confounding': confound,
    'slope_with_2NA_lambda_convention': float(slope2),
    'convention_note': 'sweep cutoff_ratio uses NA/lambda; slope is invariant '
                       'to the constant factor 2 (2NA/lambda), only the fitted '
                       'prefactor shifts.',
    'design_note': 'all 180 combos share one surface realisation (seed 42); '
                   'random 80/20 tests parameter interpolation for a fixed '
                   'realisation, not realisation generalisation.',
}

os.makedirs(REP, exist_ok=True)
with open(os.path.join(REP, 'scaling_law_audit.json'), 'w') as f:
    json.dump(audit, f, indent=2)
print(json.dumps(audit, indent=2))
