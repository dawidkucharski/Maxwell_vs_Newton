# Senior Associate Editor & Reviewer Panel — Hostile Audit

Date: 2026-10-16. Manuscript: "Optical Profilometry Versus the Stylus: A Spectral Theory for Closing the Accuracy Gap" (57 pp + 18 pp SI + cover letter). All probability estimates below are editorial judgement of this panel, not measured statistics. The scientific framework is assumed complete; this audit identifies what reviewers will attack and what fixes give the highest acceptance gain.

---

## PHASE 1 — TECHNICAL AUDIT (hostile Q1 reviewer)

### Verified during this audit (not assumed)

- `block5_discovery_engine.py` line 151: `H_sensor = PSD_measured / PSD_true` — the pipeline's H is a **power ratio**.
- `manuscript.tex` Eq. operator defines H as the **amplitude** transfer; Eq. mutual information uses $|H(\mathbf{f})|^2 S_h/S_\eta$ (amplitude convention); Eq. transfer-function estimate defines $H = \mathrm{PSD}_\mathrm{measured}/\mathrm{PSD}_\mathrm{true}$ (power convention).
- `manuscript.tex` Eq. gramian defines $O=\int \mathbf{h}\mathbf{h}^H d^2f$ with $\mathbf{h}=[H,\partial H/\partial f_x,\partial H/\partial f_y]^T$; `block8_info_theory.py` line 426+ computes $\kappa = \max|H|^2/\min|H|^2$ over the passband. The manuscript equation does not describe the computed quantity.
- Eq. SNR-dependent resolution–bandwidth bound appears in the main text with no derivation; SI \S S4.3 only *uses* it ("the main text establishes…"). No derivation exists in either document.
- `pipeline/outputs/iter01/ensemble/ensemble_stats.json` (n=30 α, f_cross, equivalence fraction, RMSE) has **no generating script** in the repository (grep finds only readers). The stress-test block (block11) does vary seeds (42, 142, 242, …).

### Weakness inventory (ranked)

| # | Weakness | Severity | P(reviewer finds it) |
|---|----------|----------|----------------------|
| T1 | **Amplitude vs power convention for H.** Eqs. operator / transfer-estimate / mutual-information are mutually inconsistent; the MI numbers were computed with a different convention than the estimator equation implies. | **Critical** | 0.8 |
| T2 | **The headline bound $\Delta x_\mathrm{eff}\Delta f_\mathrm{eff}\ge(1/4\pi)(1+1/\overline{\mathrm{SNR}})$ has no derivation and no operational definitions of $\Delta x_\mathrm{eff},\Delta f_\mathrm{eff}$.** Cover letter calls it "a new measurement limit". As written it is unfalsifiable and unverifiable. | **Critical** | 0.9 |
| T3 | **Observability Gramian equation ≠ computed κ.** Mixed units in $\mathbf{h}=[H,\partial H/\partial f]$ make κ scale-dependent; the reported $\Xi_o/\Xi_s=1.31$ rests on the code's definition, not the printed equation. | High | 0.5 |
| T4 | **n=30 ensemble statistics not reproducible from committed code** (stored JSON only). | High | 0.6 |
| T5 | **Purely computational; zero experimental validation.** Stated honestly, but every STMP referee will still raise it; it is the dominant acceptance risk. | High | 1.0 |
| T6 | **Length 57+18 pp** — desk-rejection risk at STMP despite cover-letter justification. | High | 0.4 (desk) |
| T7 | **Monochromatic λ=550 nm OTF presented under "broadband WLI"** without an explicit monochromatic mean-λ approximation statement; public benchmark shows real instruments roll off at ≈0.65 µm mean λ. | Medium | 0.7 |
| T8 | **MI ratio estimator-dependence (1.61 vs 1.71)** disclosed but two estimators coexist; referees prefer one consistent estimator reported with uncertainty. | Medium | 0.6 |
| T9 | **ρ called "reconstructability index"** for a channel the manuscript itself calls nonlinear; linearised caveat exists but the naming invites challenge. | Medium | 0.5 |
| T10 | **γ null result has n=3** — inconclusive by design; already honestly framed. | Medium | 0.4 |
| T11 | **Single-realisation numbers in Results** (L_s, L_o, per-band table, MIR proxy) are n=1 visuals; ensemble means exist for some but are not quoted in the same place. | Medium | 0.4 |
| T12 | **WLI coherence envelope excluded from baseline optical model**; quantified via public benchmark (≈15%) but a WLI specialist will ask for an in-model variant. | Medium | 0.6 |
| T13 | fig8/fig10 generated but never referenced; the public-benchmark figure is not referenced in the text. | Low | 0.2 |
| T14 | First-person "I introduce…" style vs IOP convention (third person). | Low | 0.3 |
| T15 | Decision table mixes the correlation MI proxy (0.90) with Shannon MI elsewhere; explained once, but easily misread. | Low | 0.3 |

