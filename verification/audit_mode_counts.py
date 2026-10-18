#!/usr/bin/env python3
"""Reproducible mode-count audit (replaces untraceable 254,542/97,301).

Definition (block8 convention, committed data):
  resolved mode = DFT bin with per-mode SNR > 1,
  SNR(f) = |H(f)|^2 S_true(f) / S_noise,
  H = PSD-ratio (power), S_noise = median of the positive bins of the
  difference-field periodogram.

Inputs: pipeline/outputs/iter01/{h_true,h_stylus,h_optical}.npy
Writes: reports/mode_counts_audit.json
"""
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, 'pipeline')
REP = os.path.join(ROOT, 'reports')
os.makedirs(REP, exist_ok=True)

ht = np.load(os.path.join(PIPE, 'outputs', 'iter01', 'h_true.npy'))
hs = np.load(os.path.join(PIPE, 'outputs', 'iter01', 'h_stylus.npy'))
ho = np.load(os.path.join(PIPE, 'outputs', 'iter01', 'h_optical.npy'))
N = ht.shape[0]
dx = 100e-6 / N


def psd(h):
    w = np.hanning(N)[:, None] * np.hanning(N)[None, :]
    return np.abs(np.fft.fft2(h * w)) ** 2 * dx ** 2 / np.sum(w ** 2)


Pt = psd(ht)
H_s = np.clip(psd(hs) / np.maximum(Pt, 1e-35), 0, None)
H_o = np.clip(psd(ho) / np.maximum(Pt, 1e-35), 0, None)
n_s = np.median(psd(hs - ht)[psd(hs - ht) > 0])
n_o = np.median(psd(ho - ht)[psd(ho - ht) > 0])

counts = {}
for name, Hf, nf in [('stylus', H_s, n_s), ('optical', H_o, n_o)]:
    snr = Hf * Pt / nf
    counts[name] = {
        'n_modes_SNR_gt_1': int((snr > 1.0).sum()),
        'n_modes_SNR_gt_0p5': int((snr > 0.5).sum()),
        'noise_floor': float(nf),
    }

out = {
    'method': 'count of DFT bins with per-mode SNR > threshold; '
              'SNR = H(power) * S_true / noise_floor; noise floor = median of '
              'positive bins of difference-field periodogram (block8 convention); '
              'N=512, seed 42 baseline arrays.',
    'stylus': counts['stylus'],
    'optical': counts['optical'],
    'total_bins': N * N,
    'caveat': 'mode counts are grid- and noise-estimator-dependent; quoted for '
              'illustration of mode coverage only, not as an absolute capacity.',
}
with open(os.path.join(REP, 'mode_counts_audit.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
