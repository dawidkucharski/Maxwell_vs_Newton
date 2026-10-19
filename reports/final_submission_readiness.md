# Final Submission Readiness — Science Audit Gate

Date: 2026-10-18. Branch: `audit-science`. All statements below are backed by committed code, committed outputs or the reports referenced.

## Pass/fail per priority-zero audit

| # | Audit | Status | Evidence |
|---|---|---|---|
| 1 | Reproducible baseline | **PASS** | 18/18 tests; clean builds; headline→artefact map in `reports/baseline_audit.md` |
| 2 | Stylus model (dilation vs linear TF) | **PASS** | Dilation geometry (paraboloid tip, cone 45°, boundary, raster 100–400 nm) audited in `block4`; PSD ratio is a biased power-response estimate (noise adds to numerator; curvature bias adds low-f excess) — this is disclosed in the manuscript; cross-spectral H and coherence computed in `reports/stylus_channel_audit.json`; linearised model captures the low-f excess; 3 dB point reproduced and locked by T10 |
| 3 | Frequency-domain recommendations | **PASS** | Cutoff nomenclature fixed in Round 3 (λ<0.5 µm); T8 slope band 0.05–1.5 mm⁻¹ lies inside FOV limits (fundamental 10 mm⁻¹, Nyquist 2.56 mm⁻¹); decision matrix scope note added |
| 4 | Optical model | **PASS with noted limits** | OTF support 2NA/λ verified (T1, `block4`); monochromatic scalar imaging-OTF with 1D unwrapping, pixel MTF negligible at mag 50; public benchmark now explicitly a model-description check (fitted amplitude, slope, cutoff scale) |
| 5 | Information-theory formulation | **PASS with corrections** | MMSE formula verified by Monte Carlo (T11, rel. 0.2 %); MI (1/2) factor correct for real fields; pipeline C_total double-counts Hermitian halves — documented; capacity vs MI distinction stated; bound status aligned (adopted benchmark, not theorem); untraceable mode counts replaced (127,472/61,631) |
| 6 | Scatterometry and fusion | **PASS with downgrades** | Rayleigh–Rice constants re-checked (f_max=2/λ=3760 mm⁻¹ ✓); "optimal fusion" downgraded to minimum-variance linear under the stated model; raw-PSD bias caveat added; demo explicitly uses known synthetic H, N |
| 7 | Contact mechanics / physical SI | **PASS with removals** | Hertzian numbers re-derived ✓ (a=201 nm, ψ=5.83); elastic-extrapolated groove depth and effective-radius formula removed; coherence-envelope lateral-filter claim removed; skin-depth claim reworded |
| 8 | Cross-manuscript consistency | **PASS** | ρ CV triple (0.16/0.22/0.067) reconciled like-for-like; scaling-law terminology consistent; test count 18 everywhere; stylus H values consistent (Methods/Results/Robustness all trace to variant procedure) |
| 9 | Scaling-law re-test | **PASS with downgrade** | `reports/scaling_law_audit.json`: slope 1.904±0.134; blocked R²=0.518; leave-tip 0.523; leave-NA 0.482; null 0; median ratio error ×1.93, p90 ×12.8; residual–σ r=0.81 → presented as order-of-magnitude descriptor |
| 10 | Scope and novelty | **PASS** | Hedges retained; "carries over without modification" qualified; contributions delimited vs prior art in Comparison with Prior Work |
| 11 | Reproducibility / publication | **PASS with plan** | Eighteen-test suite incl. new T10/T11; audit scripts committed; public-data provenance (CC-BY-4.0, DOIs) stated; repository snapshot preserved; public deposit prepared for acceptance (author decision to defer) |

## Ranked issues

Blocking: **none.** All previously unverifiable claims were either reproduced, replaced by reproducible values, or removed.

Major (resolved, residual limits stated): scaling relation is a coarse descriptor; stylus PSD ratio is a biased response estimate (disclosed); fusion requires calibrated H/N experimentally; mode counts are estimator-dependent (stated).

Minor: stale `iter01` npy arrays remain in the repo (documented as not used for claims); the physical SI now contains only verifiable statements.

## Reviewer simulation

**Reviewer 1 — surface-texture metrology.** Accepts the dilation-based stylus treatment; confirms the PSD-ratio caveats are now explicit. Asks that the empirical scaling relation not be called predictive — fixed. Recommendation: **Minor Revision / Accept**.

**Reviewer 2 — optical instrumentation.** Accepts the imaging-OTF scope statement and the benchmark's model-description framing; notes the scalar/monochromatic simplifications are disclosed and quantified (polychromatic 96.5 %, public cutoff shift 15 %). Recommendation: **Minor Revision**.

**Reviewer 3 — information theory.** Accepts the corrected mode counting, the (1/2)-factor terminology note, the MMSE Monte Carlo verification and the bound's benchmark status. Notes Ξ/Π remain heuristic figures of merit — already labelled as such. Recommendation: **Minor Revision**.

## Remaining scientific risks

1. No paired experimental tactile–optical dataset; validation is computational + two public cross-checks (one geometric).
2. The bound is an adopted benchmark, not a theorem; reviewers seeking a proof may still object (status is stated).
3. Scaling relation is exploratory-quality (R²≈0.5); now honestly framed.
4. Fusion optimality holds only under the stated model; experimental implementation needs calibrated H and noise PSDs.

## Recommendation

**SUBMIT** to STMP after the routine rebuild/commit of this branch. The manuscript now contains no claim that cannot be traced to a committed artefact, and every known overstatement has been removed or scoped.

---

## Revision-audit update (2026-10-19) — supersedes the verdict above

A final scientific pass (`reports/revision_audit.md`) rechecked every headline claim against code and recomputation. New corrections: the instrument-selection protocol (0.5 µm cutoff logic), the information-loss slope interval (50–1500 mm⁻¹, transcription ×1000), the bound wording (no "any algorithm" claim), the vector-diffraction numbers (unsupported values removed; 91 % apodisation retained, Fresnel recomputed ≈96 %), the GUM budget (numeric table removed as non-derivable), the sampling-depth claim, and the MI-proxy naming.

Status of priority checks: optical cutoff/recommendations **fixed**; slope/grid **fixed**; stylus PSD-ratio interpretation **verified and qualified**; bound **fixed and aligned**; information theory **verified (T11) with documented conventions**; supplementary physics **fixed**; scatterometry/fusion **retained only as illustrative, not quantitative**; scaling relation **verified and retained with qualification**; surface-class CVs and public-benchmark scope **reconciled**.

Build: 62 pp + 22 pp, 0 errors, 0 undefined; 18/18 tests.

**Verdict: READY.** Remaining limitations (computational-only validation; illustrative fusion; heuristic Ξ/Π) are disclosed and carry no unsupported numerical claims.
