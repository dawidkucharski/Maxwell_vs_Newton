# Literature and Novelty Audit — Phase 3

Date: 2026-10-16. Method: Crossref bibliographic searches (8 targeted queries), DOI metadata verification, prior verified bibliography. Note: no Scopus subscription available in this environment; Crossref + publisher records used. Claims qualified accordingly.

## Close prior work identified (all Crossref-verified, added to references.bib)

| Ref | What it establishes | Impact on this manuscript |
|-----|---------------------|---------------------------|
| Wu 1999 (Wear 230:194), Wu 2000 (MST 11:1369) | **Spectral analysis of stylus tip curvature effects on rough and fractal profiles** | Directly prior: the spectral consequences of stylus tips are established. Our contribution must be scoped to the cross-modality comparison and the dilation-simulator treatment, NOT "first spectral analysis of stylus effects". |
| McCool 1984 (J. Tribol. 106:202) | Effect of tip radius and flight on measured topography | Prior quantitative stylus-tip distortion work. |
| Clark & Greivenkamp 2002 (Prec. Eng. 26:405) | Ball-tip stylus tilt correction | Prior stylus geometry correction. |
| de Groot 2021 (J. Phys. Photonics 3:024004) | **Instrument transfer function for optical surface topography** | The definitive modern optical-ITF reference. Must be cited in the intro (currently missing). Novelty of "computing optical H from OTF" is reduced to "simulation implementation + cross-modality comparison". |
| Dai et al. 2020 (STMP 8:045025) | 2D ITF characterisation via a material measure (PTB) | Published in the target journal: 2D ITF characterisation exists experimentally. |
| Takacs et al. 2010 (IODC) | 2D↔1D PSD comparison considerations | Prior cross-dimensional PSD methodology. |
| Yashchuk et al. 2015 (have) + Hirose et al. 2025 (AO 64:5461) | Measured ITFs from binary pseudo-random arrays | Experimental ITF measurement exists for WLI; supports roadmap + gives a public-data benchmark (see Phase 4/7). |
| Leach & Sherlock 2013 (STMP 2:023001) | Super-resolution in surface topography measurement | Prior resolution-limit discussion in the target journal. |
| Haitjema 2015 (STMP 3:035004) | Uncertainty in surface topography measurement | Prior metrological-uncertainty framing. |
| Greco & Boyer 2019 (Signal Process. 164:217) | Angular resolution limit under compound Gaussian noise | Prior art for SNR-dependent resolution bounds → the manuscript's SNR bound must be presented as a metrological formulation, not a new limit. |
| Krüger-Sehm 2013 (Encyclopedia of Tribology) | Stylus profilometry reference chapter | Standard reference. |

## Claim-by-claim novelty disposition

1. "First-principles computation of H_stylus and H_optical without calibration artefacts" → **RETAIN but narrow**: components are known (OTF: standard optics; stylus spectral effects: Wu; ITF: de Groot, Yashchuk). The genuine additions: (a) the morphological-dilation simulator producing H≈1 with curvature bias (§ Phase 2 finding), (b) the paired cross-modality k-space comparison, (c) the information-theoretic comparison.
2. "SNR-dependent resolution–bandwidth trade-off as new limit" → **NARROW** to "metrological formulation", cite Greco & Boyer 2019 (already done in 2026-10-13 revision; add citation).
3. "No prior information-theoretic comparison of modalities" → **RETAIN with qualification** ("to the best of my knowledge… systematic") — no directly comparable paper found in the searches (closest: Leach & Sherlock super-resolution; Haitjema uncertainty; neither computes MI/capacity).
4. "Anisotropy tensor first quantitative measure of measurement-system anisotropy" → **RETAIN with qualification**; note 2D-PSD directionality analyses (Takacs 2010) as adjacent.
5. "Gaussian stylus transfer exp(−2π²r²f²)" → **REPLACE** (refuted by own simulator; §B of math audit). Wu 1999/2000 give the literature anchor for spectral stylus analysis.
6. "I ∝ exp(−5H)" → **REMOVE** (hardcoded placeholder; honest refit γ=−0.02±0.19, n=3).
7. "RMSE scaling law first simulation-derived" → RETAIN with exponent δ=1.90±0.13 (SE), R²=0.53, out-of-sample R²=0.51.

## Novelty summary for the cover letter

The defensible novel core: (i) a cross-modality k-space comparison framework that pairs a geometric dilation stylus model with an incoherent-OTF optical model on the same surfaces; (ii) empirical demonstration that the small-slope dilation transfer is ≈flat with a curvature bias (contrasting the classical Gaussian-filter idealisation); (iii) the first Shannon-theoretic comparison (MI, MMSE, water-filling) of tactile vs optical surface measurement channels; (iv) simulation-derived scaling and equivalence maps with quantified uncertainty and out-of-sample support.
