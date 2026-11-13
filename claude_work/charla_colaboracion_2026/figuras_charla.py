"""All data figures of the UMD Foundations Meeting talk, with English labels.

Each figure uses the same data, selections and fits as the thesis code it comes from:
  dense_ring  Dense Ring fit example and A1 vs theta
              (Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py)
  infill      UMD A1(r), UMD vs SD total, SD breakdown, MC geometry (Scripts/plots_seccion_6.py)
  selection   Test 1 (with/without HasStation), Test 2 (muons in excluded/kept tanks) and the
              SD-minus-UMD difference with 95% bands (Scripts/plots_seccion_6.py and
              claude_work/revision_asimetrias_sd_umd/02_notebooks/03_sd_vs_umd/comparar_sd_umd.py)
  core        Core shift Delta r vs phi (Scripts/Cap5_corrimiento_nucleo.py), error bars = SEM
  rec_geometry  A1 with the true and the reconstructed core (thesis Table 6.2.1 and the
              Appendix REC grid), local LDF slope beta, -beta b / r, and A1(r) MC vs REC at 40-50 deg
  backups     English versions of the backup figures: Dense Ring fit quality, counting bias and toy
              model (Scripts/validacion_rec_muones.py), robustness and reconstruction performance
              (presentacion_feb_2026_v2.py), counting reconstruction on the Infill (plots_seccion_6.py)
  field_data  Phase II profile and A1(r) data vs REC-level MC
              (Scripts/Procesamiento_Datos_Campo/Analisis_Asimetria_DatosCampo_Cap7.py estimator)

Usage (repository venv, reads parquet/CSV only, about a minute in total):
    venv/bin/python claude_work/charla_colaboracion_2026/figuras_charla.py            # all
    venv/bin/python claude_work/charla_colaboracion_2026/figuras_charla.py selection  # one block
Writes PDFs into figuras/ and prints the numbers quoted on the slides.

Simulation input: ADST_Alexey_module_v9/ (Dense Ring) and ADST_Alexey_module_v11/ (Infill) under
TALK_MC_ROOT (default ~/Github). Since 31 Oct 2026 both folders are archived in
~/Github/procesado_viejo/ADST_Alexey_module_v{9,11}.tar.gz; extract them anywhere and point
TALK_MC_ROOT there, e.g.  TALK_MC_ROOT=/some/scratch venv/bin/python .../figuras_charla.py
"""
import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "figuras"
REPO = next(p for p in HERE.parents if (p / "Tesis - Latex").is_dir())
SELECTION_DIR = REPO / "claude_work" / "revision_asimetrias_sd_umd"
MC_ROOT = Path(os.environ.get("TALK_MC_ROOT", Path.home() / "Github"))
DENSE_RING_FOLDER = str(MC_ROOT / "ADST_Alexey_module_v9" / "parquet_sib_proton_17") + "/"
INFILL_FOLDER = str(MC_ROOT / "ADST_Alexey_module_v11" / "parquet_sib_proton_17") + "/"

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'xtick.minor.visible': True, 'ytick.minor.visible': True, 'axes.linewidth': 1.2,
    'legend.frameon': True, 'legend.edgecolor': 'black',
    'lines.linewidth': 2, 'lines.markersize': 8, 'xtick.labelsize': 14, 'ytick.labelsize': 14,
})

PHI_EDGES = np.linspace(-180, 180, 13)
PHI_CENTERS = 0.5 * (PHI_EDGES[1:] + PHI_EDGES[:-1])


# =============================================================================
# Helpers
# =============================================================================
def harmonic(phi_deg, a1):
    return 1.0 + a1 * np.cos(np.deg2rad(phi_deg))


def ensure_degrees(series):
    if series.dropna().abs().max() < 7.0:
        return np.rad2deg(series)
    return series


def annotate(ax, lines, y0=0.95, x=0.96, ha='right', fontsize=13):
    colors = ['royalblue', 'purple', 'black', 'dimgray']
    for k, text in enumerate(lines):
        ax.text(x, y0 - 0.07 * k, text, transform=ax.transAxes, fontsize=fontsize, va='top', ha=ha,
                color=colors[min(k, len(colors) - 1)], fontweight='bold')


