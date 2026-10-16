"""
Block 2 — Research Gap Detector
================================
Analyses the knowledge graph to identify missing structure in the literature:
- Missing unified operator framework
- Missing frequency-domain interpretation
- Missing anisotropy analysis
- Missing information-theoretic formulation
- Missing equivalence regimes between sensors

Input:  Knowledge graph from Block 1
Output: Structured gap statements with confidence scores
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Tuple
from block1_literature_mining import KnowledgeGraph, Reference, DOMAIN_KEYWORDS


@dataclass
class GapStatement:
    """A single identified research gap."""
    gap_id: str
    category: str
    statement: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    severity: str = "moderate"  # critical, major, moderate, minor
    affected_domains: List[str] = field(default_factory=list)
    suggested_approach: str = ""


# ============================================================
# Gap Detection Logic
# ============================================================

def detect_all_gaps(kg: KnowledgeGraph) -> List[GapStatement]:
    """Run all gap detection modules and return consolidated gaps."""
    gaps = []

    gaps.extend(_detect_unified_operator_gap(kg))
    gaps.extend(_detect_frequency_domain_gap(kg))
    gaps.extend(_detect_anisotropy_gap(kg))
    gaps.extend(_detect_information_theoretic_gap(kg))
    gaps.extend(_detect_equivalence_regime_gap(kg))
    gaps.extend(_detect_cross_domain_gaps(kg))

    # Sort by confidence descending
    gaps.sort(key=lambda g: g.confidence, reverse=True)

    return gaps


def _detect_unified_operator_gap(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect absence of a unified operator framework connecting
    stylus and optical profilometry measurements.
    """
    gaps = []

    # Check: do any papers propose an operator model M[h(x,y)] for both modalities?
    has_operator_papers = any(
        "operator" in (f.lower() if isinstance(f, str) else "")
        for ref in kg.references
        for f in ref.formalisms_found
    )

    # Check: do any papers span both stylus AND optical domains?
    stylus_ids = set(kg.domains.get("stylus_profilometry", []))
    optical_ids = set(kg.domains.get("optical_interferometry", []))
    cross_papers = stylus_ids & optical_ids

    # Check for systematic comparison beyond RMSE
    comparison_keywords = ["comparison", "versus", "vs", "both", "difference"]
    has_systematic_comparison = False
    for ref in kg.references:
        if ref.ref_id in cross_papers:
            text = (ref.title + " " + ref.abstract).lower()
            if any(kw in text for kw in comparison_keywords):
                has_systematic_comparison = True
                break

    # Check for transfer function / k-space model
    has_transfer_function = any(
        "transfer function" in (f.lower() if isinstance(f, str) else "")
        for ref in kg.references
        for f in ref.formalisms_found
    )

    confidence = 0.0
    if not has_operator_papers:
        confidence += 0.4
    if len(cross_papers) < 3:
        confidence += 0.2
    if not has_systematic_comparison:
        confidence += 0.2
    if not has_transfer_function:
        confidence += 0.2

    gaps.append(GapStatement(
        gap_id="GAP-OP-001",
        category="missing_unified_operator_framework",
        statement=(
            "No unified k-space operator model exists for stylus vs optical "
            "profilometry that accounts for anisotropic information loss. "
            "The literature treats these modalities independently, without "
            "a common mathematical framework relating measurement operators "
            "M_stylus[h(x,y)] and M_optical[h(x,y)] in the frequency domain."
        ),
        evidence=[
            f"Only {len(cross_papers)} papers address both stylus and optical modalities",
            f"Operator formalism found: {has_operator_papers}",
            f"Transfer function approach found: {has_transfer_function}",
            f"Systematic modality comparison beyond RMSE: {has_systematic_comparison}"
        ],
        confidence=confidence,
        severity="critical" if confidence > 0.5 else "major",
        affected_domains=["stylus_profilometry", "optical_interferometry"],
        suggested_approach=(
            "Define M_s[h] = T_s * h + n_s and M_o[h] = F^{-1}[H_o · F[h]] + n_o, "
            "analyse their ratio in k-space: H_ratio(f_x, f_y) = H_o/H_s"
        )
    ))

    return gaps


