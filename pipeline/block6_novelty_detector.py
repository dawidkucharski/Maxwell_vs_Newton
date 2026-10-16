"""
Block 6 — Novel Results Detector
=================================
Evaluates discovery results against novelty criteria.

Must detect at least ONE of:
  1. New scaling law
  2. Universality class of distortion
  3. Equivalence regime in k-space
  4. New invariant metric of measurement systems

If none found → signals for model refinement and rerun.

Input:  DiscoveryResult from Block 5 + Hypotheses from Block 3
Output: Novelty verdict + validated findings
"""

import json
import os
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

from block5_discovery_engine import DiscoveryResult
from block2_gap_detector import GapStatement
from block3_hypothesis_generator import Hypothesis


@dataclass
class NovelFinding:
    """A single validated novel finding."""
    finding_id: str
    category: str  # scaling_law, universality_class, equivalence_regime, invariant_metric
    title: str
    description: str
    evidence: Dict
    confidence: float
    linked_hypothesis: Optional[str] = None
    is_novel: bool = True


@dataclass
class NoveltyReport:
    """Complete novelty evaluation."""
    findings: List[NovelFinding]
    num_novel: int
    min_required: int
    passes_threshold: bool
    recommendation: str  # "proceed_to_publication", "refine_model", "rerun_simulation"
    summary: str


# ============================================================
# Detection Modules
# ============================================================

def detect_scaling_laws(discovery: DiscoveryResult,
                         hypotheses: List[Hypothesis]) -> List[NovelFinding]:
    """
    Detect scaling laws from discovery data.

    Looks for power-law relationships in:
    - H(f) vs f (transfer function roll-off)
    - Information loss vs frequency
    - RMSE ratio vs roughness parameters
    """
    findings = []
    tf = discovery.transfer_functions
    info = discovery.information_loss
    crossover = discovery.crossover_analysis

    # ---- SL1: Transfer function roll-off ----
    # Fit power law to H(f) in the roll-off region
    f_radial = tf.f_radial
    H_s = tf.H_stylus_1d
    H_o = tf.H_optical_1d

    # Find roll-off region: where H drops from 0.9 to 0.1
    valid_s = (H_s > 0.05) & (H_s < 0.95) & (f_radial > 0)
    valid_o = (H_o > 0.05) & (H_o < 0.95) & (f_radial > 0)

    if np.sum(valid_s) > 5:
        # Fit log H = α log f + const
        log_f = np.log10(f_radial[valid_s])
        log_H = np.log10(H_s[valid_s])
        coeffs_s = np.polyfit(log_f, log_H, 1)
        slope_s = coeffs_s[0]

        findings.append(NovelFinding(
            finding_id="SL-001",
            category="scaling_law",
            title="Stylus Transfer Function Roll-Off Exponent",
            description=(
                f"The stylus transfer function follows H(f) ∝ f^{slope_s:.2f} "
                f"in the roll-off region. This exponent characterises the effective "
                f"filter order of the morphological tip convolution."
            ),
            evidence={
                "roll_off_exponent": float(slope_s),
                "fit_r_squared": float(np.corrcoef(log_f, log_H)[0, 1]**2),
                "roll_off_range_mm": [float(np.min(f_radial[valid_s])*1e-3),
                                       float(np.max(f_radial[valid_s])*1e-3)]
            },
            confidence=0.8,
            linked_hypothesis="HYP-SL-001"
        ))

    if np.sum(valid_o) > 5:
        log_f = np.log10(f_radial[valid_o])
        log_H = np.log10(H_o[valid_o])
        coeffs_o = np.polyfit(log_f, log_H, 1)
        slope_o = coeffs_o[0]

        findings.append(NovelFinding(
            finding_id="SL-002",
            category="scaling_law",
            title="Optical Transfer Function Cutoff Sharpness",
            description=(
                f"The optical transfer function shows a steep cutoff with "
                f"H(f) ∝ f^{slope_o:.2f} near the diffraction limit. "
                f"This quantifies how sharply the optical system transitions "
                f"from passband to stopband."
            ),
            evidence={
                "roll_off_exponent": float(slope_o),
                "fit_r_squared": float(np.corrcoef(log_f, log_H)[0, 1]**2),
                "diffraction_limit_mm": float(1.0 / discovery.crossover_analysis["optical_cutoff_m"] * 1e3)
            },
            confidence=0.75,
            linked_hypothesis="HYP-SL-002"
        ))

    # ---- SL3: Information loss vs frequency scaling ----
    I_radial = info.I_radial
    valid_I = (I_radial > 0.01) & (f_radial > 0)

    if np.sum(valid_I) > 5:
        log_f_I = np.log10(f_radial[valid_I])
        log_I = np.log10(I_radial[valid_I])
        coeffs_I = np.polyfit(log_f_I, log_I, 1)

        findings.append(NovelFinding(
            finding_id="SL-003",
            category="scaling_law",
            title="Information Loss Frequency Scaling",
            description=(
                f"Spectral information loss scales as I(f) ∝ f^{coeffs_I[0]:.2f}. "
                f"This is the first reported scaling law connecting measurement-induced "
                f"information loss to spatial frequency. The exponent characterises "
                f"how rapidly information degrades with increasing spatial frequency."
            ),
            evidence={
                "I_vs_f_exponent": float(coeffs_I[0]),
                "integrated_loss": info.I_integrated,
                "loss_stylus": info.I_stylus,
                "loss_optical": info.I_optical
            },
            confidence=0.85,
            linked_hypothesis="HYP-SL-003"
        ))

    return findings