def save(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("saved", path.name)


def style_r_axis(ax, r_edges, xmax):
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.set_xlabel(r'Distance to the shower axis $r_{\mathrm{MC}}$ [m]', fontsize=15)
    ax.set_ylabel(r'$A_1$', fontsize=16)
    ax.set_xlim(100, xmax)
    ax.set_xticks(r_edges)
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.grid(True, which='minor', linestyle=':', alpha=0.3)


# =============================================================================
# 1. Dense Ring
# =============================================================================
def dense_ring():
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


# =============================================================================
# 2. Infill, MC geometry
# =============================================================================
def load_infill():
    infill = pd.concat([pd.read_parquet(f) for f in glob.glob(INFILL_FOLDER + "*.parquet")],
                       ignore_index=True)
    infill = infill[infill['counterId'] >= 100000].copy()
    euler = ensure_degrees(infill['phi_plane_euler_MC_true_core'])
    infill['phi_MC_Truth'] = ((euler - 180) % 360 + 180) % 360 - 180
    return infill


def a1_vs_r(df, column, r_edges):
    """Chapter 6 estimator: 12 phi bins, mean and SEM per bin, fit 1 + A1 cos(phi)."""
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


def infill():
    data = load_infill()

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
        sel = data[(data['theta_MC'] >= t_min) & (data['theta_MC'] < t_max)]
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

    # 2b, 2c. 30-40 deg: UMD vs SD total, and the SD breakdown. The UMD uses the injected
    # muon number in both, as on the following slides.
    r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
    r_centers = 0.5 * (r_edges[1:] + r_edges[:-1])
    sel = data[(data['theta_MC'] >= 30) & (data['theta_MC'] < 40)]
    curves = {
        'umd': ('nMuones_MC', r'UMD muons ($N_\mu^{\mathrm{MC}}$)', 'mediumblue', 's'),
        'em': ('sd_nEM_MC', 'SD electromagnetic (MC count)', 'darkorange', '^'),
        'sdmu': ('sd_nMuons_MC', 'SD muons (MC count)', 'forestgreen', 'v'),
        'sd': ('sdSignal_REC', 'SD total signal (VEM)', 'firebrick', 'o'),
    }
    results = {key: a1_vs_r(sel, spec[0], r_edges) for key, spec in curves.items()}
    for key, (vals, _) in results.items():
        print(f"  30-40 deg {curves[key][0]}:", np.round(vals, 3))
    for name, keys, ylim in [('Infill_UMD_vs_SD_Total_EN.pdf', ['umd', 'sd'], (-0.12, 0.25)),
                             ('Infill_SD_Breakdown_vs_UMD_EN.pdf', ['umd', 'em', 'sdmu', 'sd'], (-0.15, 0.55))]:
        fig, ax = plt.subplots(figsize=(10, 7))
        for key in keys:
            column, label, color, marker = curves[key]
            vals, errs = results[key]
            ax.errorbar(r_centers, vals, yerr=errs, fmt=f'-{marker}', color=color, label=label,
                        markersize=8, linewidth=2.5, capsize=4, markeredgecolor='black', markeredgewidth=0.5)
        style_r_axis(ax, r_edges, 1400)
        ax.set_ylim(*ylim)
        ax.legend(fontsize=11 if len(keys) > 2 else 12, loc='upper left', framealpha=0.9)
        annotate(ax, ['Proton showers, SIBYLL 2.3e', r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$',
                      'True (MC) geometry'])
        save(fig, name)


# =============================================================================
# 3. Station selection
# =============================================================================
def selection():
    plt.rcParams.update({'xtick.labelsize': 15, 'ytick.labelsize': 15})
    control = pd.read_csv(SELECTION_DIR / "02_notebooks" / "03_sd_vs_umd" / "resultados"
                          / "comparacion_directa.csv")
    r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350])

    # 3a. Test 1
    fig, ax = plt.subplots(figsize=(10, 7))
    for col, err, label, color, fmt, shift in [
            ('A_UMD_original', 'sigma_boot_UMD', r'UMD ($N_\mu^{\mathrm{MC}}$)', 'mediumblue', '-s', -12),
            ('A_SD_antes', 'sigma_boot_SD_antes', 'SD muons (MC count): all stations', 'forestgreen', '-^', 0),
            ('A_SD_despues', 'sigma_boot_SD_despues', 'SD muons (MC count): HasStation only',
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
    annotate(ax, ['Proton showers, SIBYLL 2.3e', r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$',
                  'True (MC) geometry'], fontsize=15)
    save(fig, 'Selection_Test1_EN.pdf')
    row = control[control['r_min'] == 1200].iloc[0]
    print(f"  1200-1350 m: all {row['A_SD_antes']:.3f} +- {row['sigma_boot_SD_antes']:.3f}, "
          f"HasStation {row['A_SD_despues']:.3f} +- {row['sigma_boot_SD_despues']:.3f}")

    # 3b. Backup: SD muons over all stations minus UMD, with pointwise and simultaneous 95% bands
    # (paired shower-level bootstrap of comparar_sd_umd.py).
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.fill_between(control['r_center'], control['delta_antes_sim_low95'], control['delta_antes_sim_high95'],
                    color='forestgreen', alpha=0.15, label='Simultaneous 95% band')
    ax.vlines(control['r_center'], control['delta_antes_low95'], control['delta_antes_high95'],
              color='forestgreen', linewidth=2.5)
    ax.plot(control['r_center'], control['delta_antes_menos_UMD'], '-v', color='forestgreen', markersize=9,
            markeredgecolor='black', markeredgewidth=0.5, linewidth=2,
            label=r'$A_1$(SD muons, all stations) $-$ $A_1$(UMD), pointwise 95% CI')
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.set_xlabel(r'Distance to the shower axis $r_{\mathrm{MC}}$ [m]', fontsize=16)
    ax.set_ylabel(r'$\Delta A_1$ (SD $-$ UMD)', fontsize=16)
    ax.set_xlim(100, 1400)
    ax.set_ylim(-0.16, 0.10)
    ax.set_xticks(r_edges)
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.legend(fontsize=13, loc='upper left', framealpha=0.95)
    annotate(ax, ['Proton showers, SIBYLL 2.3e', r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$'],
             y0=0.16, x=0.04, ha='left', fontsize=14)
    save(fig, 'Selection_Difference_SD_UMD_EN.pdf')
    inner = control[control['r_max'] <= 900]
    print("  SD(all) - UMD, 150-900 m:", inner['delta_antes_menos_UMD'].round(3).tolist(),
          "| 95% CI upper edges:", inner['delta_antes_high95'].round(3).tolist())

    # 3c. Test 2: muons in excluded and kept tanks, 900-1500 m. Each region (early, late) is
    # normalised to all of its tanks, so that excluded + kept add up to 1 within a region and
    # the area of each set of bars is the fraction of tanks lost or kept.
    stations = pd.read_csv(SELECTION_DIR / "04_soporte" / "tablas" / "adst_counts_fast.csv")
    stations['phi_deg'] = np.rad2deg(stations['phi'])
    band = stations[(stations['r'] >= 900) & (stations['r'] < 1500)]
    regions = [('early', np.abs(band['phi_deg']) < 60, 'darkorange', None),
               ('late', np.abs(band['phi_deg']) > 120, 'mediumblue', '//')]
    n_max = 6
    values = np.arange(0, n_max + 1)

    print("  Test 2 table, 900-1500 m:")
    summary = {}
    for name, mask, _, _ in regions:
        region = band[mask]
        kept = region[region['has_rec'] == 1]
        excluded = region[region['has_rec'] == 0]
        summary[name] = {
            'all': region['mu'].mean(), 'kept': kept['mu'].mean(), 'excluded': excluded['mu'].mean(),
            'fraction_kept': len(kept) / len(region), 'excluded_le1': np.mean(excluded['mu'] <= 1),
        }
        print(f"    {name}: <Nmu> all = {summary[name]['all']:.2f}, kept = {summary[name]['kept']:.2f}, "
              f"excluded = {summary[name]['excluded']:.2f}, fraction kept = {summary[name]['fraction_kept']:.2f}, "
              f"excluded with <= 1 mu = {summary[name]['excluded_le1']:.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)
    for ax, (title, has_rec) in zip(axes, [('Excluded tanks (HasStation = False)', 0),
                                           ('Kept tanks (HasStation = True)', 1)]):
        for k, (name, mask, color, hatch) in enumerate(regions):
            region = band[mask]
            tanks = region[region['has_rec'] == has_rec]
            counts = np.clip(tanks['mu'].to_numpy(), 0, n_max)
            fractions = np.array([np.sum(counts == n) for n in values]) / len(region)
            share = len(tanks) / len(region)
            ax.bar(values - 0.2 + 0.4 * k, fractions, width=0.4, color=color, alpha=0.8,
                   edgecolor='black', linewidth=0.6, hatch=hatch,
                   label=f"{name}: {100 * share:.0f}% of its tanks")
        ax.set_title(title, fontsize=17)
        ax.set_xlabel(r'Muons crossing the tank, $N_\mu$ (MC)', fontsize=16)
        ax.set_xticks(values)
        ax.set_xticklabels([str(n) for n in values[:-1]] + [rf'$\geq${n_max}'])
        ax.grid(True, which='major', linestyle='-', alpha=0.5)
        ax.legend(fontsize=15, loc='upper right', framealpha=0.95)
    axes[0].set_ylabel('Fraction of all tanks in the region', fontsize=15)
    axes[0].text(0.96, 0.66, r'$\leq 1\,\mu$: ' + f"{100 * summary['early']['excluded_le1']:.0f}% (early), "
                 f"{100 * summary['late']['excluded_le1']:.0f}% (late)",
                 transform=axes[0].transAxes, fontsize=15, va='top', ha='right', fontweight='bold')
    axes[1].text(0.96, 0.66, r'$900 \leq r < 1500$ m', transform=axes[1].transAxes, fontsize=15,
                 va='top', ha='right', fontweight='bold')
    axes[1].text(0.96, 0.58, r'$30^\circ \leq \theta_{\mathrm{MC}} < 40^\circ$', transform=axes[1].transAxes,
                 fontsize=15, va='top', ha='right', fontweight='bold')
    fig.tight_layout()
    save(fig, 'Selection_Test2_EN.pdf')


# =============================================================================
# 4. Core shift
# =============================================================================
ZENITH_BINS_CORE = [(20, 30), (30, 40), (40, 50)]


def load_infill_stations():
    """One row per SD station per event (the radial distances are station quantities)."""
    columns = ["event_id", "run_number", "theta_MC", "counterId", "sdId", "r_core", "r_core_MC",
               "phi_plane_euler_MC_true_core"]
    modules = pd.concat([pd.read_parquet(p, columns=columns)
                         for p in sorted(glob.glob(INFILL_FOLDER + "*.parquet"))], ignore_index=True)
    stations = modules[modules["counterId"] >= 100000].drop_duplicates(subset=["run_number", "event_id", "sdId"]).copy()
    stations = stations[(stations["r_core"] > 0) & (stations["r_core"] < 1400.0)]
    phi = stations["phi_plane_euler_MC_true_core"].to_numpy(dtype=float)
    if np.nanmax(np.abs(phi)) < 7.0:
        phi = np.rad2deg(phi)
    stations["phi"] = ((phi - 180.0) + 180.0) % 360.0 - 180.0   # validated convention (early at phi = 0)
    stations["delta_r"] = stations["r_core_MC"] - stations["r_core"]
    return stations


def fit_core_shift(stations, edges):
    """Mean and standard error of Delta r per phi bin, and the fit a + b cos(phi) weighted by them."""
    centres = 0.5 * (edges[1:] + edges[:-1])
    grouped = stations.groupby(pd.cut(stations["phi"], edges), observed=False)["delta_r"]
    profile = pd.DataFrame({"phi": centres, "mean": grouped.mean().to_numpy(),
                            "sem": grouped.sem().to_numpy(), "std": grouped.std().to_numpy()})

    def model(phi_deg, a, b):
        return a + b * np.cos(np.deg2rad(phi_deg))

    parameters, covariance = curve_fit(model, profile["phi"], profile["mean"], sigma=profile["sem"],
                                       absolute_sigma=True)
    residuals = (profile["mean"] - model(profile["phi"], *parameters)) / profile["sem"]
    return {"profile": profile, "a": parameters[0], "a_err": np.sqrt(covariance[0, 0]),
            "b": parameters[1], "b_err": np.sqrt(covariance[1, 1]),
            "chi2": float(np.sum(residuals ** 2)), "ndf": len(profile) - 2}


def core():
    plt.rcParams.update({'xtick.labelsize': 15, 'ytick.labelsize': 15})
    stations = load_infill_stations()
    edges = np.linspace(-180.0, 180.0, 19)
    curve_phi = np.linspace(-180.0, 180.0, 361)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), sharey=True)
    for ax, (lo, hi), color, marker in zip(axes, ZENITH_BINS_CORE,
                                           ['tab:blue', 'tab:orange', 'tab:red'], ['o', 's', '^']):
        sub = stations[(stations["theta_MC"] >= lo) & (stations["theta_MC"] < hi) & stations["delta_r"].notna()]
        ax.scatter(sub["phi"], sub["delta_r"], s=2, alpha=0.08, color=color, rasterized=True)
        fit = fit_core_shift(sub, edges)
        profile = fit["profile"]
        ax.errorbar(profile["phi"], profile["mean"], yerr=profile["sem"], color='black',
                    markerfacecolor=color, marker=marker, markersize=7, capsize=2, linewidth=1.0,
                    linestyle='none', label='mean (error bars: SEM)')
        ax.plot(curve_phi, fit["a"] + fit["b"] * np.cos(np.deg2rad(curve_phi)), color='black', linewidth=2,
                linestyle='--', label=r'fit $a + b\cos\phi$')
        ax.text(0.5, 0.86, rf"$b = {fit['b']:.1f} \pm {fit['b_err']:.1f}$ m", transform=ax.transAxes,
                ha='center', va='top', fontsize=16, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='gray'))
        print(f"  core shift {lo}-{hi}: a = {fit['a']:.2f} +- {fit['a_err']:.2f} m, "
              f"b = {fit['b']:.2f} +- {fit['b_err']:.2f} m, chi2/ndf = {fit['chi2']:.1f}/{fit['ndf']}, "
              f"stations = {len(sub)}, mean SEM per bin = {profile['sem'].mean():.2f} m, "
              f"mean spread per bin = {profile['std'].mean():.1f} m")
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
        ax.legend(fontsize=12, framealpha=0.95, loc='lower center')
    axes[0].set_ylabel(r'$\Delta r = r_{\mathrm{MC}} - r_{\mathrm{REC}}$ [m]', fontsize=16)
    fig.tight_layout()
    save(fig, 'Core_Shift_EN.pdf')


# =============================================================================
# 5. Reconstructed geometry: A1 with true and reconstructed core, and -beta b / r
# =============================================================================
def add_geometries(data):
    """Azimuth with respect to the true core (MC) and the reconstructed core (REC), in degrees."""
    euler = ensure_degrees(data['phi_plane_euler_MC_true_core'])
    data['phi_MC_Truth'] = ((euler - 180) % 360 + 180) % 360 - 180
    raw_sp = ensure_degrees(data['phi_plane_sp'])
    phi_rec = ensure_degrees(data['phi_REC'])
    data['phi_REC_plane'] = ((raw_sp + phi_rec) % 360 + 180) % 360 - 180
    return data


def a1_one_cell(cell, phi_column):
    """Chapter 6 estimator on one cell: 12 phi bins, mean and SEM, fit 1 + A1 cos(phi)."""
    cell = cell.copy()
    cell['bin_phi'] = pd.cut(cell[phi_column], bins=PHI_EDGES)
    st = cell.groupby('bin_phi', observed=False)['nMuones_MC'].agg(['mean', 'sem'])
    norm = np.nanmean(st['mean'].values)
    y, yerr = st['mean'].values / norm, st['sem'].values / norm
    ok = ~np.isnan(y) & ~np.isnan(yerr) & (yerr > 0)
    popt, pcov = curve_fit(harmonic, PHI_CENTERS[ok], y[ok], sigma=yerr[ok], absolute_sigma=True,
                           bounds=(-2.0, 2.0))
    return {"A1": popt[0], "A1_err": np.sqrt(pcov[0, 0])}


def local_log_slope(cell_true_distance, r_lo, r_hi, step=25):
    """beta = -d ln<N_mu> / d ln r, from 25 m bins of true distance inside [r_lo, r_hi)."""
    fine = np.arange(r_lo, r_hi + 1, step)
    centres = 0.5 * (fine[1:] + fine[:-1])
    means = cell_true_distance.groupby(pd.cut(cell_true_distance['r_core_MC'], fine),
                                       observed=False)['nMuones_MC'].mean().to_numpy()
    return -np.polyfit(np.log(centres), np.log(means), 1)[0]


def rec_geometry():
    data = add_geometries(load_infill())
    stations = load_infill_stations()
    r_lo, r_hi = 450, 600

    print(f"  Table, UMD injected muons, {r_lo} <= r < {r_hi} m:")
    rows = []
    for lo, hi in ZENITH_BINS_CORE:
        in_zenith = (data['theta_MC'] >= lo) & (data['theta_MC'] < hi)
        sel = data[in_zenith]
        cell_mc = sel[(sel['r_core_MC'] >= r_lo) & (sel['r_core_MC'] < r_hi)]
        cell_rec = sel[(sel['r_core'] >= r_lo) & (sel['r_core'] < r_hi)]
        a1_mc = a1_one_cell(cell_mc, 'phi_MC_Truth')
        a1_rec = a1_one_cell(cell_rec, 'phi_REC_plane')
        a1_rec_true_phi = a1_one_cell(cell_rec, 'phi_MC_Truth')
        a1_true_r_rec_phi = a1_one_cell(cell_mc, 'phi_REC_plane')
        sub_stations = stations[(stations["theta_MC"] >= lo) & (stations["theta_MC"] < hi)
                                & stations["delta_r"].notna()]
        shift = fit_core_shift(sub_stations, np.linspace(-180.0, 180.0, 19))
        beta = local_log_slope(cell_mc, r_lo, r_hi)
        r_eff = 1.0 / np.mean(1.0 / cell_rec['r_core'].to_numpy())
        measured = a1_rec["A1"] - a1_mc["A1"]
        predicted = -beta * shift["b"] / r_eff
        rows.append({"theta": f"{lo}-{hi}", "b_m": shift["b"], "beta": beta, "r_eff_m": r_eff,
                     "A1_MC": a1_mc["A1"], "A1_REC": a1_rec["A1"], "dA1_measured": measured,
                     "dA1_predicted": predicted, "residual": measured - predicted,
                     "A1(r_MC,phi_REC)": a1_true_r_rec_phi["A1"], "A1(r_REC,phi_MC)": a1_rec_true_phi["A1"]})
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    # Candidate figure: A1(r) with the true and the reconstructed core, 40-50 deg.
    r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500])
    r_centers = 0.5 * (r_edges[1:] + r_edges[:-1])
    sel = data[(data['theta_MC'] >= 40) & (data['theta_MC'] < 50)]
    curves = [
        {"r_col": "r_core_MC", "phi_col": "phi_MC_Truth", "label": "true core (MC geometry)",
         "color": "mediumblue", "fmt": "-s", "shift": -10},
        {"r_col": "r_core", "phi_col": "phi_REC_plane", "label": "reconstructed core (REC geometry)",
         "color": "firebrick", "fmt": "-o", "shift": 10},
    ]
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for curve in curves:
        values = []
        errors = []
        for lo_r, hi_r in zip(r_edges[:-1], r_edges[1:]):
            cell = sel[(sel[curve["r_col"]] >= lo_r) & (sel[curve["r_col"]] < hi_r)]
            result = a1_one_cell(cell, curve["phi_col"])
            values.append(result["A1"])
            errors.append(result["A1_err"])
        ax.errorbar(r_centers + curve["shift"], values, yerr=errors, fmt=curve["fmt"], color=curve["color"],
                    label=curve["label"], markersize=8, linewidth=2.5, capsize=4, markeredgecolor='black',
                    markeredgewidth=0.5)
        print(f"  40-50 deg, {curve['label']}:", np.round(values, 3))
    ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.axvspan(450, 600, color='gold', alpha=0.15, linewidth=0)
    ax.text(525, 0.165, '450-600 m:\n0.108 $\\rightarrow$ $-$0.002', ha='center', va='bottom', fontsize=13,
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='goldenrod'))
    ax.set_xlabel(r'Distance to the shower axis $r$ [m]', fontsize=16)
    ax.set_ylabel(r'$A_1$', fontsize=16)
    ax.set_xlim(100, 1550)
    ax.set_ylim(-0.12, 0.32)
    ax.set_xticks(r_edges)
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.legend(fontsize=13, loc='upper left', framealpha=0.95)
    annotate(ax, ['UMD, injected muons', 'Proton showers, SIBYLL 2.3e',
                  r'$40^\circ \leq \theta_{\mathrm{MC}} < 50^\circ$'], y0=0.24, x=0.96, ha='right', fontsize=14)
    save(fig, 'Rec_vs_MC_A1_vs_r_40_50_EN.pdf')


