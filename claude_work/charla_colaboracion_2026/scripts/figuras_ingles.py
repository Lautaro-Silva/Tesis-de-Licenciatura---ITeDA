"""English-labelled versions of the thesis figures used in the collaboration talk.

Same data, binning and fit as the thesis code; only labels and annotations change:
  - Dense Ring (fit example, A1 vs theta): Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py
  - Infill (A1 vs r, UMD vs SD, SD breakdown): Scripts/plots_seccion_6.py
Writes PDFs into ../figuras/ with the suffix _EN and prints the fitted A1 values so they can be
checked against the thesis figures. Reads only parquet files; runs in the repository venv.
"""
import glob
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

DENSE_RING_FOLDER = "/home/lsilva/Github/ADST_Alexey_module_v9/parquet_sib_proton_17/"
INFILL_FOLDER = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras")

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'xtick.minor.visible': True, 'ytick.minor.visible': True, 'axes.linewidth': 1.2,
    'legend.frameon': True, 'legend.shadow': True, 'legend.edgecolor': 'black',
    'lines.linewidth': 2, 'lines.markersize': 8, 'xtick.labelsize': 14, 'ytick.labelsize': 14,
})

PHI_EDGES = np.linspace(-180, 180, 13)
PHI_CENTERS = 0.5 * (PHI_EDGES[1:] + PHI_EDGES[:-1])


def harmonic(phi_deg, a1):
    return 1.0 + a1 * np.cos(np.deg2rad(phi_deg))


def ensure_degrees(series):
    if series.dropna().abs().max() < 7.0:
        return np.rad2deg(series)
    return series


def annotate(ax, lines, y0=0.95, x=0.96, ha='right'):
    colors = ['royalblue', 'purple', 'black', 'dimgray']
    for k, text in enumerate(lines):
        ax.text(x, y0 - 0.07 * k, text, transform=ax.transAxes, fontsize=13, va='top', ha=ha,
                color=colors[min(k, len(colors) - 1)], fontweight='bold')


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("saved", os.path.relpath(path))


# =============================================================================
# 1. Dense Ring (same as presentacion_feb_2026_v2.py)
# =============================================================================
ring = pd.concat([pd.read_parquet(f, columns=['counterId', 'theta_REC', 'phi_REC', 'logE_REC',
                                                'nMuones_REC', 'nMuones_MC', 'sdSignal_REC',
                                                'phi_plane_sp'])
                  for f in glob.glob(DENSE_RING_FOLDER + "*.parquet")], ignore_index=True)
ring = ring.dropna(subset=['theta_REC', 'phi_REC', 'logE_REC'])
ring = ring[(ring['counterId'] >= 90000) & (ring['counterId'] < 100000)].copy()
s2_bins = np.linspace(0.0, np.sin(np.deg2rad(65)) ** 2, 11)
theta_edges = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
ring['theta_bin'] = pd.cut(ring['theta_REC'], bins=theta_edges, labels=False)
ring['phi_deg'] = (np.rad2deg(ring['phi_plane_sp']) + 180) % 360 - 180
ring['phi_bin'] = pd.cut(ring['phi_deg'], bins=PHI_EDGES)

columns = ['nMuones_REC', 'nMuones_MC', 'sdSignal_REC']
evolution = {col: ([], []) for col in columns}
for i in range(10):
    sub = ring[ring['theta_bin'] == i]
    stats = sub.groupby('phi_bin', observed=True)[columns].agg(['mean', 'sem'])
    for col in columns:
        norm = stats[col]['mean'].mean()
        y, yerr = stats[col]['mean'] / norm, stats[col]['sem'] / norm
        popt, pcov = curve_fit(harmonic, PHI_CENTERS, y, p0=[0.05], sigma=yerr, absolute_sigma=True)
        evolution[col][0].append(popt[0])
        evolution[col][1].append(np.sqrt(pcov[0, 0]))
        if i == 9 and col != 'sdSignal_REC':
            fig, ax = plt.subplots(figsize=(8, 5))
            color = 'navy' if col == 'nMuones_REC' else 'forestgreen'
            ax.errorbar(PHI_CENTERS, y, yerr=yerr, fmt='o', color=color, capsize=5, label='Data')
            x_fit = np.linspace(-180, 180, 200)
            ax.plot(x_fit, harmonic(x_fit, popt[0]), 'k--', lw=2,
                    label=rf'Fit: $A_1 = {popt[0]:.3f} \pm {np.sqrt(pcov[0, 0]):.3f}$')
            ax.set_xlim(-180, 180)
            ax.set_ylim(0.88, 1.13)
            ax.set_xticks(np.arange(-180, 181, 60))
            ax.grid(True, alpha=0.5)
            ax.legend(fontsize=12, loc='upper right')
            symbol = r'N_\mu^{\mathrm{REC}}' if col == 'nMuones_REC' else r'N_\mu^{\mathrm{MC}}'
            ax.set_ylabel(rf'${symbol} / \langle {symbol} \rangle$', fontsize=15)
            ax.set_xlabel(r'Station azimuth in the shower plane $\phi$ [deg]', fontsize=14)
            annotate(ax, ['Dense Ring (450 m)', rf'${theta_edges[9]:.1f}^\circ < \theta < 65^\circ$'],
                     y0=0.16, x=0.5, ha='center')
            suffix = 'REC' if col == 'nMuones_REC' else 'MC'
            save(fig, f'DenseRing_Fit_UMD_{suffix}_EN.pdf')
            print(f"  Dense Ring bin 9 {col}: A1 = {popt[0]:.4f} +- {np.sqrt(pcov[0, 0]):.4f}")

