#!/usr/bin/env python3
"""
Phase 7 public-data benchmark: measured WLI spectra (Hirose et al. 2025,
Applied Optics 64:5461; Zenodo 10.5281/zenodo.15750880, CC-BY-4.0) versus the
incoherent-OTF optical channel model of this project.

Method (model validation, WLI-only):
  log PSD_meas(f) = log A + beta*log f + log ITF_model(f; c * 2NA/lambda, D)
fit over the band [f_lo, 0.85 * Nyquist] for free (A, beta, c).
  - c ~ 1  => measured data consistent with nominal 2NA/lambda incoherent cutoff
  - ITF_model = radial average of |OTF|^2 * sinc^2(D f_x) * sinc^2(D f_y)
  - model-selection: with pixel sinc vs lens-only (compare residual RMS)

Secondary check: measured ITF = PSD_WLI / PSD_AFM, normalised at 0.75 um^-1,
reported with the caveat that the 2 um AFM field truncates low frequencies.

Outputs: reports/public_data_benchmark.json, fig_public_benchmark.pdf
"""
import json
import os
import sys

import h5py
import numpy as np

OPTICA = os.path.join(os.path.dirname(__file__), '..', 'data_public', 'hirose2025', 'optica')
sys.path.insert(0, OPTICA)

from utils import read_seiko_xqd                    # noqa: E402
from surface_process import subtract_polynomial_fit  # noqa: E402
from psd import (                                    # noqa: E402
    calculate_frequency_mesh_and_axes,
    compute_psd2d,
    calculate_radial_psd,
)

SAMPLES = [  # (WLI file, AFM file, feature height nm)
    ('080nm_50x.datx', '080nm-2um-4.xqd', 80),
    ('160nm_50x.datx', '160nm-2um-1.xqd', 160),
    ('240nm_50x.datx', '240nm-2um-2.xqd', 240),
]
WLI_DIR = os.path.join(OPTICA, 'data', 'Zegage', 'BPRA')
AFM_DIR = os.path.join(OPTICA, 'data', 'AFM', 'BPRA')


def read_datx_surface(path):
    import datx
    height, _unit, attrs, _path = datx.read_surface(path)
    na = float(attrs[1]) if attrs[1] is not None else None
    latres = float(attrs[2]) * 1e6 if attrs[2] is not None else None  # m -> um
    wavelen = None
    with h5py.File(path, 'r') as f:

        def find_wav(name, obj):
            nonlocal wavelen
            if hasattr(obj, 'attrs'):
                for k, v in obj.attrs.items():
                    if k == 'Data Context.Data Attributes.Wavelength:Value':
                        wavelen = float(v[0]) * 1e6
        f.visititems(find_wav)
    return np.asarray(height, dtype=float), na, latres, wavelen


def radial_psd(topography, d_um):
    freqs_x, freqs_y, f_x, f_y = calculate_frequency_mesh_and_axes(topography.shape, d_um)
    psd2d = compute_psd2d(topography, d_um)
    return calculate_radial_psd(freqs_x, freqs_y, f_x, f_y, psd2d)


def model_itf(f, na, lam_um, d_um, pixel=True):
    """Radial average of |OTF|^2 * [sinc(D fx) sinc(D fy)]^2 (incoherent)."""
    vals = []
    for fx, fy in ((f, 0.0), (0.0, f), (f / np.sqrt(2), f / np.sqrt(2))):
        fr = np.sqrt(fx ** 2 + fy ** 2)
        F = np.minimum(fr * lam_um / (2.0 * na), 1.0)
        otf = 2.0 / np.pi * (np.arccos(F) - F * np.sqrt(1 - F ** 2))
        itf = otf ** 2
        if pixel:
            itf = itf * np.sinc(d_um * fx) ** 2 * np.sinc(d_um * fy) ** 2
        vals.append(itf)
    return np.mean(vals, axis=0)


def fit_model(f, psd, na, lam, d, pixel):
    """Fit log PSD = logA + beta log f + log ITF(c*2NA/lam)."""
    from scipy.optimize import least_squares

    def resid(p):
        A, beta, c = np.exp(p[0]), p[1], p[2]
        itf = model_itf(f, na, lam / c, d, pixel=pixel)
        itf = np.maximum(itf, 1e-8)
        return np.log(psd) - np.log(A * f ** beta * itf)

    p0 = [np.log(np.median(psd)), 0.0, 1.0]
    sol = least_squares(resid, p0, method='lm', max_nfev=2000)
    rms = np.sqrt(np.mean(resid(sol.x) ** 2))
    return np.exp(sol.x[0]), sol.x[1], sol.x[2], rms


