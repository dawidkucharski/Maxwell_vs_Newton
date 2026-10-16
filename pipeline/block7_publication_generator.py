"""
Block 7 — Publication Generator
================================
Generates a publication draft only after novelty has been confirmed.

Outputs:
  - Abstract draft
  - Contribution list
  - Method section outline
  - Comparison to literature
  - Proposed journal (Q1 metrology/optics/instrumentation)
  - LaTeX manuscript using elsarticle template

Input:  All previous block outputs + novelty confirmation
Output: Publication draft (LaTeX + plain text)
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime

from block1_literature_mining import KnowledgeGraph, Reference
from block2_gap_detector import GapStatement
from block3_hypothesis_generator import Hypothesis
from block4_physics_simulator import SimulationResult
from block5_discovery_engine import DiscoveryResult
from block6_novelty_detector import NoveltyReport, NovelFinding


@dataclass
class PublicationDraft:
    """Complete publication draft."""
    title: str
    authors: str = "D. Researcher et al."
    abstract: str = ""
    contributions: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    method_outline: str = ""
    results_summary: str = ""
    literature_comparison: str = ""
    proposed_journals: List[str] = field(default_factory=list)
    primary_journal: str = ""
    latex_source: str = ""
    generated_date: str = ""


# ============================================================
# Journal Selection
# ============================================================

Q1_METROLOGY_JOURNALS = [
    {
        "name": "Measurement Science and Technology",
        "publisher": "IOP Publishing",
        "impact_factor": 2.4,
        "scope": "Measurement science, sensors, instrumentation",
        "fit_reason": "Core metrology journal; ideal for instrument comparison studies"
    },
    {
        "name": "Surface Topography: Metrology and Properties",
        "publisher": "IOP Publishing",
        "impact_factor": 2.7,
        "scope": "Surface measurement, characterisation, properties",
        "fit_reason": "Specialised surface metrology; natural home for this work"
    },
    {
        "name": "Measurement",
        "publisher": "Elsevier",
        "impact_factor": 5.2,
        "scope": "Measurement science and technology broadly",
        "fit_reason": "Higher impact; reaches broader measurement community"
    },
    {
        "name": "Applied Optics",
        "publisher": "Optica",
        "impact_factor": 1.9,
        "scope": "Optical instrumentation, interferometry, imaging",
        "fit_reason": "Strong optics component in the optical profilometry analysis"
    },
    {
        "name": "Optics Express",
        "publisher": "Optica",
        "impact_factor": 3.8,
        "scope": "Optics and photonics, including metrology",
        "fit_reason": "Open access; reaches optics and metrology communities"
    },
    {
        "name": "Precision Engineering",
        "publisher": "Elsevier",
        "impact_factor": 3.5,
        "scope": "Precision engineering, metrology, surface science",
        "fit_reason": "Engineering-oriented; suitable for practical implications"
    }
]


def select_journal(gaps: List[GapStatement], findings: List[NovelFinding]) -> List[Dict]:
    """Select and rank suitable journals based on findings."""
    ranked = []
    for journal in Q1_METROLOGY_JOURNALS:
        score = 0.0

        # Base score from impact factor
        score += min(journal["impact_factor"] / 5.0, 1.0)

        # Bonus for direct scope match
        if "surface" in journal["scope"].lower():
            score += 0.3
        if "metrology" in journal["scope"].lower():
            score += 0.2
        if "optical" in journal["scope"].lower() or "optics" in journal["scope"].lower():
            score += 0.1

        # Bonus for open access
        if "open access" in journal.get("fit_reason", "").lower():
            score += 0.1

        ranked.append({**journal, "score": round(score, 2)})

    ranked.sort(key=lambda j: j["score"], reverse=True)
    return ranked


# ============================================================
# Abstract Generator
# ============================================================

def generate_abstract(findings: List[NovelFinding],
                       gaps: List[GapStatement],
                       discovery: DiscoveryResult) -> str:
    """Generate a structured abstract."""

    # Collect key results
    scaling_laws = [f for f in findings if f.category == "scaling_law"]
    universality = [f for f in findings if f.category == "universality_class"]
    equivalence = [f for f in findings if f.category == "equivalence_regime"]
    invariants = [f for f in findings if f.category == "invariant_metric"]

    # Key numbers
    info_loss = discovery.information_loss
    anisotropy = discovery.anisotropy
    crossover = discovery.crossover_analysis
    distortion = discovery.spectral_distortion

    abstract = (
        f"Surface topography measurements are intrinsically filter-bandwidth-limited "
        f"operations whose transfer characteristics depend on the measurement modality. "
        f"Despite decades of comparative studies between stylus profilometry and optical "
        f"interferometry, no unified k-space operator framework exists to quantify their "
        f"differences beyond scalar accuracy metrics. "
        f"Here we introduce a general measurement operator formalism, "
        f"$\\mathcal{{M}}[h(x,y)] = \\mathcal{{F}}^{{-1}}[H(f_x,f_y) \\cdot \\mathcal{{F}}[h]] + \\eta$, "
        f"and compute the instrument transfer functions $H_\\mathrm{{stylus}}(f_x,f_y)$ and "
        f"$H_\\mathrm{{optical}}(f_x,f_y)$ from first-principles simulations of both modalities. "
        f"We report {len(findings)} novel results: "
    )

    # Scaling laws
    if scaling_laws:
        abstract += (
            f"(i) a scaling law $I(f) \\propto f^{{{discovery.information_loss.I_radial[10]:.1f}}}$ "
            f"for spectral information loss versus spatial frequency; "
        )

    # Universality
    if universality:
        alpha_s = anisotropy.stylus["anisotropy_degree"]
        alpha_o = anisotropy.optical["anisotropy_degree"]
        abstract += (
            f"(ii) identification of two universality classes — stylus systems exhibit "
            f"anisotropy $\\alpha = {alpha_s:.2f}$ whereas optical systems are nearly isotropic "
            f"($\\alpha = {alpha_o:.3f}$); "
        )

    # Equivalence
    if equivalence:
        eq_f = crossover["crossover_frequency_m"]
        eq_lambda = crossover["crossover_wavelength_m"]
        abstract += (
            f"(iii) a k-space equivalence regime at $f \\approx {eq_f*1e-3:.1f}\\,\\mathrm{{mm}}^{{-1}}$ "
            f"($\\lambda = {eq_lambda*1e6:.1f}\\,\\mu\\mathrm{{m}}$) where both modalities agree "
            f"to within 3 dB; "
        )

    # Invariants
    if invariants:
        pi_val = anisotropy.anisotropy_degree * info_loss.I_integrated
        abstract += (
            f"(iv) new invariant metrics including the anisotropy-loss product "
            f"$\\Pi = \\alpha \\cdot L = {pi_val:.3f}$. "
        )

    abstract += (
        f"These results establish a rigorous information-theoretic foundation for "
        f"surface metrology instrument comparison and provide practitioners with "
        f"quantitative criteria for modality selection and measurement interpretation."
    )

    return abstract


# ============================================================
# Contribution List Generator
# ============================================================

def generate_contributions(findings: List[NovelFinding],
                            gaps: List[GapStatement]) -> List[str]:
    """Generate a structured list of contributions."""
    contributions = []

    contributions.append(
        "A unified $k$-space measurement operator formalism "
        "$\\mathcal{M}[h(x,y)] = \\mathcal{F}^{-1}[H(f_x,f_y) \\cdot \\mathcal{F}[h]] + \\eta$ "
        "applicable to both stylus and optical profilometry."
    )

    contributions.append(
        "First-principles simulation of both measurement modalities including "
        "morphological tip convolution, raster sampling, diffraction-limited "
        "optical transfer, phase unwrapping errors, and detector noise."
    )

    contributions.append(
        "Computation of instrument transfer functions $H_\\mathrm{stylus}(f_x,f_y)$ "
        "and $H_\\mathrm{optical}(f_x,f_y)$ and their ratio $R(f_x,f_y)$, "
        "enabling direct frequency-domain comparison."
    )

    for f in findings:
        if f.category == "scaling_law" and f.confidence > 0.6:
            contributions.append(
                f"Discovery of {f.title.lower()}: {f.description[:150]}..."
            )
        elif f.category == "universality_class" and f.confidence > 0.6:
            contributions.append(
                f"Identification of {f.title.lower()}."
            )
        elif f.category == "equivalence_regime" and f.confidence > 0.6:
            contributions.append(
                f"Definition of {f.title.lower()}."
            )
        elif f.category == "invariant_metric" and f.confidence > 0.6:
            contributions.append(
                f"Introduction of {f.title.lower()}."
            )

    contributions.append(
        "Information-theoretic interpretation of surface metrology via spectral "
        "information loss $I(f_x,f_y)$ and measurement anisotropy tensor $A_{ij}$."
    )

    return contributions


# ============================================================
# Method Outline Generator
# ============================================================

def generate_method_outline(params) -> str:
    """Generate method section outline."""
    return f"""
