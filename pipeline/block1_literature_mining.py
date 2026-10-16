"""
Block 1 — Literature Mining
===========================
Parses literature overview, extracts structured knowledge,
and builds a knowledge graph of the surface metrology domain.

Input:  literature_overview.rtf (Scopus AI abstracts/reviews)
Output: Structured knowledge graph (JSON + in-memory)
"""

import re
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from striprtf.striprtf import rtf_to_text


# ============================================================
# Domain ontology
# ============================================================
DOMAIN_KEYWORDS = {
    "stylus_profilometry": [
        "stylus", "profilometer", "contact profilometry", "diamond tip",
        "scanning force microscopy", "AFM", "atomic force microscopy",
        "tip radius", "morphological", "raster scan"
    ],
    "optical_interferometry": [
        "white light interferometry", "WLI", "interferometer", "optical profilometry",
        "confocal microscopy", "phase shifting", "Fourier optics",
        "NA", "numerical aperture", "optical transfer function",
        "image reconstruction", "interferometric"
    ],
    "surface_roughness_psd": [
        "power spectral density", "PSD", "power spectrum", "spectral analysis",
        "autocorrelation", "spatial frequency", "roughness exponent",
        "fractal", "surface topography", "areal surface", "spectral"
    ],
    "inverse_problems_metrology": [
        "inverse problem", "regularisation", "regularization", "ill-posed",
        "uncertainty propagation", "error propagation", "systematic error",
        "correction method", "artifacts", "reconstruction"
    ],
    "afm_metrology": [
        "AFM", "atomic force", "nonlinear distortion", "force microscopy",
        "topographic images", "nanoscale"
    ]
}

METRICS_PATTERNS = [
    r"\bRMSE\b", r"\bRa\b", r"\bSa\b", r"\bRq\b", r"\bSq\b",
    r"\bPSD\b", r"power spectral density", r"\bRz\b", r"\bRt\b",
    r"root mean square", r"roughness average", r"\bRsk\b", r"\bRku\b",
    r"autocorrelation", r"correlation length", r"fractal dimension",
    r"Hurst exponent", r"roll-off", r"modulation transfer function",
    r"MTF"
]

FORMALISM_PATTERNS = [
    r"Fourier", r"convolution", r"transfer function", r"operator",
    r"Zernike", r"wavelet", r"multifractal", r"Green.s function",
    r"Helmholtz", r"diffraction", r"Kirchhoff", r"Rayleigh",
    r"morphological filter", r"envelope", r"motif",
    r"Gaussian process", r"stochastic process"
]

LIMITATION_PATTERNS = [
    r"(?:limitation|limited by|constrain|drawback|disadvantage|artifact|bias|error|systematic|not able|cannot|fail|missing|lack|absence|unresolved)\b[^.]*\.",
    r"(?:however|nevertheless|although|despite|unfortunately)[^.]*\.",
    r"(?:does not|do not|is not|are not|remains|still)[^.]*?(?:account|capture|consider|address|resolve|measure|characterise)[^.]*\."
]


@dataclass
class Reference:
    """A single literature reference."""
    ref_id: int
    title: str
    authors: List[str]
    journal: str
    year: str
    citations: int
    abstract: str = ""
    domain_tags: List[str] = field(default_factory=list)
    metrics_found: List[str] = field(default_factory=list)
    formalisms_found: List[str] = field(default_factory=list)
    limitations_found: List[str] = field(default_factory=list)


@dataclass
class KnowledgeGraph:
    """Structured knowledge graph for the domain."""
    domains: Dict[str, List[int]] = field(default_factory=dict)  # domain -> [ref_ids]
    metrics_used: Dict[str, List[str]] = field(default_factory=dict)  # metric -> papers
    formalisms: Dict[str, List[int]] = field(default_factory=dict)
    limitations: List[str] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    cross_domain_links: List[Tuple[int, int, str]] = field(default_factory=list)


# ============================================================
# RTF Parser
# ============================================================
def parse_rtf_literature(rtf_path: str) -> List[Reference]:
    """Parse the RTF literature file into structured references."""
    with open(rtf_path, 'r', encoding='utf-8', errors='replace') as f:
        rtf_content = f.read()

    text = rtf_to_text(rtf_content)

    # Split into individual reference blocks
    # Pattern: "Reference Ncitations" or "Reference N citations"
    blocks = re.split(r'\n(?=Reference\s+\d+)', text)

    references = []
    for block in blocks:
        ref = _parse_single_reference(block)
        if ref:
            references.append(ref)

    return references


