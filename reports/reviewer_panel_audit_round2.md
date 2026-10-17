# Senior Associate Editor & Reviewer Panel — Round 2 (post-revision state)

Date: 2026-10-17. Manuscript state: 60 pp + 19 pp SI + 3 pp cover letter, all Round-1 panel fixes applied (H convention, regenerated ensemble, Gramian aligned with code, SNR-bound status clarified, variants added, passive voice, no technical script references). This audit identifies only the weaknesses that remain after those fixes. Probabilities are panel judgement, not measured statistics. The scientific framework is assumed complete; no new mathematics is proposed.

---

## PHASE 1 — TECHNICAL AUDIT (hostile Q1 reviewer)

### Verified during this audit

- Limitations \S"Grid convergence" states the equivalence fraction is 0.52/0.45/0.30/0.21 for N=128/256/512/1024, while the current, code-regenerated n=30 ensemble at N=512 gives **9.6%±0.3%** — a direct internal contradiction at the N=512 point (0.30 vs 0.096).
- SI \S2 complementarity item still cites "$f_\mathrm{cross} \approx \SI{311}{mm^{-1}}$" (current value: 454).
- $\Pi = \num{7.4e9}$ and "similarly valued $\Pi$ ... reflecting the comparable anisotropy levels" are stale: with the regenerated $\alpha$ (stylus ≈7× optical) and $L_s = 2.76\times10^{12}$ vs $L_o = 1.35\times10^{12}$, the products differ by ≈30×, not "similarly valued".
- The Δx-sweep sentence claims RMSE changes "less than 20%": the values 13.6/16.3/16.7 nm span 22.8%.
- Eq. factorisation includes an undefined factor $H_\mathrm{noise}(f_x,f_y)$; noise is additive in Eq. operator, not multiplicative.
- $B_\mathrm{eq}$ (information-equivalent bandwidth) and $\eta$ (information efficiency) are named in the Research-Gap paragraph and Practitioner table but are **never defined anywhere in the main text** (ε has a table definition; B_eq and η do not).
- Conclusions item 4 and the fig4 caption still use "stylus cutoff" where the current text elsewhere calls it a "conventional tip-radius scale".
- The practitioner table retains the stale symbol $\kappa(O)$ (the Gramian was replaced by max/min condition number).
- `grid_convergence.json` and `gap_closure_sweep.json` have reader scripts only; no generator script is committed for either.

### Remaining weakness inventory

| # | Weakness | Severity | P(reviewer finds it) |
|---|----------|----------|----------------------|
| R1 | **Grid-convergence numbers contradict the regenerated ensemble** (0.30 vs 0.096 at N=512). A referee cross-checking the Limitations against the Results will find a quantitative contradiction. | **Critical** | 0.6 |
| R2 | **$\Pi$ paragraph is numerically stale and self-contradictory** ("similarly valued" vs the ≈30× ratio implied by the updated $\alpha$ and $L$ values). | High | 0.5 |
| R3 | **$B_\mathrm{eq}$, $\eta$ named but undefined**; "included for completeness" with no definition invites the referee to demand either definitions or removal. | Medium | 0.5 |
| R4 | **Stale notation/wording cluster**: $\kappa(O)$, "stylus cutoff" in Conclusions/figure captions, SI "311 mm⁻¹". Cheap but visible. | Medium | 0.4 |
| R5 | **Δx "less than 20%" arithmetic** (22.8% actual). Trivial, but a careful referee computes it. | Low | 0.25 |
| R6 | **$H_\mathrm{noise}$ in the factorisation equation is undefined** (multiplicative noise factor vs additive η). | Medium | 0.4 |
| R7 | **Single-run (n=1) numbers in the information-loss section** (L_s, L_o, per-band table, MIR proxy) while the rest of the paper now reports n=30 ensemble statistics. | Medium | 0.35 |
| R8 | **$I(f)\propto f^{0.01}$ is not verified by any committed test** (unlike every other headline exponent). | Low | 0.2 |
| R9 | **Grid-convergence and gap-closure data have no generator scripts** (reproducibility hole for those two studies). | Medium | 0.3 |
| R10 | **Bound prominence vs "ansatz" status**: fully transparent now, but a referee may still object to a definitionally anchored bound occupying the headline position (abstract + cover-letter item 1). | Medium | 0.5 |
| R11 | Computational-only study; length 60 pp. | High | 1.0 (comment) / 0.3 (desk) |
| R12 | Fisher spectrum (fig8) rests on a crude noise-floor estimator (median of difference-field PSD); labelled as amplitude-convention but the noise model is not stated in the caption. | Low | 0.2 |
| R13 | Cover letter says "single-anonymous" and cites Section 4.6 for the roadmap — section numbering may shift after edits; verify. | Low | 0.1 |

---

## PHASE 2 — NOVELTY AUDIT

