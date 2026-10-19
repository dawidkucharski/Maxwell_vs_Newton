# Reviewer Panel Audit — Round 5 (final audited state)

Date: 2026-10-19. State: `audit-science` @ 6072c40 + Round-5 fixes (applied, no page change). 62 pp + 22 pp + 3 pp; 0 errors, 0 undefined; 18/18 tests.

All probability estimates are editorial judgement, not measured statistics.

## PHASE 1 — TECHNICAL AUDIT

**Critical: none. High: none editable.** The manuscript has now been through five panel rounds plus two science audits; every reviewer-catchable defect has been fixed or removed. The only High-severity residual is **inherent scope** (computational-only validation, P≈1.0), which is disclosed and benchmarked, not fixable by editing.

Remaining findings found in this round (all fixed in-place, no length change):

- **M1 — Symbol/name mismatch:** the text said "spectral-similarity proxy" but the symbols were still `MI_stylus`/`MI_optical` and "mutual information ratio MIR". P(reviewer notes): 0.5. Fixed: symbols now $\mathcal{S}_\mathrm{stylus}$/$\mathcal{S}_\mathrm{optical}$, "similarity ratio $\mathcal{R}_\mathrm{S}$".
- **M2 — "Stylus anisotropy universality … confirming … robust, parameter-independent".** α_s = 0.011±0.011 has CV≈100 %; the label overstated the evidence. P: 0.3. Fixed: "Stylus anisotropy across the sweep … showing that … is small across parameter combinations".
- **M3 — Protocol overlap:** step 3 (prefer stylus for λ>2 µm) overlapped step 5 (average over 1.5–3.5 µm). P: 0.25. Fixed: averaging band now 1.5–2 µm, giving a disjoint partition (optical 0.5–1.5 µm; average 1.5–2 µm; stylus >2 µm; neither <0.5 µm).
- **Low:** none remaining beyond proofreading-level items.

## PHASE 2 — NOVELTY AUDIT

All "first/novel/unique/universal/no prior work" claims are hedged ("to the best of my knowledge", search-basis footnote) or scoped ("conceptually new in the surface metrology context"). The two unhedged phrases found in earlier rounds are gone. **No flags.**

## PHASE 3 — ASSUMPTION AUDIT

Gaussian signal/noise, stationarity, isotropy, small-slope dilation, linearity, scalar optics, monochromatic approximation, 1D unwrapping, known H/noise for fusion, independent noise across modalities — all stated, justified, and with stated limits. **No hidden assumptions.**

## PHASE 4 — ROBUSTNESS AUDIT

Six surface classes, non-Gaussian ensemble, 3 OTF variants, polychromatic illumination, raster 100–400 nm, σ 5–200 nm, Gaussian-vs-Poisson, grid 128–1024, 180-point sweep, n=30 ensemble, two public datasets. **No additional simulations are warranted.**

## PHASE 5 — REPRODUCIBILITY AUDIT

18 automated tests (equation-level, data-level, statistical); fixed seeds; parameter tables; versions; committed generators and audit scripts; public-data provenance with licences/DOIs. **PASS.**

## PHASE 6 — FALSIFIABILITY AUDIT

Every prediction has a protocol (H(f) 3 dB; exponent 1.9±0.3; ρ <20 % class variation; bound product below (1/4π)(1+1/SNR); scatterometry factor 2). **PASS.**

## PHASE 7 — PRACTICAL IMPACT AUDIT

All quantities have physical/metrological interpretation and a measurement route. Ξ and Π remain heuristic composites — correctly labelled. **No action.**

## PHASE 8 — JOURNAL FIT (panel judgement)

| Journal | Scope | Novelty | Significance | Rigor | Clarity | Desk rej. | Major | Minor | Accept after rev. |
|---|---|---|---|---|---|---|---|---|---|
| STMP | 90 % | 72 % | 72 % | 91 % | 90 % | 8–12 % | 30–35 % | 35–40 % | 78–82 % |
| MST | 80 % | 72 % | 70 % | 91 % | 90 % | 8–12 % | 30–35 % | 35–40 % | 75–80 % |

STMP remains first choice: ideal scope, demonstrably high rigor, honest limitations.

## PHASE 9 — REVIEWER SIMULATION

- **Surface metrology:** no remaining major comments; minor (Π units, anisotropy orientation). **Minor Revision.**
- **Optical physics:** no major comments; minor (benchmark scope already stated). **Minor Revision.**
- **Information theory:** no major comments; minor (heuristic status of Ξ/Π accepted as labelled). **Minor Revision.**

Panel aggregate: **Minor Revision** in all three cases; no reviewer finds a Critical or High defect.

## PHASE 10 — FINAL ACTION PLAN (Top-20)

Items 1–3 were the only genuine findings and are **already applied** (in-place, no page change). The remaining roadmap is verification only:

| # | Action | Sci | Rev | Diff | Time | Gain |
|---|---|---|---|---|---|---|
| 1 | M1 symbol rename (applied) | 1 | 3 | 1 | 0.05 | +1 |
| 2 | M2 anisotropy wording (applied) | 1 | 2 | 1 | 0.05 | +1 |
| 3 | M3 protocol partition (applied) | 1 | 2 | 1 | 0.05 | +0.5 |
| 4 | Rebuild all PDFs; 0 errors/0 undefined (done: 62+22+3 pp) | 1 | 2 | 1 | 0.5 | +1 |
| 5 | 18/18 tests (done) | 1 | 2 | 1 | 0.2 | +1 |
| 6 | Grep sweep for `MI_`, `MIR`, "universality", "confirming" → 0 | 1 | 1 | 1 | 0.1 | +0.5 |
| 7–20 | Standard submission checks (figures legible, references intact, British English, equation numbering, cover-letter numbers, final commit) | — | — | — | ~1 | +0.5 total |

**Conclusion.** No further acceptance-gaining edits exist within the current framework. The Top-20 is exhausted; the manuscript is submission-ready at 62+22+3 pp with 0 build errors and 18/18 tests. Page count unchanged by this round.
