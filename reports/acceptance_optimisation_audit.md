# Hostile Panel Audit — Acceptance Optimisation (Round 6, Final)

**Documents audited:** `elsarticle/manuscript.tex` (main, 62 pp), `elsarticle/manuscript_supplementary.tex` (SI, 22 pp), `IMEKO_2027/class_iwc2027_v2/imeko-wc-extended-abstract.tex` (4 pp).
**Date:** 2026-10-21 · **Status before this round:** READY (5 prior panel rounds; 18/18 tests; clean builds).
**Scope discipline:** no new mathematics, no new simulations beyond trivially-free text fixes; do not lengthen the paper.

---

## PHASE 1 — TECHNICAL AUDIT (hostile Q1 reviewer)

### Genuinely new findings of this round (not previously fixed)

**A1. Unit error in the information-loss slope range — HIGH, P(reviewer notices) ≈ 0.6.**
Results §Spectral Information Loss states the local log–log slope is `≈ 0.4 over 0.05–1.5 mm⁻¹`. Frequencies in this study span ≈17–2000 mm⁻¹; "0.05–1.5 mm⁻¹" is below the first resolved mode and is physically nonsensical. The IMEKO abstract states the same slope over 50–1500 mm⁻¹ (correct). This is a plain unit/decade slip in the manuscript. Fix: `50–1500 mm⁻¹`.

**A2. Internal contradiction in the gap-closure residual argument — HIGH, P ≈ 0.5.**
Roadmap: the residual 13% of k-space "is where the stylus transfer function is H ≈ 1.0 while the optical OTF … is H < 1.0 due to the fundamental arccos shape". Two problems: (i) the paper's own Fig./Results give H_stylus ≈ 2.2 at 17 mm⁻¹, not ≈1.0; (ii) the incoherent OTF at f < 20 mm⁻¹ with cutoff 2000 mm⁻¹ is 1 − 2f̃/π ≈ 0.994 (≈ −0.06 dB), far below the 3 dB criterion — the OTF shape cannot explain a 3 dB-level residual gap at low f. The dominant low-frequency effect is the stylus curvature-bias **excess** (+3.4 dB), which is a correctable bias, not the optical low-pass character. Fix: attribute the residual gap to the stylus curvature-bias excess (and note that bias subtraction would shrink it), not to the OTF being low-pass.

**A3. Confocal/focus-variation transfer statement is wrong as written — HIGH, P ≈ 0.5.**
Limitations: "Focus-variation microscopy and confocal microscopy share the same diffraction-limited incoherent OTF structure as WLI, differing only in their axial sectioning mechanisms". Confocal lateral imaging has the **product** of illumination and detection apertures (OTF support to 4NA/λ for point detection) — a fundamentally different, steeper lateral transfer. A knowledgeable reviewer will flag this. Fix: one clause — confocal has a steeper lateral transfer (product of two apertures), focus-variation shares the broad incoherent-OTF envelope; the modality-catalogue claim then survives.

**A4. SI internal inconsistency: ground-class ρ — HIGH, P ≈ 0.45.**
SI §S3: "ρ … varying only from 0.79 (biological) to 0.82 (Gaussian self-affine, ground)". SI §S5 Table: ground ρ = 0.5890 ± 0.0104 (n = 20). Same named class, two orders of standard error apart. The manuscript itself is consistent (quotes 0.59–0.82, CV = 0.16), but the SI contradicts itself. Fix: one sentence in §S3 noting that the n = 5 six-class ground realisation (milder anisotropy/amplitude) differs from the n = 20 non-Gaussian ground ensemble of §S5, and that 0.589–0.82 is the true class-to-class spread the main text already reports.

**A5. Trilemma is close to a tautology — MEDIUM–HIGH, P ≈ 0.5 (Reviewer 3).**
Eq. (trilemma) `I·Δx² ≈ σ²·F(SNR)` with F ∝ A/(2σ²) makes the RHS independent of σ² — the "energy" cancels, as the text itself admits ("the surface variance cancels"). A hostile information-theorist will call it a rearrangement of the flat-channel approximation rather than a trade-off. No new work needed: demote the framing in two sentences ("the trilemma reduces to the flat-channel capacity estimate; the σ² cancellation shows …"). The bound it is built on is already honestly framed as an ansatz.

