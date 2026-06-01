r'''

Because the foundational parameters of the Dewar pyrimidone molecule were fully mapped out in the 2026 Science paper—and the raw kinetic, differential scanning calorimetry (DSC), and thermogravimetric analysis (TGA) datasets are publicly hosted on Dryad—you have a wealth of concrete empirical values to work with right now. 
Before committing resources in the wet lab, you can construct a multi-scale simulation framework spanning three distinct regimes: Quantum Chemistry, Molecular Dynamics, and Continuum Engineering.
Track 1: Quantum Chemistry (DFT Cluster Models)
    • What you already have: The exact molecular coordinates and geometries of the ground-state pyrimidone and the strained Dewar photoisomer (from the Nguyen et al. supplementary data), along with the baseline activation energy ($\sim 95\text{ kJ/mol}$).
    • What you can simulate now: You don't need a full protein matrix to estimate the confinement free energy ($\Delta G_{\text{conf}}$). You can use DFT cluster modeling in open-source quantum chemistry packages like ORCA or NWChem.
    • Methodology: 1. Build a small cluster containing one Dewar pyrimidone molecule surrounded by 3 to 5 representative functional groups dominant in plant proteins like pea protein (e.g., formamide to mimic the peptide backbone, acetamide for glutamine/asparagine side chains, and a guanidinium ion for arginine).
      2. Optimize the ground-state geometry and locate the transition state (TS) for the thermal back-reaction within this hydrogen-bonding cluster.
      3. Compare the calculated activation barrier ($\Delta G^{\ddagger}_{\text{cluster}}$) to the isolated molecule ($\Delta G^{\ddagger}_{\text{isolated}}$). The difference provides your first theoretical estimate of whether the protein matrix will structurally stabilize or accidentally destabilize the charged state.
Track 2: Mesoscale Molecular Dynamics (Host-Guest Mechanics)
    • What you already have: The primary storage components of pea protein isolate are well characterized—principally 7S vicilin and 11S legumin. Their full structural coordinate files are completely accessible via the AlphaFold Protein Structure Database.
    • What you can simulate now: You can evaluate the maximum gravimetric loading limit and catalyst shielding before the protein fibrils structurally break down under the weight of the active material.
    • Methodology:
        1. Use molecular docking tools (like AutoDock Vina) to identify favorable binding pockets or interstitial channels within the AlphaFold structures of legumin/vicilin aggregates.
        2. Run classical Molecular Dynamics (MD) simulations using a package like OpenMM or GROMACS with the protein chains embedded with varying mass fractions (e.g., 20%, 40%, 60%) of the pyrimidone guest.
        3. Track the Radial Distribution Function ($g(r)$) of water or hydronium ions relative to the embedded Dewar isomer. This tells you if the dense protein matrix successfully locks out ambient moisture and accidental acid/base triggers, thereby protecting the system from premature discharge.
Track 3: Macro-Scale Continuum Modeling (Device Engineering)
If you compress this composite into a solid-state "heat cartridge," how does the thermal wave actually behave when localized triggering occurs?
Using the exact empirical thermodynamic value from the paper ($1.65\text{ MJ/kg}$) and standard biopolymer transport metrics, we can solve the coupled partial differential equations (PDEs) for heat conduction and chemical depletion using standard Python:
$$\rho C_p \frac{\partial T}{\partial t} = \kappa \frac{\partial^2 T}{\partial x^2} + \dot{q}_{\text{gen}}$$
Here is a complete, ready-to-run 1D Finite Difference simulator. It models a 2 cm solid-state cartridge, accounting for the dead weight of your protein scaffold (set here at a conservative 40% active isomer loading), and tracks the resulting thermal wave propagation over time.




What this script lets you analyze immediately:
    1. The Dilution Penalty: Change ISOMER_MASS_FRACTION. If your MD simulations reveal that you can only achieve a 20% host loading before structural breakdown, you can visualize how much lower the peak output temperature becomes.
    2. Thermal Conductivity Requirements: Biopolymers are notorious thermal insulators ($\sim0.25\text{ W/m·K}$). By tweaking THERMAL_COND, you can see if the heat stalls locally or if it smoothly conducts down the axis to perpetuate a clean, self-sustaining thermal front.



'''


