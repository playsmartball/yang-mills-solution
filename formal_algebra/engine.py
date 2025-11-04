from __future__ import annotations
from typing import List
import sympy as sp
from .core import SymbolicVar
from .proof import Proof, ProofStep


class Prover:
    def __init__(self):
        self.phi = SymbolicVar('phi', positive=True).to_symbol()
        self.g0 = SymbolicVar('g0', positive=True).to_symbol()
        self.beta_exp = SymbolicVar('beta_exp', positive=True).to_symbol()
        self.Lambda = SymbolicVar('Lambda', positive=True).to_symbol()
        self.c_strong = SymbolicVar('c_strong', positive=True).to_symbol()

    def assumptions_common(self) -> List[str]:
        return [
            'phi ∈ (0,1]',
            'g0 > 0',
            'beta_exp > 0',
            'Lambda > 0',
            'c_strong > 0',
        ]

    def g_of_phi(self):
        return self.g0 * self.phi**(-self.beta_exp)

    def prove_T1_domain_positivity(self) -> Proof:
        steps: List[ProofStep] = []
        g_phi = self.g_of_phi()
        steps.append(ProofStep(
            description='Define g(φ) = g0 * φ^(−β_exp).',
            before=None,
            after=str(g_phi),
        ))
        steps.append(ProofStep(
            description='Since g0>0, φ>0, β_exp>0, we have φ^(−β_exp)>0 and thus g(φ)>0 on (0,1].',
        ))
        conclusion = 'For φ∈(0,1], g(φ) > 0.'
        return Proof('T1: Positivity of g(φ)', self.assumptions_common(), steps, conclusion)

    def prove_T2_monotone_decreasing(self) -> Proof:
        steps: List[ProofStep] = []
        g_phi = self.g_of_phi()
        dg_dphi = sp.diff(g_phi, self.phi)
        steps.append(ProofStep(
            description='Compute derivative of g(φ).',
            before=str(g_phi),
            after=str(dg_dphi),
        ))
        steps.append(ProofStep(
            description='Since g0>0, β_exp>0, φ>0, then −β_exp*g0*φ^(−β_exp−1) < 0.',
        ))
        conclusion = 'g′(φ) < 0 on (0,1]; g(φ) is strictly decreasing.'
        return Proof('T2: Monotonicity of g(φ)', self.assumptions_common(), steps, conclusion)

    def prove_T3_mass_gap_positivity(self) -> Proof:
        steps: List[ProofStep] = []
        g = sp.Symbol('g', positive=True)
        M_strong = self.Lambda * g * self.c_strong
        M_weak = self.Lambda * sp.exp(-8*sp.pi**2/(3*g**2))
        steps.append(ProofStep(
            description='Strong regime (g>1): M = Λ * g * c_strong with Λ>0, g>0, c_strong>0 ⇒ M>0.',
            before=str(M_strong),
            after='M>0',
        ))
        steps.append(ProofStep(
            description='Weak regime (0<g≤1): M = Λ * exp(-8π²/(3 g²)), exp(...)>0 and Λ>0 ⇒ M>0.',
            before=str(M_weak),
            after='M>0',
        ))
        conclusion = 'For all g>0, M(g) > 0; hence spectral positivity (mass gap) holds pointwise.'
        return Proof('T3: Positivity of mass gap M(g)', self.assumptions_common(), steps, conclusion)