---

## PHASE 2 — NOVELTY AUDIT

| Claim (exact wording) | Verdict | Conservative rewrite |
|---|---|---|
| Abstract: "yet no unified $k$-space framework exists to quantify differences between stylus and optical profilometry" | Unsupported absolute | "no widely adopted $k$-space framework currently quantifies the differences between stylus and optical profilometry beyond scalar metrics" |
| "I introduce a measurement operator formalism" | Fine (re-introducing standard operator language in this context is defensible; keep, it is not a novelty claim itself) | keep |
| "I obtain a metrological formulation of the SNR-dependent resolution–bandwidth bound" | **Unsafe until T2 is fixed** | "a metrological formulation of a noise-generalised resolution–bandwidth bound, anchored to [Greco & Boyer 2019]" + derivation |
| "the first simulation-derived scaling law connecting instrument cutoff frequencies to cross-modality accuracy ratios" | Qualified ("to the best of my knowledge"); keep | keep with qualification |
| "the first quantitative measure of measurement-system anisotropy" | Qualified; keep, cite Takacs 2D↔1D as adjacent (done) | keep |
| "no prior work has systematically applied information theory to the comparison of fundamentally different surface measurement modalities" | Search-level claim, qualified; keep | keep, but state the search basis in a footnote or SI |
| "I introduce the reconstructability index ρ" + "mathematically equivalent to R²" | Internal tension acknowledged in text; keep | keep both sentences; consider renaming to "reconstructability $R^2$" |
| Cover letter: "A new measurement limit" | **Unsafe until T2 fixed** | "a noise-generalised form of the Fourier uncertainty bound, applied to surface metrology" |
| "Universal metrics" in SI stress test | CV<0.3 across classes supports it; keep with the existing caveats | keep |

**Action:** soften the abstract sentence, reword cover-letter item 1, and add the search-basis footnote. No other novelty flags remain after the Phase 3 audit of the earlier mission.

---

## PHASE 3 — ASSUMPTION AUDIT

| Assumption | Stated? | Justified? | Limits conclusions? | Recommended modification |
|---|---|---|---|---|
| Linear shift-invariant measurement operator | Yes, with nonlinear-dilation caveat | Partially (stylus is nonlinear) | Yes — main caveat | Add one sentence at Eq. operator: "H is defined in the amplitude convention; its power counterpart is \|H\|² (see Eq. transfer estimate)." (kills T1) |
| H estimated as PSD ratio (power) | Yes (Eq. transfer estimate) | **No — conflicts with amplitude convention** | Yes | Fix convention (T1) |
| Gaussian surface heights (MI/MMSE) | Yes | Yes (SI non-Gaussian validation) | Bounds only | keep |
| Self-affine, stationary, ergodic surfaces | Yes | Yes | Yes — local-spectral caveat present | keep |
| Isotropic *surface* statistics | Yes | Yes | Directional claims are instrument-attributed | keep |
| Small-slope dilation (σ/r=0.025) | Yes, with quantified linearity sweep | Yes | Yes | keep (now data-consistent) |
| Broadband WLI modelled as monochromatic λ=550 nm | **Not explicitly** | Partially (public benchmark quantifies ≈15% envelope shift) | Yes | Add explicit sentence in Optical Simulation (fixes T7) |
| Scalar optics, incoherent OTF, no aberrations/defocus in baseline | Yes (variants in Discussion) | Yes | Yes | keep |
| Additive Gaussian camera noise, high illumination | Yes, validated vs Poisson (3.6%) | Yes | Yes | keep |
| Ideal tip (no wear/skid/dynamics) | Yes (SI Hertzian budget) | Yes | Yes | keep |
| 1D row unwrapping, fixed 1% error probability | Yes, sensitivity discussed | Yes | Yes | keep |
| Single random seed for visuals; seeds stated | Yes | Yes | No | keep |

