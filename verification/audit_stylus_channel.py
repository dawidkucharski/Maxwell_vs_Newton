#!/usr/bin/env python3
"""Priority-2 audit: stylus channel — PSD ratio vs cross-spectral estimates,
linearised curvature-bias model, low-frequency excess, 3 dB point vs raster.

Part A (committed data): verify manuscript stylus H values (2.2/0.91/0.74/0.57
at 17/292/567/843 mm^-1; 3 dB at ~1049 mm^-1) from H_stylus_2d.npy.

Part B (fresh ensemble, seeds 200-219): ensemble PSD-ratio H, cross-spectral
H (S_ty/S_tt), magnitude-squared coherence, and the linearised prediction
S(h + (r/2)|grad h|^2)/S(h).

Part C (fresh sims): 3 dB point of the azimuthal PSD-ratio H at raster
intervals 100/200/400 nm (N=512, baseline otherwise).

Writes reports/stylus_channel_audit.json.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pipeline.block4_physics_simulator import SimulationParams, simulate_stylus  # noqa: E402

PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')
os.makedirs(REP, exist_ok=True)

audit = {}


def psd2d(h, dx):
    n = h.shape[0]
    w = np.hanning(n)[:, None] * np.hanning(n)[None, :]
    return np.abs(np.fft.fft2(h * w)) ** 2 * dx ** 2 / np.sum(w ** 2)


def azavg(field2d, fx, fy, edges):
    fr = np.sqrt(fx[:, None] ** 2 + fy[None, :] ** 2)
    out = []
    for i in range(len(edges) - 1):
        m = (fr >= edges[i]) & (fr < edges[i + 1])
        out.append(np.mean(field2d[m]) if m.sum() else np.nan)
    return np.array(out)


# ---------- Part A: committed baseline ----------
N = 512
dx = 100e-6 / N
fx = np.fft.fftfreq(N, d=dx)
H = np.load(os.path.join(PIPE, 'outputs', 'iter01', 'H_stylus_2d.npy'))
fr = np.sqrt(fx[:, None] ** 2 + fx[None, :] ** 2)
edges = np.linspace(0, np.max(fr) * 0.95, 101)
fcent = 0.5 * (edges[:-1] + edges[1:])
Haz = azavg(H, fx, fx, edges)

def val_at(f_mm):
    i = np.argmin(np.abs(fcent / 1e3 - f_mm))
    return float(Haz[i]), float(fcent[i] / 1e3)

audit['partA_committed'] = {
    f'{f_mm}_mm-1': {'H': val_at(f_mm)[0], 'bin_f_mm-1': val_at(f_mm)[1]}
    for f_mm in (17, 292, 567, 843)
}
i3 = np.where(Haz < 10 ** (-3 / 10))[0]
audit['partA_3dB'] = {
    'f_3dB_mm-1': float(fcent[i3[0]] / 1e3) if len(i3) else None,
    'method': 'first azimuthal bin below -3 dB (power ratio)',
}

# ---------- Part B: fresh ensemble (cross-spectral + coherence) ----------
p = SimulationParams()  # baseline: r=2 um, dX=200 nm
seeds = list(range(200, 220))
Stt = Ssy = Syy = None
Hlin_num = Hlin_den = None
for sd in seeds:
    ht, hs = None, None
    from pipeline.block4_physics_simulator import generate_self_affine_surface
    ht = generate_self_affine_surface(p, seed=sd)
    hs, _ = simulate_stylus(ht, p)
    S = psd2d(ht, dx); Y = psd2d(hs, dx)
    F = np.fft.fft2(ht * (np.hanning(N)[:, None] * np.hanning(N)[None, :]))
    F = F * np.sqrt(dx ** 2 / np.sum((np.hanning(N)[:, None] * np.hanning(N)[None, :]) ** 2))
    G = np.fft.fft2(hs * (np.hanning(N)[:, None] * np.hanning(N)[None, :]))
    G = G * np.sqrt(dx ** 2 / np.sum((np.hanning(N)[:, None] * np.hanning(N)[None, :]) ** 2))
    # linearised model: b = (r/2)|grad h|^2
    gy, gx = np.gradient(ht, dx)
    b = (p.tip_radius / 2.0) * (gx ** 2 + gy ** 2)
    Sb = psd2d(ht + b, dx)
    Stt = S if Stt is None else Stt + S
    Ssy = (np.conj(F) * G) if Ssy is None else Ssy + np.conj(F) * G
    Syy = Y if Syy is None else Syy + Y
    Hlin_num = Sb if Hlin_num is None else Hlin_num + Sb
    Hlin_den = S if Hlin_den is None else Hlin_den + S
Stt /= len(seeds); Ssy /= len(seeds); Syy /= len(seeds)
Hlin_num /= len(seeds); Hlin_den /= len(seeds)

H_psd = Syy / np.maximum(Stt, 1e-40)            # power-ratio estimate
H_cross = np.abs(Ssy) / np.maximum(Stt, 1e-40)  # |cross-spectral| amplitude
coh2 = np.abs(Ssy) ** 2 / np.maximum(Stt * Syy, 1e-60)
H_lin = Hlin_num / np.maximum(Hlin_den, 1e-40)

Hp = azavg(H_psd, fx, fx, edges)
Hc = azavg(H_cross, fx, fx, edges)
Hl = azavg(H_lin, fx, fx, edges)
c2 = azavg(coh2, fx, fx, edges)

band_lo = (fcent > 0.5e4) & (fcent < 5e4)    # 0.005-0.05 mm^-1 (below FOV min is excluded)
band_mid = (fcent > 0.05e6) & (fcent < 0.5e6)
band_hi = (fcent > 0.5e6) & (fcent < 1.5e6)

audit['partB_ensemble'] = {
    'n_seeds': len(seeds),
    'H_psd_ratio_lowest_bin': float(Hp[band_lo][0]),
    'H_cross_lowest_bin': float(Hc[band_lo][0]),
    'H_linearised_model_lowest_bin': float(Hl[band_lo][0]),
    'mean_coherence_mid_band': float(np.nanmean(c2[band_mid])),
    'mean_coherence_high_band': float(np.nanmean(c2[band_hi])),
    'H_psd_mean_mid_band': float(np.nanmean(Hp[band_mid])),
    'H_cross_mean_mid_band': float(np.nanmean(Hc[band_mid])),
    'H_linearised_mean_mid_band': float(np.nanmean(Hl[band_mid])),
    'note': 'H_psd_ratio = <S_yy>/S_tt (biased by noise + nonlinear distortion); '
            'H_cross = |<S_ty>|/S_tt (LTI-optimal amplitude estimate); '
            'H_linearised = S(h+(r/2)|grad h|^2)/S(h).',
}

# ---------- Part C: 3 dB point vs raster interval ----------
raster_res = {}
for si in (100e-9, 200e-9, 400e-9):
    pp = SimulationParams(sampling_interval=si)
    ht = generate_self_affine_surface(pp, seed=42)
    hs, _ = simulate_stylus(ht, pp)
    Hr = psd2d(hs, dx) / np.maximum(psd2d(ht, dx), 1e-40)
    Hazr = azavg(Hr, fx, fx, edges)
    i3r = np.where(Hazr < 10 ** (-3 / 10))[0]
    raster_res[f'{int(si*1e9)}nm'] = float(fcent[i3r[0]] / 1e3) if len(i3r) else None
audit['partC_raster_3dB_mm-1'] = raster_res

with open(os.path.join(REP, 'stylus_channel_audit.json'), 'w') as f:
    json.dump(audit, f, indent=2)
print(json.dumps(audit, indent=2))
