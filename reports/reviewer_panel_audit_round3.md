# Reviewer Panel Audit — Round 3 (post public-data + SI relocation)

Date: 2026-10-17. Manuscript: "Optical Profilometry Versus the Stylus: A Spectral Theory for Closing the Accuracy Gap" (60 pp + 21 pp SI + 3 pp cover letter). Journals: STMP, MST, IEEE TIM, Precision Engineering, Optics and Lasers in Engineering.

All probability estimates below are editorial judgement of this panel, not measured statistics. The scientific framework is assumed complete; this audit identifies what reviewers will attack and which fixes give the highest acceptance gain. Quotes are verbatim from the current files.

**Changes since Round 2 that materially alter the risk profile:**
- Two public-dataset cross-checks (Hirose WLI benchmark; Aksulu ball-standard geometric check) — partially neutralises the "purely computational" objection.
- Main text trimmed 61→60 pp; fig8/fig10/GUM moved to SI (S3/S4/new section).
- T8 and T9 added — the verification suite now has **16** tests.

---

## PHASE 1 — TECHNICAL AUDIT

### Critical

**C1 — Scaling-law worked example uses the wrong optical cutoff (factor 2).**
"an optical system with $\mathrm{NA}=0.3$ ($f_{c,o}\approx\SI{545}{mm^{-1}}$)".
The manuscript's own definition is $f_{c,\mathrm{opt}} = 2\mathrm{NA}/\lambda$ (used correctly elsewhere: $2\times0.55/0.55\ \mu\mathrm{m} = 2000$ mm⁻¹). For NA = 0.3, λ = 550 nm the correct value is **1091 mm⁻¹**, not 545. The downstream numbers are internally consistent with the wrong input (8.5 = 545/64; $8.5^{1.90}\approx58$; $0.74\approx(545/637)^{1.90}$) but all three become wrong once the cutoff is corrected: the ratio becomes 17.1, the exponentiated ratio ≈2.2×10², and the second example becomes ≈2.8 instead of 0.74 — which also flips the example's rhetorical point ("making the modalities comparable"). Probability a reviewer recomputes: **0.8**. This is exactly the arithmetic a hostile Q1 referee checks against the paper's own equations.

**C2 — The status of the central bound is stated inconsistently between main text and SI.**
Main text: "the following bound holds (derivation in Supplementary Material \S S4.3)".
SI S4.3: "is adopted as a metrological ansatz anchored to the classical Fourier uncertainty ... The bound is therefore a definitionally anchored, falsifiable benchmark **rather than a new theorem**".
A reviewer who cross-reads S4.3 (information-theorists do) will flag the main text as overclaiming relative to the author's own SI. Probability: **0.7**.

### High

**H1 — Stale test-suite count.** Data Availability: "An accompanying verification suite (fourteen automated tests)". The suite now has 16 (T1–T9 incl. T8, T9). Internal quality-control error, immediately visible. Probability: **0.8**.

**H2 — The Information–Energy–Resolution trilemma's stated interpretation is not supported by its own explicit form.** Main text: "increasing the extracted information requires either measuring rougher surfaces (larger $\sigma^2$) or accepting coarser resolution". SI S4.3 gives $\mathcal{F}(\overline{\mathrm{SNR}}) = \frac{A}{2\sigma^2}\frac{1}{(4\pi)^2}(1+1/\overline{\mathrm{SNR}})^2\log_2(1+\overline{\mathrm{SNR}})$, so in $I\cdot(\Delta x_\mathrm{eff})^2 \approx \sigma^2\cdot\mathcal{F}$ the $\sigma^2$ **cancels**: the right-hand side is a function of SNR and area only. The "rougher surfaces" lever enters exclusively through SNR, not as an independent factor. Probability: **0.6** (information-theory reviewer).

