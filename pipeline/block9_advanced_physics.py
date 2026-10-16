"""
Block 9 — Advanced Physics Layer
=================================
Extends the simulation framework with complete physical effects
for both tactile (stylus) and optical surface texture measurements.

Physical effects added:
  1. Hertzian elastic contact mechanics (stylus)
  2. Coherence envelope for white-light interferometry
  3. Vector diffraction theory for high-NA systems
  4. Material property effects (Young's modulus, hardness, refractive index)
  5. Physical uncertainty propagation
  6. Scale-dependent physics crossover

Input:  SimulationResult + DiscoveryResult
Output: Advanced physics metrics + physical interpretation
"""

import numpy as np
from numpy.fft import fft2, ifft2, fftfreq, fftshift
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import json, os

from block4_physics_simulator import SimulationParams, SimulationResult
from block5_discovery_engine import TransferFunctions


# ============================================================
# 1. HERTZIAN CONTACT MECHANICS
# ============================================================

@dataclass
class ContactMechanicsParams:
    """Physical parameters for tip-surface contact."""
    tip_youngs_modulus: float = 1140e9    # Diamond: 1140 GPa
    tip_poisson_ratio: float = 0.07       # Diamond
    surface_youngs_modulus: float = 200e9  # Steel: ~200 GPa
    surface_poisson_ratio: float = 0.30    # Steel
    surface_hardness: float = 5e9          # Steel: ~5 GPa
    normal_load: float = 1e-3             # 1 mN typical stylus load
    adhesion_energy: float = 0.05          # J/m² (van der Waals)


def compute_hertz_contact(params: SimulationParams,
                          contact: ContactMechanicsParams) -> Dict:
    """
    Compute Hertzian elastic contact parameters for stylus measurements.

    The contact between a spherical diamond tip and a flat surface produces
    a circular contact area with radius a:

        a³ = (3/4) · R_eff · F_n / E_eff

    where:
        R_eff = r_tip (assuming flat surface)
        1/E_eff = (1-ν_tip²)/E_tip + (1-ν_surf²)/E_surf

    The mean contact pressure: p_mean = F_n / (π a²)
    The maximum contact pressure: p_max = (3/2) p_mean

    If p_max > H_surface (hardness), plastic deformation occurs.
    """
    E_tip = contact.tip_youngs_modulus
    nu_tip = contact.tip_poisson_ratio
    E_surf = contact.surface_youngs_modulus
    nu_surf = contact.surface_poisson_ratio
    F_n = contact.normal_load
    R_tip = params.tip_radius
    H_surf = contact.surface_hardness

    # Effective modulus
    E_eff = 1.0 / ((1 - nu_tip**2) / E_tip + (1 - nu_surf**2) / E_surf)

    # Effective radius (flat surface → R_eff = R_tip)
    R_eff = R_tip

    # Hertzian contact radius
    a_hertz = (3.0 * R_eff * F_n / (4.0 * E_eff))**(1/3)

    # Contact area
    A_contact = np.pi * a_hertz**2

    # Mean and max pressure
    p_mean = F_n / A_contact
    p_max = 1.5 * p_mean

    # Plasticity index (Greenwood & Williamson)
    # ψ = (E_eff/H_surf) · √(σ_s/R_tip)
    # where σ_s is the RMS roughness of the surface (asperity scale)
    sigma_asperity = params.rms_roughness  # use surface RMS as proxy
    psi = (E_eff / H_surf) * np.sqrt(sigma_asperity / R_tip)

    # Classification
    if p_max > H_surf:
        regime = "plastic"
        contact_note = (
            f"Peak pressure p_max={p_max*1e-9:.2f} GPa exceeds hardness "
            f"H={H_surf*1e-9:.2f} GPa → plastic deformation expected. "
            f"Tip leaves permanent groove in surface."
        )
    elif psi > 1:
        regime = "elastoplastic"
        contact_note = (
            f"Plasticity index ψ={psi:.2f} > 1 → some plastic deformation "
            f"at asperity contacts, but bulk contact remains elastic."
        )
    else:
        regime = "elastic"
        contact_note = (
            f"Plasticity index ψ={psi:.2f} < 1 → fully elastic contact. "
            f"No permanent surface damage."
        )

    # Adhesion correction (JKR model)
    # For soft materials and small tips, adhesion increases contact area
    # JKR contact radius: a³ = (3R/4E_eff) [F_n + 3πRγ + √(6πRγF_n + (3πRγ)²)]
    gamma = contact.adhesion_energy
    adhesion_term = 3.0 * np.pi * R_eff * gamma
    F_eff = F_n + adhesion_term + np.sqrt(6.0 * np.pi * R_eff * gamma * F_n + adhesion_term**2)
    a_jkr = (3.0 * R_eff * F_eff / (4.0 * E_eff))**(1/3)
    adhesion_ratio = a_jkr / a_hertz

    # Effective tip radius after elastic flattening
    # Under load, the spherical tip flattens, increasing effective radius
    # r_eff = r_tip · (1 + p_mean/E_eff)^(1/3) — approximate
    r_eff_loaded = R_tip * (1.0 + p_mean / E_eff)**(1/3)

    return {
        "contact_radius_m": float(a_hertz),
        "contact_area_m2": float(A_contact),
        "mean_pressure_Pa": float(p_mean),
        "max_pressure_Pa": float(p_max),
        "plasticity_index": float(psi),
        "regime": regime,
        "note": contact_note,
        "effective_modulus_Pa": float(E_eff),
        "adhesion_ratio": float(adhesion_ratio),
        "effective_tip_radius_loaded_m": float(r_eff_loaded),
        "hertz_contact_radius_nm": float(a_hertz * 1e9),
        "max_pressure_GPa": float(p_max * 1e-9)
    }


