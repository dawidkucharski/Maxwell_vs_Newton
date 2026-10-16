#!/usr/bin/env python3
"""
Panel fixes T8/T9: minimal additional simulations.

1. Stylus raster-sampling sweep: Delta-x in {100, 200, 400} nm at baseline
   parameters on the stored true surface; reports RMSE and the empirical 3 dB
   point of H_stylus per sampling.

2. Polychromatic optical OTF variant: uniform illumination lambda in 500-700 nm
   (mean 600 nm) averaged incoherent OTF; reports the passband fraction where
   the polychromatic OTF agrees with the monochromatic (550 nm) OTF to within
   3 dB, and the effective cutoff scale relative to 2 NA / lam_mean.

Outputs: pipeline/outputs/iter01/robustness/variant_simulations.json
"""
import json
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import (            # noqa: E402
    SimulationParams, simulate_stylus,
)
from block5_discovery_engine import (             # noqa: E402
    compute_psd_2d, azimuthal_average,
)

OUT = os.path.join(PIPE, 'outputs', 'iter01', 'robustness')


def baseline_params():
    return SimulationParams(
        grid_size=512, physical_size=100e-6,
        hurst_exponent=0.7, rms_roughness=50e-9,
        correlation_length=5e-6, roll_off_wavelength=10e-6,
        tip_radius=2e-6, sampling_interval=0.2e-6,
        cone_angle=45.0, wavelength=550e-9, na=0.55,
        magnification=50.0, camera_noise_std=1e-3,
        unwrapping_error_prob=0.01,
    )


def otf_incoherent(f_radial, na, lam):
    """Incoherent OTF of a circular pupil, amplitude convention."""
    F = np.clip(f_radial * lam / (2.0 * na), 0, 1)
    return 2.0 / np.pi * (np.arccos(F) - F * np.sqrt(1 - F ** 2))


def psd2d(h, dx):
    w = np.hanning(h.shape[0])[:, None] * np.hanning(h.shape[1])[None, :]
    P = np.abs(np.fft.fft2(h * w)) ** 2 * dx ** 2 / np.sum(w ** 2)
    return np.fft.fftshift(P)


def azavg(P, fr, nbin=100):
    fmax = np.max(fr) * 0.95
    edges = np.linspace(0, fmax, nbin + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    out = np.zeros(nbin)
    for i in range(nbin):
        m = (fr >= edges[i]) & (fr < edges[i + 1])
        out[i] = np.mean(P[m]) if m.sum() else np.nan
    return centers, out


def main():
    os.makedirs(OUT, exist_ok=True)
    h_true = np.load(os.path.join(PIPE, 'outputs', 'iter01', 'h_true.npy'))
    results = {}

    # ---- 1. Stylus Delta-x sweep (verified PSD procedure) -------------------
    N = h_true.shape[0]
    dx_grid = 100e-6 / N
    fx = np.fft.fftshift(np.fft.fftfreq(N, d=dx_grid))
    FX, FY = np.meshgrid(fx, fx)
    fr = np.sqrt(FX ** 2 + FY ** 2)
    Pt = psd2d(h_true, dx_grid)
    fc, _ = azavg(Pt, fr)

    sampling_results = []
    for dx_nm in (100.0, 200.0, 400.0):
        p = baseline_params()
        p.sampling_interval = dx_nm * 1e-9
        h_s, _meta = simulate_stylus(h_true, p)
        rmse = float(np.sqrt(np.mean((h_s - h_true) ** 2)))
        Ps = psd2d(h_s, dx_grid)
        _, Hs1 = azavg(Ps, fr)
        _, Pt1 = azavg(Pt, fr)
        H = Hs1 / np.maximum(Pt1, 1e-30)
        i50 = np.where(H <= 0.5)[0]
        f3 = float(fc[i50[0]]) if len(i50) else None
        sampling_results.append(dict(sampling_nm=dx_nm, rmse_nm=rmse,
                                     H_3dB_mm=float(f3 * 1e-3) if f3 else None))
        print(f"Delta-x = {dx_nm:.0f} nm: RMSE = {rmse*1e9:.2f} nm, "
              f"H_stylus 3 dB at {f3*1e-3 if f3 else float('nan'):.0f} mm-1")
    results['stylus_sampling_sweep'] = sampling_results

    # ---- 2. Polychromatic optical OTF variant -------------------------------
    N = p.grid_size
    fx = np.fft.fftfreq(N, d=p.dx)
    FX, FY = np.meshgrid(fx, fx)
    f_rad = np.sqrt(FX ** 2 + FY ** 2)

    otf_mono = otf_incoherent(f_rad, 0.55, 550e-9)
    lams = np.linspace(500e-9, 700e-9, 21)
    otf_poly = np.mean([otf_incoherent(f_rad, 0.55, l) for l in lams], axis=0)

    # passband = support of the monochromatic OTF
    mask = f_rad < 2 * 0.55 / 550e-9
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio_db = 10 * np.log10(
            np.where(mask, np.maximum(otf_poly, 1e-6) / np.maximum(otf_mono, 1e-6), 1.0))
    agree = np.mean(np.abs(ratio_db[mask]) < 3.0)
    # effective cutoff scale: frequency where poly OTF = 0.5 relative to mono
    f_cut_mono = 2 * 0.55 / 550e-9
    f_half_poly = None
    fr_sorted = np.sort(f_rad[mask])
    otf_sorted = otf_poly[mask][np.argsort(f_rad[mask])]
    below = np.where(otf_sorted <= 0.5)[0]
    if len(below):
        f_half_poly = float(fr_sorted[below[0]])
    results['polychromatic_otf'] = dict(
        wavelengths_um=[0.5, 0.7],
        mean_wavelength_um=0.6,
        passband_frac_within_3dB=float(agree),
        cutoff_scale_c_eff=float(f_half_poly / f_cut_mono) if f_half_poly else None,
    )
    print(f"Polychromatic OTF (500-700 nm): passband frac within 3 dB of "
          f"monochromatic = {agree:.3f}; effective cutoff scale = "
          f"{results['polychromatic_otf']['cutoff_scale_c_eff']:.3f}")

    with open(os.path.join(OUT, 'variant_simulations.json'), 'w') as f:
        json.dump(results, f, indent=2)
    print('wrote', os.path.join(OUT, 'variant_simulations.json'))


if __name__ == '__main__':
    main()