**H3 — Equivalence-criterion protocol contradicts the paper's own cutoff.** "For wavelengths $\lambda < \SI{1}{\micro m}$ (above the optical cutoff), only the optical measurement is valid". The optical cutoff is $\lambda = 0.5\ \mu\mathrm{m}$ ($f_c = 2000$ mm⁻¹); the band 0.5–1 µm lies **below** the cutoff. Metrology reviewers will catch the misstatement. Probability: **0.7**.

**H4 — Ξ usage guidance omits the SI's own surface-class caveat.** Main text: "When purchasing or qualifying an instrument, $\Xi$ can be computed from a reference surface measurement and compared across instruments. Two instruments with similar RMSE may have $\Xi$ values differing by factors of 2–5". SI S3: $\Xi$ "spans nearly two orders of magnitude across classes ... suggesting that single-number instrument comparison via $\Xi$ requires specification of the reference surface class" (CV = 0.68). The main-text guidance must carry this caveat or it will be read as contradicting the SI. Probability: **0.5**.

### Medium

- **M1 — Headline equivalence fraction is grid-sensitive.** 9.6 %±0.3 % is at N=512; the same quantity is 0.042 at N=1024, and the roadmap baseline is 48 % at N=256. Documented in Limitations, but the Results/abstract headline does not carry "(N=512)" at first use. Probability: **0.5**.
- **M2 — Decision matrix rows extrapolate beyond swept ranges.** "Rough ($H<0.4$, $\sigma>50$ nm)" — the sweep covers σ ∈ {10, 25, 50} nm and H ∈ {0.3, 0.5, 0.7}; the σ>50 nm regime is covered only by the stylus-linearity σ-sweep (up to 200 nm), not by the full cross-modality sweep. "RMSE $<20$~nm" for smooth surfaces is not reported anywhere else in the manuscript. Probability: **0.5**.
- **M3 — Data Availability omits the Aksulu dataset.** The ball-standard cross-check is reported in Results, but Data Availability names only Hirose et al. Both are public CC-BY-4.0; both should be cited there. Probability: **0.6**.
- **M4 — Residual unhedged novelty phrasing.** "the fact that the measurement system itself introduces directional bias has not been quantified previously" (second sentence is unhedged; the first is hedged). Probability: **0.3**.
- **M5 — "four manufactured classes" (abstract).** The CV = 0.22 estimate pools 3 manufactured classes + the simulated Gaussian baseline; "four surface classes" is accurate, "four manufactured classes" is not. Probability: **0.4**.
- **M6 — No operational formula for $\eta$ or $B_\mathrm{eq}$.** The practitioner table gives verbal definitions ("fraction of the noise-free capacity achieved"; "width of a flat transfer function with the same total information throughput"), but the SI stress test reports $\eta$ to three decimals and no formula appears anywhere. Round-2's "define or delete" was only half-resolved. Probability: **0.5**.
- **M7 — Visible broken cross-references in SI.** "Eq.~hstylus" (SI §2.3) and "Eq.~(metrological uncertainty bound)" (SI S4.3) render literally as prose. Probability: **0.9** (severity low, visibility high).
- **M8 — Dangling clause in the capacity subsection.** "where $\sigma^2$ is the total surface variance. The solution---the classical water-filling allocation..." — the water-filling problem statement (variance constraint $\iint S_h\,d^2\!f = \sigma^2$) is never stated in the main text before "the solution". Probability: **0.6**.
- **M9 — SI §1 physical numbers are hand-computed and untraceable.** Hertzian contact, coherence-envelope, and vector-diffraction constants (201 nm, 7.9 GPa, 3.0 µm, 0.504, Strehl 0.91) follow from displayed equations but no script/table in the repository reproduces them. One provenance sentence suffices. Probability: **0.4**.
- **M10 — Simulated noise floor vs SI uncertainty budget.** Simulation uses 0.1 % of σ = 0.05 nm additive noise; SI Table 1 lists "Base measurement noise 0.5 nm / 1.0 nm". The idealised floor is never reconciled with the realistic budget. Probability: **0.3**.

### Low

