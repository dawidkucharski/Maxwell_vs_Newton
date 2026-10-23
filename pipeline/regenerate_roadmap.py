#!/usr/bin/env python3
"""Regenerate fig_roadmap.pdf with improved spacing between panels (a) and (b).

Data: gap_closure_sweep.json (432-point sweep across NA × noise_mult × wavelength)
Layout: 3-panel figure with (a) equivalence fraction vs NA, (b) max tolerable
noise multiplier, (c) prescriptive summary text.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import ScalarFormatter
import os

# ── Load data ───────────────────────────────────────────────────────────────
data_path = os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'outputs',
                         'iter01', 'gap_closure', 'gap_closure_sweep.json')
with open(data_path) as f:
    sweep = json.load(f)

results = sweep['results']
baseline_noise = sweep.get('baseline_noise')

# Group by noise_mult
from collections import defaultdict
by_noise = defaultdict(list)
for r in results:
    by_noise[r['noise_mult']].append(r)

# Sort each group by NA
for nm in by_noise:
    by_noise[nm].sort(key=lambda x: x['NA'])

noise_mults = sorted(by_noise.keys())

# ── Colours and styling ─────────────────────────────────────────────────────
# Colour map for noise multipliers
cmap = plt.cm.viridis
noise_colors = {nm: cmap(i / (len(noise_mults) - 1)) for i, nm in enumerate(noise_mults)}

# Light green for "achievable", light orange for "challenging"
green_zone = '#d5f5e3'
orange_zone = '#fdebd0'
red_baseline = '#e74c3c'

# ── Create figure ───────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 5.5))
gs = GridSpec(1, 3, figure=fig, width_ratios=[0.9, 0.65, 1.3], wspace=0.38)

ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[0, 2])

# ═════════════════════════════════════════════════════════════════════════════
# PANEL (a): Equivalence fraction vs NA
# ═════════════════════════════════════════════════════════════════════════════
# Use wavelength=550 nm for the "standard" curves
wavelength_nm_target = 550.0

for nm in noise_mults:
    # Filter to λ = 550 nm
    subset = [r for r in by_noise[nm] if abs(r['wavelength_nm'] - wavelength_nm_target) < 1.0]
    subset.sort(key=lambda x: x['NA'])
    nas = [r['NA'] for r in subset]
    eqs = [r['eq_fraction'] * 100 for r in subset]
    
    label = f'{nm:.2f}×' if nm < 1 else f'{nm:.0f}×'
    if nm == 1.0:
        label = '1× (baseline)'
    
    lw = 2.0 if nm == 1.0 else 1.2
    alpha = 1.0 if nm == 1.0 else 0.7
    ax_a.plot(nas, eqs, 'o-', color=noise_colors[nm], lw=lw, ms=4,
              alpha=alpha, label=label)

# Baseline horizontal line at 9.6% (n=30 ensemble, N=512)
ax_a.axhline(9.6, color=red_baseline, ls='--', lw=1.5, alpha=0.7,
             label='Baseline (9.6%, n=30)')
ax_a.axhline(50.0, color='grey', ls=':', lw=1.2, alpha=0.7,
             label='50% equivalence')

ax_a.set_xlabel('Numerical aperture, NA', fontsize=11)
ax_a.set_ylabel('Equivalence fraction (%)', fontsize=11)
ax_a.set_title('(a) Equivalence fraction vs. NA (λ = 550 nm)', fontsize=12, fontweight='bold')
ax_a.legend(fontsize=6.5, loc='upper left', ncol=2, framealpha=0.75,
           bbox_to_anchor=(-0.02, 1.02))
ax_a.set_xlim(0.28, 0.92)
ax_a.set_ylim(0, 105)
ax_a.grid(True, alpha=0.3)
ax_a.set_xticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

# ═════════════════════════════════════════════════════════════════════════════
# PANEL (b): Max tolerable noise multiplier for 50/70/90% equivalence
# ═════════════════════════════════════════════════════════════════════════════
targets = [50, 60, 70]
all_nas = sorted(set(r['NA'] for r in results))

# The noise response of the 3 dB equivalence fraction is non-monotone: it peaks
# at ~0.1x of the baseline floor and falls again at very low noise because the
# criterion also counts bins where both measured PSDs lie below the noise floor
# as equivalent. Panel (b) therefore reports the full TOLERABLE WINDOW per
# target: the ceiling (largest qualifying multiplier, solid) and the floor
# (smallest qualifying multiplier, dashed), both at lambda = 550 nm.
target_colors = {50: '#1f77b4', 60: '#ff7f0e', 70: '#2ca02c'}

for target in targets:
    ceil_by_na, floor_by_na = [], []
    for na in all_nas:
        quals = sorted(r['noise_mult'] for r in results
                       if abs(r['NA'] - na) < 0.001
                       and abs(r['wavelength_nm'] - wavelength_nm_target) < 1.0
                       and r['eq_fraction'] * 100 > target)
        if quals:
            floor_by_na.append((na, quals[0]))
            ceil_by_na.append((na, quals[-1]))
    if ceil_by_na:
        nas_p, nms_p = zip(*ceil_by_na)
        ax_b.plot(nas_p, nms_p, 's-', lw=2.0, ms=5,
                  color=target_colors[target],
                  label=f'{target}% ceiling')
        if len(floor_by_na) > 1:
            nas_f, nms_f = zip(*floor_by_na)
            ax_b.plot(nas_f, nms_f, 'o--', lw=1.4, ms=4,
                      color=target_colors[target], alpha=0.8,
                      label=f'{target}% floor')

# Zone shading (in data coordinates, log scale)
# Lower noise_mult = less noise = better = "achievable"
# noise_mult=1.0 = baseline
ax_b.axhspan(0.005, 0.1, alpha=0.12, color='green', zorder=0)
ax_b.axhspan(0.1, 1.0, alpha=0.10, color='orange', zorder=0)
ax_b.axhspan(1.0, 20.0, alpha=0.10, color='red', zorder=0)

# Zone labels placed inside the plot area at fixed x position
# Use clip_on=False so text isn't cropped at axis edges
ax_b.text(0.50, 0.025, 'Achievable\n(cooled sCMOS\n+ brighter source)',
          transform=ax_b.transAxes, fontsize=7.5, ha='center', va='bottom',
          color='#27ae60', fontstyle='italic', clip_on=False)
ax_b.text(0.50, 0.18, 'Challenging\n(long integration)',
          transform=ax_b.transAxes, fontsize=7.5, ha='center', va='center',
          color='#e67e22', fontstyle='italic', clip_on=False)
ax_b.text(0.50, 0.50, 'Current\nbaseline',
          transform=ax_b.transAxes, fontsize=7.5, ha='center', va='center',
          color=red_baseline, fontstyle='italic', clip_on=False)

ax_b.set_xlabel('Numerical aperture, NA', fontsize=11)
ax_b.set_ylabel('Tolerable noise multiplier', fontsize=11)
ax_b.set_title('(b) Noise budget for equivalence targets ($\lambda$ = 550 nm)', fontsize=12, fontweight='bold')
ax_b.legend(fontsize=8, loc='upper left', framealpha=0.75,
           bbox_to_anchor=(-0.02, 1.02))
ax_b.set_xlim(0.28, 0.92)
ax_b.set_ylim(0.005, 20)
ax_b.set_yscale('log')
ax_b.grid(True, alpha=0.3)
ax_b.set_xticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

# ═════════════════════════════════════════════════════════════════════════════
# PANEL (c): Prescriptive summary
# ═════════════════════════════════════════════════════════════════════════════
ax_c.axis('off')

summary_text = (
    r"$\bf{(c)\;Four\;improvements\;to\;close\;the\;gap}$" "\n"
    "\n"
    r"$\bf{1.}$ Reduce optical noise floor ($\bf{10\times}$ sweep optimum)" "\n"
    r"    Cooled sCMOS, brighter LED/laser, multi-frame" "\n"
    r"    averaging ($\sqrt{N}$ gain)" "\n"
    r"    $\rightarrow$ Single most impactful change" "\n"
    "\n"
    r"$\bf{2.}$ Increase NA to $\bf{0.7{-}0.9}$" "\n"
    r"    High-NA Mirau objectives (NA 0.8)" "\n"
    r"    $\rightarrow f_c$ from 2000 to 2909 mm$^{-1}$ (2NA/$\lambda$)" "\n"
    "\n"
    r"$\bf{3.}$ Shorter $\bf{\lambda = 400{-}450}$ nm" "\n"
    r"    Blue LED / diode laser" "\n"
    r"    $\rightarrow f_c$ reaches 4000 mm$^{-1}$ (NA 0.8, $\lambda$=400 nm)" "\n"
    "\n"
    r"$\bf{4.}$ 2D phase unwrapping" "\n"
    r"    Quality-guided or temporal PSI" "\n"
    r"    $\rightarrow$ 1% $\rightarrow$ 0.1% error rate" "\n"
    "\n"
    r"$\bf{9.6\% \rightarrow 82.8\%}$ equivalence (sweep)"
    r"  --  $\bf{17\%}$ residual: bias-limited"
)

ax_c.text(0.0, 1.0, summary_text, transform=ax_c.transAxes,
          fontsize=10, va='top', ha='left',
          linespacing=1.5,
          bbox=dict(boxstyle='round,pad=0.6', facecolor='lightyellow',
                    edgecolor='#ccccaa', alpha=0.5))

# ── Save ────────────────────────────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'outputs',
                          'iter01', 'figures')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'fig_roadmap.pdf')
fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f'Saved: {output_path}')
plt.close()
