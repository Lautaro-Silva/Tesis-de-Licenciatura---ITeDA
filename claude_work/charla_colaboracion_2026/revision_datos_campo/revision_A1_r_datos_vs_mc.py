# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Review: A1(r) in field data vs simulations
#
# This notebook rebuilds, step by step, the figure `cap7_A1_vs_r_datos_vs_mc.pdf`
# (thesis Fig. 6.4.3; backup slide "A1(r) in field data vs. simulations" of the Foundations talk),
# and the Phase II azimuthal profile (thesis Fig. 6.4.2, A1 = 0.063 ± 0.017), so that every
# ingredient can be checked. It reproduces the code of
# `Scripts/Procesamiento_Datos_Campo/Analisis_Asimetria_DatosCampo_Cap7.py` (sections 1–4 and
# figure 4) and `claude_work/presentacion_defensa_2026/scripts/figura_datos_campo.py`; nothing new
# is assumed.
#
# ## What the figure shows
#
# - **One panel per band of reconstructed zenith angle** θ_REC: 0–10°, 10–20°, 20–30°, 30–40°,
#   40–50°, 50–55° and 55–65°.
# - **x axis:** distance of the station to the shower axis, computed from the **reconstructed**
#   core (`r_core`), in bins of 150 m from 150 m; the figure stops at 1350 m.
# - **y axis:** A1 of the UMD muon number per module in that (θ, r) cell.
# - **Black points:** field data, Phase I + Phase II, 17.5 ≤ lg(E_REC/eV) < 18.0, 6T5, rejected
#   stations and counters removed, only `candidate` modules, Phase II 2022 (commissioning) removed.
#   In the 55–65° panel the points are open because the SD-750 energy calibration is standard only
#   below about 55°.
# - **Coloured points:** simulations processed with the **same reconstruction** (REC level):
#   θ_REC, r from the reconstructed core, azimuth from `GetAzimuthSP()`, reconstructed muon number,
#   and the same HasStation-selected stations. p, He, Fe with SIBYLL 2.3e and He with QGSJET-III.
#   The MC is selected by **true** energy, 17.5 ≤ lg E_MC < 18.0 (the whole library), because the
#   reconstructed MC energy is about 0.14 low; each MC event is weighted by E⁻² so that the sample
#   follows the steep field spectrum within the bin. Points are shifted slightly in r for legibility.
# - **Yellow band:** the "golden region", 600 ≤ r < 1200 m in the panels with 20° ≤ θ < 55°. It
#   was fixed **before looking at the data**, from the Chapter 6 REC-geometry simulations, as the
#   region where the asymmetry survives the reconstruction (the reconstructed core shift washes it
#   out closer to the core). The quoted data-vs-MC numbers average A1 inside it.
#
# ## The estimator in one cell (section 4 below)
#
# 1. Split the modules of the cell into 12 bins of shower-plane azimuth φ.
# 2. In each bin take the (event-weighted) mean muon number per module.
# 3. Fit the 12 means with ρ₀ (1 + A1 cos φ + B1 sin φ) by weighted least squares. B1 must vanish
#    by symmetry, so it is a null test.
# 4. Errors: Poisson bootstrap over **events** (400 replicas), because the modules of one event,
#    and especially the three modules of one counter, are correlated. The same bootstrap gives the
#    error of each bin mean, used as weight and in χ²/ndf.
#
# The Phase II profile of the talk and thesis Fig. 6.4.2 uses a different, simpler estimator
# (standard error of the mean per bin, modules treated as independent). Section 9 compares both.
#
# **Runtime:** reading the field data (about 450 MB, 2300 files) takes a few minutes; the bootstrap
# over the whole grid for data and four MC samples takes a few more. Single process.

# %%
import glob
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "axes.linewidth": 1.2,
    "legend.frameon": True, "legend.edgecolor": "black",
    "xtick.labelsize": 12, "ytick.labelsize": 12, "axes.labelsize": 13,
})