**A6. Audit-language leaks into the scientific text — MEDIUM, P ≈ 0.7 (at least one reviewer remarks on it).**
"verified independently in the accompanying verification suite" (Methods), "see the sweep audit above" (Discussion), "verified independently" (Results, information-loss slope), "checked by eighteen automated verification tests" is fine in Data Availability but not in results prose. Fix: replace with neutral phrasing ("cross-checked by the verification suite", "see the sweep statistics in §…"), move test references to the Data Availability paragraph.

**A7. Protocol band mismatch across documents — LOW–MEDIUM, P ≈ 0.3.**
Manuscript protocol: average in λ ≈ 1.5–3.5 µm; IMEKO applications: 1.5–2 µm; crossover point: 2.2 µm (454 mm⁻¹). Within one document each is defensible, but harmonising to one consistent crossover band (±1σ around 2.2 µm, i.e. ≈1.4–4.8 µm, or the stated 1.5–2 µm) removes a gratuitous inconsistency.

**A8. Baseline stylus noise is unrealistically low — MEDIUM (pre-empted but still visible), P ≈ 0.5.**
Stylus noise 0.1% of σ = 0.05 nm versus SI's own "realistic base noise 0.5–1.0 nm". The text pre-empts (robustness statement), but a reviewer will still ask why the headline baseline isn't at realistic noise. Optional zero-simulation fix: state explicitly in Methods that the conclusions are invariant between 0.05 and 1 nm stylus noise (the robustness analysis already computed this).

**A9. "First" claims have asymmetric support — MEDIUM, P ≈ 0.35.**
The information-theoretic "first" claim carries a search-basis footnote; the scaling-law and anisotropy-tensor "first" claims do not. Fix: extend the same footnote or soften both to "to the best of our knowledge, not previously reported".

**A10. Π = α·L is introduced and never used — LOW, P ≈ 0.3.**
One occurrence, no protocol. Either give it one sentence of use ("instrument acceptance screening: flag Π > …") or fold it into a remark. No new computation.

### Confirmed strengths (will not be criticised)
Mathematical rigour of MMSE/MI derivations; ansatz status of the resolution–bandwidth bound (honestly flagged in both main text and SI S4.3); estimator-dependence of total MI honestly reported with a withdrawn claim; public-data model check framed as description, not independent ITF measurement; Hertzian plastic-regime caveat; fusion explicitly illustrative; grid dependence of the equivalence fraction documented; seeds/versions/DOI in Data Availability; 18-test suite.

### Rankings (existing items, status after prior rounds)
- Equivalence fraction grid-dependence of the headline 9.6% — MEDIUM (documented; arbitrary but disclosed).
- "Order-of-magnitude descriptor" framing of the R² = 0.53 scaling law — LOW (appropriately downgraded).
- Scalar-OTF / monochromatic / coherence-envelope exclusions — LOW (each quantified as a variant or public-data check).
- Single-author study with no experiments — MEDIUM structural risk, mitigated by roadmap + public data; not fixable by text.

---

## PHASE 2 — NOVELTY AUDIT

| Claim | Verdict | Action |
|---|---|---|
| "first simulation-derived scaling law connecting instrument cutoff frequencies to cross-modality accuracy ratios" | Defensible, hedged, falsification window given | Add search footnote parity (A9) |
| "first quantitative measure of measurement-system anisotropy in surface metrology" | Defensible, hedged | Add footnote parity (A9) |
| "no prior work has systematically applied information theory to the comparison…" | Defensible, footnote with search basis present | None |
| "without precedent" (info-theory section) | Hedged | None |
| "universal metrics" (SI S3) | Bounded by CV thresholds; framed as categories, not a law | None |
| "refuting the classical Gaussian-tip picture" | Borderline — simulation contrasts two models; "refutes" invites the reply "the Gaussian model was never claimed for paraboloid tips". Soften to "shows that the Gaussian-tip idealisation underestimates the empirical transfer by two orders of magnitude" | 1-word-level fix |
| "explains why stylus and optical profilometry produce different measurements" (Conclusions) | Causal verb for an observational/computational study | Replace with "characterises how and when" (also consistent with project style rules) |