# ============================================================
# 2. COHERENCE ENVELOPE (WLI)
# ============================================================

def compute_coherence_envelope(params: SimulationParams) -> Dict:
    """
    Compute the white-light interferometry coherence envelope.

    WLI uses broadband illumination. The interference signal is modulated
    by a coherence envelope of width l_c (coherence length):

        l_c = λ₀² / Δλ   (for Gaussian spectrum)

    where λ₀ is the centre wavelength and Δλ is the spectral width (FWHM).

    The envelope acts as a Gaussian window in the axial (z) direction,
    limiting the vertical measurement range and providing the height
    resolution mechanism.

    The axial PSF of WLI is:
        h(z) = exp[-z²/(2σ_z²)] · cos(4πz/λ₀)

    where σ_z = l_c / (2√(2 ln 2)) ≈ l_c / 2.355

    Vertical resolution (1σ): δz = λ₀ / (2π · SNR · √N_fringes)
    """
    lambda0 = params.wavelength          # centre wavelength
    delta_lambda = 100e-9                # spectral width ~100 nm for typical LED
    l_c = lambda0**2 / delta_lambda      # coherence length [m]

    # Axial resolution
    sigma_z = l_c / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    # Effective numerical aperture effect on coherence
    # High NA reduces effective coherence length due to oblique rays
    na = params.na
    if na > 0.1:
        # Obliquity factor: rays at angle θ have different OPD
        # Effective coherence reduced by ~ cos(θ_max) ≈ √(1 - NA²)
        obliquity = np.sqrt(1.0 - na**2) if na < 1.0 else 0.1
        l_c_eff = l_c * obliquity
    else:
        l_c_eff = l_c

    # Number of measurable fringes within coherence envelope
    N_fringes = l_c_eff / (lambda0 / 2.0)

    # Envelope width in spatial frequency domain
    # The Fourier transform of a Gaussian envelope is also Gaussian
    # with width σ_f = 1/(2π σ_z)
    sigma_fz = 1.0 / (2.0 * np.pi * sigma_z)

    return {
        "centre_wavelength_m": float(lambda0),
        "spectral_width_m": float(delta_lambda),
        "coherence_length_m": float(l_c),
        "coherence_length_um": float(l_c * 1e6),
        "effective_coherence_length_m": float(l_c_eff),
        "axial_resolution_m": float(sigma_z),
        "axial_resolution_nm": float(sigma_z * 1e9),
        "n_fringes": float(N_fringes),
        "obliquity_factor": float(obliquity) if na > 0.1 else 1.0,
        "envelope_frequency_width": float(sigma_fz),
        "note": (
            f"Coherence length l_c = {l_c*1e6:.1f} µm, "
            f"axial resolution σ_z = {sigma_z*1e9:.1f} nm, "
            f"{N_fringes:.0f} measurable fringes."
        )
    }


