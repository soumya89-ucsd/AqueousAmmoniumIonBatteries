r'''
2. Gravimetric Dilution vs. Stability Trade-off OptimizerAs noted in Section 6, embedding the isomer in a protein matrix adds dead weight, lowering the composite's overall energy density ($\rho_E$). This script solves for the optimization frontier: finding the minimum protein mass fraction required to hit a target shelf-life without completely tanking your energy density.  
'''


import numpy as np
import matplotlib.pyplot as plt
def optimize_composite(mass_fraction_isomer, neat_density_mj_kg=1.65):
    """Calculates the diluted energy density based on host loading."""
    # Composite energy density scaling linearly with mass fraction of active material
    return mass_fraction_isomer * neat_density_mj_kg

# Range of isomer mass loadings (from 10% active up to 100% neat isomer)
isomer_loadings = np.linspace(0.1, 1.0, 50)
composite_densities = optimize_composite(isomer_loadings)

# Let's assume a hypothetical relationship where higher protein content (lower isomer loading)
# linearly or logarithmically increases confinement quality up to a ceiling.
def empirical_dg_conf(isomer_loading):
    # Max 15 kJ/mol at low loading, drops to 0 at 100% loading (neat solid)
    return 15.0 * (1.0 - isomer_loading)

plt.figure(figsize=(10, 5))
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Isomer Mass Fraction in Composite')
ax1.set_ylabel('Composite Heat Storage Density (MJ/kg)', color=color)
ax1.plot(isomer_loadings, composite_densities, color=color, linewidth=2)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:green'
ax2.set_ylabel('Hypothetical Confinement Barrier ΔG_conf (kJ/mol)', color=color)
ax2.plot(isomer_loadings, [empirical_dg_conf(x) for x in isomer_loadings], color=color, linestyle='--')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('The Optimization Frontier: Energy Density vs. Confinement Stabilization')
fig.tight_layout()  
plt.show()
# TODO FIX THE BLANK PLOT