---

## PHASE 4 — ROBUSTNESS AUDIT

Covered: six surface classes (5 realisations each, varied seeds), optical OTF variants, grid convergence N=128–1024, Gaussian vs Poisson noise, non-stationarity example, 180-pt sweep, out-of-sample scaling check, public-data benchmark (optical channel).

Missing (minimum additional simulations, nothing more):
1. **Stylus sampling density** — Δx fixed at 200 nm; one 3-point sweep Δx ∈ {100, 200, 400 nm} at baseline parameters closes the only untested stylus axis. (1 sim set, ~minutes)
2. **In-model coherence envelope** — one optical variant with a Gaussian envelope of width 2.5 µm (SI has the parameters) to show the 15% cutoff shift internally. (1 sim)
3. **Ensemble re-run script** — 30 baseline seeds to regenerate `ensemble_stats.json` from code (fixes T4). (30 sims)
Nothing else is required; all other axes are already swept.

---

## PHASE 5 — REPRODUCIBILITY AUDIT

Strong: pinned Python/deps, fixed seeds (42, 123, stress-test seeds), 14/14 verification tests, figures generated from code, public-data provenance with SHA-256.

Gaps:
1. `ensemble_stats.json` — no generator script (T4). **Add one.**
2. No tabulated 180-point sweep parameter grid in SI (described in text only). **Add a 5-line table** (tip radii, NAs, H, σ).
3. The public benchmark depends on `h5py` (installed ad hoc); pin it in a dev-requirements file.
4. Water-filling figure (fig7b) uses a water-filling implementation inside `generate_missing_figures.py`; acceptable, but state the algorithm in the SI one-liner (already standard).

---

## PHASE 6 — FALSIFIABILITY AUDIT

| Prediction | Falsification pathway in manuscript? | Recommendation |
|---|---|---|
| H(f) computed matches measured H(f) within 3 dB (roadmap item 1) | Yes, explicit | keep |
| Scaling law δ≈1.9 with out-of-sample R²=0.51 | Yes (out-of-sample check exists) | state "a measured exponent outside 1.9±0.3 would falsify" |
| Equivalence fraction expands with NA/noise (roadmap) | Yes | keep |
| SNR-dependent bound | **No — no operational definitions** | After T2 fix: define Δx_eff (e.g., PSF second moment) and Δf_eff (e.g., effective bandwidth from \|H\|²) so the bound is computable from measured PSF/ITF/noise; add one falsification sentence |
| Trilemma | Yes (measurable quantities listed) | keep |
| γ (info loss vs H) null | n=3 inconclusive | phrase as "no H-dependence detectable at n=3; testable at larger n" |
| Water-filling artefact design | Yes (recommended artefact PSD) | keep |

---

## PHASE 7 — PRACTICAL IMPACT AUDIT