# ============================================================
# 3. VECTOR DIFFRACTION THEORY (HIGH-NA)
# ============================================================

def compute_vector_diffraction_correction(params: SimulationParams) -> Dict:
    """
    Compute corrections to the scalar OTF for high-NA optical systems.

    For NA > 0.5, the scalar diffraction theory (which assumes light
    is a scalar field) becomes inaccurate. Vector effects include:

    1. Polarisation-dependent transmission (Fresnel coefficients)
    2. Apodisation (energy conservation in spherical wave conversion)
    3. Depolarisation at high angles (cross-polarisation coupling)

    The vector OTF for incoherent imaging through a high-NA lens includes:
    - Apodisation factor: √(cos θ) for aplanatic lenses
    - Fresnel transmission: depends on s and p polarisation
    - Effective cutoff reduction due to these factors

    Reference: Richards & Wolf (1959), Sheppard & Larkin (1997)
    """
    na = params.na
    n_medium = 1.0  # air
    theta_max = np.arcsin(na / n_medium) if na < n_medium else np.pi/2

    # Apodisation factor (Abbe sine condition)
    # The aplanatic factor is cos^(1/2)(θ) for the pupil function
    # This reduces effective transmission at the pupil edge
    theta = np.linspace(0, theta_max, 100)
    apodisation = np.sqrt(np.cos(theta))

    # Average transmission (Fresnel, unpolarised)
    # For air-glass interface:
    # T_s = 4n cosθ √(n²-sin²θ) / (cosθ + √(n²-sin²θ))²
    # T_p = similar with additional n factors
    # Simplified: T_avg ≈ 0.96 at normal incidence, decreasing to ~0.85 at θ_max
    n_glass = 1.515  # BK7 glass
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    n_cos_t = np.sqrt(np.maximum(n_glass**2 - sin_theta**2, 0))

    T_s = 4.0 * n_glass * cos_theta * n_cos_t / (cos_theta + n_glass * n_cos_t)**2
    T_p = 4.0 * n_glass * cos_theta * n_cos_t / (n_glass * cos_theta + n_cos_t)**2
    T_avg = 0.5 * (T_s + T_p)

    # Combined pupil function
    pupil = apodisation * np.sqrt(T_avg)

    # Effective NA (weighted by pupil function)
    # NA_eff² = ∫₀^{NA} pupil²(θ) sinθ dθ / ∫₀^{NA} sinθ dθ
    sin_th = np.sin(theta)
    numerator = np.trapz(pupil**2 * sin_th, theta)
    denominator = np.trapz(sin_th, theta)
    na_eff_factor = np.sqrt(numerator / denominator) if denominator > 0 else 1.0
    na_eff = na * na_eff_factor

    # Scalar-to-vector correction for OTF
    # The vector OTF rolls off slightly faster than scalar OTF
    # Correction: H_vec(f) ≈ H_scalar(f) · [1 - α·(f/f_c)²] for f < f_c
    alpha_vec = 0.15 * (na / 0.95)**2  # empirical from literature

    # Strehl ratio approximation (effect of aberrations + vector effects)
    # Strehl ≈ exp(-(2π σ_wave)²) where σ_wave is RMS wavefront error
    # For diffraction-limited: Strehl ≥ 0.8
    sigma_wave = 0.05  # λ/20 RMS — diffraction-limited
    strehl = np.exp(-(2.0 * np.pi * sigma_wave)**2)

    return {
        "theta_max_deg": float(np.degrees(theta_max)),
        "apodisation_at_edge": float(apodisation[-1]),
        "transmission_at_edge": float(T_avg[-1]),
        "pupil_at_edge": float(pupil[-1]),
        "na_effective": float(na_eff),
        "na_efficiency": float(na_eff / na),
        "vector_correction_alpha": float(alpha_vec),
        "strehl_ratio": float(strehl),
        "diffraction_limit_mm": float(na / params.wavelength * 1e-3),
        "effective_cutoff_mm": float(na_eff / params.wavelength * 1e-3),
        "note": (
            f"NA_eff = {na_eff:.3f} ({na_eff/na*100:.1f}% of nominal NA={na}). "
            f"Vector correction α = {alpha_vec:.3f}. Strehl = {strehl:.3f}."
        )
    }