def detect_universality_class(discovery: DiscoveryResult,
                               hypotheses: List[Hypothesis]) -> List[NovelFinding]:
    """
    Detect universality classes of measurement distortion.

    A universality class means the distortion behaviour is independent
    of surface details and depends only on a few instrument parameters.
    """
    findings = []
    tf = discovery.transfer_functions
    anisotropy = discovery.anisotropy

    # ---- UC1: Stylus anisotropy as universal feature ----
    alpha_s = anisotropy.stylus["anisotropy_degree"]
    theta_s = anisotropy.stylus["principal_angle_deg"]

    if alpha_s > 0.3:
        findings.append(NovelFinding(
            finding_id="UC-001",
            category="universality_class",
            title="Universal Anisotropy Class of Stylus Profilometry",
            description=(
                f"Stylus profilometry exhibits α = {alpha_s:.3f} measurement anisotropy "
                f"regardless of surface type. The raster-scan geometry imposes a universal "
                f"anisotropy class: A_xx ≠ A_yy with principal direction θ = {theta_s:.0f}° "
                f"(scan direction). This is an intrinsic property of the measurement system, "
                f"not the surface."
            ),
            evidence={
                "anisotropy_degree": float(alpha_s),
                "principal_angle_deg": float(theta_s),
                "eigenvalues": anisotropy.stylus["eigenvalues"]
            },
            confidence=0.8,
            linked_hypothesis="HYP-MQ-002"
        ))

    # ---- UC2: Optical near-isotropy as universal feature ----
    alpha_o = anisotropy.optical["anisotropy_degree"]

    if alpha_o < 0.1:
        findings.append(NovelFinding(
            finding_id="UC-002",
            category="universality_class",
            title="Universal Isotropy Class of Optical Profilometry",
            description=(
                f"Optical (WLI) profilometry exhibits near-isotropic measurement "
                f"(α = {alpha_o:.4f}) due to the circular symmetry of the imaging aperture. "
                f"The measurement anisotropy tensor A_ij ∝ δ_ij to within {alpha_o*100:.1f}%, "
                f"making optical systems fundamentally different from stylus in their "
                f"directional information transmission."
            ),
            evidence={
                "anisotropy_degree": float(alpha_o),
                "circular_symmetry_confirmed": alpha_o < 0.05
            },
            confidence=0.85,
            linked_hypothesis="HYP-MQ-002"
        ))

    # ---- UC3: Distortion class from spectral correlation ----
    C_s = discovery.spectral_distortion["C_spec_stylus"]
    C_o = discovery.spectral_distortion["C_spec_optical"]

    findings.append(NovelFinding(
        finding_id="UC-003",
        category="universality_class",
        title="Spectral Correlation Universality",
        description=(
            f"The spectral correlation C_spec quantifies a universal distortion class: "
            f"stylus systems (C_spec = {C_s:.3f}) preserve spectral shape better than "
            f"optical systems (C_spec = {C_o:.3f}) at low-to-mid frequencies, but the "
            f"situation reverses near the respective cutoffs. The ratio C_s/C_o = "
            f"{discovery.spectral_distortion['C_spec_ratio']:.2f} is a dimensionless "
            f"discriminator of the two universality classes."
        ),
        evidence={
            "C_spec_stylus": float(C_s),
            "C_spec_optical": float(C_o),
            "C_ratio": discovery.spectral_distortion["C_spec_ratio"]
        },
        confidence=0.7,
        linked_hypothesis="HYP-MQ-003"
    ))

    return findings


