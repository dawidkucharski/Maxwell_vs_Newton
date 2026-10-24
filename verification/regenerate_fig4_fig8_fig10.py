#!/usr/bin/env python3
"""
Figure audit repairs (graphics only, no changes to science):

1. fig4_azimuthal_profiles.pdf  — panel (b) now plots the transfer functions
   with the manuscript's committed estimator: the ratio of azimuthal means of
   Hanning-windowed periodograms (variant_simulations.psd2d), reproducing the
   headline values H_stylus = 2.2 / 0.91 / 0.74 / 0.57 at 17 / 292 / 567 /
   843 mm^-1 and the 3 dB point at 1049 mm^-1 (verified by T10). The previous
   committed PDF used the average-of-ratios estimator, whose azimuthal profile
   disagree with the manuscript. Panel (b) uses a logarithmic y-axis so both
   the passband structure and the noise-dominated optical rise above the
   unwrapping-error floor are fully visible (no clipping). Panel (a) is
   unchanged.

2. fig8_cramer_rao.pdf — the committed PDF saturated both curves against an
   arbitrary display clip (F clipped at 1e20, CRB flat at 1e-20). The clip is
   removed here; the Fisher spectrum is plotted on a log-y axis. Computation
   is identical to block8 (amplitude convention, difference-field noise-floor
   median), only the artificial display cap is gone.

3. fig10_ensemble_validation.pdf — panel (a) redrawn from the updated
   ensemble_stats.json whose H curves now use the same ratio-of-azimuthal-means
   estimator (see run_ensemble.py), so it is consistent with fig4(b); a
   logarithmic y-axis is used for the same full-visibility treatment. Panels
   (b)/(c) are unchanged.

All outputs are vector PDFs written to pipeline/outputs/iter01/figures/.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ITER = os.path.join(ROOT, 'pipeline', 'outputs', 'iter01')
OUT = os.path.join(ITER, 'figures')
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))

from block5_discovery_engine import azimuthal_average, compute_psd_2d  # noqa: E402
from variant_simulations import psd2d  # noqa: E402

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10,
    'axes.labelsize': 11, 'axes.titlesize': 11,
    'legend.fontsize': 9, 'figure.dpi': 150,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.08,
})

N = 512
DX = 100e-6 / N


def load(name):
    return np.load(os.path.join(ITER, name))


def ratio_of_azmeans(psd_meas, psd_true, fx, fy):
    """Committed manuscript estimator: ratio of azimuthal means."""
    fr, p_t = azimuthal_average(psd_true, fx, fy)
    _, p_m = azimuthal_average(psd_meas, fx, fy)
    return fr, p_m / np.maximum(p_t, 1e-30)


def fig4():
    h_t = load('h_true.npy')
    h_s = load('h_stylus.npy')
    h_o = load('h_optical.npy')
    fx = load('fx.npy')
    fy = load('fy.npy')

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)

    # ---- (a) PSDs: unchanged from visualisation.fig_azimuthal_profiles ----
    f_r, psd_t = azimuthal_average(compute_psd_2d(h_t, DX), fx, fy)
    _, psd_s = azimuthal_average(compute_psd_2d(h_s, DX), fx, fy)
    _, psd_o = azimuthal_average(compute_psd_2d(h_o, DX), fx, fy)
    axes[0].loglog(f_r * 1e-3, psd_t, 'k-', linewidth=1.5, label='True')
    axes[0].loglog(f_r * 1e-3, psd_s, 'b--', linewidth=1.2, label='Stylus')
    axes[0].loglog(f_r * 1e-3, psd_o, 'r-.', linewidth=1.2, label='Optical')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'PSD [m$^3$]')
    axes[0].set_title('(a)  Power Spectral Density', loc='left', fontsize=10.5,
                      fontweight='bold', pad=12)
    axes[0].legend(loc='lower left', framealpha=0.85)
    axes[0].grid(True, alpha=0.3, which='both')

    # ---- (b) transfer functions: manuscript-consistent estimator ----
    fr, H_s = ratio_of_azmeans(psd2d(h_s, DX), psd2d(h_t, DX), fx, fy)
    fr, H_o = ratio_of_azmeans(psd2d(h_o, DX), psd2d(h_t, DX), fx, fy)
    fmm = fr * 1e-3
    axes[1].semilogx(fmm, H_s, 'b-', linewidth=1.5, label='Stylus')
    axes[1].semilogx(fmm, H_o, 'r-', linewidth=1.5, label='Optical')
    axes[1].set_yscale('log')
    axes[1].axhline(1.0, color='gray', linestyle=':', linewidth=0.6)
    axes[1].axhline(0.5, color='gray', linestyle=(0, (1, 3)), linewidth=0.6)
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'$H(f)$')
    axes[1].set_title('(b)  Transfer Functions', loc='left', fontsize=10.5,
                      fontweight='bold', pad=12)
    axes[1].legend(loc='lower left', framealpha=0.85)
    axes[1].grid(True, alpha=0.3, which='both')
    axes[1].set_ylim([0.03, 300.0])
    axes[1].set_xlim([fmm[2], fmm[-1] * 1.05])

    # markers: optical cutoff (2000 mm^-1) and stylus tip-radius scale
    # (1/(pi r_tip) = 159 mm^-1), as in the committed figure
    for fc, lbl, clr in [(2000.0, 'Opt.', 'red'), (159.0, 'Sty.', 'blue')]:
        axes[1].axvline(fc, color=clr, linestyle=':', alpha=0.6, linewidth=1)
        axes[1].text(fc * 1.05, 0.42, lbl, color=clr, fontsize=7, rotation=90)

    fig.savefig(os.path.join(OUT, 'fig4_azimuthal_profiles.pdf'))
    plt.close(fig)
    print('  wrote fig4_azimuthal_profiles.pdf (ratio-of-azimuthal-means)')


def fig8():
    """Fisher / CRB spectra without the artificial 1e20 display clip."""
    h_t = load('h_true.npy')
    h_s = load('h_stylus.npy')
    h_o = load('h_optical.npy')
    fx = load('fx.npy')
    fy = load('fy.npy')
    H_pow_s = load('H_stylus_2d.npy')   # power transfer (committed 2D field)
    H_pow_o = load('H_optical_2d.npy')

    # same noise-floor estimate as block8: median of difference-field PSD
    for diff, name in [(h_s - h_t, 's'), (h_o - h_t, 'o')]:
        psd_d = compute_psd_2d(diff, DX)
        nf = np.median(psd_d[psd_d > 0]) if np.any(psd_d > 0) else 1e-35
        nf = max(float(nf), 1e-35)
        print(f'  noise floor {name}: {nf:.3e}')

    psd_ds = compute_psd_2d(h_s - h_t, DX)
    psd_do = compute_psd_2d(h_o - h_t, DX)
    nf_s = max(float(np.median(psd_ds[psd_ds > 0])), 1e-35)
    nf_o = max(float(np.median(psd_do[psd_do > 0])), 1e-35)

    F_s = H_pow_s / nf_s          # |H_amp|^2 / N  (amplitude convention)
    F_o = H_pow_o / nf_o
    CRB_s = 1.0 / (F_s + 1e-35)
    CRB_o = 1.0 / (F_o + 1e-35)

    f_f, F_s_1d = azimuthal_average(F_s, fx, fy)
    _, F_o_1d = azimuthal_average(F_o, fx, fy)
    _, CRB_s_1d = azimuthal_average(CRB_s, fx, fy)
    _, CRB_o_1d = azimuthal_average(CRB_o, fx, fy)
    fmm = f_f * 1e-3

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
    axes[0].loglog(fmm, CRB_s_1d, label='stylus')
    axes[0].loglog(fmm, CRB_o_1d, label='optical')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'CRB on $\hat{H}(f)$')
    axes[0].set_title('(a) Cramer--Rao bound')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].loglog(fmm, F_s_1d, label='stylus')
    axes[1].loglog(fmm, F_o_1d, label='optical')
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'Fisher information $F(f)$')
    axes[1].set_title('(b) Fisher information spectrum')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.savefig(os.path.join(OUT, 'fig8_cramer_rao.pdf'))
    plt.close(fig)
    print('  wrote fig8_cramer_rao.pdf (no display clip, log-y Fisher)')


def fig10():
    ens = json.load(open(os.path.join(ITER, 'ensemble', 'ensemble_stats.json')))
    f_e = np.array(ens['f_radial']) * 1e-3
    H_sm = np.array(ens['H_stylus_mean'])
    H_sd = np.array(ens['H_stylus_std'])
    H_om = np.array(ens['H_optical_mean'])
    H_od = np.array(ens['H_optical_std'])

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    axes[0].semilogx(f_e, H_sm, label='stylus')
    axes[0].fill_between(f_e, H_sm - H_sd, H_sm + H_sd, alpha=0.25)
    axes[0].semilogx(f_e, H_om, label='optical')
    axes[0].fill_between(f_e, H_om - H_od, H_om + H_od, alpha=0.25)
    axes[0].set_yscale('log')
    axes[0].axhline(1.0, color='gray', linestyle=':', linewidth=0.6)
    axes[0].axhline(0.5, color='gray', linestyle=(0, (1, 3)), linewidth=0.6)
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'$H(f)$ (mean$\pm$std, $n=30$)')
    axes[0].set_title('(a) Ensemble transfer functions')
    axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim([0.03, 300.0])
    axes[0].set_xlim([f_e[2], f_e[-1] * 1.05])

    axes[1].bar(['stylus', 'optical'],
                [ens['rmse_stylus_mean'] * 1e9, ens['rmse_optical_mean'] * 1e9],
                yerr=[ens['rmse_stylus_std'] * 1e9, ens['rmse_optical_std'] * 1e9],
                color=['#4472C4', '#ED7D31'], capsize=4)
    axes[1].set_ylabel('RMSE [nm]')
    axes[1].set_title('(b) RMSE, $n=30$')

    axes[2].bar(['stylus', 'optical'],
                [ens['alpha_stylus_mean'], ens['alpha_optical_mean']],
                yerr=[ens['alpha_stylus_std'], ens['alpha_optical_std']],
                color=['#4472C4', '#ED7D31'], capsize=4)
    axes[2].set_ylabel(r'$\alpha$')
    axes[2].set_title(r'(c) Anisotropy, $n=30$')

    fig.savefig(os.path.join(OUT, 'fig10_ensemble_validation.pdf'))
    plt.close(fig)
    print('  wrote fig10_ensemble_validation.pdf (consistent estimator)')


if __name__ == '__main__':
    fig4()
    fig8()
    fig10()