---

## PHASE 3 — ASSUMPTION AUDIT

Extracted assumptions and their current status:

| Assumption | Stated | Justified | Limiting? |
|---|---|---|---|
| Gaussian, stationary surface prior | Yes (channel section) | Baseline only; six classes tested | No |
| Ergodicity of the PSD estimator | Yes (Methods) | Hann-window periodogram, sensitivity 0.7–0.9 f_max for ρ | No |
| Small-slope linearity of dilation | Yes | σ/r_tip = 0.025 at boundary; σ sweep to 200 nm quantifies the nonlinear onset | At upper edge — disclosed |
| Scalar optics / monochromatic OTF | Yes | Vector correction ≈8% (SI 1.3); polychromatic variant within 3 dB over 96.5% | No |
| Additive Gaussian noise | Yes | Poisson comparison: 3.6% RMSE difference | No |
| Ideal paraboloid tip | Yes | Tip-geometry invariance paragraph (sphere, cone+cap, same small-slope structure) | No |
| 1D row unwrapping | Yes | Identified as dominant optical error; 2D unwrapping is roadmap item | Yes — disclosed |
| Coherence envelope excluded laterally | Yes | SI: envelope is axial; steep-slope drop-outs noted; 15% cutoff shift benchmarked | Qualitative only |
| Stationarity of noise (tail-based noise-floor estimate) | Implicit | Conservative by construction; threshold sensitivity tested | LOW — one sentence could state the white-noise assumption explicitly |
| Stylus noise = 0.05 nm baseline | Yes, flagged idealised | Robustness statement | A8 |

**Recommendation:** one added sentence on the noise-tail estimator assumption (white-noise tail). That is the only uncovered implicit assumption.

---

## PHASE 4 — ROBUSTNESS AUDIT

Coverage matrix — every headline conclusion vs. perturbation axes:

| Conclusion | Surface classes | Optical model variants | Tip geometry | Raster | Noise level | Verdict |
|---|---|---|---|---|---|---|
| H_stylus flat-with-bias | 6 classes | — | sphere/cone+cap same small-slope | 100–400 nm tested | robust | Robust |
| H_optical follows OTF | 6 classes | aberrated/Gaussian OTF CV=0.03 | — | — | robust | Robust |
| ρ stylus > ρ optical (baseline) | random classes 0.59–0.82 | CV 0.03 across OTFs | — | — | robust | Robust |
| f_cross weak tip dependence (r^-0.06) | — | — | — | — | — | Sweep-level |
| Scaling law exponent 1.90±0.13 | blocked + out-of-sample R² 0.51–0.52 | — | — | — | — | Adequate as descriptor |
| 87% roadmap | N=256 only | — | — | — | noise sweep central | Grid-caveated |
| Anisotropy ranking α_s > α_o | n=30 + n=180 sweep | — | — | — | — | Robust (definition-dependent) |

**Missing evidence that a reviewer may legitimately request (minimum only):** none that requires new simulations. The four-grid convergence, σ sweep, Poisson comparison, and OTF-variant tests cover the standard demand set. The only soft spot is the 87% roadmap being on N=256 — already disclosed; optionally restate the N=256 baseline (48%) next to the 87% number in the abstract-level materials (already done in IMEKO).

---

## PHASE 5 — REPRODUCIBILITY AUDIT

