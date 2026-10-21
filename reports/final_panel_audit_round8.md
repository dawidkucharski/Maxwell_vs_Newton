# Hostile Panel Audit — Round 8 (from scratch, arithmetic-focussed)

**Documents:** manuscript, supplementary, IMEKO extended abstract.
**Method:** independent re-read + first-time numerical verification of derived quantities against the displayed formulas (previous rounds audited text and logic; this round independently recomputed arithmetic).
**Date:** 2026-10-21. Fixes committed as `62f50ed`.

---

## PHASE 1 — TECHNICAL AUDIT (with independent recomputation)

### New findings this round

**A1. Uncertainty-product inflation percentages 10× inflated — MEDIUM, P(reviewer) ≈ 0.3. FIXED.**
Text stated stylus product "0.081 (18% above the classical limit)" and optical "0.083 (31% above)". Recomputing from the paper's own formula, $(1/4\pi)(1+1/\overline{\mathrm{SNR}})$:
- classical limit $1/4\pi = 0.07958$;
- stylus, SNR ≈ 56 → bound $0.0810$ = **+1.8%**, not 18%;
- optical, SNR ≈ 32 → bound $0.0821$ = **+3.1%**, not 31% — and the printed 0.083 corresponds to SNR ≈ 23, contradicting the stated SNR ≈ 32.
Fixed: optical bound now 0.082, percentages now 1.8% and 3.1%. The qualitative conclusion (stylus closer to the classical limit) is unchanged.

**A2. Roadmap cutoff attribution — LOW, P ≈ 0.15. FIXED.**
"λ = 400–450 nm … combined with NA = 0.8, the cutoff reaches 4000 mm⁻¹" holds only at λ = 400 nm (at 450 nm it is 3556 mm⁻¹). Sentence now anchored to λ = 400 nm.

### Verified correct by recomputation this round (spot checks)
Hertzian contact (a = 201 nm, p_mean = 7.9 GPa, p_max = 11.8 GPa, ψ = 5.83) · coherence envelope (l_c = 3.0 µm, σ_z = 1.3 µm, obliquity factor 0.84) · Rayleigh criterion boundary (69 nm) · all roadmap cutoffs (2000/2909/3273 mm⁻¹) · scaling-law worked examples (17^1.90 ≈ 2.2×10²; 1.71^1.90 ≈ 2.8) · crossover wavelength (1/454 mm⁻¹ = 2.20 µm) · stylus H values and 3 dB point (verified against test T10) · 0.907/0.706/1.28 proxy values · equivalence 9.6%±0.3% · CV triple (0.16/0.22/0.067).

### Ranks of all open items after this round
- No Critical, no High items remain. Nothing else found in this fresh pass.

---

## PHASE 2 — NOVELTY AUDIT
All "first/novel/no prior work/universal" claims are hedged or carry search-basis footnotes (scaling law, anisotropy tensor, information-theoretic application). No rewrite required; none triggered this round.

## PHASE 3 — ASSUMPTION AUDIT
All assumptions stated, justified, boundary-tested (Gaussianity, stationarity, ergodicity, small-slope linearity, scalar/monochromatic optics, additive Gaussian noise, tip geometry, 1D unwrapping, coherence envelope, white-noise tail). No unstated assumption found.

## PHASE 4 — ROBUSTNESS AUDIT
Coverage complete: six surface classes, three OTF variants, tip-geometry variants, raster sweep, noise sweeps, Poisson comparison, σ sweep, four-grid convergence, non-stationary test. The new bias-limited residual-gap statement is robust by construction (follows from H values verified by T10). No additional simulations recommended.

## PHASE 5 — REPRODUCIBILITY AUDIT
Parameters, seeds, versions, methods, repository (release v1.0.2), Zenodo concept DOI, 18 tests, three audit scripts. Complete.

## PHASE 6 — FALSIFIABILITY AUDIT
Explicit falsification pathways for the scaling law, the resolution–bandwidth benchmark, the roadmap, ρ universality, and the equivalence protocol. Complete.

## PHASE 7 — PRACTICAL IMPACT AUDIT
Every quantity has physical/engineering/metrological interpretation and a measurement path. None lacking.

## PHASE 8 — JOURNAL FIT
STMP: scope 95%, novelty 72%, significance 75%, rigour 87%, clarity 84%; desk rejection ≈5%, major revision 10–15%, minor 50%, accept after revision 80–85%. MST: secondary (≈55–60%). IMEKO abstract ≈85%.

## PHASE 9 — REVIEWER SIMULATION
- **Reviewer 1 (surface metrology):** no major comments; minor: explain §S3/§S5 realisation-set differences (prepared answer exists). **Accept / Minor.**
- **Reviewer 2 (optical physics):** no major comments; minor: cite Wilson & Sheppard for confocal transfer. **Accept.**
- **Reviewer 3 (information theory):** no major comments; minor: B_eq definitional note. **Accept / Minor.**

## PHASE 10 — FINAL ACTION PLAN
Executed this round: A1 (uncertainty-product arithmetic), A2 (400 nm attribution). Both trivial difficulty, high correctness value, no length increase.
**Top-20 roadmap:** items 3–20 are all "do nothing" — any further modification (new simulations, metrics, validation, wording) violates the no-expansion constraint with negligible acceptance gain.

### Bottom line
With A1–A2 fixed, a third independent audit pass finds **no remaining reviewer-findable weakness.** The documents are final. **Stop here.**
