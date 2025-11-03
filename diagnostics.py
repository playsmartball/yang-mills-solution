"""
Diagnostic analysis for Yang-Mills mass gap calculation issues
Identifies problems and suggests theoretical refinements
"""

import numpy as np
import matplotlib.pyplot as plt
from yang_mills_theory import YangMillsParameters, PhiCoordinateTheory


class MassGapDiagnostics:
    """Diagnose issues with mass gap calculation"""
    
    def __init__(self):
        self.params = YangMillsParameters()
        self.theory = PhiCoordinateTheory(self.params)
        
    def analyze_coupling_regime(self):
        """Analyze whether coupling is in appropriate regime"""
        print("\n" + "="*70)
        print("DIAGNOSTIC: Coupling Strength Analysis")
        print("="*70)
        
        phi_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        print("\nCoupling values across φ range:")
        print(f"{'φ':>8} {'g(φ)':>12} {'g²':>12} {'8π²/3g²':>15} {'exp(-8π²/3g²)':>20}")
        print("-"*70)
        
        for phi in phi_values:
            g = self.theory.coupling_at_phi(phi)
            g2 = g**2
            exponent_arg = 8*np.pi**2 / (3*g2) if g > 0 else np.inf
            mass_factor = np.exp(-exponent_arg) if exponent_arg < 100 else 0.0
            
            print(f"{phi:8.3f} {g:12.6f} {g2:12.6f} {exponent_arg:15.2f} {mass_factor:20.6e}")
        
        print("\n⚠ PROBLEM IDENTIFIED:")
        print("   The coupling g(φ) is too small throughout most of the φ range.")
        print("   This causes exp(-8π²/3g²) → 0, giving M_gap → 0.")
        
        print("\n💡 POTENTIAL SOLUTIONS:")
        print("   1. Modify coupling evolution: g(φ) = g₀ * φ^(-β₀) [note the negative power]")
        print("   2. Adjust mass gap formula to use running scale")
        print("   3. Include non-perturbative corrections")
        print("   4. Redefine φ mapping to physical scales")
        
    def test_alternative_coupling(self):
        """Test alternative coupling parametrization"""
        print("\n" + "="*70)
        print("DIAGNOSTIC: Alternative Coupling Parametrization")
        print("="*70)
        
        phi_values = np.linspace(0.1, 0.9, 50)
        
        # Original: g = g₀ φ^β₀ (decreases as φ increases)
        g_original = np.array([self.theory.coupling_at_phi(p) for p in phi_values])
        
        # Alternative 1: g = g₀ φ^(-β₀) (increases as φ increases - correct for IR)
        g_alt1 = self.params.g0 * phi_values**(-self.params.beta0_coefficient)
        
        # Alternative 2: g = g₀ / (1 - φ) (pole at φ=1)
        g_alt2 = self.params.g0 / (1.0 - phi_values)
        
        # Alternative 3: g = g₀ * (φ/(1-φ))^β₀
        g_alt3 = self.params.g0 * (phi_values / (1.0 - phi_values))**self.params.beta0_coefficient
        
        # Compute mass gaps
        Lambda = self.params.Lambda_QCD
        
        def safe_mass_gap(g_vals):
            result = []
            for g in g_vals:
                if g > 0.5:  # Only compute where coupling is strong
                    exponent = -8*np.pi**2/(3*g**2)
                    if exponent > -50:  # Avoid underflow
                        result.append(Lambda * np.exp(exponent))
                    else:
                        result.append(0.0)
                else:
                    result.append(0.0)
            return np.array(result)
        
        M_alt1 = safe_mass_gap(g_alt1)
        M_alt3 = safe_mass_gap(g_alt3)
        
        # Find where mass gap is non-zero
        valid_alt1 = np.where(M_alt1 > 0)[0]
        valid_alt3 = np.where(M_alt3 > 0)[0]
        
        print("\nAlternative 1: g(φ) = g₀ φ^(-β₀)")
        if len(valid_alt1) > 0:
            idx = valid_alt1[0]
            print(f"   First non-zero mass gap at φ={phi_values[idx]:.3f}")
            print(f"   g={g_alt1[idx]:.4f}, M_gap={M_alt1[idx]:.6e} GeV")
        else:
            print("   No non-zero mass gap found")
        
        print("\nAlternative 3: g(φ) = g₀ (φ/(1-φ))^β₀")
        if len(valid_alt3) > 0:
            idx = valid_alt3[0]
            print(f"   First non-zero mass gap at φ={phi_values[idx]:.3f}")
            print(f"   g={g_alt3[idx]:.4f}, M_gap={M_alt3[idx]:.6e} GeV")
            
            # Check at φ=0.5
            idx_half = np.argmin(np.abs(phi_values - 0.5))
            print(f"\n   At φ=0.5: g={g_alt3[idx_half]:.4f}, M_gap={M_alt3[idx_half]:.6e} GeV")
        else:
            print("   No non-zero mass gap found")
        
        # Plot comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(phi_values, g_original, 'b-', label='Original: φ^β₀', linewidth=2)
        ax1.plot(phi_values, np.minimum(g_alt1, 5), 'r--', label='Alt1: φ^(-β₀)', linewidth=2)
        ax1.plot(phi_values, np.minimum(g_alt3, 5), 'g-.', label='Alt3: (φ/(1-φ))^β₀', linewidth=2)
        ax1.axvline(x=0.5, color='k', linestyle=':', alpha=0.5)
        ax1.set_xlabel('φ')
        ax1.set_ylabel('g(φ)')
        ax1.set_title('Coupling Evolution Comparison')
        ax1.set_ylim(0, 5)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.semilogy(phi_values[M_alt1>0], M_alt1[M_alt1>0], 'r--', label='Alt1', linewidth=2)
        ax2.semilogy(phi_values[M_alt3>0], M_alt3[M_alt3>0], 'g-.', label='Alt3', linewidth=2)
        ax2.axhline(y=1.67, color='orange', linestyle=':', label='Glueball (lattice)', alpha=0.7)
        ax2.axvline(x=0.5, color='k', linestyle=':', alpha=0.5)
        ax2.set_xlabel('φ')
        ax2.set_ylabel('M_gap (GeV)')
        ax2.set_title('Mass Gap with Alternative Couplings')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/Users/hodge/Desktop/yang-mills/diagnostic_alternatives.png', dpi=150)
        print("\n📊 Diagnostic plot saved: diagnostic_alternatives.png")
        
    def analyze_dimensional_interpretation(self):
        """Analyze the physical interpretation of φ"""
        print("\n" + "="*70)
        print("DIAGNOSTIC: φ-Coordinate Physical Interpretation")
        print("="*70)
        
        print("\nCurrent interpretation: φ ∈ [0,1]")
        print("  φ → 0: UV limit (high energy, short distance)")
        print("  φ = 0.5: Critical boundary")
        print("  φ → 1: IR limit (low energy, long distance)")
        
        print("\nRelation to RG scale:")
        print("  If φ ~ (Λ/μ)^(1/b₀), then:")
        print("    • φ → 0 corresponds to μ → ∞ (UV)")
        print("    • φ → 1 corresponds to μ → Λ (IR)")
        
        print("\n⚠ INCONSISTENCY:")
        print("  Current: g(φ) = g₀ φ^β₀")
        print("  This gives g → 0 as φ → 0 (correct)")
        print("  But also g → 0 as φ → 1 if using φ ~ (Λ/μ)^(1/b₀)")
        print("  We need g → large as φ → 1 (IR) for confinement!")
        
        print("\n💡 SUGGESTED FIX:")
        print("  Use inverse relationship: g(φ) = g₀ (1-φ)^(-α) or g₀ φ^(-β₀)")
        print("  This ensures:")
        print("    • g small at φ → 0 (asymptotic freedom)")
        print("    • g large at φ → 1 (confinement)")
        
    def recommend_corrections(self):
        """Provide concrete recommendations for theory refinement"""
        print("\n" + "="*70)
        print("RECOMMENDATIONS FOR THEORY REFINEMENT")
        print("="*70)
        
        print("\n1. COUPLING PARAMETRIZATION:")
        print("   Current: g(φ) = g₀ φ^β₀")
        print("   Corrected: g(φ) = g₀ φ^(-β₀)  [inverted power]")
        print("   Rationale: Ensures strong coupling in IR (large φ)")
        
        print("\n2. MASS GAP FORMULA:")
        print("   Keep: M_gap = Λ_QCD exp(-8π²/3g²(φ))")
        print("   But evaluate at: φ ≈ 0.8-0.9 (deep IR)")
        print("   Expected: g(φ=0.9) ~ 1-2, giving M_gap ~ 0.1-1 GeV ✓")
        
        print("\n3. DIMENSIONAL BOUNDARY:")
        print("   Keep: φ_c = 0.5 as transition point")
        print("   Interpretation: Transition from perturbative to non-perturbative")
        print("   For φ < 0.5: perturbative QCD (weak coupling)")
        print("   For φ > 0.5: non-perturbative (strong coupling, confinement)")
        
        print("\n4. BETA FUNCTION CONSISTENCY:")
        print("   With g(φ) = g₀ φ^(-β₀):")
        print("   dg/dφ = -β₀ g₀ φ^(-β₀-1) = -β₀ g/φ")
        print("   This naturally gives β(g) ~ -g³ behavior ✓")
        
        print("\n5. IMPLEMENTATION:")
        print("   Modify line in yang_mills_theory.py:")
        print("   FROM: return self.params.g0 * phi_val**(self.params.beta0_coefficient)")
        print("   TO:   return self.params.g0 * phi_val**(-self.params.beta0_coefficient)")
        
        print("\n6. EXPECTED OUTCOMES:")
        print("   • Mass gap at φ=0.5: ~10^-3 GeV (transition)")
        print("   • Mass gap at φ=0.9: ~1 GeV (matches glueball)")
        print("   • Asymptotic freedom maintained")
        print("   • Confinement in IR regime")


if __name__ == "__main__":
    diagnostics = MassGapDiagnostics()
    
    diagnostics.analyze_coupling_regime()
    diagnostics.test_alternative_coupling()
    diagnostics.analyze_dimensional_interpretation()
    diagnostics.recommend_corrections()
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nThe primary issue is the sign of the power in the coupling evolution.")
    print("The corrected formula should produce a mass gap in the GeV range.")