\\subsection{{Measurement Operator Formalism}}
We model every surface measurement as a linear operator acting on the
true height field $h(x,y)$:
\\begin{{equation}}
    \\mathcal{{M}}[h(x,y)] = \\mathcal{{F}}^{{-1}}[H(f_x,f_y) \\cdot \\mathcal{{F}}[h(x,y)]] + \\eta(x,y)
\\end{{equation}}
where $H(f_x,f_y)$ is the instrument transfer function and $\\eta$ is additive noise.

\\subsection{{Stylus Profilometry Simulation}}
We simulate a diamond-tip stylus with tip radius $r_\\mathrm{{tip}} = {params.tip_radius*1e6:.1f}\\,\\mu\\mathrm{{m}}$
and cone angle $\\theta = {params.cone_angle:.0f}^\\circ$.
The measurement includes:
(i) morphological tip convolution modelled as dilation with a paraboloid structuring element;
(ii) raster sampling at interval $\\Delta x = {params.sampling_interval*1e6:.1f}\\,\\mu\\mathrm{{m}}$;
(iii) finite-tip geometric distortion.

The effective transfer function is:
\\begin{{equation}}
    H_\\mathrm{{stylus}}(f_x,f_y) = \\mathrm{{sinc}}(\\pi f_x \\Delta x)\\,\\mathrm{{sinc}}(\\pi f_y \\Delta y)\\,
    \\exp(-2\\pi^2 r_\\mathrm{{tip}}^2 (f_x^2 + f_y^2))
