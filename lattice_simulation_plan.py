"""
Reproducible Lattice QCD Simulation Plan
Yang-Mills φ-Coordinate Implementation
"""

import numpy as np
import yaml

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

simulation_params = {
    'gauge_group': 'SU(3)',
    'N_colors': 3,
    'n_flavors': 0,  # Pure Yang-Mills
    
    'phi_values': [0.2, 0.3, 0.4, 0.5, 0.6, 0.8],
    'g0': 0.00073242,
    'beta0': 11.0,
    
    'lattice_sizes': [
        [24, 24, 24, 48],
        [32, 32, 32, 64],
        [40, 40, 40, 80]
    ],
    
    'hmc': {
        'trajectory_length': 1.0,
        'n_steps': 100,
        'target_acceptance': 0.75,
    },
    
    'thermalization': 1000,
    'n_configurations': 2000,
    'measurement_interval': 10,
    
    'smearing': {
        'type': 'APE',
        'alpha': 0.5,
        'n_iterations': 50
    }
}

# Save parameters
with open('/Users/hodge/Desktop/yang-mills/lattice_params.yaml', 'w') as f:
    yaml.dump(simulation_params, f)

print("Lattice simulation parameters saved to lattice_params.yaml")
print(f"Ready for {len(simulation_params['phi_values'])} φ values")
print(f"Ready for {len(simulation_params['lattice_sizes'])} lattice sizes")
