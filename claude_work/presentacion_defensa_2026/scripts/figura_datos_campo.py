"""Field-data azimuthal profile for the defense deck (Phase II, preliminary).

Reproduces the cut and fit of cell 22 of
Scripts/Procesamiento_Datos_Campo/Analisis_Preliminar_DatosCampo_Phase2 (the source of
thesis Fig. 6.4.2), but draws the figure for the talk:
  - no fit result in the legend,
  - "Fase II" in the cuts box,
  - a large semi-transparent PRELIMINAR watermark.

Reads only the needed columns of the Phase II parquet files (read-only).
Usage: venv/bin/python scripts/figura_datos_campo.py
"""
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

PARQUET_DIR = '/home/lsilva/Github/parquet_datos_campo/'
SUBSET = 'PhaseIISPMTPhaseIIBeta'
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figuras',
                      'datos_campo_preliminar.pdf')

COLUMNS = ['is_sd_rejected', 'is_counter_rejected', 'module_status', 'logE_REC',
           'theta_REC', 'r_core', 'phi_plane_sp', 'nMuones_REC']

# --- 1. Load Phase II, same quality mask as the notebook -------------------------------
files = sorted(glob.glob(os.path.join(PARQUET_DIR, '**', f'ADST_{SUBSET}_*.parquet'),
                         recursive=True))
print(f'files found: {len(files)}')
tables = []
for path in files:
    tables.append(pd.read_parquet(path, columns=COLUMNS))
modules = pd.concat(tables, ignore_index=True)

clean = modules.query('not is_sd_rejected and not is_counter_rejected '
                      'and module_status == "candidate"')

# --- 2. Kinematic cuts (thesis headline bin) -------------------------------------------
in_energy = (clean['logE_REC'] >= 18.0) & (clean['logE_REC'] < 18.5)
in_zenith = (clean['theta_REC'] >= 50.0) & (clean['theta_REC'] < 60.0)
in_radius = (clean['r_core'] >= 750) & (clean['r_core'] < 1250)
selected = clean[in_energy & in_zenith & in_radius].copy()
selected['phi_deg'] = np.rad2deg(selected['phi_plane_sp'])
print(f'modules after cuts: {len(selected)}')

# --- 3. Azimuthal profile: 12 bins, mean and standard error of the mean ---------------
phi_edges = np.linspace(-180, 180, 13)
phi_centres = 0.5 * (phi_edges[1:] + phi_edges[:-1])
selected['phi_bin'] = pd.cut(selected['phi_deg'], bins=phi_edges, labels=phi_centres)
profile = selected.groupby('phi_bin', observed=False)['nMuones_REC'].agg(['mean', 'sem', 'count'])
profile = profile.dropna()
profile = profile[profile['count'] > 15]

phi = profile.index.astype(float).values
normalisation = np.nanmean(profile['mean'].values)
density = profile['mean'].values / normalisation
density_error = profile['sem'].values / normalisation


def first_harmonic(phi_deg, a1):
    return 1.0 + a1 * np.cos(np.deg2rad(phi_deg))


parameters, covariance = curve_fit(first_harmonic, phi, density, sigma=density_error,
                                   absolute_sigma=True, bounds=(-2.0, 2.0))
a1 = parameters[0]
a1_error = np.sqrt(covariance[0, 0])
chi2 = np.sum(((density - first_harmonic(phi, a1)) / density_error) ** 2)
print(f'A1 = {a1:.3f} +- {a1_error:.3f}   chi2/ndf = {chi2:.1f}/{len(phi) - 1}')

# --- 4. Figure --------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6.5))

data_style = dict(fmt='o', color='mediumblue', markersize=8, linewidth=2, capsize=4,
                  markeredgecolor='black', label='Datos')
ax.errorbar(phi, density, yerr=density_error, **data_style)

phi_curve = np.linspace(-180, 180, 300)
ax.plot(phi_curve, first_harmonic(phi_curve, a1), '-', color='firebrick', linewidth=2.5,
        label='Ajuste del primer armónico')
ax.axhline(1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.6)

ax.set_xlabel(r'$\phi$ [$^\circ$]', fontsize=18)
ax.set_ylabel(r'$\rho_\mu/\langle\rho_\mu\rangle$', fontsize=18)
ax.set_xlim(-180, 180)
ax.set_xticks(np.arange(-180, 181, 45))
ax.tick_params(labelsize=13)
ax.grid(True, which='major', linestyle='-', alpha=0.5)
ax.grid(True, which='minor', linestyle=':', alpha=0.3)
ax.minorticks_on()
ax.legend(fontsize=14, loc='upper right', framealpha=0.9)

cuts_text = '\n'.join([
    r'$\mathbf{Fase\ II}$',
    r'$18.0 \leq \log_{10}(E_{\mathrm{REC}}/\mathrm{eV}) < 18.5$',
    r'$50^\circ \leq \theta_{\mathrm{REC}} < 60^\circ$',
    r'$750 \leq r < 1250$ m',
])
box_style = dict(boxstyle='round', facecolor='whitesmoke', alpha=0.85, edgecolor='gray')
ax.text(0.03, 0.96, cuts_text, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=box_style)

fig.text(0.53, 0.5, 'PRELIMINAR', fontsize=96, fontweight='bold', color='gray',
         alpha=0.28, rotation=25, ha='center', va='center')

fig.tight_layout()
fig.savefig(OUTPUT)
print(f'saved {os.path.normpath(OUTPUT)}')