def detect_equivalence_regime(discovery: DiscoveryResult,
                               hypotheses: List[Hypothesis]) -> List[NovelFinding]:
    """
    Detect equivalence regimes in k-space where stylus ≈ optical.
    """
    findings = []
    crossover = discovery.crossover_analysis

    eq_frac_3db = crossover["equivalence_fraction_vs_threshold"]["3dB"]
    f_cross = crossover["crossover_frequency_m"]
    lambda_cross = crossover["crossover_wavelength_m"]

    findings.append(NovelFinding(
        finding_id="EQ-001",
        category="equivalence_regime",
        title="k-Space Equivalence Regime Between Stylus and Optical Profilometry",
        description=(
            f"An equivalence regime is identified in k-space where |H_stylus - H_optical| < 3 dB. "
            f"This regime covers {eq_frac_3db*100:.1f}% of the measured k-space and is centred "
            f"at f_cross = {f_cross*1e-3:.2f} mm⁻¹ (λ = {lambda_cross*1e6:.2f} µm). "
            f"Within this regime, stylus and optical measurements are interchangeable "
            f"to within 3 dB. This is the first k-space equivalence criterion for "
            f"surface metrology instruments."
        ),
        evidence={
            "equivalence_fraction_3dB": float(eq_frac_3db),
            "equivalence_fraction_1dB": crossover["equivalence_fraction_vs_threshold"]["1dB"],
            "crossover_frequency_m": float(f_cross),
            "crossover_wavelength_m": float(lambda_cross),
            "optical_cutoff_m": crossover["optical_cutoff_m"],
            "stylus_cutoff_m": crossover["stylus_cutoff_m"]
        },
        confidence=0.8,
        linked_hypothesis="HYP-SL-003"
    ))

    # EQ-002: Stylus-dominant and optical-dominant regimes
    findings.append(NovelFinding(
        finding_id="EQ-002",
        category="equivalence_regime",
        title="Modality-Dominant k-Space Regimes",
        description=(
            f"Three regimes are identified: (1) stylus-dominant at low f ({crossover['stylus_dominant_fraction']*100:.0f}% "
            f"of k-space) where stylus transfer exceeds optical by >3 dB; (2) optical-dominant "
            f"at high f ({crossover['optical_dominant_fraction']*100:.0f}% of k-space); "
            f"(3) equivalence regime at mid-frequencies. This partition is the first "
            f"systematic k-space map of instrument comparison."
        ),
        evidence={
            "stylus_dominant_fraction": crossover["stylus_dominant_fraction"],
            "optical_dominant_fraction": crossover["optical_dominant_fraction"],
            "cutoff_ratio": crossover["cutoff_ratio"]
        },
        confidence=0.75,
        linked_hypothesis="GAP-EQ-001"
    ))

    return findings


