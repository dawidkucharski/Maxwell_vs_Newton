# Baseline Audit — reproducible submission state

Date: 2026-10-18. Branch: `audit-science` (created from `stmp-revision` @ d51d6d0; pristine original preserved in git history, `main` @ ed79ded).

## Environment and commands

- Python: 3.9 venv at `.venv/` (NumPy 2.0.2, SciPy 1.13.1, Matplotlib 3.9.4, scikit-image, h5py, PyYAML).
- Tests: `.venv/bin/python verification/run_tests.py` → **18/18 passed** (T1–T11; T10/T11 added this audit).
- LaTeX: TinyTeX; `cd elsarticle && rm -f *.bbl && for f in manuscript manuscript_supplementary cover_letter; do pdflatex -interaction=nonstopmode $f; bibtex $f; pdflatex $f; pdflatex $f; done` → 0 errors, 0 undefined citations.
- Seeds: surface generation + sweep 42; unwrapping-error stream 123; 30-member ensemble 100–129; audit ensembles 200–219.

## Headline result → producing artefact map

| # | Headline result | Producing artefact | Status |
|---|---|---|---|
| 1 | Stylus H = 2.2/0.91/0.74/0.57 at 17/292/567/843 mm⁻¹; 3 dB at 1049 mm⁻¹ | `pipeline/variant_simulations.py` (ratio of azimuthal means, Hanning periodogram, seed 42, N=512); reproduced this audit → 2.228/0.913/0.737/0.569, 1049 mm⁻¹. Locked by T10. | **Verified** |
| 2 | Stylus H ≈ 1 + curvature bias (low-f excess); not Gaussian tip | `pipeline/block4_physics_simulator.py` (`grey_dilation`, paraboloid tip, cone 45°, raster 100–400 nm); fresh ensemble (seeds 200–219): PSD-ratio lowest bin 1.92, linearised bias model 1.70, cross-spectral mid-band 0.945, coherence mid 0.97 | **Verified** |
| 3 | Δx sweep: RMSE 13.6/16.3/16.7 nm; 3 dB 1255/1049/671 mm⁻¹ | `pipeline/variant_simulations.py` → regenerated identical values this audit | **Verified** |
| 4 | Polychromatic OTF: 96.5 % of passband within 3 dB | same script → 0.965 | **Verified** |
| 5 | Optical OTF support at 2NA/λ = 2000 mm⁻¹ | `block4` `optical_cutoff = NA/λ`, normalisation `f/(2·f_cutoff)`; T1 pupil-autocorrelation | **Verified** |
| 6 | Equivalence fraction 9.6 % ± 0.3 %, f_cross 454±166 mm⁻¹ | `pipeline/run_ensemble.py` → `pipeline/outputs/iter01/ensemble/ensemble_stats.json` | **Verified (n=30, N=512)** |
| 7 | Grid convergence 0.25/0.20/0.098/0.042 | `pipeline/run_grid_convergence.py` | **Verified** |
| 8 | Scaling relation exponent 1.90±0.13, R²=0.53/0.51 | `pipeline/outputs/sweep/sweep_results.json` + `verification/fix_scaling_fits.py`; independent blocked-CV audit this session: slope 1.904±0.134, R²_in 0.531, R²_blocked 0.518, leave-tip 0.523, leave-NA 0.482, null R²=0, median ratio error ×1.93, p90 ×12.8, residual–σ correlation 0.81 | **Verified + downgraded (order-of-magnitude descriptor)** |
| 9 | MI slope of information loss ≈0.4 over 0.05–1.5 mm⁻¹ | T8 (uses committed h_true/h_stylus arrays); band is inside FOV limits (fundamental 10 mm⁻¹, Nyquist ≈2.56 mm⁻¹) | **Verified** |
| 10 | MMSE formula / I-MMSE | Eq. checked analytically; T11 Monte Carlo Wiener: rel. diff 0.2 % | **Verified** |
| 11 | MI expression (1/2)Σ log₂(1+SNR) | Correct for real fields; pipeline `C_total` omits the 1/2 (sums both Hermitian halves) — ratios unaffected; stated in manuscript terminology note | **Verified, documented** |
| 12 | Mode counts 254,542 / 97,301 | **Not reproducible from committed artefacts** → replaced by 127,472 / 61,631 (SNR>1, difference-field floor, N=512; `verification/audit_mode_counts.py`) | **Replaced** |
| 13 | Public optical benchmark c = 1.15±0.01 | `verification/public_data_benchmark.py` + `data_public/hirose2025/` | **Verified; scope clause added** |
| 14 | Ball-standard parallel-curve check 3–5 % | `verification/ball_standard_benchmark.py` (synthetic-geometry cross-check) + T9 | **Verified (geometric only)** |
| 15 | Contact mechanics (a=201 nm, ψ=5.83) | SI §1.1 closed-form; verified by re-derivation (a=(3RF/4E)^(1/3)=201 nm ✓). Groove-depth/r_eff elastic-extrapolation REMOVED (invalid in plastic regime) | **Corrected** |
| 16 | ρ CVs 0.22 / 0.067 | 0.22 = 4-class (incl. saturating deterministic), 0.16 = Gaussian+ground only, 0.067 = six-class (n=5); now stated like-for-like in abstract/Conclusions | **Reconciled** |
| 17 | Anisotropy α_s/α_o ensemble + sweep | `ensemble_stats.json`, `sweep_results.json` | **Verified** |
| 18 | MI proxy 0.907/0.706; per-band losses 0.071/0.296/0.446 | `ensemble_stats.json` | **Verified** |
| 19 | Roadmap 48 %→87 % (N=256) | `pipeline/run_gap_closure.py` | **Verified (grid-qualified)** |
| 20 | Ξ_o/Ξ_s = 5.9; Π_s/Π_o | `block8_info_theory.py` output | **Verified** |

## Unverified-at-source artefacts (resolved this audit)

- `pipeline/outputs/iter01/*.npy` (h_stylus/h_optical/H_*_2d) are stale relative to current `block4` code; they are not used for headline claims. Fresh regeneration reproduces all quoted values (rows 1–5). (Keep, documented.)
- The published ball-standard profiles cannot support a tip-level validation (44–120 µm scatter); only the geometric parallel-curve check is claimed.