- Parameters: baseline table, sweep table, noise levels, unwrapping rate, seeds (42/123/100–129), grid sizes, software versions (Python 3.9, NumPy 2.0, SciPy 1.13, Matplotlib 3.9) — present.
- Numerical methods: periodogram with Hann window, Tikhonov at noise floor, azimuthal bins (100) — present.
- Convergence: four-grid study N=128–1024 — present.
- Code: public GitHub repository, release v1.0.2, Zenodo DOI 10.5281/zenodo.23493875; 18 automated tests; three audit scripts; figure scripts committed — present, best in class.
- Missing (minor): the Tikhonov regularisation parameter value is not quoted in text (recoverable from code). LOW.

**Verdict:** reproducibility will not trigger criticism. Do nothing.

---

## PHASE 6 — FALSIFIABILITY AUDIT

- Scaling law: "a measured exponent outside 1.9 ± 0.3 would falsify it" — explicit.
- Resolution–bandwidth bound: measurable PSF, transfer function, SNR; product below bound falsifies — explicit.
- Roadmap: four predictions with quantitative targets — explicit.
- Equivalence protocol: directly testable on any paired stylus/WLI dataset — explicit.
- ρ universality hypothesis: "varies by less than 20% across classes" with n ≥ 10 — explicit.

**Verdict:** strongest phase; no changes.

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

| Quantity | Physical | Engineering | Metrological | Measurable? |
|---|---|---|---|---|
| H(f) | ✓ | ✓ | ✓ | Yes (BPRA) |
| I(f) loss | ✓ | ✓ | ✓ | Yes (PSD ratio) |
| Ω_eq, f_cross | ✓ | ✓ (trust boundary) | ✓ | Yes |
| ρ | ✓ | ✓ | ✓ | Yes |
| α, A_ij | ✓ | ✓ | ✓ | Yes |
| Ξ | ✓ | ✓ | ✓ | Yes (needs reference class — stated) |
| Π = α·L | ✓ | ✗ | ✗ | — **A10** |
| Trilemma F | marginal | ✗ | ✗ | — **A5** |

**Verdict:** Π and the trilemma are the only quantities lacking practical anchoring; handle per A5/A10 with text-only demotion.

---

## PHASE 8 — JOURNAL FIT

| Criterion | STMP | MST |
|---|---|---|
| Scope fit | 95% (topography measurement, instrument physics, PSD) | 80% (instrument science yes; surface-specific) |
| Novelty | 70% | 65% |
| Scientific significance | 75% | 65% |
| Technical rigour | 85% | 85% |
| Clarity | 80% | 80% |
| Desk rejection | 5–8% | 15% |
| Major revision | 20–25% | 30% |
| Minor revision | 45–50% | 35% |
| Accept after revision | 70–75% | 50–55% |

Reasoning: single-author, purely computational study with no experiments is the dominant residual risk at STMP; the public-data model check, falsifiable roadmap, and the 18-test reproducibility suite are the strongest mitigators. IOP data policy is satisfied via the public repository + Zenodo DOI.

**IMEKO extended abstract:** scope fit ≈ 95%; acceptance probability high (~80–85% for a WC extended abstract with public-data validation and reproducibility assets), assuming the four-page format is respected (it is: 4 pages, clean build).

---

## PHASE 9 — REVIEWER SIMULATION

### Reviewer 1 — Surface metrology (stylus/areal)
**Major:** (i) baseline stylus noise 0.05 nm is not representative of commercial instruments — why not 0.5–1 nm as your own SI says? (ii) The low-frequency residual gap is attributed to the optical OTF, but your own H_stylus ≈ 2.2 at 17 mm⁻¹ shows the stylus bias dominates there — rework this argument. (iii) Ball-standard check is geometric only; the stylus transfer remains unvalidated against any measured stylus ITF.
**Minor:** protocol band (1.5–3.5 µm) vs crossover (2.2 µm) inconsistency; "refutes" too strong for a simulation contrast; Π unused.
**Recommendation:** Major Revision if (i)–(ii) unaddressed; Minor Revision after.

### Reviewer 2 — Optical physics
**Major:** the confocal "same OTF as WLI" statement is incorrect (product of two apertures). WLI OTF is partial-coherence dependent; the 15% cutoff shift attribution to the coherence envelope is asserted, not modelled.
**Minor:** scalar OTF at NA=0.55 (you quantified it — good); pixel/MTF exclusion fine.
**Recommendation:** Minor Revision after the confocal correction.

