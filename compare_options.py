import numpy as np
from dataclasses import replace
from yang_mills_theory import YangMillsParameters, PhiCoordinateTheory
from experimental_validation import ExperimentalData


def summarize_option(name: str, params: YangMillsParameters):
    theory = PhiCoordinateTheory(params)
    data = ExperimentalData()

    phi_c = params.phi_critical
    g_05 = theory.coupling_at_phi(0.5)
    M_05 = theory.mass_gap(0.5)
    M_0505 = theory.mass_gap(0.505)

    # Glueball at 0.52 (as in validation) and at 0.505 (to match manuscript narrative)
    M_glue_052 = theory.mass_gap(0.52)
    M_lat, dM = data.glueball_0pp
    sigma_052 = abs(M_glue_052 - M_lat) / dM

    M_glue_0505 = theory.mass_gap(0.505)
    sigma_0505 = abs(M_glue_0505 - M_lat) / dM

    # String tension proxy at 0.55, as in validation
    phi_string = 0.55
    M_gap = theory.mass_gap(phi_string)
    sigma_pred = (M_gap / 2.2) ** 2
    sigma_exp, delta_sigma = data.string_tension
    rel_err_sigma = abs(sigma_pred - sigma_exp) / sigma_exp

    # Asymptotic freedom at UV ~ 0.95 per manuscript mapping
    phi_uv = 0.95
    g_uv = theory.coupling_at_phi(phi_uv)
    perturbative = g_uv < 1.0

    # W3 positivity sweep
    phis = np.linspace(0.1, 0.9, 20)
    gaps = np.array([theory.mass_gap(p) for p in phis])
    min_gap = float(gaps.min())
    all_positive = bool((gaps > 0).all())

    print(f"\n=== {name} ===")
    print(f"Params: g0={params.g0:.6g}, beta_exp={params.beta0_coefficient:.6g}, Lambda_QCD={params.Lambda_QCD:.3f}")
    print(f"g(0.5) = {g_05:.4f}")
    print(f"M_gap(0.5) = {M_05:.3f} GeV; M_gap(0.505) = {M_0505:.3f} GeV")
    print(f"Glueball (0.52): pred={M_glue_052:.3f} vs lat={M_lat:.3f} ± {dM:.3f} → {sigma_052:.2f}σ")
    print(f"Glueball (0.505): pred={M_glue_0505:.3f} vs lat={M_lat:.3f} ± {dM:.3f} → {sigma_0505:.2f}σ")
    print(f"String tension proxy (0.55): pred={sigma_pred:.3f} GeV^2 vs exp={sigma_exp:.3f} → rel err={rel_err_sigma*100:.1f}%")
    print(f"Asymptotic freedom at φ=0.95: g={g_uv:.4f} → perturbative={perturbative}")
    print(f"W3 positivity: min gap over φ∈[0.1,0.9] = {min_gap:.3e} GeV; all_positive={all_positive}")


if __name__ == "__main__":
    # Option A: current code parameters (after minimal fixes)
    params_A = YangMillsParameters()

    # Option B: use exponent 11.0 and tune g0 so that strong-regime M_gap(0.5) ≈ 1.83 GeV
    # Strong branch gives M ≈ Λ_QCD * g * 2.8 ⇒ target g ≈ 1.83 / (Λ * 2.8)
    Lambda = 0.200
    target_M = 1.83
    target_g = target_M / (Lambda * 2.8)  # ≈ 3.27
    beta_exp_B = 11.0
    phi = 0.5
    g0_B = target_g * (phi ** beta_exp_B)  # g0 = g * φ^{β}

    params_B = replace(params_A, g0=float(g0_B), beta0_coefficient=float(beta_exp_B))

    summarize_option("Option A (φ-scheme exponent 11/3, g0=0.25)", params_A)
    summarize_option("Option B (exponent 11.0, tuned g0)", params_B)
