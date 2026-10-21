#!/usr/bin/env python3
"""Regenerate fig9 (three-way transfer) from saved arrays.

Reconstructs the three_way data object expected by block10's plotting
function from the committed .npy outputs (no pipeline re-run), and writes
the corrected frequency-coverage panel (stylus 3 dB point 1049 mm^-1,
WLI diffraction cutoff 2000 mm^-1, scatterometry usable range).
"""
import json
import os
import sys
import types

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ITER = os.path.join(ROOT, 'pipeline', 'outputs', 'iter01')
OUT = os.path.join(ITER, 'figures')

sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import block10_scatterometry as b10  # noqa: E402
from block5_discovery_engine import (  # noqa: E402
    azimuthal_average, compute_psd_2d)

fx = np.load(os.path.join(ITER, 'fx.npy'))
fy = np.load(os.path.join(ITER, 'fy.npy'))
meta = json.load(open(os.path.join(ITER, 'simulation_meta.json')))
dx = float(meta['dx']) if 'dx' in meta else 195e-9

h_true = np.load(os.path.join(ITER, 'h_true.npy'))
h_stylus = np.load(os.path.join(ITER, 'h_stylus.npy'))
h_optical = np.load(os.path.join(ITER, 'h_optical.npy'))
H_stylus_2d = np.load(os.path.join(ITER, 'H_stylus_2d.npy'))
H_optical_2d = np.load(os.path.join(ITER, 'H_optical_2d.npy'))
H_scat_2d = np.load(os.path.join(ITER, 'scatterometry',
                                 'H_scatterometry_2d.npy'))
psd_scat = np.load(os.path.join(ITER, 'scatterometry',
                                'psd_scatterometry.npy'))
scat_meta = json.load(open(os.path.join(ITER, 'scatterometry',
                                        'scatterometry_meta.json')))

three_way = types.SimpleNamespace()
three_way.params = types.SimpleNamespace(dx=dx)
three_way.scat_meta = scat_meta

three_way.psd_stylus = compute_psd_2d(h_stylus, dx)
three_way.psd_optical = compute_psd_2d(h_optical, dx)
three_way.psd_scatterometry = psd_scat
three_way.f_radial, three_way.psd_true_1d = azimuthal_average(
    compute_psd_2d(h_true, dx), fx, fy)
_, three_way.H_stylus_1d = azimuthal_average(H_stylus_2d, fx, fy)
_, three_way.H_optical_1d = azimuthal_average(H_optical_2d, fx, fy)
_, three_way.H_scat_1d = azimuthal_average(H_scat_2d, fx, fy)

b10.fig_three_way_transfer(three_way, OUT)
print('Figure 9 regenerated with corrected coverage bars')
