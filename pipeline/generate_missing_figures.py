#!/usr/bin/env python3
"""
Phase 9 reproducibility: regenerate the four figures that lacked generators.
- fig7_channel_capacity.pdf : from block4+block5+block8 recomputation
- fig8_cramer_rao.pdf       : Fisher/CRB radial spectra from block8
- fig10_ensemble_validation : from stored ensemble_stats.json (30-run ensemble)
- figS2_fusion_demo.pdf     : from block10 three-way comparison + Eq. fusion
Also refreshes fig1-fig6 via visualisation.generate_all_figures on the fresh
block4/block5 outputs (same seeds as the committed baseline).
"""
import os
import sys

import numpy as np

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

from block4_physics_simulator import run_block4, SimulationParams  # noqa: E402
from block5_discovery_engine import run_block5                      # noqa: E402
from block8_info_theory import (                                    # noqa: E402
    compute_fisher_information_spectrum,
    compute_channel_capacity,
)
from block10_scatterometry import run_three_way_comparison          # noqa: E402
from visualisation import generate_all_figures                      # noqa: E402

OUT = os.path.join(PIPE, 'outputs', 'iter01')


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


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'serif', 'font.size': 10,
        'axes.labelsize': 11, 'axes.titlesize': 11,
        'legend.fontsize': 9, 'figure.dpi': 150,
        'savefig.dpi': 300, 'savefig.bbox': 'tight',
    })

    print('=== block4 + block5 (baseline, seed 42 inside run_simulation) ===')
    result = run_block4(baseline_params(), output_dir=OUT)
    discovery = run_block5(result, output_dir=OUT)
    tf = discovery.transfer_functions

    print('=== block8: Fisher + capacity ===')
    fisher = compute_fisher_information_spectrum(result, tf)
    capacity = compute_channel_capacity(result, tf)

    # ---- fig7: spectral information density + water filling -----------------
    f_r = capacity['C_radial'] * 1e-3  # mm^-1
    iota_s = 0.5 * capacity['C_stylus_1d']
    iota_o = 0.5 * capacity['C_optical_1d']
    snr_s = np.clip(capacity['SNR_stylus_2d'], 0, 1e8)
    snr_o = np.clip(capacity['SNR_optical_2d'], 0, 1e8)

    def waterfill(snr_2d, budget=1.0, tol=1e-6, max_iter=200):
        """Classical water-filling over 2D modes: P_i = max(0, mu - 1/SNR_i)."""
        inv = 1.0 / np.maximum(snr_2d.ravel(), 1e-30)
        lo, hi = inv.min(), inv.max() + budget / max(inv.size, 1)
        mu = hi
        for _ in range(max_iter):
            alloc = np.maximum(0.0, mu - inv)
            diff = alloc.sum() - budget
            if abs(diff) < tol * max(budget, 1.0):
                break
            if diff > 0:
                hi = mu
            else:
                lo = mu
            mu = 0.5 * (lo + hi)
        return alloc.reshape(snr_2d.shape)

    alloc_s = waterfill(snr_s)
    alloc_o = waterfill(snr_o)
    from block5_discovery_engine import azimuthal_average
    _, alloc_s_1d = azimuthal_average(alloc_s, result.fx, result.fy)
    _, alloc_o_1d = azimuthal_average(alloc_o, result.fx, result.fy)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
    axes[0].semilogx(f_r, iota_s, label='stylus')
    axes[0].semilogx(f_r, iota_o, label='optical')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'$\iota(f)$ [bits per mode]')
    axes[0].set_title('(a) Spectral information density')
    axes[0].legend(); axes[0].grid(alpha=0.3)
    axes[1].semilogx(f_r, alloc_s_1d / max(alloc_s_1d.max(), 1e-30), label='stylus')
    axes[1].semilogx(f_r, alloc_o_1d / max(alloc_o_1d.max(), 1e-30), label='optical')
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'$S_h^*(f)$ [normalised]')
    axes[1].set_title('(b) Water-filling allocation')
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.savefig(os.path.join(OUT, 'figures', 'fig7_channel_capacity.pdf'))
    plt.close(fig)
    print('  wrote fig7_channel_capacity.pdf')

    # ---- fig8: Cramer-Rao bound ---------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
    f_f = fisher['F_radial'] * 1e-3
    axes[0].loglog(f_f, fisher['CRB_stylus_1d'], label='stylus')
    axes[0].loglog(f_f, fisher['CRB_optical_1d'], label='optical')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'CRB on $\hat{H}(f)$')
    axes[0].set_title('(a) Cramer--Rao bound')
    axes[0].legend(); axes[0].grid(alpha=0.3)
    axes[1].semilogx(f_f, fisher['F_stylus_1d'], label='stylus')
    axes[1].semilogx(f_f, fisher['F_optical_1d'], label='optical')
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'Fisher information $F(f)$')
    axes[1].set_title('(b) Fisher information spectrum')
    axes[1].legend(); axes[1].grid(alpha=0.3)
    fig.savefig(os.path.join(OUT, 'figures', 'fig8_cramer_rao.pdf'))
    plt.close(fig)
    print('  wrote fig8_cramer_rao.pdf')

    # ---- figS2: k-space trust-region fusion ---------------------------------
    print('=== block10: three-way comparison (fusion) ===')
    three_way = run_three_way_comparison(result, discovery, os.path.join(OUT, 'scatterometry'))
    f_r = three_way.f_radial * 1e-3
    psd_true = three_way.psd_true_1d
    psd_s = azimuthal_average(three_way.psd_stylus, result.fx, result.fy)[1]
    psd_o = azimuthal_average(three_way.psd_optical, result.fx, result.fy)[1]
    psd_sc = azimuthal_average(three_way.psd_scatterometry, result.fx, result.fy)[1]
    H_s = three_way.H_stylus_1d
    H_o = three_way.H_optical_1d
    H_sc = three_way.H_scat_1d

    def noise_floor_psd(psd_1d, frac=0.05):
        return np.quantile(psd_1d[psd_1d > 0], frac) if np.any(psd_1d > 0) else 1e-35

    n_s, n_o, n_sc = noise_floor_psd(psd_s), noise_floor_psd(psd_o), noise_floor_psd(psd_sc)
    w_s = np.clip(H_s, 0, 10) ** 2 / max(n_s, 1e-35)
    w_o = np.clip(H_o, 0, 10) ** 2 / max(n_o, 1e-35)
    w_sc = np.clip(H_sc, 0, 10) ** 2 / max(n_sc, 1e-35)
    psd_fused = (psd_s * w_s + psd_o * w_o + psd_sc * w_sc) / np.maximum(w_s + w_o + w_sc, 1e-35)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
    axes[0].loglog(f_r, psd_true, 'k-', lw=1.5, label='true')
    axes[0].loglog(f_r, psd_s, alpha=0.7, label='stylus')
    axes[0].loglog(f_r, psd_o, alpha=0.7, label='WLI')
    axes[0].loglog(f_r, psd_sc, alpha=0.7, label='scatterometry')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[0].set_ylabel('PSD')
    axes[0].set_title('(a) Individual estimates')
    axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)
    axes[1].loglog(f_r, psd_true, 'k-', lw=1.5, label='true')
    axes[1].loglog(f_r, psd_fused, 'r--', lw=1.5, label='fused (Eq. fusion)')
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[1].set_ylabel('PSD')
    axes[1].set_title('(b) Trust-region fusion')
    axes[1].legend(fontsize=7); axes[1].grid(alpha=0.3)
    fig.savefig(os.path.join(OUT, 'figures', 'figS2_fusion_demo.pdf'))
    plt.close(fig)
    print('  wrote figS2_fusion_demo.pdf')

    # ---- fig10: ensemble validation (from stored 30-run ensemble stats) ------
    import json
    with open(os.path.join(OUT, 'ensemble', 'ensemble_stats.json')) as fh:
        ens = json.load(fh)
    f_e = np.array(ens['f_radial']) * 1e-3
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    axes[0].semilogx(f_e, ens['H_stylus_mean'], label='stylus')
    axes[0].fill_between(f_e,
                         np.array(ens['H_stylus_mean']) - np.array(ens['H_stylus_std']),
                         np.array(ens['H_stylus_mean']) + np.array(ens['H_stylus_std']),
                         alpha=0.25)
    axes[0].semilogx(f_e, ens['H_optical_mean'], label='optical')
    axes[0].fill_between(f_e,
                         np.array(ens['H_optical_mean']) - np.array(ens['H_optical_std']),
                         np.array(ens['H_optical_mean']) + np.array(ens['H_optical_std']),
                         alpha=0.25)
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[0].set_ylabel(r'$H(f)$ (mean$\pm$std, $n=30$)')
    axes[0].set_title('(a) Ensemble transfer functions')
    axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)
    axes[1].bar(['stylus', 'optical'],
                [ens['rmse_stylus_mean'] * 1e9, ens['rmse_optical_mean'] * 1e9],
                yerr=[ens['rmse_stylus_std'] * 1e9, ens['rmse_optical_std'] * 1e9],
                color=['#4472C4', '#ED7D31'], capsize=4)
    axes[1].set_ylabel('RMSE [nm]'); axes[1].set_title('(b) RMSE, $n=30$')
    axes[2].bar(['stylus', 'optical'],
                [ens['alpha_stylus_mean'], ens['alpha_optical_mean']],
                yerr=[ens['alpha_stylus_std'], ens['alpha_optical_std']],
                color=['#4472C4', '#ED7D31'], capsize=4)
    axes[2].set_ylabel(r'$\alpha$'); axes[2].set_title(r'(c) Anisotropy, $n=30$')
    fig.savefig(os.path.join(OUT, 'figures', 'fig10_ensemble_validation.pdf'))
    plt.close(fig)
    print('  wrote fig10_ensemble_validation.pdf')

    # ---- refresh fig1-fig6 from the same fresh outputs ----------------------
    print('=== visualisation: fig1-fig6 ===')
    generate_all_figures(result, discovery, OUT)
    print('  regenerated fig1-fig6')


if __name__ == '__main__':
    main()