- "approximately 9 measurable interference fringes" — $l_c/(\lambda/2) \approx 11$ (SI §1.2). Probability: **0.2**.
- Decision table "MI$_s=0.91$" vs text 0.907±0.001 — precision mismatch only.
- "the measured spectra thus roll off ≈15 % beyond the nominal monochromatic cutoff" — "beyond" is ambiguous (cutoff shifted 15 % higher vs roll-off starting 15 % earlier). Probability: **0.2**.

---

## PHASE 2 — NOVELTY AUDIT

Claims checked (verbatim):

1. "this is the first simulation-derived scaling law connecting instrument cutoff frequencies to cross-modality accuracy ratios" — hedged ("To the best of my knowledge"), falsifiable, defensible. **Keep.**
2. "The anisotropy tensor $A_{ij}$ is, to the best of my knowledge, the first quantitative measure of measurement-system anisotropy in surface metrology." — hedged in sentence 1; sentence 2 ("has not been quantified previously") is not. **Recommended conservative rewrite:** "has not, to the best of our knowledge, been quantified". Preserves value, removes the challenge surface (M4).
3. "to the best of my knowledge, without precedent" / "no prior work has systematically applied information theory to the comparison of fundamentally different surface measurement modalities" — hedged, footnote documents the search basis (Crossref queries, log available). Residual risk of a reviewer finding adjacent work (information capacity of 3D imaging, directional ITF analyses); the hedge is adequate. **Keep.**
4. "conceptually new in the surface metrology context" ($\rho$, $\Xi$) — correctly scoped ("context", not "period"), and the manuscript explicitly disclaims novelty of the underlying formulas. **Keep.**

**Flags:** only item 2 (second sentence). No other "first/novel/unique/universal" claims were found that are unhedged.

---

## PHASE 3 — ASSUMPTION AUDIT

| Assumption | Stated? | Justified? | Limits conclusions? | Action |
|---|---|---|---|---|
| Gaussian surface heights (info-theory section) | Yes | Yes (Gaussian channel model; non-Gaussian ensemble in SI) | Yes, stated | None |
| Additive Gaussian noise | Yes | Yes (Poisson comparison, 3.6 % RMSE difference) | Yes, stated | None |
| Stationarity/ergodicity (periodogram) | Yes | Yes (wear-scar test in Limitations) | Yes, stated | None |
| Statistical isotropy of simulated surfaces | Yes | Yes (anisotropy attributed to instrument) | Yes | None |
| Linearity of $\mathcal{M}$ | Yes | Yes (σ-sweep, baseline at upper edge of small-slope regime) | Yes, stated | None |
| Small-slope dilation | Yes | Yes (curvature-bias verification; nonlinear regime flagged) | Yes | None |
| Scalar optics at NA = 0.55 | Partly | Main text is scalar; SI §1.3 gives vector corrections but the baseline simulation does not use them | The effective cutoff drops ~8 % (1830 vs 2000 mm⁻¹) | Add one clause in Methods noting the scalar OTF is retained for the baseline and the vector correction is quantified in the SI (Low) |
| Monochromatic λ = 550 nm | Yes | Yes (polychromatic variant: 96.5 % of passband within 3 dB; public benchmark c = 1.15) | No | None |
| Idealised noise floors (0.1 % σ) | Yes, but unreconciled with SI budget | Partly | Minor | M10 one-clause reconciliation |

No assumption is hidden; none is unjustified. Two small wording additions (scalar-OTF clause, noise-floor reconciliation) close the remaining gaps.

---

## PHASE 4 — ROBUSTNESS AUDIT

