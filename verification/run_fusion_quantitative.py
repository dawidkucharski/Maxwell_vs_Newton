#!/usr/bin/env python3
"""Acceptance pass, Tier 1c: quantitative k-space fusion (two-angle scatterometry).

Fixes the two defects of the earlier illustrative fusion demo:
  1. The single-angle (theta_i = 0) scatterometry channel was filled with a
     constant 1e-18 outside its angular coverage, poisoning the fused estimate.
     Coverage of incidence angle theta_i is f <= (1 + sin theta_i)/lambda, i.e.
     1/lambda = 1880 mm-1 at normal incidence; a second angle (85 deg) extends
     coverage to (1 + sin 85 deg)/lambda ~= 3753 mm-1 (geometric maximum 2/lambda).
  2. The fused estimate is now formed only on bins where each modality has valid
     data, with minimum-variance weights w_i = |H_i|^2 / N_i (N_i = noise floor,
     5th percentile of positive PSD values, per modality).

Reports, on the tuning surface (seed 42) and held-out surfaces (777, 999):
  band-averaged |log10(PSD_est/PSD_true)| per modality and for the fused estimate,
  over the common band (10-1880 mm-1) and over the extended band (1880-3753 mm-1).

Writes reports/fusion_quantitative_audit.json
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')
sys.path.insert(0, ROOT)
sys.path.insert(0, PIPE)

from block4_physics_simulator import (SimulationParams,
                                      generate_self_affine_surface,
                                      simulate_stylus, simulate_optical)
from block10_scatterometry import compute_optical_factor_Q
from block5_discovery_engine import compute_psd_2d, azimuthal_average

WAVELEN = 532e-9
THETA_I_DEG = [0.0, 85.0]
BANDS = {'common': (10e3, 1880e3), 'extended': (1880e3, 3753e3)}


def scatterometry_two_angle(h_true, params, n_mat=2.5 + 3.3j):
    """Two-angle Rayleigh--Rice BSDF->PSD inversion with NaN outside coverage."""
    N = params.grid_size
    dx = params.dx
    psd_true = compute_psd_2d(h_true, dx)
    fx = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
    fy = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
    FX, FY = np.meshgrid(fx, fy)
    f_mag = np.sqrt(FX ** 2 + FY ** 2)
    phi_s = np.arctan2(FY, FX)

    prefactor = 16.0 * np.pi ** 2 / (WAVELEN ** 4)
    bsdf_noise_floor = 1e-8
    rng = np.random.RandomState(12345)

    psd_rec = np.full_like(psd_true, np.nan)
    for th_i_deg in THETA_I_DEG:
        th_i = np.radians(th_i_deg)
        # |sin(th_s) - sin(th_i)| = f * lambda; the negative branch
        # sin(th_s) = sin(th_i) - f*lambda is the one that extends coverage to
        # f <= (1 + sin(th_i))/lambda
        sin_th_s = np.sin(th_i) - f_mag * WAVELEN
        valid = (sin_th_s >= -1.0) & (f_mag > 0) & (f_mag * WAVELEN <= 1.0 + np.sin(th_i))
        if not np.any(valid):
            continue
        th_s = np.arcsin(np.clip(sin_th_s, -1.0, 1.0))
        cos_th_s = np.abs(np.cos(th_s))
        Q = np.zeros_like(f_mag)
        ii, jj = np.where(valid)
        for i, j in zip(ii, jj):
            Q[i, j] = compute_optical_factor_Q(th_i, th_s[i, j], phi_s[i, j],
                                               n_mat, 'unpolarised')
        bsdf = prefactor * np.cos(th_i) * cos_th_s * Q * psd_true
        bsdf[~valid] = 0.0
        noise = rng.randn(N, N) * bsdf_noise_floor * 0.1
        bsdf_meas = bsdf + noise
        inv_ok = valid & (Q > 1e-10) & (cos_th_s > 0.1)
        rec = np.full_like(psd_true, np.nan)
        rec[inv_ok] = bsdf_meas[inv_ok] / (
            prefactor * np.cos(th_i) * cos_th_s[inv_ok] * Q[inv_ok])
        rec = np.maximum(rec, 1e-35)
        # merge: keep first-angle value where both angles valid (they agree);
        # otherwise fill bins not yet covered
        both = inv_ok & ~np.isnan(psd_rec)
        rec[both] = 0.5 * (rec[both] + psd_rec[both])
        psd_rec[~np.isnan(rec)] = rec[~np.isnan(rec)]

    return psd_rec


def band_accuracy(psd_est, psd_true, f_r, lo, hi):
    m = ((f_r > lo) & (f_r <= hi) & (psd_true > 0)
         & np.isfinite(psd_est) & (psd_est > 0))
    if m.sum() == 0:
        return float('nan'), 0
    return float(np.mean(np.abs(np.log10(psd_est[m] / psd_true[m])))), int(m.sum())


def run(seed):
    p = SimulationParams()
    h_true = generate_self_affine_surface(p, seed=seed)
    h_s, _ = simulate_stylus(h_true, p)
    h_o, _ = simulate_optical(h_true, p)

    fx = np.fft.fftfreq(p.grid_size, d=p.dx)
    fx_s = np.fft.fftshift(fx)  # compute_psd_2d stores fftshift'ed PSDs
    Pt = compute_psd_2d(h_true, p.dx)
    Ps = compute_psd_2d(h_s, p.dx)
    Po = compute_psd_2d(h_o, p.dx)
    Psc = scatterometry_two_angle(h_true, p)

    f_r, pt = azimuthal_average(Pt, fx_s, fx_s)
    _, ps = azimuthal_average(Ps, fx_s, fx_s)
    _, po = azimuthal_average(Po, fx_s, fx_s)
    _, psc = azimuthal_average(np.nan_to_num(Psc, nan=0.0), fx_s, fx_s)
    # coverage fraction along radius: build the validity mask on the SAME
    # fftshift'ed frequency grid as the PSD storage
    FX, FY = np.meshgrid(fx_s, fx_s)
    f_mag = np.sqrt(FX ** 2 + FY ** 2)
    cov = np.zeros_like(Psc, dtype=bool)
    for th_i_deg in THETA_I_DEG:
        cov |= f_mag * WAVELEN <= 1.0 + np.sin(np.radians(th_i_deg))
    _, cov_1d = azimuthal_average(cov.astype(float), fx_s, fx_s)

    def nf(x):
        v = x[(x > 0) & np.isfinite(x)]
        return np.quantile(v, 0.05) if v.size else 1e-35

    n_s, n_o, n_sc = nf(ps), nf(po), nf(psc)
    H_s = np.clip(ps / np.maximum(pt, 1e-35), 0, 10)
    H_o = np.clip(po / np.maximum(pt, 1e-35), 0, 10)
    H_sc = np.clip(psc / np.maximum(pt, 1e-35), 0, 10)
    w_s = H_s ** 2 / max(n_s, 1e-35)
    w_o = H_o ** 2 / max(n_o, 1e-35)
    w_sc = H_sc ** 2 / max(n_sc, 1e-35)
    w_sc[cov_1d < 0.99] = 0.0  # no scatterometry weight where coverage incomplete
    wsum = np.maximum(w_s + w_o + w_sc, 1e-35)
    fused = (ps * w_s + po * w_o + psc * w_sc) / wsum

    out = {'seed': seed}
    for band, (lo, hi) in BANDS.items():
        out[band] = {
            'n_bins': band_accuracy(ps, pt, f_r, lo, hi)[1],
            'stylus': band_accuracy(ps, pt, f_r, lo, hi)[0],
            'wli': band_accuracy(po, pt, f_r, lo, hi)[0],
            'scatterometry': band_accuracy(psc, pt, f_r, lo, hi)[0],
            'fused': band_accuracy(fused, pt, f_r, lo, hi)[0],
        }
    return out


def main():
    out = {'tuning': run(42), 'held_out': [run(777), run(999)]}
    out['notes'] = {
        'geometry': (f"scatterometry lambda={WAVELEN*1e9:.0f} nm, theta_i = "
                     f"{THETA_I_DEG}; coverage per angle f <= (1+sin(theta_i))/lambda; "
                     f"two-angle coverage to ~3753 mm-1 (geometric max 2/lambda = 3760 mm-1)"),
        'weights': 'w_i = |H_i|^2 / N_i, N_i = 5th percentile of positive PSD values',
        'error_metric': 'mean |log10(PSD_est/PSD_true)| over radial bins in band',
        'caveat': ('the simulated scatterometry channel uses the same Rayleigh-Rice linear '
                   'forward model for measurement and inversion, so its sub-0.05-decade errors '
                   'are model-internal bounds on calibration-limited accuracy, not real '
                   'instrument performance'),
    }
    os.makedirs(REP, exist_ok=True)
    with open(os.path.join(REP, 'fusion_quantitative_audit.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