import numpy as np
import matplotlib.pyplot as plt

# --- Physical Inputs (Grounded in Nguyen et al. 2026 & Biopolymer Data) ---
ENERGY_DENSITY_NEAT = 1.65e6  # J/kg (1.65 MJ/kg from the paper)
ISOMER_MASS_FRACTION = 0.40   # 40% isomer loading / 60% pea protein scaffold
ENERGY_DENSITY_COMPOSITE = ENERGY_DENSITY_NEAT * ISOMER_MASS_FRACTION

# Estimated thermal properties of a dense, consolidated protein composite matrix
DENSITY = 1350.0              # kg/m^3
SPECIFIC_HEAT = 1600.0         # J/(kg*K)
THERMAL_COND = 0.30            # W/(m*K)
THERMAL_DIFFUSIVITY = THERMAL_COND / (DENSITY * SPECIFIC_HEAT)

# --- Spatial and Temporal Discretization ---
L = 0.02                      # 2 cm cartridge length
Nx = 100                      # Number of grid points
dx = L / (Nx - 1)
x = np.linspace(0, L, Nx)

Total_time = 15.0             # Simulation time in seconds
dt = 0.0005                   # Time step (must satisfy CFL condition)
Nt = int(Total_time / dt)

# CFL Stability Verification
cfl = THERMAL_DIFFUSIVITY * dt / dx**2
assert cfl < 0.5, f"CFL condition violated: {cfl:.4f}. Reduce dt."

# --- Initial Conditions ---
T = np.ones(Nx) * 298.15          # Ambient start (25 °C / 298.15 K)
fraction_charged = np.ones(Nx)   # Matrix is 100% charged at t=0

# Kinetic trigger rate constant (1/s) when acid catalyst is active
K_TRIGGER = 3.5  

# --- Simulation Loop ---
t_plots = [0.0, 0.5, 1.5, 3.0, 8.0, 15.0]
plt.figure(figsize=(10, 6))

for step in range(Nt):
    T_new = T.copy()
    current_time = step * dt
    
    # Define a propagating trigger boundary or threshold condition.
    # For this simulation, we "inject" the catalyst at the left tip (first 1.5mm),
    # and nearby zones trigger autocatalytically if the local temperature exceeds 55°C (328.15 K)
    rate = np.zeros(Nx)
    rate[(x < 0.0015) | (T > 328.15)] = K_TRIGGER
    
    # Calculate isomer depletion and corresponding volumetric heat generation
    d_fraction = -rate * fraction_charged * dt
    fraction_charged += d_fraction
    
    # Volumetric heat generation source term: q = (d_fraction/dt) * energy_density * density
    Q_gen = (-d_fraction / dt) * ENERGY_DENSITY_COMPOSITE * DENSITY
    
    # Explicit Finite Difference Form for 1D Heat Equation
    for i in range(1, Nx - 1):
        conduction = THERMAL_DIFFUSIVITY * (T[i+1] - 2*T[i] + T[i-1]) / dx**2
        generation = Q_gen[i] / (DENSITY * SPECIFIC_HEAT)
        T_new[i] = T[i] + (conduction + generation) * dt
        
    # Adiabatic / Insulated Boundary Conditions (Neumann)
    T_new[0] = T_new[1]
    T_new[-1] = T_new[-2]
    
    T = T_new.copy()
    
    # Capture snapshot profiles at requested intervals
    if any(np.isclose(current_time, tp, atol=dt/2) for tp in t_plots):
        plt.plot(x * 100, T - 273.15, label=f"t = {current_time:.1f} s")
        t_plots = [tp for tp in t_plots if not np.isclose(current_time, tp, atol=dt/2)]

plt.xlabel('Position Along Cartridge (cm)')
plt.ylabel('Temperature (°C)')
plt.title('Predictive Thermal Wave Propagation via Localized Triggering')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right')
plt.show()