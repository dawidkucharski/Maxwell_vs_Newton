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
    "Theory for Closing the Accuracy Gap'. Repository: "
    "https://github.com/dawidkucharski/Maxwell_vs_Newton")
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

# Vocabulary ids verified against https://zenodo.org/api/vocabularies/
RESOURCE_TYPE = "software"
RIGHTS_ID = "mit-cmu"


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


def metadata_body(resource_type_as_object=True):
    """InvenioRDM metadata (nested under 'metadata' as Zenodo now expects).

    The new /api/records endpoint accepts the resource type as an object
    {"id": ...}; the legacy deposit endpoint wants a plain string.
    """
    rtype = ({"id": RESOURCE_TYPE} if resource_type_as_object
             else RESOURCE_TYPE)
    return {
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
            "resource_type": rtype,
            "publication_date": PUBLICATION_DATE,
            "description": DESCRIPTION,
            "version": VERSION,
            "keywords": [{"subject": k} for k in KEYWORDS],
            "rights": [{"id": RIGHTS_ID}],
        }
    }


def _auth(url, token, bearer, headers):
    if token:
        if bearer:
            headers["Authorization"] = f"Bearer {token}"
        else:
            sep = "&" if "?" in url else "?"
            url += sep + "access_token=" + urllib.parse.quote(token)
    return url


def _upload_one(token, base, path, bearer):
    """Try several upload variants until one returns 2xx."""
    name = path.name
    data = path.read_bytes()
    ctype = "application/zip" if path.suffix == ".zip" else "application/pdf"
    boundary = "----zenodo-upload-7f3a2c"
    part = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; '
            f'filename="{name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n").encode()
    body = part + data + f"\r\n--{boundary}--\r\n".encode()
    variants = [
        (base, "POST", body,
         f"multipart/form-data; boundary={boundary}"),
        (f"{base}/{name}", "PUT", data, ctype),
        (f"{base}/{name}", "PUT", data, "application/octet-stream"),
    ]
    for url, method, payload, hdr_ct in variants:
        headers = {"Content-Type": hdr_ct}
        url = _auth(url, token, bearer, headers)
        req = urllib.request.Request(url, data=payload, headers=headers,
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                if resp.status in (200, 201, 202):
                    return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            continue
    return False


def upload_files(token, rec, files, bearer, records_base):
    """Upload via InvenioRDM draft-files endpoint or legacy bucket link."""
    rid = rec.get("id")
    links = rec.get("links", {}) or {}
    if "files" in links:
        base = links["files"]
    elif "bucket" in links:
        base = links["bucket"]
    else:
        base = f"{records_base}/{rid}/draft/files"
    for path in files:
        if not _upload_one(token, base, path, bearer):
            raise RuntimeError(f"upload failed for {path.name}")


def deposit(token, files, bearer, depo_base, records_base,
            resource_type_as_object=True):
    status, rec = http("POST", depo_base, token=token,
                       data=metadata_body(resource_type_as_object),
                       bearer=bearer)
    if status not in (200, 201) or not rec or "id" not in rec:
        raise RuntimeError(f"draft creation failed (status {status}): {rec}")
    rid = rec["id"]
    upload_files(token, rec, files, bearer, records_base)
    status, _ = http("POST",
                     f"{depo_base}/{rid}/actions/publish",
                     token=token, bearer=bearer)
    if status not in (200, 202):
        raise RuntimeError(f"publish failed: status {status}")
    status, rec = http("GET", f"{records_base}/{rid}", token=token,
                       bearer=bearer)
    doi = None
    try:
        doi = rec["metadata"]["pids"]["doi"]["identifier"]
    except (KeyError, TypeError):
        pass
    if not doi:
        try:
            doi = rec["metadata"]["prereserve_doi"]["doi"]
        except (KeyError, TypeError):
            doi = f"10.5281/zenodo.{rid}"
    return doi, rid


def main():
    token = get_token()
    tag = get_tag()
    print(f"release tag : {tag}")
    files = build_files(tag)
    print("files       : " + ", ".join(str(p.name) for p in files))
    doi = None
    attempts = [
        ("new API (Bearer)", True,
         "https://zenodo.org/api/records",
         "https://zenodo.org/api/records", True),
        ("legacy API (token query)", False,
         "https://zenodo.org/api/deposit/depositions",
         "https://zenodo.org/api/records", False),
    ]
    for name, bearer, depo_base, records_base, rtype_obj in attempts:
        try:
            doi, rid = deposit(token, files, bearer, depo_base, records_base,
                               rtype_obj)
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