# %% [markdown]
# ## 1. Configuration
#
# The simulation folder `ADST_Alexey_module_v11/` was archived on 31 Oct 2026 in
# `~/Github/procesado_viejo/ADST_Alexey_module_v11.tar.gz`. Extract it somewhere and set `MC_DIR`.

# %%
DATA_DIR = Path.home() / "Github" / "parquet_datos_campo"
MC_DIR = Path(os.environ.get("TALK_MC_ROOT", Path.home() / "Github")) / "ADST_Alexey_module_v11"
OUTPUT_DIR = Path.cwd()

SUBSET_PHASE_I = "PhaseI"
SUBSET_PHASE_II = "PhaseIISPMTPhaseIIBeta"
PHASE_II_COMMISSIONING_YEAR = 2022

MAIN_ENERGY = {"lo": 17.5, "hi": 18.0}
MAX_THETA = 65.0
MAX_THETA_CALIBRATED = 55.0

R_EDGES = np.arange(150, 1651, 150)
THETA_EDGES = np.array([0, 10, 20, 30, 40, 50, 55, 65])
R_MAX_PLOTTED = 1350

GOLDEN_REGION = {"r_lo": 600, "r_hi": 1200, "theta_lo": 20, "theta_hi": 55}

N_PHI_BINS = 12
N_BOOTSTRAP = 400
MIN_EVENTS_PER_CELL = 50
RANDOM_SEED = 20261004

MC_SAMPLES = [
    {"key": "sib_proton", "label": "p (SIBYLL 2.3e)", "folder": "parquet_sib_proton_17",
     "color": "#4169e1", "marker": "o", "offset": -24},
    {"key": "sib_helio", "label": "He (SIBYLL 2.3e)", "folder": "parquet_sib_helio_17",
     "color": "#2e8b57", "marker": "^", "offset": -8},
    {"key": "sib_hierro", "label": "Fe (SIBYLL 2.3e)", "folder": "parquet_sib_hierro_17",
     "color": "#b22222", "marker": "s", "offset": 8},
    {"key": "qgs_helio", "label": "He (QGSJET-III)", "folder": "parquet_qgs_helio_17",
     "color": "#e08a00", "marker": "D", "offset": 24},
]

print("field data:", DATA_DIR, DATA_DIR.is_dir())
print("simulations:", MC_DIR, MC_DIR.is_dir())

# %% [markdown]
# ## 2. Field data
#
# One row per UMD module per event. Only events with lg E_REC ≥ 17.5 are kept in memory: this
# notebook does not need the lower energies. The azimuth `phi_plane_sp` of the field-data parquet
# is the raw `GetAzimuthSP()` (early region at φ = 0).

# %%
DATA_COLUMNS = [
    "event_id", "logE_REC", "theta_REC", "counterId", "nMuones_REC", "module_status",
    "r_core", "phi_plane_sp", "is_sd_rejected", "is_counter_rejected", "subset", "year",
]

data_files = sorted(glob.glob(str(DATA_DIR / "**" / "*.parquet"), recursive=True))
print(len(data_files), "parquet files")

pieces = []
start = time.time()
for index, path in enumerate(data_files):
    table = pd.read_parquet(path, columns=DATA_COLUMNS)
    table = table[table["logE_REC"] >= MAIN_ENERGY["lo"]]
    pieces.append(table)
    if (index + 1) % 500 == 0:
        print(f"  {index + 1} files read ({time.time() - start:.0f} s)")
data_all = pd.concat(pieces, ignore_index=True)
print(f"{len(data_all):,} module rows with lgE >= {MAIN_ENERGY['lo']}")

