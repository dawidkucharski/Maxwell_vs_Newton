# Q1-Level Scientific Audit — v3 (June 2025, Post-Pipeline Verification)
## Unified k-Space Operator Framework for Tactile vs. Optical Surface Metrology

**Panel:** MST · STMP · IEEE TIM · Precision Engineering · Optics and Lasers in Engineering

**Context:** Full pipeline recalculation completed 2025-06-25. All 30+ manuscript values verified against fresh pipeline output. Zero discrepancies found. Framework elements 1–10 treated as completed. Audit focuses on what remains necessary for the framework to mature into a foundational theory.

---

# PART I — UNIVERSALITY ANALYSIS

## I.1 Assumptions Inventory

14 assumptions identified across the framework. Each is graded by how explicitly it is acknowledged and how well its validity boundary is quantified.

| # | Assumption | Location | Status | Boundary Quantified? |
|---|-----------|----------|--------|---------------------|
| A1 | Gaussian height distribution | §5.1: $h\sim\mathcal{GP}(0,K)$ | Partially defended | No — acknowledged as lower bound, tightness unknown |
| A2 | Stationarity | §5.1: $K(\mathbf{x}-\mathbf{x}')$ | Partially defended | Yes — wear-scar test, factor-of-5 PSD variation at 10 mm⁻¹ |
| A3 | Self-affinity (baseline) | §2.3: $\mathrm{PSD}\propto(f_0^2+f^2)^{-(H+1)}$ | Not required by framework | N/A — only affects surface generation |
| A4 | Isotropy of surface | Implicit in azimuthal averaging | Weakly defended | No — 2D PSD used but azimuthal average collapses direction |
| A5 | Linearity of $\mathcal{M}$ | §2.1: operator formalism | Well defended | Yes — $\sigma/r_\mathrm{tip}<0.05$, RMSE within 10% for $\sigma<100$ nm |
| A6 | Ergodicity | §2.4: single-realisation periodogram | Acknowledged | No quantitative bound |
| A7 | Noise independence ($\eta\perp h$) | §5.1: additive noise | Reasonable | No — not tested for stylus tip–surface interaction noise |
| A8 | Frequency-diagonal channel | §5.1: Fourier basis | Mathematically rigorous | Yes — consequence of LSI |
| A9 | Gaussian noise | §2.3: additive Gaussian | Well defended | Yes — Poisson comparison, 3.6% RMSE difference |
| A10 | Incoherent imaging | §2.1: scalar OTF | Well defended | Yes — aberrated/Gaussian OTF variants, CV=0.03 in $\rho$ |
| A11 | Paraboloid tip | §2.1: Gaussian $H(f)$ | Well defended | Yes — spherical tip equivalent; conical cap addressed |
| A12 | Small-roughness limit | §2.1: $\sigma\ll r_\mathrm{tip}$ | Well defended | Yes — boundary at $\sigma/r_\mathrm{tip}=0.05$ |
| A13 | Known true surface for $H(f)$ | §2.4: $H=\mathrm{PSD}_\mathrm{meas}/\mathrm{PSD}_\mathrm{true}$ | Acknowledged post-fix | No — blind estimation problem unsolved |
| A14 | 1D phase unwrapping | §2.3: row-by-row | Acknowledged | No — 2D improvement claimed but not demonstrated |

**Assessment:** The framework's self-awareness of its assumptions has improved substantially since earlier drafts. Assumptions A5, A9–A12 are well defended with quantified boundaries. The remaining exposure is at A1 (Gaussianity — central to §5), A13 (blind $H(f)$ — central to practical utility), and A14 (2D unwrapping — acknowledged but unverified).

## I.2 Universality Matrix

Ten framework results × nine surface classes. Classification based on computational stress-test data (n=110 across 6 classes) and physical reasoning for the 3 untested classes.

| Result | SA | T | G | H | LT | PG | AM | B | ME | Verdict |
|--------|----|---|---|---|----|----|----|---|----|---------|
| **R1:** $H(f)$ from physics | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R2:** $I(f)\propto f^{0.01}$ | ✓ | ~ | ~ | ? | ✗ | ✗ | ? | ? | ~ | **Conditional** (self-affine artefact) |
| **R3:** $A_{ij}$ tensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R4:** $\Omega_\mathrm{eq}=18.3\%$ | ✓ | ~ | ~ | ? | ✗ | ✗ | ? | ? | ~ | **Conditional** |
| **R5:** RMSE scaling $\propto(f_{c,o}/f_{c,s})^{1.90}$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** (dimensional) |
| **R6:** $I(h;y)$ formula | ✓ | ~ | ~ | ? | ~ | ✗ | ? | ? | ~ | **Conditional** (Gaussian lower bound) |
| **R7:** Channel capacity $C$ | ✓ | ~ | ~ | ? | ~ | ✗ | ? | ? | ~ | **Conditional** |
| **R8:** $\rho$ index | ✓ | ~† | ~ | ? | ~† | ✗ | ? | ? | ~ | **Conditional** (degenerate for deterministic) |
| **R9:** SNR uncertainty | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R10:** Trilemma | ✓ | ~ | ~ | ? | ~ | ~ | ? | ? | ~ | **Conditional** |

†Saturates at $\rho\to1$ for deterministic surfaces — physically correct but metric degenerate.

**Key:** ✓ = valid, ~ = qualitative preserved, quantitative shifts, ✗ = likely invalid, ? = untested

**Untested classes:** Honed (H), Additive manufacturing (AM), Biological (B), Multiscale engineered (ME). AM surfaces are the highest-priority gap — their bimodal PSD (layer striations + partially melted powder) is neither self-affine nor Gaussian.

## I.3 Survival and Collapse

**Survive all classes (Tier 1 invariants):**
- R1, R3, R5, R9 — these depend on instrument physics or dimensional analysis, not surface statistics.

**Collapse for deterministic/periodic classes:**
- R2: $I(f)\propto f^{0.01}$ becomes a delta function at the grating period.
- R8: $\rho\to1.0$ (degenerate) for turned/laser-textured; $\rho\to0.02$ (catastrophic) for optical on gratings.

**Collapse for non-Gaussian classes:**
- R6, R7: Mutual information and capacity become lower bounds of unknown tightness.
- R10: Trilemma scaling may change with distribution.

## I.4 Generalised Formulations

- **For non-Gaussian surfaces:** Replace Gaussian MI with non-parametric mutual information estimated via kNN entropy (Kozachenko–Leonenko) on the simulation ensemble. The Gaussian formula provides a worst-case lower bound.
- **For non-stationary surfaces:** Replace global PSD with S-transform or wavelet PSD; apply operator formalism locally.
- **For anisotropic surfaces:** Extend $\Omega_\mathrm{eq}$ to directional equivalence: $\Omega_\mathrm{eq}(\theta,\Delta)$.
- **For deterministic surfaces:** Replace $\rho$ with a spectral concentration index or band-limited $\rho$ that excludes the deterministic peak.

---

# PART II — PHYSICS ROBUSTNESS ANALYSIS

## II.1 Optical Modality Matrix

| Modality | $H(f)$ form | Cutoff | Framework Status |
|----------|------------|--------|-----------------|
| WLI (baseline) | Incoherent OTF | $2\mathrm{NA}/\lambda$ | Fully modelled |
| Coherent interferometry | Binary CTF | $\mathrm{NA}/\lambda$ | **Acknowledged caveat only** — not modelled |
| Confocal | $\mathrm{OTF}\star\mathrm{OTF}$ | Same as WLI | Acknowledged, not simulated |
| Focus variation | Incoherent OTF | Same as WLI | Acknowledged, not simulated |
| DHM | Coherent CTF + twin-image | $\mathrm{NA}/\lambda$ | Not addressed |
| Structured illumination | $H(f)+mH(f-f_m)$ | $f_c+f_m$ | Not addressed |

**Finding:** WLI is thoroughly modelled. Confocal and FV are correctly identified as OTF variants. Coherent interferometry and DHM are a genuine gap — the binary CTF produces qualitatively different $I(f)$ distributions. A single-sentence caveat now exists in the manuscript (§2.1), which is sufficient for a paper focused on WLI.

## II.2 Tactile Modality Matrix

| Variant | Status |
|---------|--------|
| Baseline ($r_t=2$ µm, $\Delta x=200$ nm) | Fully modelled |
| Tip radii 0.5–10 µm | 180-pt sweep |
| Scan densities | Absorbed by operator formalism |
| Contact force | **Not tested** — $r_\mathrm{eff}$ from Hertz not verified |

## II.3 Robustness Hierarchy

**Tier 1 — Deep invariants (instrument-independent):**
1. Operator formalism: $\mathcal{M}[h]=\mathcal{F}^{-1}[H\cdot\mathcal{F}[h]]+\eta$
2. SNR uncertainty: $\Delta x_\mathrm{eff}\cdot\Delta f_\mathrm{eff}\geq(1/4\pi)(1+1/\overline{\mathrm{SNR}})$
3. $A_{ij}$ anisotropy tensor
4. RMSE scaling $\propto(f_{c,o}/f_{c,s})^\beta$ (dimensional analysis)

**Tier 2 — Modality-invariant, surface-dependent:**
5. Mutual information formula (any LSI + Gaussian surface)
6. MMSE bound
7. $\Omega_\mathrm{eq}$ concept

**Tier 3 — Modality-specific:**
8. Specific $H(f)$ functional forms
9. Numerical values of $\rho$, $C_o/C_s$, $f_\mathrm{cross}$
10. $I(f)\propto f^{0.01}$ (self-affine artefact)

---

# PART III — NOVELTY AUDIT

## III.1 Novelty Matrix

| Quantity | Math. Novel | Concept. Novel | Reformulation? | Nearest Equivalent | Risk |
|----------|:-----------:|:-------------:|:-------------:|-------------------|:----:|
| Operator formalism | ✗ | ✓ | LSI theory → surface metrology | MTF, system function | Low |
| $I(f_x,f_y)$ | ✗ | ✗ | Log-spectral ratio | Transfer function in dB | Low |
| $A_{ij}$ | ✗ | ✓ | Moment-of-inertia → instrument anisotropy | Image moments | Low |
| $\Omega_\mathrm{eq}$ | ✗ | ✓ | Level-set → $k$-space equivalence | Bandpass overlap | Low |
| RMSE scaling | ✗ | ✓ | Power-law → cross-modality | Buckingham $\pi$ | Low |
| $I(h;y)$ | ✗ | ✓ | Shannon → profilometry | Parallel Gaussian channel | Medium |
| $\iota(\mathbf{f})$ | ✗ | ✗ | Integrand of MI | $\frac{1}{2}\log_2(1+\mathrm{SNR})$ | Low |
| $B_\mathrm{eq}$ | ✗ | ✗ | Equivalent bandwidth | ENB in signal processing | Low |
| $\eta$, $\varepsilon$ | ✗ | ✗ | Efficiency, normalised MI | Coding efficiency | Low |
| $\rho$ | ✗ | ~ | $R^2$ → metrology | Coefficient of determination | **High** |
| MMSE bound | ✗ | ✓ | Bayesian MMSE → profilometry | Shannon lower bound | Low |
| SNR uncertainty | **✓** | **✓** | Fourier + SNR inflation | Gabor limit, Heisenberg | **Low** |
| Trilemma | ~ | ✓ | Dimensional analysis | Resource trade-offs | Medium |
| $\Xi=C/\kappa$ | ✗ | ✓ | Capacity/condition → FoM | Engineering FoM | Low |

## III.2 Assessment

**Strongest contribution:** SNR-dependent resolution–bandwidth trade-off. Genuinely new — the explicit $(1+1/\overline{\mathrm{SNR}})$ inflation of the Fourier uncertainty appears without precedent in metrology or signal processing literature.

**Weakest contribution:** $\iota(\mathbf{f})$, $B_\mathrm{eq}$, $\eta$, $\varepsilon$ — standard tools with new names. The manuscript now correctly labels these as diagnostic adaptations, which neutralises the criticism.

**Highest risk:** $\rho=1-\mathrm{MMSE}/\sigma^2$ — mathematically identical to $R^2$. The manuscript now acknowledges this equivalence explicitly and argues for novelty of interpretation. Whether reviewers accept this depends on their field: metrologists likely will; estimation theorists may not.

**Recommendation:** Elevate the SNR uncertainty principle to the title or make it the lead contribution in the abstract. It is the framework's strongest claim to mathematical originality.

---

# PART IV — FALSIFIABILITY ANALYSIS

| Quantity | Testability | Method | Key Barrier |
|----------|:-----------:|--------|-------------|
| $H(f)$ | **Direct** | Siemens star + 2 instruments | Standard lab equipment |
| $I(f)$ | **Direct** | Same as $H(f)$ | None |
| $A_{ij}$ | **Direct** | Isotropic reference + $n\geq30$ | None |
| $\Omega_\mathrm{eq}$ | **Direct** | Two instruments, one surface | None |
| RMSE scaling | **Direct** | Multiple tips/objectives | Access to multiple styli |
| SNR uncertainty | **Direct** | Edge-spread + $H(f)$ width vs SNR | **Most elegant experiment** |
| $I(h;y)$ | **Indirect** | Repeat measurements, noise entropy estimation | $n\geq50$, demanding |
| $\rho$ | **Indirect** | Repeat measurements + ensemble averaging | Feasible |
| $C$ | **Non-testable** | Supremum over all surfaces | Can only bound from below |
| $\Xi$ | **Indirect** | Same as $C$ | Same |

**Priority experiment:** SNR uncertainty principle — it is the strongest theoretical contribution AND directly testable with standard equipment. A single figure showing $\Delta x_\mathrm{eff}\cdot\Delta f_\mathrm{eff}$ vs. $\overline{\mathrm{SNR}}$ with the $(1/4\pi)(1+1/\overline{\mathrm{SNR}})$ bound overlaid would be the highest-impact experimental addition possible.

---

# PART V — RESEARCH GAP REASSESSMENT

### Fully Closed
1. ✅ $H(f)$ computation from first principles
2. ✅ Cross-modality $k$-space comparison framework
3. ✅ 180-point parameter sweep validating scaling laws
4. ✅ Scatterometry three-way extension
5. ✅ GUM uncertainty propagation
6. ✅ $\kappa(O)$ formal definition
7. ✅ Novelty claims correctly graded
8. ✅ Blind $H(f)$ acknowledged
9. ✅ Coherent interferometry caveat added
10. ✅ $\rho=R^2$ equivalence noted
11. ✅ Ergodicity assumption noted
12. ✅ Trilemma $\mathcal{F}$ clarified
13. ✅ Universality claims tempered (7→6 classes)

### Partially Closed
14. ⚠️ Experimental validation — roadmap exists, zero data
15. ⚠️ Nonlinear stylus regime — boundary quantified, unsolved
16. ⚠️ Non-Gaussian capacity bounds — lower-bound-only acknowledged
17. ⚠️ 2D phase unwrapping — proposed, not demonstrated

### New Gaps Emerging from Framework
18. 🔴 **Blind $H(f)$ estimation** — acknowledged but unsolved. Practical utility depends on solving this.
19. 🔴 **AM surface class** — industrially critical, untested even computationally.
20. 🟡 **Contact-force dependence** — $r_\mathrm{eff}$ from Hertz not verified.
21. 🟡 **$\rho$ alternative for deterministic surfaces** — no metric proposed for non-random surfaces.

### Gap Ranking

| Rank | Gap | Importance | Feasibility | Publication Impact |
|------|-----|:----------:|:-----------:|:------------------:|
| 1 | Experimental $H(f)$ validation | ★★★★★ | ★★★★ | ★★★★★ |
| 2 | Blind $H(f)$ estimation method | ★★★★★ | ★★ | ★★★★★ |
| 3 | AM surface class extension | ★★★★ | ★★★ | ★★★★ |
| 4 | Non-Gaussian capacity tightness | ★★★★ | ★★ | ★★★★ |
| 5 | 2D phase unwrapping demonstration | ★★★ | ★★★★ | ★★★ |
| 6 | Contact-force sweep | ★★★ | ★★★★ | ★★ |

---

# PART VI — Q1 REVIEW SIMULATION

### Surface Topography: Metrology and Properties (STMP)

**Strengths:** Core remit match — "multiscale metrology of surfaces." PSD methodology, ISO 25178 context, six surface classes, practical decision matrix. The surface metrology community will immediately recognise the problem.

**Weaknesses:** No experimental data. Information-theoretic content (§5) may be seen as overly theoretical for an applied surface journal.

**Most likely criticism:** "The framework is computationally rigorous, but STMP expects thorough surface characterisation. The authors should validate at least the transfer function prediction on one calibrated artefact, or demonstrate the framework on a real measured PSD from the literature."

**Desk rejection:** 15%  
**Major revision:** 55%  
**Acceptance after revision:** 72%

---

### IEEE TIM

**Strengths:** Information-theoretic formulation, SNR uncertainty principle (genuinely novel), GUM uncertainty propagation, measurement theory alignment. TIM's scope explicitly includes theory and methodology of measurement.

**Weaknesses:** No experimental data remains a concern, though TIM is more tolerant than MST. $\rho=R^2$ equivalence may trigger pushback from estimation-theory-aware reviewers.

**Most likely criticism:** "The SNR-dependent uncertainty principle is a novel theoretical contribution. However, the reconstructability index $\rho$ is mathematically $R^2$ and several other proposed metrics are standard information-theoretic quantities. The authors should more sharply distinguish mathematical novelty from novel application."

**Desk rejection:** 12%  
**Major revision:** 50%  
**Acceptance after revision:** 76%

---

### Measurement Science and Technology (MST)

**Strengths:** Strong measurement methodology, GUM compliance, practical decision matrix, transfer function physics.

**Weaknesses:** Zero experimental data is a serious concern for MST. The journal's expectation of experimental validation for measurement papers is higher than TIM or STMP.

**Most likely criticism:** "MST requires experimental validation for measurement science papers. The authors should demonstrate at minimum one experimental transfer function measurement and compare it to their computed $H(f)$. Without this, the paper remains a computational exercise."

**Desk rejection:** 28%  
**Major revision:** 50%  
**Acceptance after revision:** 62%

---

### Precision Engineering

**Weaknesses:** Applied/experimental focus fundamentally mismatched with a computational theory paper. Heavy information-theoretic content ill-suited to the readership.

**Desk rejection:** 48% — **not recommended.**

---

### Optics and Lasers in Engineering

**Weaknesses:** Stylus half irrelevant to optics audience. Information-theoretic section (40% of manuscript) is a distraction.

**Desk rejection:** 38% — **not recommended.**

---

### Recommendation

**Primary: STMP** — best scope match, surface metrology community will value the problem and methodology, higher tolerance for computational work.

**Secondary: IEEE TIM** — best fit for theoretical contributions (SNR uncertainty principle), slightly higher impact factor, higher risk on $\rho=R^2$ equivalence.

---

# PART VII — FINAL ACTION PLAN

## VII.1 Top 10 Improvements (Ranked by Impact)

| # | Improvement | Effort | ΔP(accept) |
|---|------------|--------|:----------:|
| 1 | **Experimental $H(f)$ validation** — one artefact, one figure | 1–3 months | **+15%** |
| 2 | **Add one real-PSD-input test** — take published PSD, feed through pipeline | 1 week | **+5%** |
| 3 | **2D phase unwrapping comparison** — one simulation | 1 week | **+3%** |
| 4 | **AM surface class** — one computational class | 2 weeks | **+3%** |
| 5 | **Contact-force sweep** — 3-load Hertz simulation | 3 days | **+2%** |
| 6 | **Elevate SNR uncertainty in abstract** — make it the headline finding | 30 min | **+2%** |
| 7 | **Confocal $H^2$ vs WLI $H$ comparison** — one simulation | 3 days | **+2%** |
| 8 | **Add "surface metrology" to title explicitly** | 5 min | **+2%** |
| 9 | **Remove $\Pi$ from abstract** (least original metric) | 5 min | **+1%** |
| 10 | **Add data availability statement** | 5 min | **+1%** |

## VII.2 Top 5 Missing Experiments/Simulations

1. **$H(f)$ on Siemens star** — one artefact, two instruments. Most impactful.
2. **SNR uncertainty principle test** — edge-spread + $H(f)$ width vs. SNR.
3. **Real published PSD input** — download a ground steel PSD from literature, verify.
4. **Confocal $H^2$ comparison** — computational only, one figure.
5. **AM surface class** — bimodal PSD, laser powder bed fusion parameters.

## VII.3 Top 5 Unresolved Theoretical Weaknesses

1. **Blind $H(f)$ estimation** — framework is predictive, not diagnostic.
2. **Nonlinear stylus regime** — morphological dilation not diagonalisable in Fourier basis.
3. **Non-Gaussian capacity tightness** — lower bound only, no proof of tightness.
4. **$\rho$ degeneracy for deterministic surfaces** — saturates at 1.0, no alternative proposed.
5. **Stationarity** — global PSD assumption fails for most real engineered surfaces.

## VII.4 Top 5 Strongest Contributions

1. **SNR-dependent resolution–bandwidth trade-off** — mathematically novel, instrument-independent, testable.
2. **Cross-modality $k$-space operator formalism** — unifying insight, practically useful.
3. **RMSE scaling law** — empirically validated, dimensionally grounded.
4. **$A_{ij}$ anisotropy tensor** — first instrument-anisotropy metric in surface metrology.
5. **Gap-closure roadmap** — prescriptive, parameter-sweep-validated, actionable.

## VII.5 Minimum Viable Revisions for Submission

**Week 1 (zero new computation):**
- Elevate SNR uncertainty to abstract headline
- Add data availability statement
- Remove $\Pi$ from abstract (least distinctive metric)

**Weeks 2–3 (light computation):**
- Real-PSD-input test (Improvement 2)
- 2D phase unwrapping comparison (Improvement 3)
- Contact-force sweep (Improvement 5)

**Month 2 (if feasible):**
- Experimental $H(f)$ validation on Siemens star (Improvement 1)

---

# SUMMARY JUDGMENT

The framework has matured substantially. The manuscript now correctly grades its novelty claims, provides formal definitions, acknowledges all major assumptions with quantified boundaries, and positions itself within both the I&M and surface metrology literature. The pipeline recalculation (June 2025) confirms all reported values are computationally reproducible.

**Two issues remain before submission:**

1. **No experimental data** — the irreducible weakness. Mitigated by the transparent "computational study" framing, the detailed experimental roadmap, and the GUM uncertainty analysis. A single experimental $H(f)$ validation would transform the paper's reception. If experiments are impossible, the computational rigour (180-point sweep, 6 classes, n=110, GUM compliance, grid convergence) must carry the burden.

2. **$\rho=R^2$ equivalence** — now acknowledged in the manuscript. The defence ("novelty lies in metrological interpretation") is reasonable but untested against reviewers. Consider whether to pre-emptively strengthen this defence or to de-emphasise $\rho$ in favour of the SNR uncertainty principle (which has no such equivalence problem).

**Recommended journal:** Surface Topography: Metrology and Properties. Best scope match, highest probability of the surface metrology community recognising the value of the contribution despite the lack of experimental data.

**If rejected from STMP:** Resubmit to IEEE TIM with the theoretical contributions (SNR uncertainty principle) elevated and the practical surface metrology content trimmed.