def _parse_single_reference(block: str) -> Optional[Reference]:
    """Parse a single reference block."""
    # Extract reference number and citation count
    header_match = re.match(
        r'Reference\s+(\d+)\s*(?:citations?)?\s*\n?',
        block
    )
    if not header_match:
        header_match = re.match(
            r'Reference\s+(\d+)\s*\n?',
            block
        )
    if not header_match:
        return None

    ref_id = int(header_match.group(1))

    # Extract citation count
    citations_match = re.search(r'(\d+)\s*citations?', block)
    citations = int(citations_match.group(1)) if citations_match else 0

    # Split into lines
    lines = block.strip().split('\n')

    # Title is typically the first line after "Reference X ... citations"
    title = ""
    authors = []
    journal = ""
    year = ""

    # Find title (first substantial line after header)
    title_start = 1 if citations_match else 1
    for i, line in enumerate(lines):
        if i == 0:
            continue
        line_clean = line.strip()
        if not line_clean:
            continue
        if 'opens author details' in line_clean.lower():
            continue
        if 'opens journal info' in line_clean.lower():
            continue
        if 'opens document details' in line_clean.lower():
            continue
        if line_clean.lower() == 'show abstract':
            continue
        if re.match(r'^\d{4}$', line_clean):
            year = line_clean
            continue
        if not title and len(line_clean) > 10:
            title = line_clean
            continue

    # Extract authors
    for line in lines:
        if 'opens author details' in line.lower():
            author = line.split(',')[0].strip()
            if author and author not in authors:
                authors.append(author)

    # Extract journal
    for i, line in enumerate(lines):
        if 'opens journal info' in line.lower():
            # Journal name is usually the line before
            if i > 0:
                journal = lines[i-1].strip()

    # If we couldn't find journal from the marker, look for known journal names
    if not journal:
        known_journals = [
            "Proceedings of SPIE", "Measurement Science and Technology",
            "Surface Topography: Metrology and Properties",
            "Journal of Tribology", "Applied Optics",
            "Journal of Micro/Nanolithography", "Materials",
            "Journal of Applied Physics", "Review of Scientific Instruments",
            "Measurement", "Pure and Applied Geophysics",
            "Journal of Physical Chemistry C", "SPE Journal",
            "Journal of Vacuum Science", "Technisches Messen",
            "Optics InfoBase Conference Papers",
            "Characterisation of Areal Surface Texture",
            "Applied Sciences", "Journal of Geophysical Research"
        ]
        for jn in known_journals:
            if jn.lower() in block.lower():
                journal = jn
                # Year often follows journal name
                yr_match = re.search(re.escape(jn) + r'\s*\n?\s*(\d{4})', block)
                if yr_match:
                    year = yr_match.group(1)
                break

    # Try to extract year if not found
    if not year:
        yr_match = re.search(r'\b(19\d{2}|20\d{2})\b', block)
        if yr_match:
            year = yr_match.group(1)

    ref = Reference(
        ref_id=ref_id,
        title=title,
        authors=authors,
        journal=journal,
        year=year,
        citations=citations,
        abstract=block  # Store full block as abstract proxy
    )

    # Tag domains
    ref = _tag_domains(ref)

    # Extract metrics, formalisms, limitations
    ref = _extract_features(ref)

    return ref


def _tag_domains(ref: Reference) -> Reference:
    """Tag reference with relevant domains."""
    text_lower = (ref.title + " " + ref.abstract + " " + ref.journal).lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                if domain not in ref.domain_tags:
                    ref.domain_tags.append(domain)
                break
    return ref


def _extract_features(ref: Reference) -> Reference:
    """Extract metrics, formalisms, and limitations from reference text."""
    text = ref.title + " " + ref.abstract

    for pattern in METRICS_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if m.upper() not in [x.upper() for x in ref.metrics_found]:
                ref.metrics_found.append(m)

    for pattern in FORMALISM_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if m not in ref.formalisms_found:
                ref.formalisms_found.append(m)

    # Extract limitations from abstract
    for pattern in LIMITATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if m not in ref.limitations_found:
                ref.limitations_found.append(m)

    return ref