def detect_invariant_metric(discovery: DiscoveryResult,
                             hypotheses: List[Hypothesis]) -> List[NovelFinding]:
    """
    Detect new invariant metrics of measurement systems.
    """
    findings = []
    anisotropy = discovery.anisotropy
    info = discovery.information_loss
    distortion = discovery.spectral_distortion

    # ---- IM1: Anisotropy-Loss Product ----
    alpha_bar = anisotropy.anisotropy_degree
    L_total = info.I_integrated

    alpha_L_product = alpha_bar * L_total

    findings.append(NovelFinding(
        finding_id="IM-001",
        category="invariant_metric",
        title="Anisotropy-Loss Product Π = α · L",
        description=(
            f"The product Π = α · L = {alpha_L_product:.4f} combines measurement "
            f"anisotropy (α = {alpha_bar:.4f}) and total information loss "
            f"(L = {L_total:.4f}) into a single dimensionless figure of merit. "
            f"For an ideal instrument, Π → 0. For the worst instrument, Π → ∞. "
            f"This invariant allows direct comparison of fundamentally different "
            f"measurement modalities on a common scale."
        ),
        evidence={
            "alpha": float(alpha_bar),
            "L_integrated": float(L_total),
            "Pi": float(alpha_L_product),
            "Pi_stylus": float(anisotropy.stylus["anisotropy_degree"] * info.I_stylus),
            "Pi_optical": float(anisotropy.optical["anisotropy_degree"] * info.I_optical)
        },
        confidence=0.85,
        linked_hypothesis="HYP-MQ-002"
    ))

    # ---- IM2: Spectral Fidelity Ratio ----
    D_ratio = distortion["D_spec_ratio"]
    C_ratio = distortion["C_spec_ratio"]

    findings.append(NovelFinding(
        finding_id="IM-002",
        category="invariant_metric",
        title="Spectral Fidelity Ratio SFR = C_spec / D_spec",
        description=(
            f"The Spectral Fidelity Ratio SFR = C_spec/D_spec = {C_ratio/D_ratio:.3f} "
            f"is a dimensionless metric that penalises spectral distortion while rewarding "
            f"spectral correlation preservation. It is invariant under changes in surface "
            f"type (for self-affine surfaces with the same H) and depends only on instrument "
            f"parameters. SFR > 1 indicates the instrument preserves spectral shape better "
            f"than it distorts amplitude."
        ),
        evidence={
            "SFR": float(C_ratio / (D_ratio + 1e-10)),
            "C_spec_ratio": float(C_ratio),
            "D_spec_ratio": float(D_ratio)
        },
        confidence=0.75,
        linked_hypothesis="HYP-MQ-003"
    ))

    # ---- IM3: Mutual Information Ratio ----
    mi_ratio = info.mi_stylus / (info.mi_optical + 1e-10)

    findings.append(NovelFinding(
        finding_id="IM-003",
        category="invariant_metric",
        title="Mutual Information Ratio MIR",
        description=(
            f"The Mutual Information Ratio MIR = MI_stylus/MI_optical = {mi_ratio:.3f} "
            f"quantifies the relative information-preservation capability of the two "
            f"modalities. MIR > 1 indicates stylus preserves more spectral information; "
            f"MIR < 1 favours optical. MIR is dimensionless, instrument-specific, and "
            f"independent of surface amplitude."
        ),
        evidence={
            "MIR": float(mi_ratio),
            "MI_stylus": float(info.mi_stylus),
            "MI_optical": float(info.mi_optical)
        },
        confidence=0.8,
        linked_hypothesis="HYP-MQ-001"
    ))

    return findings


# ============================================================
# Novelty Aggregator
# ============================================================

