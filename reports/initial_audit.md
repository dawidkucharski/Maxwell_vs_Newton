# Initial Repository and Manuscript Audit — Maxwell_vs_Newton

Date: 2026-10-16
Branch: `stmp-revision` (pristine baseline committed on `main` at `ed79ded`)

## 1. Project inventory

| Path | Content |
|------|---------|
| `README.md` | Pipeline overview, quick start, seed policy (base 42) |
| `requirements.txt` | Pinned versions (numpy 2.0.2, scipy 1.13.1, matplotlib 3.9.4, scikit-image 0.24.0, PyYAML 6.0.3, striprtf) |
| `literature_overview.rtf` | Sole literature input to Block 1 |
| `pipeline/block1…block11`, `parameter_sweep.py`, `visualisation.py`, `pipeline_main.py`, `regenerate_roadmap.py`, `config.yaml` | Simulation/discovery pipeline |
| `pipeline/outputs/iter01/**` | Baseline outputs (sim, discovery, ensemble n=30, non-Gaussian, stress_test, info_theory, limitations, robustness, gap_closure, scatterometry, novelty, publication, figures) |
| `pipeline/outputs/sweep/**` | 180-point sweep results + scaling-law fits |
| `elsarticle/manuscript.tex` | Main manuscript (51 pp PDF, hand-edited, diverges from Block-7 auto-draft) |
| `elsarticle/manuscript_supplementary.tex` | Supplementary (18 pp) |
| `elsarticle/cover_letter.tex` | STMP cover letter (3 pp) |
| `elsarticle/references.bib` | 69 entries; DOIs verified 2026-06-30 |
| `elsarticle/PANEL_AUDIT_v4.md`, `Q1_AUDIT*.md`, `latex_audit_report.txt` | Prior audit history |
| `elsarticle/manuscript_base.tex`, `manuscript_derivations.tex`, `cover_letter_MST.*` | **Stale files (cleanliness issue)** |

## 2. Manuscript section map (main)

1 Introduction · 2 Methods (operator formalism, simulation, analysis, sweep) · 3 Results (accuracy, H(f), info loss, anisotropy, equivalence, scaling) · 4 Discussion (practitioner, info-theory value, prior work, robustness, limitations, roadmap, gap-closure) · 5 Information-Theoretic Analysis (channel, MI, SID, MMSE, SNR bound, trilemma, Ξ, research gap) · 6 Conclusions · Acknowledgements · Data Availability.

## 3. Equation/symbol inventory (central)

- `eq:operator` M[h] = F⁻¹[H·F[h]] + η — linear shift-invariant (LSI) operator model
- `eq:factorisation` H = H_aperture·H_sampling·H_noise
- `eq:hstylus` H_stylus ≈ exp(−2π²r²(fx²+fy²))·sinc(πfxΔx)·sinc(πfyΔy)
- `eq:hoptical` incoherent circular-aperture OTF, f̃ = λf/(2NA)
- `eq:psd`, `eq:transfer_est` (PSD-ratio H estimate), `eq:gum`, `eq:info_loss`, `eq:anisotropy`, `eq:equivalence`
- `eq:mutual_info(_cont)`, `eq:sid`, `eq:mmse`, `eq:metrological_uncertainty`, `eq:trilemma`, `eq:gramian`, `eq:xi`
- SI: Hertz (eq:hertz), Rayleigh–Rice (eq:rayleigh_rice), water-filling (eq:waterfilling), I-MMSE (eq:immse), trilemma explicit form (eq:trilemma_explicit)

## 4. Figures/tables and code provenance

| Asset | Generator | Reproducible? |
|-------|-----------|---------------|
| fig1–fig6 | `pipeline/visualisation.py` | ✅ |
| fig7_channel_capacity | **no generator in repo** | ⚠️ regenerate |
| fig8_cramer_rao | **no generator in repo** | ⚠️ regenerate (not referenced by manuscript) |
| fig9_three_way | `block10_scatterometry.py` | ✅ |
| fig10_ensemble_validation | **no generator in repo** | ⚠️ regenerate |
| fig_roadmap | `regenerate_roadmap.py` (reconstructed) | ✅ |
| figS1_stress_test | `block11_stress_test.py` | ✅ |
| figS2_fusion_demo | **no generator in repo** | ⚠️ regenerate |
| Tables | hand-written in TeX; numbers traced to JSONs below | ✅ (see §6) |

## 5. Baseline reproduction

`pipeline_main.py` ran to completion 2026-10-16 (fresh run). Block-7 auto-draft regenerated (auto title/journal differ from the hand-edited manuscript — expected, block 7 is a draft scaffold).

## 6. Claims vs. evidence (verified against JSONs)

