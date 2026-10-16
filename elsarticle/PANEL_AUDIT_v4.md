# Panel Audit — Senior Associate Editor + Reviewer Panel (v4)

**STATUS (2026-10-13): All Phase-10 action items 1–17 and 19–20 APPLIED.**
Manuscript recompiled: 51 pp main + 18 pp SI + 3 pp cover, 0 undefined references/citations.
Remaining open items: #18 (grid-convergence figure for the 18.3 % headline — numbers now stated in text from existing grid_convergence.json) and #20 (overlay of a published measured ITF — requires literature data extraction).

Target journals: STMP (IOP), MST (IOP), IEEE TIM, Precision Engineering, Optics and Lasers in Engineering.
Manuscript: "Optical Profilometry Versus the Stylus: A Spectral Theory for Closing the Accuracy Gap" (50 pp + 18 pp SI).
Date: 2026-10-13. Scope: identify weaknesses; do NOT rewrite the manuscript; no new theory.

---

## PHASE 1 — TECHNICAL AUDIT (hostile Q1 reviewer)

| # | Weakness | Rank | P(reviewer finds) |
|---|----------|------|-------------------|
| 1 | **Factor-of-2 cutoff inconsistency.** Eq. hoptical defines f̃=λf/(2NA)<1 → incoherent OTF cutoff is 2NA/λ = 2000 mm⁻¹. Text repeatedly states f_c = NA/λ = 1000 mm⁻¹ and uses it for the roadmap (1450 mm⁻¹ at NA 0.8). The convention is never declared. An optics reviewer will catch this. | **Critical** | 0.80 |
| 2 | **Equivalence-fraction inconsistency.** Baseline equivalence is 18.3 % ± 0.2 %; the robustness section reports the equivalence fraction "varies from 0.46 to 0.48" across OTF variants — 2.5× larger, unexplained. Internal contradiction. | **Critical** | 0.70 |
| 3 | **Inverted linearity-boundary statement.** "RMSE ∝ σ holds within 10 % for σ > 100 nm; for σ < 50 nm discretisation errors dominate and the linear approximation overestimates RMSE." Dilation nonlinearity *increases* with σ; the sentence reads backwards and the σ/r_tip>0.05 inequality contradicts the ≤-sign expected for the linear regime. | **High** | 0.65 |
| 4 | **Mutual-information proxy contradicts Shannon MI.** MIR = MI_s/MI_o = 1.28 (stylus better) vs I_o/I_s = 1.71 (optical better). Both appear; the tension is never explained. A reviewer will demand reconciliation. | **High** | 0.75 |
| 5 | **CV(ρ) inconsistency.** Abstract/conclusions: CV=0.22 "across four manufactured classes". SI: "for random rough surfaces ρ varies by only 16 %". Also ρ saturates at 1.0 for deterministic classes, which the paper admits — so "instrument-limited, weakly modulated by surface" sits uneasily next to saturation. | **High** | 0.60 |
| 6 | **Headline scaling law has R²=0.53** yet abstract says "validates the scaling law". Exponent ±0.05 with R²=0.53 invites challenge; "empirically validated" overstates simulation evidence. | **High** | 0.70 |
| 7 | **Novelty claims at risk (see Phase 2).** "No prior work has applied information theory to the comparison of surface measurement modalities" + "no closed-form mutual information ... for any profilometry modality" — the Gaussian-channel MI formula is textbook (Cover & Thomas, cited); the "derivation" is an application. | **High** | 0.65 |
| 8 | **SNR-dependent uncertainty bound presented as new.** Δx·Δf ≥ (1/4π)(1+1/SNR̄)-type noise-generalised uncertainty bounds exist in the signal-processing/optics literature. "A new measurement limit" will be challenged. | **High** | 0.55 |
| 9 | **Ensemble count inconsistency.** Intro: "n=110 across six surface classes". SI: 6 classes × n=5 (=30) + non-Gaussian 3×20 (=60) + baseline n=30 ⇒ 120, not 110. Reconcile or define. | **Medium** | 0.50 |
| 10 | **Stylus cutoff 159 mm⁻¹ unexplained.** 3 dB point of the Gaussian tip filter alone is ≈94 mm⁻¹; with sinc it is lower. The criterion yielding 159 mm⁻¹ is never stated. | **Medium** | 0.40 |
| 11 | **Anisotropy principal direction claim.** θ=136.8° "approximately aligned with the raster scan direction" — 136.8° is ~47° from the scan axis, and for α≈0.005 the tensor is near-degenerate, so θ is ill-conditioned. The alignment claim is unsupported and risky. | **Medium** | 0.55 |
| 12 | **"Information loss" I(f)=log₁₀(PSD ratios) is not an information measure**; terminology collides with the Shannon analysis later. Reviewers may object to calling a PSD-ratio diagnostic "information loss" in the same paper that defines true MI. | **Medium** | 0.45 |
| 13 | **Noise-model inputs unsourced.** 0.1 %·σ Gaussian camera noise and 1 % phase-unwrapping error probability are asserted, not referenced. | **Medium** | 0.50 |
| 14 | **Roadmap feasibility overstated.** "100× noise reduction" via cooled sCMOS (~10× read-noise gain) + averaging needs ~10⁴ frames; "noise reduction expands equivalence more than NA or λ" is a simulation statement about one specific noise model. | **Medium** | 0.45 |
| 15 | **f_cross = 311 ± 173 mm⁻¹** (±56 % scatter) is reported in the abstract as a crisp crossover; should be qualified as highly variable across the ensemble. | **Medium** | 0.40 |
| 16 | **H_stylus ∝ f^-1.52 "effective filter order"** — a Gaussian has no order; the fitted slope depends on the fitting window. Terminology risk. | **Low** | 0.35 |
| 17 | **"Ergodicity" wording** for the periodogram (only stationarity + windowing matter for consistency). | **Low** | 0.25 |
| 18 | **GUM bands ±1.2/±0.9 dB** computed from assumed parameter tolerances (±100 nm tip, ±0.01 NA) without sources. | **Low-Medium** | 0.35 |
| 19 | **Computational-only.** The strongest single acceptance risk for I&M-flavoured journals; STMP/MST tolerate it better but reviewers will still ask for at least one literature benchmark against a measured ITF. | **High** | 0.85 (as a criticism) |

