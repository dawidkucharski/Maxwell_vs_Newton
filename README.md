# Maxwell_vs_Newton — k-Space Transfer Functions for Surface Metrology

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23493875.svg)](https://doi.org/10.5281/zenodo.23493875)

Automated discovery pipeline for comparing stylus profilometry, white-light
interferometry (WLI), and scatterometry through a unified $k$-space operator
framework.

## System Requirements

- Python 3.9+
- Required packages: numpy, scipy, matplotlib, pyyaml, striprtf
- LaTeX (TinyTeX or TeX Live) with `elsarticle` class for manuscript compilation

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline Structure

| Block | File | Purpose |
|-------|------|---------|
| 1 | `block1_literature_mining.py` | Parse literature, build knowledge graph |
| 2 | `block2_gap_detector.py` | Identify research gaps |
| 3 | `block3_hypothesis_generator.py` | Generate testable hypotheses |
| 4 | `block4_physics_simulator.py` | Simulate surfaces and measurements |
| 5 | `block5_discovery_engine.py` | Compute transfer functions, PSD, metrics |
| 6 | `block6_novelty_detector.py` | Detect novel findings |
| 7 | `block7_publication_generator.py` | Generate LaTeX manuscript draft |
| 8 | `block8_info_theory.py` | Information-theoretic analysis |
| 9 | `block9_advanced_physics.py` | Contact mechanics, diffraction physics |
| 10 | `block10_scatterometry.py` | Rayleigh-Rice scatterometry simulation |

## Quick Start

```bash
cd pipeline
python pipeline_main.py
```

This runs the full pipeline end-to-end. Outputs appear in `outputs/iter01/`.

## Reproducibility

All random seeds are explicitly set (base seed = 42). To reproduce exact results:

```python
from block4_physics_simulator import SimulationParams, generate_self_affine_surface
params = SimulationParams(grid_size=512, hurst_exponent=0.7, rms_roughness=5e-8,
                          tip_radius=2e-6, na=0.55, wavelength=550e-9)
np.random.seed(42)
h = generate_self_affine_surface(params, seed=42)
```

Ensemble statistics (n=30) are available in `outputs/iter01/ensemble/ensemble_stats.json`.

## Configuration

Edit `pipeline/config.yaml` to modify simulation parameters:
- `grid_size`: Simulation grid (512 for main, 256 for sweep)
- `hurst_exponent`: Surface self-affinity (0.3–0.9)
- `rms_roughness`: RMS height in metres
- `tip_radius`: Stylus tip radius in metres
- `na`: Numerical aperture
- `wavelength`: Optical wavelength in metres

## Manuscript

The manuscript (`elsarticle/manuscript.tex`) compiles with:

```bash
cd elsarticle
rm -f manuscript.aux manuscript.bbl manuscript.blg
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

## License

This project is part of ongoing research at Poznan University of Technology,
Institute of Mechanical Engineering. Contact: dawid.kucharski@put.poznan.pl

## Citation

Please cite this repository as:

> Kucharski, D. (2026). Maxwell_vs_Newton: A Unified k-Space
> Operator Framework for Stylus and Optical Profilometry (Version 1.0.2).
> Zenodo, https://doi.org/10.5281/zenodo.23493875. GitHub repository,
> https://github.com/dawidkucharski/Maxwell_vs_Newton.

Each GitHub release is archived on Zenodo and receives its own DOI
automatically.

## Public data provenance

The public-data cross-checks use the CC-BY-4.0 dataset of Hirose et al.
(Zenodo 10.5281/zenodo.15750880, DOI 10.1364/AO.562002) and the CC-BY-4.0
ball-standard profiles of Aksulu (Zenodo 10.5281/zenodo.4471347), fetched by
`verification/fetch_public_data.sh` with provenance recorded in `data_public/`.
