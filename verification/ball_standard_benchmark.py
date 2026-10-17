#!/usr/bin/env python3
"""
Stylus-channel public-data benchmark using published ball-standard calibration
profiles (Aksulu, 2021; Zenodo 10.5281/zenodo.4471347, CC-BY-4.0).

Ball-standard calibration is the industry-standard geometry for stylus
verification: the stylus trace of a precision ball of radius R_true is the
parallel curve; the tip-bottom envelope of a concave reference fits
R_true - r_tip, the tip-centre path fits R_true + r_tip.

Honest scope: the published profiles carry ~40-100 um scatter (far above the
2-5 um tip scale), so this benchmark verifies the SIMULATOR's reproduction of
the analytic parallel-curve radius shift on the fitted calibration geometry,
and reports the public data's noise floor; it is not a tip-resolving
instrument comparison.
"""
import json
import os

import numpy as np
from scipy.ndimage import grey_dilation

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                    'data_public', 'aksulu2021')
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                      'reports', 'ball_standard_benchmark.json')


def fit_circle(X, Z):
    A = np.column_stack([X, Z, np.ones_like(X)])
    b = X ** 2 + Z ** 2
    coef, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, zc = coef[0] / 2, coef[1] / 2
    R = np.sqrt(coef[2] + xc ** 2 + zc ** 2)
    resid = np.sqrt((X - xc) ** 2 + (Z - zc) ** 2) - R
    return R, float(np.sqrt(np.mean(resid ** 2)))


def dilate_1d(Z, X, r_tip, dx_fine):
    Xf = np.arange(X.min(), X.max(), dx_fine)
    Zf = np.interp(Xf, X, Z)
    n_pts = int(2.0 * r_tip / dx_fine) + 1
    u = (np.arange(2 * n_pts + 1) - n_pts) * dx_fine
    tip = -(u ** 2) / (2 * r_tip)
    Zd = grey_dilation(Zf[None, :], structure=tip[None, :], mode='nearest')[0]
    return Xf, Zd


def main():
    results = []
    for tag in ('M40-20', 'M1000-20'):
        X = np.loadtxt(os.path.join(DATA, f'StylusOnBallData_{tag}_Xdu.txt'))
        Z = np.loadtxt(os.path.join(DATA, f'StylusOnBallData_{tag}_Zm.txt'))
        R_true, rms = fit_circle(X, Z)
        # Synthetic clean copy of the fitted calibration geometry:
        # Z_syn(x) = zc - sqrt(R^2 - (x - xc)^2), sampled on a fine grid.
        xc = 0.0  # apex at X=0 in both published profiles
        zc = R_true
        Xf = np.arange(X.min(), X.max(), 1e-4)
        Zsyn = zc - np.sqrt(np.maximum(R_true ** 2 - (Xf - xc) ** 2, 1e-12))
        for r_tip in (2e-3, 5e-3, 50e-3):
            n_pts = int(2.0 * r_tip / 1e-4) + 1
            u = (np.arange(2 * n_pts + 1) - n_pts) * 1e-4
            tip = -(u ** 2) / (2 * r_tip)
            Zd = grey_dilation(Zsyn[None, :], structure=tip[None, :], mode='nearest')[0]
            m = (Xf > X.min() + 1.0) & (Xf < X.max() - 1.0)  # exclude edge band
            R_dil, _ = fit_circle(Xf[m], Zd[m])
            shift = R_dil - R_true
            expected = -r_tip  # tip-bottom envelope of the concave reference
            rel = float((shift - expected) / expected)
            results.append(dict(
                tag=tag, data_noise_rms_mm=rms,
                r_tip_mm=r_tip, R_true_mm=float(R_true),
                R_dilated_mm=float(R_dil),
                shift_mm=float(shift), expected_mm=expected, rel_error=rel,
            ))
            print(f"{tag}: data noise {rms*1e3:.0f} um | r_tip={r_tip*1e3:.0f} um: "
                  f"shift={shift*1e3:+.2f} um (expected {expected*1e3:+.2f} um, "
                  f"rel err {rel:+.2%})")

    with open(REPORT, 'w') as f:
        json.dump(results, f, indent=2)
    print('wrote', REPORT)


if __name__ == '__main__':
    main()