| Conclusion | Variants tested | Evidence | Status |
|---|---|---|---|
| $H_\mathrm{stylus} \approx 1$ + bias | Tip shapes (spherical/conical-cap), raster 100–400 nm | Methods/Robustness | **Covered** |
| $H_\mathrm{optical}$ = incoherent OTF | Aberrated/Gaussian OTF variants, polychromatic 500–700 nm | Robustness; public benchmark c = 1.15 | **Covered** |
| Modality ranking / ρ | Six surface classes (n=5 each), non-Gaussian ensemble (n=60) | SI §3, §5 | **Covered** |
| Equivalence regime | 180-pt sweep, grid study | Results/Limitations | Covered with grid caveat (M1) |
| Scaling law | 180 combos, out-of-sample R² = 0.51 | Results | Covered (but C1 example arithmetic) |
| Noise robustness | Gaussian vs Poisson; SNR sweep | Limitations | **Covered** |
| Confocal/other optical modalities | Claimed by analogy only ("variants of $H_\mathrm{optical}(f)$") | Limitations | Accepted as argument, flagged as untested analogy — soften to "expected to be" (Low) |

**Minimum additional simulations required: none.** Every major conclusion already has a variant test or a public-data check. All remaining fixes are textual.

---

## PHASE 5 — REPRODUCIBILITY AUDIT

Present: fixed seeds (42/123/100–129), parameter tables (Table 1), grid sizes, software versions (Python 3.9, NumPy 2.0, SciPy 1.13, Matplotlib 3.9), committed generators for the grid study and gap-closure sweep, verification suite, public-data fetch scripts.

Missing / stale:
1. "fourteen automated tests" → 16 (H1).
2. Aksulu dataset absent from Data Availability (M3).
3. SI §1 physical constants have no repository trace (M9).
4. η and $B_\mathrm{eq}$ formulas absent (M6).

Otherwise a group with the repository could reproduce every figure. **No missing parameter blocks.**

---

## PHASE 6 — FALSIFIABILITY AUDIT

Every prediction has an explicit falsification pathway:

- $H(f)$ prediction: 3 dB across passband on a calibrated artefact (Roadmap 1).
- Scaling law: exponent outside 1.9±0.3 falsifies it.
- ρ universality: >20 % class variation hypothesis (Roadmap 2).
- Uncertainty bound: measured product below $(1/4\pi)(1+1/\overline{\mathrm{SNR}})$ falsifies the formulation.
- Scatterometry: inverted PSD within factor 2 (Roadmap 4).

**No changes required.**

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

| Quantity | Physical | Engineering | Metrological | Measurable? | Flag |
|---|---|---|---|---|---|
| $H(\mathbf{f})$ | yes | yes | yes | yes (Yashchuk gratings) | — |
| $I(f)$ | yes | yes | yes | yes | — |
| $A_{ij}$, α | yes | yes | yes | yes | — |
| $\Omega_\mathrm{eq}$ | yes | yes | yes | yes | grid caveat (M1) |
| $I(h;y)$ | yes | yes | yes | yes (estimator-dep., stated) | — |
| ι(f) | yes | yes | yes | yes | — |
| ρ | yes | yes | yes | yes | — |
| κ, Ξ | yes | yes | partial | yes | **H4 caveat missing** |
| $B_\mathrm{eq}$, η, ε | partial | partial | partial | not without formulas | **M6 formulas missing** |
| Uncertainty bound | yes | yes | yes | yes | C2 status wording |
| Trilemma | partial | partial | partial | yes | **H2 interpretation** |

---

## PHASE 8 — JOURNAL FIT

All figures are panel judgement.

| Journal | Scope fit | Novelty | Significance | Rigor | Clarity | Desk rej. | Major | Minor | Accept after rev. |
|---|---|---|---|---|---|---|---|---|---|
| STMP | 90 % | 70 % | 72 % | 88 % | 90 % | 10–15 % | 35–40 % | 25–30 % | 70–75 % |
| MST | 80 % | 70 % | 70 % | 88 % | 90 % | 10–15 % | 35–40 % | 25–30 % | 70 % |
| IEEE TIM | 70 % | 65 % | 65 % | 85 % | 85 % | 20–25 % | 40–45 % | 20 % | 60 % |
| Precision Engineering | 75 % | 70 % | 70 % | 85 % | 88 % | 15–20 % | 35–40 % | 25 % | 70 % |
| Opt. Lasers Eng. | 60 % | 65 % | 60 % | 85 % | 88 % | 25–30 % | 40 % | 15 % | 50–55 % |