def main():
    results = []
    for wli_name, afm_name, feat in SAMPLES:
        wli, na, latres, wavelen = read_datx_surface(os.path.join(WLI_DIR, wli_name))
        afm, xres_a, yres_a, xreal_a, yreal_a = read_seiko_xqd(os.path.join(AFM_DIR, afm_name))
        d_afm = (xreal_a / 1e3) / xres_a
        lam = wavelen if wavelen and wavelen > 0 else 0.60

        wli = subtract_polynomial_fit(wli, degree=2)
        afm = subtract_polynomial_fit(afm, degree=2)
        f_w, p_w = radial_psd(wli, latres)
        f_a, p_a = radial_psd(afm, d_afm)

        # primary: free (A, beta, c) fit on WLI PSD, band [0.4, 0.85 Nyquist]
        f_hi = min(0.85 / (2 * latres), 0.95 * 2 * na / lam)
        band = (f_w >= 0.4) & (f_w <= f_hi) & np.isfinite(p_w) & (p_w > 0)
        A_pix, beta_pix, c_pix, rms_pix = fit_model(f_w[band], p_w[band], na, lam, latres, pixel=True)
        A_lens, beta_lens, c_lens, rms_lens = fit_model(f_w[band], p_w[band], na, lam, latres, pixel=False)

        # secondary: measured ITF = WLI/AFM ratio, normalised at 0.75 um^-1
        p_a_i = np.interp(f_w, f_a, p_a)
        b2 = (f_w >= 0.5) & (f_w <= 2.0) & (p_a_i > 0) & np.isfinite(p_w)
        itf_meas = p_w[b2] / p_a_i[b2]
        i_ref = np.argmin(np.abs(f_w[b2] - 0.75))
        itf_meas_n = itf_meas / itf_meas[i_ref]
        itf_model_n = model_itf(f_w[b2], na, lam, latres, pixel=True)
        itf_model_n = itf_model_n / itf_model_n[i_ref]
        corr_itf = np.corrcoef(itf_meas_n, itf_model_n)[0, 1]

        results.append(dict(
            sample=wli_name.replace('.datx', ''),
            feature_height_nm=feat, NA=na, lambda_um=lam, sampling_wli_um=latres,
            nominal_cutoff_mm=2 * na / lam * 1000,
            fit_c_cutoff_pixel=float(c_pix), fit_beta_pixel=float(beta_pix),
            fit_rms_log_pixel=float(rms_pix),
            fit_c_cutoff_lens=float(c_lens), fit_rms_log_lens=float(rms_lens),
            itf_ratio_corr=float(corr_itf),
            n_band_points=int(np.sum(band)),
        ))
        print(f"{wli_name}: c(pixel)={c_pix:.2f} beta={beta_pix:.2f} rms={rms_pix:.2f} | "
              f"c(lens)={c_lens:.2f} rms={rms_lens:.2f} | ITF-ratio corr={corr_itf:.3f}")

    out_json = os.path.join(os.path.dirname(__file__), '..', 'reports', 'public_data_benchmark.json')
    with open(out_json, 'w') as fh:
        json.dump(results, fh, indent=2)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, (wli_name, afm_name, feat) in zip(axes, SAMPLES):
        wli, na, latres, wavelen = read_datx_surface(os.path.join(WLI_DIR, wli_name))
        lam = wavelen if wavelen and wavelen > 0 else 0.60
        wli = subtract_polynomial_fit(wli, degree=2)
        f_w, p_w = radial_psd(wli, latres)
        f_hi = min(0.85 / (2 * latres), 0.95 * 2 * na / lam)
        band = (f_w >= 0.4) & (f_w <= f_hi) & np.isfinite(p_w) & (p_w > 0)
        A, beta, c, rms = fit_model(f_w[band], p_w[band], na, lam, latres, pixel=True)
        f = f_w[band]
        pred = A * f ** beta * model_itf(f, na, lam / c, latres, pixel=True)
        ax.loglog(f_w[band] * 1000, p_w[band], '.', ms=4, label='measured WLI PSD')
        ax.loglog(f * 1000, pred, '-', lw=1.5, label=rf'fit: $\beta={beta:.1f}$, $c={c:.2f}$')
        ax.axvline(2 * na / lam * 1000, color='k', lw=0.6, alpha=0.4)
        ax.set_xlim(right=(2 * na / lam * 1000) * 1.06)
        ax.set_title(f'{feat} nm BPRA (50x)')
        ax.set_xlabel(r'$f$ [mm$^{-1}$]')
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r'radial PSD [nm$^2\,\mu$m$^2$]')
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig_dir = os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'outputs', 'iter01', 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    fig.savefig(os.path.join(fig_dir, 'fig_public_benchmark.pdf'))
    print('wrote', out_json)


if __name__ == '__main__':
    main()