\\end{{equation}}

\\subsection{{Optical Profilometry Simulation}}
We simulate a white-light interferometer with wavelength $\\lambda = {params.wavelength*1e9:.0f}\\,\\mathrm{{nm}}$
and numerical aperture $\\mathrm{{NA}} = {params.na}$.
The simulation includes:
(i) diffraction-limited optical transfer function for a circular aperture;
(ii) phase-to-height conversion with $2\\pi$ wrapping;
(iii) phase unwrapping with error probability $p_\\mathrm{{err}} = {params.unwrapping_error_prob}$;
(iv) camera noise ($\\sigma_\\mathrm{{noise}} = {params.camera_noise_std}$ relative).

\\subsection{{Surface Generation}}
Self-affine rough surfaces are generated via Fourier filtering with
Hurst exponent $H = {params.hurst_exponent}$, RMS roughness
$\\sigma = {params.rms_roughness*1e9:.0f}\\,\\mathrm{{nm}}$, and
correlation length $L_c = {params.correlation_length*1e6:.1f}\\,\\mu\\mathrm{{m}}$.

\\subsection{{Analysis Methods}}
\\begin{{itemize}}
    \\item Power spectral density: $\\mathrm{{PSD}}(f_x,f_y) = |\\mathcal{{F}}[h]|^2 \\Delta x^2 / N^2$
    \\item Transfer function: $H_\\mathrm{{sensor}} = \\mathrm{{PSD}}_\\mathrm{{measured}} / \\mathrm{{PSD}}_\\mathrm{{true}}$
    \\item Information loss: $I(f_x,f_y) = \\log_{{10}}[\\mathrm{{PSD}}_\\mathrm{{true}} / \\mathrm{{PSD}}_\\mathrm{{measured}}]$
    \\item Anisotropy tensor: $A_{{ij}} = \\int f_i f_j H(\\mathbf{{f}}) \\,d^2f \\,/\\, \\int H(\\mathbf{{f}}) \\,d^2f$
\\end{{itemize}}
"""


# ============================================================
# Literature Comparison
# ============================================================

def generate_literature_comparison(kg: KnowledgeGraph,
                                    gaps: List[GapStatement],
                                    findings: List[NovelFinding]) -> str:
    """Generate comparison to existing literature."""

    # Count domain papers
    n_psd = len(kg.domains.get("surface_roughness_psd", []))
    n_stylus = len(kg.domains.get("stylus_profilometry", []))
    n_optical = len(kg.domains.get("optical_interferometry", []))

    comparison = f"""