# =============================================================================
# 6. Field data (Chapter 7 estimator: event-level Poisson bootstrap, cos + sin)
# =============================================================================
FIELD_DATA_DIR = Path.home() / "Github" / "parquet_datos_campo"
SUBSET_PHASE_II = "PhaseIISPMTPhaseIIBeta"
N_BOOTSTRAP = 400
RANDOM_SEED = 20261004
FIELD_R_EDGES = np.arange(150, 1651, 150)
FIELD_THETA_EDGES = np.array([0, 10, 20, 30, 40, 50, 55, 65])
GOLDEN_REGION = {"r_lo": 600, "r_hi": 1200, "theta_lo": 20, "theta_hi": 55}
FIELD_MC_SAMPLES = [
    {"key": "sib_proton", "label": "p (SIBYLL 2.3e)", "folder": "parquet_sib_proton_17",
     "color": "#4169e1", "marker": "o", "offset": -24},
    {"key": "sib_helio", "label": "He (SIBYLL 2.3e)", "folder": "parquet_sib_helio_17",
     "color": "#2e8b57", "marker": "^", "offset": -8},
    {"key": "sib_hierro", "label": "Fe (SIBYLL 2.3e)", "folder": "parquet_sib_hierro_17",
     "color": "#b22222", "marker": "s", "offset": 8},
    {"key": "qgs_helio", "label": "He (QGSJET-III)", "folder": "parquet_qgs_helio_17",
     "color": "#e08a00", "marker": "D", "offset": 24},
]
DESIGN_SIN_COS = np.column_stack([np.ones(12), np.cos(np.deg2rad(PHI_CENTERS)), np.sin(np.deg2rad(PHI_CENTERS))])


