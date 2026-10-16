"""
Block 4 — Physics + Signal Simulator
=====================================
Simulates both stylus and optical profilometry measurements of
rough surfaces, including realistic instrument physics.

STYLUS simulation:
  - Morphological convolution (tip dilation)
  - Raster sampling (discrete grid)
  - Geometric distortion (tip shape effects)

OPTICAL simulation:
  - Fourier optics cutoff (diffraction limit)
  - Phase reconstruction (interferometric)
  - Noise + unwrapping errors

Input:  Simulation parameters from config
Output: True surface + both measured surfaces + metadata
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftfreq, fftshift
from scipy.ndimage import grey_dilation, uniform_filter
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Tuple
import os
import json
import traceback


@dataclass
class SimulationParams:
    """Parameters for the physics simulation."""
    grid_size: int = 512
    physical_size: float = 100e-6  # 100 µm

    # Surface parameters
    hurst_exponent: float = 0.7
    rms_roughness: float = 50e-9     # 50 nm
    correlation_length: float = 5e-6  # 5 µm
    roll_off_wavelength: float = 10e-6  # 10 µm

    # Stylus parameters
    tip_radius: float = 2.0e-6       # 2 µm
    sampling_interval: float = 0.2e-6  # 200 nm
    cone_angle: float = 45.0          # degrees

    # Optical parameters
    wavelength: float = 550e-9        # 550 nm
    na: float = 0.55
    magnification: float = 50.0
    camera_noise_std: float = 0.001   # relative
    unwrapping_error_prob: float = 0.01

    @property
    def dx(self) -> float:
        return self.physical_size / self.grid_size

    @property
    def df(self) -> float:
        return 1.0 / self.physical_size

    @property
    def optical_cutoff(self) -> float:
        """Spatial frequency cutoff from diffraction limit (1/m)."""
        return self.na / self.wavelength

    @property
    def stylus_cutoff(self) -> float:
        """Approximate spatial frequency cutoff from tip radius."""
        return 1.0 / (np.pi * self.tip_radius)


@dataclass
class SimulationResult:
    """Complete simulation output."""
    params: SimulationParams

    # Surfaces (2D arrays in meters)
    h_true: np.ndarray = field(default=None, repr=False)
    h_stylus: np.ndarray = field(default=None, repr=False)
    h_optical: np.ndarray = field(default=None, repr=False)

    # Coordinates
    x: np.ndarray = field(default=None, repr=False)
    y: np.ndarray = field(default=None, repr=False)
    fx: np.ndarray = field(default=None, repr=False)
    fy: np.ndarray = field(default=None, repr=False)

    # Metadata
    rmse_stylus: float = 0.0
    rmse_optical: float = 0.0
    correlation_stylus: float = 0.0
    correlation_optical: float = 0.0


# ============================================================
# Surface Generation
# ============================================================

def generate_self_affine_surface(params: SimulationParams, seed: int = 42) -> np.ndarray:
    """
    Generate a self-affine rough surface using the Fourier filtering method.

    PSD(f) ∝ 1 / (f₀² + f²)^(H + 1)  for f < f_rolloff
    PSD(f) ∝ 1 / f^(2H + 2)          for f > f_rolloff

    where f_rolloff = 1/λ_rolloff, H = Hurst exponent.
    """
    rng = np.random.RandomState(seed)
    N = params.grid_size
    L = params.physical_size

    # Frequency grids (centered)
    fx = fftfreq(N, d=L/N)
    fy = fftfreq(N, d=L/N)
    FX, FY = np.meshgrid(fx, fy)
    f_mag = np.sqrt(FX**2 + FY**2)
    f_mag[0, 0] = fx[1] * 1e-3  # Avoid division by zero at DC

    # Roll-off frequency
    f_rolloff = 1.0 / params.roll_off_wavelength
    H = params.hurst_exponent

    # PSD: self-affine with roll-off
    psd = np.power(f_mag**2 + f_rolloff**2, -(H + 1.0))

    # Normalise to desired RMS roughness
    h_fourier = np.zeros((N, N), dtype=complex)
    # Random phases with PSD-derived amplitude
    noise = rng.randn(N, N) + 1j * rng.randn(N, N)
    h_fourier = noise * np.sqrt(psd / 2.0)
    h_fourier[0, 0] = 0  # Zero mean

    # Transform to real space
    h = np.real(ifft2(h_fourier))

    # Normalise to target RMS
    h_rms = np.std(h)
    h = h * (params.rms_roughness / h_rms)

    return h


# ============================================================
# Stylus Simulation
# ============================================================

def simulate_stylus(h_true: np.ndarray, params: SimulationParams) -> Tuple[np.ndarray, Dict]:
    """
    Simulate stylus profilometry measurement with physically correct ordering.

    Physical model:
    1. The stylus tip acts as a morphological dilation — the measured height
       at (x,y) is the maximum of [h_true(x+u, y+v) - tip_shape(u,v)] over
       the tip contact region. Equivalently: the tip envelope.
    2. Raster scanning: discrete sampling along x-direction scan lines with
       spacing Δy between lines and sampling interval Δx along each line.
    3. Small additive measurement noise.

    The transfer function emerges naturally — it is NOT imposed as a Gaussian
    filter. For a paraboloid tip with radius r_tip, the morphological filter
    has an effective k-space width ∝ 1/√(r_tip · κ_rms) where κ_rms is the
    RMS surface curvature.
    """
    N = params.grid_size
    L = params.physical_size
    dx = params.dx

    # ---- Step 1: Morphological dilation with paraboloid tip ----
    # The measured surface is the morphological dilation of h_true by the tip.
    # For a paraboloid tip: t(u,v) = (u²+v²)/(2·r_tip) within the contact circle.
    # The dilation: h_dilated(x,y) = max_{u,v}[h_true(x-u, y-v) - t(u,v)]
    # This is equivalent to: the tip centre height when the tip touches the surface.

    # Tip contact radius (limited by cone angle)
    contact_radius = params.tip_radius * np.tan(np.radians(params.cone_angle / 2.0))
    tip_px_radius = max(2, int(contact_radius / dx))
    se_size = 2 * tip_px_radius + 1

    # Build structuring element: paraboloid tip shape
    y_se, x_se = np.ogrid[-tip_px_radius:tip_px_radius+1, -tip_px_radius:tip_px_radius+1]
    r2 = (x_se * dx)**2 + (y_se * dx)**2
    # Tip height above contact point: t(r) = r²/(2·r_tip)
    tip_height = r2 / (2.0 * params.tip_radius)
    # Truncate beyond contact radius (cone angle limit)
    tip_height[r2 > contact_radius**2] = 1e6  # effectively infinite → no contact

    # Morphological dilation: for each pixel, the measured height is the
    # maximum of (h_true - tip_height) within the tip footprint.
    # grey_dilation computes: max_{footprint}[input + structure]
    # We want: max[h_true(x+u, y+v) - tip(u,v)] = max[h_true + (-tip)]
    # So structure = -tip_height
    try:
        footprint = np.ones((se_size, se_size), dtype=bool)
        h_dilated = grey_dilation(h_true, footprint=footprint,
                                  structure=(-tip_height).astype(np.float64))
    except Exception as e:
        # Fallback: use a simpler sliding-window maximum with tip correction
        print(f"    [WARN] grey_dilation failed ({e}), using Gaussian approximation")
        sigma_tip = params.tip_radius / np.sqrt(2.0)
        fx = fftfreq(N, d=dx)
        fy = fftfreq(N, d=dx)
        FX, FY = np.meshgrid(fx, fy)
        H_tip = np.exp(-2.0 * np.pi**2 * sigma_tip**2 * (FX**2 + FY**2))
        h_dilated = np.real(ifft2(fft2(h_true) * H_tip))

    # ---- Step 2: Raster sampling ----
    # Stylus scans along x at sampling interval Δx, with line spacing Δy
    # between scan lines (typically Δy ≈ Δx for areal measurement)
    sampling_interval = params.sampling_interval
    n_samples_x = max(2, int(L / sampling_interval))
    n_samples_y = max(2, int(L / sampling_interval))  # same sampling in y

    # Sample indices
    ix_samples = np.linspace(0, N-1, min(N, n_samples_x), dtype=int)
    iy_samples = np.linspace(0, N-1, min(N, n_samples_y), dtype=int)

    # Interpolate from dilated surface onto sampling grid
    # Use bilinear-like interpolation: for each output pixel, find nearest
    # sampled point and interpolate
    h_sampled = np.zeros_like(h_dilated)
    for iy_out in range(N):
        # Find bracketing scan lines
        iy_frac = iy_out * (len(iy_samples) - 1) / (N - 1) if N > 1 else 0
        iy_lo = int(np.floor(iy_frac))
        iy_hi = min(iy_lo + 1, len(iy_samples) - 1)
        wy = iy_frac - iy_lo

        row_lo = h_dilated[iy_samples[iy_lo], :]
        row_hi = h_dilated[iy_samples[iy_hi], :]

        # Interpolate between scan lines
        row_interp = (1 - wy) * row_lo + wy * row_hi

        # Sample along x within this row
        for ix_out in range(N):
            ix_frac = ix_out * (len(ix_samples) - 1) / (N - 1) if N > 1 else 0
            ix_lo = int(np.floor(ix_frac))
            ix_hi = min(ix_lo + 1, len(ix_samples) - 1)
            wx = ix_frac - ix_lo

            h_sampled[iy_out, ix_out] = (
                (1 - wx) * row_interp[ix_samples[ix_lo]] +
                wx * row_interp[ix_samples[ix_hi]]
            )

    # ---- Step 3: Small additive measurement noise ----
    noise_std = params.rms_roughness * 0.001  # 0.1% of roughness
    noise = np.random.randn(N, N) * noise_std
    h_stylus = h_sampled + noise

    # Compute metrics
    rmse = np.sqrt(np.mean((h_stylus - h_true)**2))
    corr = np.corrcoef(h_true.ravel(), h_stylus.ravel())[0, 1]

    meta = {
        "rmse": rmse,
        "correlation": corr,
        "tip_radius": params.tip_radius,
        "sampling_interval": params.sampling_interval,
        "contact_radius": contact_radius,
        "effective_cutoff_spatial": params.stylus_cutoff
    }

    return h_stylus, meta


# ============================================================
# Optical Simulation
# ============================================================

def simulate_optical(h_true: np.ndarray, params: SimulationParams) -> Tuple[np.ndarray, Dict]:
    """
    Simulate optical (white-light interferometry / phase-shifting) measurement.

    Steps:
    1. Fourier optics: circular aperture cutoff
    2. Phase measurement with wrapped phase
    3. Phase unwrapping with error probability
    4. Camera noise
    """
    N = params.grid_size
    L = params.physical_size
    dx = params.dx

    # ---- Step 1: Optical transfer function ----
    # Circular aperture: H(f) = 1 for |f| < NA/λ, 0 otherwise (ideal)
    # Real systems: gradual roll-off + aberrations
    fx = fftfreq(N, d=dx)
    fy = fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fy)
    f_radial = np.sqrt(FX**2 + FY**2)

    f_cutoff = params.optical_cutoff

    # Diffraction-limited OTF with smooth transition
    # Using the ideal incoherent OTF for a circular pupil
    f_norm = f_radial / (2.0 * f_cutoff)  # Normalise to 2× cutoff for incoherent
    f_norm = np.clip(f_norm, 0, 1)

    # Incoherent OTF of a circular aperture:
    # H(f) = 2/π [arccos(f_norm) - f_norm √(1 - f_norm²)]
    H_opt = np.where(
        f_norm < 1.0,
        (2.0 / np.pi) * (np.arccos(f_norm) - f_norm * np.sqrt(1.0 - f_norm**2)),
        0.0
    )
    # Normalise to 1 at DC
    H_opt = H_opt / np.max(H_opt)

    # ---- Step 2: Phase reconstruction ----
    # In interferometry, h(x,y) is encoded in phase: φ(x,y) = (4π/λ) · h(x,y)
    # The measured phase is wrapped modulo 2π
    wavelength_eq = params.wavelength / 2.0  # Equivalent wavelength for double-pass

    H_f = fft2(h_true)
    H_f_filtered = H_f * H_opt
    h_filtered = np.real(ifft2(H_f_filtered))

    # Phase wrapping
    phase = (4.0 * np.pi / params.wavelength) * h_filtered
    phase_wrapped = np.mod(phase + np.pi, 2.0 * np.pi) - np.pi

    # ---- Step 3: Phase unwrapping with errors ----
    # Simulate 1D unwrapping along rows (simplified)
    h_unwrapped = np.zeros_like(h_filtered)
    for iy in range(N):
        row = phase_wrapped[iy, :]
        unwrapped = np.unwrap(row)
        h_unwrapped[iy, :] = unwrapped * params.wavelength / (4.0 * np.pi)

    # Add unwrapping errors: random 2π jumps
    rng = np.random.RandomState(123)
    error_mask = rng.rand(N, N) < params.unwrapping_error_prob
    # Each error adds ±2π phase error = ±λ/2 height error
    error_heights = (rng.randint(0, 2, (N, N)) * 2 - 1) * params.wavelength / 2.0
    h_unwrapped += error_mask * error_heights

    # ---- Step 4: Camera noise ----
    noise = np.random.randn(N, N) * params.camera_noise_std * params.rms_roughness
    h_optical = h_unwrapped + noise

    # ---- Step 5: Detector pixel averaging (MTF of camera) ----
    # Apply slight low-pass to simulate detector pixel integration
    pixel_size = L / N / params.magnification
    sigma_pixel = pixel_size / np.sqrt(12)  # Uniform pixel MTF approx
    sigma_freq = 1.0 / (2.0 * np.pi * sigma_pixel)
    if sigma_freq < 10 * f_cutoff:  # Only if pixel effects matter
        H_pixel = np.exp(-2.0 * np.pi**2 * sigma_pixel**2 * (FX**2 + FY**2))
        H_f2 = fft2(h_optical)
        H_f2 *= H_pixel
        h_optical = np.real(ifft2(H_f2))

    # Compute metrics
    rmse = np.sqrt(np.mean((h_optical - h_true)**2))
    corr = np.corrcoef(h_true.ravel(), h_optical.ravel())[0, 1]

    meta = {
        "rmse": rmse,
        "correlation": corr,
        "wavelength": params.wavelength,
        "na": params.na,
        "optical_cutoff_spatial": f_cutoff,
        "unwrapping_error_prob": params.unwrapping_error_prob
    }

    return h_optical, meta


# ============================================================
# Full Simulation Runner
# ============================================================

def run_simulation(params: SimulationParams, seed: int = 42) -> SimulationResult:
    """Run complete simulation: surface generation + both measurement modalities."""
    print("\n" + "─"*70)
    print("  BLOCK 4 — PHYSICS + SIGNAL SIMULATOR")
    print("─"*70)

    # Generate true surface
    print(f"  Generating self-affine surface (H={params.hurst_exponent}, "
          f"σ={params.rms_roughness*1e9:.1f} nm)...")
    h_true = generate_self_affine_surface(params, seed=seed)

    # Simulate stylus measurement
    print(f"  Simulating stylus (r_tip={params.tip_radius*1e6:.1f} µm, "
          f"Δx={params.sampling_interval*1e6:.1f} µm)...")
    h_stylus, meta_s = simulate_stylus(h_true, params)

    # Simulate optical measurement
    print(f"  Simulating optical (λ={params.wavelength*1e9:.0f} nm, "
          f"NA={params.na})...")
    h_optical, meta_o = simulate_optical(h_true, params)

    # Build coordinate arrays
    L = params.physical_size
    N = params.grid_size
    x = np.linspace(-L/2, L/2, N)
    y = np.linspace(-L/2, L/2, N)
    fx = fftshift(fftfreq(N, d=L/N))
    fy = fftshift(fftfreq(N, d=L/N))

    result = SimulationResult(
        params=params,
        h_true=h_true,
        h_stylus=h_stylus,
        h_optical=h_optical,
        x=x, y=y, fx=fx, fy=fy,
        rmse_stylus=meta_s["rmse"],
        rmse_optical=meta_o["rmse"],
        correlation_stylus=meta_s["correlation"],
        correlation_optical=meta_o["correlation"]
    )

    print(f"\n  Results:")
    print(f"    Stylus:  RMSE = {meta_s['rmse']*1e9:.2f} nm, "
          f"r = {meta_s['correlation']:.4f}")
    print(f"    Optical: RMSE = {meta_o['rmse']*1e9:.2f} nm, "
          f"r = {meta_o['correlation']:.4f}")
    print(f"    RMSE ratio (optical/stylus): {meta_o['rmse']/meta_s['rmse']:.3f}")

    return result


def save_simulation(result: SimulationResult, output_dir: str):
    """Save simulation results to disk."""
    os.makedirs(output_dir, exist_ok=True)

    # Save surfaces as .npy
    np.save(os.path.join(output_dir, "h_true.npy"), result.h_true)
    np.save(os.path.join(output_dir, "h_stylus.npy"), result.h_stylus)
    np.save(os.path.join(output_dir, "h_optical.npy"), result.h_optical)
    np.save(os.path.join(output_dir, "fx.npy"), result.fx)
    np.save(os.path.join(output_dir, "fy.npy"), result.fy)

    # Save metadata
    meta = {
        "params": asdict(result.params),
        "rmse_stylus": float(result.rmse_stylus),
        "rmse_optical": float(result.rmse_optical),
        "correlation_stylus": float(result.correlation_stylus),
        "correlation_optical": float(result.correlation_optical),
        "optical_cutoff_m": result.params.optical_cutoff,
        "stylus_cutoff_m": result.params.stylus_cutoff
    }
    with open(os.path.join(output_dir, "simulation_meta.json"), 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"  Simulation saved to: {output_dir}")


# ============================================================
# Main
# ============================================================
def run_block4(params: SimulationParams, output_dir: str) -> SimulationResult:
    """Run Block 4: Physics + Signal Simulation."""
    result = run_simulation(params)
    save_simulation(result, output_dir)
    return result


if __name__ == "__main__":
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./outputs/sim"
    params = SimulationParams()
    run_block4(params, output_dir)