### Reviewer 3 — Information theory / signal processing
**Major:** the trilemma: σ² cancels, so it is a flat-channel rearrangement, not a trade-off — either prove a non-trivial inequality or demote it. "No algorithm can achieve lower MSE" — true only under your Gaussian-channel linearisation; make the linearised-benchmark status lead the sentence (you mostly do).
**Minor:** mutual-information estimator-dependence handled honestly; κ/Ξ definitions are fine; B_eq definitional.
**Recommendation:** Minor Revision after trilemma demotion.

Consensus: **Minor Revision** with the fixes in Phase 10; no rejection path visible if A1–A6 are fixed.

---

## PHASE 10 — FINAL ACTION PLAN (only high-gain, zero/low-effort items)

Estimated costs: all items are text edits ≤ 1 hour total; no new simulations, no new derivations, no length increase.

### Ranked Top-20 improvement roadmap

| # | Fix | Sci. impact | Reviewer impact | Difficulty | Time | Acceptance gain |
|---|---|---|---|---|---|---|
| 1 | A1 unit fix 0.05–1.5 mm⁻¹ → 50–1500 mm⁻¹ | Correctness | High | Trivial | 2 min | ++ |
| 2 | A2 residual-gap attribution → stylus bias excess | Logic | High | Small | 15 min | ++ |
| 3 | A3 confocal transfer clause | Correctness | High | Trivial | 5 min | ++ |
| 4 | A4 SI §S3/§S5 ground-ρ reconciliation sentence | Consistency | High | Small | 10 min | ++ |
| 5 | A5 trilemma demotion to flat-channel remark | Rigour | High | Small | 15 min | ++ |
| 6 | A6 remove audit-language ("verified independently", "sweep audit") | Polish | Medium | Small | 15 min | + |
| 7 | A7 harmonise crossover band (use 1.5–2 µm + cite 2.2 µm mean) | Consistency | Medium | Small | 10 min | + |
| 8 | A8 state noise-invariance 0.05→1 nm explicitly | Pre-emption | Medium | Trivial | 5 min | + |
| 9 | A9 footnote parity for "first" claims | Novelty defence | Medium | Trivial | 10 min | + |
| 10 | A10 Π: one sentence of use or demotion | Focus | Low-Med | Trivial | 5 min | + |
| 11 | Soften "refutes"/"explains" verbs | Tone | Medium | Trivial | 10 min | + |
| 12 | State white-noise assumption of the noise-tail estimator | Completeness | Low | Trivial | 5 min | + |
| 13 | Quote Tikhonov regularisation value in Methods | Reproducibility | Low | Trivial | 5 min | + |
| 14 | IMEKO: mirror fixes 1, 11 (units already correct there) | Consistency | Low | Trivial | 5 min | + |
| 15 | Cover letter: align "single-author study" and data sentence (already updated) — verify only | — | Low | — | 0 | — |
| 16 | Move "eighteen tests" sentence in IMEKO from results to repository sentence (already partly done) | — | Low | Trivial | 5 min | + |
| 17 | Do NOT add new metrics/simulations | — | — | — | — | — |
| 18 | Do NOT expand SI | — | — | — | — | — |
| 19 | Rebuild all PDFs + 18/18 tests + commit (after 1–14) | — | — | Small | 30 min | — |
| 20 | Stop. Current READY state is already submission-grade; items 1–5 alone shift the three simulated reviews from Major→Minor | — | — | — | — | — |

### Bottom line
The manuscript is already in a defensible state. **Items 1–5 are factual/logical corrections that a hostile reviewer can find by reading, and each costs minutes.** Applying them (plus the cheap 6–14) converts the most likely panel outcome from "Minor Revision" to "Accept/Minor with cosmetic comments", and meaningfully lowers the ~20–25% Major-Revision probability. No new science, no new simulations, no length increase. Recommend: apply 1–14, rebuild, re-verify, commit; then stop.
