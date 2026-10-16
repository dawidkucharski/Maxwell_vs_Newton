"""
Block 3 — Hypothesis Generator (Novelty Engine)
=================================================
Generates new scientific hypotheses based on identified research gaps.
Produces three types of output:
  (A) New operator models: M_sensor[h(x,y)]
  (B) New measurable quantities: information loss field, anisotropy tensor, etc.
  (C) New scaling laws: tip radius vs cutoff, NA vs fidelity, etc.

Input:  Knowledge graph + Gap statements
Output: Structured hypotheses with mathematical formulation
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from block2_gap_detector import GapStatement
from block1_literature_mining import KnowledgeGraph


@dataclass
class Hypothesis:
    """A single generated hypothesis."""
    hyp_id: str
    category: str  # new_operator_model, new_measurable_quantity, new_scaling_law
    title: str
    mathematical_formulation: str
    physical_interpretation: str
    testable_prediction: str
    linked_gaps: List[str] = field(default_factory=list)
    novelty_score: float = 0.0
    feasibility: str = "medium"  # high, medium, low


# ============================================================
# (A) New Operator Models
# ============================================================

def generate_operator_hypotheses(kg: KnowledgeGraph, gaps: List[GapStatement]) -> List[Hypothesis]:
    """Generate novel operator model hypotheses."""
    hypotheses = []

    # H1: Unified k-space measurement operator
    hypotheses.append(Hypothesis(
        hyp_id="HYP-OP-001",
        category="new_operator_model",
        title="Unified k-Space Measurement Operator for Surface Profilometry",
        mathematical_formulation=(
            "M[h(x,y)] = F^{-1}[ H(f_x, f_y) · F[h(x,y)] ] + η(x,y)\n\n"
            "where H(f_x, f_y) = H_aperture(f_x, f_y) · H_sampling(f_x, f_y) · H_noise(f_x, f_y)\n\n"
            "For stylus: H_s(f_x, f_y) = sinc(π f_x Δx) · sinc(π f_y Δy) · exp(-2π²σ_tip²(f_x² + f_y²))\n"
            "For optical: H_o(f_x, f_y) = circ(√(f_x²+f_y²) · λ/NA) · exp(-σ_phase²(f_x, f_y))\n\n"
            "Ratio operator: R(f_x, f_y) = H_o(f_x, f_y) / H_s(f_x, f_y)"
        ),
        physical_interpretation=(
            "Every surface measurement can be represented as a linear operator acting on "
            "the true height field h(x,y), followed by additive noise η. The transfer function "
            "H(f_x, f_y) encapsulates the instrument's k-space filtering. The stylus acts as a "
            "low-pass filter with tip-radius-dependent Gaussian roll-off plus raster sampling "
            "sinc modulation. The optical system has a hard circular cutoff at the diffraction "
            "limit plus phase-noise-dependent degradation."
        ),
        testable_prediction=(
            "For surfaces with roughness below the optical diffraction limit but above the "
            "stylus tip-radius cutoff, the ratio R(f_x, f_y) should show a cross-over region "
            "where R ≈ 1 (equivalence regime), flanked by regions where one modality dominates."
        ),
        linked_gaps=["GAP-OP-001", "GAP-FD-001"],
        novelty_score=0.85,
        feasibility="high"
    ))

    # H2: Morphological convolution operator with tip geometry
    hypotheses.append(Hypothesis(
        hyp_id="HYP-OP-002",
        category="new_operator_model",
        title="Morphological Convolution Operator with Finite Tip Geometry",
        mathematical_formulation=(
            "M_stylus[h(x,y)] = min_{(u,v)∈Ω_tip}[ h(x+u, y+v) + t(u,v) ]\n\n"
            "where t(u,v) is the tip shape function (paraboloid approximation):\n"
            "  t(u,v) = (u² + v²) / (2 · r_tip)  for √(u²+v²) ≤ r_tip · tan(θ_cone/2)\n\n"
            "In frequency domain (small-roughness limit):\n"
            "  H_tip(f) ≈ exp[ -2π² r_tip h''_rms f² ]\n"
            "  where h''_rms is the RMS surface curvature."
        ),
        physical_interpretation=(
            "The stylus does not perform a simple linear convolution — it performs morphological "
            "dilation. The measured profile is the envelope of the tip as it slides over the surface. "
            "This is fundamentally nonlinear. However, in the small-roughness limit where the tip "
            "radius is much larger than asperity curvature, it reduces to a linear Gaussian filter "
            "whose width depends on both tip radius AND surface curvature."
        ),
        testable_prediction=(
            "The effective cutoff frequency f_c ∝ 1/√(r_tip · h''_rms). For surfaces with "
            "different curvature but identical r_tip, the measured PSD will differ at high "
            "frequencies even with the same instrument."
        ),
        linked_gaps=["GAP-OP-001", "GAP-FD-001"],
        novelty_score=0.75,
        feasibility="high"
    ))

    return hypotheses


# ============================================================
# (B) New Measurable Quantities
# ============================================================

def generate_measurable_quantity_hypotheses(kg: KnowledgeGraph, gaps: List[GapStatement]) -> List[Hypothesis]:
    """Generate novel measurable quantity hypotheses."""
    hypotheses = []

    # H3: Information loss field
    hypotheses.append(Hypothesis(
        hyp_id="HYP-MQ-001",
        category="new_measurable_quantity",
        title="Spectral Information Loss Field I(f_x, f_y)",
        mathematical_formulation=(
            "I(f_x, f_y) = log₁₀[ PSD_true(f_x, f_y) / PSD_measured(f_x, f_y) ]\n\n"
            "Integrated information loss: L = ∫∫ I(f_x, f_y) df_x df_y\n\n"
            "Per-band information loss: L_band = ∫_{band} I(f_x, f_y) df_x df_y\n\n"
            "Properties:\n"
            "  • I(f_x, f_y) ≥ 0 (measurement never adds information)\n"
            "  • I(f_x, f_y) = 0 in the passband\n"
            "  • I(f_x, f_y) → ∞ at the instrument cutoff\n"
            "  • I conveys more than RMSE: two systems with identical RMSE can have "
            "different I(f_x, f_y) distributions"
        ),
        physical_interpretation=(
            "I(f_x, f_y) is a 2D map showing where in k-space each instrument loses information "
            "about the true surface. This is fundamentally different from RMSE, which collapses "
            "all spatial-frequency information into a single scalar. I(f_x, f_y) reveals anisotropic "
            "loss patterns — e.g. stylus loses more along the scan direction due to tip convolution, "
            "while optical loses isotropically at the diffraction limit."
        ),
        testable_prediction=(
            "For a known test surface (e.g. sinusoidal grating), I(f_x, f_y) can be measured "
            "directly and compared to the theoretical H_sensor(f_x, f_y). The integrated loss L "
            "should scale with r_tip/λ_dominant for stylus and λ_dominant·NA/λ for optical."
        ),
        linked_gaps=["GAP-IT-001", "GAP-FD-001"],
        novelty_score=0.9,
        feasibility="high"
    ))

    # H4: Anisotropy tensor of measurement
    hypotheses.append(Hypothesis(
        hyp_id="HYP-MQ-002",
        category="new_measurable_quantity",
        title="Measurement Anisotropy Tensor A_ij",
        mathematical_formulation=(
            "A_ij = ∫∫ f_i f_j · H_sensor(f_x, f_y) · df_x df_y  /  ∫∫ H_sensor(f_x, f_y) df_x df_y\n\n"
            "where f_1 = f_x, f_2 = f_y\n\n"
            "Eigendecomposition: A = λ_1 ê_1 ê_1^T + λ_2 ê_2 ê_2^T\n\n"
            "Anisotropy degree: α = |λ_1 - λ_2| / (λ_1 + λ_2)\n"
            "Anisotropy direction: θ_A = arctan(ê_1,y / ê_1,x)\n\n"
            "For perfect isotropic sensor: A_ij ∝ δ_ij, α = 0\n"
            "For stylus (raster along x): A_xx > A_yy, α > 0, θ_A ≈ 0° or 90°\n"
            "For optical (circular aperture): A_ij ≈ A_0 δ_ij, α ≈ 0"
        ),
        physical_interpretation=(
            "The anisotropy tensor A_ij quantifies the directional dependence of measurement "
            "fidelity. Its eigenvalues λ_1, λ_2 give the principal bandwidths, and its "
            "eigenvectors ê_1, ê_2 give the directions of maximum and minimum information "
            "transmission. α = 0 means isotropic measurement; α = 1 means purely 1D measurement "
            "(e.g. single profilometer trace). This provides a rigorous, coordinate-invariant "
            "characterisation of measurement anisotropy."
        ),
        testable_prediction=(
            "For a stylus instrument scanning along x: α_stylus > 0.5 (highly anisotropic). "
            "For a WLI with NA=0.55: α_optical < 0.05 (nearly isotropic). "
            "The product α · L (anisotropy × loss) is a dimensionless figure of merit."
        ),
        linked_gaps=["GAP-AN-001", "GAP-IT-001"],
        novelty_score=0.9,
        feasibility="high"
    ))

    # H5: Spectral distortion metric
    hypotheses.append(Hypothesis(
        hyp_id="HYP-MQ-003",
        category="new_measurable_quantity",
        title="Spectral Distortion Metric D_spec",
        mathematical_formulation=(
            "D_spec = [ ∫∫ |H_true(f) - H_measured(f)|² df / ∫∫ |H_true(f)|² df ]^(1/2)\n\n"
            "Alternatively, the Wasserstein distance between normalised PSDs:\n"
            "D_W = W₂( PSD_measured/||PSD_measured||₁ , PSD_true/||PSD_true||₁ )\n\n"
            "Normalised spectral correlation:\n"
            "C_spec = ∫∫ PSD_true(f) · PSD_measured(f) df / "
            "[√(∫∫ PSD_true² df) · √(∫∫ PSD_measured² df)]"
        ),
        physical_interpretation=(
            "D_spec quantifies how much the measurement system distorts the surface's power "
            "spectrum. Unlike RMSE (spatial-domain scalar), D_spec distinguishes between "
            "different types of distortion: low-pass filtering, anisotropic attenuation, "
            "and phase errors all produce distinct signatures in D_spec. C_spec measures "
            "spectral correlation — how well the measured PSD preserves the shape of the true PSD, "
            "even if amplitudes differ."
        ),
        testable_prediction=(
            "D_spec(stylus) and D_spec(optical) will cross at a characteristic spatial frequency "
            "f_cross that depends on r_tip, NA, and surface roughness exponent H. "
            "C_spec → 0 as either r_tip → ∞ or NA → 0."
        ),
        linked_gaps=["GAP-FD-001", "GAP-OP-001"],
        novelty_score=0.8,
        feasibility="high"
    ))

    return hypotheses


# ============================================================
# (C) New Scaling Laws
# ============================================================

def generate_scaling_law_hypotheses(kg: KnowledgeGraph, gaps: List[GapStatement]) -> List[Hypothesis]:
    """Generate novel scaling law hypotheses."""
    hypotheses = []

    # H6: Tip radius vs cutoff frequency
    hypotheses.append(Hypothesis(
        hyp_id="HYP-SL-001",
        category="new_scaling_law",
        title="Tip-Radius Cutoff Scaling Law",
        mathematical_formulation=(
            "f_c(r_tip, H, σ) = C · r_tip^(-β) · σ^(γ) · L_c^(H-1)\n\n"
            "where:\n"
            "  f_c = effective cutoff spatial frequency\n"
            "  r_tip = stylus tip radius\n"
            "  H = surface Hurst exponent\n"
            "  σ = RMS roughness\n"
            "  L_c = correlation length\n"
            "  β ≈ 0.5 (theoretical: f_c ∝ 1/√r_tip for Gaussian tip approximation)\n"
            "  γ = H - 1 (roughness-dependent correction)\n\n"
            "In dimensionless form: f_c* = C · (L_c/r_tip)^β · (σ/L_c)^γ"
        ),
        physical_interpretation=(
            "The effective spatial-frequency cutoff of a stylus instrument scales as "
            "f_c ∝ r_tip^(-1/2), not r_tip^(-1) as naive intuition suggests. This is because "
            "the tip acts as a morphological filter whose width in k-space is set by the "
            "tip's radius of curvature convolved with the surface's curvature distribution. "
            "The Hurst exponent H enters because smoother surfaces (higher H) have less "
            "high-curvature asperities, effectively increasing the cutoff for a given tip radius."
        ),
        testable_prediction=(
            "For a self-affine surface with H = 0.7: plotting log(f_c) vs log(r_tip) should "
            "yield slope β ≈ 0.5. For H = 0.3 (rougher), β should be larger (~0.6-0.7) due "
            "to increased tip-surface interaction at small scales."
        ),
        linked_gaps=["GAP-OP-001", "GAP-FD-001"],
        novelty_score=0.85,
        feasibility="high"
    ))

    # H7: NA vs reconstruction fidelity
    hypotheses.append(Hypothesis(
        hyp_id="HYP-SL-002",
        category="new_scaling_law",
        title="NA–Fidelity Scaling Law for Optical Profilometry",
        mathematical_formulation=(
            "F(NA, λ, σ) = 1 - exp[ -(NA/NA_crit)^α ]\n\n"
            "where:\n"
            "  F = reconstruction fidelity (0 ≤ F ≤ 1)\n"
            "  NA_crit = λ / (2 · σ · √(log(SNR)))\n"
            "  α ≈ 2 (Gaussian optics limit)\n\n"
            "Equivalently: SNR_effective = SNR_0 · (NA · σ / λ)^2\n\n"
            "Fidelity-bandwidth product: Π = F · BW_effective"
        ),
        physical_interpretation=(
            "Optical profilometry reconstruction fidelity F does not degrade gradually with "
            "decreasing NA — it follows a threshold behaviour. Below NA_crit, phase information "
            "is lost catastrophically due to the inability to resolve surface slopes. The "
            "critical NA depends on both roughness amplitude σ and wavelength λ. For typical "
            "engineering surfaces (σ ~ 50 nm, λ = 550 nm), NA_crit ≈ 0.05, meaning most "
            "commercial WLI systems (NA ≈ 0.3-0.55) operate well above threshold."
        ),
        testable_prediction=(
            "For σ = 50 nm, λ = 550 nm: F(NA) should show a sharp transition near NA ≈ 0.05-0.1. "
            "Below this, unwrapping errors proliferate and F → 0 rapidly."
        ),
        linked_gaps=["GAP-FD-001", "GAP-EQ-001"],
        novelty_score=0.75,
        feasibility="medium"
    ))

    # H8: Roughness exponent vs measurement bias scaling
    hypotheses.append(Hypothesis(
        hyp_id="HYP-SL-003",
        category="new_scaling_law",
        title="Roughness Exponent H vs Measurement Bias Scaling",
        mathematical_formulation=(
            "Bias(H; instrument) = B_0 · (f_inst / f_ref)^(2H-2)\n\n"
            "where:\n"
            "  Bias = (σ_measured² - σ_true²) / σ_true²\n"
            "  f_inst = instrument cutoff frequency\n"
            "  f_ref = reference high-frequency limit\n\n"
            "For stylus: Bias_s ∝ r_tip^(1-H) · σ^(H-1)\n"
            "For optical: Bias_o ∝ (λ/NA)^(2-2H) · σ^(2H-1)\n\n"
            "Crossover condition (Bias_s = Bias_o):\n"
            "  r_tip / (λ/NA) = (λ/NA / σ)^((1-2H)/(1-H))"
        ),
        physical_interpretation=(
            "The bias in measured roughness depends critically on the surface's Hurst exponent H. "
            "For smooth surfaces (H → 1), both instruments approach the true roughness. For rough "
            "surfaces (H → 0), the bias becomes severe and instrument-dependent. This provides a "
            "rigorous criterion for when stylus and optical measurements can be compared: they "
            "agree only when both resolve all roughness scales, which requires f_inst ≫ 1/L_c."
        ),
        testable_prediction=(
            "For H = 0.3 (fractal-like rough surface): Bias_s and Bias_o can differ by > 50% "
            "even when both instruments are 'well-calibrated'. For H = 0.9 (smooth): bias is "
            "negligible (< 5%) for both. This is testable on calibration gratings with known H."
        ),
        linked_gaps=["GAP-EQ-001", "GAP-OP-001", "GAP-FD-001"],
        novelty_score=0.9,
        feasibility="high"
    ))

    return hypotheses


# ============================================================
# Hypothesis Evaluator
# ============================================================
def evaluate_hypotheses(hypotheses: List[Hypothesis], kg: KnowledgeGraph) -> List[Hypothesis]:
    """Score and rank hypotheses by novelty, feasibility, and gap coverage."""
    for hyp in hypotheses:
        # Base novelty from the hypothesis itself
        base_score = hyp.novelty_score

        # Bonus for linking to critical gaps
        critical_links = sum(1 for gid in hyp.linked_gaps if "critical" in str(gid))
        base_score += 0.05 * critical_links

        # Bonus for multiple gap links
        base_score += 0.02 * (len(hyp.linked_gaps) - 1)

        # Cap at 1.0
        hyp.novelty_score = min(base_score, 1.0)

    return sorted(hypotheses, key=lambda h: h.novelty_score, reverse=True)


def print_hypotheses_summary(hypotheses: List[Hypothesis]):
    """Print concise hypothesis summary."""
    print("\n" + "█"*70)
    print("█  BLOCK 3 — HYPOTHESIS GENERATOR (NOVELTY ENGINE)")
    print("█"*70)

    by_category = {}
    for hyp in hypotheses:
        cat = hyp.category.replace("new_", "").replace("_", " ").title()
        by_category.setdefault(cat, []).append(hyp)

    for cat, hyps in by_category.items():
        print(f"\n  --- {cat} ---")
        for hyp in hyps:
            print(f"\n  💡 {hyp.hyp_id}: {hyp.title}")
            print(f"     Novelty: {hyp.novelty_score:.2f} | Feasibility: {hyp.feasibility}")
            print(f"     Linked gaps: {', '.join(hyp.linked_gaps)}")
            print(f"     Prediction: {hyp.testable_prediction[:120]}...")

    print(f"\n  Total hypotheses: {len(hypotheses)}")
    print("█"*70 + "\n")


def export_hypotheses(hypotheses: List[Hypothesis], output_path: str):
    """Export hypotheses to JSON."""
    data = [asdict(h) for h in hypotheses]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Block 3] Hypotheses exported to: {output_path}")


# ============================================================
# Main
# ============================================================
def run_block3(kg: KnowledgeGraph, gaps: List[GapStatement], output_dir: str) -> List[Hypothesis]:
    """Run Block 3: Hypothesis Generation."""
    print("\n" + "█"*70)
    print("█  BLOCK 3 — HYPOTHESIS GENERATOR")
    print("█"*70)

    all_hypotheses = []
    all_hypotheses.extend(generate_operator_hypotheses(kg, gaps))
    all_hypotheses.extend(generate_measurable_quantity_hypotheses(kg, gaps))
    all_hypotheses.extend(generate_scaling_law_hypotheses(kg, gaps))

    all_hypotheses = evaluate_hypotheses(all_hypotheses, kg)
    print_hypotheses_summary(all_hypotheses)

    os.makedirs(output_dir, exist_ok=True)
    export_hypotheses(
        all_hypotheses,
        os.path.join(output_dir, "hypotheses.json")
    )

    return all_hypotheses


if __name__ == "__main__":
    import sys
    from block1_literature_mining import run_block1
    from block2_gap_detector import run_block2

    input_file = sys.argv[1] if len(sys.argv) > 1 else "../literature_overview.rtf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./outputs"

    kg = run_block1(input_file, output_dir)
    gaps, _ = run_block2(kg, output_dir)
    run_block3(kg, gaps, output_dir)
