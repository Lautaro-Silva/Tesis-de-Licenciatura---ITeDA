"""English-labelled, slide-sized versions of the selection and core-shift figures.

Same inputs, selections and fits as the thesis code; only labels, font sizes and layout change:
  - Test 1 (SD muons with/without HasStation) and Test 2 (muons in excluded tanks):
    Scripts/plots_seccion_6.py, reading the CSVs in claude_work/revision_asimetrias_sd_umd/
  - Core shift (Delta r vs phi): Scripts/Cap5_corrimiento_nucleo.py, reading the parquet files
Writes PDFs into ../figuras/ with the suffix _EN and prints the numbers quoted on the slides.
"""
import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "figuras"
REPO = next(p for p in HERE.parents if (p / "Tesis - Latex").is_dir())
SELECTION_DIR = REPO / "claude_work" / "revision_asimetrias_sd_umd"
PARQUET_FOLDER = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/"

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'xtick.minor.visible': True, 'ytick.minor.visible': True, 'axes.linewidth': 1.2,
    'legend.frameon': True, 'legend.edgecolor': 'black',
    'xtick.labelsize': 15, 'ytick.labelsize': 15,
})


def save(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("saved", path.name)


# =============================================================================
# Test 1: SD muon asymmetry over all stations vs HasStation stations
# =============================================================================
control = pd.read_csv(SELECTION_DIR / "02_notebooks" / "03_sd_vs_umd" / "resultados"
                      / "comparacion_directa.csv")
r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
fig, ax = plt.subplots(figsize=(10, 7))
for col, err, label, color, fmt, shift in [
        ('A_UMD_original', 'sigma_boot_UMD', r'UMD ($N_\mu^{\mathrm{MC}}$)', 'mediumblue', '-s', -12),
        ('A_SD_antes', 'sigma_boot_SD_antes', 'SD muons (MC count): all stations', 'forestgreen', '-^', 0),
        ('A_SD_despues', 'sigma_boot_SD_despues', r'SD muons (MC count): HasStation only',
         'forestgreen', '--v', 12)]:
    ax.errorbar(control['r_center'] + shift, control[col], yerr=control[err], fmt=fmt, color=color,
                label=label, markersize=9, linewidth=2.5, capsize=4, markeredgecolor='black',
                markeredgewidth=0.5)
ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8)
ax.set_xlabel(r'Distance to the shower axis $r_{\mathrm{MC}}$ [m]', fontsize=17)
ax.set_ylabel(r'$A_1$', fontsize=18)
ax.set_xlim(100, 1400)
ax.set_ylim(-0.16, 0.26)
ax.set_xticks(r_edges)
ax.grid(True, which='major', linestyle='-', alpha=0.5)
ax.grid(True, which='minor', linestyle=':', alpha=0.3)
ax.legend(fontsize=14, loc='lower left', framealpha=0.95)
for k, (text, color) in enumerate([('Proton showers, SIBYLL 2.3e', 'royalblue'),
                                   (r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$', 'black'),
                                   ('True (MC) geometry', 'dimgray')]):
    ax.text(0.96, 0.95 - 0.07 * k, text, transform=ax.transAxes, fontsize=15, va='top', ha='right',
            color=color, fontweight='bold')
save(fig, 'Selection_Test1_EN.pdf')
row = control[control['r_min'] == 1200].iloc[0]
print(f"  1200-1350 m: all {row['A_SD_antes']:.3f} +- {row['sigma_boot_SD_antes']:.3f}, "
      f"HasStation {row['A_SD_despues']:.3f} +- {row['sigma_boot_SD_despues']:.3f}")

# =============================================================================
# Test 2: muons in excluded (HasStation = False) and kept tanks
# =============================================================================
stations = pd.read_csv(SELECTION_DIR / "04_soporte" / "tablas" / "adst_counts_fast.csv")
stations['phi_deg'] = np.rad2deg(stations['phi'])
early = np.abs(stations['phi_deg']) < 60
late = np.abs(stations['phi_deg']) > 120

far = stations[(stations['r'] >= 1200) & (stations['r'] < 1350)]
for name, region in [('early', early), ('late', late)]:
    sel = far[region.loc[far.index]]
    print(f"  kept fraction 1200-1350 m, {name}: {sel['has_rec'].mean():.2f}")

band = stations[(stations['r'] >= 900) & (stations['r'] < 1500)]
n_max = 6
values = np.arange(0, n_max + 1)
fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)
for ax, (title, has_rec) in zip(axes, [('Excluded tanks (HasStation = False)', 0),
                                       ('Kept tanks (HasStation = True)', 1)]):
    sel = band[band['has_rec'] == has_rec]
    for k, (name, region, color, hatch) in enumerate([('early', early, 'darkorange', None),
                                                      ('late', late, 'mediumblue', '//')]):
        tanks = sel[region.loc[sel.index]]
        counts = np.clip(tanks['mu'].to_numpy(), 0, n_max)
        fractions = np.array([np.mean(counts == n) for n in values])
        ax.bar(values - 0.2 + 0.4 * k, fractions, width=0.4, color=color, alpha=0.8,
               edgecolor='black', linewidth=0.6, hatch=hatch,
               label=rf"{name}: $\langle N_\mu \rangle$ = {tanks['mu'].mean():.2f}")
        print(f"  {title} {name}: N = {len(tanks)}, mean mu = {tanks['mu'].mean():.2f}, "
              f"frac mu<=1 = {np.mean(tanks['mu'] <= 1):.2f}, mean em = {tanks['em'].mean():.1f}")
    ax.set_title(title, fontsize=17)
    ax.set_xlabel(r'Muons crossing the tank, $N_\mu$ (MC)', fontsize=16)
    ax.set_xticks(values)
    ax.set_xticklabels([str(n) for n in values[:-1]] + [rf'$\geq${n_max}'])
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.legend(fontsize=15, loc='upper right', framealpha=0.95)
axes[0].set_ylabel('Fraction of tanks', fontsize=16)
axes[0].text(0.96, 0.66, r'$900 \leq r < 1500$ m', transform=axes[0].transAxes, fontsize=15,
             va='top', ha='right', fontweight='bold')
