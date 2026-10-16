# Q1-Level Scientific Audit
## Unified k-Space Operator Framework for Tactile vs. Optical Surface Metrology

**Audit Panel:** Measurement Science and Technology · Surface Topography: Metrology and Properties · IEEE TIM · Precision Engineering · Optics and Lasers in Engineering

**Date:** 2026-06-24

---

# PART I — UNIVERSALITY ANALYSIS

## I.1 Assumptions Extracted from the Framework

The following 14 assumptions are embedded, either explicitly as modelling choices or implicitly as preconditions for mathematical derivations:

| # | Assumption | Location | Status |
|---|-----------|----------|--------|
| A1 | **Gaussian height distribution** | §5.1 channel model: $h \sim \mathcal{GP}(0,K)$ | Explicit |
| A2 | **Stationarity** | §5.1: $K(\mathbf{x}-\mathbf{x}')$ depends only on separation | Explicit |
| A3 | **Self-affinity** | §2.3: PSD $\propto (f_0^2+f^2)^{-(H+1)}$ | Explicit (baseline) |
| A4 | **Isotropy of the surface** | §2.3: azimuthal averaging of PSD | Implicit |
| A5 | **Linearity of $\mathcal{M}$** | §2.1, Eq. 1: $\mathcal{M}[h] = \mathcal{F}^{-1}[H\cdot\mathcal{F}[h]]+\eta$ | Explicit |
| A6 | **Ergodicity** | §2.4: periodogram PSD estimation from a single realisation | Implicit |
| A7 | **Additive noise independence** | §5.1: $\eta$ independent of $h$ | Explicit |
| A8 | **Frequency-diagonal channel** | §5.1: Fourier basis diagonalises the channel | Explicit (from LSI) |
| A9 | **Gaussian noise** | §2.3: additive Gaussian camera noise | Explicit |
| A10 | **Incoherent imaging** | §2.1, Eq. 3: incoherent OTF for circular aperture | Explicit |
| A11 | **Paraboloid tip** | §2.1: $H_\mathrm{stylus} \approx \exp[-2\pi^2 r_\mathrm{tip}^2 f^2]$ | Explicit |
| A12 | **Small-roughness limit** | §2.1: $\sigma \ll r_\mathrm{tip}$ for linear stylus model | Explicit |
| A13 | **Single-surface measurement** | §2.4: $H$ estimated as PSD ratio from one realisation | Implicit |
| A14 | **Continuous phase** | §2.3: 1D phase unwrapping model (no branch cuts) | Implicit |

## I.2 Universality Matrix: 10 Framework Results × 9 Surface Classes

**Surface classes:**
1. Gaussian self-affine (SA)
2. Turned surfaces (T)
3. Ground surfaces (G)
4. Honed surfaces (H)
5. Laser-textured surfaces (LT)
6. Periodic gratings (PG)
7. Additively manufactured surfaces (AM)
8. Biological surfaces (B)
9. Multiscale engineered surfaces (ME)

### Matrix

| Framework Result | SA | T | G | H | LT | PG | AM | B | ME | Classification |
|-----------------|----|---|---|---|----|----|----|---|----|----------------|
| **R1:** $H(f)$ computable from first principles | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R2:** Spectral information loss $I(f) \propto f^{0.01}$ | ✓ | ~ | ~ | ~ | ✗ | ✗ | ~ | ? | ~ | **Conditionally valid** |
| **R3:** Anisotropy tensor $A_{ij}$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R4:** Equivalence regime $\Omega_\mathrm{eq}$ at 18.3% | ✓ | ~ | ~ | ~ | ✗ | ✗ | ~ | ? | ~ | **Conditionally valid** |
| **R5:** RMSE scaling law $\propto (f_{c,o}/f_{c,s})^{1.90}$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R6:** Mutual information $I(h;y)$ formula | ✓ | ~ | ~ | ~ | ~ | ✗ | ~ | ? | ~ | **Conditionally valid** |
| **R7:** Channel capacity $C$ | ✓ | ~ | ~ | ~ | ~ | ✗ | ~ | ? | ~ | **Conditionally valid** |
| **R8:** Reconstructability index $\rho$ | ✓ | ✗† | ~ | ~ | ✗† | ✗ | ~ | ? | ~ | **Conditionally valid** |
| **R9:** SNR-dependent resolution–bandwidth trade-off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **Universal** |
| **R10:** Information–energy–resolution trilemma | ✓ | ~ | ~ | ~ | ~ | ~ | ~ | ? | ~ | **Conditionally valid** |

**Legend:** ✓ = valid, ~ = partially valid (quantitative values shift, qualitative behaviour preserved), ✗ = likely invalid, † = saturates at boundary (ρ→1 for deterministic surfaces — physically meaningful but metric degenerate), ? = untested

## I.3 Key Universality Findings

### Survive across all surface classes:
- **R1** ($H(f)$ computability): Transfer functions depend only on instrument physics, not surface class. This is the framework's deepest invariant.
- **R3** (Anisotropy tensor): $A_{ij}$ is a property of the instrument, not the surface. It generalises trivially.
- **R5** (RMSE scaling law): The exponent 1.90 may shift but the power-law form $\mathrm{RMSE}_s/\mathrm{RMSE}_o \propto (f_{c,o}/f_{c,s})^\beta$ is universal because it follows from dimensional analysis.
- **R9** (Resolution–bandwidth trade-off): Follows from Fourier uncertainty + SNR inflation. Independent of surface statistics.

### Collapse or degrade when assumptions relaxed:
- **R2** ($I(f) \propto f^{0.01}$): This is a self-affine-surface artefact. For turned/ground surfaces, $I(f)$ will concentrate at the feed-mark period. For periodic gratings, it collapses to a delta function. **The near-constant-loss-per-decade result is NOT universal.**
- **R4, R6, R7, R8, R10**: All depend on the Gaussian channel model (A1). For non-Gaussian height distributions (turned, ground, AM), the mutual information formula is a *lower bound*, not the exact value. The reconstructability index $\rho$ saturates at 1.0 for deterministic surfaces (degenerate behaviour).
- **R8** specifically: $\rho$ fails catastrophically for periodic gratings ($\rho_\mathrm{optical}=0.02$) — this is physically correct but the metric cannot distinguish "instrument failure" from "all spectral power at one $k$-point."

### Critical gap: surfaces NOT tested
The framework claims seven surface classes but actually tested:
- Simulated self-affine Gaussian (the baseline)
- Six manufactured classes via block11 stress test (ground, turned, laser-textured, periodic grating, biological-like)

**Not tested:** Honed surfaces, additively manufactured (AM) surfaces, truly multiscale engineered surfaces. AM surfaces are particularly important — their as-built roughness combines large-scale layer striations with small-scale partially-melted powder particles, producing a non-self-affine, non-Gaussian, highly anisotropic PSD. The framework's Gaussian-channel capacity calculation would be a lower bound only.

## I.4 Proposed Generalised Formulations

**For non-Gaussian surfaces (A1 relaxed):**
Replace $I(h;y) = \frac{1}{2}\sum \log_2(1+\mathrm{SNR})$ with the general mutual information:
$$I(h;y) = h(y) - h(y|h) = h(y) - h(\eta)$$
where $h(\cdot)$ is differential entropy. For non-Gaussian $h$, compute via kNN entropy estimation (Kozachenko–Leonenko) on the simulated measurement ensemble. The Gaussian formula remains a *lower bound* (worst-case distribution for given variance).

**For non-stationary surfaces (A2 relaxed):**
Replace global PSD with local PSD via S-transform or wavelet PSD, then apply the operator framework locally. The transfer function $H(f)$ remains instrument-specific; only the surface spectrum $S_h(f)$ becomes position-dependent.

**For non-self-affine surfaces (A3 relaxed):**
The entire framework is independent of the self-affinity assumption — A3 only affects the baseline surface generation. All metrics ($H(f)$, $I(f)$, $\rho$, $C$) are defined for arbitrary $S_h(f)$.

**For highly anisotropic surfaces (A4 relaxed):**
The 1D azimuthally-averaged PSD is insufficient. The 2D anisotropy tensor $A_{ij}$ already handles this. The equivalence regime should be extended to a *directional* equivalence fraction $\Omega_\mathrm{eq}(\theta, \Delta)$.

---

# PART II — PHYSICS ROBUSTNESS ANALYSIS

## II.1 Optical Modality Robustness

| Optical Modality | $H(f)$ functional form | Cutoff | Axial physics | Framework applicability |
|-----------------|----------------------|--------|---------------|------------------------|
| **Coherent interferometry** (laser, $\lambda$=633 nm) | Coherent CTF: $H(f)=1$ for $f<f_c$, 0 otherwise | $f_c = \mathrm{NA}/\lambda$ | Sinusoidal fringe, $2\pi$ ambiguity | Operators 1–4, 9 valid. Coherent CTF is a special case of Eq. 3 (replace incoherent OTF). |
| **White-light interferometry** (WLI, LED) | Incoherent OTF (Eq. 3) | $f_c = 2\mathrm{NA}/\lambda$ | Coherence envelope, $l_c$ | **Baseline model.** Fully applicable. |
| **Confocal microscopy** | $H(f) = \mathrm{OTF} \star \mathrm{OTF}$ (squared OTF) | Same $f_c$ as WLI, sharper roll-off | Pinhole axial sectioning | Operators 1–9 directly applicable. Replace OTF with OTF². |
| **Focus variation (FV)** | Incoherent OTF (Eq. 3) | Same $f_c$ | Depth-from-defocus, Laplacian operator | Operators 1–9 directly applicable. Same lateral $H(f)$ as WLI. |
| **Digital holographic microscopy (DHM)** | Coherent CTF | $f_c = \mathrm{NA}/\lambda$ | Numerical refocusing, twin-image | Operators 1–4 valid. Coherent CTF replaces incoherent OTF. Twin-image artefact is a structured noise source. |
| **Structured illumination (SIM)** | $H_\mathrm{eff}(f) = H(f) + m H(f-f_m)$ | Extended cutoff to $f_c + f_m$ | Moiré fringe down-modulation | Operators 1–4 valid with modified $H_\mathrm{eff}$. Information-theoretic analysis (5–9) carries over with expanded bandwidth. |

### Deepest invariant
**The operator formalism $\mathcal{M} = \mathcal{F}^{-1}[H \cdot \mathcal{F}[h]] + \eta$ is invariant to choice of optical modality.** Every LSI optical instrument has a transfer function $H(f)$. The differences are in the *specific form* of $H(f)$, not in the framework structure. The information-theoretic quantities ($I(h;y)$, $C$, $\rho$, $\Xi$) are defined identically for all modalities — only the numerical inputs change.

## II.2 Tactile Modality Robustness

| Tactile variant | $H(f)$ modification | Framework robustness |
|----------------|-------------------|---------------------|
| **Baseline stylus** ($r_\mathrm{tip}$=2 µm, $\Delta x$=200 nm) | $H = \exp[-2\pi^2 r_t^2 f^2] \cdot \operatorname{sinc}(\pi f_x \Delta x)\operatorname{sinc}(\pi f_y \Delta y)$ | Baseline |
| **Different tip radii** (0.5–10 µm) | Gaussian width scales $\propto r_t$ | 180-pt sweep confirms: $\rho$ varies smoothly, $\alpha_s=0.014\pm0.011$ universal |
| **Different scan densities** (100–500 nm) | Sinc width scales $\propto \Delta x$ | Operator formalism absorbs trivially |
| **Different contact forces** (0.1–10 mN) | Tip penetration depth changes effective $r_\mathrm{eff}$ via Hertz contact | **NOT tested.** At high loads, plastic deformation invalidates linearity. At low loads, adhesion/snap-in invalidates the Hertz model. |

### Critical gap
**Contact-force regime not explored.** For very rough surfaces ($\sigma > r_\mathrm{tip}/20$), the stylus may lose contact (bouncing) or plough plastically. The equivalent linear $H(f)$ would need to be replaced with a *state-dependent* transfer operator. This is the single biggest physics gap in the tactile modelling.

## II.3 Robustness Hierarchy

**Tier 1 — Deep invariants (independent of instrument implementation):**
1. Operator formalism $\mathcal{M} = \mathcal{F}^{-1}[H \cdot \mathcal{F}[h]] + \eta$
2. Resolution–bandwidth trade-off $\Delta x \cdot \Delta f \geq (1/4\pi)(1+1/\overline{\mathrm{SNR}})$
3. Anisotropy tensor $A_{ij}$ as an instrument fingerprint
4. Dimensional scaling $\mathrm{RMSE}_s/\mathrm{RMSE}_o \propto (f_{c,o}/f_{c,s})^\beta$

**Tier 2 — Modality-invariant but surface-dependent:**
5. Mutual information formula (valid for any LSI instrument, but surface must be Gaussian)
6. MMSE bound (same qualifier)
7. Equivalence regime concept (threshold-dependent, surface-dependent)

**Tier 3 — Modality-specific:**
8. Specific $H(f)$ functional forms (Gaussian for stylus, arccos OTF for WLI)
9. Specific numerical values ($\rho=0.79$ for stylus, $C_\mathrm{total}=5.45\times10^{13}$ for optical)
10. $I(f) \propto f^{0.01}$ scaling (self-affine surface artefact)

---

# PART III — NOVELTY AUDIT

## III.1 Novelty Matrix

| Quantity | Mathematical novelty | Conceptual novelty | Reformulation? | Equivalence to existing concept | Verdict |
|----------|---------------------|-------------------|----------------|--------------------------------|---------|
| **Operator formalism** $\mathcal{M}[h]$ | ✗ (standard LSI theory) | ✓ (first application to cross-modality surface metrology) | Reformulation of LSI system theory | MTF in optics, system function in signal processing | **Conceptually novel in context** |
| **$I(f) = \log_{10}(\mathrm{PSD}_\mathrm{true}/\mathrm{PSD}_\mathrm{measured})$** | ✗ | ✗ | Reformulation of log-spectral ratio | Transfer function magnitude in dB; standard in signal processing | **Reformulation** |
| **$A_{ij}$ anisotropy tensor** | ✗ (second-moment tensor) | ✓ (first quantification of *instrument* anisotropy) | Reformulation of moment-of-inertia tensor | Image moments, inertia tensor | **Conceptually novel** |
| **$\Omega_\mathrm{eq}$ equivalence regime** | ✗ | ✓ (first $k$-space equivalence definition) | New application of level-set thresholding | Bandpass overlap in filter theory | **Conceptually novel** |
| **RMSE scaling law** | ✗ (power-law fit) | ✓ (first cross-modality scaling law) | Empirical regression | Buckingham π theorem | **Conceptually novel** |
| **$I(h;y)$ mutual information** | ✗ (standard Shannon formula) | ✓ (first application to profilometry) | Reformulation: parallel Gaussian channel capacity | Shannon–Hartley theorem, water-filling | **Reformulation in new domain** |
| **$\iota(\mathbf{f})$ spectral information density** | ✗ (integrand of mutual info) | ~ (new name for known quantity) | Reformulation | $\frac{1}{2}\log_2(1+\mathrm{SNR})$ is standard | **Reformulation with new name** |
| **$B_\mathrm{eq}$ information-equivalent bandwidth** | ✗ (equivalent rectangular bandwidth) | ~ | Reformulation | Equivalent noise bandwidth (ENB) in signal processing | **Reformulation** |
| **$\eta$ information efficiency** | ✗ (ratio of MI to capacity) | ~ | Reformulation | Coding efficiency, spectral efficiency | **Reformulation** |
| **$\varepsilon = I/\sigma^2$** | ✗ (normalised mutual information) | ~ | Reformulation | Information per unit variance; related to SNR efficiency | **Reformulation** |
| **$\rho = 1 - \mathrm{MMSE}/\sigma^2$** | ✗ | ~ | Reformulation | $R^2$ in regression, NMSE, reconstruction quality metric | **Reformulation** |
| **MMSE bound** | ✗ (standard Wiener filter MMSE) | ✓ (first applied to surface metrology as fundamental limit) | Reformulation of estimation-theoretic MMSE | Bayesian MMSE, Shannon lower bound | **Reformulation in new domain** |
| **SNR-dependent resolution–bandwidth** | ✓ (explicit SNR inflation factor) | ✓ (first in metrology context) | Extension of classical Fourier uncertainty | Heisenberg uncertainty, Gabor limit | **Mathematically novel** |
| **Information–energy–resolution trilemma** | ~ | ✓ | Dimensional analysis with SNR function | Resource trade-offs in information theory | **Conceptually novel** |
| **$\Xi = C/\kappa$** | ✗ (ratio of capacity to condition number) | ✓ | New composite metric | Figure of merit (FoM) in engineering | **Conceptually novel** |
| **Critical $H_c$** (reconstructability threshold) | ~ | ✓ | Phase-transition concept | Percolation threshold, phase transitions | **Conceptually novel** |

## III.2 Novelty Assessment Summary

### Strongest original contributions (ranked):
1. **SNR-dependent resolution–bandwidth trade-off** (Eq. 15): Explicit inflation of the classical Fourier uncertainty by $(1+1/\overline{\mathrm{SNR}})$ appears genuinely new. Neither the metrology nor the signal-processing literature formulates the uncertainty principle with an SNR-dependent inflation factor.
2. **Cross-modality operator formalism applied to surface metrology**: While LSI system theory is standard, its systematic application to *comparing fundamentally different modalities* (tactile vs. optical vs. scattering) is new and practically significant.
3. **Anisotropy tensor $A_{ij}$ as instrument fingerprint**: First quantitative characterisation of measurement-system-induced anisotropy. ISO 25178 characterises *surface* anisotropy but not *instrument* anisotropy.
4. **$\Xi = C/\kappa$**: A single figure of merit combining information throughput with frequency-response uniformity. Novel in metrology.
5. **RMSE scaling law $\propto (f_{c,o}/f_{c,s})^{1.90}$**: First empirically validated scaling law connecting instrument parameters to cross-modality accuracy.

### Weakest contributions:
- $\iota(\mathbf{f})$ (SID): This is simply the integrand of the mutual information formula — standard in information theory. The new name does not add conceptual content.
- $B_\mathrm{eq}$: Equivalent noise bandwidth is a standard signal-processing concept. The application is new but the quantity is not.
- $\varepsilon = I/\sigma^2$: Normalising mutual information by variance is natural — not mathematically deep.

### Highest-risk contributions:
- **$\rho$ (reconstructability index)**: Saturates at 1.0 for deterministic surfaces and 0.02 for gratings, making it a poor scalar summary for non-random surfaces. Risk of rejection by reviewers who work with engineered (non-random) surfaces.
- **$H_c$ (critical Hurst exponent)**: The "reconstructability transition" is physically appealing but the exponent 0.25 (stylus) vs. 0.10 (optical) is a single-parameter-fit result. The concept is at risk of being dismissed as curve-fitting unless supported by an analytic derivation showing *why* a threshold exists.
- **Channel capacity $C$**: Absolute values ($10^{13}$ bits) are physically uninterpretable. Reviewers from MST and Precision Engineering will ask: "What does $5.45\times10^{13}$ bits actually mean for a metrologist?" The ratio $C_o/C_s = 1.71$ is the meaningful quantity.

## III.3 Novelty Enhancement Recommendations

1. **Elevate the SNR-dependent uncertainty principle** to the title/abstract — it is the most original mathematical contribution.
2. **Demote $\iota(\mathbf{f})$** from a "new quantity" to a "convenient visualisation of the mutual information integrand."
3. **Replace $B_\mathrm{eq}$** with a clearer connection to existing metrological bandwidth concepts — or drop it.
4. **Provide an analytic derivation of $H_c$** rather than empirical curve-fitting — or frame it as an empirical observation rather than a phase transition.
5. **Report capacity ratios, not absolute values.** The absolute capacity in bits depends on grid size and is not physically meaningful.

---

# PART IV — FALSIFIABILITY ANALYSIS

## IV.1 Falsifiability of Each Quantity

### 1. Transfer function $H(f)$
- **Experimental setup:** Measure one calibrated artefact (Siemens star or chirp standard) with both stylus and WLI. Compute $H(f) = \mathrm{PSD}_\mathrm{measured}/\mathrm{PSD}_\mathrm{true}$.
- **Instrumentation:** Commercial stylus profilometer + WLI + calibrated artefact (Siemens star, 50 µm diameter, 2 µm minimum period).
- **Observable:** $H(f)$ from 10–1000 mm⁻¹.
- **Prediction:** Computed $H(f)$ matches measured $H(f)$ within 3 dB across passband.
- **Failure criterion:** Measured $H(f)$ differs from computed $H(f)$ by >6 dB in >20% of the passband.
- **Testability:** **Directly testable.** Standard lab equipment.

### 2. Spectral information loss $I(f)$
- **Experimental setup:** Same as above. $I(f) = \log_{10}(\mathrm{PSD}_\mathrm{true}/\mathrm{PSD}_\mathrm{measured})$.
- **Prediction:** $I(f) \propto f^{0.01}$ for self-affine surfaces; deviates for other classes.
- **Failure criterion:** $I(f)$ scaling exponent outside $0.01 \pm 0.05$ for self-affine surfaces.
- **Testability:** **Directly testable.**

### 3. Anisotropy tensor $A_{ij}$
- **Experimental setup:** Measure an isotropic reference surface (e.g., lapped glass) with both modalities. $n \geq 30$ repeats.
- **Prediction:** $\alpha_s = 0.014 \pm 0.011$, $\alpha_o = 0.0031 \pm 0.0018$.
- **Failure criterion:** $\alpha_s$ outside [0.003, 0.025] or $\alpha_o > 0.01$.
- **Testability:** **Directly testable.**

### 4. Equivalence regime $\Omega_\mathrm{eq}$
- **Experimental setup:** Compare stylus and WLI PSDs of the same surface. Compute $f_\mathrm{cross}$ where $H_s \approx H_o$.
- **Prediction:** $f_\mathrm{cross} = 311 \pm 173$ mm⁻¹; equivalence fraction = 18.3% ± 0.2% at 3 dB.
- **Failure criterion:** $f_\mathrm{cross}$ outside [100, 500] mm⁻¹ for baseline parameters.
- **Testability:** **Directly testable.**

### 5. RMSE scaling law
- **Experimental setup:** Vary $r_\mathrm{tip}$ (0.5, 2, 5, 10 µm) and NA (0.2, 0.3, 0.4, 0.55). Measure same surface. Fit $\mathrm{RMSE}_s/\mathrm{RMSE}_o \propto (f_{c,o}/f_{c,s})^\beta$.
- **Prediction:** $\beta = 1.90 \pm 0.05$.
- **Failure criterion:** $\beta$ outside [1.5, 2.5].
- **Testability:** **Directly testable.** Requires access to multiple styli and objectives.

### 6. Mutual information $I(h;y)$
- **Experimental setup:** NOT directly measurable — mutual information requires knowledge of the joint distribution $p(h,y)$, which is inaccessible from a single measurement pair. Can be bounded: estimate $H(y|h)$ from repeat measurements on the same surface.
- **Prediction:** $I_o/I_s = 1.71$.
- **Testability:** **Indirectly testable.** Requires $n \geq 50$ repeat measurements to estimate noise entropy. Experimentally demanding.

### 7. Channel capacity $C$
- **Testability:** **Currently non-testable.** Channel capacity is a supremum over all possible input distributions (surfaces). Cannot be verified with a finite set of surfaces. Can only be bounded from below by $I(h;y)$ for specific surfaces.

### 8. Reconstructability index $\rho$
- **Experimental setup:** Measure surface $n \geq 50$ times. Compute $\mathrm{MMSE}$ as mean squared deviation from the ensemble mean. Compare to Eq. 14.
- **Prediction:** $\rho_\mathrm{stylus} \approx 0.79$, $\rho_\mathrm{optical} \approx 0.64$ for $H=0.7$, $\sigma=50$ nm.
- **Failure criterion:** Measured $\rho$ differs from predicted by >0.15.
- **Testability:** **Indirectly testable.** Requires repeat measurements — feasible.

### 9. SNR-dependent resolution–bandwidth trade-off
- **Experimental setup:** Measure the same surface at different SNRs (vary illumination for optical; vary averaging for stylus). Compute $\Delta x_\mathrm{eff}$ from edge-spread function; $\Delta f_\mathrm{eff}$ from $H(f)$ width. Plot product vs. SNR.
- **Prediction:** Product $\geq (1/4\pi)(1+1/\overline{\mathrm{SNR}})$.
- **Failure criterion:** Any measurement falls below the bound.
- **Testability:** **Directly testable.** Elegant experiment.

### 10. $\Xi = C/\kappa$
- **Testability:** Same issues as $C$ — **indirectly testable** via lower bounds.

## IV.2 Validation Roadmap

**Phase 1 — Directly testable (3–6 months, standard lab):**
1. Transfer function validation on Siemens star (falsifies R1)
2. Anisotropy tensor measurement on isotropic reference (falsifies R3)
3. SNR-dependent uncertainty bound (falsifies R9)
4. RMSE scaling law with different tips/objectives (falsifies R5)

**Phase 2 — Indirectly testable (6–12 months, dedicated campaign):**
5. $\rho$ via repeat measurements on calibrated surfaces
6. $I(h;y)$ lower bound via noise entropy estimation
7. Equivalence regime on multiple surface classes

**Phase 3 — Long-term/conceptual:**
8. Channel capacity (builds surface library for lower-bound tightening)
9. $\Xi$ (same)

---

# PART V — RESEARCH GAP REASSESSMENT

## V.1 Which original gaps are fully closed?

1. ✅ **First-principles $H(f)$ computation for stylus and WLI** — closed. Transfer functions computed, validated against known physics, and shown invariant to model variants.
2. ✅ **Cross-modality $k$-space comparison framework** — closed. The operator formalism, transfer function ratio $R(f_x,f_y)$, and equivalence regime $\Omega_\mathrm{eq}$ provide a complete framework.
3. ✅ **Systematic parameter sweep** — closed. 180-point sweep validates the main scaling laws.
4. ✅ **Scatterometry extension** — closed. Three-way comparison complete (Supplementary §S2).

## V.2 Which gaps are only partially closed?

5. ⚠️ **Experimental validation** — entirely absent. This is the framework's single biggest weakness and the primary reason for desk rejection risk at top journals. A purely computational study comparing instruments without any experimental data is vulnerable to the criticism: "How do we know the simulations represent real instruments?"
6. ⚠️ **Nonlinear stylus regime** — acknowledged as a limitation but not solved. The linearity boundary ($\sigma/r_\mathrm{tip}=0.025$) covers only smooth surfaces. Rough engineering surfaces ($\sigma > 100$ nm) lie outside.
7. ⚠️ **Universality proof across surface classes** — six classes tested but only computationally. Honed, AM, and multiscale surfaces not addressed. Non-Gaussian information-theoretic analysis is lower-bound only.
8. ⚠️ **Optical 2D phase unwrapping** — 1D row-by-row used. The stated 2D improvement is not demonstrated.
9. ⚠️ **Vector diffraction at high NA** — acknowledged in Supplementary §S1.2 but not integrated into the main optical $H(f)$ model. For NA > 0.7, the scalar OTF is incorrect.

## V.3 New gaps that emerge from the framework

10. 🔴 **Contact-force-dependent $H(f)$** — the stylus transfer function depends on normal load through Hertzian contact area. At different loads, $r_\mathrm{eff}$ changes. This is unexplored.
11. 🔴 **Non-Gaussian information-theoretic capacity** — the Gaussian channel model gives a lower bound, but the true capacity for non-Gaussian surfaces (turned, ground, AM) is unknown. Computing it requires solving a variational problem over input distributions.
12. 🟡 **Temporal effects** — stylus scan speed affects dynamic forces; WLI acquisition time affects drift. Neither is modelled.
13. 🟡 **Environmental sensitivity** — temperature drift, vibration, and humidity affect real instruments differently. The current framework treats these as lumped additive noise.

## V.4 Gap Ranking by Scientific Importance × Feasibility × Publication Potential

| Rank | Gap | Importance | Feasibility | Publication potential |
|------|-----|-----------|-------------|----------------------|
| 1 | Experimental validation of $H(f)$ | ★★★★★ | ★★★★ | ★★★★★ |
| 2 | Non-Gaussian channel capacity | ★★★★ | ★★ | ★★★★★ |
| 3 | Nonlinear stylus $H(f)$ | ★★★★ | ★★★ | ★★★★ |
| 4 | Contact-force dependence | ★★★ | ★★★★ | ★★★★ |
| 5 | 2D phase unwrapping | ★★★ | ★★★ | ★★★ |
| 6 | Vector diffraction OTF | ★★★ | ★★★★ | ★★★ |
| 7 | AM surface class extension | ★★★ | ★★ | ★★★★ |
| 8 | Honed surface class | ★★ | ★★★ | ★★★ |
| 9 | Temporal/dynamic effects | ★★ | ★ | ★★ |
| 10 | Environmental sensitivity | ★★ | ★★ | ★★ |

---

# PART VI — Q1 REVIEW SIMULATION

## VI.1 Measurement Science and Technology (MST)

**Scope:** Measurement science, instrumentation, sensors, metrology. Strong preference for experimental validation.

**Major strengths:**
- Transfer function framework directly addresses a long-standing metrology problem
- Clear practical guidance (decision matrix, equivalence protocol)
- SNR-dependent uncertainty principle is theoretically elegant
- Parameter sweep validates scaling laws

**Major weaknesses:**
- **Zero experimental data.** This is a severe problem for MST. The journal expects at least some experimental validation, even if limited to one surface and one instrument pair.
- The absolute capacity values ($10^{13}$ bits) are physically uninterpretable — MST reviewers will push back.
- No measurement uncertainty analysis per GUM — expected for any metrology paper.

**Most likely reviewer criticism:**
> "This is an interesting theoretical framework, but without experimental validation it remains a computational exercise. The authors should demonstrate at minimum one experimental transfer function measurement on a calibrated artefact and compare it to their computed $H(f)$."

**Desk rejection probability:** 40%
**Major revision probability:** 50%
**Acceptance probability after revision:** 60% (if experimental validation added)

---

## VI.2 Surface Topography: Metrology and Properties (STMP)

**Scope:** Surface measurement, characterisation, properties. Interdisciplinary — metrology, tribology, materials. More tolerant of computational work than MST.

**Major strengths:**
- PSD-based analysis aligns with STMP's methodological focus
- Seven surface classes tested (even if computationally)
- Decision matrix for instrument selection is practically useful
- Anisotropy tensor is novel and surface-topography-relevant

**Major weaknesses:**
- No experimental validation (same as MST, but STMP slightly more forgiving)
- Self-affine baseline limits generality — STMP readers work with diverse surface types
- Scatterometry extension feels appended rather than integrated
- No connection to functional surface properties (tribology, wetting, etc.)

**Most likely reviewer criticism:**
> "The framework is applied to simulated self-affine surfaces. How does it perform on real manufactured surfaces that are non-self-affine, non-Gaussian, and often non-stationary? The authors should test on at least one real manufactured surface class."

**Desk rejection probability:** 25%
**Major revision probability:** 55%
**Acceptance probability after revision:** 70%

---

## VI.3 IEEE Transactions on Instrumentation and Measurement (IEEE TIM)

**Scope:** Instrumentation, measurement theory, signal processing, uncertainty. High theoretical tolerance.

**Major strengths:**
- Information-theoretic formulation is novel in metrology
- SNR-dependent uncertainty principle is a genuine theoretical contribution
- Channel capacity analysis for profilometry is unprecedented
- MMSE bound provides a benchmark for algorithm development

**Major weaknesses:**
- The information-theoretic quantities ($\iota$, $B_\mathrm{eq}$, $\eta$, $\varepsilon$) are largely reformulations of standard concepts — IEEE TIM reviewers will recognise this
- Missing comparison with estimation-theoretic bounds from signal processing literature
- No treatment of sparse reconstruction or compressive sensing, which are hot topics at IEEE TIM
- The Gaussian channel assumption is strong — non-Gaussian capacity bounds are needed

**Most likely reviewer criticism:**
> "Several of the proposed metrics ($\iota$, $B_\mathrm{eq}$, $\eta$) are standard quantities from information and estimation theory, renamed for the metrology context. The authors should clearly distinguish which contributions are mathematically new and which are novel applications of existing theory. Additionally, the Gaussian channel assumption limits the generality of the capacity results — a non-Gaussian extension or a justification of why Gaussian is worst-case would strengthen the manuscript."

**Desk rejection probability:** 15%
**Major revision probability:** 60%
**Acceptance probability after revision:** 75% (strong theoretical alignment)

---

## VI.4 Precision Engineering

**Scope:** Precision manufacturing, metrology, machine tools, tolerancing. Strong engineering focus.

**Major strengths:**
- RMSE scaling law is directly useful for instrument selection
- Gap-closure roadmap provides actionable engineering guidance
- Decision matrix (Table 4) is the kind of practical tool PE readers value
- 432-point parameter sweep is thorough

**Major weaknesses:**
- **Zero experimental data** — Precision Engineering is an experimental/applied journal
- Heavy information-theoretic content may be seen as overly theoretical
- No connection to manufacturing tolerances or ISO GPS standards
- No cost-benefit analysis of the gap-closure roadmap

**Most likely reviewer criticism:**
> "The practical recommendations (use stylus for $f<20$ mm⁻¹, optical for $f>20$ mm⁻¹) are useful but need experimental confirmation. Additionally, how do these recommendations interact with ISO GPS tolerancing standards? The connection to industrial practice is not established."

**Desk rejection probability:** 50%
**Major revision probability:** 40%
**Acceptance probability after revision:** 45% (mismatch between theoretical framework and applied journal expectations)

---

## VI.5 Optics and Lasers in Engineering

**Scope:** Optical metrology, laser applications, optical instrumentation. Strong optical physics focus.

**Major strengths:**
- Optical $H(f)$ modelling from OTF is physically sound
- Vector diffraction corrections (Supplementary) add rigour
- Scatterometry extension is optically sophisticated
- 432-point NA/wavelength sweep is convincing

**Major weaknesses:**
- The stylus half of the framework is irrelevant to an optics audience
- No experimental optical measurement
- The information-theoretic section (40% of the manuscript) is a distraction for optics readers
- No comparison with existing optical metrology transfer standards

**Most likely reviewer criticism:**
> "The optical modelling (scalar OTF + 1D phase unwrapping) is a simplified representation. The authors should compare their simulated $H_\mathrm{optical}(f)$ against experimentally measured OTF for at least one commercial WLI instrument, or use a more sophisticated optical model incorporating the instrument's actual illumination and imaging chain."

**Desk rejection probability:** 35%
**Major revision probability:** 45%
**Acceptance probability after revision:** 50%

---

## VI.6 Journal Recommendation Summary

| Journal | Desk reject | Major revision | Accept after revision | Recommendation |
|---------|------------|----------------|----------------------|----------------|
| **IEEE TIM** | 15% | 60% | 75% | ★★★★★ Best fit |
| **STMP** | 25% | 55% | 70% | ★★★★ Good fit |
| **MST** | 40% | 50% | 60% | ★★★ Acceptable |
| **Optics and Lasers in Eng.** | 35% | 45% | 50% | ★★ Mismatch |
| **Precision Engineering** | 50% | 40% | 45% | ★★ Mismatch |

**Primary recommendation: IEEE TIM** — the information-theoretic content aligns best, the theoretical tolerance is highest, and the SNR-dependent uncertainty principle would be recognised as novel.
**Secondary: STMP** — good fit for the surface metrology community if experimental data added.

---

# PART VII — FINAL ACTION PLAN

## VII.1 Top 10 Improvements Ranked by Impact

| Rank | Improvement | Impact | Effort | Risk reduction |
|------|------------|--------|--------|---------------|
| 1 | **Add experimental validation of $H(f)$ on one calibrated artefact** | ★★★★★ | High (3 months) | Eliminates #1 desk-rejection cause |
| 2 | **Reframe capacity values as ratios** — drop absolute $C$ numbers, report only $C_o/C_s$ | ★★★★ | Low (1 day) | Eliminates uninterpretable-number criticism |
| 3 | **Demote $\iota(\mathbf{f})$, $B_\mathrm{eq}$, $\eta$, $\varepsilon$** from "new quantities" to "convenient diagnostic tools derived from standard theory" | ★★★★ | Low (1 day) | Eliminates "renaming existing concepts" criticism |
| 4 | **Provide analytic (not empirical) derivation of $H_c$** or reframe as "empirical reconstructability threshold observed in simulations" | ★★★★ | Medium (1 week) | Eliminates "curve-fitting masquerading as phase transition" criticism |
| 5 | **Demonstrate 2D phase unwrapping improvement** — rerun one optical simulation with 2D quality-guided unwrapping, show RMSE reduction | ★★★ | Medium (1 week) | Closes stated limitation, strengthens optical model |
| 6 | **Vector diffraction OTF at high NA** — compute Richards–Wolf vector OTF at NA=0.8 and compare to scalar OTF results | ★★★ | Medium (1 week) | Closes stated limitation, strengthens optical rigour |
| 7 | **Test on one non-self-affine, non-Gaussian manufactured surface** — use a real measured PSD as input, simulate both modalities | ★★★★ | Low–Medium (2 weeks) | Addresses universality concern without full experimental campaign |
| 8 | **Add GUM-compliant uncertainty budget** for the transfer function estimation — propagate tip radius, NA, and noise uncertainties to $H(f)$ | ★★★ | Medium (1 week) | Required for MST/IEEE TIM metrology papers |
| 9 | **Contact-force sweep** — simulate stylus at three loads (0.1, 1, 10 mN) with Hertz-predicted $r_\mathrm{eff}$ | ★★★ | Low (3 days) | Closes contact-force gap |
| 10 | **Reposition $\rho$** — acknowledge it is degenerate for deterministic surfaces; propose a "spectral concentration index" as an alternative for non-random surfaces | ★★ | Low (1 day) | Pre-empts $\rho$ criticism from engineered-surface community |

## VII.2 Top 5 Missing Experiments/Simulations

1. **$H(f)$ experimental validation on Siemens star** — one artefact, two instruments, one afternoon of measurement. Highest-impact addition possible.
2. **2D vs 1D phase unwrapping comparison** — already implemented in most WLI software; simulate or benchmark. Quantify RMSE reduction.
3. **Vector diffraction OTF at NA=0.7–0.9** — close the scalar/vector gap for the gap-closure roadmap (which uses NA up to 0.9 where scalar theory is inaccurate).
4. **Real PSD input test** — download a published measured PSD of a ground or turned surface, feed it through the simulation pipeline, verify that predicted $H(f)$ behaviour holds.
5. **Contact-force sweep** — three loads, same surface, quantify how $r_\mathrm{eff}$ affects $\rho$ and $f_\mathrm{cross}$.

## VII.3 Top 5 Unresolved Theoretical Weaknesses

1. **Nonlinear stylus regime ($\sigma/r_\mathrm{tip} > 0.05$):** No framework exists for the nonlinear operator. This is a hard mathematical problem (morphological dilation is not diagonalisable in Fourier basis).
2. **Non-Gaussian channel capacity:** The true capacity for non-Gaussian surfaces is unknown. Computing it requires solving a difficult variational problem. The current Gaussian capacity is a lower bound — but how tight?
3. **Stationarity:** The framework assumes global stationarity. Real surfaces are rarely stationary. Local spectral methods (wavelets) need integration into the operator formalism.
4. **Causality of $H(f)$ estimation:** $H(f) = \mathrm{PSD}_\mathrm{measured}/\mathrm{PSD}_\mathrm{true}$ requires knowledge of the true PSD, which is unavailable in practice. The transfer function must be estimated from the measurement itself — a blind deconvolution problem. Yashchuk's calibration gratings solve this experimentally but not computationally.
5. **Observability Gramian not defined:** $\kappa(O)$ is mentioned but the observability Gramian $O$ is never formally defined in the manuscript. This is a critical omission for the $\Xi$ metric.

## VII.4 Top 5 Strongest Contributions (Defend These)

1. **SNR-dependent resolution–bandwidth trade-off** — genuinely new, mathematically crisp, experimentally testable.
2. **Cross-modality operator formalism** — the unifying insight that stylus and optical profilometry are both LSI filters with different $H(f)$.
3. **RMSE scaling law** — empirically validated, practically useful, dimensional-analysis-grounded.
4. **Anisotropy tensor $A_{ij}$** — first quantification of instrument anisotropy, not surface anisotropy.
5. **Gap-closure roadmap** — prescriptive (not just diagnostic), parameter-sweep-validated, actionable.

## VII.5 Exact Modifications to Maximise Q1 Acceptance Probability

### Immediate (before submission, 1–2 weeks):
1. **Rewrite §5 abstract/preamble** to clearly label which quantities are mathematically novel (SNR uncertainty principle), which are novel applications of standard theory (mutual information, MMSE), and which are convenient diagnostic tools (SID, $B_\mathrm{eq}$, $\eta$, $\varepsilon$).
2. **Drop absolute capacity values.** Replace $C_\mathrm{stylus}=3.19\times 10^{13}$ with $C_o/C_s=1.71$ throughout. Add a footnote explaining why absolute values are not meaningful.
3. **Define $\kappa(O)$ formally.** Add the observability Gramian definition: $O = \iint \mathbf{h}(\mathbf{f})\mathbf{h}^H(\mathbf{f}) d^2f$ where $\mathbf{h}(\mathbf{f})$ is the vector of transfer function values at frequency $\mathbf{f}$, and $\kappa(O) = \lambda_\mathrm{max}/\lambda_\mathrm{min}$.
4. **Add GUM uncertainty propagation** for $H(f)$ — a simple first-order propagation of tip radius, NA, and noise uncertainties through Eq. 2–3. One table.
5. **Reposition $H_c$** as an empirical observation ("we observe a transition in $\rho$ at $H \approx 0.25$") rather than a derived phase transition.

### Short-term (before resubmission, 1–3 months):
6. **Perform one experimental $H(f)$ validation.** Even a single surface (Siemens star or chirp standard), single instrument pair (one stylus + one WLI), and single comparison figure would transform the manuscript from "purely computational" to "computationally predicted and experimentally validated." This is the single change that most increases acceptance probability.
7. **Run one real-PSD-input test.** Take a published PSD from the literature (e.g., a ground steel surface from one of the cited references), feed it through the simulation pipeline, and verify predictions.
8. **Compare 1D vs 2D phase unwrapping** computationally. Quantify the RMSE reduction.

### Strategic (for revision):
9. **Contact-force sweep** (3 loads, simulation only).
10. **Vector OTF at NA=0.8** for the gap-closure roadmap.
11. **Add one non-Gaussian surface class** (AM or honed) to the stress-test.

---

# SUMMARY JUDGMENT

**The framework is theoretically sound and makes several genuinely novel contributions** (SNR-dependent uncertainty principle, cross-modality operator formalism, RMSE scaling law, anisotropy tensor). **It is not yet submission-ready for a Q1 journal** due to three critical deficiencies:

1. **Zero experimental validation** — the single biggest risk factor. All five target journals expect at least some experimental data for a metrology/instrumentation paper.
2. **Inflation of novelty claims** — several quantities ($\iota$, $B_\mathrm{eq}$, $\eta$, $\varepsilon$) are standard information/signal-processing concepts renamed, and claiming them as new invites reviewer pushback.
3. **Missing formal definitions** — the observability Gramian $\kappa(O)$ is used but not defined; $H_c$ lacks analytic derivation.

**With the top 5 immediate modifications (1–2 weeks), the desk-rejection risk drops from ~40% to ~15%. With one experimental validation added (1–3 months), the acceptance probability at IEEE TIM rises to ~80%.**

**Verdict: Major revision required → Resubmit after experimental validation.**
