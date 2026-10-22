"""Proton vs. iron A1 in the Dense Ring, without the significance S (defense deck).

Repeats the computation of the "CÁLCULO MASIVO DE ASIMETRÍA" and "DISCRIMINACIÓN DE MASA"
cells of Scripts/Presentacion_Foundations/presentacion_feb_2026_v2 (source of thesis
Fig. 5.5.1) for SIBYLL 2.3e, 17.5-18.0, proton and iron only, and draws only the two A1
curves. Reads the Dense Ring parquet files read-only.
Usage: venv/bin/python scripts/figura_masa.py
"""
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

ROOT_DIR = '/home/lsilva/Github/ADST_Alexey_module_v9'
FOLDERS = {'Proton': 'parquet_sib_proton_17', 'Hierro': 'parquet_sib_hierro_17'}
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figuras',
                      'Mass_Discrimination_sinS.pdf')
COLUMNS = ['counterId', 'theta_REC', 'phi_REC', 'logE_REC', 'nMuones_REC', 'phi_plane_sp']

# Zenith bins equally spaced in sin^2(theta), 0-65 degrees, as in the notebook
sin2_edges = np.linspace(0.0, np.sin(np.deg2rad(65)) ** 2, 11)
theta_edges = np.rad2deg(np.arcsin(np.sqrt(sin2_edges)))
theta_labels = [f'{theta_edges[k]:.1f}° - {theta_edges[k + 1]:.1f}°' for k in range(10)]
phi_edges = np.linspace(-180, 180, 13)
phi_centres = 0.5 * (phi_edges[:-1] + phi_edges[1:])


def first_harmonic(phi_deg, a1):
    return 1.0 + a1 * np.cos(np.deg2rad(phi_deg))


def fit_a1(stations):
    profile = stations.groupby('phi_bin', observed=False)['nMuones_REC'].agg(['mean', 'sem'])
    keep = profile['mean'].notna().values
    if keep.sum() < 8:
        return np.nan, np.nan
    normalisation = profile['mean'][keep].mean()
    parameters, covariance = curve_fit(first_harmonic, phi_centres[keep],
                                       profile['mean'][keep] / normalisation, p0=[0.05],
                                       sigma=profile['sem'][keep] / normalisation,
                                       absolute_sigma=True)
    return parameters[0], np.sqrt(covariance[0, 0])


results = {}
for primary, folder in FOLDERS.items():
    files = sorted(glob.glob(os.path.join(ROOT_DIR, folder, '*.parquet')))
    stations = pd.concat([pd.read_parquet(f, columns=COLUMNS) for f in files], ignore_index=True)
    stations = stations.dropna(subset=['theta_REC', 'phi_REC', 'logE_REC'])
    dense_ring = stations[(stations['counterId'] >= 90000) & (stations['counterId'] < 100000)].copy()
    dense_ring['theta_bin'] = pd.cut(dense_ring['theta_REC'], bins=theta_edges, labels=False)
    phi_deg = (np.rad2deg(dense_ring['phi_plane_sp']) + 180) % 360 - 180
    dense_ring['phi_bin'] = pd.cut(phi_deg, bins=phi_edges)
    fits = [fit_a1(dense_ring[dense_ring['theta_bin'] == k]) for k in range(10)]
    results[primary] = np.array(fits)
    print(primary, ' '.join(f'{a:.3f}+-{e:.3f}' for a, e in fits))

fig, ax = plt.subplots(figsize=(10, 6))
bins = np.arange(10)
ax.errorbar(bins, results['Proton'][:, 0], yerr=results['Proton'][:, 1], fmt='o-',
            color='royalblue', label=r'Protón ($A=1$)', lw=2.5, markersize=8, capsize=4)
ax.errorbar(bins, results['Hierro'][:, 0], yerr=results['Hierro'][:, 1], fmt='s-',
            color='firebrick', label=r'Hierro ($A=56$)', lw=2.5, markersize=8, capsize=4)
ax.set_xlabel(r'$\theta_{\mathrm{sh}}$', fontsize=16)
ax.set_ylabel(r'$A_1$', fontsize=16)
ax.set_ylim(0, 0.11)
ax.set_xticks(bins)
ax.set_xticklabels(theta_labels, rotation=35, ha='right', fontsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.text(0.99, 0.96, r'$\mathbf{SIB2.3e}$', transform=ax.transAxes, fontsize=14, va='top',
        ha='right', color='purple')
ax.text(0.99, 0.89, r'$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$', transform=ax.transAxes,
        fontsize=12, va='top', ha='right')
ax.legend(loc='upper left', fontsize=13)
ax.grid(True, which='major', linestyle='-', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.minorticks_on()
fig.tight_layout()
fig.savefig(OUTPUT, bbox_inches='tight')
print(f'saved {os.path.normpath(OUTPUT)}')
