# Reviewer Panel Audit — Round 4 (post science-audit)

Date: 2026-10-18. Manuscript: "Optical Profilometry Versus the Stylus: A Spectral Theory for Closing the Accuracy Gap" (62 pp + 21 pp SI + 3 pp cover letter). State: branch `audit-science` @ bc56f03; 18/18 tests pass; builds 0 errors, 0 undefined.

All probability estimates are editorial judgement, not measured statistics. The scientific framework is assumed complete. Round 4 differs from Rounds 1–3 in kind: the reproducibility and internal-consistency defects were eliminated by the science audit, so what remains is almost entirely **inherent scope** plus a small set of **residual wording inconsistencies introduced or left by earlier rounds**.

---

## PHASE 1 — TECHNICAL AUDIT

### Critical
None. Every headline number now reproduces from committed artefacts (T1–T11, three audit scripts).

### High

**H1 — Computational-only validation (inherent, unfixable by editing).** P(reviewer raises): **1.0**. Mitigation exists and is honest (two public-data cross-checks — one optical, one geometric; falsifiable roadmap). This is now the single dominant acceptance risk and cannot be reduced further without new experiments.

**H2 — Main-text length 62 pp + 21 pp SI.** P(reviewer/editor raises): **0.5**. Cover letter justifies the three-framework integration and the SI relocation was done; residual desk risk only.

**H3 — Abstract still reads "a metrological formulation … is obtained", while SI S4.3 says it is "adopted as a metrological ansatz … rather than a new theorem".** P(careful reviewer cross-checks): **0.6** if unfixed. Direct internal contradiction in claim strength. Fix is one phrase.

**H4 — Cover letter still says fusion "is the optimal strategy", contradicting the manuscript's corrected "practical strategy / minimum-variance under the stated model".** P(editor or reviewer reads cover letter): **0.7** if unfixed. The cover letter is the first document the editor reads.

### Medium

- **M1 — "The framework's conclusions are invariant to the choice of optical model---any physically reasonable OTF with the same cutoff frequency yields the same modality ranking."** Three variants were tested; "any physically reasonable OTF" is a generalisation beyond the evidence. P(challenge): **0.4**.
- **M2 — Introduction: "making the cross-modality comparison predictive rather than descriptive."** Since the scaling relation is now an order-of-magnitude descriptor, "predictive" invites a direct challenge. P(challenge): **0.35**.
- **M3 — Scaling relation remains weak (R²≈0.53; median ratio error ×1.93; residual–σ r=0.81).** Now honestly framed; a reviewer may still ask why it is retained. P(question): **0.4**; defensible answer: it is falsifiable and better than the null.
- **M4 — Fusion demonstration evaluated only on the surface used to set the weights; single realisation.** P(reviewer asks for a held-out check): **0.35**.
- **M5 — Ξ and Π remain heuristic composites with no external validation; Π mixes α (dimensionless) with L (decades·mm⁻²).** P(challenge): **0.4**; the paper labels them figures of merit, which is the correct defence.
- **M6 — Decision matrix extrapolates beyond swept ranges (now noted); smooth-surface RMSE provenance added.** P(challenge): **0.25**.
- **M7 — Anisotropy principal direction (136.8°) is ill-conditioned and the manuscript says so; a reviewer may ask why it is reported at all.** P(question): **0.25**.
- **M8 — Public optical benchmark is a model-description check (now stated), not an independent OTF measurement.** P(question): **0.35**; scope clause addresses it.
- **M9 — Scatterometry extension is unvalidated and its H≈1 is definitional.** P(question): **0.3**; now caveated as a conceptual/computational demonstration.
- **M10 — The `iter01` `.npy` arrays are stale relative to current code (documented in reports, not in the manuscript).** P(referee notices): **0.05**; no action needed beyond the existing documentation.

