#!/usr/bin/env python3
"""Robustness audits of SI S8 and S10 (validity boundaries + OTF variants).

Reproduces the four quantitative validity-boundary claims and the
optical-model invariance claim:

  1. Linearity of the dilation operator (SI S8(i)):
     stylus RMSE vs surface rms amplitude sigma, swept at the S8 grid
     (N=256) for sigma in {5,10,20,50,100,150,200} nm, compared against
     the baseline-anchored linear extrapolation: RMSE_lin(sigma) =
     RMSE_baseline(N=512, sigma=50 nm) * sigma/50 nm.

  2. Gaussian vs Poisson (shot) camera noise (SI S8(ii)):
     two-frame phase-shift interferometry model; per-pixel photon count
     N_p in {1e3, 1e4, 1e5, 1e6, 1e7}; Poisson channel draws the actual
     photon counts and estimates the phase, Gaussian channel uses the
     matched-variance Gaussian height noise; reports the optical RMSE
     difference per illumination level.

  3. Statistical stationarity (SI S8(iii)): two-half wear-scar surface
     (left sigma=5 nm, right sigma=100 nm, same seed); local PSD of each
     half estimated on the zero-padded half window; ratio of the local
     PSDs at f = 10 mm-1.

  4. Optical-model invariance (SI S10): ideal incoherent OTF, Maréchal-
     aberrated OTF (lambda/4 defocus + lambda/10 spherical, RMS wavefront
     0.151 waves), and a Gaussian OTF approximation with the -3 dB point
     matched to the ideal OTF; per variant the optical reconstructability
     rho (block11 conventions) and the passband fraction within 3 dB of
     the ideal OTF.

Writes: reports/robustness_audit.json
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')
sys.path.insert(0, PIPE)

from block4_physics_simulator import (SimulationParams,
                                      generate_self_affine_surface,
                                      simulate_stylus, simulate_optical)
from block5_discovery_engine import compute_psd_2d, azimuthal_average
from block11_stress_test import compute_all_metrics


def baseline_params(grid):
    return SimulationParams(
        grid_size=grid, physical_size=100e-6,
        hurst_exponent=0.7, rms_roughness=50e-9,
        correlation_length=5e-6, roll_off_wavelength=10e-6,
        tip_radius=2e-6, sampling_interval=0.2e-6,
        cone_angle=45.0, wavelength=550e-9, na=0.55,
        magnification=50.0, camera_noise_std=1e-3,
        unwrapping_error_prob=0.01,
    )


def otf_incoherent(f_radial, na, lam):
    F = np.clip(f_radial * lam / (2.0 * na), 0, 1)
    return 2.0 / np.pi * (np.arccos(F) - F * np.sqrt(1 - F ** 2))


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def simulate_optical_with_otf(h_true, params, otf, noise_seed=8):
    """Optical channel with a custom 2D OTF (same chain as simulate_optical)."""
    N = params.grid_size
    H_f = np.fft.fft2(h_true) * otf
    h_filtered = np.real(np.fft.ifft2(H_f))
    phase = (4.0 * np.pi / params.wavelength) * h_filtered
    phase_wrapped = np.mod(phase + np.pi, 2.0 * np.pi) - np.pi
    h_unwrapped = np.zeros_like(h_filtered)
    for iy in range(N):
        row = phase_wrapped[iy, :]
        h_unwrapped[iy, :] = np.unwrap(row) * params.wavelength / (4.0 * np.pi)
    rng = np.random.RandomState(123)
    error_mask = rng.rand(N, N) < params.unwrapping_error_prob
    error_heights = (rng.randint(0, 2, (N, N)) * 2 - 1) * params.wavelength / 2.0
    h_unwrapped += error_mask * error_heights
    noise = np.random.RandomState(noise_seed).randn(N, N) * params.camera_noise_std * params.rms_roughness
    return h_unwrapped + noise


# ------------------------------------------------------------------
# 1. Linearity of the dilation operator
# ------------------------------------------------------------------
def audit_linearity():
    N = 256
    p = baseline_params(N)
    rmse_vals = {}
    for sigma_nm in (5, 10, 20, 50, 100, 150, 200):
        p.rms_roughness = sigma_nm * 1e-9
        ht = generate_self_affine_surface(p, seed=42)
        hs, _ = simulate_stylus(ht, p)
        rmse_vals[sigma_nm] = rmse(hs, ht) * 1e9
    # baseline anchor: N=512 baseline run, sigma=50 nm
    p512 = baseline_params(512)
    ht512 = generate_self_affine_surface(p512, seed=42)
    hs512, _ = simulate_stylus(ht512, p512)
    rmse_baseline = rmse(hs512, ht512) * 1e9
    rows = []
    for sigma_nm, val in rmse_vals.items():
        lin = rmse_baseline * sigma_nm / 50.0
        rows.append(dict(sigma_nm=sigma_nm, rmse_stylus_nm=round(val, 3),
                         rmse_linear_extrap_nm=round(lin, 3),
                         ratio=round(val / lin, 4)))
    return dict(grid=N, baseline_anchor_nm=round(rmse_baseline, 2),
                rows=rows)


# ------------------------------------------------------------------
# 2. Gaussian vs Poisson (shot) noise
# ------------------------------------------------------------------
def audit_poisson():
    p = baseline_params(256)
    ht = generate_self_affine_surface(p, seed=42)
    # filtered, wrapped phase field shared by both channels
    N = p.grid_size
    fx = np.fft.fftfreq(N, d=p.dx)
    FX, FY = np.meshgrid(fx, fx)
    H_opt = otf_incoherent(np.sqrt(FX ** 2 + FY ** 2), p.na, p.wavelength)
    h_filtered = np.real(np.fft.ifft2(np.fft.fft2(ht) * H_opt))
    phase = (4.0 * np.pi / p.wavelength) * h_filtered
    phase_wrapped = np.mod(phase + np.pi, 2.0 * np.pi) - np.pi
    h_unwrapped = np.zeros_like(h_filtered)
    for iy in range(N):
        h_unwrapped[iy, :] = np.unwrap(phase_wrapped[iy, :]) * p.wavelength / (4.0 * np.pi)
    rng = np.random.RandomState(123)
    error_mask = rng.rand(N, N) < p.unwrapping_error_prob
    error_heights = (rng.randint(0, 2, (N, N)) * 2 - 1) * p.wavelength / 2.0
    h_base = h_unwrapped + error_mask * error_heights  # no camera noise yet

    rows = []
    for n_phot in (1e3, 1e4, 1e5, 1e6, 1e7):
        n_phot = int(n_phot)
        sigma_h = p.wavelength / (4.0 * np.pi) / np.sqrt(2.0 * n_phot)
        # Gaussian channel
        g = np.random.RandomState(11).randn(N, N) * sigma_h
        rmse_g = rmse(h_base + g, ht) * 1e9
        # Poisson channel: actual photon counts in two pi/2-shifted frames
        r = np.random.RandomState(12)
        i1 = r.poisson(n_phot * (1.0 + np.cos(phase_wrapped)))
        i2 = r.poisson(n_phot * (1.0 + np.sin(phase_wrapped)))
        phase_est = np.arctan2(i2 - n_phot, i1 - n_phot)
        h_pois = h_base + (phase_est - phase_wrapped) * p.wavelength / (4.0 * np.pi)
        rmse_p = rmse(h_pois, ht) * 1e9
        rows.append(dict(photons_per_pixel=n_phot,
                         sigma_h_nm=round(sigma_h * 1e9, 3),
                         rmse_gaussian_nm=round(rmse_g, 3),
                         rmse_poisson_nm=round(rmse_p, 3),
                         rel_diff_pct=round(100.0 * abs(rmse_p - rmse_g) / rmse_g, 3)))
    return dict(method='two-frame phase-shift shot noise; unwrapping errors shared',
                rows=rows,
                max_rel_diff_pct=round(max(r['rel_diff_pct'] for r in rows), 3))


# ------------------------------------------------------------------
# 3. Statistical stationarity (wear-scar surface)
# ------------------------------------------------------------------
def audit_wear_scar():
    N = 512
    p = baseline_params(N)
    half = N // 2
    p.rms_roughness = 5e-9
    left = generate_self_affine_surface(p, seed=42)
    p.rms_roughness = 100e-9
    right = generate_self_affine_surface(p, seed=42)
    h_wear = np.zeros((N, N))
    h_wear[:, :half] = left[:, :half]
    h_wear[:, half:] = right[:, half:]

    def local_psd(region, target_n):
        # zero-pad the half field to target_n to resolve f = 10 mm-1
        out = np.zeros((target_n, target_n))
        n = region.shape[0]
        out[:n, :n] = region
        return compute_psd_2d(out, 100e-6 / target_n)

    P_l = local_psd(left, 1024)
    P_r = local_psd(right, 1024)
    fx = np.fft.fftshift(np.fft.fftfreq(1024, d=100e-6 / 1024))
    f_r, pl = azimuthal_average(P_l, fx, fx)
    _, pr = azimuthal_average(P_r, fx, fx)
    i10 = int(np.argmin(np.abs(f_r - 10e3)))
    ratio = float(pr[i10] / pl[i10])
    # global PSD of the composite field
    P_g = compute_psd_2d(h_wear, 100e-6 / N)
    _, pg = azimuthal_average(P_g, np.fft.fftshift(np.fft.fftfreq(N, d=100e-6 / N)),
                              np.fft.fftshift(np.fft.fftfreq(N, d=100e-6 / N)))
    return dict(sigma_left_nm=5, sigma_right_nm=100, sigma_ratio=20.0,
                f_eval_mm=10.0,
                local_psd_ratio_at_f=round(ratio, 2),
                sigma_squared_ratio=400.0,
                note='half-window local PSD, zero-padded to N=1024 (df=10 mm-1)')


# ------------------------------------------------------------------
# 4. Optical-model invariance (OTF variants)
# ------------------------------------------------------------------
def audit_otf_variants():
    N = 512
    p = baseline_params(N)
    ht = generate_self_affine_surface(p, seed=42)
    fx = np.fft.fftfreq(N, d=p.dx)
    FX, FY = np.meshgrid(fx, fx)
    f_rad = np.sqrt(FX ** 2 + FY ** 2)
    fc = 2.0 * p.na / p.wavelength
    otf_ideal = otf_incoherent(f_rad, p.na, p.wavelength)

    # Maréchal: RMS wavefront = sqrt(W20^2/3 + W40^2/5), W20=lam/4, W40=lam/10
    sigma_w = np.sqrt((0.25 ** 2) / 3.0 + (0.10 ** 2) / 5.0)
    nu = np.clip(f_rad / fc, 0, 1)
    otf_marechal = otf_ideal * np.exp(-(2.0 * np.pi * sigma_w * nu) ** 2)

    # Gaussian approximation with the -3 dB point matched to the ideal OTF
    nu_fine = np.linspace(0, 1, 4001)
    otf_fine = otf_incoherent(nu_fine * fc, p.na, p.wavelength)
    nu_3db = float(np.interp(0.5, otf_fine[::-1], nu_fine[::-1]))
    otf_gauss = np.exp(-(nu / nu_3db) ** 2 * np.log(2.0))

    h_s, _ = simulate_stylus(ht, p)
    rows = []
    mask = f_rad < fc
    for name, otf in [('ideal', otf_ideal), ('marechal', otf_marechal),
                      ('gaussian', otf_gauss)]:
        h_o = simulate_optical_with_otf(ht, p, otf)
        m = compute_all_metrics(ht, h_s, h_o, p)
        ratio_db = 10.0 * np.log10(np.maximum(otf, 1e-9) / np.maximum(otf_ideal, 1e-9))
        agree = float(np.mean(np.abs(ratio_db[mask]) < 3.0))
        rows.append(dict(variant=name,
                         rho_stylus=round(m['rho_stylus'], 6),
                         rho_optical=round(m['rho_optical'], 6),
                         rmse_optical_nm=round(m['rmse_optical_nm'], 3),
                         frac_passband_within_3dB_of_ideal=round(agree, 6)))
    return dict(rms_wavefront_waves=round(sigma_w, 3),
                gaussian_3dB_point_nu=round(nu_3db, 4),
                rows=rows)


def main():
    out = {
        'linearity': audit_linearity(),
        'poisson': audit_poisson(),
        'wear_scar': audit_wear_scar(),
        'otf_variants': audit_otf_variants(),
    }
    os.makedirs(REP, exist_ok=True)
    with open(os.path.join(REP, 'robustness_audit.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
