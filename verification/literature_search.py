#!/usr/bin/env python3
"""Literature search for novelty audit — Crossref bibliographic queries.
Only records what the API returns (title/authors/year/DOI)."""
import urllib.request, urllib.parse, json, time

queries = {
    "stylus tip convolution transfer function": "stylus tip convolution spectral transfer surface",
    "stylus PSD attenuation": "stylus profilometry spatial frequency response power spectral density",
    "instrument transfer function areal": "instrument transfer function surface topography measurement",
    "cross-technique PSD comparison": "power spectral density comparison stylus optical profilometer",
    "information theory surface metrology": "information theory surface metrology topography measurement",
    "SNR uncertainty resolution": "signal-to-noise ratio uncertainty relation resolution limit imaging",
    "water-filling optical channel": "channel capacity incoherent imaging water filling",
    "morphological dilation surface": "morphological dilation tip surface topography simulation",
}

out = {}
for name, q in queries.items():
    url = ("https://api.crossref.org/works?query=" + urllib.parse.quote(q) +
           "&rows=6&select=DOI,title,author,container-title,published-print,issued")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LitAudit/1.0 (mailto:audit@example.org)"})
        with urllib.request.urlopen(req, timeout=25) as r:
            items = json.loads(r.read())["message"]["items"]
        out[name] = []
        for it in items:
            t = (it.get("title") or [""])[0][:130]
            j = (it.get("container-title") or [""])[0][:60]
            au = ", ".join(f"{a.get('family','')}" for a in (it.get("author") or [])[:3])
            yr = (it.get("published-print") or it.get("issued") or {}).get("date-parts", [[None]])[0][0]
            out[name].append({"doi": it.get("DOI"), "title": t, "journal": j, "authors": au, "year": yr})
        print(f"OK   {name}: {len(out[name])} hits")
    except Exception as e:
        print(f"FAIL {name}: {e}")
    time.sleep(0.4)

with open("/Users/dawid/Projects/Maxwell_vs_Newton/reports/literature_search_results.json", "w") as f:
    json.dump(out, f, indent=1)
print("saved.")