| Manuscript claim | Source JSON | Match |
|---|---|---|
| RMSE 16.3 / 29.3 nm; r 0.964 / 0.834 | `iter01/sim/simulation_meta.json` | ✅ (16.286, 29.292; 0.9637, 0.8342) |
| α_s 0.0049±0.0026, α_o 0.0031±0.0018 (n=30) | `ensemble/ensemble_stats.json` | ✅ (0.00486±0.00259; 0.00309±0.00176) |
| f_cross 311±173 mm⁻¹ | ensemble JSON | ✅ (310,690±173,278) |
| eq 18.3%±0.2% | ensemble JSON | ✅ (0.1834±0.0020) |
| L_s 2.76e12, L_o 1.35e12; bands 0.07/0.30/0.46 | `discovery/discovery_metrics.json` | ✅ |
| MI proxy 0.90 / 0.70 → MIR 1.28 | discovery JSON | ✅ (0.9031/0.7042=1.282) |
| C_o/C_s = 1.71, modes 254,542 / 97,301 | `info_theory/info_theory_results.json` | ✅ (ratio 1/0.5859=1.707; ranks 254,542/97,301) |
| Scaling exponent 1.90, R² 0.53 (n=180) | `sweep/scaling_law_fits.json` | ✅ (1.9043, 0.5305) |
| f_cross ∝ r^−0.07, R² 0.26 | sweep fits | ✅ (0.0683, 0.2569) |
| α_s sweep 0.014±0.011 | sweep fits | ⚠️ JSON n_points=5 (tip radii only), manuscript says n=180 — reconcile |
| **I ∝ exp(−γH), γ≈5** | sweep fits | ❌ **HARDCODED** (`gamma: 5.0`, `I_0: 100.0`, `gamma_std: Infinity`) — no real fit |
| Gaussian vs Poisson 3.6% | `limitations/quantified_limits.json` | ✅ (~3.7% difference; note absolute values 68.5 nm from 256-grid harness, not baseline) |
| Grid convergence 12% @N=512 | `gap_closure/grid_convergence.json` | ✅ ((18.51−16.29)/18.51=12.0%) |
| eq_frac grid trend 0.52→0.45→0.30→0.21 | grid_convergence.json | ✅ (matches new text) |
| **Linearity boundary wording** | `limitations/quantified_limits.json` | ❌ **see Critical Finding 1** |

## 7. Critical findings

1. **Linearity validity paragraph is wrong in both historical versions.** Data (σ vs RMSE): σ=5–20 nm → actual/linear ≈ 0.003 (discretisation floor); σ=50 nm → 0.34; σ=100 nm → 0.96 (crossing); σ=150–200 nm → 1.34–1.60 (nonlinear super-linear). Truth: sub-linear below ~75 nm, crossing ≈100 nm, super-linear above. The `rmse_linear` reference is itself anchored at the baseline simulation RMSE (σ/50·16.3), i.e. not an independent linear prediction. Manuscript must state the actual crossing behaviour with these numbers.
2. **info-loss-vs-H fit is a placeholder** (γ=5 hardcoded, std=∞). The manuscript's γ≈5 claim is unsupported by any fit. Recompute honestly from the 3-point sweep or remove/qualify.
3. **capacity_efficiency_optical = 1.265 > 1** in block8 — definitional bug (efficiency must ≤1 for a true capacity). Not quoted in manuscript, but fix or document; manuscript's "capacity" language must match what was actually computed (water-filled or MI-for-fixed-prior).
4. **F_integrated_stylus == F_integrated_optical** in block8 (ratio 1.0) — degenerate; not quoted in manuscript. Document/fix.
5. **α_s sweep n mismatch**: sweep fit JSON reports n_points=5 for stylus anisotropy; manuscript reports n=180. Recompute α across all 180 combos or correct n.
6. **Figure generators missing** for fig7, fig8, fig10, figS2 (one-off scripts lost). Rebuild from data.
7. **Stale files** in elsarticle (manuscript_base.tex, manuscript_derivations.tex, cover_letter_MST.*, stray aux/log) — clean or delete.
8. Stylus simulator is a true geometric morphological-dilation model (paraboloid tip truncated at cone contact radius) with bilinear raster interpolation — better than the analytic Gaussian model; the Gaussian H_stylus is only the small-slope approximation. Domains of validity need quantitative statement (cf. finding 1).
9. Optical simulator implements incoherent OTF with support 2NA/λ (code: f_norm = f/(2·f_cutoff)) but metadata labels NA/λ as `optical_cutoff_m`=1.0e6. Manuscript was corrected to 2NA/λ on 2026-10-13; code metadata still reports NA/λ — keep code as-is (convention documented in manuscript) but record the convention in reproducibility docs.
10. Reference audit (2026-06-30): 20 DOIs corrected, titles verified; 3 uncited entries have no valid DOI (documented). Re-verify at Phase 9.
11. Auto-generated Block-7 draft says "Journal: Precision Engineering" and a different title — the submission manuscript is the hand-edited elsarticle files; the auto-draft is not part of the submission (documented divergence).

## 8. Reproducibility blockers

- Missing figure generators (finding 6).
- Placeholder fit (finding 2).
- `quantified_limits.json` and `model_variants.json`, `grid_convergence.json`, `gap_closure_sweep.json` generators not in repo (one-off scripts) — reconstruct or document.
- No environment lockfile beyond requirements.txt (acceptable); no container.
- `.venv` present and working (numpy 2.0.2 etc.).