| Claim | Verdict |
|---|---|
| "no prior work has systematically applied information theory to the comparison of fundamentally different surface measurement modalities" | Qualified + search-basis footnote now present. Keep. |
| "first simulation-derived scaling law connecting instrument cutoff frequencies to cross-modality accuracy ratios" | Qualified. Keep. |
| "first quantitative measure of measurement-system anisotropy" | Qualified; Takacs cited as adjacent. Keep. |
| "$\rho$ and $\Xi$ conceptually new in the surface metrology context" | ρ acknowledged as R²-equivalent; Ξ defensible. Keep. |
| "no widely adopted $k$-space framework currently quantifies..." | Softened. Keep. |
| SI "Status of the bound": factor is "the unique first-order noise inflation consistent with (i)–(ii)" | Defensible interpolation claim; keep, but soften "unique" to "the natural first-order" if challenged. |
| "Universal metrics" in SI stress test | Supported by CVs with caveats. Keep. |

No further novelty rewrites required. Only R10 (prominence vs status of the bound) touches novelty framing, and it is already transparent.

---

## PHASE 3 — ASSUMPTION AUDIT

All assumptions from Round 1 remain adequately stated, plus the new ones added (monochromatic mean-λ, polychromatic variant, Δx sweep). Two new items:

1. **Implicit: noise factorises multiplicatively (Eq. factorisation)** — contradicts the additive-noise model. Fix: rewrite the factorisation as aperture × sampling, with noise additive as in Eq. operator (kills R6).
2. **Implicit: information-loss diagnostics are representative of the ensemble** — the section reports n=1 values while the paper now claims ensemble-level statistics elsewhere. Fix: either quote ensemble mean ± std (one extension of the existing ensemble runner) or add an explicit "single representative realisation" qualifier (kills R7).

---

## PHASE 4 — ROBUSTNESS AUDIT

Covered after Round 1: six surface classes, OTF variants (aberrations, Gaussian, polychromatic), tip-shape invariance, Δx = 100/200/400 nm, Gaussian vs Poisson noise, stationarity, non-Gaussian ensembles, public-data benchmark, out-of-sample scaling check.

Minimum additional work (nothing more):

1. **Re-run the four-grid convergence study with the current code** (N = 128, 256, 512, 1024; 4 sims, minutes each) and replace the Limitations numbers with current values. This simultaneously fixes R1 and R9 (generator script committed).
2. **Extend the ensemble runner** with the two information-loss scalars (MI correlation proxy per seed; per-band loss) and quote mean ± std in the Results table (fixes R7; 30 sims, reuses existing runner).

No other simulations are required.

---

## PHASE 5 — REPRODUCIBILITY AUDIT

Strong: seeds (42/123/100–129), pinned dependencies + h5py dev pin, ensemble runner, variant script, benchmark with SHA-256, sweep parameter table, 14/14 tests.

Remaining gaps:
1. Grid-convergence study has no regenerating script (R9) — the committed numbers conflict with the current pipeline anyway (R1).
2. Gap-closure 432-point sweep generator not committed (only the roadmap figure reader).
3. The verification suite is mentioned in the text but not described in the SI; add one sentence in the SI or Data Availability ("a 14-test verification suite accompanies the repository").

---

## PHASE 6 — FALSIFIABILITY AUDIT

Falsification protocols now exist for: the SNR bound (operational definitions + measurement protocol), the scaling law (exponent outside 1.9±0.3), the roadmap (equivalence-fraction targets), and γ (larger-n test recommended — one clause to add). All theoretical quantities thus have at least one falsification pathway. No changes required beyond the optional γ clause.

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

- **Π (anisotropy-loss product)** — weakest quantity: numerically stale (R2) and its practical reading ("trade-off between isotropy and fidelity") is thinner than ρ, Ξ, or the decision table. Options: recompute honestly with the regenerated α and state the ≈30× modality difference, or fold it into the anisotropy paragraph without a dedicated number. Recommended: recompute and reword (one line).
- **$B_\mathrm{eq}$, $\eta$** — currently have no operational definition; a practitioner cannot compute them (R3). Either add one-line definitions or delete from the table/paragraph.
- All other quantities (H, I(f), α, ρ, Ξ, ι, water-filling, MMSE) retain full physical/engineering/metrological interpretations and measurement pathways.

---

## PHASE 8 — JOURNAL FIT

Post-Round-1 estimates (panel judgement):

**STMP** — Scope fit 90% · Novelty 65% · Significance 70% · Rigor 80% (→88% after the R1–R5 fixes) · Clarity 90%
- Desk rejection: **15–20%** (length and computational-only are the residual drivers)
- Major revision: 35–40% · Minor revision: 20–25% · Acceptance after revision: **65–75%**

**MST** — Scope fit 80%, similar profile; viable fallback; the information-theoretic sections carry slightly more weight there.

The single most damaging remaining item is R1 (the internal grid contradiction): reviewers who cross-check will read it as a quality-control failure. R2 and R4 are the next most visible.

---

## PHASE 9 — REVIEWER SIMULATION

### Reviewer 1 — Surface metrology

