#!/usr/bin/env python3
"""Deposit the current release of Maxwell_vs_Newton to Zenodo and mint a DOI.

Usage
-----
    export ZENODO_TOKEN='<your token>'   # or create ~/.zenodo_token (chmod 600)
    python tools/zenodo_release.py

Works locally and inside GitHub Actions (tag taken from GITHUB_REF_NAME).
Tries the current Zenodo REST API first and falls back to the legacy
deposit API. The token is read from the environment or ~/.zenodo_token
and is never printed.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

TITLE = ("Maxwell_vs_Newton: A Unified k-Space Operator Framework for "
         "Stylus and Optical Profilometry")
DESCRIPTION = (
    "Simulation pipeline, verification suite and generated outputs for "
    "comparing stylus profilometry and optical interferometry through "
    "instrument transfer functions, spectral information loss, anisotropy, "
    "equivalence regimes and information-theoretic diagnostics. Companion "
    "to the manuscript 'Optical Profilometry Versus the Stylus: A Spectral "
    "Theory for Closing the Accuracy Gap'.")
AFFILIATION = ("Institute of Mechanical Technology, "
               "Poznan University of Technology, Poland")
KEYWORDS = [
    "surface metrology",
    "stylus profilometry",
    "white-light interferometry",
    "instrument transfer function",
    "power spectral density",
    "information theory",
]
PUBLICATION_DATE = "2026-10-20"
VERSION = "1.0.0"
REPO_URL = "https://github.com/dawidkucharski/Maxwell_vs_Newton"


def get_token():
    token = os.environ.get("ZENODO_TOKEN", "").strip()
    if not token:
        p = pathlib.Path.home() / ".zenodo_token"
        if p.exists():
            token = p.read_text().strip()
    if not token:
        sys.exit("ZENODO_TOKEN not found. Export it in the shell or create "
                 "~/.zenodo_token (chmod 600).")
    return token


def get_tag():
    ref = os.environ.get("GITHUB_REF_NAME", "").strip()
    if ref.startswith("v"):
        return ref
    try:
        out = subprocess.run(["git", "describe", "--tags", "--abbrev=0"],
                             cwd=ROOT, capture_output=True, text=True,
                             check=True)
        tag = out.stdout.strip()
        if tag:
            return tag
    except subprocess.CalledProcessError:
        pass
    return "v1.0.0"


def build_files(tag):
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / f"Maxwell_vs_Newton-{tag}.zip"
    subprocess.run(["git", "archive", "--format=zip", "-o", str(zip_path),
                    tag], cwd=ROOT, check=True)
    files = [zip_path]
    for src, dst in [
        (ROOT / "elsarticle/manuscript.pdf", DIST / "manuscript.pdf"),
        (ROOT / "IMEKO_2027/class_iwc2027_v2/"
               "imeko-wc-extended-abstract.pdf",
         DIST / "imeko-wc-extended-abstract.pdf"),
    ]:
        if src.exists():
            shutil.copyfile(src, dst)
            files.append(dst)
    return files


def http(method, url, token=None, data=None, raw=None, bearer=True,
         content_type="application/json"):
    headers = {}
    if token:
        if bearer:
            headers["Authorization"] = f"Bearer {token}"
        else:
            if "?" in url:
                url += "&"
            else:
                url += "?"
            url += "access_token=" + urllib.parse.quote(token)
    if data is not None:
        headers["Content-Type"] = content_type
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    elif raw is not None:
        headers["Content-Type"] = content_type
        body = raw
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
            if not payload:
                return resp.status, None
            return resp.status, json.loads(payload)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:800]
        return err.code, {"error": detail}
    except urllib.error.URLError as err:
        return 0, {"error": str(err)}


def deposit_new(token, files, tag):
    meta = {
        "metadata": {
            "title": TITLE,
            "creators": [{
                "person_or_org": {
                    "type": "personal",
                    "name": "Kucharski, Dawid",
                    "given_name": "Dawid",
                    "family_name": "Kucharski",
                    "affiliations": [{"name": AFFILIATION}],
                }
            }],
            "resource_type": {"id": "software"},
            "publication_date": PUBLICATION_DATE,
            "description": DESCRIPTION,
            "version": VERSION,
            "keywords": [{"subject": k} for k in KEYWORDS],
            "rights": [{"id": "MIT", "title": {"en": "MIT License"}}],
        }
    }
    status, rec = http("POST", "https://zenodo.org/api/records",
                       token=token, data=meta)
    if status not in (200, 201) or "id" not in rec:
        raise RuntimeError(f"new-API draft creation failed: {rec}")
    rid = rec["id"]
    base = f"https://zenodo.org/api/records/{rid}/draft/files"
    for path in files:
        status, _ = http("PUT", f"{base}/{path.name}", token=token,
                         raw=path.read_bytes(),
                         content_type="application/octet-stream")
        if status not in (200, 201):
            raise RuntimeError(f"new-API upload failed for {path.name}: "
                               f"status {status}")
    status, _ = http("POST",
                     f"https://zenodo.org/api/records/{rid}/draft/"
                     "actions/publish", token=token)
    if status not in (200, 202):
        raise RuntimeError(f"new-API publish failed: status {status}")
    status, rec = http("GET", f"https://zenodo.org/api/records/{rid}",
                       token=token)
    doi = None
    try:
        doi = rec["metadata"]["pids"]["doi"]["identifier"]
    except (KeyError, TypeError):
        doi = f"10.5281/zenodo.{rid}"
    return doi, rid


def deposit_legacy(token, files, tag):
    meta = {
        "title": TITLE,
        "description": DESCRIPTION,
        "upload_type": "software",
        "creators": [{"name": "Kucharski, Dawid",
                      "affiliation": AFFILIATION}],
        "license": "MIT",
        "access_right": "open",
        "version": VERSION,
        "keywords": KEYWORDS,
        "publication_date": PUBLICATION_DATE,
        "related_identifiers": [
            {"relation": "isSupplementTo", "identifier": REPO_URL,
             "resource_type": "software"},
        ],
    }
    status, rec = http("POST",
                       "https://zenodo.org/api/deposit/depositions",
                       token=token, data=meta, bearer=False)
    if status not in (200, 201) or "id" not in rec:
        raise RuntimeError(f"legacy-API draft creation failed: {rec}")
    did = rec["id"]
    bucket = rec["links"]["bucket"]
    for path in files:
        status, _ = http("PUT", f"{bucket}/{path.name}", token=token,
                         raw=path.read_bytes(), bearer=False,
                         content_type="application/octet-stream")
        if status not in (200, 201):
            raise RuntimeError(f"legacy-API upload failed for {path.name}: "
                               f"status {status}")
    status, rec = http("POST",
                       f"https://zenodo.org/api/deposit/depositions/{did}/"
                       "actions/publish", token=token, bearer=False)
    if status not in (200, 202):
        raise RuntimeError(f"legacy-API publish failed: status {status}")
    doi = None
    try:
        doi = rec["metadata"]["prereserve_doi"]["doi"]
    except (KeyError, TypeError):
        doi = f"10.5281/zenodo.{did}"
    return doi, did


def main():
    token = get_token()
    tag = get_tag()
    print(f"release tag : {tag}")
    files = build_files(tag)
    print("files       : " + ", ".join(str(p.name) for p in files))
    doi = None
    for name, fn in (("new API", deposit_new), ("legacy API",
                                                deposit_legacy)):
        try:
            doi, rid = fn(token, files, tag)
            print(f"deposited via {name}, record {rid}")
            break
        except Exception as err:  # noqa: BLE001 - fallback is intentional
            print(f"{name} failed: {err}")
    if not doi:
        sys.exit("Zenodo deposit failed on both API variants.")
    DIST.mkdir(exist_ok=True)
    (DIST / "doi.txt").write_text(doi + "\n")
    print()
    print(f"DOI         : {doi}")
    print(f"landing page: https://doi.org/{doi}")
    print(f"badge       : [![DOI](https://zenodo.org/badge/DOI/{doi}.svg)]"
          f"(https://doi.org/{doi})")


if __name__ == "__main__":
    main()