### Low
- "confirms the methodological principle" (abstract) — "supports" is safer (P≈0.2).
- "The three-way comparison establishes…" (conclusions) — "indicates" (P≈0.15).
- Fringe count, MI symbol precision, figure legibility: proofreading level.

---

## PHASE 2 — NOVELTY AUDIT (claims checked verbatim)

1. "first simulation-derived scaling **relation**" — hedged ("to the best of my knowledge"), falsifiable. **Keep.**
2. "first quantitative measure of measurement-system anisotropy … has not, to the best of our knowledge, been quantified previously" — double-hedged. **Keep.**
3. "no prior work has systematically applied information theory to the comparison …" — hedged + search-basis footnote. **Keep.**
4. "conceptually new in the surface metrology context" (ρ, Ξ) — correctly scoped; formulas explicitly disclaimed as standard. **Keep.**
5. **"making the cross-modality comparison predictive rather than descriptive"** — unhedged, and now in tension with the downgraded scaling relation. **Rewrite (M2).**
6. **"invariant to the choice of optical model … any physically reasonable OTF"** — unhedged generalisation. **Rewrite (M1).**
7. "confirms the methodological principle" — **soften to "supports"**.

No other unhedged first/novel/unique/universal/unprecedented claims found in the current text.

---

## PHASE 3 — ASSUMPTION AUDIT

| Assumption | Stated? | Justified? | Limits? | Action |
|---|---|---|---|---|
| Gaussian surface (channel metrics) | Yes | Yes; non-Gaussian ensemble in SI | Yes, stated | None |
| Gaussian noise (poisson check 3.6 %) | Yes | Yes | Stated | None |
| Stationarity/ergodicity | Yes | Wear-scar test | Stated | None |
| Isotropy of simulated surfaces | Yes | Anisotropy attributed to instrument | Stated | None |
| Linearity of M (σ-sweep, baseline at edge) | Yes | Yes | Stated | None |
| Small-slope dilation | Yes | Verified; nonlinear regime flagged | Stated | None |
| Scalar optics | Yes | Vector correction quantified in SI (≈8 %) | Stated | None |
| Monochromatic λ=550 nm | Yes | Polychromatic variant 96.5 % | Stated | None |
| 1D row unwrapping, 1 % errors | Yes | Sensitivity discussed | Stated | None |
| **Independent noise across modalities (fusion)** | **Implicit** | Reasonable but unstated | Affects the "minimum-variance" claim | Add one clause |
| Known H(f) and noise PSD (fusion, experimental use) | Yes (added in audit) | — | Stated | None |

No hidden assumptions remain.

---

## PHASE 4 — ROBUSTNESS AUDIT

Covered: six surface classes (n=5 each), non-Gaussian ensemble (n=60), optical OTF variants (3), polychromatic illumination, tip geometry argument, raster 100–400 nm, σ 5–200 nm, noise (Gaussian vs Poisson), grid N=128–1024, 180-point sweep, 30-member ensemble.

Missing: **one held-out fusion evaluation** (M4). Minimum additional work: run the existing fusion demo on one independent surface seed and report bias/error alongside the in-sample result (~0.5–1 h). Everything else is complete; **no other simulations are warranted.**

---

## PHASE 5 — REPRODUCIBILITY AUDIT

PASS. 18 automated tests (T1–T11) including equation-level checks (OTF autocorrelation, MI, bound limits, MMSE Monte Carlo, parallel-curve), data-level checks (stylus H, info-loss slope), and statistical checks (refits, blocked validation); fixed seeds; parameter tables; software versions; committed figure generators; audit scripts; public-data provenance with licences and DOIs; repository snapshot statement in Data Availability.

Remaining gaps: none material. The stale `iter01` arrays are documented as unused for headline claims.

---

## PHASE 6 — FALSIFIABILITY AUDIT

All predictions have protocols: H(f) vs artefact (3 dB), scaling exponent outside 1.9±0.3, ρ class-variation <20 %, bound product below (1/4π)(1+1/SNR), scatterometry inversion within factor 2. No changes required.

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