**STMP reasoning:** scope is ideal (spectral surface metrology); the residual desk-rejection drivers are length (60 pp main, mitigated by SI relocation and cover letter) and computational-only (mitigated by two public benchmarks). Rigor is high because every prior Critical/High finding has been closed. The remaining items in this audit are precision-of-scholarship defects (C1, C2, H1–H4), not framework defects — they do not threaten acceptance *if fixed pre-submission*, but they will each surface as referee comments and convert what would be a Minor Revision into a Major one.

---

## PHASE 9 — REVIEWER SIMULATION

### Reviewer 1 — Surface metrology
**Major.** (1) The worked example in "How to interpret the scaling law" computes $f_{c,\mathrm{opt}}$ for NA = 0.3 as 545 mm⁻¹, but your own definition gives 1091 mm⁻¹ — please correct the example or remove it. (2) "λ < 1 µm (above the optical cutoff)" contradicts the 2000 mm⁻¹ cutoff stated earlier. (3) The decision matrix recommends optical for σ > 50 nm, but the 180-point sweep ends at 50 nm; state the basis.
**Minor.** "Fourteen automated tests" vs sixteen; Aksulu dataset missing from Data Availability; "RMSE < 20 nm" provenance; fringe count in SI.
**Recommendation:** Minor-to-Major Revision.

### Reviewer 2 — Optical physics
**Major.** (1) Main text says the bound "holds" with a derivation in S4.3, but S4.3 explicitly says it is an ansatz, not a theorem — align the two. (2) The scalar OTF is used throughout the baseline while SI §1.3 quantifies an 8 % vector correction to the effective cutoff; state which convention the numbers use. (3) The public benchmark is strong; please also state the ball-standard cross-check's dataset in Data Availability.
**Minor.** "≈15 % beyond the nominal monochromatic cutoff" wording; SI "Eq. hstylus" broken reference.
**Recommendation:** Minor Revision (conditional on the arithmetic fixes).

### Reviewer 3 — Information theory / signal processing
**Major.** (1) In the trilemma, the explicit $\mathcal{F}$ in S4.3 contains $1/\sigma^2$, so $\sigma^2$ cancels from the right-hand side; the claim that "rougher surfaces" is an independent lever overstates the relation — the lever is SNR. (2) $\eta$ and $B_\mathrm{eq}$ are used to three decimals in the SI stress test but have no formulas anywhere; define them. (3) Ξ guidance in the main text should carry the SI's own caveat that Ξ varies by two orders of magnitude across surface classes.
**Minor.** Dangling "where σ² is the total surface variance" before the water-filling solution; "capacity" terminology note is appreciated.
**Recommendation:** Major Revision.

**Panel aggregate:** one Major, one Minor, one Major — the first-round outcome is driven entirely by **C1 (arithmetic), C2 (bound status), H2 (trilemma)** and the reviewer-visible staleness items. All are textual fixes of under half a day total. Without them: Major Revision likely. With them: Minor Revision / Accept-with-minor-changes is the modal outcome.

---

## PHASE 10 — FINAL ACTION PLAN (Top-20, highest acceptance gain first)

Estimates: Sci (1–5), Rev (1–5), Diff (1–5), Time (h), Gain (0–5).

