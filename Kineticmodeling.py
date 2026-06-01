r'''
1. Kinetic Modeling & Half-Life Predictions
This script uses Eyring-Polanyi transition-state theory to calculate how different confinement free energies ($\Delta G_{\text{conf}}$) impact the thermal back-reaction rate ($k_{\text{host}}$) and shelf life ($\tau_{\text{host}}$) across a range of operational temperatures. 
'''
import numpy as np
import matplotlib.pyplot as plt

# Universal Constants
KB = 1.380649e-23  # Boltzmann constant (J/K)
H = 6.62607015e-34  # Planck constant (J s)
R = 8.3145          # Ideal gas constant (J/mol K)

def calculate_rate_constant(temperature, delta_g_activation):
    """Calculates the first-order rate constant using Eyring-Polanyi theory."""
    return (KB * temperature / H) * np.exp(-delta_g_activation / (R * temperature))

def simulate_shelf_life(t_celsius, dg_relax_kj, dg_conf_kj):
    """Predicts half-life extension based on baseline and confinement energy."""
    temp_k = t_celsius + 273.15
    dg_relax = dg_relax_kj * 1000  # Convert to J/mol
    dg_conf = dg_conf_kj * 1000    # Convert to J/mol
    
    # Calculate rates
    k_free = calculate_rate_constant(temp_k, dg_relax)
    k_host = calculate_rate_constant(temp_k, dg_relax + dg_conf)
    
    # Half-life (t_1/2 = ln(2)/k)
    tau_free_days = (np.log(2) / k_free) / (24 * 3600)
    tau_host_days = (np.log(2) / k_host) / (24 * 3600)
    
    return tau_free_days, tau_host_days

# --- Run a Prediction ---
# Let's assume a baseline relaxation barrier that gives a room-temp half-life of ~3 days
DG_RELAX_ASSUMED = 95.0  # kJ/mol
DG_CONF_HYPOTHESIS = 12.0  # kJ/mol (as suggested in paper)
temp_range = np.linspace(0, 50, 100)  # 0°C to 50°C

free_lifes, host_lifes = [], []
for T in temp_range:
    tau_f, tau_h = simulate_shelf_life(T, DG_RELAX_ASSUMED, DG_CONF_HYPOTHESIS)
    free_lifes.append(tau_f)
    host_lifes.append(tau_h)

# Plotting the impact
plt.figure(figsize=(10, 5))
plt.plot(temp_range, free_lifes, 'r--', label='Neat / Solution (Unconfined)')
plt.plot(temp_range, host_lifes, 'g-', label='In Protein Matrix (Confined)')
plt.yscale('log')
plt.xlabel('Ambient Temperature (°C)')
plt.ylabel('Charged Isomer Half-life (Days)')
plt.title('Predicted Shelf-life Extension via Matrix Confinement')
plt.grid(True, which="both", ls="--")
plt.legend()
plt.show()

# Print specific room temp calculation
f_25, h_25 = simulate_shelf_life(25, DG_RELAX_ASSUMED, DG_CONF_HYPOTHESIS)
print(f"At 25°C:")
print(f"  Baseline half-life: {f_25:.2f} days")
print(f"  Predicted scaffolded half-life: {h_25:.2f} days (Factor of {h_25/f_25:.1f}x improvement)")