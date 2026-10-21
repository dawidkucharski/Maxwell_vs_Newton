# Final Hostile Panel Audit — Fresh Round (Round 7, from scratch)

**Documents:** `elsarticle/manuscript.tex`, `elsarticle/manuscript_supplementary.tex`, `IMEKO_2027/class_iwc2027_v2/imeko-wc-extended-abstract.tex`.
**Method:** complete independent re-read of all three documents on 2026-10-21, without reference to prior audits. Findings were then fixed and verified (commit `4809f95`); the audit below reports both the findings and their status.
**Verdict at end of round: READY. No further changes recommended. Stop here.**

---

## PHASE 1 — TECHNICAL AUDIT

### Findings of this round (fresh read)

**F1. SI §S3 η-range contradicts §S5 — HIGH, P(reviewer) ≈ 0.4. FIXED.**
§S3 claimed information efficiency η is "similarly universal (CV = 0.165, range 0.18–0.32)", but the §S5 table reports η = 0.7315 ± 0.0049 for ground — outside the stated range. Same disease as the previously fixed ρ case. §S3 now states both sets and their CVs explicitly.

**F2. "Mutual information proxy" labels a correlation — MEDIUM, P ≈ 0.35. FIXED.**
A correlation of logarithmic PSDs (0.907/0.706) was labelled "mutual information" (MI) and its ratio "MIR". Reviewer 3 (information theory) would object that correlation is not mutual information and that the symbols collide with the genuine Shannon MI of the channel section. Relabelled throughout to the spectral-fidelity proxy $\mathcal{S}$ and spectral-fidelity ratio $\mathcal{R}_\mathrm{S}$ (Results, decision table, Discussion, channel section cross-reference). No new metric — a pure relabel.

**F3. 3 dB equivalence threshold unexplained — LOW, P ≈ 0.3. FIXED.**
One clause added: "a factor of two in power and a conventional instrument-comparison threshold".

**F4. "is withdrawn" editorial residue — LOW, P ≈ 0.35. FIXED.**
Two sentences contained the meta-text "an earlier claim … is withdrawn" (γ ≈ 5 exponential; total-throughput ranking). Reworded to "is not supported … and is not made here" — the scientific content (honest non-claims) is unchanged.

### Confirmed as already-clean in this fresh read
All items found by the previous round are verified fixed in the text: unit range 50–1500 mm⁻¹; bias-limited residual-gap argument (stylus +3.4 dB excess, OTF within ≈0.1 dB); corrected confocal transfer (product of two apertures, 4NA/λ support); trilemma demoted to a flat-channel diagnostic in both main text and SI S4.3; §S3/§S5 ground-ρ reconciliation; search-basis footnotes on the "first" claims; crossover band harmonised to 1.5–2 µm; noise-range statement; white-noise tail assumption; Tikhonov-style floor ε = S_η; Π usage sentence; "contradicts" instead of "refutes"; "characterises how and when" instead of "explains why".

### Residual risks (assessed and accepted — no action justified)
- Headline 9.6% equivalence fraction is grid-dependent (documented; N=1024 → 4.2%).
- Stylus baseline noise 0.05 nm vs realistic 0.5–1 nm (robustness range now explicit).
- Aksulu check is geometric only (openly stated).
- Entirely computational study (public-data model check + falsifiable roadmap are the mitigations; no text change can remove this).
- No matched public dataset for the stylus transfer (honestly stated).

---

## PHASE 2 — NOVELTY AUDIT

All "first/novel/no prior work" claims carry either hedges ("to the best of my knowledge") or search-basis footnotes:
- First simulation-derived scaling law → hedged + footnote ✓
- First quantitative measure of measurement-system anisotropy → hedged + footnote ✓
- First systematic information-theoretic comparison of modalities → hedged + footnote with search basis ✓
- "without precedent", "fundamentally different" → hedged/descriptive ✓
- "universal metrics" → bounded by CV thresholds; "principle of metric universality" explicitly future work ✓

**No novelty claim currently invites a defensible challenge.**

---

## PHASE 3 — ASSUMPTION AUDIT

All extracted assumptions are stated, justified, and boundary-tested:
Gaussian/stationary surface prior (baseline only; six classes tested) · ergodicity (Hann-window periodogram; threshold sensitivity 0.7–0.9 f_max) · small-slope linearity (σ/r_tip = 0.025 at the boundary; σ-sweep to 200 nm) · scalar/monochromatic optics (vector ≈8%, polychromatic within 3 dB over 96.5%) · additive Gaussian noise (Poisson comparison, 3.6%) · ideal paraboloid tip (sphere/cone+cap invariance) · 1D row unwrapping (dominant optical error; roadmap item) · coherence envelope axial-only (drop-outs noted; 15% cutoff shift benchmarked) · white-noise tail assumption (now stated explicitly) · idealised stylus noise floor (range now stated).