# %%
# Quality and sample cuts, the same as Chapter 7.
is_clean_module = (
    (~data_all["is_sd_rejected"])
    & (~data_all["is_counter_rejected"])
    & (data_all["module_status"] == "candidate")
)
is_commissioning = (data_all["subset"] == SUBSET_PHASE_II) & (data_all["year"] == PHASE_II_COMMISSIONING_YEAR)
is_in_zenith_range = data_all["theta_REC"] <= MAX_THETA

data_clean = data_all[is_clean_module & ~is_commissioning & is_in_zenith_range].copy()
data_clean["phi_deg"] = np.rad2deg(data_clean["phi_plane_sp"])
data_clean["weight"] = 1.0
print(f"clean sample: {len(data_clean):,} modules, {data_clean['event_id'].nunique():,} events")

# %% [markdown]
# ## 3. Simulations
#
# The Chapter 6 parquet stored `phi_plane_sp = GetAzimuthSP() − φ_REC`, so `phi_plane_sp + φ_REC`
# gives back the raw `GetAzimuthSP()` that the field data store directly. Events whose
# reconstruction failed (θ_REC = 0 sentinel, about 3%) are dropped.

# %%
MC_COLUMNS = [
    "event_id", "logE_MC", "logE_REC", "theta_REC", "phi_REC", "counterId",
    "nMuones_REC", "module_status", "phi_plane_sp", "r_core",
]


def to_degrees(series):
    """Some parquet columns are stored in radians, others in degrees."""
    if series.dropna().abs().max() < 7.0:
        return np.rad2deg(series)
    return series


def wrap_degrees(angle_deg):
    return (angle_deg + 180.0) % 360.0 - 180.0


def load_mc_sample(sample):
    files = sorted(glob.glob(str(MC_DIR / sample["folder"] / "*.parquet")))
    pieces = []
    for path in files:
        table = pd.read_parquet(path, columns=MC_COLUMNS)
        pieces.append(table[table["counterId"] >= 100000])
    mc = pd.concat(pieces, ignore_index=True)

    is_reconstructed = (mc["theta_REC"] > 0) & mc["logE_REC"].notna()
    is_candidate = mc["module_status"] == "candidate"
    mc = mc[is_reconstructed & is_candidate].copy()

    mc["phi_deg"] = wrap_degrees(to_degrees(mc["phi_plane_sp"]) + mc["phi_REC"])
    mc["weight"] = 10.0 ** (-2.0 * (mc["logE_MC"] - 17.5))   # E^-1 library -> E^-3 spectrum
    return mc


mc_by_sample = {}
for sample in MC_SAMPLES:
    mc_by_sample[sample["key"]] = load_mc_sample(sample)
    n_events = mc_by_sample[sample["key"]]["event_id"].nunique()
    print(f"{sample['label']:>18}: {n_events:,} events")

# %% [markdown]
# ## 4. The estimator
#
# `fit_cell` returns a dictionary with named fields. `bin_means` and `bin_errors` are normalised
# to the fitted ρ₀, so the profile can be drawn directly against 1 + A1 cos φ + B1 sin φ.

# %%
PHI_EDGES = np.linspace(-180.0, 180.0, N_PHI_BINS + 1)
PHI_CENTERS = 0.5 * (PHI_EDGES[1:] + PHI_EDGES[:-1])
PHI_RADIANS = np.deg2rad(PHI_CENTERS)
DESIGN = np.column_stack([np.ones(N_PHI_BINS), np.cos(PHI_RADIANS), np.sin(PHI_RADIANS)])


def weighted_harmonic_fit(bin_means, bin_errors):
    """Weighted least squares of a + b cos(phi) + c sin(phi). Returns the coefficients and chi2."""
    weights = 1.0 / bin_errors ** 2
    normal_matrix = DESIGN.T @ (DESIGN * weights[:, None])
    coefficients = np.linalg.solve(normal_matrix, DESIGN.T @ (weights * bin_means))
    residuals = bin_means - DESIGN @ coefficients
    chi2 = float(np.sum(weights * residuals ** 2))
    return {"a": coefficients[0], "b": coefficients[1], "c": coefficients[2], "chi2": chi2}