All quantities have physical/metrological interpretation and a plausible measurement route. Flagged: **Π = α·L** (units decades·mm⁻²; heuristic composite) and **Ξ = C/κ** (single-number benchmark; surface-class dependent). Both are labelled figures of merit with stated caveats — acceptable; do not add more metrics.

---

## PHASE 8 — JOURNAL FIT (panel judgement)

**STMP**
- Scope fit **90 %** · Novelty **72 %** · Significance **72 %** · Rigor **90 %** · Clarity **90 %**
- Desk rejection **8–12 %** · Major revision **33–38 %** · Minor revision **30–35 %** · Acceptance after revision **75–80 %**
- Reasoning: ideal scope; rigor now demonstrably high; the residual risks are computational-only (inherent) and length (justified).

**MST**
- Scope fit **80 %** · Novelty **72 %** · Significance **70 %** · Rigor **90 %** · Clarity **90 %**
- Desk rejection **8–12 %** · Major **33–38 %** · Minor **30–35 %** · Acceptance after revision **72–78 %**
- Reasoning: similar profile; information-theoretic sections carry slightly more weight; stylus-metrology emphasis slightly less central.

---

## PHASE 9 — REVIEWER SIMULATION

### Reviewer 1 — surface metrology
**Major.** (1) The scaling relation explains only half the log-variance and has ×2 typical prediction error — please state explicitly that no absolute RMSE prediction should be made from it. (2) The decision matrix extrapolates beyond the swept σ range (noted, but the rough row should perhaps be withdrawn).
**Minor.** Anisotropy orientation ill-conditioned (stated); Π units.
**Recommendation: Minor Revision.**

### Reviewer 2 — optical physics
**Major.** (1) The abstract says the resolution–bandwidth bound "is obtained", but SI S4.3 calls it an adopted ansatz — align. (2) The "invariant to any physically reasonable OTF" claim exceeds the three tested variants.
**Minor.** Scatterometry section is peripheral but clearly labelled; public benchmark scope is now stated.
**Recommendation: Minor Revision.**

### Reviewer 3 — information theory / signal processing
**Major.** (1) Fusion is called minimum-variance without stating the independent-noise assumption — add it. (2) The fusion demonstration is in-sample only — a held-out check would strengthen it.
**Minor.** η/B_eq formulas now present; C_total factor convention documented; Ξ/Π remain heuristic (acceptable if labelled).
**Recommendation: Minor-to-Major Revision.**

**Panel aggregate:** all three lean **Minor Revision**; no reviewer identifies a Critical or High scientific defect. The first-round decision is now driven by inherent scope (computational-only), not by defects.

---

## PHASE 10 — FINAL ACTION PLAN (Top-20, ranked by acceptance gain)

Estimates: Sci (1–5), Rev (1–5), Diff (1–5), Time (h), Gain (0–5).

