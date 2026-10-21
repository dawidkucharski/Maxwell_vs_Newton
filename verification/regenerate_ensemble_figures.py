#!/usr/bin/env python3
"""Regenerate figures 3, 5 and 6 with n = 30 ensemble annotations.

The pipeline draws these figures from the baseline run (seed 42), while the
manuscript quotes the n = 30 ensemble. This script redraws the identical
figure content from the saved arrays and replaces every annotation with the
ensemble mean +- std values (fig3, fig6) or the ensemble anisotropy values
(fig5), so the figures match the numbers in the text. Values are formatted
directly from ensemble_stats.json -- nothing is hardcoded.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ITER = os.path.join(ROOT, 'pipeline', 'outputs', 'iter01')
OUT = os.path.join(ITER, 'figures')
ENS = json.load(open(os.path.join(ITER, 'ensemble', 'ensemble_stats.json')))
DM = json.load(open(os.path.join(ITER, 'discovery_metrics.json')))

sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
from block5_discovery_engine import azimuthal_average  # noqa: E402

fx = np.load(os.path.join(ITER, 'fx.npy'))
fy = np.load(os.path.join(ITER, 'fy.npy'))
I_field = np.load(os.path.join(ITER, 'I_field_2d.npy'))
H_stylus = np.load(os.path.join(ITER, 'H_stylus_2d.npy'))
H_optical = np.load(os.path.join(ITER, 'H_optical_2d.npy'))

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10,
    'axes.labelsize': 11, 'axes.titlesize': 11,
    'legend.fontsize': 8, 'figure.dpi': 150,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.08,
})


def fig3():
    f_max = np.max(fx) * 1e-3 * 0.92
    extent = [-f_max, f_max, -f_max, f_max]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)

    im = axes[0].imshow(I_field, extent=extent, origin='lower', cmap='hot',
                        aspect='equal')
    axes[0].set_title(r'(a)  $I(f_x, f_y)$', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[0].set_xlabel(r'$f_x$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'$f_y$ [mm$^{-1}$]')
    fig.colorbar(im, ax=axes[0], label='$I$ [decades]', fraction=0.046, pad=0.02)

    f_r, I_rad = azimuthal_average(I_field, fx, fy)
    axes[1].semilogx(f_r * 1e-3, I_rad, 'k-', linewidth=1.4)
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'$\langle I\rangle(f)$ [decades]')
    axes[1].set_title(r'(b)  Azimuthal Average', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[1].grid(True, alpha=0.3, which='both')
    axes[1].set_xlim([f_r[2] * 1e-3, f_max * 1.05])

    Ls = ENS['I_stylus_mean'] / 1e12
    dLs = ENS['I_stylus_std'] / 1e12
    Lo = ENS['I_optical_mean'] / 1e12
    dLo = ENS['I_optical_std'] / 1e12
    Ss, dSs = ENS['mi_stylus_mean'], ENS['mi_stylus_std']
    So, dSo = ENS['mi_optical_mean'], ENS['mi_optical_std']
    textstr = (f"$L_{{\\rm s}}=({Ls:.2f}\\pm{dLs:.2f})\\times10^{{12}}$\n"
               f"$L_{{\\rm o}}=({Lo:.2f}\\pm{dLo:.2f})\\times10^{{12}}$\n"
               f"$\\mathcal{{S}}_{{\\rm s}}={Ss:.3f}\\pm{dSs:.3f}$\n"
               f"$\\mathcal{{S}}_{{\\rm o}}={So:.3f}\\pm{dSo:.3f}$\n"
               f"($n=30$)")
    axes[1].text(0.97, 0.97, textstr, transform=axes[1].transAxes, va='top',
                 ha='right', fontsize=8, family='monospace',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    fig.savefig(os.path.join(OUT, 'fig3_information_loss.pdf'))
    plt.close(fig)
    print('  Figure 3 saved (ensemble annotations)')


def tensor_from_degree_angle(alpha, theta_deg):
    lam1 = 1.0
    lam2 = (1.0 - alpha) / (1.0 + alpha)
    t = np.radians(theta_deg)
    v = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return np.array([lam1, lam2]), v


def fig5():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), constrained_layout=True)

    def plot_tensor(ax, eigvals, eigvecs, alpha, color):
        ratio = eigvals[1] / eigvals[0]
        angle = np.degrees(np.arctan2(eigvecs[1, 0], eigvecs[0, 0]))
        a_major = 2.4
        a_minor = max(0.3, a_major * (1.0 - 5.0 * alpha))
        if a_minor >= a_major * 0.995:
            a_minor = a_major * 0.95
        ellipse = Ellipse((0, 0), a_major, a_minor, angle=angle,
                          facecolor=color, alpha=0.30, edgecolor=color,
                          linewidth=3.0)
        ax.add_patch(ellipse)
        vec_maj = eigvecs[:, 0]
        ax.arrow(0, 0, vec_maj[0] * a_major * 0.55, vec_maj[1] * a_major * 0.55,
                 head_width=0.14, head_length=0.18, fc=color, ec=color,
                 alpha=0.9, linewidth=2.2, length_includes_head=True, zorder=5)
        ax.add_patch(plt.Circle((0, 0), a_major * 0.5, fill=False,
                                color='gray', linestyle=(0, (5, 5)),
                                linewidth=1.8, alpha=0.6, zorder=2))
        lim = a_major * 0.85
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        ax.set_aspect('equal')
        ax.axhline(0, color='gray', linewidth=0.4, alpha=0.25)
        ax.axvline(0, color='gray', linewidth=0.4, alpha=0.25)
        ax.set_xlabel(r'$f_x$ direction')
        ax.set_ylabel(r'$f_y$ direction')
        # annotation uses ensemble values (passed via the caller)
        return ratio

    panels = [
        ('stylus', axes[0], '#2166ac',
         ENS['alpha_stylus_mean'], ENS['alpha_stylus_std']),
        ('optical', axes[1], '#b2182b',
         ENS['alpha_optical_mean'], ENS['alpha_optical_std']),
    ]
    base_alpha = {
        'stylus': DM['anisotropy']['stylus']['anisotropy_degree'],
        'optical': DM['anisotropy']['optical']['anisotropy_degree'],
    }
    base_theta = {
        'stylus': DM['anisotropy']['stylus']['principal_angle_deg'],
        'optical': DM['anisotropy']['optical']['principal_angle_deg'],
    }
    for modality, ax, color, amean, astd in panels:
        ev, evec = tensor_from_degree_angle(base_alpha[modality],
                                            base_theta[modality])
        plot_tensor(ax, ev, evec, base_alpha[modality], color)
        ax.text(0.97, 0.05,
                r'$\alpha = ' + f'{amean:.4f} \pm {astd:.4f}$' + '\n'
                r'($n = 30$)',
                transform=ax.transAxes, va='bottom', ha='right', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='white',
                          edgecolor='gray', alpha=0.9))
    axes[0].set_title('(a)  Stylus Profilometry', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[1].set_title('(b)  Optical Interferometry', loc='left', fontsize=10.5,
                      fontweight='bold')
    fig.savefig(os.path.join(OUT, 'fig5_anisotropy_tensor.pdf'))
    plt.close(fig)
    print('  Figure 5 saved (ensemble annotations)')


def fig6():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)

    center = H_stylus.shape[0] // 2
    f_x_mm = fx * 1e-3
    pos = fx > 0
    H_s_x = H_stylus[center, pos]
    H_o_x = H_optical[center, pos]
    axes[0].semilogx(f_x_mm[pos], H_s_x, 'b-', linewidth=1.5, label='Stylus')
    axes[0].semilogx(f_x_mm[pos], H_o_x, 'r-', linewidth=1.5, label='Optical')
    axes[0].fill_between(f_x_mm[pos], H_s_x, H_o_x, alpha=0.15, color='purple')
    axes[0].set_xlabel(r'$f_x$ [mm$^{-1}$]')
    axes[0].set_ylabel(r'$H(f_x, 0)$')
    axes[0].set_title('(a)  Transfer Along $f_x$', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[0].legend(loc='upper right', framealpha=0.85, fontsize=8)
    axes[0].grid(True, alpha=0.3, which='both')
    ymax_a = max(np.percentile(H_s_x, 99), np.percentile(H_o_x, 99)) * 1.1
    axes[0].set_ylim([0, max(ymax_a, 1.2)])

    H_diff_db = 10.0 * np.abs(
        np.log10(np.clip(H_stylus, 1e-10, None)) -
        np.log10(np.clip(H_optical, 1e-10, None)))
    f_max = np.max(fx) * 1e-3 * 0.92
    extent = [-f_max, f_max, -f_max, f_max]
    vmax_db = np.percentile(H_diff_db, 95)
    im = axes[1].imshow(H_diff_db, extent=extent, origin='lower',
                        cmap='RdYlGn_r', aspect='equal', vmin=0, vmax=vmax_db)
    axes[1].set_title(r'(b)  $|H_s - H_o|$ [dB]', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[1].set_xlabel(r'$f_x$ [mm$^{-1}$]')
    axes[1].set_ylabel(r'$f_y$ [mm$^{-1}$]')
    fig.colorbar(im, ax=axes[1], label='dB', fraction=0.046, pad=0.02)
    Nx, Ny = H_diff_db.shape[1], H_diff_db.shape[0]
    axes[1].contour(np.linspace(-f_max, f_max, Nx),
                    np.linspace(-f_max, f_max, Ny), H_diff_db,
                    levels=[3.0], colors='white', linewidths=1.8)
    axes[1].text(0, -f_max * 0.78, r'$\leq 3$ dB', color='white', fontsize=8,
                 ha='center',
                 bbox=dict(facecolor='black', alpha=0.4,
                           boxstyle='round,pad=0.2'))

    thresholds = [1, 2, 3, 6]
    frac = DM['crossover_analysis']['equivalence_fraction_vs_threshold']
    fractions = [frac[f'{t}dB'] * 100 for t in thresholds]
    fractions[2] = ENS['eq_frac_mean'] * 100          # ensemble at 3 dB
    errs = [0.0, 0.0, ENS['eq_frac_std'] * 100, 0.0]
    colors_bar = ['#2ca02c', '#bcbd22', '#d62728', '#7f7f7f']
    bars = axes[2].bar(thresholds, fractions, width=0.8, color=colors_bar,
                       edgecolor='white', linewidth=0.5,
                       yerr=errs, capsize=4, error_kw={'elinewidth': 1.2})
    axes[2].set_xlabel('Threshold [dB]')
    axes[2].set_ylabel(r'$k$-space fraction [%]')
    axes[2].set_title('(c)  Equivalence Regime Size', loc='left', fontsize=10.5,
                      fontweight='bold')
    axes[2].set_ylim([0, max(100, max(fractions) * 1.25)])
    axes[2].set_xticks(thresholds)
    for bar, fr in zip(bars, fractions):
        axes[2].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                     f'{fr:.1f}%', ha='center', fontsize=8.5)
    fc_mean = ENS['f_cross_mean'] * 1e-3
    fc_std = ENS['f_cross_std'] * 1e-3
    lam_cross = 1e3 / fc_mean
    eqm, eqs = ENS['eq_frac_mean'] * 100, ENS['eq_frac_std'] * 100
    axes[2].text(0.5, 0.30,
                 f"$3$ dB: ${eqm:.1f} \\pm {eqs:.1f}$\\% ($n=30$)\n"
                 f"$f_{{\\rm cross}}={fc_mean:.0f}\\pm{fc_std:.0f}$ mm$^{{-1}}$\n"
                 f"$\\lambda_{{\\rm cross}}={lam_cross:.1f}$ \u00b5m\n"
                 f"(1, 2, 6 dB bars: baseline run)",
                 transform=axes[2].transAxes, fontsize=8, ha='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    fig.savefig(os.path.join(OUT, 'fig6_crossover_analysis.pdf'))
    plt.close(fig)
    print('  Figure 6 saved (ensemble annotations)')


if __name__ == '__main__':
    fig3()
    fig5()
    fig6()