def weighted_harmonic_fit(bin_means, bin_errors):
    weights = 1.0 / bin_errors ** 2
    normal_matrix = DESIGN_SIN_COS.T @ (DESIGN_SIN_COS * weights[:, None])
    coefficients = np.linalg.solve(normal_matrix, DESIGN_SIN_COS.T @ (weights * bin_means))
    residuals = bin_means - DESIGN_SIN_COS @ coefficients
    return {"a": coefficients[0], "b": coefficients[1], "c": coefficients[2],
            "chi2": float(np.sum(weights * residuals ** 2))}


def fit_cell_bootstrap(phi_deg, signal, event_id, weight, rng, min_events=50):
    """Same estimator as Analisis_Asimetria_DatosCampo_Cap7.fit_cell. None if the cell is unusable."""
    phi_bin = np.clip(np.digitize(phi_deg, PHI_EDGES) - 1, 0, 11)
    event_code, unique_events = pd.factorize(event_id)
    n_events = len(unique_events)
    if n_events < min_events:
        return None
    signal_sum = np.zeros((n_events, 12))
    weight_sum = np.zeros((n_events, 12))
    np.add.at(signal_sum, (event_code, phi_bin), weight * signal)
    np.add.at(weight_sum, (event_code, phi_bin), weight)
    total_weight = weight_sum.sum(axis=0)
    if np.any(total_weight <= 0):
        return None
    bin_means = signal_sum.sum(axis=0) / total_weight
    poisson_counts = rng.poisson(1.0, size=(N_BOOTSTRAP, n_events)).astype(float)
    boot_signal = poisson_counts @ signal_sum
    boot_weight = poisson_counts @ weight_sum
    complete = np.all(boot_weight > 0, axis=1)
    if complete.mean() < 0.9:
        return None
    boot_means = boot_signal[complete] / boot_weight[complete]
    bin_errors = boot_means.std(axis=0, ddof=1)
    if np.any(bin_errors <= 0):
        return None
    fit = weighted_harmonic_fit(bin_means, bin_errors)
    boot_a1 = []
    for replica_means in boot_means:
        replica = weighted_harmonic_fit(replica_means, bin_errors)
        boot_a1.append(replica["b"] / replica["a"])
    return {"A1": fit["b"] / fit["a"], "A1_err": float(np.std(boot_a1, ddof=1)), "B1": fit["c"] / fit["a"],
            "chi2": fit["chi2"], "ndf": 9, "n_events": n_events,
            "bin_means": bin_means / fit["a"], "bin_errors": bin_errors / fit["a"]}