All quantities have interpretations (Practitioner's Summary table). Flags:
- **Ξ (Capacity–Uniformity Product)** — weakest practical quantity: κ is scale-dependent under the printed Gramian equation (T3). After fixing the equation, its interpretation survives.
- **SID ι(f) and water-filling** — illustrative diagnostics; fine, but explicitly labelled as such (already are).
- **ρ** — practical, with nonlinear-channel caveat (T9).
- **Anisotropy α** — definition-dependent; the manuscript already mandates same-definition comparisons. Keep.
- No quantity lacks physical/engineering/metrological interpretation; none need removal.

---

## PHASE 8 — JOURNAL FIT

Estimates (editorial judgement; after implementing the Top-20 fixes below):

**Surface Topography: Metrology and Properties (STMP)**
- Scope fit 90% · Novelty 65% · Significance 70% · Rigor 75% (→85% after fixes) · Clarity 85%
- Desk rejection: **25–35%** (length, computational-only; drops to ~15% if SI-anchored trimming is done)
- Major revision: 50% · Minor revision: 10% · Acceptance after revision: **60–70%**

**Measurement Science and Technology (MST)**
- Scope fit 80% · similar profile; slightly lower topically (STMP is the primary target), but equally viable as fallback.
- Key difference: MST referees are more measurement-general and less surface-specific; the information-theoretic sections would carry more weight there.

The manuscript is correctly targeted at STMP. The two things that most change the outcome are (a) the T1/T2 rigor fixes and (b) any signal that experimental follow-up is planned/feasible (already in the roadmap).

---

## PHASE 9 — REVIEWER SIMULATION

### Reviewer 1 — Surface metrology (hostile)

**Major comments.** (1) The stylus transfer result contradicts decades of Gaussian-tip filtering practice — the dilation argument and the empirical 2.2/0.91/0.74/0.57 values are convincing, but the manuscript should state the regime boundary explicitly in the abstract-level conclusions (currently buried in Methods). (2) Why is the stylus sampling fixed at 200 nm? A Δx sweep is needed before claiming sampling-scale roll-off. (3) The n=30 ensemble statistics cannot be regenerated from the repository. (4) Decision table mixes correlation-proxy MI with Shannon MI.
**Minor.** Tip radius tolerance (±100 nm) is the dominant uncertainty yet the main text assumes a perfect paraboloid; SI covers it but the main text should cross-reference. SI stress test uses 5 realisations/class — adequate.
**Recommendation:** Major revision (→ Accept after the fixes).

### Reviewer 2 — Optical physics (hostile)

**Major comments.** (1) "Broadband WLI" is simulated with a monochromatic OTF at 550 nm; the coherence envelope is excluded. The public-data comparison partially redeems this (1.15× cutoff), but the model must be labelled a monochromatic mean-λ approximation. (2) The optical channel ignores detector MTF and defocus in the baseline; variants exist but one in-model envelope variant would close the loop. (3) Phase-unwrapping model (1D, 1% errors) dominates optical RMSE — the equivalence-fraction conclusions are conditional on this rate; sensitivity is claimed in the Discussion but should be tabulated. (4) The public-data benchmark is excellent; make it a figure.
**Minor.** Aberration variants cite the Maréchal approximation — fine. NA=0.55 with λ=550 nm cutoff statements are correct.
**Recommendation:** Minor-to-Major revision (envelope variant + table), leaning accept.

### Reviewer 3 — Information theory / signal processing (hostile)

**Major comments.** (1) **The central bound has no derivation and no operational definitions of the effective widths** — this is the single most damaging gap in the manuscript. It must be derived (or anchored to a theorem with citation) with explicit definitions, otherwise the headline claim cannot stand. (2) The transfer-function convention is inconsistent: the operator equation is amplitude, the estimator is a power ratio, and the MI formula squares H. (3) The Gramian equation does not match the computed condition number; mixed units make κ scale-dependent. (4) MI depends on the noise-floor estimator (1.61 vs 1.71); choose one estimator, report one value with uncertainty. (5) ρ is computed under a Gaussian linear channel for a nonlinear dilation channel — the linearised caveat is present and appreciated.
**Minor.** Water-filling presentation is standard; fine. Fisher spectrum (fig8) is unreferenced.
**Recommendation:** Major revision.

**Panel aggregate:** Two major-revision recommendations and one minor-leaning-accept, with the first-round decision most likely **Major Revision** unless T1/T2 are fixed before submission — which is exactly why the fixes below should be applied *pre-submission*.

---

## PHASE 10 — FINAL ACTION PLAN (highest acceptance gain first)

Estimates: impact (1–5), reviewer impact (1–5), difficulty (1–5, 5=hard), time (h), acceptance gain (0–5).

| # | Action | Sci. | Rev. | Diff. | Time | Gain |
|---|--------|------|------|-------|------|------|
| 1 | Fix the H convention: define H as amplitude transfer; estimator = $\sqrt{\mathrm{PSD ratio}}$; state it in one sentence at Eq. transfer estimate; re-derive MI consistently. | 4 | 5 | 2 | 2 h | +5 |
| 2 | Derive or rigorously anchor the SNR-bound with operational definitions of Δx_eff/Δf_eff (e.g., second-moment PSF width and effective noise-bandwidth), 1 SI paragraph + citation anchor. | 5 | 5 | 3 | 3 h | +5 |
| 3 | Make Eq. gramian match the code (or the code match the equation); choose the unit-consistent definition and recompute Ξ_o/Ξ_s. | 4 | 4 | 2 | 1.5 h | +3 |
| 4 | Write the ensemble runner script (30 seeds) regenerating ensemble_stats.json; state seeds in SI. | 4 | 4 | 2 | 2 h + 1 h run | +3 |
| 5 | Soften abstract claim + cover-letter "new measurement limit" wording (Phase 2 table). | 2 | 4 | 1 | 0.5 h | +2 |
| 6 | Add explicit monochromatic mean-λ approximation sentence in Optical Simulation. | 3 | 4 | 1 | 0.25 h | +2 |
| 7 | One MI estimator everywhere (report 1.61 with CI; footnote the 1.71 alternative). | 3 | 3 | 2 | 1 h | +2 |
| 8 | Add the in-model coherence-envelope variant (1 sim) + one sentence in robustness. | 3 | 3 | 2 | 1 h | +2 |
| 9 | Stylus Δx sweep {100, 200, 400 nm} (1 sim set) + one sentence. | 2 | 3 | 1 | 1 h | +1.5 |
| 10 | Reference the public-benchmark figure in Results (fig_public_benchmark.pdf exists). | 1 | 3 | 1 | 0.25 h | +1.5 |
| 11 | Add falsification sentence for the bound and scaling law (Phase 6). | 2 | 3 | 1 | 0.5 h | +1.5 |
| 12 | Add 5-line sweep parameter table to SI. | 1 | 2 | 1 | 0.5 h | +1 |
| 13 | Rename ρ to "reconstructability R²" (one global substitution) to disarm the "novel metric" attack. | 1 | 3 | 1 | 0.25 h | +1 |
| 14 | Cross-reference tip-radius uncertainty (SI budget) from the stylus Methods. | 1 | 2 | 1 | 0.25 h | +1 |
| 15 | Third-person voice pass (editorial). | 1 | 2 | 2 | 1.5 h | +0.5 |
| 16 | Cite fig8/fig10 or delete the files (consistency). | 1 | 1 | 1 | 0.25 h | +0.5 |
| 17 | Pin h5py in a dev-requirements file for the benchmark. | 1 | 1 | 1 | 0.25 h | +0.5 |
| 18 | Search-basis footnote for the "no prior work" claims. | 1 | 2 | 1 | 0.25 h | +0.5 |
| 19 | Trim 2–3 pp of redundant Discussion prose to reduce desk risk. | 1 | 2 | 3 | 3 h | +1 (desk only) |
| 20 | Add explicit "no experimental facilities; roadmap offered as falsifiable targets" line to the abstract (one clause). | 1 | 2 | 1 | 0.25 h | +1 |

**Top-20 conclusion.** Actions 1–4 are the pre-submission must-do set (they kill the two critical and two high-severity findings). Actions 5–11 are strongly recommended and cost under a day combined. Actions 12–20 are cheap polish. Total effort ≈ 1.5–2 working days; expected effect: first-round decision moves from a likely Major Revision toward Minor Revision / Accept, and desk-rejection probability drops materially.