| # | Action | Sci | Rev | Diff | Time | Gain |
|---|---|---|---|---|---|---|
| 1 | **C1:** Correct the scaling-law example: $f_{c,o}(\mathrm{NA}=0.3) = 1091$ mm⁻¹, ratio 17.1, ratio^1.9 ≈ 2.2×10²; second example ratio ≈ 1.7 → ≈2.8. | 3 | 5 | 1 | 0.25 | +4 |
| 2 | **C2:** Change "the following bound holds" to "the following metrological bound is adopted" (align with S4.3 ansatz status). | 2 | 4 | 1 | 0.2 | +3 |
| 3 | **H1:** "fourteen automated tests" → "sixteen automated tests". | 1 | 3 | 1 | 0.1 | +2 |
| 4 | **H3:** "λ < 1 µm (above the optical cutoff)" → "λ < 0.5 µm (above the optical cutoff of 2000 mm⁻¹)". | 2 | 3 | 1 | 0.1 | +2 |
| 5 | **H2:** Reword trilemma interpretation: the lever is SNR (σ enters through SNR; the explicit $\mathcal{F}$ cancels σ²). | 3 | 3 | 2 | 0.5 | +2.5 |
| 6 | **H4:** Add to the Ξ paragraph: "with the reference surface class specified, since Ξ varies by up to two orders of magnitude across classes (SI §3)". | 1 | 3 | 1 | 0.2 | +2 |
| 7 | **M3:** Add Aksulu dataset (Zenodo 10.5281/zenodo.4471347, CC-BY-4.0) to Data Availability. | 1 | 3 | 1 | 0.1 | +1.5 |
| 8 | **M6:** One-line formulas for $\eta = I/C_\mathrm{noise-free}$ (or MMSE equivalent) and $B_\mathrm{eq}$ in the practitioner-table footnote. | 2 | 2 | 1 | 0.3 | +1.5 |
| 9 | **M2:** Mark decision-matrix rows requiring extrapolation; give the σ-sweep as the basis for σ>50 nm; cite provenance of "RMSE < 20 nm". | 1 | 3 | 1 | 0.3 | +2 |
| 10 | **M7:** Fix "Eq.~hstylus" and "Eq.~(metrological uncertainty bound)" to plain-text cross-references. | 1 | 2 | 1 | 0.2 | +1 |
| 11 | **M8:** State the water-filling constraint $\iint S_h\,d^2\!f = \sigma^2$ before "The solution---". | 2 | 2 | 1 | 0.2 | +1 |
| 12 | **M4:** "has not been quantified previously" → "has not, to the best of our knowledge, been quantified". | 1 | 2 | 1 | 0.1 | +1 |
| 13 | **M9:** One SI sentence: SI §1 constants follow from the displayed equations with the stated parameters (no code required). | 1 | 2 | 1 | 0.2 | +1 |
| 14 | **M1:** Append "(N=512)" at the first headline use of 9.6 % in Results. | 1 | 2 | 1 | 0.1 | +1 |
| 15 | **M10:** One clause reconciling the 0.1 %-σ simulated floor with the SI budget's 0.5/1.0 nm base noise. | 1 | 2 | 1 | 0.2 | +1 |
| 16 | **M5:** "four manufactured classes" → "four surface classes" (abstract). | 1 | 1 | 1 | 0.1 | +0.5 |
| 17 | **Low:** fringe count "approximately 9" → drop the count or use 11. | 1 | 1 | 1 | 0.1 | +0.5 |
| 18 | **Low:** Methods clause that the baseline keeps the scalar OTF with vector corrections quantified in SI. | 1 | 2 | 1 | 0.2 | +1 |
| 19 | Rebuild all three PDFs; re-run 16/16 tests; commit. | 1 | 2 | 1 | 0.5 | +2 |
| 20 | Cover letter: re-check every number after items 1–16 (esp. the example and test count). | 1 | 1 | 1 | 0.2 | +0.5 |

**Conclusion.** Total effort ≈ 3–4 h, no new mathematics, no new simulations, no length increase (net ≈ ±0.2 pp). Items 1–8 remove the two Criticals and four Highs; the remainder are one-line proofreading-grade fixes. Expected effect: first-round decision moves from likely **Major Revision** (driven by the arithmetic and bound-status findings) to **Minor Revision / Accept-with-minor-changes**; desk-rejection risk unchanged (~10–15 % at STMP); acceptance-after-review at STMP rises from ~70–75 % toward ~80 %.