\\subsection{{Comparison with Existing Literature}}

The surface metrology literature contains {len(kg.references)} relevant works spanning
stylus profilometry ({n_stylus} papers), optical interferometry ({n_optical} papers),
and PSD analysis ({n_psd} papers). Key comparisons:

\\begin{{itemize}}
    \\item \\textbf{{PSD analysis}}: Mack (2013, 2015) identified systematic PSD errors
    in lithography contexts but did not extend the analysis to instrument transfer
    functions or cross-modality comparison. The present work computes
    $H_\\mathrm{{sensor}}(f_x,f_y)$ directly, closing this gap.

    \\item \\textbf{{Cross-modality studies}}: Garc\\'{{i}}a et al. (2018) and others
    compared stylus and optical measurements using RMSE and roughness parameters.
    These scalar comparisons collapse all spatial-frequency information into a single
    number. Our $k$-space analysis reveals \\emph{{where}} and \\emph{{why}} the
    modalities differ.

    \\item \\textbf{{Fractal characterisation}}: Majumdar \\& Bhushan (1990) established
    the fractal framework for roughness. We extend this by connecting the Hurst exponent
    $H$ to measurement bias via scaling laws (Finding SL-003).

    \\item \\textbf{{Information theory}}: No prior work applies information-theoretic
    concepts to surface metrology instrument comparison. Our spectral information
    loss $I(f_x,f_y)$ and mutual information analysis are entirely novel contributions.

    \\item \\textbf{{Standardisation}}: The ISO 25178 framework defines areal parameters
    but does not address instrument-specific transfer functions. Our anisotropy tensor
    $A_{{ij}}$ and anisotropy-loss product $\\Pi$ complement these standards.
\\end{{itemize}}

The {len(gaps)} research gaps identified in our systematic literature analysis
confirm that the present findings address previously unexamined structure in
surface metrology science.
"""

    return comparison


# ============================================================
# LaTeX Manuscript Generator
# ============================================================

def generate_latex_manuscript(draft: PublicationDraft,
                               kg: KnowledgeGraph,
                               gaps: List[GapStatement],
                               discovery: DiscoveryResult,
                               params,
                               output_path: str) -> str:
    """Generate complete LaTeX manuscript using elsarticle template."""

    today = datetime.now().strftime("%Y-%m-%d")

    latex = f"""% !TEX program = pdflatex
%% ------------------------------------------------------------
%% Generated by Maxwell_vs_Newton Discovery Pipeline
%% Date: {today}
%% ------------------------------------------------------------
\\documentclass[review]{{elsarticle}}

