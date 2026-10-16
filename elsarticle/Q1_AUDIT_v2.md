# Q1-Level Scientific Audit — FRESH ASSESSMENT (June 2026)
## Unified k-Space Operator Framework for Tactile vs. Optical Surface Metrology

**Panel:** MST · STMP · IEEE TIM · Precision Engineering · Optics and Lasers in Engineering

**Manuscript state:** 45 pages, 33 references, 10 framework elements, 0 LaTeX warnings. All non-experimental Q1 audit fixes applied (novelty claims graded, absolute capacity values dropped, $\kappa(O)$ formally defined, GUM uncertainty propagation added, $H_c$ replaced with $\rho$-based guidance).

---

# PART I — UNIVERSALITY ANALYSIS

## I.1 Assumptions Inventory

14 assumptions identified, graded by explicitness and testability:

| # | Assumption | Type | Defensibility |
|---|-----------|------|---------------|
| A1 | **Gaussian height distribution** — $h \sim \mathcal{GP}(0,K)$ in §5.1 | Explicit modelling choice | Partially defended: acknowledged as lower bound for non-Gaussian surfaces, but no quantitative bound tightness demonstrated |
| A2 | **Stationarity** — $K(\mathbf{x}-\mathbf{x}')$ depends only on separation | Explicit | Acknowledged in Limitations (§4.5), wear-scar counterexample tested, local spectral methods proposed as remedy |
| A3 | **Self-affinity** — PSD $\propto (f_0^2+f^2)^{-(H+1)}$ baseline | Explicit (baseline only) | Not required by framework — only affects surface generation. Framework works for arbitrary $S_h(f)$ |
| A4 | **Isotropy of the surface** (implicit in azimuthal averaging) | Implicit | Partially addressed: 2D PSD and anisotropy tensor capture directional effects; azimuthal average is a visualisation choice |
| A5 | **Linearity of $\mathcal{M}$** | Explicit, tested | Defended: $\sigma/r_\mathrm{tip}=0.025$ at baseline, linearity holds within 10% for $\sigma<100$ nm. Nonlinear regime acknowledged as limitation |
| A6 | **Ergodicity** — single-realisation periodogram | Implicit | Not discussed. Ensemble statistics ($n=110$) partially address this but PSD estimation from single realisations remains an implicit ergodicity assumption |
| A7 | **Additive noise independence** — $\eta \perp h$ | Explicit | Reasonable for thermal/electronic noise. Less defensible for stylus tip--surface interaction noise |
| A8 | **Frequency-diagonal channel** — Fourier basis diagonalises | Explicit (from LSI) | Mathematically rigorous consequence of LSI + stationary surface |
| A9 | **Gaussian noise** — additive Gaussian camera/electronic noise | Explicit, tested | Defended: Poisson comparison shows 3.6% RMSE difference. Stylus vibration noise may not be Gaussian |
| A10 | **Incoherent imaging** — scalar OTF for circular aperture | Explicit, tested | Defended: aberrated OTF, Gaussian OTF variants tested, CV=0.03 in $\rho$. Vector diffraction at high NA acknowledged in Supplementary |
| A11 | **Paraboloid tip** — $H_\mathrm{stylus} \approx \exp[-2\pi^2 r_t^2 f^2]$ | Explicit, tested | Defended: true spherical tip differs only in roll-off steepness. Conical+spherical cap tip addressed |
| A12 | **Small-roughness limit** — $\sigma \ll r_\mathrm{tip}$ | Explicit, tested | Boundary quantified: $\sigma/r_\mathrm{tip} < 0.05$ |
| A13 | **Single-surface $H(f)$ estimation** — $H$ from one PSD ratio | Implicit | **Not addressed.** In practice, $H(f)$ must be estimated without knowledge of true PSD (blind problem). Yashchuk calibration gratings are the experimental solution but no computational blind-estimation method is proposed |
| A14 | **Continuous phase** — 1D phase unwrapping model | Implicit | Acknowledged: 1D used, 2D proposed as improvement. Not demonstrated |

**New concern not in previous audit:** A13 (blind $H(f)$ estimation) and A6 (ergodicity) are implicit assumptions with no discussion. A13 is the more serious — the framework's central practical claim ("compute $H(f)$ from first principles") implicitly assumes knowledge of the true surface PSD, which is unavailable in real measurements.

## I.2 Universality Matrix (Current State)

**Surface classes:** SA = Gaussian self-affine, T = Turned, G = Ground, H = Honed, LT = Laser-textured, PG = Periodic grating, AM = Additive manufacturing, B = Biological, ME = Multiscale engineered

| Framework Result | SA | T | G | H | LT | PG | AM | B | ME | Verdict |
|-----------------|----|---|---|---|----|----|----|---|----|---------|
| **R1:** $H(f)$ from first principles | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R2:** $I(f) \propto f^{0.01}$ | ✓ | ~ | ~ | ? | ✗ | ✗ | ? | ? | ~ | **Conditionally valid** (self-affine artefact) |
| **R3:** $A_{ij}$ anisotropy tensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R4:** $\Omega_\mathrm{eq}$ = 18.3% | ✓ | ~ | ~ | ? | ✗ | ✗ | ? | ? | ~ | **Conditionally valid** |
| **R5:** RMSE scaling $\propto (f_{c,o}/f_{c,s})^{1.90}$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** (dimensional analysis) |
| **R6:** $I(h;y)$ mutual information formula | ✓ | ~ | ~ | ? | ~ | ✗ | ? | ? | ~ | **Conditionally valid** (Gaussian lower bound) |
| **R7:** Channel capacity $C$ | ✓ | ~ | ~ | ? | ~ | ✗ | ? | ? | ~ | **Conditionally valid** |
| **R8:** $\rho$ reconstructability index | ✓ | ~† | ~ | ? | ~† | ✗ | ? | ? | ~ | **Conditionally valid** (degenerate for deterministic) |
| **R9:** SNR resolution–bandwidth trade-off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R10:** Info–energy–resolution trilemma | ✓ | ~ | ~ | ? | ~ | ~ | ? | ? | ~ | **Conditionally valid** |

†Saturates at $\rho=1.0$ for deterministic surfaces — physically correct but metric degenerate.

**Key:** ✓ = valid, ~ = partially valid (quantitative values shift), ✗ = likely invalid, ? = untested

### Critical universality gaps:
1. **Honed, AM, biological, and multiscale engineered surfaces are entirely untested** — even computationally. The framework's claim of "seven surface classes tested" actually covers six (Gaussian SA + five manufactured), with honed and AM being the most important missing classes for industrial relevance.
2. **R2, R4, R6, R7, R8, R10 are all conditioned on Gaussian statistics.** For non-Gaussian surfaces, the mutual information formula is a lower bound of unknown tightness. A quantitative bound on the gap between Gaussian MI and true MI for non-Gaussian surfaces would substantially strengthen universality.
3. **R8 ($\rho$) is degenerate for deterministic surfaces.** The manuscript now acknowledges this (post-edit) but no alternative metric is proposed for periodic/deterministic surfaces.

---

# PART II — PHYSICS ROBUSTNESS ANALYSIS

## II.1 Optical Modality Matrix

| Modality | $H(f)$ type | Cutoff $f_c$ | Axial physics | Framework coverage |
|----------|------------|-------------|---------------|-------------------|
| **Coherent interferometry** | Coherent CTF (binary) | $\mathrm{NA}/\lambda$ | $2\pi$ phase ambiguity | Not modelled. CTF differs fundamentally from OTF — binary vs. gradual roll-off |
| **White-light interferometry** | Incoherent OTF | $2\mathrm{NA}/\lambda$ | Coherence envelope $l_c$ | **Baseline.** Well modelled |
| **Confocal microscopy** | $\mathrm{OTF} \star \mathrm{OTF}$ | Same as WLI | Pinhole axial sectioning | Acknowledged in Discussion. Not simulated. OTF² gives sharper cutoff — would shift $f_\mathrm{cross}$ and $\Omega_\mathrm{eq}$ |
| **Focus variation** | Incoherent OTF | Same as WLI | Depth-from-defocus | Acknowledged. Not simulated |
| **Digital holographic microscopy** | Coherent CTF | $\mathrm{NA}/\lambda$ | Numerical refocusing, twin-image artefact | Not addressed |
| **Structured illumination** | $H(f) + mH(f-f_m)$ | Extended: $f_c+f_m$ | Moiré down-modulation | Not addressed |

### Optical robustness finding:
The framework correctly acknowledges FV and confocal as sharing the OTF structure, but **this claim is asserted, not demonstrated.** A single computational comparison — running the same surface through a confocal model ($H^2$) vs. WLI model ($H$) — would cost minimal compute and transform "asserted" into "demonstrated."

**Coherent interferometry and DHM are genuine gaps** — the coherent CTF (binary, $H(f)=1$ for $f<f_c$, 0 otherwise) produces fundamentally different information-loss patterns than the incoherent OTF (gradual roll-off). For laser-based interferometers (e.g., phase-shifting at $\lambda=633$ nm), the current WLI model is incorrect. A footnote or caveat would suffice.

## II.2 Tactile Modality Matrix

| Variant | $H(f)$ modification | Tested? | Robustness |
|---------|-------------------|---------|------------|
| Baseline ($r_t$=2 µm, $\Delta x$=200 nm) | Gaussian × sinc | ✓ (baseline) | — |
| Tip radii 0.5–10 µm | $\exp[-2\pi^2 r_t^2 f^2]$ scaled | ✓ (180-pt sweep) | Robust |
| Scan density 100–500 nm | Sinc width scaled | Not independently | Trivial (operator formalism absorbs) |
| Contact force 0.1–10 mN | $r_\mathrm{eff}$ via Hertz | **Not tested** | **Gap** |
| Plastic deformation regime | Nonlinear, state-dependent | Not tested | **Hard gap** |

### Tactile robustness finding:
The contact-force gap is modest — a 3-load sweep (0.1, 1, 10 mN) with Hertz-predicted $r_\mathrm{eff}$ would close it computationally at low cost. The plastic-deformation regime is a hard physics problem beyond the framework's linear scope and is correctly identified as a limitation.

## II.3 Robustness Hierarchy (Current State)

**Tier 1 — Deep invariants (instrument-independent):**
1. Operator formalism $\mathcal{M}[h] = \mathcal{F}^{-1}[H\cdot\mathcal{F}[h]]+\eta$ — holds for any LSI measurement
2. SNR-dependent resolution–bandwidth trade-off — purely Fourier + SNR, independent of instrument physics
3. $A_{ij}$ anisotropy tensor — defined for any $H(f)$, instrument-agnostic
4. Dimensional RMSE scaling $\propto (f_{c,o}/f_{c,s})^\beta$ — follows from Buckingham $\pi$

**Tier 2 — Modality-invariant, surface-dependent:**
5. Mutual information formula (any LSI + Gaussian surface)
6. MMSE bound (same)
7. Equivalence regime concept (any two $H(f)$, any surface)

**Tier 3 — Modality-specific:**
8. Specific $H(f)$ functional forms
9. Numerical values of $\rho$, $C_o/C_s$, $f_\mathrm{cross}$
10. $I(f) \propto f^{0.01}$ scaling

---

# PART III — NOVELTY AUDIT (POST-FIX)

The manuscript now correctly distinguishes three tiers of novelty. This section assesses whether that self-assessment is accurate.

| Quantity | Manuscript claim | Our assessment | Agreement? |
|----------|-----------------|---------------|------------|
| **Operator formalism** | Novel application | ✓ Correct. LSI theory is standard; its systematic application to cross-modality surface metrology comparison is the novel contribution | ✓ |
| **$I(f_x,f_y)$** | Information loss (descriptive) | Reformulation of log-spectral ratio. Useful but not mathematically novel | ✓ (no novelty claim made) |
| **$A_{ij}$** | First instrument-anisotropy metric | ✓ Correct. ISO 25178 covers surface anisotropy, not instrument anisotropy | ✓ |
| **$\Omega_\mathrm{eq}$** | First $k$-space equivalence definition | ✓ Correct. Conceptually simple (level-set of $|H_s-H_o|$) but no prior equivalent in metrology | ✓ |
| **RMSE scaling law** | First cross-modality scaling law | ✓ Correct. Empirically validated, dimensionally grounded | ✓ |
| **$I(h;y)$** | First mutual information for profilometry | ✓ Correct as novel application. The formula itself is Shannon's parallel Gaussian channel — standard. The application is genuinely new | ✓ |
| **$\iota(\mathbf{f})$** | Standard tool adapted as diagnostic | ✓ Correct (post-fix). The manuscript now correctly labels this as the integrand of mutual information | ✓ |
| **$B_\mathrm{eq}$** | Standard tool adapted | ✓ Correct. Equivalent noise bandwidth from signal processing | ✓ |
| **$\eta$, $\varepsilon$** | Standard tools adapted | ✓ Correct. Efficiency and normalised MI are standard concepts | ✓ |
| **$\rho$** | Conceptually novel | ~ Partially correct. $1-\mathrm{MMSE}/\sigma^2$ is mathematically $R^2$ (coefficient of determination). The *application* to surface metrology and the *interpretation* as "reconstructability" is novel. A reviewer from estimation theory would recognise the formula | ⚠️ |
| **MMSE bound** | Novel application | ✓ Correct. Standard Bayesian MMSE formula, first application to profilometry | ✓ |
| **SNR uncertainty principle** | Mathematically novel | ✓ **Strongest original contribution.** Explicit $(1+1/\overline{\mathrm{SNR}})$ inflation of the Fourier uncertainty appears genuinely new | ★ |
| **Trilemma** | Conceptually novel | ~ Dimensional analysis with an unspecified $\mathcal{F}(\overline{\mathrm{SNR}})$ function. The concept is appealing but the derivation is incomplete — $\mathcal{F}$ is not given in closed form | ⚠️ |
| **$\Xi = C/\kappa$** | Conceptually novel | ✓ Correct. The combination of capacity with Gramian condition number as a single FoM is new | ✓ |

### Novelty verdict (post-fix):
- **Strongest contribution:** SNR-dependent resolution–bandwidth trade-off (mathematically novel, experimentally testable, independent of surface/instrument specifics)
- **Weakest contribution:** Information–energy–resolution trilemma (conceptually appealing but mathematically incomplete — $\mathcal{F}(\overline{\mathrm{SNR}})$ not derived)
- **Highest-risk contribution:** $\rho$ — mathematically equivalent to $R^2$, risks "old wine in new bottles" criticism from estimation-theory-aware reviewers. The manuscript's post-fix acknowledgement of degeneracy for deterministic surfaces partially mitigates this.

### Remaining novelty risk:
The trilemma's $\mathcal{F}(\overline{\mathrm{SNR}})$ function is stated as "see Supplementary Material §S4.3" but if that derivation is also incomplete or the function is only empirically fitted, this becomes a significant weakness. The trilemma is presented as a fundamental law ($I \cdot \Delta x^2 \approx \sigma^2 \cdot \mathcal{F}$) but may be a dimensional-analysis observation rather than a derived bound.

---

# PART IV — FALSIFIABILITY ANALYSIS

Falsifiability is the framework's greatest weakness — it remains entirely computational. The experimental roadmap in §4.6 is well-specified but no experiments have been performed.

| Quantity | Testability | Key barrier |
|----------|------------|-------------|
| $H(f)$ | **Directly testable** | Requires calibrated artefact (Siemens star). Standard lab equipment |
| $I(f)$ | **Directly testable** | Same as $H(f)$ |
| $A_{ij}$ | **Directly testable** | Isotropic reference surface + $n\geq30$ repeats. Feasible |
| $\Omega_\mathrm{eq}$ | **Directly testable** | Two instruments, one surface. Feasible |
| RMSE scaling law | **Directly testable** | Multiple tips/objectives needed. Moderate effort |
| $I(h;y)$ | **Indirectly testable** | Requires $n\geq50$ repeat measurements to estimate noise entropy. Demanding |
| $C$ | **Non-testable** | Supremum over all surfaces — can only be bounded from below |
| $\rho$ | **Indirectly testable** | Repeat measurements + ensemble averaging. Feasible |
| SNR uncertainty principle | **Directly testable** | Edge-spread + $H(f)$ width vs. SNR. Elegant experiment |
| $\Xi$ | **Indirectly testable** | Same issues as $C$ |

### Most urgent experiment:
**SNR-dependent uncertainty principle** — it is the framework's strongest theoretical contribution AND directly testable with standard equipment. A single figure showing $\Delta x_\mathrm{eff} \cdot \Delta f_\mathrm{eff}$ vs. $\overline{\mathrm{SNR}}$ with the theoretical bound overlaid would be the highest-impact experimental addition.

---

# PART V — RESEARCH GAP REASSESSMENT (POST-FIX)

### Fully closed:
1. ✅ $H(f)$ computation from first principles (stylus + WLI)
2. ✅ Cross-modality $k$-space comparison framework
3. ✅ 180-point parameter sweep validating scaling laws
4. ✅ Scatterometry extension
5. ✅ GUM uncertainty propagation for $H(f)$ (post-fix)
6. ✅ $\kappa(O)$ formal definition (post-fix)
7. ✅ Novelty claims correctly graded (post-fix)

### Partially closed:
8. ⚠️ **Experimental validation** — roadmap exists, zero data. Remains the #1 weakness
9. ⚠️ **Nonlinear stylus regime** — boundary quantified but not solved
10. ⚠️ **Non-Gaussian capacity bounds** — acknowledged as lower-bound-only
11. ⚠️ **2D phase unwrapping** — proposed, not demonstrated
12. ⚠️ **Vector diffraction at NA>0.7** — in Supplementary, not integrated into main $H(f)$

### New gaps (emergent from the framework):
13. 🔴 **Blind $H(f)$ estimation** — the framework computes $H(f) = \mathrm{PSD}_\mathrm{measured}/\mathrm{PSD}_\mathrm{true}$, which requires knowledge of the true PSD. In practice, neither the true PSD nor $H(f)$ is known. This is a blind deconvolution problem that the framework does not address. Without it, the framework is predictive (given true surface, predict measurement) but not diagnostic (given measurement, estimate $H(f)$).
14. 🔴 **Coherent interferometry gap** — laser-based interferometers (phase-shifting, DHM) use coherent CTF, not incoherent OTF. The binary CTF produces fundamentally different $I(f)$ patterns. A footnote caveat is needed.
15. 🟡 **Trilemma $\mathcal{F}(\overline{\mathrm{SNR}})$ not derived** — if the Supplementary only provides an empirical fit, the trilemma is dimensional analysis, not a derived bound.
16. 🟡 **$\rho$ degeneracy for deterministic surfaces** — acknowledged post-fix, but no alternative metric proposed.
17. 🟡 **Ergodicity in PSD estimation** — single-realisation periodogram implicitly assumes ergodicity. Not discussed.

### Gap ranking:

| Rank | Gap | Importance | Feasibility | Publication impact |
|------|-----|-----------|-------------|-------------------|
| 1 | Experimental $H(f)$ validation | ★★★★★ | ★★★★ | ★★★★★ |
| 2 | Blind $H(f)$ estimation method | ★★★★★ | ★★ | ★★★★★ |
| 3 | Non-Gaussian capacity bound tightness | ★★★★ | ★★ | ★★★★ |
| 4 | Coherent interferometry caveat | ★★★ | ★★★★★ | ★★★ |
| 5 | Trilemma $\mathcal{F}$ derivation | ★★★ | ★★★ | ★★★ |
| 6 | Confocal $H^2$ vs. WLI $H$ comparison | ★★ | ★★★★★ | ★★★ |
| 7 | Contact-force sweep | ★★ | ★★★★ | ★★ |
| 8 | AM surface class | ★★★ | ★★ | ★★★ |
| 9 | $\rho$ alternative for deterministic surfaces | ★★ | ★★★★ | ★★ |
| 10 | Ergodicity discussion | ★ | ★★★★★ | ★ |

---

# PART VI — Q1 REVIEW SIMULATION (POST-FIX)

## VI.1 Measurement Science and Technology

**Strengths:** GUM uncertainty propagation now included; novelty claims correctly graded; practical decision matrix; SNR uncertainty principle is a genuine theoretical contribution.

**Weaknesses:** Zero experimental data remains the dominant weakness. MST expects experimental validation for metrology papers. Blind $H(f)$ estimation problem not addressed.

**Most likely criticism:** "The computational framework is rigorous and the theoretical contributions are clearly delineated. However, MST requires experimental validation for measurement science papers. The authors should demonstrate at minimum one experimental transfer function measurement and compare it to their computed $H(f)$. Additionally, the practical utility of the framework depends on estimating $H(f)$ from measurements without knowledge of the true surface — this blind estimation problem is not addressed."

**Desk rejection:** 25% (down from 40% — GUM + novelty grading reduce risk)
**Major revision:** 55%
**Acceptance after revision:** 65% (up from 60%)

## VI.2 Surface Topography: Metrology and Properties

**Strengths:** PSD-based analysis; seven surface classes; anisotropy tensor; practical decision matrix; $\rho$ degeneracy now acknowledged.

**Weaknesses:** No experimental data; honed and AM surfaces untested even computationally; self-affine baseline limits generality claims.

**Most likely criticism:** "The framework's universality claims are supported by six simulated surface classes, but honed and additively manufactured surfaces — both industrially critical — are absent. The authors should either extend their computational ensemble or temper their universality claims."

**Desk rejection:** 20%
**Major revision:** 55%
**Acceptance after revision:** 70%

## VI.3 IEEE TIM

**Strengths:** Information-theoretic formulation is novel in metrology; SNR uncertainty principle is a genuine theoretical contribution; MMSE bound; channel capacity analysis; novelty claims now correctly self-assessed (post-fix).

**Weaknesses:** $\rho$ is mathematically $R^2$ — estimation-theory-aware reviewers will notice; trilemma $\mathcal{F}(\overline{\mathrm{SNR}})$ not derived; blind $H(f)$ estimation problem is a signal-processing gap that IEEE TIM reviewers would flag.

**Most likely criticism:** "The reconstructability index $\rho = 1-\mathrm{MMSE}/\sigma^2$ is mathematically equivalent to the coefficient of determination $R^2$ in regression. While the application to surface metrology is novel, the authors should explicitly acknowledge this equivalence and clarify what new insight $\rho$ provides beyond the standard $R^2$ interpretation. Additionally, the information–energy–resolution trilemma requires a closed-form expression for $\mathcal{F}(\overline{\mathrm{SNR}})$ to be considered a derived bound rather than dimensional analysis."

**Desk rejection:** 10% (lowest — best theoretical fit)
**Major revision:** 55%
**Acceptance after revision:** 78% (up from 75%)

## VI.4 Precision Engineering

**Strengths:** RMSE scaling law; gap-closure roadmap; decision matrix; 432-point parameter sweep.

**Weaknesses:** Zero experimental data is fatal for Precision Engineering; heavy information-theoretic content ill-suited to applied audience; no connection to ISO GPS tolerancing.

**Most likely criticism:** "This is a theoretical paper submitted to an applied journal. The practical recommendations are useful but entirely unvalidated. Precision Engineering expects experimental confirmation of engineering claims."

**Desk rejection:** 45%
**Major revision:** 40%
**Acceptance after revision:** 45%

### Journal recommendation (unchanged):
**Primary: IEEE TIM** — best theoretical alignment, lowest desk-rejection risk (10%), highest acceptance probability (78%).
**Secondary: STMP** — good fit for surface metrology community.

---

# PART VII — FINAL ACTION PLAN

## VII.1 Top 10 Improvements (ranked by acceptance-probability impact)

| Rank | Action | Effort | ΔP(accept) |
|------|--------|--------|------------|
| 1 | **Add experimental $H(f)$ validation** — one artefact, one figure | 1–3 months | **+15%** |
| 2 | **Address blind $H(f)$ estimation** — one paragraph acknowledging the problem + proposed solution direction (regularised deconvolution, Yashchuk gratings) | 2 hours | **+5%** |
| 3 | **Derive or bound $\mathcal{F}(\overline{\mathrm{SNR}})$ for trilemma** — if empirical, say so; if derivable, derive | 1–3 days | **+3%** |
| 4 | **Add coherent interferometry caveat** — footnote: "laser-based interferometers use a coherent CTF; the present WLI model applies to incoherent broadband sources" | 30 minutes | **+2%** |
| 5 | **Explicitly note $\rho = R^2$ equivalence** — "$\rho$ is the coefficient of determination $R^2$ applied to surface reconstruction; its novelty lies in the metrological interpretation, not the formula" | 30 minutes | **+2%** |
| 6 | **Add confocal $H^2$ comparison** — one simulation, one paragraph in Discussion | 2–3 days | **+2%** |
| 7 | **Temper universality claims for untested classes** — change "seven surface classes tested" to "six classes tested (Gaussian SA + five manufactured); honed and AM surfaces remain for future work" | 30 minutes | **+1%** |
| 8 | **Add contact-force sweep** — three loads, Hertz $r_\mathrm{eff}$, one paragraph | 1–2 days | **+1%** |
| 9 | **Add ergodicity note** — one sentence in PSD estimation methods: "the periodogram estimator assumes ergodicity; for non-stationary surfaces, local spectral methods are required (see Limitations)" | 15 minutes | **+1%** |
| 10 | **Reduce abstract length** — currently ~290 words; trim to 250 for MST/IEEE TIM limits | 30 minutes | **+1%** |

## VII.2 Top 5 Missing Experiments/Simulations

1. **$H(f)$ on Siemens star** — one artefact, two instruments. The single most impactful addition possible.
2. **SNR uncertainty principle test** — measure $\Delta x_\mathrm{eff} \cdot \Delta f_\mathrm{eff}$ vs. SNR. Directly tests the strongest theoretical contribution.
3. **Confocal vs. WLI $H(f)$ comparison** — computational only. Replace OTF with OTF², rerun. One figure.
4. **Real measured PSD input** — take a published PSD, feed through pipeline, verify predictions.
5. **Contact-force sweep** — computational only. Three loads.

## VII.3 Top 5 Unresolved Theoretical Weaknesses

1. **Blind $H(f)$ estimation** — the framework is predictive (true surface → measurement) but real applications need diagnostic (measurement → $H(f)$). This is the deepest theoretical gap.
2. **Nonlinear stylus regime** — morphological dilation is not diagonalisable in Fourier basis. No solution exists in the current framework. This is a hard mathematical problem.
3. **Non-Gaussian capacity bound tightness** — the Gaussian MI formula is a lower bound of unknown tightness for non-Gaussian surfaces. Computing the true capacity requires a difficult variational problem.
4. **Trilemma $\mathcal{F}(\overline{\mathrm{SNR}})$** — presented as a derived law but may be dimensional analysis with an empirical fit. Needs clarification.
5. **Stationarity** — the framework assumes global stationarity but real surfaces rarely satisfy this. Integration with local spectral methods (wavelets) is an open problem.

## VII.4 Top 5 Strongest Contributions (Defend These in Revision)

1. **SNR-dependent resolution–bandwidth trade-off** — mathematically novel, instrument-independent, experimentally testable.
2. **Cross-modality $k$-space operator formalism** — the unifying insight that stylus and WLI are both LSI filters.
3. **RMSE scaling law** $\propto (f_{c,o}/f_{c,s})^{1.90}$ — empirically validated, practically useful.
4. **$A_{ij}$ anisotropy tensor** — first instrument-anisotropy metric in surface metrology.
5. **Gap-closure roadmap** — prescriptive, parameter-sweep-validated, actionable.

## VII.5 Minimum Viable Revisions for Q1 Submission

**Week 1 (text-only, zero new computation):**
- Add blind $H(f)$ estimation acknowledgement (Improvement 2)
- Add coherent interferometry caveat (Improvement 4)
- Note $\rho = R^2$ equivalence (Improvement 5)
- Temper universality claims (Improvement 7)
- Add ergodicity note (Improvement 9)
- Clarify trilemma $\mathcal{F}$ status (Improvement 3)
- Trim abstract to 250 words (Improvement 10)

**Weeks 2–3 (light computation):**
- Confocal $H^2$ vs. WLI $H$ comparison (Improvement 6)
- Contact-force sweep (Improvement 8)

**Months 1–3 (experimental, if feasible):**
- $H(f)$ validation on Siemens star (Improvement 1)

---

# SUMMARY JUDGMENT

**The framework is theoretically sound and makes several genuinely novel contributions.** The post-fix manuscript correctly grades its novelty claims, provides formal definitions for all quantities, and includes GUM-compliant uncertainty analysis.

**Three issues remain before Q1 submission:**

1. **Zero experimental data** — the dominant weakness. Even one experimental $H(f)$ validation transforms acceptance probability from ~65% to ~80%. If experiments are impossible now, the abstract and conclusions must prominently state "computational study; experimental validation roadmap provided" to set reviewer expectations.

2. **Blind $H(f)$ estimation** — the framework's practical utility depends on estimating $H(f)$ from measurements alone (without true PSD). This problem is not addressed. A one-paragraph acknowledgement with proposed solution direction (regularised deconvolution, Yashchuk calibration gratings) would pre-empt a likely reviewer criticism.

3. **$\rho = R^2$ equivalence** — the reconstructability index is mathematically the coefficient of determination. An estimation-theory-aware reviewer at IEEE TIM will notice. Explicitly acknowledging this equivalence and arguing for the metrological interpretation (rather than claiming mathematical novelty) neutralises the criticism.

**Verdict: Minor revision → Resubmit to IEEE TIM.** The 7 text-only improvements in Week 1 above take one afternoon and raise acceptance probability from ~65% to ~75%. With one experimental validation added, acceptance probability reaches ~85%.
