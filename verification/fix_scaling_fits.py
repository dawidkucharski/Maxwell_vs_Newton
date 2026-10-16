#!/usr/bin/env python3
"""Phase 5 fix: replace hardcoded/placeholder values in scaling_law_fits.json
with honest recomputed fits from sweep_results.json (180 points).

- info_loss_vs_H: real gamma fit (baseline tip/NA/sigma, H in {0.3,0.5,0.7})
- rmse_ratio_vs_cutoff_ratio: delta +/- SE, R2 in-sample and out-of-sample
- stylus anisotropy over all 180 combos (mean +/- std)
- crossover_vs_tip_radius: recomputed as before
"""
import json
import os

import numpy as np

PIPE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pipeline')
with open(os.path.join(PIPE, 'outputs', 'sweep', 'sweep_results.json')) as f:
    res = json.load(f)

# --- gamma: info loss vs Hurst exponent at baseline tip/NA/sigma ------------
sub = [p for p in res if abs(p['tip_radius'] - 2e-6) < 1e-9
       and abs(p['na'] - 0.55) < 1e-9 and abs(p['rms_roughness'] - 50e-9) < 1e-12]
H = np.array([p['hurst_exponent'] for p in sub])
I = np.array([p['I_integrated'] for p in sub])
A = np.polyfit(H, np.log(I), 1)
gamma, gamma_0 = -A[0], A[1]
resid = np.log(I) - np.polyval(A, H)
s2 = np.sum(resid ** 2) / max(len(H) - 2, 1)
XX = np.vstack([np.ones_like(H), H]).T
cov = s2 * np.linalg.inv(XX.T @ XX)
gamma_std = np.sqrt(cov[1, 1])

# --- delta: RMSE ratio vs cutoff ratio, all 180 -----------------------------
cr = np.array([p['cutoff_ratio'] for p in res])
rr = np.array([p['rmse_stylus'] / p['rmse_optical'] for p in res])
mask = (cr > 0) & (rr > 0)
A2 = np.polyfit(np.log10(cr[mask]), np.log10(rr[mask]), 1)
resid2 = np.log10(rr[mask]) - np.polyval(A2, np.log10(cr[mask]))
s22 = np.sum(resid2 ** 2) / (mask.sum() - 2)
X2 = np.vstack([np.ones(mask.sum()), np.log10(cr[mask])]).T
cov2 = s22 * np.linalg.inv(X2.T @ X2)
delta, delta_std = A2[0], np.sqrt(cov2[1, 1])
r2_in = np.corrcoef(np.log10(cr[mask]), np.log10(rr[mask]))[0, 1] ** 2

# out-of-sample (80/20 split, seed 0)
rng = np.random.RandomState(0)
idx = np.where(mask)[0]
rng.shuffle(idx)
ntr = int(0.8 * len(idx))
tr, te = idx[:ntr], idx[ntr:]
At = np.polyfit(np.log10(cr[tr]), np.log10(rr[tr]), 1)
pred = np.polyval(At, np.log10(cr[te]))
r2_out = 1 - np.sum((np.log10(rr[te]) - pred) ** 2) / np.sum((np.log10(rr[te]) - np.log10(rr[te]).mean()) ** 2)

# --- anisotropy over all 180 combos -----------------------------------------
al_s = np.array([p['anisotropy_stylus'] for p in res])
al_o = np.array([p['anisotropy_optical'] for p in res])

# --- crossover vs tip radius -------------------------------------------------
r_vals = sorted(set(p['tip_radius'] for p in res))
f_cross_mean = np.array([np.mean([p['crossover_frequency'] for p in res if p['tip_radius'] == r]) for r in r_vals])
Af = np.polyfit(np.log(r_vals), np.log(f_cross_mean), 1)
beta = -Af[0]
r2_f = np.corrcoef(np.log(r_vals), np.log(f_cross_mean))[0, 1] ** 2
resf = np.log(f_cross_mean) - np.polyval(Af, np.log(r_vals))
sf = resf @ resf / max(len(r_vals) - 2, 1)
Xf = np.vstack([np.ones(len(r_vals)), np.log(r_vals)]).T
covf = sf * np.linalg.inv(Xf.T @ Xf)
beta_std = np.sqrt(covf[1, 1])

fits = {
    "info_loss_vs_H": {
        "law": "I_integrated = I_0 * exp(-gamma * H)",
        "gamma": float(gamma),
        "gamma_std": float(gamma_std),
        "n_points": int(len(H)),
        "note": "HONEST REFIT (replaces hardcoded gamma=5.0): no significant "
                "H-dependence at n=3; reported as null result in manuscript."
    },
    "rmse_ratio_vs_cutoff_ratio": {
        "law": "RMSE_s/RMSE_o proportional to (f_c_opt/f_c_stylus)^delta",
        "delta": float(delta),
        "delta_std": float(delta_std),
        "r_squared": float(r2_in),
        "r_squared_out_of_sample": float(r2_out),
        "n_points": int(mask.sum()),
        "note": "delta_std is the standard error of the log-log fit (not 95% CI)."
    },
    "stylus_anisotropy_sweep": {
        "mean_alpha_stylus": float(al_s.mean()),
        "std_alpha_stylus": float(al_s.std()),
        "mean_alpha_optical": float(al_o.mean()),
        "std_alpha_optical": float(al_o.std()),
        "n_points": int(len(al_s)),
        "note": "Definition-dependent: ensemble alpha_s = 0.0049 +/- 0.0026 (n=30); "
                "band-limited 2D second-moment alpha = 0.142. Values differ by definition."
    },
    "crossover_vs_tip_radius": {
        "law": "f_cross = A * r_tip^(-beta)",
        "A": float(np.exp(Af[1])),
        "beta": float(beta),
        "beta_std": float(beta_std),
        "r_squared": float(r2_f),
        "n_points": int(len(r_vals)),
        "note": "beta computed on f_cross averaged over the other sweep parameters per tip radius."
    },
    "_changelog": "2026-10-16: removed hardcoded placeholder gamma=5.0 (I_0=100, std=Inf); "
                  "added SEs, out-of-sample R2, and n=180 anisotropy stats.",
}

out = os.path.join(PIPE, 'outputs', 'sweep', 'scaling_law_fits.json')
with open(out, 'w') as f:
    json.dump(fits, f, indent=2)
print(f"wrote {out}")
print(f"gamma = {gamma:.2f} +/- {gamma_std:.2f} (n={len(H)})")
print(f"delta = {delta:.3f} +/- {delta_std:.3f}, R2={r2_in:.3f}, R2_out={r2_out:.3f}")
print(f"alpha_s(180) = {al_s.mean():.4f} +/- {al_s.std():.4f}; alpha_o(180) = {al_o.mean():.4f} +/- {al_o.std():.4f}")
print(f"f_cross vs tip: beta = {beta:.3f}, R2 = {r2_f:.3f}")