def fit_cell(phi_deg, signal, event_id, weight, rng):
    """First-harmonic fit of one cell with an event-level Poisson bootstrap. None if unusable."""
    phi_bin = np.clip(np.digitize(phi_deg, PHI_EDGES) - 1, 0, N_PHI_BINS - 1)
    event_code, unique_events = pd.factorize(event_id)
    n_events = len(unique_events)
    if n_events < MIN_EVENTS_PER_CELL:
        return None

    # Per-event, per-phi-bin sums: the bootstrap then only needs a matrix product.
    signal_sum = np.zeros((n_events, N_PHI_BINS))
    weight_sum = np.zeros((n_events, N_PHI_BINS))
    np.add.at(signal_sum, (event_code, phi_bin), weight * signal)
    np.add.at(weight_sum, (event_code, phi_bin), weight)
    total_weight = weight_sum.sum(axis=0)
    if np.any(total_weight <= 0):
        return None
    bin_means = signal_sum.sum(axis=0) / total_weight

    poisson_counts = rng.poisson(1.0, size=(N_BOOTSTRAP, n_events)).astype(float)
    boot_signal = poisson_counts @ signal_sum
    boot_weight = poisson_counts @ weight_sum
    replica_is_complete = np.all(boot_weight > 0, axis=1)
    if replica_is_complete.mean() < 0.9:
        return None
    boot_means = boot_signal[replica_is_complete] / boot_weight[replica_is_complete]
    bin_errors = boot_means.std(axis=0, ddof=1)
    if np.any(bin_errors <= 0):
        return None

    fit = weighted_harmonic_fit(bin_means, bin_errors)
    boot_a1 = []
    boot_b1 = []
    for replica_means in boot_means:
        replica_fit = weighted_harmonic_fit(replica_means, bin_errors)
        boot_a1.append(replica_fit["b"] / replica_fit["a"])
        boot_b1.append(replica_fit["c"] / replica_fit["a"])

    ndf = N_PHI_BINS - 3
    return {
        "A1": fit["b"] / fit["a"], "A1_err": float(np.std(boot_a1, ddof=1)),
        "B1": fit["c"] / fit["a"], "B1_err": float(np.std(boot_b1, ddof=1)),
        "chi2": fit["chi2"], "ndf": ndf, "chi2_ndf": fit["chi2"] / ndf,
        "n_events": n_events, "n_modules": len(signal),
        "bin_means": bin_means / fit["a"], "bin_errors": bin_errors / fit["a"],
    }


# %% [markdown]
# ## 5. Scan the grid
#
# `scan_grid` fits every (θ, r) cell of a table and returns one row per cell. The profile of each
# cell is kept in a separate dictionary, so that any cell can be plotted in section 7.

# %%
def scan_grid(table, sample_key):
    rng = np.random.default_rng(RANDOM_SEED)
    theta_index = np.digitize(table["theta_REC"].to_numpy(), THETA_EDGES) - 1
    r_index = np.digitize(table["r_core"].to_numpy(), R_EDGES) - 1
    in_grid = (theta_index >= 0) & (theta_index < len(THETA_EDGES) - 1) & (r_index >= 0) & (r_index < len(R_EDGES) - 1)
    table = table[in_grid].assign(theta_index=theta_index[in_grid], r_index=r_index[in_grid])

    rows = []
    profiles = {}
    for (t_i, r_i), cell in table.groupby(["theta_index", "r_index"]):
        result = fit_cell(cell["phi_deg"].to_numpy(), cell["nMuones_REC"].to_numpy(dtype=float),
                          cell["event_id"].to_numpy(), cell["weight"].to_numpy(), rng)
        if result is None:
            continue
        theta_lo = float(THETA_EDGES[t_i])
        r_lo = float(R_EDGES[r_i])
        rows.append({
            "sample": sample_key,
            "theta_lo": theta_lo, "theta_hi": float(THETA_EDGES[t_i + 1]),
            "r_lo": r_lo, "r_hi": float(R_EDGES[r_i + 1]),
            "A1": result["A1"], "A1_err": result["A1_err"],
            "B1": result["B1"], "B1_err": result["B1_err"],
            "chi2_ndf": result["chi2_ndf"], "n_events": result["n_events"], "n_modules": result["n_modules"],
        })
        profiles[(theta_lo, r_lo)] = result
    return pd.DataFrame(rows), profiles