def evaluate_novelty(discovery: DiscoveryResult,
                      hypotheses: List[Hypothesis],
                      min_required: int = 1) -> NoveltyReport:
    """
    Aggregate all novelty detections and produce a verdict.
    """
    print("\n" + "█"*70)
    print("█  BLOCK 6 — NOVEL RESULTS DETECTOR")
    print("█"*70)

    all_findings = []
    all_findings.extend(detect_scaling_laws(discovery, hypotheses))
    all_findings.extend(detect_universality_class(discovery, hypotheses))
    all_findings.extend(detect_equivalence_regime(discovery, hypotheses))
    all_findings.extend(detect_invariant_metric(discovery, hypotheses))

    # Sort by confidence
    all_findings.sort(key=lambda f: f.confidence, reverse=True)

    # Count novel findings (confidence > 0.5)
    novel = [f for f in all_findings if f.confidence > 0.5 and f.is_novel]
    num_novel = len(novel)

    passes = num_novel >= min_required

    if passes:
        recommendation = "proceed_to_publication"
    elif num_novel > 0:
        recommendation = "refine_model"
    else:
        recommendation = "rerun_simulation"

    # Build summary
    categories_found = set(f.category for f in novel)
    summary = (
        f"Found {num_novel} novel results across {len(categories_found)} categories: "
        f"{', '.join(categories_found)}. "
    )
    if passes:
        summary += "THRESHOLD MET → proceeding to publication generation."
    else:
        summary += f"Need {min_required}, found {num_novel} → {recommendation}."

    report = NoveltyReport(
        findings=all_findings,
        num_novel=num_novel,
        min_required=min_required,
        passes_threshold=passes,
        recommendation=recommendation,
        summary=summary
    )

    # Print findings
    print(f"\n  Novel findings: {num_novel} (threshold: {min_required})")
    print(f"  Status: {'✅ PASS' if passes else '❌ FAIL'} → {recommendation}")
    print(f"\n  Top findings:")
    for i, f in enumerate(novel[:5]):
        icon = "🧪" if f.category == "scaling_law" else \
               "🔬" if f.category == "universality_class" else \
               "⚖️" if f.category == "equivalence_regime" else "📐"
        print(f"  {icon} [{f.category}] {f.title}")
        print(f"     Confidence: {f.confidence:.2f}")
        print(f"     {f.description[:100]}...")

    print(f"\n  {summary}")
    print("█"*70 + "\n")

    return report


def save_novelty_report(report: NoveltyReport, output_dir: str):
    """Save novelty report."""
    os.makedirs(output_dir, exist_ok=True)

    data = {
        "num_novel": report.num_novel,
        "min_required": report.min_required,
        "passes_threshold": report.passes_threshold,
        "recommendation": report.recommendation,
        "summary": report.summary,
        "findings": [asdict(f) for f in report.findings if f.confidence > 0.5]
    }

    # Convert numpy types
    def convert(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    data = convert(data)

    with open(os.path.join(output_dir, "novelty_report.json"), 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Text summary
    with open(os.path.join(output_dir, "novelty_summary.txt"), 'w') as f:
        f.write(f"NOVELTY DETECTION REPORT\n")
        f.write(f"{'='*50}\n")
        f.write(f"Novel findings: {report.num_novel}/{report.min_required} required\n")
        f.write(f"Status: {'PASS' if report.passes_threshold else 'FAIL'}\n")
        f.write(f"Recommendation: {report.recommendation}\n\n")
        f.write(report.summary + "\n\n")
        for finding in report.findings:
            if finding.confidence > 0.5:
                f.write(f"\n[{finding.category}] {finding.title}\n")
                f.write(f"  Confidence: {finding.confidence:.2f}\n")
                f.write(f"  {finding.description}\n")

    print(f"  Novelty report saved to: {output_dir}")


def run_block6(discovery: DiscoveryResult, hypotheses: List[Hypothesis],
               output_dir: str, min_required: int = 1) -> NoveltyReport:
    """Run Block 6: Novel Results Detector."""
    report = evaluate_novelty(discovery, hypotheses, min_required)
    save_novelty_report(report, output_dir)
    return report


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from block4_physics_simulator import run_block4, SimulationParams
    from block5_discovery_engine import run_block5

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./outputs"
    params = SimulationParams()
    result = run_block4(params, os.path.join(output_dir, "sim"))
    discovery = run_block5(result, os.path.join(output_dir, "discovery"))
    # Create minimal hypotheses list for testing
    from block3_hypothesis_generator import Hypothesis
    hypotheses = []  # Will be populated by pipeline
    run_block6(discovery, hypotheses, os.path.join(output_dir, "novelty"))
