# Changelog — STMP Submission Readiness Mission

All work on branch `stmp-revision`; baseline preserved on `main` (`ed79ded`).

## f2350dc — Phase 1: initial audit
- Repo initialised; inventory of pipeline, manuscripts, outputs.
- Number cross-check against outputs; critical findings listed.
- `reports/initial_audit.md`.

## 7c1d9a2 — Phase 2: mathematical/physics audit + test suite
- `verification/run_tests.py` (14 tests): OTF vs pupil autocorrelation (T1),
  small-slope dilation H≈1 + curvature bias (T2a/b), independent MI recompute
  (T3), SNR-bound limits (T4), analytic isotropy (T5), honest sweep refits (T6a-c),
  out-of-sample scaling law (T7).
- Central finding: Eq. hstylus (Gaussian×sinc) refuted by the dilation simulator.
- `reports/mathematical_physics_audit.md`.

## 85df68d — Phases 3, 4, 7: literature, public data, benchmark
- 10 Crossref-verified references added (Wu 1999/2000; McCool 1984; de Groot 2021;
  Dai 2020; Takacs 2010; Leach & Sherlock 2013; Haitjema 2015; Greco & Boyer 2019;
  Clark & Greivenkamp 2002) + Hirose 2025 (Applied Optics 64:5461).
- `reports/literature_novelty_audit.md` (claim-by-claim novelty disposition).
- contact.engineering unreachable (DNS); Zenodo searched; Hirose dataset
  (10.5281/zenodo.15750880, CC-BY-4.0, 403 MB) downloaded with SHA-256 provenance;
  git-ignored; re-fetch script added.
- `verification/public_data_benchmark.py`: WLI spectra vs incoherent-OTF model,
  fitted cutoff scale c = 1.15 ± 0.01, shape correlation ≈0.97.
- `reports/public_data_audit.md`, `reports/public_data_benchmark.json`.

## 16aedb7 — Phases 5–9: evidence rebuild, manuscript revision, reproducibility
- `verification/fix_scaling_fits.py`: replaces hardcoded placeholder γ=5.0 with
  honest refit (γ = −0.02 ± 0.19, n=3); δ = 1.904 ± 0.134 (SE), R² = 0.531,
  out-of-sample R² = 0.511; α_s = 0.0112 ± 0.0112 (n=180); crossover vs tip
  β = −0.056 ± 0.009 (R² = 0.93, tip-averaged).
- `pipeline/generate_missing_figures.py`: regenerates fig7 (SID + water-filling),
  fig8 (CRB/Fisher), figS2 (k-space trust-region fusion), fig10 (ensemble
  validation), and refreshes fig1–6; pipeline re-run reproduces stored JSONs
  bit-identically.
- Manuscript revisions (main + supplementary + cover letter):
  - Eq. hstylus replaced by small-slope dilation result with curvature bias;
    Gaussian idealisation removed and flagged as refuted.
  - f_c,stylus = 159 mm⁻¹ retained only as definitional tip-radius scale.
  - f^{-1.52} removed (local descriptor f^{-0.43}).
  - γ≈5 claim withdrawn (null result reported).
  - δ uncertainty corrected to ±0.13 (SE) with out-of-sample R².
  - α_s sweep value corrected (0.011 ± 0.011) with definition-dependence note.
  - MI ratio reported as 1.6–1.7 with estimator dependence; capacity/MI
    terminology fixed; "capacity efficiency > 1" noted as not a true capacity.
  - Linearity section rewritten with actual sub-linear/crossing/super-linear data.
  - ρ definition unified and flagged as linearised quantity for the stylus channel.
  - H_optical scoped below the unwrapping-error floor; imaging-OTF scope explicit.
  - Comparison-with-Prior-Work rewritten with 10 new references; novelty narrowed.
  - Public-data validation paragraph added (cutoff scale 1.15 ± 0.01).
  - Conclusions and data-availability updated; cover letter aligned.
  - LaTeX: \pm moved into math mode, \bibliography unguarded (fixes empty bbl),
    duplicate bib entries removed; all builds clean (57 + 18 + 3 pages,
    0 errors, 0 undefined).
- 14/14 verification tests pass after all changes.

## Phase 10
- `reports/final_submission_readiness.md` (this changelog accompanies it).
- Verdict: submission-ready; remaining limitations are stated in the manuscript,
  none are fatal blockers.