axes[0].text(0.96, 0.58, r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$', transform=axes[0].transAxes,
             fontsize=15, va='top', ha='right', fontweight='bold')
fig.tight_layout()
save(fig, 'Selection_Test2_EN.pdf')
del stations

# =============================================================================
# Core shift: Delta r = r_MC - r_REC vs true shower-plane azimuth
# =============================================================================
columns = ["event_id", "run_number", "theta_MC", "counterId", "sdId", "r_core", "r_core_MC",
           "phi_plane_euler_MC_true_core"]
modules = pd.concat([pd.read_parquet(p, columns=columns)
                     for p in sorted(glob.glob(PARQUET_FOLDER + "*.parquet"))], ignore_index=True)
st = modules[modules["counterId"] >= 100000].drop_duplicates(subset=["run_number", "event_id", "sdId"]).copy()
st = st[(st["r_core"] > 0) & (st["r_core"] < 1400.0)]
phi = st["phi_plane_euler_MC_true_core"].to_numpy(dtype=float)
if np.nanmax(np.abs(phi)) < 7.0:
    phi = np.rad2deg(phi)
st["phi"] = ((phi - 180.0) + 180.0) % 360.0 - 180.0   # validated convention (early at phi = 0)
st["delta_r"] = st["r_core_MC"] - st["r_core"]

edges = np.linspace(-180.0, 180.0, 19)
centres = 0.5 * (edges[1:] + edges[:-1])
curve_phi = np.linspace(-180.0, 180.0, 361)
fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), sharey=True)
for ax, (lo, hi), color, marker in zip(axes, [(20, 30), (30, 40), (40, 50)],
                                       ['tab:blue', 'tab:orange', 'tab:red'], ['o', 's', '^']):
    sub = st[(st["theta_MC"] >= lo) & (st["theta_MC"] < hi) & st["delta_r"].notna()].copy()
    ax.scatter(sub["phi"], sub["delta_r"], s=2, alpha=0.08, color=color, rasterized=True)
    design = np.column_stack([np.ones(len(sub)), np.cos(np.deg2rad(sub["phi"]))])
    (a, b), *_ = np.linalg.lstsq(design, sub["delta_r"].to_numpy(), rcond=None)
    grouped = sub.groupby(pd.cut(sub["phi"], edges), observed=False)["delta_r"]
    ax.errorbar(centres, grouped.mean().to_numpy(), yerr=grouped.std().to_numpy(), color='black',
                markerfacecolor=color, marker=marker, markersize=7, capsize=2, linewidth=1.0,
                linestyle='none', label=r'mean $\pm 1\sigma$')
    ax.plot(curve_phi, a + b * np.cos(np.deg2rad(curve_phi)), color='black', linewidth=2,
            linestyle='--', label=r'fit $a + b\cos\phi$')
    print(f"  core shift {lo}-{hi}: b = {b:.1f} m")
    ax.axhline(0.0, color='black', linewidth=0.8)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-80, 80)
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.grid(True, alpha=0.3)
    ax.set_title(rf'${lo}^\circ \leq \theta_{{\mathrm{{MC}}}} < {hi}^\circ$', fontsize=17)
    ax.set_xlabel(r'True azimuth $\phi_{\mathrm{MC}}$ [deg]', fontsize=16)
    for x, ha, text in [(0.5, 'center', 'early'), (0.02, 'left', 'late'), (0.98, 'right', 'late')]:
        ax.text(x, 0.97, text, transform=ax.transAxes, ha=ha, va='top', fontsize=14, color='dimgray',
                fontweight='bold')
    ax.legend(fontsize=13, framealpha=0.95, loc='lower center')
axes[0].set_ylabel(r'$\Delta r = r_{\mathrm{MC}} - r_{\mathrm{REC}}$ [m]', fontsize=16)
fig.tight_layout()
save(fig, 'Core_Shift_EN.pdf')