# ============================================================
# Knowledge Graph Builder
# ============================================================
def build_knowledge_graph(references: List[Reference]) -> KnowledgeGraph:
    """Build structured knowledge graph from parsed references."""
    kg = KnowledgeGraph(references=references)

    # Build domain -> reference mapping
    for domain in DOMAIN_KEYWORDS:
        kg.domains[domain] = []

    for ref in references:
        for tag in ref.domain_tags:
            if tag in kg.domains:
                kg.domains[tag].append(ref.ref_id)

    # Aggregate metrics
    for ref in references:
        for metric in ref.metrics_found:
            metric_key = metric.upper().strip()
            if metric_key not in kg.metrics_used:
                kg.metrics_used[metric_key] = []
            kg.metrics_used[metric_key].append(ref.title[:60])

    # Aggregate formalisms
    for ref in references:
        for formalism in ref.formalisms_found:
            if formalism not in kg.formalisms:
                kg.formalisms[formalism] = []
            kg.formalisms[formalism].append(ref.ref_id)

    # Aggregate limitations
    for ref in references:
        kg.limitations.extend(ref.limitations_found)

    # Cross-domain links: references spanning multiple domains
    for ref in references:
        if len(ref.domain_tags) >= 2:
            for i in range(len(ref.domain_tags)):
                for j in range(i+1, len(ref.domain_tags)):
                    kg.cross_domain_links.append(
                        (ref.ref_id, ref.ref_id,
                         f"{ref.domain_tags[i]} ↔ {ref.domain_tags[j]}")
                    )

    return kg


def print_knowledge_summary(kg: KnowledgeGraph):
    """Print a structured summary of the knowledge graph."""
    print("\n" + "="*70)
    print("KNOWLEDGE GRAPH SUMMARY")
    print("="*70)

    print(f"\nTotal references: {len(kg.references)}")

    print("\n--- DOMAINS ---")
    for domain, ref_ids in sorted(kg.domains.items(), key=lambda x: -len(x[1])):
        print(f"  {domain}: {len(ref_ids)} papers")

    print("\n--- METRICS USED ---")
    for metric, papers in sorted(kg.metrics_used.items(), key=lambda x: -len(x[1])):
        print(f"  {metric}: {len(papers)} papers")

    print("\n--- FORMALISMS FOUND ---")
    for formalism, ref_ids in sorted(kg.formalisms.items(), key=lambda x: -len(x[1])):
        print(f"  {formalism}: {len(ref_ids)} papers")

    print(f"\n--- LIMITATIONS EXTRACTED ---")
    print(f"  {len(kg.limitations)} limitation statements found")

    print(f"\n--- CROSS-DOMAIN LINKS ---")
    print(f"  {len(kg.cross_domain_links)} cross-domain connections")

    # Citation analysis
    print("\n--- TOP CITED ---")
    top = sorted(kg.references, key=lambda r: r.citations, reverse=True)[:5]
    for ref in top:
        print(f"  [{ref.ref_id}] {ref.citations:4d} cit. — {ref.title[:70]}")

    print("="*70 + "\n")


def export_knowledge_graph(kg: KnowledgeGraph, output_path: str):
    """Export knowledge graph to JSON."""
    data = {
        "domains": kg.domains,
        "metrics_used": kg.metrics_used,
        "formalisms": kg.formalisms,
        "limitations": kg.limitations,
        "cross_domain_links": [
            {"ref_a": a, "ref_b": b, "link": l}
            for a, b, l in kg.cross_domain_links
        ],
        "references": [
            {
                "ref_id": r.ref_id,
                "title": r.title,
                "authors": r.authors,
                "journal": r.journal,
                "year": r.year,
                "citations": r.citations,
                "domain_tags": r.domain_tags,
                "metrics_found": r.metrics_found,
                "formalisms_found": r.formalisms_found,
                "limitations_found": r.limitations_found[:3]
            }
            for r in kg.references
        ],
        "statistics": {
            "total_references": len(kg.references),
            "domains": {d: len(ids) for d, ids in kg.domains.items()},
            "total_limitation_statements": len(kg.limitations)
        }
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Block 1] Knowledge graph exported to: {output_path}")


# ============================================================
# Main
# ============================================================
def run_block1(input_path: str, output_dir: str) -> KnowledgeGraph:
    """Run Block 1: Literature Mining pipeline."""
    print("\n" + "█"*70)
    print("█  BLOCK 1 — LITERATURE MINING")
    print("█"*70)

    print(f"\nParsing: {input_path}")
    references = parse_rtf_literature(input_path)
    print(f"Parsed {len(references)} references")

    kg = build_knowledge_graph(references)
    print_knowledge_summary(kg)

    os.makedirs(output_dir, exist_ok=True)
    export_knowledge_graph(kg, os.path.join(output_dir, "knowledge_graph.json"))

    return kg


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "../literature_overview.rtf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./outputs"
    run_block1(input_file, output_dir)
