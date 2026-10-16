#!/usr/bin/env python3
"""Independent verification: empirical stylus transfer function of the geometric
dilation simulator vs the manuscript's analytic Gaussian model (eq:hstylus).

Run from pipeline/ so imports resolve.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from numpy.fft import fft2, ifft2, fftfreq
from block4_physics_simulator import SimulationParams, generate_self_affine_surface, simulate_stylus, simulate_optical

np.random.seed(42)
params = SimulationParams(grid_size=512, physical_size=100e-6,
                          hurst_exponent=0.7, rms_roughness=50e-9,
                          correlation_length=5e-6, roll_off_wavelength=10e-6,
                          tip_radius=2e-6, sampling_interval=200e-9,
                          cone_angle=45.0, wavelength=550e-9, na=0.55,
                          magnification=50.0, camera_noise_std=1e-3,
                          unwrapping_error_prob=0.01)
h_true = generate_self_affine_surface(params, seed=42)
h_stylus, meta_s = simulate_stylus(h_true, params)
h_optical, meta_o = simulate_optical(h_true, params)
print('fresh sim: RMSE_s = %.2f nm, RMSE_o = %.2f nm' % (meta_s['rmse']*1e9, meta_o['rmse']*1e9))

def psd2d(h, dx):
    w = np.hanning(h.shape[0])[:, None] * np.hanning(h.shape[1])[None, :]
    P = np.abs(fft2(h * w))**2 * dx**2 / (np.sum(w**2))
    return np.fft.fftshift(P)

dx = params.dx
Pt = psd2d(h_true, dx); Ps = psd2d(h_stylus, dx); Po = psd2d(h_optical, dx)
fx = np.fft.fftshift(fftfreq(512, d=dx)); fy = np.fft.fftshift(fftfreq(512, d=dx))
FX, FY = np.meshgrid(fx, fy); fr = np.sqrt(FX**2 + FY**2)

# Azimuthal average helper
def azavg(P, nbin=100):
    fmax = np.max(fr) * 0.95
    edges = np.linspace(0, fmax, nbin + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    out = np.zeros(nbin)
    for i in range(nbin):
        m = (fr >= edges[i]) & (fr < edges[i + 1])
        out[i] = np.mean(P[m]) if m.sum() else np.nan
    return centers, out

fc, Pt1 = azavg(Pt); _, Ps1 = azavg(Ps); _, Po1 = azavg(Po)
Hs = Ps1 / np.maximum(Pt1, 1e-30); Ho = Po1 / np.maximum(Pt1, 1e-30)

r = 2e-6
print('\nf [mm-1]  H_stylus   H_optical  gauss_full  gauss_half')
for k in range(0, 100, 8):
    if fc[k] > 900e3: break
    g1 = np.exp(-2*np.pi**2*r**2*fc[k]**2)
    g2 = np.exp(-np.pi**2*r**2*fc[k]**2)
    print('%8.0f  %9.4f  %9.4f  %10.4f  %10.4f' % (fc[k]/1e3, Hs[k], Ho[k], g1, g2))

i50 = np.where(Hs <= 0.5)[0]
print('\nempirical H_stylus crosses 0.5 at f = %s mm^-1' % ('>%.0f' % (fc[-1]/1e3) if len(i50)==0 else '%.0f' % (fc[i50[0]]/1e3)))