in_main_energy = (data_clean["logE_REC"] >= MAIN_ENERGY["lo"]) & (data_clean["logE_REC"] < MAIN_ENERGY["hi"])
data_main = data_clean[in_main_energy]

start = time.time()
grid_data, profiles_data = scan_grid(data_main, "data")
print(f"data: {len(grid_data)} cells ({time.time() - start:.0f} s)")

grids_mc = []
profiles_mc = {}
for sample in MC_SAMPLES:
    start = time.time()
    grid, profiles = scan_grid(mc_by_sample[sample["key"]], sample["key"])
    grids_mc.append(grid)
    profiles_mc[sample["key"]] = profiles
    print(f"{sample['key']}: {len(grid)} cells ({time.time() - start:.0f} s)")
grid_mc = pd.concat(grids_mc, ignore_index=True)

# %% [markdown]
# ## 6. The figure (English labels)

# %%
def plot_a1_vs_r(axis, grid, sample_key, style, offset):
    rows = grid[(grid["sample"] == sample_key) & (grid["r_lo"] < R_MAX_PLOTTED)].sort_values("r_lo")
    r_center = 0.5 * (rows["r_lo"] + rows["r_hi"]) + offset
    axis.errorbar(r_center, rows["A1"], yerr=rows["A1_err"], **style)


theta_bands = list(zip(THETA_EDGES[:-1], THETA_EDGES[1:]))
figure, axes = plt.subplots(2, 4, figsize=(17, 8), sharex=True, sharey=True)
axes = axes.ravel()
for panel_index, (theta_lo, theta_hi) in enumerate(theta_bands):
    axis = axes[panel_index]
    band_data = grid_data[grid_data["theta_lo"] == theta_lo]
    band_mc = grid_mc[grid_mc["theta_lo"] == theta_lo]

    for sample in MC_SAMPLES:
        mc_style = {"fmt": sample["marker"], "color": sample["color"], "markersize": 5, "capsize": 2,
                    "linestyle": "none", "alpha": 0.85, "label": sample["label"]}
        plot_a1_vs_r(axis, band_mc, sample["key"], mc_style, sample["offset"])

    data_style = {"fmt": "o", "color": "black", "markersize": 6, "capsize": 3, "linestyle": "none",
                  "label": "Data (Phase I + II)", "zorder": 5}
    if theta_lo >= MAX_THETA_CALIBRATED:
        data_style["markerfacecolor"] = "white"
        data_style["label"] = "Data (outside standard calibration)"
    plot_a1_vs_r(axis, band_data, "data", data_style, 0)

    axis.axhline(0, color="gray", linewidth=1, linestyle=":")
    is_golden_band = theta_lo >= GOLDEN_REGION["theta_lo"] and theta_hi <= GOLDEN_REGION["theta_hi"]
    if is_golden_band:
        axis.axvspan(GOLDEN_REGION["r_lo"], GOLDEN_REGION["r_hi"], color="gold", alpha=0.12, linewidth=0,
                     label="Golden region (fixed from MC)")
    axis.set_title(rf"${theta_lo:.0f}^\circ \leq \theta_{{\mathrm{{REC}}}} < {theta_hi:.0f}^\circ$", fontsize=12)
    axis.set_ylim(-0.15, 0.25)
    if panel_index >= 4:
        axis.set_xlabel(r"Distance to the reconstructed axis $r$ [m]")
    if panel_index % 4 == 0:
        axis.set_ylabel(r"$A_1$")

