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

## Panel-audit execution (2026-10-16, after reviewer-panel audit)

Applied the Top-20 acceptance-gain roadmap. Key changes and consequences:

- **H convention fixed (T1):** block8 Fisher/capacity/observability now use the
  amplitude convention (tf.H is the power transfer; sqrt recovered first).
  CONSEQUENCE: the pipeline MI ratio flips to I_o/I_s = 0.68 — the
  "optical transmits 1.6-1.7x more MI" headline was an artefact of double
  squaring + estimator choice and is WITHDRAWN; manuscript now reports the
  ratio as estimator-dependent (0.7-1.6) with the robust per-band ranking.
- **Ensemble regenerated from code (T4):** pipeline/run_ensemble.py (seeds
  100-129) rewrote ensemble_stats.json. New values: alpha_s=0.0095+/-0.0037,
  alpha_o=0.0013+/-0.0006 (stylus ~7x optical, intervals no longer overlap),
  f_cross=454+/-166 mm-1 (lambda_cross=2.2 um), eq_frac=9.6%+/-0.3%
  (was 18.3%+/-0.2%). Manuscript abstract/results/captions/table/conclusions
  and the roadmap baseline updated accordingly.
- **Gramian equation aligned with code (T3):** observability condition number
  redefined as max|H|^2/min|H|^2 over the passband; Xi_o/Xi_s = 5.9 (was 1.31,
  recomputed under the amplitude convention).
- **SNR bound status clarified (T2):** operational second-moment definitions of
  the effective widths + SI S4.3 status paragraph (definitionally anchored
  ansatz consistent with the classical limit and Greco & Boyer 2019; explicit
  falsification protocol). Cover-letter "new measurement limit" reworded.
- **Variants added (T8/T9):** stylus raster sweep Delta-x = 100/200/400 nm
  (RMSE 13.6/16.3/16.7 nm; 3 dB at 1255/1049/671 mm-1) and polychromatic OTF
  average 500-700 nm (96.5% of passband within 3 dB of monochromatic).
  Stored in robustness/variant_simulations.json; summarised in the
  "Sampling and illumination variants" paragraph.
- **Housekeeping:** monochromatic mean-lambda statement; scaling-law and
  SNR-bound falsification sentences; sweep parameter table; public-benchmark,
  Fisher/CRB (fig8) and ensemble (fig10) figures now referenced; search-basis
  footnote for "no prior work"; tip-radius uncertainty cross-reference; h5py
  pinned in verification/requirements-benchmark.txt; ensemble seeds stated in
  Data Availability; roadmap figure baseline marker updated (regenerate_roadmap.py).
- Builds: main 60 pp, SI 19 pp, cover 3 pp — all 0 errors, 0 undefined.
  14/14 verification tests pass.

## Round-2 panel execution (2026-10-17)

Executed the Round-2 Top-20 roadmap:

- **Grid convergence regenerated (R1):** new generator pipeline/run_grid_convergence.py;
  eq_frac now 0.25/0.20/0.098/0.042 for N=128/256/512/1024 (monotonic; N=512
  consistent with the 9.6% ensemble). Limitations updated.
- **Π recomputed (R2):** Π_s ≈ 2.6e10, Π_o ≈ 1.7e9 (≈15×, dominated by stylus
  anisotropy); "similarly valued" wording removed.
- **B_eq/η defined in one line each (R3); κ(O)→κ; "stylus cutoff"→"tip-radius
  scale" (Conclusions, fig4, SI fig9); SI f_cross 311→454 mm⁻¹ (R4).**
- **Ensemble runner extended (R7):** MI proxy 0.907±0.001 vs 0.706±0.012 (n=30);
  L_s=(2.72±0.04)e12, L_o=(1.29±0.03)e12; per-band losses with ±std. Results
  section and Table tab:bands updated.
- **T8 added (R9/R8):** independent information-loss slope check. RESULT: the
  manuscript's "I(f) ∝ f^0.01 (near-constant)" claim is REFUTED — verified
  log-log slope ≈ 0.45 over 0.05–1.5 mm⁻¹. Abstract, fig3 caption and Results
  updated to "increases mildly with frequency (slope ≈0.4)".
- **R6:** factorisation equation now aperture × sampling (noise additive).
- **R5:** Δx "less than 20%" → "less than 25%" (13.6–16.7 nm span).
- **R10:** gap-closure generator pipeline/run_gap_closure.py (--limit preview
  validated; committed JSON documented as generated by it).
- **R11–R17:** verification-suite sentence in Data Availability; fig8 caption
  states noise estimator; γ "testable at larger n"; SI "natural first-order".
- Builds: 61 pp + 19 pp + 3 pp, 0 errors, 0 undefined. 15/15 tests pass.
- **Public-data extension (stylus):** Aksulu 2021 ball-standard calibration
  profiles (Zenodo 10.5281/zenodo.4471347, CC-BY-4.0) downloaded to
  data_public/aksulu2021. Direct tip validation impossible: published profiles
  carry 44/120 um scatter (M40/M1000) and are non-circular (edge artefacts
  -623/-9286 um dominate). Honest reframe: synthetic-geometry parallel-curve
  cross-check on the fitted calibration geometry — simulator reproduces
  measured radius = true radius - tip radius within 3-5% for r_tip = 2/5/50 um.
  Manuscript + cover letter now state this geometric check with the noise-floor
  caveat; Aksulu cited. T9 added (self-contained, no data dependency) — 16/16.
- **SI relocation (page reduction):** fig8 Fisher/CRB and fig10 ensemble moved
  to Supplementary Material as Fig. S3/S4 (main text keeps one-sentence
  pointers); GUM uncertainty-propagation derivation moved to a new SI section
  (main text keeps the 1.2/0.9 dB bands and the threshold comparison).
- Builds: 60 pp + 21 pp + 3 pp, 0 errors, 0 undefined. 16/16 tests pass.