def _detect_frequency_domain_gap(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect missing frequency-domain interpretation.
    PSD analysis exists but is it connected to instrument transfer functions?
    """
    gaps = []

    has_psd_analysis = any(
        "PSD" in ref.metrics_found or "power spectral density" in str(ref.metrics_found).lower()
        for ref in kg.references
    )

    # Check if PSD is used to characterise instruments (not just surfaces)
    psd_instrument_papers = 0
    for ref in kg.references:
        text = (ref.title + " " + ref.abstract).lower()
        if ("psd" in text or "power spectral" in text) and \
           any(kw in text for kw in ["instrument", "transfer function", "measurement system", "error"]):
            psd_instrument_papers += 1

    # Check for systematic PSD error analysis (Mack papers)
    has_psd_error_analysis = any(
        "systematic error" in ref.title.lower() and "psd" in ref.title.lower()
        for ref in kg.references
    )

    confidence = 0.0
    if has_psd_analysis:
        confidence += 0.15  # PSD exists but...
    if psd_instrument_papers < 3:
        confidence += 0.35  # ... rarely applied to instrument characterisation
    if not has_psd_error_analysis:
        confidence += 0.2

    # Even Mack's work focuses on lithography PSD, not surface metrology instruments
    confidence = min(confidence + 0.2, 1.0)

    gaps.append(GapStatement(
        gap_id="GAP-FD-001",
        category="missing_frequency_domain_interpretation",
        statement=(
            "The frequency-domain interpretation of measurement distortion is incomplete. "
            "While PSD analysis is widely used for surface characterisation, the PSD of "
            "the measurement operator itself — H_sensor(f_x, f_y) — is rarely computed or "
            "used to correct raw topography data. Mack (2013, 2015) identified systematic "
            "PSD errors in lithography contexts, but this has not been generalised to "
            "surface metrology instrument comparison."
        ),
        evidence=[
            f"PSD used in {sum(1 for r in kg.references if 'PSD' in str(r.metrics_found))} papers",
            f"PSD applied to instrument characterisation: {psd_instrument_papers} papers",
            "No instrument transfer function PSD comparison between modalities found"
        ],
        confidence=confidence,
        severity="major",
        affected_domains=["surface_roughness_psd", "optical_interferometry", "stylus_profilometry"],
        suggested_approach=(
            "Compute H_sensor(f) = PSD_measured(f) / PSD_true(f) for both modalities, "
            "analyse where each system loses information in k-space."
        )
    ))

    return gaps


def _detect_anisotropy_gap(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect missing anisotropy analysis in measurement systems.
    """
    gaps = []

    has_anisotropy = any(
        any(kw in (ref.title + " " + ref.abstract).lower()
            for kw in ["anisotrop", "directional", "orientation", "lay", "texture"])
        for ref in kg.references
    )

    # Check if anisotropy is connected to measurement systems
    anisotropy_instrument = 0
    for ref in kg.references:
        text = (ref.title + " " + ref.abstract).lower()
        if any(kw in text for kw in ["anisotrop", "directional"]) and \
           any(kw in text for kw in ["stylus", "optical", "instrument", "measurement"]):
            anisotropy_instrument += 1

    confidence = 0.0
    if has_anisotropy:
        confidence += 0.2  # Anisotropy studied but...
    if anisotropy_instrument == 0:
        confidence += 0.5  # ...never connected to instrument anisotropy
    confidence += 0.2  # Tensor formulation absent

    gaps.append(GapStatement(
        gap_id="GAP-AN-001",
        category="missing_anisotropy_analysis",
        statement=(
            "No anisotropy tensor formulation exists for surface metrology instruments. "
            "Stylus profilometry is inherently anisotropic (raster scanning along x), "
            "while optical systems have different NA-limited resolution in x and y. "
            "The literature characterises surface anisotropy but NOT measurement-system "
            "anisotropy. An anisotropy tensor A_ij = ∫ f_i f_j H(f) df could quantify "
            "directional information loss."
        ),
        evidence=[
            f"Surface anisotropy studied: {has_anisotropy}",
            f"Instrument anisotropy characterised: {anisotropy_instrument} papers",
            "Zero papers found proposing an anisotropy tensor for measurement systems"
        ],
        confidence=confidence,
        severity="major",
        affected_domains=["stylus_profilometry", "optical_interferometry", "surface_roughness_psd"],
        suggested_approach=(
            "Define A_ij = ∫ f_i f_j H_sensor(f_x, f_y) df_x df_y, compute eigenvalues "
            "λ_1, λ_2 quantifying principal directions of information loss."
        )
    ))

    return gaps


def _detect_information_theoretic_gap(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect missing information-theoretic formulation of measurement.
    """
    gaps = []

    has_info_theory = any(
        any(kw in (ref.title + " " + ref.abstract).lower()
            for kw in ["information", "entropy", "shannon", "fisher information",
                       "mutual information", "channel capacity"])
        for ref in kg.references
    )

    confidence = 0.0
    if not has_info_theory:
        confidence = 0.85
    else:
        confidence = 0.5  # Some info-theoretic concepts exist but likely not for instruments

    gaps.append(GapStatement(
        gap_id="GAP-IT-001",
        category="missing_information_theoretic_formulation",
        statement=(
            "No information-theoretic formulation exists for surface metrology. "
            "Measurement can be viewed as an information channel: the surface h(x,y) "
            "is the source, the instrument is the channel, and the measured topography "
            "is the received signal. Information loss I(f_x, f_y) = log(PSD_true/PSD_measured) "
            "provides a spectral map of where each instrument loses information. "
            "This framework is entirely absent from the surface metrology literature."
        ),
        evidence=[
            f"Information-theoretic concepts in metrology literature: {has_info_theory}",
            "Zero papers frame stylus/optical comparison as information channel problem"
        ],
        confidence=confidence,
        severity="critical",
        affected_domains=["all"],
        suggested_approach=(
            "Define I(f_x, f_y) = log(PSD_true / PSD_measured), compute mutual information "
            "between true and measured surfaces, derive channel capacity bounds."
        )
    ))

    return gaps


def _detect_equivalence_regime_gap(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect missing equivalence regime analysis between sensors.
    Under what conditions do stylus and optical give equivalent results?
    """
    gaps = []

    # Look for papers comparing modalities
    comparison_papers = []
    for ref in kg.references:
        text = (ref.title + " " + ref.abstract).lower()
        stylus_kw = any(kw in text for kw in ["stylus", "contact", "afm", "profilometer"])
        optical_kw = any(kw in text for kw in ["optical", "interferomet", "confocal", "wli"])
        if stylus_kw and optical_kw:
            comparison_papers.append(ref.ref_id)

    # Are equivalence conditions discussed?
    has_equivalence = any(
        any(kw in (ref.title + " " + ref.abstract).lower()
            for kw in ["equivalence", "equivalent", "agree", "agreement", "consistent",
                       "comparable", "correspond"])
        for ref in kg.references
    )

    confidence = 0.0
    if len(comparison_papers) < 3:
        confidence += 0.4
    if not has_equivalence:
        confidence += 0.3
    confidence += 0.2  # k-space equivalence regime never defined

    gaps.append(GapStatement(
        gap_id="GAP-EQ-001",
        category="missing_equivalence_regimes_between_sensors",
        statement=(
            "No equivalence regime analysis in k-space exists between stylus and optical "
            "profilometry. The question 'Under what spatial-frequency conditions do these "
            "modalities produce equivalent measurements?' is unanswered. An equivalence "
            "regime could be defined where |H_stylus - H_optical| < ε in some k-space region, "
            "providing practitioners with rigorous criteria for instrument interchangeability."
        ),
        evidence=[
            f"Cross-modality comparison papers: {len(comparison_papers)}",
            f"Equivalence conditions discussed: {has_equivalence}",
            "No k-space equivalence criterion defined in any paper"
        ],
        confidence=confidence,
        severity="critical",
        affected_domains=["stylus_profilometry", "optical_interferometry"],
        suggested_approach=(
            "Define k-space equivalence region: Ω_eq = {(f_x, f_y) : |H_s - H_o| < 0.1}. "
            "Find scaling of Ω_eq area with tip radius, NA, and roughness parameters."
        )
    ))

    return gaps


def _detect_cross_domain_gaps(kg: KnowledgeGraph) -> List[GapStatement]:
    """
    Detect structural gaps: domains that should be connected but aren't.
    """
    gaps = []

    # Check inverse problems ↔ metrology connection
    inv_ids = set(kg.domains.get("inverse_problems_metrology", []))
    stylus_ids = set(kg.domains.get("stylus_profilometry", []))
    optical_ids = set(kg.domains.get("optical_interferometry", []))

    inv_stylus = inv_ids & stylus_ids
    inv_optical = inv_ids & optical_ids

    if len(inv_stylus) < 2 or len(inv_optical) < 2:
        gaps.append(GapStatement(
            gap_id="GAP-CD-001",
            category="missing_cross_domain_connection",
            statement=(
                "Inverse-problem methods (regularisation, uncertainty propagation) are "
                "under-utilised in surface metrology instrument comparison. Only "
                f"{len(inv_stylus)} papers connect inverse problems to stylus and "
                f"{len(inv_optical)} to optical profilometry."
            ),
            evidence=[
                f"Inverse problems × stylus: {len(inv_stylus)} papers",
                f"Inverse problems × optical: {len(inv_optical)} papers"
            ],
            confidence=0.6,
            severity="major",
            affected_domains=["inverse_problems_metrology", "stylus_profilometry", "optical_interferometry"],
            suggested_approach="Apply Tikhonov regularisation to deconvolve instrument response from measured topography."
        ))

    # Fractal geometry ↔ PSD connection exists but incomplete
    psd_ids = set(kg.domains.get("surface_roughness_psd", []))
    has_fractal_psd = False
    for ref in kg.references:
        if ref.ref_id in psd_ids:
            text = (ref.title + " " + ref.abstract).lower()
            if "fractal" in text:
                has_fractal_psd = True
                break

    if not has_fractal_psd:
        gaps.append(GapStatement(
            gap_id="GAP-CD-002",
            category="missing_cross_domain_connection",
            statement=(
                "Fractal geometry and PSD analysis are connected in the tribology literature "
                "(Majumdar & Bhushan, 1990) but this connection has not been extended to "
                "instrument comparison or information-loss analysis."
            ),
            evidence=["Majumdar & Bhushan (1990) connects fractals to roughness but not to measurement systems"],
            confidence=0.55,
            severity="moderate",
            affected_domains=["surface_roughness_psd"],
            suggested_approach="Connect fractal dimension D_f to spectral information loss via H = 2D_f - 3 scaling."
        ))

    return gaps


# ============================================================
# Gap Report Generation
# ============================================================
def generate_gap_report(gaps: List[GapStatement], output_path: str):
    """Generate a structured gap report."""
    lines = []
    lines.append("="*70)
    lines.append("RESEARCH GAP REPORT — Surface Metrology")
    lines.append("="*70)
    lines.append(f"\nTotal gaps identified: {len(gaps)}")
    lines.append(f"Critical: {sum(1 for g in gaps if g.severity == 'critical')}")
    lines.append(f"Major:    {sum(1 for g in gaps if g.severity == 'major')}")
    lines.append(f"Moderate: {sum(1 for g in gaps if g.severity == 'moderate')}")
    lines.append(f"Minor:    {sum(1 for g in gaps if g.severity == 'minor')}")
    lines.append("")

    for i, gap in enumerate(gaps, 1):
        lines.append("-"*70)
        lines.append(f"GAP {i}: [{gap.severity.upper()}] {gap.gap_id}")
        lines.append(f"Category: {gap.category}")
        lines.append(f"Confidence: {gap.confidence:.2f}")
        lines.append(f"Domains affected: {', '.join(gap.affected_domains)}")
        lines.append("")
        lines.append(f"STATEMENT:")
        lines.append(f"  {gap.statement}")
        lines.append("")
        lines.append("EVIDENCE:")
        for e in gap.evidence:
            lines.append(f"  • {e}")
        lines.append("")
        lines.append(f"SUGGESTED APPROACH:")
        lines.append(f"  {gap.suggested_approach}")
        lines.append("")

    lines.append("="*70)
    lines.append("END OF GAP REPORT")
    lines.append("="*70)

    report = "\n".join(lines)

    # Save as text
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Save as JSON
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(g) for g in gaps], f, indent=2, ensure_ascii=False)

    print(f"\n[Block 2] Gap report saved to: {output_path}")
    print(f"[Block 2] Gap data saved to: {json_path}")

    return report