| # | Action | Sci | Rev | Diff | Time | Gain |
|---|---|---|---|---|---|---|
| 1 | Cover letter: replace "is the optimal strategy" with "is a practical minimum-variance strategy under the stated model" (match manuscript). | 1 | 5 | 1 | 0.05 | +2.5 |
| 2 | Abstract: "a metrological formulation … is obtained" → "a metrological formulation … is proposed and evaluated as a falsifiable benchmark" (match SI ansatz status). | 2 | 4 | 1 | 0.05 | +2.5 |
| 3 | Invariance claim: "invariant to the choice of optical model---any physically reasonable OTF…" → "unchanged across the three tested optical-model variants; OTFs with the same cutoff are expected to behave similarly, but this is not a proof". | 2 | 3 | 1 | 0.1 | +2 |
| 4 | Introduction: "predictive rather than descriptive" → "quantitative and mechanism-based rather than descriptive". | 1 | 3 | 1 | 0.05 | +1.5 |
| 5 | Abstract: "confirms the methodological principle" → "supports the methodological principle". | 1 | 2 | 1 | 0.05 | +1 |
| 6 | Fusion: add "assuming independent noise across modalities" to the minimum-variance statement (main + SI). | 1 | 2 | 1 | 0.1 | +1 |
| 7 | Optional held-out fusion run on one independent seed; report bias/error next to the in-sample demo. | 2 | 3 | 2 | 0.75 | +1.5 |
| 8 | Conclusions: "establishes" → "indicates" (three-way complementarity). | 1 | 1 | 1 | 0.05 | +0.5 |
| 9 | Cover letter: "Hertzian contact mechanics" → "order-of-magnitude contact-mechanics analysis". | 1 | 1 | 1 | 0.05 | +0.5 |
| 10 | Add one Limitations clause: the scaling relation must not be used for absolute RMSE prediction. | 1 | 2 | 1 | 0.05 | +1 |
| 11 | Rebuild all three PDFs; verify 0 errors/0 undefined; 18/18 tests. | 1 | 2 | 1 | 0.5 | +2 |
| 12 | Consistency sweep: test count (18), SI pages (21), ρ CV triple, N=512, blocked R² — automated grep. | 1 | 2 | 1 | 0.3 | +1.5 |
| 13 | Proofread figure captions for legibility and symbol consistency (H vs \|H\|²). | 1 | 1 | 2 | 0.5 | +0.5 |
| 14 | Verify reference list integrity (81 entries) and supplementary cross-references. | 1 | 1 | 1 | 0.3 | +0.5 |
| 15 | British English sweep of the newly added audit sentences. | 1 | 1 | 1 | 0.2 | +0.3 |
| 16 | Re-check that no residual "optimal/universal/predictive" appears in abstract/cover letter. | 1 | 2 | 1 | 0.1 | +1 |
| 17 | Verify the decision-matrix scope note renders adjacent to the table. | 1 | 1 | 1 | 0.1 | +0.3 |
| 18 | Confirm Data Availability names both datasets, licences, DOIs, and the 18-test suite. | 1 | 1 | 1 | 0.1 | +0.3 |
| 19 | Check equation numbering after edits (Eq. references in SI unaffected). | 1 | 1 | 1 | 0.1 | +0.3 |
| 20 | Final git commit on `audit-science` with a one-line change log. | 0 | 1 | 1 | 0.1 | +0.3 |

**Conclusion.** Items 1–6 and 10 are the only genuine remaining *defects* (all introduced by claim-strength mismatches between documents); total ≈ 30 minutes, no new mathematics, no length change. Item 7 is the only recommended new simulation (≤1 h) and is optional. Everything else is verification polish. Expected effect: removes the last cross-document contradictions; first-round outcome remains Minor Revision under the current panel, with the inherent computational-only limitation as the accepted scope.

---

## EXECUTION ADDENDUM (same day)

All Top-20 items were applied. Two outcomes differ from the audit plan:

- **Item 7 (held-out fusion run) produced a new finding rather than a confirmation.** `verification/audit_fusion_holdout.py` (seeds 42/777/999) showed the scatterometry PSD returned by the Rayleigh–Rice inversion is not on the same absolute scale as the height PSD (median ≈1e-18 vs ≈1e-30), so the previous claim that the fused estimate "matches the true PSD across the combined bandwidth" was unsupported. The SI text and fig. S2 caption now classify the demonstration as illustrative of the weighting rule only. This is a downgrade, not a new result.
- All wording defects (items 1–6, 8–10) were fixed with no length change; the manuscript's cross-document claim strength is now uniform ("proposed and evaluated as a falsifiable benchmark"; "practical minimum-variance strategy under the stated independent-noise model"; "unchanged across the three tested variants").

Final state: 18/18 tests (T1–T11 unchanged); the fusion audit is a separate committed script (`verification/audit_fusion_holdout.py`) with output in `reports/fusion_holdout_audit.json`; 0 build errors, 0 undefined citations.