## PHASE 2 — NOVELTY AUDIT

Risky claims and conservative rewrites (preserving scientific value):

1. "**A new measurement limit**" (SNR-dependent resolution–bandwidth trade-off) →
   "a metrological formulation of the SNR-dependent resolution–bandwidth bound; we quantify it for two modalities" (drop "new"; cite classical sources).
2. "**No prior work has applied information theory to the comparison of fundamentally different surface measurement modalities**" →
   "To the best of my knowledge, a systematic Shannon-theoretic comparison of fundamentally different surface measurement modalities has not been reported" (add "systematic", drop absoluteness).
3. "**No closed-form mutual information between surface and measurement has been derived for any profilometry modality**" →
   Delete or rephrase as "the Gaussian-channel mutual information expression has not previously been applied to compare profilometry modalities" (otherwise a reviewer simply points at Cover & Thomas, p. 274).
4. "**This is the first empirically validated scaling law connecting instrument cutoff frequencies to cross-modality accuracy ratios**" →
   "to the best of my knowledge, the first" + "simulation-consistent" instead of "empirically validated" (no experiments exist).
5. "**The anisotropy tensor A_ij is ... the first quantitative measure of measurement-system anisotropy in surface metrology**" →
   "to the best of my knowledge" + acknowledge directional 2D-PSD anisotropy analyses in the contact-mechanics literature.
6. "**the reconstructability index ρ and Ξ are conceptually new**" → keep, but explicitly note ρ ≡ R² of the linear-Gaussian estimator (already stated; keep) and that novelty is the metrological interpretation.
7. "**Universal**" applied to ρ/η (CV<0.3 on six *simulated* classes) → "instrument-dominated in our six simulated classes"; reserve "universal" for a claim about real surfaces which does not exist yet.
8. Title claim "Closing the Accuracy Gap" is aspirational — acceptable, but the abstract must not promise closure (it does not; fine).