def load_field_data():
    columns = ["event_id", "logE_REC", "theta_REC", "counterId", "nMuones_REC", "module_status", "r_core",
               "phi_plane_sp", "is_sd_rejected", "is_counter_rejected", "subset", "year"]
    pieces = []
    for path in sorted(glob.glob(str(FIELD_DATA_DIR / "**" / "*.parquet"), recursive=True)):
        table = pd.read_parquet(path, columns=columns)
        pieces.append(table[table["logE_REC"] >= 17.5])
    data = pd.concat(pieces, ignore_index=True)
    is_clean = (~data["is_sd_rejected"]) & (~data["is_counter_rejected"]) & (data["module_status"] == "candidate")
    is_commissioning = (data["subset"] == SUBSET_PHASE_II) & (data["year"] == 2022)
    data = data[is_clean & ~is_commissioning & (data["theta_REC"] <= 65.0)].copy()
    data["phi_deg"] = np.rad2deg(data["phi_plane_sp"])
    data["weight"] = 1.0
    return data


def load_field_mc(sample):
    columns = ["event_id", "logE_MC", "logE_REC", "theta_REC", "phi_REC", "counterId", "nMuones_REC",
               "module_status", "phi_plane_sp", "r_core"]
    pieces = []
    for path in sorted(glob.glob(str(MC_ROOT / "ADST_Alexey_module_v11" / sample["folder"] / "*.parquet"))):
        table = pd.read_parquet(path, columns=columns)
        pieces.append(table[table["counterId"] >= 100000])
    mc = pd.concat(pieces, ignore_index=True)
    mc = mc[(mc["theta_REC"] > 0) & mc["logE_REC"].notna() & (mc["module_status"] == "candidate")].copy()
    mc["phi_deg"] = ((ensure_degrees(mc["phi_plane_sp"]) + mc["phi_REC"] + 180.0) % 360.0) - 180.0
    mc["weight"] = 10.0 ** (-2.0 * (mc["logE_MC"] - 17.5))
    return mc


def scan_field_grid(table, sample_key):
    rng = np.random.default_rng(RANDOM_SEED)
    theta_index = np.digitize(table["theta_REC"].to_numpy(), FIELD_THETA_EDGES) - 1
    r_index = np.digitize(table["r_core"].to_numpy(), FIELD_R_EDGES) - 1
    in_grid = ((theta_index >= 0) & (theta_index < len(FIELD_THETA_EDGES) - 1)
               & (r_index >= 0) & (r_index < len(FIELD_R_EDGES) - 1))
    table = table[in_grid].assign(theta_index=theta_index[in_grid], r_index=r_index[in_grid])
    rows = []
    for (t_i, r_i), cell in table.groupby(["theta_index", "r_index"]):
        result = fit_cell_bootstrap(cell["phi_deg"].to_numpy(), cell["nMuones_REC"].to_numpy(dtype=float),
                                    cell["event_id"].to_numpy(), cell["weight"].to_numpy(), rng)
        if result is None:
            continue
        rows.append({"sample": sample_key, "theta_lo": float(FIELD_THETA_EDGES[t_i]),
                     "theta_hi": float(FIELD_THETA_EDGES[t_i + 1]), "r_lo": float(FIELD_R_EDGES[r_i]),
                     "r_hi": float(FIELD_R_EDGES[r_i + 1]), "A1": result["A1"], "A1_err": result["A1_err"]})
    return pd.DataFrame(rows)


def field_data():
    plt.rcParams.update({'xtick.labelsize': 13, 'ytick.labelsize': 13})
    data = load_field_data()
    print(f"  clean field sample: {len(data):,} modules, {data['event_id'].nunique():,} events")

    # 6a. Phase II profile (headline cell of the thesis), event-bootstrap estimator.
    in_cell = ((data["subset"] == SUBSET_PHASE_II) & (data["logE_REC"] >= 18.0) & (data["logE_REC"] < 18.5)
               & (data["theta_REC"] >= 50.0) & (data["theta_REC"] < 60.0)
               & (data["r_core"] >= 750) & (data["r_core"] < 1250))
    cell = data[in_cell]
    fit = fit_cell_bootstrap(cell["phi_deg"].to_numpy(), cell["nMuones_REC"].to_numpy(dtype=float),
                             cell["event_id"].to_numpy(), np.ones(len(cell)), np.random.default_rng(RANDOM_SEED))
    print(f"  Phase II cell: {fit['n_events']} events, A1 = {fit['A1']:.3f} +- {fit['A1_err']:.3f} "
          f"({fit['A1'] / fit['A1_err']:.1f} sigma), B1 = {fit['B1']:.3f}, chi2/ndf = {fit['chi2']:.1f}/{fit['ndf']}")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.errorbar(PHI_CENTERS, fit["bin_means"], yerr=fit["bin_errors"], fmt='o', color='mediumblue', markersize=8,
                linewidth=2, capsize=4, markeredgecolor='black', label='Data (errors: event bootstrap)')
    phi_curve = np.linspace(-180, 180, 300)
    curve = 1 + fit["A1"] * np.cos(np.deg2rad(phi_curve)) + fit["B1"] * np.sin(np.deg2rad(phi_curve))
    fit_label = (rf"Fit: $A_1 = {fit['A1']:.3f} \pm {fit['A1_err']:.3f}$, "
                 rf"$\chi^2/\mathrm{{ndf}} = {fit['chi2']:.1f}/{fit['ndf']}$")
    ax.plot(phi_curve, curve, '-', color='firebrick', linewidth=2.5, label=fit_label)
    ax.axhline(1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.set_xlabel(r'Station azimuth in the shower plane $\phi$ [deg]', fontsize=16)
    ax.set_ylabel(r'$\rho_\mu/\langle\rho_\mu\rangle$', fontsize=17)
    ax.set_xlim(-180, 180)
    ax.set_ylim(0.82, 1.26)
    ax.set_xticks(np.arange(-180, 181, 45))
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.legend(fontsize=13, loc='upper right', framealpha=0.9)
    cuts_text = '\n'.join([r'$\mathbf{Phase\ II}$ (2022 excluded)',
                           r'$18.0 \leq \log_{10}(E_{\mathrm{REC}}/\mathrm{eV}) < 18.5$',
                           r'$50^\circ \leq \theta_{\mathrm{REC}} < 60^\circ$', r'$750 \leq r < 1250$ m'])
    ax.text(0.03, 0.97, cuts_text, transform=ax.transAxes, fontsize=13, va='top',
            bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0.85, edgecolor='gray'))
    fig.text(0.53, 0.5, 'PRELIMINARY', fontsize=80, fontweight='bold', color='gray', alpha=0.25, rotation=25,
             ha='center', va='center')
    fig.tight_layout()
    save(fig, 'FieldData_PhaseII_Profile_EN.pdf')

    # 6b. A1(r) per zenith band, data vs REC-level simulations, 17.5 <= lg E < 18.0.
    main_energy = data[(data["logE_REC"] >= 17.5) & (data["logE_REC"] < 18.0)]
    grids = [scan_field_grid(main_energy, "data")]
    for sample in FIELD_MC_SAMPLES:
        grids.append(scan_field_grid(load_field_mc(sample), sample["key"]))
    grid = pd.concat(grids, ignore_index=True)

    fig, axes = plt.subplots(2, 4, figsize=(17, 8), sharex=True, sharey=True)
    axes = axes.ravel()
    for panel, (theta_lo, theta_hi) in enumerate(zip(FIELD_THETA_EDGES[:-1], FIELD_THETA_EDGES[1:])):
        axis = axes[panel]
        band = grid[(grid["theta_lo"] == theta_lo) & (grid["r_lo"] < 1350)]
        for sample in FIELD_MC_SAMPLES:
            rows = band[band["sample"] == sample["key"]].sort_values("r_lo")
            axis.errorbar(0.5 * (rows["r_lo"] + rows["r_hi"]) + sample["offset"], rows["A1"], yerr=rows["A1_err"],
                          fmt=sample["marker"], color=sample["color"], markersize=5, capsize=2, linestyle="none",
                          alpha=0.85, label=sample["label"])
        data_style = {"fmt": "o", "color": "black", "markersize": 6, "capsize": 3, "linestyle": "none",
                      "label": "Data (Phase I + II)", "zorder": 5}
        if theta_lo >= 55:
            data_style["markerfacecolor"] = "white"
            data_style["label"] = "Data (outside standard calibration)"
        rows = band[band["sample"] == "data"].sort_values("r_lo")
        axis.errorbar(0.5 * (rows["r_lo"] + rows["r_hi"]), rows["A1"], yerr=rows["A1_err"], **data_style)
        axis.axhline(0, color="gray", linewidth=1, linestyle=":")
        is_golden_band = theta_lo >= GOLDEN_REGION["theta_lo"] and theta_hi <= GOLDEN_REGION["theta_hi"]
        if is_golden_band:
            axis.axvspan(GOLDEN_REGION["r_lo"], GOLDEN_REGION["r_hi"], color="gold", alpha=0.15, linewidth=0,
                         label="Region fixed in advance from MC")
        axis.set_title(rf"${theta_lo:.0f}^\circ \leq \theta_{{\mathrm{{REC}}}} < {theta_hi:.0f}^\circ$", fontsize=14)
        axis.set_ylim(-0.15, 0.25)
        if panel >= 4:
            axis.set_xlabel(r"Distance to the reconstructed axis $r$ [m]", fontsize=13)
        if panel % 4 == 0:
            axis.set_ylabel(r"$A_1$", fontsize=14)
    handles, labels = axes[3].get_legend_handles_labels()
    axes[-1].axis("off")
    axes[-1].legend(handles, labels, loc="center", fontsize=12, title=r"$17.5\leq\lg E<18.0$, REC level")
    fig.tight_layout()
    save(fig, 'FieldData_A1_vs_r_EN.pdf')