handles, labels = axes[3].get_legend_handles_labels()
axes[-1].axis("off")
axes[-1].legend(handles, labels, loc="center", fontsize=11, title=r"$17.5\leq\lg E<18.0$")
figure.tight_layout()
figure.savefig(OUTPUT_DIR / "A1_vs_r_data_vs_mc_EN.pdf", dpi=200, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 7. Look at the fits cell by cell
#
# The table lists every data cell: A1 with its bootstrap error, the null-test B1, χ²/ndf of the
# weighted fit (ndf = 12 − 3 = 9) and the number of events. A χ²/ndf well above 1 means the
# first harmonic does not describe the profile within the bootstrap errors.

# %%
columns_to_show = ["theta_lo", "r_lo", "A1", "A1_err", "B1", "B1_err", "chi2_ndf", "n_events"]
grid_data[columns_to_show].round(3)

# %%
cells_with_high_chi2 = grid_data[grid_data["chi2_ndf"] > 2.0]
print(f"data cells with chi2/ndf > 2: {len(cells_with_high_chi2)} of {len(grid_data)}")
cells_with_high_chi2[columns_to_show].round(3)


# %%
def plot_cell_profile(theta_lo, r_lo):
    """Draw the azimuthal profile of one data cell with its fit, and the proton MC fit."""
    data_profile = profiles_data[(theta_lo, r_lo)]
    figure, axis = plt.subplots(figsize=(7.5, 4.8))
    axis.errorbar(PHI_CENTERS, data_profile["bin_means"], yerr=data_profile["bin_errors"], fmt="o",
                  color="black", capsize=3, label="Data")

    phi_smooth = np.linspace(-180, 180, 300)
    data_curve = (1 + data_profile["A1"] * np.cos(np.deg2rad(phi_smooth))
                  + data_profile["B1"] * np.sin(np.deg2rad(phi_smooth)))
    data_label = (rf"data fit: $A_1 = {data_profile['A1']:.3f} \pm {data_profile['A1_err']:.3f}$, "
                  rf"$\chi^2/\mathrm{{ndf}} = {data_profile['chi2']:.1f}/{data_profile['ndf']}$")
    axis.plot(phi_smooth, data_curve, color="black", linewidth=1.6, label=data_label)

    proton_profiles = profiles_mc["sib_proton"]
    if (theta_lo, r_lo) in proton_profiles:
        proton = proton_profiles[(theta_lo, r_lo)]
        proton_curve = 1 + proton["A1"] * np.cos(np.deg2rad(phi_smooth))
        axis.plot(phi_smooth, proton_curve, color="#4169e1", linestyle="--",
                  label=rf"p MC: $A_1 = {proton['A1']:.3f} \pm {proton['A1_err']:.3f}$")

    axis.axhline(1, color="gray", linewidth=1, linestyle=":")
    axis.set_xlim(-180, 180)
    axis.set_xticks(np.arange(-180, 181, 60))
    axis.set_xlabel(r"$\phi$ in the shower plane [deg]")
    axis.set_ylabel(r"$\langle N_\mu^{\mathrm{REC}}\rangle_\phi / \rho_0$")
    theta_hi = THETA_EDGES[np.searchsorted(THETA_EDGES, theta_lo) + 1]
    axis.set_title(rf"${theta_lo:.0f}^\circ \leq \theta < {theta_hi:.0f}^\circ$, "
                   rf"${r_lo:.0f} \leq r < {r_lo + 150:.0f}$ m", fontsize=12)
    axis.legend(fontsize=9, loc="upper left")
    figure.tight_layout()
    plt.show()


# Cells of the golden region, 30-40 deg (change the arguments to look at any other cell).
for r_lo in [600.0, 750.0, 900.0, 1050.0]:
    plot_cell_profile(30.0, r_lo)

# %% [markdown]
# ## 8. χ²/ndf over the whole grid, data and simulations
#
# If the bootstrap errors are right and the first harmonic is adequate, χ²/ndf should scatter
# around 1 (for ndf = 9, the central 90% of a χ² distribution lies between 0.37 and 1.88).

# %%
figure, axis = plt.subplots(figsize=(7.5, 4.5))
chi2_bins = np.linspace(0, 5, 26)
axis.hist(grid_data["chi2_ndf"], bins=chi2_bins, histtype="step", linewidth=2, color="black", label="data")
for sample in MC_SAMPLES:
    sample_rows = grid_mc[grid_mc["sample"] == sample["key"]]
    axis.hist(sample_rows["chi2_ndf"], bins=chi2_bins, histtype="step", linewidth=1.4, color=sample["color"],
              label=sample["label"])
axis.axvline(1, color="gray", linestyle=":")
axis.set_xlabel(r"$\chi^2/\mathrm{ndf}$ of the cell fit")
axis.set_ylabel("cells")
axis.legend(fontsize=9)
figure.tight_layout()
plt.show()

grids_to_summarise = {"data": grid_data}
for sample in MC_SAMPLES:
    grids_to_summarise[sample["key"]] = grid_mc[grid_mc["sample"] == sample["key"]]

summary_rows = []
for sample_key, grid in grids_to_summarise.items():
    summary_rows.append({"sample": sample_key, "cells": len(grid),
                         "median chi2/ndf": grid["chi2_ndf"].median(),
                         "fraction > 2": (grid["chi2_ndf"] > 2).mean()})
pd.DataFrame(summary_rows).round(3)

# %% [markdown]
# ## 9. The Phase II profile of the talk (thesis Fig. 6.4.2)
#
# Cell: Phase II, 18.0 ≤ lg E_REC < 18.5, 50° ≤ θ_REC < 60°, 750 ≤ r < 1250 m (the values used by
# the code, the abstract and the conclusions; the caption of thesis Fig. 6.4.2 says 40–60° and
# 750–1050 m, which is a typo in the caption).
#
# Three error estimates for the same cell:
# - **(a) as in the figure:** standard error of the mean per φ bin, modules treated as
#   independent, curve_fit with absolute errors. This gave A1 = 0.063 ± 0.017, χ² = 15.5/11.
# - **(b) scaled:** (a) with the error multiplied by √(χ²/ndf), the usual correction when the
#   fit quality says the errors are too small.
# - **(c) event bootstrap:** the estimator of sections 4–5 (with the sin term), which resamples
#   whole events and therefore includes the correlation between modules of one shower.
#
# Note: the script that drew the talk and thesis figure did **not** remove the Phase II 2022
# commissioning period. In this cell that adds 17 events (36 modules): with them (a) gives
# A1 = 0.0627 ± 0.0167, χ² = 15.5/11, the numbers quoted so far; without them, as here,
# A1 = 0.0623 ± 0.0168, χ² = 16.5/11. The difference is negligible, but the sample should be
# the one the thesis text describes (2022 excluded).

# %%
in_phase_ii_cell = (
    (data_clean["subset"] == SUBSET_PHASE_II)
    & (data_clean["logE_REC"] >= 18.0) & (data_clean["logE_REC"] < 18.5)
    & (data_clean["theta_REC"] >= 50.0) & (data_clean["theta_REC"] < 60.0)
    & (data_clean["r_core"] >= 750) & (data_clean["r_core"] < 1250)
)
phase_ii_cell = data_clean[in_phase_ii_cell].copy()
print(f"Phase II cell: {len(phase_ii_cell)} modules, {phase_ii_cell['event_id'].nunique()} events")

# (a) The estimator of the figure.
phase_ii_cell["phi_bin"] = pd.cut(phase_ii_cell["phi_deg"], bins=PHI_EDGES, labels=PHI_CENTERS)
profile_sem = phase_ii_cell.groupby("phi_bin", observed=False)["nMuones_REC"].agg(["mean", "sem", "count"])
profile_sem = profile_sem.dropna()
profile_sem = profile_sem[profile_sem["count"] > 15]
phi_values = profile_sem.index.astype(float).to_numpy()
normalisation = np.nanmean(profile_sem["mean"].to_numpy())
density = profile_sem["mean"].to_numpy() / normalisation
density_error = profile_sem["sem"].to_numpy() / normalisation


def first_harmonic(phi_deg, a1):
    return 1.0 + a1 * np.cos(np.deg2rad(phi_deg))


parameters, covariance = curve_fit(first_harmonic, phi_values, density, sigma=density_error,
                                   absolute_sigma=True, bounds=(-2.0, 2.0))
a1_sem = parameters[0]
a1_sem_error = np.sqrt(covariance[0, 0])
chi2_sem = np.sum(((density - first_harmonic(phi_values, a1_sem)) / density_error) ** 2)
ndf_sem = len(phi_values) - 1

# (b) Scaled by sqrt(chi2/ndf).
scale = np.sqrt(chi2_sem / ndf_sem)
a1_scaled_error = a1_sem_error * max(scale, 1.0)

# (c) Event bootstrap.
bootstrap_fit = fit_cell(phase_ii_cell["phi_deg"].to_numpy(), phase_ii_cell["nMuones_REC"].to_numpy(dtype=float),
                         phase_ii_cell["event_id"].to_numpy(), np.ones(len(phase_ii_cell)),
                         np.random.default_rng(RANDOM_SEED))

comparison = pd.DataFrame([
    {"estimate": "(a) SEM per bin, modules independent", "A1": a1_sem, "A1_err": a1_sem_error,
     "chi2/ndf": f"{chi2_sem:.1f}/{ndf_sem}"},
    {"estimate": "(b) (a) scaled by sqrt(chi2/ndf)", "A1": a1_sem, "A1_err": a1_scaled_error,
     "chi2/ndf": f"{chi2_sem:.1f}/{ndf_sem}"},
    {"estimate": "(c) event bootstrap, cos + sin", "A1": bootstrap_fit["A1"], "A1_err": bootstrap_fit["A1_err"],
     "chi2/ndf": f"{bootstrap_fit['chi2']:.1f}/{bootstrap_fit['ndf']}"},
])
comparison["significance (A1/err)"] = comparison["A1"] / comparison["A1_err"]
comparison.round(3)

# %%
figure, axis = plt.subplots(figsize=(8, 5))
axis.errorbar(phi_values, density, yerr=density_error, fmt="o", color="mediumblue", capsize=4,
              label="Data, SEM per bin (a)")
axis.errorbar(PHI_CENTERS + 4, bootstrap_fit["bin_means"], yerr=bootstrap_fit["bin_errors"], fmt="s",
              color="black", capsize=3, markersize=4, label="Data, event bootstrap (c)")
phi_smooth = np.linspace(-180, 180, 300)
axis.plot(phi_smooth, first_harmonic(phi_smooth, a1_sem), color="firebrick", linewidth=2,
          label=rf"fit (a): $A_1 = {a1_sem:.3f} \pm {a1_sem_error:.3f}$")
axis.axhline(1, color="gray", linestyle=":")
axis.set_xlim(-180, 180)
axis.set_xticks(np.arange(-180, 181, 45))
axis.set_xlabel(r"$\phi$ [deg]")
axis.set_ylabel(r"$\rho_\mu/\langle\rho_\mu\rangle$")
axis.set_title(r"Phase II, $18.0\leq\lg E<18.5$, $50^\circ\leq\theta<60^\circ$, $750\leq r<1250$ m", fontsize=11)
axis.legend(fontsize=9, loc="upper left")
figure.tight_layout()
plt.show()