## PHASE 3 — ASSUMPTION AUDIT

| Assumption | Stated? | Justified? | Limits what? | Recommended action |
|------------|---------|-----------|--------------|--------------------|
| Linearity of stylus operator (small-slope Gaussian approximation) | Yes, with validity-boundary subsection | Boundary sentence inverted (§1 #3) | H_stylus; nonlinear dilation regime | Fix sentence; state σ/r_tip≪1 as the validity criterion |
| Additive Gaussian noise (both modalities) | Yes | Poisson test reported (3.6 %) but unwrap-error model unsourced | SNR formulation, MMSE, capacity | Cite or justify 0.1 %·σ and 1 % unwrap rates |
| Stationarity/self-affinity (H=0.7, roll-off 10 µm) | Yes | Wear-scar test reported | All PSD results | Fine; state that single-surface ergodicity is assumed |
| Ergodic representation by one realisation | Yes | Not really | ensemble claims | Reword to stationarity-based consistency |
| Scalar, incoherent, aberration-free OTF; WLI | Yes | Variant test (Maréchal etc.) reported | H_optical | Fine (invariance shown) — but see cutoff convention #1 |
| Morphological dilation vs true tip contact mechanics | Partially (SI Hertz) | SI adds plastic regime; main text ignores | Stylus H at low f | One sentence cross-ref to SI |
| Sampling: raster grid, sinc model | Yes | Grid convergence reported | high-f band | Fine |
| Ideal Rayleigh–Rice scatterometry, smooth opaque surface | Yes (SI) | Yes | scatterometry band | Fine |
| Gaussian surface channel for MI/MMSE/capacity | Yes | Non-Gaussian caveat given | info-theory quantities | Fine |
| Implicit: optical instrument is "true" WLI (not PSI/coherent) | Yes (CTF caveat exists) | Yes | generality | Fine |

## PHASE 4 — ROBUSTNESS AUDIT

- Six classes, 180-pt sweep, 432-pt roadmap, grid study, noise-model variants, OTF variants: **present and mostly sufficient**.
- **Missing (minimum necessary):** (a) convergence of the *headline* 18.3 % equivalence fraction with grid size (currently only stylus RMSE is reported converged); (b) one robustness statement for the equivalence fraction vs unwrap-error probability (the optical-dominant results hinge on it); (c) confirm 0.46–0.48 vs 18.3 % discrepancy (may already be a variant test on a different definition — must be labelled). No new physics needed; these are re-analyses of existing runs.
- Not needed: new surface classes, 2D unwrapping implementation, experimental data.

## PHASE 5 — REPRODUCIBILITY AUDIT

Present: baseline parameters (512², 100 µm, H=0.7, σ=50 nm, r_tip=2 µm, Δx=200 nm, NA=0.55, λ=550 nm), sweep dimensions, grid study, seeds "fixed" (value **not given**), code availability statement, pipeline README mention.
Missing (all cheap):
1. Random-seed value(s) for the baseline and sweep.
2. Software versions (Python, NumPy, SciPy, Matplotlib) — add to SI.
3. A consolidated baseline parameter table in the main text (currently scattered).
4. Definition of every "cutoff frequency" (criterion: 3 dB? threshold? NA/λ convention) — fixes #1 and #10 at once.
5. Noise floor estimation: threshold stated (0.8 f_max) ✓ but the Tikhonov regularisation parameter is not given.
6. IOP data policy: "available upon request" is weak; deposit pipeline on Zenodo/Figshare and cite the DOI (IOP requires a data availability statement; code is requested by funders).

## PHASE 6 — FALSIFIABILITY AUDIT

| Prediction | Falsification pathway | Status |
|-----------|----------------------|--------|
| H_stylus, H_optical from first principles | Measure with binary pseudo-random gratings (Yashchuk, cited) → compare within 3 dB | ✅ explicit |
| Equivalence fraction 18.3 % → 87 % under 4 conditions | Repeat roadmap conditions on a real instrument pair | ✅ explicit |
| ρ instrument-dominated (CV small) | n≥10 per class on real manufactured surfaces | ✅ explicit (SI S5) |
| Scatterometry bandwidth/inversion factor 2 | Super-polished Si wafer test | ✅ explicit |
| Trilemma F(SNR̄) | **None given** — capacity is not directly measurable | ⚠️ add one sentence: F is inferable from measured H, S_η, and the water-filling σ², hence testable in principle |
| Ξ = C/κ benchmarking | Indirectly via two real instruments | ⚠️ add sentence |
| SNR uncertainty bound | Compare computed vs measured Δx·Δf products on real instruments | ⚠️ add sentence |

## PHASE 7 — PRACTICAL IMPACT AUDIT

- H(f), Ω_eq, f_cross, ρ, roadmap: strong physical + engineering + metrological meaning; measurable. ✅
- I(f) "information loss": physical meaning clear (PSD ratio, decades) but name collides with Shannon I; rename risk low, but add "(PSD-ratio diagnostic, not a Shannon measure)".
- Anisotropy tensor A_ij, α: interpretable (directional bias), measurable. ✅
- I(h;y), C, ι(f), B_eq, η, ε: interpretable; direct measurement only via estimated H+S_η. Add one sentence on measurement pathway each (cheap).
- Ξ, κ(O): interpretable for instrument qualification; add one worked example sentence (already in practitioner's table). ✅
- Trilemma: least practically meaningful — keep but present as an organising relation, not a "limit".

## PHASE 8 — JOURNAL FIT

| Journal | Scope fit | Novelty | Significance | Rigor | Clarity | Desk reject | Major rev | Minor rev | Accept |
|---------|-----------|---------|--------------|-------|---------|-------------|-----------|-----------|--------|
| STMP (IOP) | 95 % | high | high | medium-high (fixes needed) | medium-high | 15–20 % | 50 % | 20 % | 10–15 % |
| MST (IOP) | 90 % | high | high | medium-high | medium-high | 15–20 % | 50 % | 20 % | 10–15 % |
| IEEE TIM | 85 % | medium-high | medium-high (no experiment hurts more) | medium | medium | 25–30 % | 50 % | 12 % | 8 % |
| Precision Engineering | 90 % | high | medium-high | medium-high | medium | 20 % | 55 % | 15 % | 10 % |
| OLE | 75 % | medium | medium | medium | medium | 30 % | 55 % | 10 % | 5 % |

Reasoning: STMP and MST are the best fits (measurement methodology + surface topography). The manuscript's scope statement, single-anonymous author choice, free subscription route, and IOP length-justification policy all align. The dominant acceptance lever is NOT journal choice but the Critical/High inconsistencies of Phase 1. With those fixed, accept-after-minor becomes realistic at STMP/MST.

## PHASE 9 — REVIEWER SIMULATION

**Reviewer 1 — Surface metrology.** Major: (a) no experimental validation of H(f); (b) equivalence fraction 0.46–0.48 vs 18.3 % contradiction; (c) stylus cutoff 159 mm⁻¹ and NA/λ convention undefined; (d) ρ saturation for deterministic surfaces undermines "instrument-limited" universality; (e) ensemble n=110 vs 120. Minor: naming of I(f); "filter order" of Gaussian; alignment of 136.8°. Recommendation: **Major Revision**.

**Reviewer 2 — Optical physics.** Major: (a) incoherent OTF cutoff is 2NA/λ, manuscript uses NA/λ everywhere — factor-of-2 error in a headline parameter; (b) unwrap-error and camera-noise models unsourced; (c) roadmap 100× noise reduction feasibility; (d) scalar vs vector treatment at NA=0.55 (SI covers it — must be cross-referenced in main text). Minor: "coherent CTF binary" simplification; Q-factor stability claim. Recommendation: **Major Revision** (bordering reject unless (a) is fixed before review).

**Reviewer 3 — Information theory/signal processing.** Major: (a) SNR-generalised uncertainty bound presented as new — likely prior art; (b) MI expression is textbook; novelty must be the cross-modality comparison, not the formula; (c) MIR=1.28 vs I_o/I_s=1.71 contradiction unexplained; (d) I(f) misnamed as information loss; (e) trilemma/capacity falsifiability absent. Minor: water-filling mode counts are grid artefacts (acknowledged — good); κ(O) condition number undefined if Gramian rank-deficient. Recommendation: **Major Revision**.

Consensus: **Major Revision**, driven almost entirely by avoidable internal inconsistencies and overclaiming — precisely the items a one-week edit can eliminate.

## PHASE 10 — FINAL ACTION PLAN (ranked Top-20, highest acceptance gain first)

Format: # / action / Sci-impact / Rev-impact / difficulty / time / acceptance-gain (H/M/L).

1. Fix factor-of-2 cutoff convention (state f_c = 2NA/λ for incoherent; or explicitly define NA/λ as the coherent reference) — Low/ **Very High** / Trivial / 0.5 d / **H**
2. Reconcile equivalence 0.46–0.48 vs 18.3 % (define metric per test, or correct the variant values) — Low / **Very High** / Trivial / 0.5 d / **H**
3. Repair inverted linearity-boundary sentence (σ/r_tip small = linear) — Medium / **High** / Trivial / 0.5 d / **H**
4. Add a reconciliation paragraph: MIR (correlation proxy) vs Shannon MI give opposite rankings because they weight modes differently — Low / **High** / Easy / 2 h / **H**
5. Soften Phase-2 novelty claims (uncertainty bound, MI derivation, "first validated") — Low / **High** / Easy / 2 h / **H**
6. Replace "validates" with "is consistent with" for R²=0.53; report CI on exponent — Low / **High** / Easy / 1 h / **H**
7. Unify ρ CV numbers (0.22 four-class vs 0.16 random-class) with an explicit definition of the class set — Low / Medium-High / Easy / 1 h / **H**
8. Update cover letter (SI 14→18 pages; state single-anonymous choice; IOP data policy) — Low / Medium / Trivial / 0.5 h / **M**
9. Justify 0.1 %·σ noise and 1 % unwrap-error rates (references or explicit sensitivity statement) — Low / Medium / Easy / 2 h / **M**
10. State seed value(s), software versions, and one consolidated baseline parameter table — Low / Medium / Easy / 2 h / **M**
11. Define every cutoff frequency criterion (fixes 159 mm⁻¹ mystery) — Low / Medium / Easy / 1 h / **M**
12. Qualify f_cross = 311±173 mm⁻¹ language in abstract — Low / Medium / Trivial / 0.5 h / **M**
13. Remove/qualify "θ≈136.8° aligned with scan direction" (near-degenerate tensor) — Low / Medium / Trivial / 0.5 h / **M**
14. Reconcile n=110 vs 120 ensemble count — Low / Medium / Trivial / 0.5 h / **M**
15. Soften roadmap feasibility wording (100× = sensor + averaging; state frame-count) — Low / Medium / Easy / 1 h / **M**
16. Add falsifiability sentences for trilemma, Ξ, SNR bound — Low / Medium / Easy / 1 h / **M**
17. Rename/annotate I(f) as PSD-ratio diagnostic — Low / Medium / Trivial / 0.5 h / **M**
18. Grid-convergence of the 18.3 % headline (re-run existing grid study, one figure) — Low / Medium / Easy / 0.5 d / **M**
19. Deposit pipeline on Zenodo; update Data Availability with DOI — Medium / Medium / Easy / 0.5 d / **M**
20. One literature benchmark: overlay a published measured ITF (e.g., Foreman 2013 curve or Yashchuk data) on computed H(f) — Medium / **High** / Moderate / 2–3 d / **M** (largest single acceptance lever left after edits)

Bottom line: items 1–17 are pure text edits within a week; they convert the simulated consensus from Major Revision into at least Minor Revision at STMP/MST, and remove the factor-of-2 and internal-contradiction flags that could otherwise trigger desk rejection at an optics-heavy panel.