BLOCKS = {'dense_ring': dense_ring, 'infill': infill, 'selection': selection, 'core': core,
          'rec_geometry': rec_geometry, 'field_data': field_data}


# =============================================================================
# 7. Backup figures (English versions of the thesis figures used in the backup slides)
# =============================================================================
DENSE_RING_ROOT = MC_ROOT / "ADST_Alexey_module_v9"
DENSE_RING_THETA_EDGES = np.rad2deg(np.arcsin(np.sqrt(np.linspace(0.0, np.sin(np.deg2rad(65)) ** 2, 11))))
DENSE_RING_THETA_LABELS = [f"{DENSE_RING_THETA_EDGES[k]:.1f}°–{DENSE_RING_THETA_EDGES[k + 1]:.1f}°" for k in range(10)]


def load_v9(folder, columns):
    files = sorted(glob.glob(str(DENSE_RING_ROOT / folder / "*.parquet")))
    return pd.concat([pd.read_parquet(f, columns=columns) for f in files], ignore_index=True)


def dense_ring_profile_fit(sub, column):
    """12-bin profile of one column, normalised; fit 1 + A1 cos(phi). Returns a dict (or None)."""
    stats = sub.groupby('phi_bin', observed=True)[column].agg(['mean', 'sem']).dropna()
    if len(stats) < 8:
        return None
    norm = stats['mean'].mean()
    y = (stats['mean'] / norm).to_numpy()
    yerr = (stats['sem'] / norm).to_numpy()
    centres = np.array([interval.mid for interval in stats.index])
    popt, pcov = curve_fit(harmonic, centres, y, p0=[0.05], sigma=yerr, absolute_sigma=True)
    chi2 = float(np.sum(((y - harmonic(centres, popt[0])) / yerr) ** 2))
    return {"A1": popt[0], "A1_err": np.sqrt(pcov[0, 0]), "chi2": chi2, "ndf": len(y) - 2}


def add_dense_ring_bins(table):
    table['theta_bin'] = pd.cut(table['theta_REC'], bins=DENSE_RING_THETA_EDGES, labels=False)
    table['phi_deg'] = (np.rad2deg(table['phi_plane_sp']) + 180) % 360 - 180
    table['phi_bin'] = pd.cut(table['phi_deg'], bins=PHI_EDGES)
    return table


def label_box(ax, lines, x=0.96, y0=0.95, ha='right', fontsize=12):
    annotate(ax, lines, y0=y0, x=x, ha=ha, fontsize=fontsize)


