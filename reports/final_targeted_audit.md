# Final Targeted Audit — STMP manuscript and Supplementary Material

Date: 2026-10-20. Branch: `audit-science`. Sources audited: `elsarticle/manuscript.tex` (62 pp), `elsarticle/manuscript_supplementary.tex` (22 pp); no `manuscript(3).pdf` files were present in the repository, so the source files are authoritative. No project expansion: only minimal wording corrections were made.

| # | Issue checked | Evidence / code inspected | Action | Status |
|---|---|---|---|---|
| P1.1 | Bound status main text vs SI §4.3 | Abstract: "proposed and evaluated as a falsifiable benchmark"; §5.5: "metrological bound is adopted"; §4.1 practitioner text: "instrument-independent reference … expected to be bounded from below … a measured product substantially below this value would falsify the formulation"; SI S4.3: "adopted as a metrological ansatz … rather than a new theorem" | Dropped the word "derivation" from the §5.5 parenthetical (SI contains no proof); no other change needed — statuses are already aligned | VERIFIED AND FIXED |
| P1.2 | Universal-inequality wording | grep: no "cannot be reduced", "by any algorithm", "absolute" | None needed | VERIFIED |
| P1.3 | Eq. (17) trilemma dimensional audit | SI S4.3 explicit form: F = (A/2σ²)·(4π)⁻²·(1+1/SNR)²·log₂(1+SNR); A/σ² dimensionless, bits dimensionless → LHS I·Δx² [m²] ≡ RHS σ²·F [m²] | None needed; main text already states σ² cancels and SNR is the operative lever | VERIFIED AND RETAINED |
| P2.1 | Scaling law reproducibility | `verification/audit_scaling_law.py` re-run: slope 1.904±0.134; R² 0.531 in / 0.511 random-80/20 / 0.518 blocked / 0.523 leave-tip / 0.482 leave-NA; median ratio error ×1.93; p90 ×12.8 | None needed — matches manuscript | VERIFIED |
| P2.2 | 1/(π r_tip) vs actual attenuation | Methods: "retained as a definitional reference … not an attenuation point"; empirical 3 dB at ≈1049 mm⁻¹ stated separately | None needed | VERIFIED |
| P2.3 | Worked examples vs prediction error | Discussion example (ratio 17 → 2.2×10²; 1.71 → 2.8) is preceded by "order-of-magnitude ranking (median prediction error ≈ factor 2 … 90th percentile ≈ factor 13 …)" | None needed | VERIFIED |
| P2.4 | Descriptor, not rule | Abstract/Results/section title use "approximately described … order-of-magnitude descriptor" | None needed | VERIFIED |
| P3.1 | Empirical PSD ratio vs linear ITF | Methods: "an empirical power transfer function … additive noise enters the numerator and is not subtracted … upper-biased"; linearised model and cross-spectral check referenced | None needed | VERIFIED AND RETAINED WITH QUALIFICATION |
| P3.2 | Downstream quantities (anisotropy, equivalence, information loss) | All defined from the same empirical ratio with the stated convention | None needed | VERIFIED |
| P4.1 | Categorical "collapsed" wording | Discussion protocol and decision matrix said "the stylus response has collapsed" although the transfer rolls off gradually | Replaced with "has rolled off" (2 places) | VERIFIED AND FIXED |
| P4.2 | Conditionality of recommendations | Protocol was unconditional | Added: "conditional on the modelled surface class, sampling interval, noise assumptions and instrument models of this study" | VERIFIED AND FIXED |
| P4.3 | Above-cutoff statement | "Below 0.5 µm … neither modality resolves features within the modelled passband" present | None needed | VERIFIED |
| P4.4 | Wavelength↔frequency mapping | 2000 mm⁻¹ ↔ 0.5 µm; 670–2000 mm⁻¹ ↔ 0.5–1.5 µm; 454 mm⁻¹ ↔ 2.2 µm; protocol partition disjoint | None needed | VERIFIED |
| P5.1 | Hertzian plastic caveat | SI §1.1: "not quantitatively valid in the plastic regime … retained only as an order-of-magnitude scale" | None needed | VERIFIED |
| P5.2 | Skin-depth qualitative | SI §1.4 and regime map: "qualitative contrast between interaction volumes, not a literal measurement-depth equivalence" | None needed | VERIFIED |
| P5.3 | Fusion illustrative | SI §2.3 and Fig. S2 caption: "illustrative rather than a quantitative accuracy claim"; scale mismatch disclosed | None needed | VERIFIED AND RETAINED WITH QUALIFICATION |
| P5.4 | No new fusion experiment | — | None added | VERIFIED |
| Build | Manuscript + SI | Clean rebuild: 62 pp + 22 pp, 0 errors, 0 undefined citations | PDFs refreshed | VERIFIED |
| Tests | Verification suite | 18/18 pass (T1–T11) | — | VERIFIED |
| IMEKO abstract | Consistency check | No "collapsed"/"absolute"/universal-bound wording; bound described as benchmark; scaling as descriptor; protocol partition present | No changes needed | VERIFIED |

## Corrections applied (this audit)

1. "the stylus response has collapsed" → "has rolled off" (decision matrix, Discussion protocol) — matches the gradual simulated roll-off.
2. Protocol now explicitly conditional on the modelled surface class, sampling interval, noise assumptions and instrument models.
3. §5.5 bound parenthetical: "operational definitions and status" (dropped "derivation", since SI S4.3 is an ansatz, not a proof).

## Unresolved limitations (disclosed in the manuscript, not defects)

- Computational-only validation (two public cross-checks, one geometric).
- Scaling relation is an order-of-magnitude descriptor (median prediction error ×1.93).
- Fusion demonstration is illustrative; scatterometry PSD scale mismatch disclosed.
- Ξ and Π are heuristic figures of merit.

## Verdict

**READY.** Every priority item was checked against the actual sources, scripts and tests; the only required changes were the three minimal wording corrections above, now applied. Builds are clean (0 errors, 0 undefined) and the verification suite passes 18/18.
