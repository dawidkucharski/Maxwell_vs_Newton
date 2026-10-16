#!/usr/bin/env bash
# Re-fetch the public WLI-ITF dataset used by the Phase 7 benchmark.
# Hirose et al. 2025, Applied Optics 64:5461, DOI 10.1364/AO.562002
# Zenodo record 10.5281/zenodo.15750880, license CC-BY-4.0
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data_public/hirose2025
curl -L -o data_public/hirose2025/optica.tar.gz \
  "https://zenodo.org/records/15750880/files/optica.tar.gz?download=1"
echo "Verify SHA-256 against data_public/hirose2025/SHA256SUMS"