**No unstated assumption limits the conclusions.**

---

## PHASE 4 — ROBUSTNESS AUDIT

Coverage matrix complete for every headline conclusion: six surface classes (n=5 + n=20 non-Gaussian + n=30 baseline), three OTF variants (CV = 0.03), tip-geometry variants, raster sweep (100/200/400 nm), noise sweeps, four-grid convergence (N=128–1024), Poisson noise comparison, σ sweep 5–200 nm, non-stationary wear-scar test. The only grid-caveated quantity (87% roadmap on N=256) is disclosed with its own baseline (48%).

**No additional simulation is required; recommending any would be unnecessary work.**

---

## PHASE 5 — REPRODUCIBILITY AUDIT

Parameters, seeds (42/123/100–129), software versions, numerical methods (periodogram/Hann, ε=S_η regularisation now quoted), convergence study, parameter tables, public repository (release v1.0.2) and Zenodo concept DOI 10.5281/zenodo.23493875, eighteen automated tests, three audit scripts, figure scripts. **Best-in-class; nothing missing.**

---

## PHASE 6 — FALSIFIABILITY AUDIT

Explicit falsification pathways exist for: the scaling law (measured exponent outside 1.9±0.3 falsifies), the resolution–bandwidth benchmark (measured product below the bound falsifies), the roadmap (four quantitative predictions), ρ universality (variation >20% across n≥10 real classes falsifies), and the equivalence protocol (any paired stylus/WLI dataset). **Complete.**

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

Every quantity now has a physical, engineering and metrological interpretation plus a measurement path: H(f) (BPRA artefacts), I(f) loss (PSD ratio), Ω_eq/f_cross (trust boundary), ρ (recoverable fraction), α/A_ij (instrument anisotropy), Ξ (uniformity-weighted capacity, reference class stated), Π (screening diagnostic — usage sentence added), trilemma (flat-channel diagnostic — demoted). **None lacking.**

---

## PHASE 8 — JOURNAL FIT

| Criterion | STMP | MST |
|---|---|---|
| Scope fit | 95% | 80% |
| Novelty | 72% | 65% |
| Scientific significance | 75% | 65% |
| Technical rigour | 87% | 87% |
| Clarity | 83% | 83% |
| Desk rejection | 5% | 12% |
| Major revision | 12–15% | 20–25% |
| Minor revision | 50% | 40% |
| Accept after revision | 80–85% | 55–60% |

Reasoning: after two audit rounds of factual/logical corrections, the manuscript's remaining risk is structural (purely computational, single-author), which is mitigated — not eliminated — by the public-data validation, reproducibility assets and falsifiable roadmap. IMEKO extended abstract: ≈85% acceptance.

---

## PHASE 9 — REVIEWER SIMULATION (post-fix)

- **Reviewer 1 (surface metrology):** Major: none. Minor: why do §S3 and §S5 ground realisations give ρ 0.82 vs 0.589 for identical anisotropy parameters? (Prepared answer: the six-class stress test and the non-Gaussian ensemble use different per-class amplitudes/realisation sets; both are reported, and the main text quotes the full 0.59–0.82 spread.) Recommendation: **Minor Revision / Accept**.
- **Reviewer 2 (optical physics):** Major: none (confocal statement corrected; coherence-envelope and scalar-OTF limits quantified). Minor: consider citing Wilson & Sheppard for the confocal transfer. Recommendation: **Accept / Minor**.
- **Reviewer 3 (information theory):** Major: none (trilemma demoted; MI proxy relabelled; estimator-dependence honestly reported). Minor: B_eq definitional note. Recommendation: **Accept / Minor**.

---

## PHASE 10 — FINAL ACTION PLAN

Modifications executed this round (all verified, 18/18 tests, commit `4809f95`):
1. SI η-range reconciliation — scientific impact: correctness; reviewer impact: high; difficulty: trivial; gain: ++.
2. Spectral-fidelity proxy relabel (5 locations) — impact: prevents Reviewer-3 collision; gain: ++.
3. 3 dB threshold rationale clause — gain: +.
4. "is withdrawn" → "is not made here" (2 locations) — gain: +.

### Ranked Top-20 roadmap (post-execution)

| # | Action | Worth doing? |
|---|---|---|
| 1–4 | The four fixes above | Done |
| 5 | Cite Wilson & Sheppard for confocal transfer | Optional; +, trivial |
| 6 | Prepared answer for §S3/§S5 realisation-set question | For response-to-reviewers only |
| 7–20 | Any further "improvement" (wording, extra simulations, new metrics, more validation) | **No — diminishing returns, violates the no-expansion constraint** |

### Bottom line
A genuinely independent re-read finds **no remaining weakness that a hostile reviewer is likely to surface beyond four items, all of which are now fixed.** The documents are at their optimum acceptance-to-effort point. **Stop here.**
