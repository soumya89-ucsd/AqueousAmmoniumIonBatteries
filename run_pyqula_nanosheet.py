# run_pyqula_nanosheet.py
import sys
import numpy as np

print("=========================================================================")
print("  PHASE 1: QUANTUM LATTICE SIMULATION FOR HYBRID ELECTRO-CHEMICAL MATERIALS")
print("=========================================================================")
sys.path.append('quantum-lattice/pysrc')
from pyqula import geometry
print("[SUCCESS] pyqula package successfully located.")



def execute_quantum_analysis():
    # 1. Initialize a 2D Honeycomb Lattice (Electronic analog for your 2D nanosheet)
    print("\n[Step 1] Initializing 2D nanosheet matrix geometry...")
    g = geometry.honeycomb_lattice()
    
    # 2. Compute Baseline Band Structure (Unstrained / State A)
    print("[Step 2] Computing baseline electronic band dispersion...")
    h_base = g.get_hamiltonian()
    nk_points = 40
    k_base, e_base = h_base.get_bands(nk=nk_points)
    
    # 3. Compute Strained Band Structure (Mechanical coupling from photoisomer state B)
    print("[Step 3] Simulating mechanical strain via modified hopping functions...")
    try:
        tij_strained = lambda r1, r2: 1.25
        h_strain = g.get_hamiltonian(tij=tij_strained)
        k_strain, e_strain = h_strain.get_bands(nk=nk_points)
        print("[SUCCESS] Strained Hamiltonian built using custom hopping function.")
    except Exception as e:
        print(f"\n[Note] Spatial hopping function signature bypassed: {e}")
        print("[Fallback] Applying uniform tight-binding scaling theorem...")
        k_strain = k_base
        e_strain = e_base * 1.25

    # 4. Extract Key Physical Metrics for Terminal Feedback
    print("\n=========================================================================")
    print("                        SIMULATION RESULTS ENGINE                        ")
    print("=========================================================================")
    
    # Resolve unique k-points while preserving reciprocal path trajectory order
    _, idx = np.unique(k_base, return_index=True)
    unique_k = k_base[np.sort(idx)]
    n_bands = len(k_base) // len(unique_k)
    
    print(f"Total k-points processed along path: {len(unique_k)}")
    print(f"Number of electronic bands resolved: {n_bands}")
    print(f"Total flat data array tokens:        {len(e_base)}")
    
    print("\n--- BASELINE ENERGY MATRIX SNAPSHOT (First 10 k-points) ---")
    print("Format: k_index | k_coordinate | Valence Band Max (eV) | Conduction Band Min (eV)")
    for i, kv in enumerate(unique_k[:10]):
        # Isolate and sort the eigenvalues corresponding to this specific k-coordinate
        energies_at_k = np.sort(e_base[np.isclose(k_base, kv)])
        mid = len(energies_at_k) // 2
        vbm = energies_at_k[mid - 1] if mid > 0 else energies_at_k[0]
        cbm = energies_at_k[mid] if mid < len(energies_at_k) else energies_at_k[-1]
        print(f"  k={i:02d}  |  k_val={kv:6.4f}  |  VBM: {vbm:7.4f} eV  |  CBM: {cbm:7.4f} eV")
        
    print("\n--- STRAINED ENERGY MATRIX SNAPSHOT (First 10 k-points) ---")
    print("Format: k_index | k_coordinate | Strained VBM (eV) | Strained CBM (eV)")
    _, idx_s = np.unique(k_strain, return_index=True)
    unique_k_strain = k_strain[np.sort(idx_s)]
    for i, kv in enumerate(unique_k_strain[:10]):
        energies_at_k_strain = np.sort(e_strain[np.isclose(k_strain, kv)])
        mid = len(energies_at_k_strain) // 2
        vbm_s = energies_at_k_strain[mid - 1] if mid > 0 else energies_at_k_strain[0]
        cbm_s = energies_at_k_strain[mid] if mid < len(energies_at_k_strain) else energies_at_k_strain[-1]
        print(f"  k={i:02d}  |  k_val={kv:6.4f}  |  VBM: {vbm_s:7.4f} eV  |  CBM: {cbm_s:7.4f} eV")
        
    # Calculate macroscopic quantum bandwidth observables across the entire flat layout
    base_bandwidth = np.max(e_base) - np.min(e_base)
    strain_bandwidth = np.max(e_strain) - np.min(e_strain)
    print("\n--- MACROSCOPIC QUANTUM OBSERVABLES ---")
    print(f"Baseline Total Electronic Bandwidth : {base_bandwidth:.4f} eV")
    print(f"Strained Total Electronic Bandwidth : {strain_bandwidth:.4f} eV")
    print(f"Bandwidth Expansion Delta            : {strain_bandwidth - base_bandwidth:.4f} eV")
    print("=========================================================================")

if __name__ == "__main__":
    execute_quantum_analysis()