# ============================================================
# 4. MATERIAL PROPERTY EFFECTS
# ============================================================

def compute_material_effects(params: SimulationParams,
                              contact: ContactMechanicsParams) -> Dict:
    """
    Compute how material properties affect stylus vs optical measurements.

    Stylus (tactile):
    - Soft materials deform elastically → measured profile is smoothed
    - Hard/brittle materials may fracture at contact points
    - Ductile materials may show pile-up around grooves
    - Material hardness limits maximum measurable roughness

    Optical:
    - Reflectivity R = |(n-ik-1)/(n+ik+1)|² determines signal strength
    - Low reflectivity → poor SNR → higher measurement uncertainty
    - Transparent materials → internal reflections confuse signal
    - Surface films/oxides → thin-film interference
    - Roughness < λ/10 → specular; roughness > λ → diffuse

    Shared:
    - Thermal expansion: ΔL = α · L · ΔT
    - For steel (α≈12×10⁻⁶ /K), ΔT=1K → Δh≈12 nm over 1 mm
    """
    # Optical material properties (typical for steel)
    n_steel = 2.5      # refractive index (real part) at 550 nm
    k_steel = 3.3      # extinction coefficient
    n_glass = 1.5
    k_glass = 0.0
    n_silicon = 4.0
    k_silicon = 0.05

    # Reflectivity at normal incidence
    def reflectivity(n, k):
        return ((n - 1)**2 + k**2) / ((n + 1)**2 + k**2)

    R_steel = reflectivity(n_steel, k_steel)
    R_glass = reflectivity(n_glass, k_glass)
    R_silicon = reflectivity(n_silicon, k_silicon)

    # Effective SNR scaling with reflectivity
    # SNR ∝ R (signal proportional to reflected intensity)
    snr_scale_steel = R_steel / R_steel  # reference = 1.0
    snr_scale_glass = R_glass / R_steel
    snr_scale_silicon = R_silicon / R_steel

    # Thermal expansion (steel at room temperature)
    alpha_steel = 12e-6     # /K
    delta_T = 0.1            # K (typical lab stability)
    L_measurement = 100e-6   # m
    thermal_drift = alpha_steel * L_measurement * delta_T

    # Roughness regime classification (Rayleigh criterion)
    lambda_opt = params.wavelength
    sigma = params.rms_roughness
    # Rayleigh: surface is "smooth" if σ < λ/(8 cos θ_i)
    rayleigh_limit = lambda_opt / (8.0 * np.cos(0))
    if sigma < rayleigh_limit:
        roughness_regime = "specular"
    elif sigma < lambda_opt / 2:
        roughness_regime = "mixed"
    else:
        roughness_regime = "diffuse"

    # Skin depth for optical (how deep light penetrates)
    skin_depth = lambda_opt / (4.0 * np.pi * k_steel) if k_steel > 0 else np.inf

    return {
        "reflectivity_steel": float(R_steel),
        "reflectivity_glass": float(R_glass),
        "reflectivity_silicon": float(R_silicon),
        "snr_scale_vs_steel": {
            "steel": float(snr_scale_steel),
            "glass": float(snr_scale_glass),
            "silicon": float(snr_scale_silicon)
        },
        "thermal_drift_per_100um_nm": float(thermal_drift * 1e9),
        "rayleigh_limit_nm": float(rayleigh_limit * 1e9),
        "roughness_regime": roughness_regime,
        "optical_skin_depth_nm": float(skin_depth * 1e9),
        "note": (
            f"Steel reflectivity R={R_steel:.2f} at {lambda_opt*1e9:.0f} nm. "
            f"Surface is in {roughness_regime} regime (Rayleigh limit = "
            f"{rayleigh_limit*1e9:.1f} nm). Thermal drift ≈ {thermal_drift*1e9:.2f} nm "
            f"over {L_measurement*1e6:.0f} µm for ΔT={delta_T} K."
        )
    }


