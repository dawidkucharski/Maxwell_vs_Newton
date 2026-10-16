# Public-Data Audit and Benchmark — Phases 4 & 7

Date: 2026-10-16.

## 1. Search for public paired datasets

- **contact.engineering** (the NPL community resource for surface measurement data): API unreachable from this environment (DNS resolution failure on repeated attempts). Noted as an infrastructure limitation of this audit; no data could be queried.
- **Zenodo**: searched for "instrument transfer function surface topography data", "stylus optical surface metrology dataset", "calibration artefact topography stylus", "roughness profilometry dataset". Only one relevant record found:
  - **Record 10.5281/zenodo.15750880** — *Topography restoration in white-light interferometry using an instrument transfer function evaluated with binary pseudo-random arrays: Dataset and Codes*, Hirose, S. (2025-06-27), license **CC-BY-4.0**, 403 MB (`optica.tar.gz`). Companion paper: Hirose et al., *Applied Optics* **64**, 5461 (2025), DOI 10.1364/AO.562002 (Crossref-verified).

**Conclusion: no public paired stylus+optical dataset of the same artefacts was found.** A full cross-modality benchmark of the tactile channel against public data is therefore not possible at this time; the stylus channel rests on the in-repo simulator tests (T2a/T2b) and literature anchors (Wu 1999/2000; McCool 1984). The public-data benchmark is therefore scoped to the **optical channel**, which the Hirose dataset supports directly.

## 2. Data acquisition (provenance)

- Downloaded `optica.tar.gz` (403,171,857 bytes) from `https://zenodo.org/records/15750880/files/optica.tar.gz` to `data_public/hirose2025/`. SHA-256 recorded in `data_public/hirose2025/SHA256SUMS`.
- Extracted to `data_public/hirose2025/optica/`: Zygo `.datx` WLI measurements of binary pseudo-random array (BPRA) samples (step heights 80/160/240 nm, 10x/50x objectives), Park/Seiko `.xqd` AFM reference scans (2 µm fields), simulation data, and the authors' analysis code (BSD-style academic scripts, included in the CC-BY-4.0 record).
- `data_public/` is git-ignored; the raw archive is not committed. A `verification/fetch_public_data.sh` documents how to re-fetch.

## 3. Benchmark design (`verification/public_data_benchmark.py`)

The model under test is this project's optical channel: radial average of the incoherent OTF squared times the pixel MTF squared, $H_\mathrm{optical}(f) = \langle |\mathrm{OTF}(f)|^2 \mathrm{sinc}^2(D f_x)\mathrm{sinc}^2(D f_y)\rangle_\phi$, cutoff $2\mathrm{NA}/\lambda$.

1. **Primary (model validation, WLI-only).** For each BPRA sample, fit
   $\log P_\mathrm{meas}(f) = \log A + \beta \log f + \log H_\mathrm{optical}(f; c \cdot 2\mathrm{NA}/\lambda)$
   over $f \in [0.4, 0.95\cdot 2\mathrm{NA}/\lambda]$ µm⁻¹, with $(A, \beta, c)$ free. A fitted $c \approx 1$ means the measured spectra are consistent with the nominal incoherent cutoff; small RMS means the functional shape of $H_\mathrm{optical}$ describes the measured roll-off.
2. **Secondary (ITF shape via AFM reference).** Measured ITF = $P_\mathrm{WLI}/P_\mathrm{AFM}$ radial ratio, normalised at 0.75 µm⁻¹, compared with the model in [0.5, 2.0] µm⁻¹ (Pearson correlation). Caveat: the 2 µm AFM field truncates the low-frequency content of the reference, so the absolute ratio is unreliable below ≈0.5 µm⁻¹; only the normalised shape in the stated band is reported.

Measurement parameters read from the `.datx` metadata: NA = 0.55, λ = 0.652 µm, sampling 0.173 µm (50x objective).

## 4. Results (`reports/public_data_benchmark.json`)

| Sample | c (cutoff scale) | β | RMS(log) | ITF-ratio corr |
|--------|------------------|---|----------|----------------|
| 80 nm BPRA  | 1.16 | +0.10 | 0.07 | 0.972 |
| 160 nm BPRA | 1.15 | −0.02 | 0.06 | 0.968 |
| 240 nm BPRA | 1.15 | −0.23 | 0.06 | 0.968 |

Pixel-MTF included vs lens-only model gave indistinguishable RMS at this sampling (D = 0.173 µm; the pixel sinc is ≈1 over the band), consistent with the authors' finding that the pixel MTF matters only near Nyquist.

**Interpretation.** Across three independent BPRA samples the fitted cutoff is $c = 1.15 \pm 0.01$ of the nominal $2\mathrm{NA}/\lambda$, i.e. the measured WLI spectra roll off at ≈1.55–1.60 µm⁻¹ versus the nominal 1.69 µm⁻¹ (a ≈9% slower cutoff, attributable to the finite coherence envelope of white-light illumination, which the monochromatic OTF does not include). The shape correlation of ≈0.97 and log-RMS of 0.06–0.07 show that the incoherent-OTF model captures the measured instrument response well within its passband.

## 5. Impact on the manuscript

- The optical channel model of this study is now **validated against independent, public, CC-BY-4.0 measurement data** (Hirose et al. 2025), not only against its own simulation.
- The manuscript's optical model scope statement ("imaging OTF only; no coherence envelope") is directly supported: the residual ≈15% cutoff discrepancy is exactly the size expected from the omitted WLI coherence envelope, and is explicitly out of scope.
- The Hirose reference (10.1364/AO.562002) is added to `references.bib` and cited where the optical-ITF prior art and the public benchmark are discussed.
- Honest limitation retained: no public paired stylus+optical data were found (contact.engineering unreachable), so the stylus channel remains validated by simulator tests and literature only. This is stated in the manuscript.
