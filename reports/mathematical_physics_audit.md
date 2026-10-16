# Mathematical and Physical Audit — Phase 2

Date: 2026-10-16. Executable tests: `verification/run_tests.py` (14/14 pass after fixes).

## A. Measurement operator

`M[h] = F^{-1}[H F[h]] + η` is LSI. Valid for: optical imaging path (diffraction is LSI in the aperture-limited model) and stylus *raster sampling* (LSI). **Not valid for:** morphological tip dilation (nonlinear, non-LSI in general), phase wrapping/unwrapping (nonlinear), and the dilation curvature bias (state-dependent offset). The operator formalism is therefore an *idealisation per stage*; the pipeline's stylus output is the dilation+samples+noise chain, which is nonlinear. Manuscript must not claim a single universal linear H for the full stylus chain.

## B. Real-contact stylus profilometry — CENTRAL FINDING

**The manuscript's analytic stylus transfer function does not describe its own simulator.**

- Pipeline implements geometric morphological dilation (paraboloid tip truncated at the cone contact radius) + raster interpolation + noise (`block4.simulate_stylus`).
- The manuscript Eq. (hstylus): H ≈ exp(−2π²r_tip²(f_x²+f_y²))·sinc·sinc predicts a 0.5 crossing at ≈94–155 mm⁻¹.
- Empirical H_stylus (fresh run, Hann windowing): H≈2.2 at 17 mm⁻¹, 0.91 at 292, 0.74 at 567, 0.57 at 843 mm⁻¹; crosses 0.5 at ≈1049 mm⁻¹. Pipeline ensemble: stays 0.94–1.26 out to ≈900 mm⁻¹, crosses 0.5 at ≈2631 mm⁻¹ (near Nyquist).
- **Independent theory (verified in T2a/T2b):** for small slopes, dilation leaves the fundamental amplitude unchanged (H≈1) and adds a curvature bias h_d − h ≈ (r/2)(dh/dx)². Tests: fundamental ratio 0.9998; bias 1.82 nm vs predicted 1.97 nm (8%). The attenuation only sets in when feature curvature approaches 1/r (λ ≲ 2π√(a·r)).
- Consequence: Eq. (hstylus) is **wrong for the dilation simulator**. The Gaussian form is a literature idealisation, not the transfer function of the model used. The empirical stylus response is ≈flat with a low-frequency curvature-bias excess and a roll-off only near the sampling limit.
- `block4`'s Gaussian *fallback* uses σ=r/√2 (exp(−π²r²f²)) — inconsistent with the manuscript's exponent (exp(−2π²r²f²)); the fallback never runs (scikit-image available).

**Required manuscript correction:** replace Eq. (hstylus) with the small-slope dilation result + empirical statement; remove `H ∝ f^{-1.52}`; remove the 159 mm⁻¹ Gaussian-derived cutoff and define cutoffs empirically or from the sim metadata with the convention stated; re-derive all downstream statements (stylus "nearly flat" in the roadmap is *correct*; "stylus dominates at low f" remains true because H_stylus ≈1 exceeds the OTF mid-band attenuation).

## C. Optical profilometry

- Code implements the ideal incoherent circular-aperture OTF with support 2NA/λ (code comment; `f_norm = f/(2·f_cutoff)`), although the metadata labels NA/λ as `optical_cutoff_m`. Manuscript now uses 2NA/λ (corrected 2026-10-13). T1 verifies the OTF equals the disc-pupil autocorrelation (err 0.0023). ✓
- The model is strictly **imaging-OTF only**: no lateral pixel MTF of the camera beyond the optional Gaussian pixel filter, no coherence-envelope vertical effects (covered in SI), and 1D row-unwrapping errors that *inject* broadband power — the empirical H_optical exceeds 1 in the high band (unwrap-error power). Manuscript's "H_optical follows the ideal OTF" must be scoped: true below the unwrap-error floor; above it the PSD-ratio is noise-dominated.
- Modality scope statement exists (WLI; CTF caveat). ✓

## D. Information theory

- MI expression verified direction and magnitude (T3: I_o/I_s = 1.61 with an ad-hoc noise-floor; pipeline 1.71 with its own floor). Ratio is definition-dependent — report with the definition.
- **`capacity_efficiency_optical = 1.265 > 1`** in `block8` — the denominator is not a true capacity (the reported C_total is MI for a fixed surface prior, not the water-filling optimum). The manuscript uses "capacity" for the water-filled quantity and MI elsewhere; keep the distinction explicit. Manuscript's C_o/C_s = 1.71 matches the stored C ratio ✓.
- `F_integrated_stylus == F_integrated_optical` (block8) — degenerate computation; not used in manuscript. Documented as a code defect; excluded from claims.
- MMSE formula algebraically consistent (σ² − ∬|H|²S²/(|H|²S+Sη) = ∬S·Sη/(…) ✓ by derivation in SI S4.2). Note: MMSE formula is valid for the *linearised* channel only; the true stylus channel is nonlinear (dilation), so ρ_stylus is a linearised quantity — state this.
- SNR bound: T4 verifies the limiting cases and the quoted products 0.081/0.083. The bound is a noise-generalised uncertainty relation; presented as "metrological formulation" after the 2026-10-13 revision ✓.
- Units: ι(f) was "bits m²" — corrected to "bits per mode" (2026-10-13) ✓. I(f) is log10 PSD ratio (decades) — annotated as a diagnostic, not Shannon information ✓.
- Isotropy: analytic H_stylus is exactly isotropic (T5 α=7.5e-17). Empirical α depends on definition: ensemble metric 0.0049±0.0026, sweep 0.011±0.011 (n=180), band-limited second-moment on the stored 2D H 0.142. The manuscript must fix ONE definition and note that α confounds physical anisotropy with raster-interpolation and noise artefacts.

## E. Numerical verification results (sweep refits)

- Scaling law: δ = 1.904 ± 0.134 (SE of slope), R² = 0.531; out-of-sample (80/20 split): R²_test = 0.511, log10-RMSE 0.873 decades (T6b, T7). The law transfers out-of-sample but is coarse; report the ±0.13 SE, not ±0.05.
- **info-loss-vs-H: honest refit gives γ = −0.02 ± 0.19 (n=3) — no significant dependence.** The stored fit (`gamma: 5.0, I_0: 100, std: Infinity`) is a hardcoded placeholder. The manuscript's "I ∝ exp(−5H), factor e per ΔH≈0.2" claim is unsupported and must be removed.
- α_s across 180 sweep combos: 0.0112 ± 0.0112 (manuscript quoted 0.014 ± 0.011 from a 5-point subset) — unify.
- Linearity sweep (quantified_limits.json): actual/linear RMSE ratio = 0.003 (σ≤20 nm) → 0.34 (50 nm) → 0.96 (100 nm) → 1.34–1.60 (150–200 nm). Sub-linear below ~75 nm (discretisation floor), crossing ≈100 nm, super-linear above (dilation nonlinearity). The current manuscript sentence (linear holds ≤50 nm) is contradicted; rewrite with these numbers (the "linear" reference is itself anchored at the baseline RMSE, i.e., not an independent prediction — state this).
- Gaussian vs Poisson: difference ≈3.6% across photon levels ✓ (claim supported); absolute 68.5 nm values come from the 256-grid harness, not the baseline — do not mix.

## F. Reproducibility blockers (from Phase 1, confirmed)

- Missing figure generators for fig7, fig8, fig10, figS2.
- Placeholder fit in `scaling_law_fits.json`.
- One-off generators for quantified_limits / model_variants / grid_convergence / gap_closure not in repo.
- Eq. (hstylus) divergence (this audit, §B).