fig, ax = plt.subplots(figsize=(9, 6))
bins = np.arange(10)
for col, label, fmt, color in [('nMuones_REC', r'UMD $N_\mu^{\mathrm{REC}}$', 'o-', 'navy'),
                               ('nMuones_MC', r'UMD $N_\mu^{\mathrm{MC}}$', 's--', 'forestgreen'),
                               ('sdSignal_REC', 'SD total signal (VEM)', '^-.', 'firebrick')]:
    ax.errorbar(bins, evolution[col][0], yerr=evolution[col][1], fmt=fmt, color=color, label=label)
ax.set_xticks(bins)
ax.set_xticklabels([f"{theta_edges[k]:.1f}°–{theta_edges[k + 1]:.1f}°" for k in bins],
                   rotation=35, ha='right', fontsize=10)
ax.set_xlabel(r'Zenith angle $\theta_{\mathrm{REC}}$', fontsize=14)
ax.set_ylabel(r'$A_1$', fontsize=14)
ax.grid(True, alpha=0.5)
ax.legend(fontsize=12, loc='upper left')
annotate(ax, ['Dense Ring (450 m)', 'Proton showers, SIBYLL 2.3e'], y0=0.17, x=0.96)
save(fig, 'DenseRing_A1_vs_Theta_EN.pdf')
for col in columns:
    print(f"  A1 vs theta {col}:", np.round(evolution[col][0], 3))
del ring

# =============================================================================
# 2. Infill (same as plots_seccion_6.py)
# =============================================================================
infill = pd.concat([pd.read_parquet(f) for f in glob.glob(INFILL_FOLDER + "*.parquet")],
                   ignore_index=True)
infill = infill[infill['counterId'] >= 100000].copy()
euler = ensure_degrees(infill['phi_plane_euler_MC_true_core'])
infill['phi_MC_Truth'] = ((euler - 180) % 360 + 180) % 360 - 180


def a1_vs_r(df, column, r_edges):
    values, errors = [], []
    for r_min, r_max in zip(r_edges[:-1], r_edges[1:]):
        sel = df[(df['r_core_MC'] >= r_min) & (df['r_core_MC'] < r_max)].copy()
        a1, err = np.nan, np.nan
        if len(sel.dropna(subset=[column])) >= 15:
            sel['bin_phi'] = pd.cut(sel['phi_MC_Truth'], bins=PHI_EDGES)
            st = sel.groupby('bin_phi', observed=False)[column].agg(['mean', 'sem'])
            norm = np.nanmean(st['mean'].values)
            if norm > 0:
                y, yerr = st['mean'].values / norm, st['sem'].values / norm
                ok = ~np.isnan(y) & ~np.isnan(yerr) & (yerr > 0)
                if ok.sum() >= 5:
                    try:
                        popt, pcov = curve_fit(harmonic, PHI_CENTERS[ok], y[ok], sigma=yerr[ok],
                                               absolute_sigma=True, bounds=(-2.0, 2.0))
                        a1, err = popt[0], np.sqrt(pcov[0, 0])
                        if err > 0.5:
                            a1, err = np.nan, np.nan
                    except RuntimeError:
                        pass
        values.append(a1)
        errors.append(err)
    return np.array(values), np.array(errors)


def style_r_axis(ax, r_edges, xmax):
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.set_xlabel(r'Distance to the shower axis $r_{\mathrm{MC}}$ [m]', fontsize=15)
    ax.set_ylabel(r'$A_1$', fontsize=16)
    ax.set_xlim(100, xmax)
    ax.set_xticks(r_edges)
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', alpha=0.3)