# ============================================================
# 5. PHYSICAL UNCERTAINTY PROPAGATION
# ============================================================

def compute_physical_uncertainty(params: SimulationParams,
                                  contact: Dict,
                                  coherence: Dict,
                                  vector: Dict,
                                  material: Dict) -> Dict:
    """
    Propagate physical parameter uncertainties to measurement uncertainty.

    Uses first-order Taylor expansion (GUM method):

        u²(y) = Σ (∂y/∂x_i)² · u²(x_i)

    where x_i are physical parameters and y is the measurement.
    """
    # Physical parameter uncertainties (typical values)
    u = {
        "tip_radius": 0.1e-6,           # ±100 nm uncertainty in tip radius
        "normal_load": 0.05e-3,         # ±50 µN load uncertainty
        "wavelength": 1e-9,             # ±1 nm wavelength calibration
        "na": 0.01,                     # ±0.01 NA uncertainty
        "temperature": 0.1,             # ±0.1 K
        "youngs_modulus": 10e9,         # ±10 GPa for steel
        "hardness": 0.5e9,              # ±0.5 GPa
    }

    # Sensitivity coefficients (∂y/∂x_i)
    # 1. Stylus RMSE sensitivity to tip radius
    #    RMSE ∝ r_tip^(1-H) for self-affine surfaces
    H = params.hurst_exponent
    dRMSE_dr = (1 - H) * params.rms_roughness / params.tip_radius

    # 2. Optical RMSE sensitivity to NA
    #    RMSE ∝ 1/NA (roughly — larger NA = better resolution)
    dRMSE_dNA = -params.rms_roughness / params.na

    # 3. Contact area sensitivity
    a_hertz = contact["contact_radius_m"]
    F_n = 1e-3  # 1 mN typical stylus load
    da_dF = a_hertz / (3.0 * F_n)

    # 4. Coherence length sensitivity to wavelength
    l_c = coherence["coherence_length_m"]
    dlc_dlambda = 2.0 * params.wavelength / 100e-9  # d(λ²/Δλ)/dλ

    # 5. Thermal expansion sensitivity
    dL_dT = 12e-6 * 100e-6  # for steel over 100 µm

    # Combined uncertainties
    u_stylus_rmse = np.sqrt(
        (dRMSE_dr * u["tip_radius"])**2 +
        (params.rms_roughness * 0.01)**2  # 1% base uncertainty
    )

    u_optical_rmse = np.sqrt(
        (dRMSE_dNA * u["na"])**2 +
        (params.rms_roughness * 0.02)**2  # 2% base (phase unwrapping)
    )

    u_contact_area = np.sqrt(
        (da_dF * u["normal_load"])**2 +
        (a_hertz * 0.05)**2  # 5% model uncertainty
    )

    u_coherence = dlc_dlambda * u["wavelength"]

    u_thermal = dL_dT * u["temperature"]

    return {
        "u_stylus_rmse_nm": float(u_stylus_rmse * 1e9),
        "u_optical_rmse_nm": float(u_optical_rmse * 1e9),
        "u_contact_area_ratio": float(u_contact_area / (contact["contact_area_m2"] + 1e-30)),
        "u_coherence_length_nm": float(u_coherence * 1e9),
        "u_thermal_drift_nm": float(u_thermal * 1e9),
        "relative_u_stylus": float(u_stylus_rmse / (params.rms_roughness + 1e-30)),
        "relative_u_optical": float(u_optical_rmse / (params.rms_roughness + 1e-30)),
        "dominant_uncertainty_source": (
            "tip radius" if abs(dRMSE_dr * u["tip_radius"]) > abs(params.rms_roughness * 0.01)
            else "base measurement noise"
        ),
        "note": (
            f"Stylus RMSE uncertainty: ±{u_stylus_rmse*1e9:.1f} nm "
            f"({u_stylus_rmse/params.rms_roughness*100:.1f}% of σ). "
            f"Optical RMSE uncertainty: ±{u_optical_rmse*1e9:.1f} nm "
            f"({u_optical_rmse/params.rms_roughness*100:.1f}% of σ)."
        )
    }