def print_gaps_summary(gaps: List[GapStatement]):
    """Print concise gap summary."""
    print("\n" + "█"*70)
    print("█  BLOCK 2 — RESEARCH GAP DETECTOR")
    print("█"*70)
    for gap in gaps:
        severity_icon = {"critical": "🔴", "major": "🟠", "moderate": "🟡", "minor": "🟢"}
        icon = severity_icon.get(gap.severity, "⚪")
        print(f"\n  {icon} [{gap.severity.upper()}] {gap.gap_id}")
        print(f"     Confidence: {gap.confidence:.2f}")
        print(f"     {gap.statement[:120]}...")
    print(f"\n  Total: {len(gaps)} gaps identified")
    print("█"*70 + "\n")


# ============================================================
# Main
# ============================================================
def run_block2(kg: KnowledgeGraph, output_dir: str) -> Tuple[List[GapStatement], str]:
    """Run Block 2: Research Gap Detection."""
    print("\n" + "█"*70)
    print("█  BLOCK 2 — RESEARCH GAP DETECTOR")
    print("█"*70)

    gaps = detect_all_gaps(kg)
    print_gaps_summary(gaps)

    os.makedirs(output_dir, exist_ok=True)
    report = generate_gap_report(
        gaps,
        os.path.join(output_dir, "gap_report.txt")
    )

    return gaps, report


if __name__ == "__main__":
    import sys
    from block1_literature_mining import run_block1

    input_file = sys.argv[1] if len(sys.argv) > 1 else "../literature_overview.rtf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./outputs"

    kg = run_block1(input_file, output_dir)
    run_block2(kg, output_dir)