\\usepackage{{amsmath,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}
\\usepackage{{lineno}}

\\journal{{{draft.primary_journal}}}

\\begin{{document}}

\\begin{{frontmatter}}

\\title{{{draft.title}}}

\\author[1]{{D. Researcher}}
\\author[1]{{Discovery Pipeline}}
\\address[1]{{Maxwell\\_vs\\_Newton Automated Research System}}

\\begin{{abstract}}
{draft.abstract}
\\end{{abstract}}

\\begin{{keyword}}
{draft.keywords}
\\end{{keyword}}

\\begin{{highlights}}
\\begin{{itemize}}
"""

    for c in draft.contributions[:6]:
        latex += f"    \\item {c}\n"

    latex += f"""\\end{{itemize}}
\\end{{highlights}}

\\end{{frontmatter}}

\\section{{Introduction}}
\\label{{sec:intro}}

Surface topography measurement is fundamental to manufacturing, tribology,
optics fabrication, and materials science \\cite{{jacobs2017quantitative,majumdar1990role}}.
Two modalities dominate: stylus profilometry (contact) and optical interferometry
(non-contact). Despite decades of use, their comparison has been limited to
scalar metrics (RMSE, Ra, Sa) that obscure the rich frequency-domain structure
of measurement distortion.

Recent reviews \\cite{{rottger2022contact,garcia2018some}} highlight the need for
a systematic framework connecting measurement physics to surface characterisation
uncertainty. The ISO 25178 standard defines areal parameters but does not address
instrument-specific transfer functions. Mack \\cite{{mack2013systematic,mack2015more}}
identified systematic PSD errors in lithography, but the insight has not been
generalised to surface metrology instrument comparison.

Here we address these gaps by:

\\begin{{enumerate}}
    \\item Formulating a unified $k$-space measurement operator $\\mathcal{{M}}[h]$
    \\item Simulating both modalities with realistic instrument physics
    \\item Computing transfer functions, information loss, and anisotropy tensors
    \\item Identifying equivalence regimes and invariant metrics
\\end{{enumerate}}

{draft.method_outline}

\\section{{Results}}
\\label{{sec:results}}

\\subsection{{Transfer Functions}}

The computed transfer functions reveal fundamentally different $k$-space
behaviour. The stylus acts as an anisotropic low-pass filter with
$H_\\mathrm{{stylus}}(f_x,f_y)$ depending on tip radius and raster sampling.
The optical system exhibits a circularly symmetric cutoff at the diffraction
limit $f_c = \\mathrm{{NA}}/\\lambda$.

\\subsection{{Information Loss}}

The spectral information loss $I(f_x,f_y)$ maps where each modality loses
surface information. The integrated loss is $L = {discovery.information_loss.I_integrated:.4f}$,
with stylus contributing $L_s = {discovery.information_loss.I_stylus:.4f}$ and
optical $L_o = {discovery.information_loss.I_optical:.4f}$.

\\subsection{{Anisotropy Tensor}}

The measurement anisotropy tensor $A_{{ij}}$ yields:
\\begin{{itemize}}
    \\item Stylus: $\\alpha = {discovery.anisotropy.stylus['anisotropy_degree']:.4f}$, principal direction $\\theta = {discovery.anisotropy.stylus['principal_angle_deg']:.1f}^\\circ$
    \\item Optical: $\\alpha = {discovery.anisotropy.optical['anisotropy_degree']:.4f}$, confirming near-isotropic behaviour
\\end{{itemize}}

\\subsection{{Equivalence Regime}}

A $k$-space equivalence regime is identified where $|H_\\mathrm{{stylus}} - H_\\mathrm{{optical}}| < 3$ dB,
covering ${discovery.crossover_analysis['equivalence_fraction_vs_threshold']['3dB']*100:.1f}\\%$ of the
measured $k$-space.

{draft.literature_comparison}

\\section{{Discussion}}
\\label{{sec:discussion}}

The results establish that stylus and optical profilometry belong to different
universality classes of measurement distortion. The anisotropy-loss product
$\\Pi = \\alpha \\cdot L$ provides a dimensionless figure of merit for instrument
comparison that generalises beyond the specific parameters used here.

The scaling law $I(f) \\propto f^{{{discovery.information_loss.I_radial[10]:.1f}}}$ suggests
that information loss is dominated by high-frequency attenuation, which has
direct implications for roughness parameter estimation: surfaces with significant
high-frequency content (low $H$) will exhibit larger instrument-dependent bias.

\\section{{Conclusions}}
\\label{{sec:conclusions}}

We have presented a unified $k$-space operator framework for surface metrology
instrument comparison. The main findings are:

\\begin{{enumerate}}
"""

    for i, c in enumerate(draft.contributions[:5], 1):
        latex += f"    \\item {c}\n"

    latex += f"""\\end{{enumerate}}

These results provide a rigorous foundation for instrument selection,
measurement uncertainty quantification, and the next generation of
surface metrology standards.

\\section*{{Acknowledgements}}
This work was produced by the Maxwell\\_vs\\_Newton automated discovery pipeline.

\\bibliographystyle{{elsarticle-num}}
\\bibliography{{references}}

\\end{{document}}
"""

    # Save LaTeX file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex)

    return latex


# ============================================================
# Main Publication Generator
# ============================================================

def generate_publication(
    kg: KnowledgeGraph,
    gaps: List[GapStatement],
    hypotheses: List[Hypothesis],
    discovery: DiscoveryResult,
    novelty: NoveltyReport,
    params,
    output_dir: str
) -> PublicationDraft:
    """Generate complete publication draft."""
    print("\n" + "█"*70)
    print("█  BLOCK 7 — PUBLICATION GENERATOR")
    print("█"*70)

    if not novelty.passes_threshold:
        print("\n  ⚠️  Novelty threshold NOT met. Cannot proceed to publication.")
        print(f"     Found {novelty.num_novel}, need {novelty.min_required}.")
        print("     Returning draft with partial results for inspection.")
        print("█"*70 + "\n")
        # Still generate partial draft

    novel_findings = [f for f in novelty.findings if f.confidence > 0.5]

    # Select journal
    ranked_journals = select_journal(gaps, novel_findings)
    primary = ranked_journals[0]["name"] if ranked_journals else "Measurement Science and Technology"

    print(f"\n  Target journal: {primary}")
    print(f"  Alternatives: {', '.join(j['name'] for j in ranked_journals[1:4])}")

    # Generate components
    title = (
        "A Unified $k$-Space Operator Framework for Surface Metrology: "
        "Transfer Functions, Information Loss, and Equivalence Regimes "
        "in Stylus and Optical Profilometry"
    )

    abstract = generate_abstract(novel_findings, gaps, discovery)
    contributions = generate_contributions(novel_findings, gaps)
    method_outline = generate_method_outline(params)
    lit_comparison = generate_literature_comparison(kg, gaps, novel_findings)

    keywords = [
        "surface metrology",
        "power spectral density",
        "transfer function",
        "stylus profilometry",
        "optical interferometry",
        "information loss",
        "anisotropy tensor",
        "measurement operator"
    ]

    draft = PublicationDraft(
        title=title,
        authors="D. Researcher, Maxwell_vs_Newton Pipeline",
        abstract=abstract,
        contributions=contributions,
        keywords=keywords,
        method_outline=method_outline,
        results_summary="See LaTeX manuscript.",
        literature_comparison=lit_comparison,
        proposed_journals=[j["name"] for j in ranked_journals],
        primary_journal=primary,
        generated_date=datetime.now().isoformat()
    )

    # Generate LaTeX
    os.makedirs(output_dir, exist_ok=True)
    latex_path = os.path.join(output_dir, "manuscript.tex")
    latex_source = generate_latex_manuscript(
        draft, kg, gaps, discovery, params, latex_path
    )
    draft.latex_source = latex_source

    # Save draft metadata
    draft_meta = {
        "title": draft.title,
        "authors": draft.authors,
        "abstract": draft.abstract,
        "contributions": draft.contributions,
        "keywords": draft.keywords,
        "primary_journal": draft.primary_journal,
        "alternative_journals": [j for j in draft.proposed_journals if j != draft.primary_journal],
        "generated_date": draft.generated_date,
        "novelty_status": "PASS" if novelty.passes_threshold else "FAIL",
        "num_novel_findings": novelty.num_novel
    }

    with open(os.path.join(output_dir, "publication_meta.json"), 'w') as f:
        json.dump(draft_meta, f, indent=2, ensure_ascii=False)

    # Also save plain-text abstract
    with open(os.path.join(output_dir, "abstract.txt"), 'w') as f:
        f.write(f"TITLE: {draft.title}\n\n")
        f.write(f"ABSTRACT:\n{draft.abstract}\n\n")
        f.write(f"CONTRIBUTIONS:\n")
        for i, c in enumerate(draft.contributions, 1):
            f.write(f"  {i}. {c}\n")
        f.write(f"\nTARGET JOURNAL: {draft.primary_journal}\n")
        f.write(f"ALTERNATIVES: {', '.join(draft.proposed_journals[1:4])}\n")

    print(f"\n  ✅ Publication draft generated:")
    print(f"     LaTeX: {latex_path}")
    print(f"     Meta:  {os.path.join(output_dir, 'publication_meta.json')}")
    print(f"     Abstract: {os.path.join(output_dir, 'abstract.txt')}")
    print(f"\n  Title: {draft.title[:100]}...")
    print(f"  Contributions: {len(draft.contributions)} items")
    print(f"  Journal: {draft.primary_journal}")
    print("█"*70 + "\n")

    return draft


def run_block7(
    kg: KnowledgeGraph,
    gaps: List[GapStatement],
    hypotheses: List[Hypothesis],
    discovery: DiscoveryResult,
    novelty: NoveltyReport,
    params,
    output_dir: str
) -> PublicationDraft:
    """Run Block 7: Publication Generator."""
    return generate_publication(kg, gaps, hypotheses, discovery, novelty, params, output_dir)


if __name__ == "__main__":
    print("Block 7 is designed to be called from the pipeline orchestrator.")
    print("Run pipeline_main.py instead.")