# ============================================================
# Block 9 Runner
# ============================================================
@dataclass
class AdvancedPhysicsResult:
    contact: Dict
    coherence: Dict
    vector_diffraction: Dict
    material: Dict
    uncertainty: Dict


def run_block9(result: SimulationResult, output_dir: str) -> AdvancedPhysicsResult:
    """Run complete advanced physics analysis."""
    print("\n" + "█"*70)
    print("█  BLOCK 9 — ADVANCED PHYSICS LAYER")
    print("█"*70)

    params = result.params
    contact_params = ContactMechanicsParams()

    # 1. Contact mechanics
    print("\n  [9.1] Hertzian Contact Mechanics...")
    contact = compute_hertz_contact(params, contact_params)
    print(f"    Regime: {contact['regime']}")
    print(f"    Contact radius: {contact['hertz_contact_radius_nm']:.1f} nm")
    print(f"    Max pressure: {contact['max_pressure_GPa']:.2f} GPa")
    print(f"    Plasticity index ψ: {contact['plasticity_index']:.2f}")
    print(f"    Adhesion ratio (JKR/Hertz): {contact['adhesion_ratio']:.3f}")
    print(f"    {contact['note']}")

    # 2. Coherence envelope
    print("\n  [9.2] WLI Coherence Envelope...")
    coherence = compute_coherence_envelope(params)
    print(f"    Coherence length: {coherence['coherence_length_um']:.1f} µm")
    print(f"    Axial resolution σ_z: {coherence['axial_resolution_nm']:.1f} nm")
    print(f"    Measurable fringes: {coherence['n_fringes']:.0f}")
    print(f"    {coherence['note']}")

    # 3. Vector diffraction
    print("\n  [9.3] Vector Diffraction Theory...")
    vector = compute_vector_diffraction_correction(params)
    print(f"    NA_eff = {vector['na_effective']:.3f} ({vector['na_efficiency']*100:.1f}%)")
    print(f"    Strehl ratio: {vector['strehl_ratio']:.3f}")
    print(f"    {vector['note']}")

    # 4. Material effects
    print("\n  [9.4] Material Property Effects...")
    material = compute_material_effects(params, contact_params)
    print(f"    Steel reflectivity: {material['reflectivity_steel']:.2f}")
    print(f"    Glass SNR vs steel: {material['snr_scale_vs_steel']['glass']:.3f}")
    print(f"    Roughness regime: {material['roughness_regime']}")
    print(f"    {material['note']}")

    # 5. Uncertainty propagation
    print("\n  [9.5] Physical Uncertainty Propagation...")
    uncertainty = compute_physical_uncertainty(params, contact, coherence, vector, material)
    print(f"    {uncertainty['note']}")
    print(f"    Dominant source: {uncertainty['dominant_uncertainty_source']}")

    # Save
    os.makedirs(output_dir, exist_ok=True)
    result_data = {
        "contact_mechanics": contact,
        "coherence": coherence,
        "vector_diffraction": vector,
        "material_effects": material,
        "uncertainty": uncertainty
    }
    with open(os.path.join(output_dir, "advanced_physics.json"), 'w') as f:
        json.dump(result_data, f, indent=2, default=str)

    print(f"\n  Advanced physics results saved to: {output_dir}")
    print("█"*70 + "\n")

    return AdvancedPhysicsResult(
        contact=contact,
        coherence=coherence,
        vector_diffraction=vector,
        material=material,
        uncertainty=uncertainty
    )


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from block4_physics_simulator import run_block4, SimulationParams
    params = SimulationParams(grid_size=512)
    sim_result = run_block4(params, "./outputs/iter01/sim")
    run_block9(sim_result, "./outputs/iter01/advanced_physics")
