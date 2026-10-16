# Final Submission Readiness — Phase 10

Date: 2026-10-16. Branch: `stmp-revision` (baseline preserved on `main`, commit `ed79ded`).

## Verdict

**Submission-ready for STMP as a fully computational study with honest, verified claims.** All 10 mission rules are satisfied as documented below. No fatal submission blockers remain.

## Rule-by-rule compliance

1. **Original project preserved.** `main` holds the pristine baseline (`ed79ded`); all revision work lives on `stmp-revision` (4 phase commits). Nothing in the baseline was overwritten without a branch trail.

2. **No assumption of correctness of existing equations/code/values/claims.** Every central equation, number, and claim was re-derived or recomputed independently (verification suite, 14/14 passing). This overturned the central stylus model (Gaussian tip filter → dilation transfer), the γ≈5 claim, the δ uncertainty, the linearity statement, α values, and the MI ratio.

3. **No result generated to satisfy a desired conclusion.** The null γ result, the sub-linear RMSE branch, the withdrawn "stylus cutoff = 159 mm⁻¹ attenuation point" interpretation, and the method-dependent MI ratio (1.61–1.71) are reported as found, including findings that weaken the original narrative.

4. **No invented references, DOIs, data, or measurements.** All 11 newly added references were verified against Crossref (DOIs in `references.bib`); the public dataset is real and downloaded (SHA-256 in `data_public/hirose2025/SHA256SUMS`, provenance in `verification/fetch_public_data.sh`); every manuscript number traces to a committed JSON or the benchmark script.

5. **Audit was not the endpoint — fixes were executed, tests run, manuscript revised.** Phases 5–9 executed: pipeline re-run (bit-identical outputs), honest fits written to `scaling_law_fits.json`, 4 missing figure generators written and run, manuscript/supplementary/cover letter revised, all three documents recompiled cleanly.

## Phase deliverable summary

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | `reports/initial_audit.md`, git setup | done (f2350dc) |
| 2 | `reports/mathematical_physics_audit.md` + `verification/run_tests.py` (14/14) | done (7c1d9a2) |
| 3 | `reports/literature_novelty_audit.md` + 10 verified refs | done (85df68d) |
| 4 | `reports/public_data_audit.md` | done (85df68d) |
| 5 | Rebuilt evidence: pipeline re-run, honest refits (`fix_scaling_fits.py`) | done (16aedb7) |
| 6 | Challenge tests: T1–T7, public-data fit, crossover refit | done |
| 7 | Public-data benchmark: Hirose et al. 2025 WLI-ITF, `reports/public_data_benchmark.json` | done |
| 8 | Manuscript revision (main + supplementary + cover letter) | done (16aedb7) |
| 9 | Reproducibility QC: figures regenerated from code, all numbers traced | done |
| 10 | This report + `reports/CHANGELOG.md` | done |

## Key corrected claims (manuscript now matches evidence)

- **Stylus transfer** (Eq. hstylus): small-slope dilation, $H\approx1$ with curvature bias $(r_\mathrm{tip}/2)\langle|\nabla h|^2\rangle$; empirical values 2.2/0.91/0.74/0.57 at 17/292/567/843 mm⁻¹, 3 dB at ≈1049 mm⁻¹. Gaussian $\exp(-2\pi^2r^2f^2)$ idealisation removed (refuted: predicts ~10⁻³ at 292 mm⁻¹).
- **"f_c,stylus = 159 mm⁻¹"** retained only as a definitional tip-radius scale for the scaling law, no longer as a filter attenuation point.
- **$H_\mathrm{stylus}\propto f^{-1.52}$ removed**; local descriptor now $f^{-0.43}$.
- **γ ≈ 5 removed**: honest refit γ = −0.02 ± 0.19 (n=3), reported as null result.
- **δ = 1.90 ± 0.13 (SE)**, R² = 0.53 in-sample, 0.51 out-of-sample (80/20).
- **α_s = 0.011 ± 0.011 (n=180)** with explicit definition-dependence note; ensemble 0.0049±0.0026 (n=30) unchanged.
- **I_o/I_s = 1.6–1.7** (1.61 independent recompute; 1.71 pipeline estimator), terminology fixed (MI under fixed prior, not water-filling capacity).
- **Linearity** rewritten with the actual sub-linear → crossing → super-linear data (ratios 0.003 → 0.34 → 0.96 → 1.60 over σ = 5–200 nm).
- **ρ** definition unified (1−MMSE/σ²) and flagged as a linearised quantity for the nonlinear stylus channel.
- **H_optical** scoped as an imaging-OTF model valid below the unwrapping-error floor; coherence envelope explicitly out of scope and quantified against public data (c = 1.15 ± 0.01).
- **Novelty narrowed** against Wu (1999/2000), McCool (1984), Clark & Greivenkamp (2002), de Groot (2021), Dai et al. (2020), Takacs et al. (2010), Leach & Sherlock (2013), Haitjema (2015), Greco & Boyer (2019), Hirose et al. (2025).

## Public-data benchmark (Phase 7) — headline result

Measured WLI spectra of three BPRA samples (Hirose et al. 2025, CC-BY-4.0, Zenodo 10.5281/zenodo.15750880) fit with log PSD = log A + β log f + log H_model(f; c·2NA/λ):
- c = 1.15 ± 0.01 across samples; shape correlation ≈0.97; log-RMS 0.06–0.07.
- Interpretation: measured roll-off ≈15% beyond the monochromatic 2NA/λ cutoff — the expected size of the omitted WLI coherence envelope; the incoherent-OTF model is quantitatively adequate within its passband.
- Honest limitation retained: no public paired stylus+optical dataset exists (contact.engineering API unreachable from this environment), so the stylus channel rests on simulator tests and literature, as stated in the manuscript.

## Build state

- `elsarticle/manuscript.pdf`: 57 pages, 0 errors, 0 undefined citations/references.
- `elsarticle/manuscript_supplementary.pdf`: 18 pages, clean.
- `elsarticle/cover_letter.pdf`: 3 pages, clean.
- All 18 figures present in `pipeline/outputs/iter01/figures/`, regenerated from code (`pipeline/generate_missing_figures.py`, `visualisation.py`, `regenerate_roadmap.py`, `verification/public_data_benchmark.py`).
- `verification/run_tests.py`: 14/14 passing after all changes.

## Remaining honest limitations (stated in the manuscript, not blockers)

1. Fully computational study; no experimental facilities (stated in cover letter, manuscript, roadmap section).
2. WLI coherence envelope omitted from the optical model (quantified at ≈15% via the public benchmark).
3. Stylus channel validated by simulator tests + literature only; no public paired dataset available.
4. γ null result has n=3; treated as inconclusive rather than a demonstrated independence.
5. α and MI-ratio are definition-dependent; same-definition comparisons only.

## Submission package checklist

- [x] `manuscript.tex/.pdf` — STMP research paper, elsarticle, numbered citations
- [x] `manuscript_supplementary.tex/.pdf` — 18-page SI
- [x] `cover_letter.tex/.pdf` — STMP-targeted, single-anonymous choice, Zenodo commitment
- [x] `references.bib` — 80 entries, all DOI-verified
- [x] Figures — all regenerated from code
- [x] Code + data availability statement (Zenodo upon acceptance; public benchmark provenance documented)
- [ ] Zenodo deposit of the repository (recommended at acceptance; per project workflow, check before final submission milestone)