def backups():
    plt.rcParams.update({'xtick.labelsize': 13, 'ytick.labelsize': 13})
    columns = ['event_id', 'counterId', 'theta_MC', 'theta_REC', 'phi_MC', 'phi_REC', 'logE_MC', 'logE_REC',
               'nMuones_REC', 'nMuones_MC', 'sdSignal_REC', 'phi_plane_sp']
    proton = load_v9("parquet_sib_proton_17", columns)
    proton = proton.dropna(subset=['theta_REC', 'phi_REC', 'logE_REC'])
    ring = add_dense_ring_bins(proton[(proton['counterId'] >= 90000) & (proton['counterId'] < 100000)].copy())

    # 7a. Fit quality on the Dense Ring (chi2/ndf per zenith bin)
    chi2_rows = []
    for i in range(10):
        sub = ring[ring['theta_bin'] == i]
        row = {"bin": i}
        for column in ['nMuones_MC', 'nMuones_REC', 'sdSignal_REC']:
            fit = dense_ring_profile_fit(sub, column)
            row[column] = fit["chi2"] / fit["ndf"]
        chi2_rows.append(row)
    chi2_table = pd.DataFrame(chi2_rows)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(chi2_table['bin'], chi2_table['nMuones_MC'], 's--', color='forestgreen', markersize=8, lw=2,
            label=r'UMD $N_\mu^{\mathrm{MC}}$')
    ax.plot(chi2_table['bin'], chi2_table['nMuones_REC'], 'o-', color='navy', markersize=8, lw=2,
            label=r'UMD $N_\mu^{\mathrm{REC}}$')
    ax.plot(chi2_table['bin'], chi2_table['sdSignal_REC'], '^-.', color='firebrick', markersize=8, lw=2,
            label='SD total signal')
    ax.axhline(1.0, color='black', lw=2, alpha=0.7, label=r'$\chi^2_\nu = 1$')
    ax.axhline(2.0, color='gray', linestyle='--', lw=1.5, alpha=0.6, label=r'$\chi^2_\nu = 2$')
    ax.set_yscale('log')
    ax.set_ylim(0.1, 15)
    from matplotlib.ticker import ScalarFormatter
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks([0.1, 0.5, 1, 2, 5, 10])
    ax.set_xticks(chi2_table['bin'])
    ax.set_xticklabels(DENSE_RING_THETA_LABELS, rotation=35, ha='right', fontsize=10)
    ax.set_xlabel(r'Zenith angle $\theta_{\mathrm{REC}}$', fontsize=14)
    ax.set_ylabel(r'Reduced $\chi^2$ of the harmonic fit', fontsize=14)
    ax.grid(True, which='major', alpha=0.4)
    ax.legend(fontsize=12, loc='upper left')
    label_box(ax, ['Dense Ring (450 m)', 'Proton showers, SIBYLL 2.3e'], y0=0.20)
    save(fig, 'Backup_Chi2_DenseRing_EN.pdf')
    print("  chi2/ndf UMD MC:", chi2_table['nMuones_MC'].round(2).tolist())
    print("  chi2/ndf SD:", chi2_table['sdSignal_REC'].round(2).tolist())

    # 7b. Directional bias of the muon counting (Dense Ring, theta bins 4-9, about 40-65 deg)
    valid = ring[ring['nMuones_MC'] > 0].copy()
    valid['residual'] = (valid['nMuones_REC'] - valid['nMuones_MC']) / valid['nMuones_MC']
    inclined = valid[valid['theta_bin'] >= 4]
    stats = inclined.groupby('phi_bin', observed=True)['residual'].agg(['mean', 'sem'])
    global_mean = inclined['residual'].mean()
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))
    ax = axes[0]
    ax.errorbar(PHI_CENTERS, stats['mean'], yerr=stats['sem'], fmt='o-', color='crimson', capsize=5, markersize=8,
                markeredgecolor='black', lw=2)
    ax.axhline(0, color='black', lw=1.5, alpha=0.8, label='Unbiased counting')
    ax.axhline(global_mean, color='gray', linestyle='--', lw=2, alpha=0.7, label=rf'Global mean ({global_mean:.3f})')
    ax.set_xlim(-180, 180)
    ax.set_xticks(np.arange(-180, 181, 60))
    ax.set_xlabel(r'$\phi$ in the shower plane [deg] (0 = early)', fontsize=14)
    ax.set_ylabel(r'$\langle (N_\mu^{\mathrm{REC}} - N_\mu^{\mathrm{MC}}) / N_\mu^{\mathrm{MC}} \rangle$', fontsize=14)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=12, loc='upper center')
    label_box(ax, ['Dense Ring (450 m)', r'$\theta_{\mathrm{REC}} \approx 40^\circ$–$65^\circ$'], x=0.04, ha='left',
              y0=0.20)
    print(f"  residual early bin {stats['mean'].iloc[5]:.3f}/{stats['mean'].iloc[6]:.3f}, "
          f"late {stats['mean'].iloc[0]:.3f}, global {global_mean:.3f}")

    # 7c. Toy model: injected muons with a residual drawn per azimuth bin (seed of the thesis notebook)
    all_valid = proton[proton['nMuones_MC'] > 0].copy()
    all_valid['residual'] = (all_valid['nMuones_REC'] - all_valid['nMuones_MC']) / all_valid['nMuones_MC']
    all_valid['phi_bin'] = pd.cut((np.rad2deg(all_valid['phi_plane_sp']) + 180) % 360 - 180, bins=PHI_EDGES)
    residual_bags = {}
    for phi_bin, group in all_valid.groupby('phi_bin', observed=True):
        residual_bags[phi_bin] = group['residual'].dropna().to_numpy()
    np.random.seed(311001)
    ring['nMuones_TOY'] = np.nan
    for phi_bin, group in ring.groupby('phi_bin', observed=True):
        bag = residual_bags.get(phi_bin, np.array([]))
        noise = np.random.choice(bag, size=len(group))
        ring.loc[group.index, 'nMuones_TOY'] = group['nMuones_MC'] * (1 + noise)
    toy_rows = []
    for i in range(10):
        sub = ring[ring['theta_bin'] == i]
        row = {"bin": i}
        for column in ['nMuones_MC', 'nMuones_REC', 'nMuones_TOY']:
            row[column] = dense_ring_profile_fit(sub, column)["A1"]
        toy_rows.append(row)
    toy = pd.DataFrame(toy_rows)
    ax = axes[1]
    ax.plot(toy['bin'], toy['nMuones_MC'], 's--', color='forestgreen', markersize=8, lw=2, label=r'UMD $N_\mu^{\mathrm{MC}}$')
    ax.plot(toy['bin'], toy['nMuones_REC'], 'o-', color='navy', markersize=8, lw=2, label=r'UMD $N_\mu^{\mathrm{REC}}$')
    ax.plot(toy['bin'], toy['nMuones_TOY'], '*:', color='crimson', markersize=12, lw=2.5,
            label=r'Toy: $N_\mu^{\mathrm{MC}}$ + residual drawn per $\phi$ bin')
    ax.set_xticks(toy['bin'])
    ax.set_xticklabels(DENSE_RING_THETA_LABELS, rotation=35, ha='right', fontsize=10)
    ax.set_xlabel(r'Zenith angle $\theta_{\mathrm{REC}}$', fontsize=14)
    ax.set_ylabel(r'$A_1$', fontsize=14)
    ax.set_ylim(0, 0.13)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=11, loc='lower right')
    fig.tight_layout()
    save(fig, 'Backup_Counting_Bias_DenseRing_EN.pdf')
    print("  toy A1:", toy['nMuones_TOY'].round(3).tolist())

    # 7d. Robustness: arrival azimuth (protons, 40-60 deg) and hadronic model (helium)
    dense = proton[(proton['counterId'] < 100000) & (proton['theta_REC'] > 40) & (proton['theta_REC'] < 60)].copy()
    dense['phi_bin'] = pd.cut((np.rad2deg(dense['phi_plane_sp']) + 180) % 360 - 180, bins=PHI_EDGES)
    dense['phi_in'] = ensure_degrees(dense['phi_REC'])
    phi_in_edges = np.linspace(0, 360, 7)
    phi_in_centres = 0.5 * (phi_in_edges[1:] + phi_in_edges[:-1])
    dense['phi_in_bin'] = pd.cut(dense['phi_in'], bins=phi_in_edges, labels=False)
    iso = {'nMuones_REC': ([], []), 'nMuones_MC': ([], [])}
    for b in range(6):
        sub = dense[dense['phi_in_bin'] == b]
        for column in iso:
            fit = dense_ring_profile_fit(sub, column)
            iso[column][0].append(fit["A1"])
            iso[column][1].append(fit["A1_err"])
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))
    ax = axes[0]
    ax.errorbar(phi_in_centres, iso['nMuones_REC'][0], yerr=iso['nMuones_REC'][1], fmt='o-', color='navy', lw=2,
                markersize=8, capsize=4, label=r'UMD $N_\mu^{\mathrm{REC}}$')
    ax.errorbar(phi_in_centres, iso['nMuones_MC'][0], yerr=iso['nMuones_MC'][1], fmt='s--', color='forestgreen', lw=2,
                markersize=8, capsize=4, label=r'UMD $N_\mu^{\mathrm{MC}}$')
    ax.axhline(np.mean(iso['nMuones_REC'][0]), color='navy', linestyle=':', alpha=0.6, lw=2,
               label=f"mean REC: {np.mean(iso['nMuones_REC'][0]):.3f}")
    ax.axhline(np.mean(iso['nMuones_MC'][0]), color='forestgreen', linestyle=':', alpha=0.6, lw=2,
               label=f"mean MC: {np.mean(iso['nMuones_MC'][0]):.3f}")
    ax.set_xlabel(r'Shower arrival azimuth $\phi_{\mathrm{shower}}$ [deg]', fontsize=14)
    ax.set_ylabel(r'$A_1$', fontsize=14)
    ax.set_ylim(0.055, 0.115)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=11, loc='lower right', ncol=2)
    label_box(ax, ['Protons, SIBYLL 2.3e', r'$40^\circ < \theta_{\mathrm{REC}} < 60^\circ$'], x=0.04, ha='left')

    helium_columns = ['counterId', 'theta_REC', 'phi_REC', 'logE_REC', 'nMuones_REC', 'phi_plane_sp']
    helium = {}
    for model, folder in [('SIBYLL 2.3e', 'parquet_sib_helio_17'), ('QGSJET-III', 'parquet_qgs_helio_17')]:
        table = load_v9(folder, helium_columns).dropna(subset=['theta_REC', 'phi_REC', 'logE_REC'])
        table = add_dense_ring_bins(table[(table['counterId'] >= 90000) & (table['counterId'] < 100000)].copy())
        values, errors = [], []
        for i in range(10):
            fit = dense_ring_profile_fit(table[table['theta_bin'] == i], 'nMuones_REC')
            values.append(fit["A1"])
            errors.append(fit["A1_err"])
        helium[model] = (np.array(values), np.array(errors))
    sib, sib_err = helium['SIBYLL 2.3e']
    qgs, qgs_err = helium['QGSJET-III']
    rel_diff = 100 * (sib - qgs) / sib
    rel_err = 100 * np.abs(1.0 / sib) * np.sqrt(qgs_err ** 2 + (qgs / sib) ** 2 * sib_err ** 2)
    axes[1].remove()
    gs = fig.add_gridspec(4, 2)
    ax_top = fig.add_subplot(gs[:3, 1])
    ax_bottom = fig.add_subplot(gs[3, 1], sharex=ax_top)
    bins = np.arange(10)
    ax_top.errorbar(bins, sib, yerr=sib_err, fmt='o-', color='forestgreen', capsize=4, markersize=7, lw=2,
                    label='SIBYLL 2.3e')
    ax_top.errorbar(bins, qgs, yerr=qgs_err, fmt='s--', color='darkorange', capsize=4, markersize=7, lw=2,
                    label='QGSJET-III')
    ax_top.set_ylabel(r'$A_1$ (helium, $N_\mu^{\mathrm{REC}}$)', fontsize=13)
    ax_top.legend(fontsize=11, loc='lower right')
    ax_top.grid(True, alpha=0.4)
    plt.setp(ax_top.get_xticklabels(), visible=False)
    ax_bottom.axhline(0, color='black', linestyle='--', lw=1.2)
    ax_bottom.fill_between(bins, -10, 10, color='gray', alpha=0.2)
    ax_bottom.errorbar(bins, rel_diff, yerr=rel_err, fmt='ko', markersize=5, capsize=3)
    ax_bottom.set_ylim(-25, 25)
    ax_bottom.set_ylabel(r'$\Delta$ [%]', fontsize=12)
    ax_bottom.set_xticks(bins)
    ax_bottom.set_xticklabels(DENSE_RING_THETA_LABELS, rotation=35, ha='right', fontsize=9)
    ax_bottom.set_xlabel(r'Zenith angle $\theta_{\mathrm{REC}}$', fontsize=13)
    fig.tight_layout()
    save(fig, 'Backup_Robustness_EN.pdf')
    print("  isotropy REC:", np.round(iso['nMuones_REC'][0], 3), " helium rel diff %:", np.round(rel_diff, 1))

    # 7e. Reconstruction performance (one row per event)
    events = proton[['event_id', 'logE_MC', 'logE_REC', 'theta_MC', 'theta_REC', 'phi_MC', 'phi_REC']].drop_duplicates()
    panels = [
        {"values": events['logE_REC'] - events['logE_MC'], "range": (-0.5, 0.5), "bins": 60, "color": 'steelblue',
         "xlabel": r'$\Delta \log_{10}E = \log_{10}E_{\mathrm{REC}} - \log_{10}E_{\mathrm{MC}}$', "unit": ""},
        {"values": events['theta_REC'] - events['theta_MC'], "range": (-5, 5), "bins": 80, "color": 'darkorange',
         "xlabel": r'$\Delta\theta = \theta_{\mathrm{REC}} - \theta_{\mathrm{MC}}$ [deg]', "unit": r"$^\circ$"},
        {"values": (events['phi_REC'] - events['phi_MC'] + 180) % 360 - 180, "range": (-10, 10), "bins": 80,
         "color": 'seagreen', "xlabel": r'$\Delta\phi = \phi_{\mathrm{REC}} - \phi_{\mathrm{MC}}$ [deg]', "unit": r"$^\circ$"},
    ]
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for ax, panel in zip(axes, panels):
        values = panel["values"]
        ax.hist(values, bins=panel["bins"], range=panel["range"], color=panel["color"], edgecolor='black',
                linewidth=0.8, alpha=0.75)
        ax.axvline(values.mean(), color='crimson', linestyle='--', lw=2, label='mean')
        ax.axvline(0, color='black', lw=1.5, alpha=0.6)
        ax.text(0.04, 0.95, f"mean {values.mean():.3f}{panel['unit']}\nsd {values.std():.3f}{panel['unit']}",
                transform=ax.transAxes, va='top', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
        ax.set_xlabel(panel["xlabel"], fontsize=13)
        ax.set_ylabel('Events', fontsize=13)
        ax.grid(True, alpha=0.4)
        print(f"  {panel['xlabel'][:20]}: mean {values.mean():.3f}, sd {values.std():.3f}")
    fig.tight_layout()
    save(fig, 'Backup_Reconstruction_EN.pdf')

    # 7f. Muon-counting reconstruction on the Infill (MC geometry, 40-50 deg)
    data = load_infill()
    sel = data[(data['theta_MC'] >= 40) & (data['theta_MC'] < 50)]
    r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1500])
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for column, label, color, fmt in [('nMuones_MC', r'injected ($N_\mu^{\mathrm{MC}}$)', 'forestgreen', '-s'),
                                      ('nMuones_REC', r'reconstructed ($N_\mu^{\mathrm{REC}}$)', 'navy', '-o')]:
        vals, errs = a1_vs_r(sel, column, r_edges)
        ax.errorbar(0.5 * (r_edges[1:] + r_edges[:-1]), vals, yerr=errs, fmt=fmt, color=color, label=label,
                    markersize=8, linewidth=2.5, capsize=4, markeredgecolor='black', markeredgewidth=0.5)
        print(f"  counting {column}:", np.round(vals, 3))
    style_r_axis(ax, r_edges, 1550)
    ax.set_ylim(-0.02, 0.40)
    ax.legend(fontsize=12, loc='upper left')
    annotate(ax, ['UMD', 'Proton showers, SIBYLL 2.3e', r'$40^\circ \leq \theta_{\mathrm{MC}} < 50^\circ$',
                  'True (MC) geometry'])
    save(fig, 'Backup_Counting_Infill_EN.pdf')


BLOCKS['backups'] = backups

if __name__ == "__main__":
    requested = sys.argv[1:] or list(BLOCKS)
    for block in requested:
        print(f"== {block}")
        BLOCKS[block]()
