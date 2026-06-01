r'''
3. Kinetic Discharging Simulator (Acid-Catalyzed Trigger)When it is time to extract the heat, an acid catalyst is applied to bypass the structural barrier. This script models the dynamic, time-dependent heat release ($Q$) profiles during a triggered discharge. 
How to use these scripts to actually "test" your theoryOnce your laboratory control experiments are complete (as outlined in Section 5), you can substitute your real data points into these scripts:  Run UV-Vis or NMR over a temperature series to obtain real values for $k_{\text{free}}$ and $k_{\text{host}}$.  Use an Arrhenius / Eyring plot (plotting $\ln(k/T)$ vs $1/T$) to extract the slope and intercept, which will give you the precise experimental values for $\Delta G^{\ddagger}_{\text{relax}}$ and $\Delta G_{\text{conf}}$.  Plug those measured values back into Script 1 to verify if your shelf-life matches predictions.   
'''


from scipy.integrate import solve_ivp

def thermal_discharge_ode(t, y, k_triggered, delta_h_j_mol):
    """ODE representing the first-order decay of the Dewar isomer [D] to Pyrimidone [P]."""
    D = y[0]  # Moles of Dewar isomer remaining
    dD_dt = -k_triggered * D
    return [dD_dt]

# Parameters
moles_init = 1.0  # Let's track 1 mole of stored isomer
DH_STORAGE = 227600  # J/mol (227.6 kJ/mol from paper)
K_TRIGGERED = 0.05   # Fast triggered back-reaction rate constant (1/s) under acid catalysis

# Simulate over 120 seconds
t_span = (0, 120)
t_eval = np.linspace(0, 120, 500)

solution = solve_ivp(thermal_discharge_ode, t_span, [moles_init], args=(K_TRIGGERED, DH_STORAGE), t_eval=t_eval)

# Calculate metrics
moles_remaining = solution.y[0]
moles_converted = moles_init - moles_remaining
cumulative_heat_released_kj = (moles_converted * DH_STORAGE) / 1000
heat_flow_rate_watts = K_TRIGGERED * moles_remaining * DH_STORAGE

# Plotting the thermal discharge behavior
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(solution.t, cumulative_heat_released_kj, 'orange', label='Total Heat Released')
plt.xlabel('Time (seconds)')
plt.ylabel('Cumulative Heat Released (kJ)')
plt.title('Energy Release Profile')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(solution.t, heat_flow_rate_watts, 'r', label='Thermal Power Output')
plt.xlabel('Time (seconds)')
plt.ylabel('Thermal Power (Watts / J per sec)')
plt.title('Power Delivery Spectrum')
plt.grid(True)

plt.tight_layout()
plt.show()