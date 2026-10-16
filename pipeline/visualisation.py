"""
Pipeline Visualisation Module (v4 — labels outside + fixed y-scales)
=====================================================================
Panel labels (a)(b)(c) placed OUTSIDE plot boxes via ax.set_title(loc='left').
Fixed: H(f) y-axis auto-scaled (was clipped at 1.05, hiding data > 1).
Fixed: anisotropy ellipse clearly distinguished from reference circle.
Fixed: difference map colormap uses full data range.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import os

from block4_physics_simulator import SimulationResult
from block5_discovery_engine import DiscoveryResult

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10,
    'axes.labelsize': 11, 'axes.titlesize': 11,
    'legend.fontsize': 8, 'figure.dpi': 150,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.08,
})


# ═══════════════════════════════════════════════════════════
# Figure 1 — Surface Comparison
# ═══════════════════════════════════════════════════════════
def fig_surface_comparison(result, output_dir):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)
    L = result.params.physical_size * 1e6
    extent = [-L/2, L/2, -L/2, L/2]
    vmin = np.percentile(result.h_true, 2) * 1e9
    vmax = np.percentile(result.h_true, 98) * 1e9
    labels = ['(a)', '(b)', '(c)']
    subtitles = ['True Surface  $h(x,y)$', 'Stylus Measured', 'Optical Measured']
    data = [result.h_true, result.h_stylus, result.h_optical]

    for ax, h, lab, sub in zip(axes, data, labels, subtitles):
        im = ax.imshow(h * 1e9, extent=extent, origin='lower', cmap='RdYlBu_r',
                       vmin=vmin, vmax=vmax, aspect='equal', rasterized=True)
        ax.set_title(f'{lab}  {sub}', loc='left', fontsize=10.5,
                     fontweight='bold' if lab in ['(a)','(b)','(c)'] else 'normal')
        ax.set_xlabel('$x$ [µm]')
        ax.set_ylabel('$y$ [µm]' if ax == axes[0] else '')

    cbar = fig.colorbar(im, ax=axes[2], label='Height [nm]', fraction=0.046, pad=0.02)
    bbox_kw = dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.85)
    axes[1].text(0.97, 0.97, f"RMSE={result.rmse_stylus*1e9:.1f} nm\n$r$={result.correlation_stylus:.3f}",
                 transform=axes[1].transAxes, va='top', ha='right', fontsize=7.5, bbox=bbox_kw)
    axes[2].text(0.97, 0.97, f"RMSE={result.rmse_optical*1e9:.1f} nm\n$r$={result.correlation_optical:.3f}",
                 transform=axes[2].transAxes, va='top', ha='right', fontsize=7.5, bbox=bbox_kw)
    fig.savefig(os.path.join(output_dir, 'fig1_surface_comparison.pdf'))
    plt.close(fig)
    print("  Figure 1 saved")


# ═══════════════════════════════════════════════════════════
# Figure 2 — Transfer Functions
# ═══════════════════════════════════════════════════════════
def fig_transfer_functions(discovery, result, output_dir):
    tf = discovery.transfer_functions
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    f_max = np.max(tf.fx) * 1e-3 * 0.92
    extent = [-f_max, f_max, -f_max, f_max]
    H_data = [tf.H_stylus, tf.H_optical, tf.H_ratio]
    labels = ['(a)', '(b)', '(c)']
    subtitles = [r'$H_{\rm stylus}(f_x, f_y)$', r'$H_{\rm optical}(f_x, f_y)$',
                 r'$H_{\rm opt}\,/\,H_{\rm stylus}$']
    cmaps = ['viridis', 'viridis', 'RdBu_r']

    for ax, H, lab, sub, cmap in zip(axes, H_data, labels, subtitles, cmaps):
        H_disp = np.log10(np.clip(H, 0.001, 10.0))
        vmin_u = -2.0 if cmap == 'viridis' else -1.0
        im = ax.imshow(H_disp, extent=extent, origin='lower', cmap=cmap,
                       aspect='equal', vmin=vmin_u, vmax=1.0)
        ax.set_title(f'{lab}  {sub}', loc='left', fontsize=10, fontweight='bold')
        ax.set_xlabel(r'$f_x$ [mm$^{-1}$]')
        ax.set_ylabel(r'$f_y$ [mm$^{-1}$]' if ax == axes[0] else '')

    cbar = fig.colorbar(im, ax=axes[2], label=r'$\log_{10} H$', fraction=0.046, pad=0.02)
    f_c_opt = result.params.optical_cutoff * 1e-3
    for ax in axes[:2]:
        ax.add_patch(plt.Circle((0, 0), f_c_opt * 0.92, fill=False, color='white',
                                 linestyle='--', linewidth=1.2, alpha=0.8))
        ax.text(f_c_opt * 0.55, -f_max * 0.82, r'$f_{\!\rm cut}$', color='white', fontsize=7.5)
    fig.savefig(os.path.join(output_dir, 'fig2_transfer_functions.pdf'))
    plt.close(fig)
    print("  Figure 2 saved")


# ═══════════════════════════════════════════════════════════
# Figure 3 — Information Loss
# ═══════════════════════════════════════════════════════════
def fig_information_loss(discovery, output_dir):
    info = discovery.information_loss; tf = discovery.transfer_functions
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    f_max = np.max(tf.fx) * 1e-3 * 0.92
    extent = [-f_max, f_max, -f_max, f_max]

    im = axes[0].imshow(info.I_field, extent=extent, origin='lower', cmap='hot', aspect='equal')
    axes[0].set_title(r'(a)  $I(f_x, f_y)$', loc='left', fontsize=10.5, fontweight='bold')
    axes[0].set_xlabel(r'$f_x$ [mm$^{-1}$]'); axes[0].set_ylabel(r'$f_y$ [mm$^{-1}$]')
    fig.colorbar(im, ax=axes[0], label='$I$ [decades]', fraction=0.046, pad=0.02)

    axes[1].semilogx(tf.f_radial * 1e-3, info.I_radial, 'k-', linewidth=1.4)
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[1].set_ylabel(r'$\langle I\rangle(f)$ [decades]')
    axes[1].set_title(r'(b)  Azimuthal Average', loc='left', fontsize=10.5, fontweight='bold')
    axes[1].grid(True, alpha=0.3, which='both')
    axes[1].set_xlim([tf.f_radial[2] * 1e-3, f_max * 1.05])
    textstr = (f"$L_{{\\rm s}}$={info.I_stylus:.2e}\n$L_{{\\rm o}}$={info.I_optical:.2e}\n"
               f"MI$_s$={info.mi_stylus:.3f}\nMI$_o$={info.mi_optical:.3f}")
    axes[1].text(0.97, 0.97, textstr, transform=axes[1].transAxes, va='top', ha='right',
                 fontsize=8, family='monospace',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    fig.savefig(os.path.join(output_dir, 'fig3_information_loss.pdf'))
    plt.close(fig)
    print("  Figure 3 saved")


# ═══════════════════════════════════════════════════════════
# Figure 4 — Azimuthal Profiles
# ═══════════════════════════════════════════════════════════
def fig_azimuthal_profiles(discovery, result, output_dir):
    tf = discovery.transfer_functions
    from block5_discovery_engine import compute_psd_2d, azimuthal_average
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    dx = result.params.dx
    f_r, psd_t = azimuthal_average(compute_psd_2d(result.h_true, dx), result.fx, result.fy)
    _, psd_s = azimuthal_average(compute_psd_2d(result.h_stylus, dx), result.fx, result.fy)
    _, psd_o = azimuthal_average(compute_psd_2d(result.h_optical, dx), result.fx, result.fy)

    axes[0].loglog(f_r * 1e-3, psd_t, 'k-', linewidth=1.5, label='True')
    axes[0].loglog(f_r * 1e-3, psd_s, 'b--', linewidth=1.2, label='Stylus')
    axes[0].loglog(f_r * 1e-3, psd_o, 'r-.', linewidth=1.2, label='Optical')
    axes[0].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[0].set_ylabel(r'PSD [m$^3$]')
    axes[0].set_title('(a)  Power Spectral Density', loc='left', fontsize=10.5, fontweight='bold', pad=12)
    axes[0].legend(loc='lower left', framealpha=0.85); axes[0].grid(True, alpha=0.3, which='both')

    # FIXED: auto y-scale — H(f) can exceed 1.0 due to noise amplification
    axes[1].semilogx(tf.f_radial * 1e-3, tf.H_stylus_1d, 'b-', linewidth=1.5, label='Stylus')
    axes[1].semilogx(tf.f_radial * 1e-3, tf.H_optical_1d, 'r-', linewidth=1.5, label='Optical')
    axes[1].axhline(1.0, color='gray', linestyle=':', linewidth=0.6)
    axes[1].set_xlabel(r'$f$ [mm$^{-1}$]'); axes[1].set_ylabel(r'$H(f)$')
    axes[1].set_title('(b)  Transfer Functions', loc='left', fontsize=10.5, fontweight='bold', pad=12)
    axes[1].legend(loc='upper right', framealpha=0.85)
    axes[1].grid(True, alpha=0.3, which='both')
    # Auto y-scale — do NOT clip at 1.05
    ymax = max(np.percentile(tf.H_stylus_1d, 99), np.percentile(tf.H_optical_1d, 99)) * 1.1
    axes[1].set_ylim([0, max(ymax, 1.2)])

    f_c_opt = result.params.optical_cutoff * 1e-3
    f_c_sty = result.params.stylus_cutoff * 1e-3
    for fc, lbl, clr in [(f_c_opt, 'Opt.', 'red'), (f_c_sty, 'Sty.', 'blue')]:
        if 0 < fc < f_r[-1] * 1e-3 * 0.9:
            axes[1].axvline(fc, color=clr, linestyle=':', alpha=0.6, linewidth=1)
            axes[1].text(fc * 1.05, ymax * 0.12, lbl, color=clr, fontsize=7, rotation=90)
    fig.savefig(os.path.join(output_dir, 'fig4_azimuthal_profiles.pdf'))
    plt.close(fig)
    print("  Figure 4 saved")


# ═══════════════════════════════════════════════════════════
# Figure 5 — Anisotropy Tensor (FIXED visibility)
# ═══════════════════════════════════════════════════════════
def fig_anisotropy_tensor(discovery, output_dir):
    """
    Anisotropy ellipses with STRONG visual exaggeration.
    The minor axis = 1 - 5*alpha so even tiny anisotropies are visible.
    Reference circle clearly shown as dashed line.
    """
    anisotropy = discovery.anisotropy
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), constrained_layout=True)

    def plot_tensor(ax, eigvals, eigvecs, alpha, color):
        if eigvals[0] < 1e-30:
            return
        ratio = eigvals[1] / eigvals[0]
        angle = np.degrees(np.arctan2(eigvecs[1, 0], eigvecs[0, 0]))

        # STRONG exaggeration: minor = 1 - 5*alpha (clamped)
        # So alpha=0.01 → minor=0.95 (visible), alpha=0.1 → minor=0.5 (obvious)
        a_major = 2.4
        a_minor = max(0.3, a_major * (1.0 - 5.0 * alpha))
        if a_minor >= a_major * 0.995:
            a_minor = a_major * 0.95  # ensure visible difference

        ellipse = Ellipse((0, 0), a_major, a_minor, angle=angle,
                          facecolor=color, alpha=0.30, edgecolor=color, linewidth=3.0)
        ax.add_patch(ellipse)

        # Major eigenvector arrow
        vec_maj = eigvecs[:, 0]
        ax.arrow(0, 0, vec_maj[0] * a_major * 0.55, vec_maj[1] * a_major * 0.55,
                 head_width=0.14, head_length=0.18, fc=color, ec=color,
                 alpha=0.9, linewidth=2.2, length_includes_head=True, zorder=5)

        # Reference circle (perfectly isotropic reference)
        ax.add_patch(plt.Circle((0, 0), a_major * 0.5, fill=False, color='gray',
                                 linestyle=(0, (5, 5)), linewidth=1.8, alpha=0.6, zorder=2))

        lim = a_major * 0.85
        ax.set_xlim([-lim, lim]); ax.set_ylim([-lim, lim])
        ax.set_aspect('equal')
        ax.axhline(0, color='gray', linewidth=0.4, alpha=0.25)
        ax.axvline(0, color='gray', linewidth=0.4, alpha=0.25)
        ax.set_xlabel(r'$f_x$ direction'); ax.set_ylabel(r'$f_y$ direction')

        # Annotation with physical values
        ax.text(0.97, 0.05,
                r'$\alpha_{\rm phys} = ' + f'{alpha:.4f}$' + '\n'
                r'$\lambda_2/\lambda_1 = ' + f'{ratio:.4f}$' + '\n'
                r'$\theta = ' + f'{np.degrees(np.arctan2(eigvecs[1,0], eigvecs[0,0])):.1f}' + r'^\circ$',
                transform=ax.transAxes, va='bottom', ha='right', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

    for modality, ax, color in [('stylus', axes[0], '#2166ac'),
                                 ('optical', axes[1], '#b2182b')]:
        A = np.array(anisotropy.__getattribute__(modality)["A_ij"])
        ev, evec = np.linalg.eigh(A)
        idx = np.argsort(ev)[::-1]; ev, evec = ev[idx], evec[:, idx]
        alpha_val = anisotropy.__getattribute__(modality)["anisotropy_degree"]
        plot_tensor(ax, ev, evec, alpha_val, color)

    # Single title per panel: (a)/(b) labels, no second overlapping title
    axes[0].set_title('(a)  Stylus Profilometry', loc='left', fontsize=10.5, fontweight='bold')
    axes[1].set_title('(b)  Optical Interferometry', loc='left', fontsize=10.5, fontweight='bold')
    fig.savefig(os.path.join(output_dir, 'fig5_anisotropy_tensor.pdf'))
    plt.close(fig)
    print("  Figure 5 saved")


# ═══════════════════════════════════════════════════════════
# Figure 6 — Crossover & Equivalence Regime (FIXED y-scale)
# ═══════════════════════════════════════════════════════════
def fig_crossover_analysis(discovery, output_dir):
    tf = discovery.transfer_functions; crossover = discovery.crossover_analysis
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)

    # (a) Transfer along f_x — FIXED: auto y-scale
    center = tf.H_stylus.shape[0] // 2
    f_x_mm = tf.fx * 1e-3; pos = tf.fx > 0
    axes[0].semilogx(f_x_mm[pos], tf.H_stylus_x[pos], 'b-', linewidth=1.5, label='Stylus')
    axes[0].semilogx(f_x_mm[pos], tf.H_optical_x[pos], 'r-', linewidth=1.5, label='Optical')
    axes[0].fill_between(f_x_mm[pos], tf.H_stylus_x[pos], tf.H_optical_x[pos],
                         alpha=0.15, color='purple')
    axes[0].set_xlabel(r'$f_x$ [mm$^{-1}$]'); axes[0].set_ylabel(r'$H(f_x, 0)$')
    axes[0].set_title('(a)  Transfer Along $f_x$', loc='left', fontsize=10.5, fontweight='bold')
    axes[0].legend(loc='upper right', framealpha=0.85, fontsize=8)
    axes[0].grid(True, alpha=0.3, which='both')
    # Auto y-scale to show all data
    ymax_a = max(np.percentile(tf.H_stylus_x[pos], 99), np.percentile(tf.H_optical_x[pos], 99)) * 1.1
    axes[0].set_ylim([0, max(ymax_a, 1.2)])

    # (b) 2D difference map
    H_diff_db = 10.0 * np.abs(
        np.log10(np.clip(tf.H_stylus, 1e-10, None)) -
        np.log10(np.clip(tf.H_optical, 1e-10, None)))
    f_max = np.max(tf.fx) * 1e-3 * 0.92; extent = [-f_max, f_max, -f_max, f_max]
    vmax_db = np.percentile(H_diff_db, 95)
    im = axes[1].imshow(H_diff_db, extent=extent, origin='lower',
                        cmap='RdYlGn_r', aspect='equal', vmin=0, vmax=vmax_db)
    axes[1].set_title(r'(b)  $|H_s - H_o|$ [dB]', loc='left', fontsize=10.5, fontweight='bold')
    axes[1].set_xlabel(r'$f_x$ [mm$^{-1}$]'); axes[1].set_ylabel(r'$f_y$ [mm$^{-1}$]')
    cbar = fig.colorbar(im, ax=axes[1], label='dB', fraction=0.046, pad=0.02)
    Nx, Ny = H_diff_db.shape[1], H_diff_db.shape[0]
    axes[1].contour(np.linspace(-f_max, f_max, Nx), np.linspace(-f_max, f_max, Ny),
                    H_diff_db, levels=[3.0], colors='white', linewidths=1.8)
    axes[1].text(0, -f_max * 0.78, r'$\leq 3$ dB', color='white', fontsize=8, ha='center',
                 bbox=dict(facecolor='black', alpha=0.4, boxstyle='round,pad=0.2'))

    # (c) Bar chart
    thresholds = [1, 2, 3, 6]
    fractions = [crossover["equivalence_fraction_vs_threshold"][f"{t}dB"] * 100 for t in thresholds]
    colors_bar = ['#2ca02c', '#bcbd22', '#d62728', '#7f7f7f']
    bars = axes[2].bar(thresholds, fractions, width=0.8, color=colors_bar,
                       edgecolor='white', linewidth=0.5)
    axes[2].set_xlabel('Threshold [dB]'); axes[2].set_ylabel(r'$k$-space fraction [%]')
    axes[2].set_title('(c)  Equivalence Regime Size', loc='left', fontsize=10.5, fontweight='bold')
    axes[2].set_ylim([0, max(100, max(fractions) * 1.25)])
    axes[2].set_xticks(thresholds)
    for bar, frac in zip(bars, fractions):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                     f'{frac:.1f}%', ha='center', fontsize=8.5)
    axes[2].text(0.5, 0.32,
                 f"$f_{{\\rm cross}}$={crossover['crossover_frequency_m']*1e-3:.1f} mm$^{{-1}}$\n"
                 f"$\\lambda_{{\\rm cross}}$={crossover['crossover_wavelength_m']*1e6:.1f} µm",
                 transform=axes[2].transAxes, fontsize=8, ha='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    fig.savefig(os.path.join(output_dir, 'fig6_crossover_analysis.pdf'))
    plt.close(fig)
    print("  Figure 6 saved")


# ═══════════════════════════════════════════════════════════
def generate_all_figures(result, discovery, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print("\n  Generating publication figures...")
    fig_surface_comparison(result, output_dir)
    fig_transfer_functions(discovery, result, output_dir)
    fig_information_loss(discovery, output_dir)
    fig_azimuthal_profiles(discovery, result, output_dir)
    fig_anisotropy_tensor(discovery, output_dir)
    fig_crossover_analysis(discovery, output_dir)
    print(f"  All figures saved to: {output_dir}")


if __name__ == "__main__":
    print("Visualisation module. Use via pipeline_main.py")
