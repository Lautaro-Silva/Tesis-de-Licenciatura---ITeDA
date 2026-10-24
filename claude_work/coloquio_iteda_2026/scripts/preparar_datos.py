"""Prepare the data tables read by PGFPlots in the colloquium slides.

Run from the project root:
    python scripts/preparar_datos.py

Inputs live in data/raw/ (downloaded public data, see fuentes_figuras.md).
Outputs are whitespace-separated tables in data/.
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

# Physical constants (SI)
H_PLANCK = 6.62607015e-34
K_B = 1.380649e-23
C_LIGHT = 2.99792458e8
HBAR = H_PLANCK / (2 * np.pi)
M_E = 9.1093837e-31
EV = 1.602176634e-19


# ---------------------------------------------------------------------------
# 1. COBE/FIRAS monopole spectrum (Fixsen et al. 1996)
# ---------------------------------------------------------------------------
def planck_intensity_mjy(nu_hz, temperature):
    """Planck B_nu in MJy/sr."""
    x = H_PLANCK * nu_hz / (K_B * temperature)
    b_nu = 2 * H_PLANCK * nu_hz**3 / C_LIGHT**2 / np.expm1(x)
    return b_nu / 1e-20  # 1 MJy = 1e-20 W m^-2 Hz^-1


firas = np.loadtxt(RAW / "firas_monopole_spec_v1.txt", comments="#")
wavenumber_cm = firas[:, 0]
frequency_ghz = wavenumber_cm * C_LIGHT * 100 / 1e9
intensity_mjy = firas[:, 1]
residual_kjy = firas[:, 2]
sigma_kjy = firas[:, 3]

firas_table = np.column_stack([frequency_ghz, intensity_mjy, residual_kjy, sigma_kjy])
np.savetxt(OUT / "firas.dat", firas_table, fmt="%.5f",
           header="nu_GHz I_MJysr resid_kJysr sigma_kJysr", comments="")

nu_curve_ghz = np.linspace(10, 700, 300)
curve = planck_intensity_mjy(nu_curve_ghz * 1e9, 2.725)
np.savetxt(OUT / "planck_2725K.dat", np.column_stack([nu_curve_ghz, curve]),
           fmt="%.5f", header="nu_GHz I_MJysr", comments="")


# ---------------------------------------------------------------------------
# 2. Planck 2018 (PR3) TT power spectrum: binned data + best-fit LCDM
# ---------------------------------------------------------------------------
binned = np.loadtxt(RAW / "COM_PowerSpect_CMB-TT-binned_R3.01.txt", comments="#")
np.savetxt(OUT / "planck_tt_binned.dat", binned[:, :4], fmt="%.5f",
           header="ell Dl errlo errhi", comments="")

lowl = np.loadtxt(RAW / "COM_PowerSpect_CMB-TT-full_R3.01.txt", comments="#")
lowl = lowl[lowl[:, 0] < 30]
np.savetxt(OUT / "planck_tt_lowl.dat", lowl[:, :4], fmt="%.5f",
           header="ell Dl errlo errhi", comments="")

theory = np.loadtxt(RAW / "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt",
                    comments="#")
# Keep every ell below 50 and every 5th above, enough for a smooth curve.
ell = theory[:, 0]
keep = (ell < 50) | (ell % 5 == 0)
theory = theory[keep]
np.savetxt(OUT / "planck_theory.dat", theory[:, :5], fmt="%.6e",
           header="ell TT TE EE BB", comments="")


# ---------------------------------------------------------------------------
# 3. Saha ionisation fraction of hydrogen (equilibrium, illustrative)
# ---------------------------------------------------------------------------
T0 = 2.7255          # K, Fixsen 2009
ETA = 6.1e-10        # baryon-to-photon ratio (Planck 2018 / BBN)
Y_HE = 0.245         # primordial helium mass fraction
B_H = 13.6057 * EV   # hydrogen binding energy
ZETA3 = 1.2020569

redshift = np.linspace(500, 2000, 301)
temperature = T0 * (1 + redshift)
n_gamma = 2 * ZETA3 / np.pi**2 * (K_B * temperature / (HBAR * C_LIGHT))**3
n_hydrogen = (1 - Y_HE) * ETA * n_gamma
saha_rhs = (M_E * K_B * temperature / (2 * np.pi * HBAR**2))**1.5 \
    * np.exp(-B_H / (K_B * temperature)) / n_hydrogen
# x^2 / (1 - x) = S  ->  x = (-S + sqrt(S^2 + 4S)) / 2
x_e = (-saha_rhs + np.sqrt(saha_rhs**2 + 4 * saha_rhs)) / 2
np.savetxt(OUT / "saha.dat", np.column_stack([redshift, temperature, x_e]),
           fmt="%.6e", header="z T_K xe", comments="")

half = redshift[np.argmin(np.abs(x_e - 0.5))]
print(f"Saha: x_e = 0.5 at z ~ {half:.0f}, T ~ {T0 * (1 + half):.0f} K "
      f"= {K_B * T0 * (1 + half) / EV:.3f} eV")
print(f"Photons per baryon: {1 / ETA:.2e}")


# ---------------------------------------------------------------------------
# 4. Neutrino effective areas: IceCube EHE (data release) vs HERON (read off)
# ---------------------------------------------------------------------------
# IceCube, 12.6 yr EHE search (arXiv:2507.07497), data release
# doi:10.7910/DVN/JHK49D: all-flavour, 4pi sky-averaged, nu/nubar averaged.
icecube = np.loadtxt(RAW / "icecube_ehe_effective_area_2025.csv", delimiter=",", comments="#")
icecube_energy_ev = icecube[:, 0] * 1e9
icecube_area_km2 = icecube[:, 1] * 1e-6
np.savetxt(OUT / "icecube_aeff.dat", np.column_stack([icecube_energy_ev, icecube_area_km2]),
           fmt="%.4e", header="E_eV A_km2", comments="")

# HERON: instantaneous effective area in its best direction (tau neutrinos),
# READ BY EYE from Kotera et al., arXiv:2507.04382, Fig. 4 left
# ("HERON, topography + standalone"). Approximate, for illustration only.
heron_points = [
    (5.5e16, 0.010), (7.5e16, 0.017), (1.0e17, 0.025), (1.5e17, 0.07),
    (2.5e17, 0.17), (4.0e17, 0.32), (7.0e17, 0.65), (1.2e18, 1.1),
    (2.0e18, 1.5), (4.0e18, 2.2), (1.0e19, 3.2), (2.0e19, 3.8),
    (4.0e19, 4.6), (1.0e20, 5.7),
]
np.savetxt(OUT / "heron_aeff_aprox.dat", np.array(heron_points), fmt="%.4e",
           header="E_eV A_km2", comments="")