# 2a. A1(r) per zenith bin, UMD injected muons
r_edges_dict = {
    (0, 10): np.array([300, 450, 600, 750, 900, 1050]),
    (10, 20): np.array([300, 450, 600, 750, 900, 1050, 1200]),
    (20, 30): np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350]),
    (30, 40): np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350]),
    (40, 50): np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500]),
    (50, 65): np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500]),
}
fig, ax = plt.subplots(figsize=(12, 7))
colors = plt.cm.viridis(np.linspace(0.1, 0.95, len(r_edges_dict)))
for k, ((t_min, t_max), r_edges) in enumerate(r_edges_dict.items()):
    sel = infill[(infill['theta_MC'] >= t_min) & (infill['theta_MC'] < t_max)]
    vals, errs = a1_vs_r(sel, 'nMuones_MC', r_edges)
    ax.errorbar(0.5 * (r_edges[1:] + r_edges[:-1]), vals, yerr=errs, fmt='-o', color=colors[k],
                label=rf'${t_min}^\circ \leq \theta < {t_max}^\circ$', markersize=8, linewidth=2.5,
                capsize=4, markeredgecolor='black', markeredgewidth=0.5)
    print(f"  A1(r) UMD MC {t_min}-{t_max}:", np.round(vals, 3))
style_r_axis(ax, np.arange(150, 1650, 150), 1550)
ax.set_ylim(-0.02, 0.40)
ax.legend(title=r'Zenith angle ($\theta_{\mathrm{MC}}$)', fontsize=12, title_fontsize=13,
          loc='upper left', framealpha=0.9)
annotate(ax, ['UMD, injected muons', 'Proton showers, SIBYLL 2.3e',
              r'$17.5 \leq \log_{10}(E/\mathrm{eV}) < 18.0$'])
save(fig, 'Infill_UMD_A1_vs_r_MC_EN.pdf')

# 2b. UMD vs SD total, 30-40 deg
r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
r_centers = 0.5 * (r_edges[1:] + r_edges[:-1])
sel = infill[(infill['theta_MC'] >= 30) & (infill['theta_MC'] < 40)]
fig, ax = plt.subplots(figsize=(10, 7))
for column, label, color, marker in [('nMuones_REC', r'UMD muons ($N_\mu^{\mathrm{REC}}$)', 'navy', 'o'),
                                     ('sdSignal_REC', 'SD total signal (VEM)', 'firebrick', '^')]:
    vals, errs = a1_vs_r(sel, column, r_edges)
    ax.errorbar(r_centers, vals, yerr=errs, fmt=f'-{marker}', color=color, label=label,
                markersize=8, linewidth=2.5, capsize=4, markeredgecolor='black', markeredgewidth=0.5)
    print(f"  UMD vs SD {column}:", np.round(vals, 3))
style_r_axis(ax, r_edges, 1400)
ax.set_ylim(-0.12, 0.25)
ax.legend(fontsize=12, loc='upper left', framealpha=0.9)
annotate(ax, ['Proton showers, SIBYLL 2.3e', r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$',
              'True (MC) geometry'], y0=0.95)
save(fig, 'Infill_UMD_vs_SD_Total_EN.pdf')

# 2c. SD breakdown vs UMD, 30-40 deg
fig, ax = plt.subplots(figsize=(10, 7))
for column, label, color, marker in [('nMuones_MC', r'UMD muons ($N_\mu^{\mathrm{MC}}$)', 'mediumblue', 's'),
                                     ('sd_nEM_MC', 'SD electromagnetic (MC count)', 'darkorange', '^'),
                                     ('sd_nMuons_MC', 'SD muons (MC count)', 'forestgreen', 'v'),
                                     ('sdSignal_REC', 'SD total signal (VEM)', 'firebrick', 'o')]:
    vals, errs = a1_vs_r(sel, column, r_edges)
    ax.errorbar(r_centers, vals, yerr=errs, fmt=f'-{marker}', color=color, label=label,
                markersize=8, linewidth=2.5, capsize=4, markeredgecolor='black', markeredgewidth=0.5)
    print(f"  SD breakdown {column}:", np.round(vals, 3))
style_r_axis(ax, r_edges, 1400)
ax.set_ylim(-0.15, 0.55)
ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
annotate(ax, ['Proton showers, SIBYLL 2.3e', r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$',
              'True (MC) geometry'], y0=0.95)
save(fig, 'Infill_SD_Breakdown_vs_UMD_EN.pdf')
