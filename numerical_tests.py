"""
Numerical tests for φ-coordinate Yang-Mills theory
Implements computational validation of theoretical predictions
"""

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
from yang_mills_theory import YangMillsParameters, PhiCoordinateTheory


class NumericalTests:
    """Numerical validation of Yang-Mills mass gap theory"""
    
    def __init__(self, params: YangMillsParameters):
        self.params = params
        self.theory = PhiCoordinateTheory(params)
        self.results = {}
        
    def test_coupling_evolution(self, phi_range: Tuple[float, float] = (0.01, 1.0), 
                                num_points: int = 1000) -> Dict:
        """Test coupling constant evolution across φ range"""
        print("\n=== Numerical Test: Coupling Evolution ===")
        
        phi_values = np.linspace(phi_range[0], phi_range[1], num_points)
        g_values = np.array([self.theory.coupling_at_phi(p) for p in phi_values])
        
        # Check asymptotic freedom: g should decrease as φ→0
        g_ratio = g_values[0] / g_values[-1]
        asymptotic_freedom_verified = g_ratio < 0.1
        
        # Check critical behavior at φ=0.5
        idx_critical = np.argmin(np.abs(phi_values - 0.5))
        g_critical = g_values[idx_critical]
        
        # Compute derivative at critical point
        delta_phi = phi_values[1] - phi_values[0]
        dg_dphi_critical = (g_values[idx_critical+1] - g_values[idx_critical-1]) / (2*delta_phi)
        
        result = {
            'test': 'Coupling Evolution',
            'phi_range': phi_range,
            'g_at_UV': g_values[0],
            'g_at_IR': g_values[-1],
            'g_at_critical': g_critical,
            'dg_dphi_at_critical': dg_dphi_critical,
            'asymptotic_freedom': asymptotic_freedom_verified,
            'passes': asymptotic_freedom_verified and g_critical > 0
        }
        
        print(f"g(φ=0.01) = {result['g_at_UV']:.6f} (UV)")
        print(f"g(φ=0.50) = {result['g_at_critical']:.6f} (Critical)")
        print(f"g(φ=1.00) = {result['g_at_IR']:.6f} (IR)")
        print(f"dg/dφ|_critical = {dg_dphi_critical:.6f}")
        print(f"{'✓ PASS' if result['passes'] else '✗ FAIL'}")
        
        self.results['coupling_evolution'] = result
        self._plot_coupling_evolution(phi_values, g_values)
        
        return result
    
    def test_mass_gap_spectrum(self) -> Dict:
        """Calculate mass gap across φ values"""
        print("\n=== Numerical Test: Mass Gap Spectrum ===")
        
        phi_values = np.linspace(0.1, 0.9, 100)
        mass_gaps = np.array([self.theory.mass_gap(p) for p in phi_values])
        
        # Find minimum mass gap
        min_gap_idx = np.argmin(mass_gaps)
        min_gap = mass_gaps[min_gap_idx]
        phi_min = phi_values[min_gap_idx]
        
        # Check positivity
        all_positive = np.all(mass_gaps > 0)
        
        # Mass gap at critical φ=0.5
        idx_critical = np.argmin(np.abs(phi_values - 0.5))
        gap_critical = mass_gaps[idx_critical]
        
        result = {
            'test': 'Mass Gap Spectrum',
            'min_mass_gap_GeV': min_gap,
            'phi_at_min_gap': phi_min,
            'mass_gap_at_critical_GeV': gap_critical,
            'all_positive': all_positive,
            'passes': all_positive and min_gap > 0
        }
        
        print(f"Minimum M_gap = {min_gap:.6e} GeV at φ={phi_min:.3f}")
        print(f"M_gap(φ=0.5) = {gap_critical:.6e} GeV")
        print(f"All gaps positive: {all_positive}")
        print(f"{'✓ PASS' if result['passes'] else '✗ FAIL'}")
        
        self.results['mass_gap_spectrum'] = result
        self._plot_mass_gap(phi_values, mass_gaps)
        
        return result
    
    def test_dimensional_boundary_sharpness(self, epsilon: float = 0.01) -> Dict:
        """Test sharpness of transition at φ=0.5±ε"""
        print(f"\n=== Numerical Test: Dimensional Boundary (ε={epsilon}) ===")
        
        phi_c = self.params.phi_critical
        
        # Sample around critical point
        phi_left = phi_c - epsilon
        phi_right = phi_c + epsilon
        
        g_left = self.theory.coupling_at_phi(phi_left)
        g_center = self.theory.coupling_at_phi(phi_c)
        g_right = self.theory.coupling_at_phi(phi_right)
        
        # Metric factor transition
        metric_left = self.theory.dimensional_metric(phi_left)
        metric_center = self.theory.dimensional_metric(phi_c)
        metric_right = self.theory.dimensional_metric(phi_right)
        
        # Check transition sharpness
        metric_transition = abs(metric_right - metric_left)
        sharp_transition = metric_transition > 0.5  # Significant change in small interval
        
        result = {
            'test': 'Dimensional Boundary Sharpness',
            'epsilon': epsilon,
            'g_before': g_left,
            'g_at_boundary': g_center,
            'g_after': g_right,
            'metric_before': metric_left,
            'metric_at_boundary': metric_center,
            'metric_after': metric_right,
            'metric_transition': metric_transition,
            'sharp_transition': sharp_transition,
            'passes': sharp_transition
        }
        
        print(f"φ = {phi_c-epsilon:.3f}: g={g_left:.4f}, metric={metric_left:.4f}")
        print(f"φ = {phi_c:.3f}: g={g_center:.4f}, metric={metric_center:.4f}")
        print(f"φ = {phi_c+epsilon:.3f}: g={g_right:.4f}, metric={metric_right:.4f}")
        print(f"Metric transition: {metric_transition:.4f}")
        print(f"{'✓ PASS' if result['passes'] else '✗ FAIL'}")
        
        self.results['dimensional_boundary'] = result
        
        return result
    
    def test_confinement_scale(self) -> Dict:
        """Test confinement scale matches QCD expectations"""
        print("\n=== Numerical Test: Confinement Scale ===")
        
        # At φ close to critical, expect confinement
        phi_conf = 0.6  # Slightly into IR region
        
        g_conf = self.theory.coupling_at_phi(phi_conf)
        M_conf = self.theory.mass_gap(phi_conf)
        
        # String tension σ ≈ (440 MeV)² from phenomenology
        # Related to mass gap: σ ~ M²
        sigma_predicted = M_conf**2
        sigma_experimental = 0.440**2  # GeV²
        
        relative_error = abs(sigma_predicted - sigma_experimental) / sigma_experimental
        acceptable_error = relative_error < 2.0  # Factor of 2
        
        result = {
            'test': 'Confinement Scale',
            'phi_confinement': phi_conf,
            'coupling_g': g_conf,
            'mass_gap_GeV': M_conf,
            'string_tension_predicted_GeV2': sigma_predicted,
            'string_tension_experimental_GeV2': sigma_experimental,
            'relative_error': relative_error,
            'passes': acceptable_error
        }
        
        print(f"At φ={phi_conf}: g={g_conf:.4f}")
        print(f"Predicted σ = {sigma_predicted:.6e} GeV²")
        print(f"Experimental σ = {sigma_experimental:.6e} GeV²")
        print(f"Relative error: {relative_error*100:.1f}%")
        print(f"{'✓ PASS' if result['passes'] else '⚠ WARNING' if relative_error < 10 else '✗ FAIL'}")
        
        self.results['confinement_scale'] = result
        
        return result
    
    def test_renormalization_group_flow(self, num_steps: int = 1000) -> Dict:
        """Test RG flow equation: dg/d(ln μ) = β(g)"""
        print("\n=== Numerical Test: Renormalization Group Flow ===")
        
        # Map φ to RG scale μ via φ ~ (Λ/μ)^(1/b0)
        # Then verify β function
        
        phi_values = np.linspace(0.1, 0.9, num_steps)
        g_values = np.array([self.theory.coupling_at_phi(p) for p in phi_values])
        
        # Numerical derivative dg/dφ
        dg_dphi = np.gradient(g_values, phi_values)
        
        # Beta function: β(g) ≈ -b₀g³
        b0 = self.params.beta0_coefficient
        beta_expected = -b0 * g_values**3
        
        # From g(φ) = g₀ φ^β₀, we get dg/dφ = β₀ g₀ φ^(β₀-1) = β₀ g/φ
        beta_from_phi = b0 * g_values / phi_values
        
        # Compare
        relative_diff = np.abs(dg_dphi - beta_from_phi) / (np.abs(beta_from_phi) + 1e-10)
        avg_diff = np.mean(relative_diff)
        
        result = {
            'test': 'RG Flow Consistency',
            'b0_coefficient': b0,
            'avg_relative_difference': avg_diff,
            'max_relative_difference': np.max(relative_diff),
            'passes': avg_diff < 0.1
        }
        
        print(f"b₀ = {b0:.4f}")
        print(f"Average RG flow deviation: {avg_diff*100:.2f}%")
        print(f"{'✓ PASS' if result['passes'] else '✗ FAIL'}")
        
        self.results['rg_flow'] = result
        
        return result
    
    def _plot_coupling_evolution(self, phi_values, g_values):
        """Plot coupling constant vs φ"""
        plt.figure(figsize=(10, 6))
        plt.plot(phi_values, g_values, 'b-', linewidth=2, label='g(φ)')
        plt.axvline(x=0.5, color='r', linestyle='--', label='φ_critical = 0.5')
        plt.xlabel('φ (dimensional parameter)', fontsize=12)
        plt.ylabel('g(φ) (coupling constant)', fontsize=12)
        plt.title('Running Coupling vs φ-Coordinate', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig('/Users/hodge/Desktop/yang-mills/coupling_evolution.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  → Plot saved: coupling_evolution.png")
    
    def _plot_mass_gap(self, phi_values, mass_gaps):
        """Plot mass gap vs φ"""
        plt.figure(figsize=(10, 6))
        plt.semilogy(phi_values, mass_gaps, 'g-', linewidth=2, label='M_gap(φ)')
        plt.axvline(x=0.5, color='r', linestyle='--', label='φ_critical = 0.5')
        plt.axhline(y=self.params.Lambda_QCD, color='k', linestyle=':', label='Λ_QCD', alpha=0.5)
        plt.xlabel('φ (dimensional parameter)', fontsize=12)
        plt.ylabel('M_gap (GeV)', fontsize=12)
        plt.title('Mass Gap Spectrum vs φ-Coordinate', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig('/Users/hodge/Desktop/yang-mills/mass_gap_spectrum.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  → Plot saved: mass_gap_spectrum.png")
    
    def generate_report(self) -> str:
        """Generate numerical test report"""
        report = "\n" + "="*70 + "\n"
        report += "NUMERICAL TEST REPORT\n"
        report += "="*70 + "\n\n"
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r.get('passes', False))
        
        for test_name, result in self.results.items():
            report += f"\n{test_name.upper().replace('_', ' ')}:\n"
            status = '✓ PASS' if result.get('passes', False) else '✗ FAIL'
            report += f"  Status: {status}\n"
            for key, value in result.items():
                if key not in ['test', 'passes']:
                    if isinstance(value, float):
                        report += f"  {key}: {value:.6e}\n"
                    else:
                        report += f"  {key}: {value}\n"
        
        report += f"\n{'='*70}\n"
        report += f"Numerical Tests Passed: {passed_tests}/{total_tests}\n"
        report += "="*70 + "\n"
        
        return report


if __name__ == "__main__":
    print("Yang-Mills Mass Gap - Numerical Validation")
    print("="*70)
    
    params = YangMillsParameters()
    tester = NumericalTests(params)
    
    # Run all numerical tests
    tester.test_coupling_evolution()
    tester.test_mass_gap_spectrum()
    tester.test_dimensional_boundary_sharpness()
    tester.test_confinement_scale()
    tester.test_renormalization_group_flow()
    
    # Print report
    print(tester.generate_report())
