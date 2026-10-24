#!/usr/bin/env python3
"""Acceptance pass, Tier 2a: quantitative confocal channel.

Implements the lateral transfer function of a point-detection confocal
microscope with equal circular illumination and detection pupils:

    H_confocal(f) = OTF_incoh (x) OTF_incoh      (2D autocorrelation),

normalised to unity at DC, with cutoff 4 NA / lambda (twice the widefield
incoherent cutoff). The channel is simulated as a linear filter on the
gridded surface plus additive camera noise at the same level as the WLI
model, WITHOUT the 1% phase-unwrapping error channel (confocal height
readout does not unwrap phase). All other conventions follow the committed
pipeline (N=512, H=0.7, sigma=50 nm, tip 2 um, NA=0.55, lambda=550 nm).

Reports per seed: RMSE, reconstructability rho (Gaussian-channel MMSE),
3 dB equivalence fraction vs stylus, crossover frequency vs stylus, and
the DC-normalised H_confocal values at reference frequencies.

Writes reports/confocal_audit.json
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
from block5_discovery_engine import compute_psd_2d, azimuthal_average


def otf_incoh_2d(fx, fy, cutoff):
    """Radial incoherent OTF of a circular pupil, cutoff = 2NA/lambda."""
    r = np.sqrt(fx[:, None] ** 2 + fy[None, :] ** 2) / cutoff
    r = np.clip(r, 0, 1)
    return (2.0 / np.pi) * (np.arccos(r) - r * np.sqrt(1.0 - r ** 2))


def confocal_otf(fx, fy, cutoff):
    """H_confocal = OTF_incoh (*) OTF_incoh via FFT autocorrelation on a fine grid."""
    # fine grid: 4x sampling, support to 4*cutoff < Nyquist; UNSHIFTED fftfreq
    # convention throughout so the autocorrelation and the interpolation grids match
    n_fine = 2048
    d_fine = 100e-6 / n_fine
    f_fine = np.fft.fftfreq(n_fine, d=d_fine)
    H = otf_incoh_2d(f_fine, f_fine, cutoff)
    # cyclic autocorrelation: auto = ifft2(|fft2(H)|^2), origin at index 0
    auto = np.real(np.fft.ifft2(np.abs(np.fft.fft2(H)) ** 2))
    auto /= auto[0, 0]
    # sample onto the measurement grid by exact index mapping (grids are
    # commensurate: d_fine = dx/4, so measurement frequencies hit fine bins)
    df_fine = f_fine[1] - f_fine[0]
    FX, FY = np.meshgrid(fx, fy)
    ix = np.rint(FX / df_fine).astype(int) % n_fine
    iy = np.rint(FY / df_fine).astype(int) % n_fine
    H_conf = auto[iy, ix]
    return np.clip(H_conf, 0, None)


def mmse_rho(h_true, h_meas, dx, H_system):
    """Gaussian-channel reconstructability rho = 1 - MMSE/sigma^2."""
    N = h_true.shape[0]

    def psd2d(h):
        w = np.hanning(N)[:, None] * np.hanning(N)[None, :]
        return np.abs(np.fft.fft2(h * w)) ** 2 * dx ** 2 / np.sum(w ** 2)

    P_t = psd2d(h_true)
    P_m = psd2d(h_meas)
    # noise floor from difference field (pipeline convention)
    eta = np.median(psd2d(h_meas - h_true)[psd2d(h_meas - h_true) > 0])
    H2 = np.clip(P_m / np.maximum(P_t, 1e-35), 0, 10)
    var = np.sum(P_t) * (dx / (N * dx)) ** 2 if False else np.sum(P_t)
    # MMSE per mode: S_h * S_eta / (H^2 S_h + S_eta); S_eta ~ eta constant
    mmse = np.sum(P_t * eta / (H2 * P_t + eta))
    sigma2 = np.sum(P_t)
    return 1.0 - mmse / sigma2


def run(seed):
    p = SimulationParams()
    h_true = generate_self_affine_surface(p, seed=seed)
    h_s, meta_s = simulate_stylus(h_true, p)
    h_o, meta_o = simulate_optical(h_true, p)

    fx = np.fft.fftfreq(p.grid_size, d=p.dx)
    cutoff_inc = 2 * p.optical_cutoff  # 2NA/lambda
    H_conf = confocal_otf(fx, fx, cutoff_inc)

    H_f = np.fft.fft2(h_true)
    h_c = np.real(np.fft.ifft2(H_f * H_conf))
    rng = np.random.RandomState(seed)
    h_c += rng.randn(p.grid_size, p.grid_size) * p.camera_noise_std * p.rms_roughness

    dx = p.dx
    N = p.grid_size
    fx_s = np.fft.fftshift(fx)  # compute_psd_2d stores fftshift'ed PSDs
    Ps = compute_psd_2d(h_s, dx)
    Po = compute_psd_2d(h_o, dx)
    Pc = compute_psd_2d(h_c, dx)
    Pt = compute_psd_2d(h_true, dx)
    f_r, ps = azimuthal_average(Ps, fx_s, fx_s)
    _, po = azimuthal_average(Po, fx_s, fx_s)
    _, pc = azimuthal_average(Pc, fx_s, fx_s)
    _, pt = azimuthal_average(Pt, fx_s, fx_s)

    H_s = np.clip(ps / np.maximum(pt, 1e-35), 0, 10)
    H_o = np.clip(po / np.maximum(pt, 1e-35), 0, 10)
    H_c = np.clip(pc / np.maximum(pt, 1e-35), 0, 10)

    # equivalence fraction vs stylus: |10 log10(H_ratio)| < 3 dB
    band = (f_r > 10e3) & (f_r <= min(4000e3, f_r.max()))
    r_o = np.abs(10 * np.log10(np.maximum(H_o[band] / np.maximum(H_s[band], 1e-12), 1e-12)))
    r_c = np.abs(10 * np.log10(np.maximum(H_c[band] / np.maximum(H_s[band], 1e-12), 1e-12)))
    eq_o = np.mean(r_o < 3.0)
    eq_c = np.mean(r_c < 3.0)

    # crossover: first frequency above 10 mm-1 where H falls below H_stylus by >3dB
    def cross(Hx):
        m = (f_r > 10e3)
        ratio = 10 * np.log10(np.maximum(Hx[m] / np.maximum(H_s[m], 1e-12), 1e-12))
        idx = np.where(ratio < -3.0)[0]
        return float(f_r[m][idx[0]]) if idx.size else float('nan')

    # reference transfer values
    def h_at(freq_mm):
        i = np.argmin(np.abs(f_r - freq_mm * 1e3))
        return float(H_c[i])

    # analytic H_confocal (2D autocorrelation of the incoherent OTF) at the
    # reference frequencies, independent of any simulated realisation
    Hc_ref = confocal_otf(np.array([1000e3, 2000e3]), np.array([0.0]), cutoff_inc)

    return {
        'seed': seed,
        'rmse_stylus_nm': float(meta_s['rmse'] * 1e9),
        'rmse_optical_nm': float(meta_o['rmse'] * 1e9),
        'rmse_confocal_nm': float(np.sqrt(np.mean((h_c - h_true) ** 2)) * 1e9),
        'rho_stylus': float(mmse_rho(h_true, h_s, dx, H_s)),
        'rho_optical': float(mmse_rho(h_true, h_o, dx, H_o)),
        'rho_confocal': float(mmse_rho(h_true, h_c, dx, H_c)),
        'eq_frac_3dB_vs_stylus_optical': float(eq_o),
        'eq_frac_3dB_vs_stylus_confocal': float(eq_c),
        'f_cross_confocal_vs_stylus_mm': cross(H_c),
        'H_confocal_at_1000mm': h_at(1000),
        'H_confocal_at_2000mm': h_at(2000),
        'H_confocal_at_3000mm': h_at(3000),
        'H_confocal_analytic_1000mm': float(Hc_ref[0, 0]),
        'H_confocal_analytic_2000mm': float(Hc_ref[0, 1]),
        'cutoff_confocal_mm': float(cutoff_inc * 1e-3 * 2),  # 4NA/lambda
    }


def main():
    out = {'tuning': run(42), 'held_out': [run(777), run(999)]}
    out['notes'] = {
        'model': ('H_confocal = OTF_incoh (*) OTF_incoh (2D autocorrelation), '
                  'cutoff 4NA/lambda = 4000 mm-1; linear filter + camera noise at '
                  'the WLI level; NO phase-unwrapping error channel'),
        'caveats': ('lateral transfer only (axial sectioning response not modelled); '
                    'grid Nyquist 2560 mm-1 truncates the channel there; confocal noise '
                    'assumed equal to the WLI camera noise'),
    }
    os.makedirs(REP, exist_ok=True)
    with open(os.path.join(REP, 'confocal_audit.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