**Major.** (1) The equivalence fraction claimed in the grid-convergence study (0.30 at N=512) contradicts the ensemble value (9.6%): which is correct? (2) The anisotropy-loss product values appear inconsistent with the reported α and L. (3) The information-loss tables are single-realisation while the paper now reports ensembles elsewhere.
**Minor.** "Stylus cutoff" wording vs the definitional tip-radius scale; fig4 caption; Δx percentage arithmetic.
**Recommendation:** Major revision.

### Reviewer 2 — Optical physics

**Major.** (1) The factorisation equation lists a noise factor that is never defined and contradicts the additive noise model. (2) The Fisher/CRB figure should state its noise-floor estimator in the caption. (3) The grid-convergence claim about the equivalence fraction deserves regeneration with the current optical model (which now includes the corrected transfer convention).
**Minor.** Polychromatic and Δx variants are appreciated; cite the variant values in the SI as well.
**Recommendation:** Minor-to-Major revision.

### Reviewer 3 — Information theory / signal processing

**Major.** (1) $B_\mathrm{eq}$ and $\eta$ are named as diagnostics but never defined — define or remove. (2) The bound's ansatz status is acknowledged; the abstract and cover letter should reflect the same status ("metrological form" not "limit"). (3) The MI proxy and per-band losses are n=1; report ensemble spread.
**Minor.** κ(O) notation is stale.
**Recommendation:** Major revision.

**Panel aggregate:** one clear Major, two leaning Major; first-round outcome most likely **Major Revision** driven by R1/R2/R3/R7 — all fixable pre-submission in under one day.

---

## PHASE 10 — FINAL ACTION PLAN (ranked Top-20)

Estimates: Sci (1–5), Rev (1–5), Diff (1–5), Time (h), Gain (0–5).

| # | Action | Sci | Rev | Diff | Time | Gain |
|---|--------|-----|-----|------|------|------|
| 1 | Re-run 4-grid convergence study with current code; replace Limitations numbers; commit generator. | 4 | 5 | 2 | 1.5 h + 4 sims | +5 |
| 2 | Recompute Π with regenerated α/L; reword "similarly valued" honestly (≈30× modality difference). | 2 | 4 | 1 | 0.5 h | +3 |
| 3 | Define or delete $B_\mathrm{eq}$ and $\eta$ (one-line definitions; delete otherwise). | 2 | 4 | 1 | 0.5 h | +3 |
| 4 | Consistency sweep: κ(O)→κ, "stylus cutoff"→"tip-radius scale" (Conclusions, fig4 caption), SI 311→454 mm⁻¹. | 1 | 4 | 1 | 0.5 h | +3 |
| 5 | Extend ensemble runner with MI-proxy + per-band means/std; quote in Results. | 3 | 3 | 2 | 1 h + 0.5 h run | +2.5 |
| 6 | Fix factorisation equation (drop $H_\mathrm{noise}$; noise additive). | 2 | 3 | 1 | 0.25 h | +2 |
| 7 | Fix "less than 20%" → "less than 25%" (13.6–16.7 nm). | 1 | 2 | 1 | 0.1 h | +1 |
| 8 | Abstract/cover-letter wording: "metrological form" of the bound (align with SI status paragraph). | 1 | 3 | 1 | 0.25 h | +1.5 |
| 9 | Add $I(f)\propto f^{0.01}$ slope verification to the test suite. | 2 | 2 | 1 | 0.5 h | +1 |
| 10 | Commit gap-closure sweep generator (or document it as fixed-config output). | 2 | 2 | 2 | 1 h | +1 |
| 11 | One SI sentence describing the 14-test verification suite. | 1 | 2 | 1 | 0.25 h | +1 |
| 12 | fig8 caption: state the noise-floor estimator. | 1 | 2 | 1 | 0.1 h | +0.5 |
| 13 | γ clause: "testable at larger n". | 1 | 1 | 1 | 0.1 h | +0.5 |
| 14 | Cover letter: verify section cross-reference numbering after edits. | 1 | 1 | 1 | 0.1 h | +0.5 |
| 15 | SI: cite variant values (Δx, polychromatic) explicitly. | 1 | 2 | 1 | 0.25 h | +0.5 |
| 16 | Practitioner table: clarify ε definition placement (currently table-only). | 1 | 2 | 1 | 0.1 h | +0.5 |
| 17 | "Unique first-order" → "natural first-order" in SI bound status (pre-empt nitpick). | 1 | 2 | 1 | 0.1 h | +0.5 |
| 18 | Recompile all three PDFs; re-run 14/14 tests; commit. | 1 | 2 | 1 | 0.5 h | +2 |
| 19 | Optional trim of 2–3 pp (desk-risk reduction only). | 1 | 2 | 3 | 3 h | +1 |
| 20 | Optional: one-line acknowledgement that the verification suite is available on request. | 1 | 1 | 1 | 0.1 h | +0.5 |

**Conclusion.** Actions 1–8 (≈ half a day, no new mathematics, no new experiments beyond four short grid sims and one ensemble-rerun extension) remove every remaining Critical/High finding and most Medium findings. Expected effect: the residual first-round decision shifts from likely Major Revision toward Minor Revision / Accept-with-minor-changes.
