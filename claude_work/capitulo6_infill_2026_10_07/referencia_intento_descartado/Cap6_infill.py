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
# # Chapter 6: the Infill array in simulations
#
# **What this notebook produces.** Every number and figure of the revised Chapter 6
# (`Tesis - Latex/DRAFTS/06_infill.tex`):
#
# | Figure | Content |
# |---|---|
# | `cap6_A1_vs_r_geometria_MC.pdf` | UMD $A_1(r)$ per zenith band, true (MC) core and angles |
# | `cap6_conteo_MC_vs_REC.pdf` | $N_\mu^{MC}$ vs $N_\mu^{REC}$, MC geometry |
# | `cap6_UMD_vs_SD.pdf` | UMD, SD total signal, SD muon count and SD EM count, 30-40 deg |
# | `cap6_seleccion_estaciones.pdf` | SD muon count on all stations vs on reconstructed stations |
# | `cap6_A1_vs_r_geometria_REC.pdf` | UMD $A_1(r)$ with the full reconstructed geometry |
# | `cap6_descomposicion_REC.pdf` | Which reconstructed coordinate washes $A_1$ out ($r$ or $\phi$) |
# | `cap6_masa.pdf` | p / He / Fe, MC and REC geometry |
#
# **Inputs (all read-only).**
# - Parquet files in `ADST_Alexey_module_v11/parquet_sib_{proton,helio,hierro}_17/`.
# - `claude_work/revision_asimetrias_sd_umd/` - the SD station-selection control
#   (`comparacion_directa.csv`, paired bootstrap; `adst_counts_fast.csv`, every simulated SD
#   station of the 30-40 deg window with its `HasStation` flag).
# - `Scripts/resultados_cap5_corrimiento_nucleo/` - the reconstructed-core displacement $b$.
#
# **Cost.** One process, no ROOT, about 1.2 GB of RAM; a few minutes.
#
# **Conventions.** $\phi = 0$ is the early region, $A_1 > 0$ means an early excess. The parquet
# column `phi_plane_euler_MC_true_core` carries a +180 deg offset, removed below and checked in
# Section 2.

# %%
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 0. Paths, binning and plotting style

# %%
def find_repo_root(start):
    folder = Path(start).resolve()
    while not (folder / "Tesis - Latex").is_dir():
        if folder.parent == folder:
            raise FileNotFoundError("Could not find the repository root from " + str(start))
        folder = folder.parent
    return folder


REPO_ROOT = find_repo_root(Path.cwd())
FIGURE_DIR = REPO_ROOT / "Tesis - Latex" / "capitulos" / "imagenes_capitulos" / "cap6"
TABLE_DIR = REPO_ROOT / "Scripts" / "resultados_cap6_infill"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

SELECTION_DIR = REPO_ROOT / "claude_work" / "revision_asimetrias_sd_umd"
CORE_SHIFT_TABLE = REPO_ROOT / "Scripts" / "resultados_cap5_corrimiento_nucleo" / "ajuste_corrimiento_nucleo.csv"

# This machine's local simulation folders.
PARQUET_ROOT = Path("/home/lsilva/Github/ADST_Alexey_module_v11")
SAMPLES = {
    "proton": {"folder": "parquet_sib_proton_17", "label": "p"},
    "helio": {"folder": "parquet_sib_helio_17", "label": "He"},
    "hierro": {"folder": "parquet_sib_hierro_17", "label": "Fe"},
}

R_EDGES_m = np.arange(150.0, 1651.0, 150.0)
N_PHI_BINS = 12
N_BOOTSTRAP = 400
MIN_SHOWERS_PER_CELL = 50
# Cells with a larger bootstrap error are computed and saved, but not drawn.
MAX_PLOTTED_ERROR = 0.10
RANDOM_SEED = 20261007

# %%
# Categorical slots of the validated reference palette (dataviz skill), in fixed order.
COLOR_UMD = "#2a78d6"        # blue
COLOR_SD_TOTAL = "#eb6834"   # orange
COLOR_SD_MUON = "#1baf7a"    # aqua
COLOR_SD_EM = "#4a3aa7"      # violet
COLOR_GRAY = "#52514e"

PRIMARY_STYLES = {
    "proton": {"color": "#2a78d6", "marker": "o", "label": "p"},
    "helio": {"color": "#eb6834", "marker": "s", "label": "He"},
    "hierro": {"color": "#1baf7a", "marker": "^", "label": "Fe"},
}

plt.rcParams.update({
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
    "legend.framealpha": 0.92,
    "errorbar.capsize": 3,
    "savefig.bbox": "tight",
})


def zenith_band_colors(n_bands):
    """One hue (blue), light to dark: zenith bands are ordered, so they get a sequential ramp."""
    colormap = plt.get_cmap("Blues")
    return [colormap(value) for value in np.linspace(0.40, 0.95, n_bands)]


def wrap_degrees(angle_deg):
    return (angle_deg + 180.0) % 360.0 - 180.0


def to_degrees(values):
    values = np.asarray(values, dtype=float)
    if np.nanmax(np.abs(values)) < 7.0:   # stored in radians
        values = np.rad2deg(values)
    return values


def add_region_labels(ax):
    ax.axhline(0.0, color="black", linewidth=0.9)


# %% [markdown]
# ## 1. Load the simulations
#
# Two tables per primary:
# - `modules`: one row per Infill UMD module (`counterId >= 100000`), the unit used for the
#   muon counts, as in Chapters 6 and 7. Only modules with `module_status == "candidate"`.
# - `stations`: one row per SD station and event. The parquet repeats each station once per
#   module (three modules per station), so the SD quantities are de-duplicated here; using the
#   module rows would count each station three times and shrink its standard error by $\sqrt{3}$.
#
# Each CORSIKA shower is thrown five times with different cores (five `run_number`s share one
# `event_id`). The bootstrap therefore resamples **progenitor showers** (`shower_id`), which
# keeps the five throws of a shower and the modules of an event together.

# %%
MODULE_COLUMNS = [
    "event_id", "run_number", "logE_MC", "theta_MC", "theta_REC", "logE_REC", "phi_REC",
    "counterId", "sdId", "module_status", "nMuones_MC", "nMuones_REC",
    "r_core", "r_core_MC", "phi_plane_sp", "phi_plane_euler_MC_true_core",
    "sdSignal_REC", "sd_nMuons_MC", "sd_nEM_MC",
]


def load_sample(sample_key):
    folder = PARQUET_ROOT / SAMPLES[sample_key]["folder"]
    pieces = []
    for path in sorted(glob.glob(str(folder / "*.parquet"))):
        table = pd.read_parquet(path, columns=MODULE_COLUMNS)
        pieces.append(table[table["counterId"] >= 100000])
    table = pd.concat(pieces, ignore_index=True)

    table["shower_id"] = table["event_id"].astype(str).str.replace(r":Use_\d+$", "", regex=True)
    table["phi_MC_deg"] = wrap_degrees(to_degrees(table["phi_plane_euler_MC_true_core"]) - 180.0)
    table["phi_REC_deg"] = wrap_degrees(to_degrees(table["phi_plane_sp"]) + table["phi_REC"])
    table["is_reconstructed"] = (table["theta_REC"] > 0) & table["logE_REC"].notna()
    return table


modules_by_sample = {}
stations_by_sample = {}
for sample_key in SAMPLES:
    table = load_sample(sample_key)
    modules = table[table["module_status"] == "candidate"].copy()
    stations = table.drop_duplicates(subset=["run_number", "event_id", "sdId"]).copy()
    modules_by_sample[sample_key] = modules
    stations_by_sample[sample_key] = stations
    print("{:>7}: {:,} candidate modules, {:,} SD station-events, {:,} progenitor showers".format(
        sample_key, len(modules), len(stations), modules["shower_id"].nunique()))

# %% [markdown]
# ## 2. Azimuth convention check
#
# The SD signal is normalised by its event mean and divided by the mean at the same distance.
# A free-phase first harmonic must then peak at $\phi \simeq 0$ (early region) for both the MC
# and the reconstructed azimuth. If this assertion fails, nothing below can be trusted.

# %%
def phase_of_maximum(stations, phi_column, r_column, r_low=400.0, r_high=800.0):
    sample = stations[(stations["theta_MC"] >= 30.0) & (stations["theta_MC"] < 50.0)]
    sample = sample[(sample[r_column] >= r_low) & (sample[r_column] < r_high)].copy()
    event_mean = sample.groupby(["run_number", "event_id"])["sdSignal_REC"].transform("mean")
    sample["normalised"] = sample["sdSignal_REC"] / event_mean
    radial_bin = pd.cut(sample[r_column], np.arange(r_low, r_high + 1.0, 50.0))
    radial_mean = sample.groupby(radial_bin, observed=True)["normalised"].transform("mean")
    relative = sample["normalised"] / radial_mean - 1.0
    phi = np.deg2rad(sample[phi_column])
    cos_coefficient = 2.0 * np.mean(relative * np.cos(phi))
    sin_coefficient = 2.0 * np.mean(relative * np.sin(phi))
    return np.rad2deg(np.arctan2(sin_coefficient, cos_coefficient))


proton_stations = stations_by_sample["proton"]
convention_rows = []
for phi_column, r_column in [("phi_MC_deg", "r_core_MC"), ("phi_REC_deg", "r_core")]:
    phase = phase_of_maximum(proton_stations, phi_column, r_column)
    convention_rows.append({"azimuth": phi_column, "distance": r_column, "phi_max_deg": phase})
convention_check = pd.DataFrame(convention_rows)
print(convention_check.round(2).to_string(index=False))
assert convention_check["phi_max_deg"].abs().max() < 10.0, "Azimuth convention is wrong"
convention_check.to_csv(TABLE_DIR / "chequeo_convencion_azimut.csv", index=False)

# %% [markdown]
# ## 3. The estimator
#
# For one cell (zenith band × radial band):
#
# 1. Split the rows into 12 azimuthal bins and take the mean of the signal in each bin.
# 2. Fit the 12 means with $a + b\cos\phi$ (phase fixed at 0, as in Chapters 3 and 5) by
#    weighted least squares; $A_1 = b/a$.
# 3. Errors: Poisson bootstrap over progenitor showers. The bootstrap spread of each bin mean is
#    the weight of the fit and enters $\chi^2/\mathrm{ndf}$ (ndf = 10); the spread of the
#    replica $A_1$ values is the quoted error.
#
# `A1_err_naive` is the error the original Chapter 6 figures used: the per-bin standard error of
# the mean, which treats all rows as independent. It is kept to document the difference.

# %%
PHI_EDGES_deg = np.linspace(-180.0, 180.0, N_PHI_BINS + 1)
PHI_CENTRES_deg = 0.5 * (PHI_EDGES_deg[1:] + PHI_EDGES_deg[:-1])
DESIGN = np.column_stack([np.ones(N_PHI_BINS), np.cos(np.deg2rad(PHI_CENTRES_deg))])


def weighted_cosine_fit(bin_means, bin_errors):
    """Weighted least squares of a + b cos(phi). Returns a dict with a, b, chi2 and cov."""
    weights = 1.0 / bin_errors ** 2
    normal_matrix = DESIGN.T @ (DESIGN * weights[:, None])
    covariance = np.linalg.inv(normal_matrix)
    coefficients = covariance @ (DESIGN.T @ (weights * bin_means))
    residuals = bin_means - DESIGN @ coefficients
    return {"a": coefficients[0], "b": coefficients[1],
            "chi2": float(np.sum(weights * residuals ** 2)), "covariance": covariance}


def fit_first_harmonic(phi_deg, signal, shower_id, rng):
    """Fit one cell. Returns a dict of named results, or None if the cell is too sparse."""
    phi_bin = np.clip(np.digitize(phi_deg, PHI_EDGES_deg) - 1, 0, N_PHI_BINS - 1)
    shower_code, unique_showers = pd.factorize(shower_id)
    n_showers = len(unique_showers)
    if n_showers < MIN_SHOWERS_PER_CELL:
        return None

    # Per-shower, per-bin sums: the bootstrap is then a matrix product.
    signal_sum = np.zeros((n_showers, N_PHI_BINS))
    row_count = np.zeros((n_showers, N_PHI_BINS))
    np.add.at(signal_sum, (shower_code, phi_bin), signal)
    np.add.at(row_count, (shower_code, phi_bin), 1.0)
    rows_per_bin = row_count.sum(axis=0)
    if np.any(rows_per_bin < 2):
        return None
    bin_means = signal_sum.sum(axis=0) / rows_per_bin

    # Naive per-bin standard error (all rows independent), as in the original figures.
    naive_errors = np.zeros(N_PHI_BINS)
    for k in range(N_PHI_BINS):
        in_bin = signal[phi_bin == k]
        naive_errors[k] = np.std(in_bin, ddof=1) / np.sqrt(len(in_bin))

    replica_weights = rng.poisson(1.0, size=(N_BOOTSTRAP, n_showers)).astype(float)
    replica_sums = replica_weights @ signal_sum
    replica_counts = replica_weights @ row_count
    complete = np.all(replica_counts > 0, axis=1)
    if complete.mean() < 0.9:
        return None
    replica_means = replica_sums[complete] / replica_counts[complete]
    bootstrap_errors = replica_means.std(axis=0, ddof=1)
    if np.any(bootstrap_errors <= 0) or np.any(naive_errors <= 0):
        return None

    nominal = weighted_cosine_fit(bin_means, bootstrap_errors)
    replica_a1 = []
    for means in replica_means:
        replica_fit = weighted_cosine_fit(means, bootstrap_errors)
        replica_a1.append(replica_fit["b"] / replica_fit["a"])
    naive = weighted_cosine_fit(bin_means, naive_errors)
    naive_a1_err = np.sqrt(naive["covariance"][1, 1]) / naive["a"]

    return {
        "A1": nominal["b"] / nominal["a"],
        "A1_err": float(np.std(replica_a1, ddof=1)),
        "A1_err_naive": float(abs(naive_a1_err)),
        "chi2_ndf": nominal["chi2"] / (N_PHI_BINS - 2),
        "n_showers": int(n_showers),
        "n_rows": int(len(signal)),
        "bin_means_normalised": bin_means / nominal["a"],
        "bin_errors_normalised": bootstrap_errors / nominal["a"],
    }


def radial_scan(table, signal_column, r_column, phi_column, theta_column, theta_low, theta_high,
                r_edges=R_EDGES_m, extra_labels=None):
    """A1 in every radial band of one zenith band. Returns a DataFrame, one row per band."""
    rng = np.random.default_rng(RANDOM_SEED)
    in_band = (table[theta_column] >= theta_low) & (table[theta_column] < theta_high)
    band = table[in_band & table[signal_column].notna()]
    rows = []
    for r_low, r_high in zip(r_edges[:-1], r_edges[1:]):
        cell = band[(band[r_column] >= r_low) & (band[r_column] < r_high)]
        result = fit_first_harmonic(cell[phi_column].to_numpy(), cell[signal_column].to_numpy(dtype=float),
                                    cell["shower_id"].to_numpy(), rng)
        row = {"signal": signal_column, "r_column": r_column, "phi_column": phi_column,
               "theta_column": theta_column, "theta_low": theta_low, "theta_high": theta_high,
               "r_low": r_low, "r_high": r_high, "r_centre": 0.5 * (r_low + r_high)}
        if extra_labels is not None:
            row.update(extra_labels)
        if result is None:
            row.update({"A1": np.nan, "A1_err": np.nan, "A1_err_naive": np.nan, "chi2_ndf": np.nan,
                        "n_showers": 0, "n_rows": len(cell)})
        else:
            for key in ["A1", "A1_err", "A1_err_naive", "chi2_ndf", "n_showers", "n_rows"]:
                row[key] = result[key]
        rows.append(row)
    return pd.DataFrame(rows)


def plotted_points(scan):
    """Only cells with a usable error are drawn; all cells stay in the CSV files."""
    return scan[scan["A1_err"] < MAX_PLOTTED_ERROR]


# %% [markdown]
# ## 4. Figure 6.1 - UMD, Monte Carlo geometry
#
# Muon number injected in each module ($N_\mu^{MC}$), true core distance $r_{MC}$, true azimuth,
# zenith bands in $\theta_{MC}$. Proton, SIBYLL 2.3e, $17.5 \le \lg(E/\mathrm{eV}) < 18$.

# %%
ZENITH_BANDS_deg = [(0.0, 10.0), (10.0, 20.0), (20.0, 30.0), (30.0, 40.0), (40.0, 50.0), (50.0, 65.0)]

proton_modules = modules_by_sample["proton"]
scans = []
for theta_low, theta_high in ZENITH_BANDS_deg:
    scan = radial_scan(proton_modules, "nMuones_MC", "r_core_MC", "phi_MC_deg", "theta_MC",
                       theta_low, theta_high)
    scans.append(scan)
umd_mc_geometry = pd.concat(scans, ignore_index=True)
umd_mc_geometry.to_csv(TABLE_DIR / "A1_UMD_geometria_MC.csv", index=False)
print(umd_mc_geometry[["theta_low", "r_low", "A1", "A1_err", "A1_err_naive", "chi2_ndf",
                       "n_showers"]].round(3).to_string(index=False))

# %%
error_ratio = (umd_mc_geometry["A1_err"] / umd_mc_geometry["A1_err_naive"]).describe()
print("Bootstrap / naive error ratio over all cells:")
print(error_ratio.round(2).to_string())

# %%
colors = zenith_band_colors(len(ZENITH_BANDS_deg))
markers = ["o", "s", "^", "D", "v", "P"]
panel_bands = [ZENITH_BANDS_deg[:3], ZENITH_BANDS_deg[3:]]

fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), sharey=True)
for ax, bands in zip(axes, panel_bands):
    for theta_low, theta_high in bands:
        index = ZENITH_BANDS_deg.index((theta_low, theta_high))
        scan = umd_mc_geometry[umd_mc_geometry["theta_low"] == theta_low]
        points = plotted_points(scan)
        style = {"color": colors[index], "marker": markers[index], "markersize": 6,
                 "markeredgecolor": "black", "markeredgewidth": 0.5, "linewidth": 1.6}
        label = "${:.0f}^\\circ \\leq \\theta_{{MC}} < {:.0f}^\\circ$".format(theta_low, theta_high)
        ax.errorbar(points["r_centre"], points["A1"], yerr=points["A1_err"], label=label, **style)
    add_region_labels(ax)
    ax.set_xlabel("$r_{MC}$ [m]")
    ax.set_xlim(100.0, 1600.0)
    ax.legend(loc="upper left", fontsize=10)
axes[0].set_ylabel("$A_1$ (UMD, $N_\\mu^{MC}$)")
axes[0].set_ylim(-0.10, 0.62)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_A1_vs_r_geometria_MC.pdf")
plt.show()

# %% [markdown]
# ## 5. Figure 6.2 - injected vs reconstructed muon number, MC geometry
#
# Same modules, same coordinates (true core and angles); only the counted quantity changes.

# %%
COUNT_BANDS_deg = [(30.0, 40.0), (40.0, 50.0)]
count_scans = []
for theta_low, theta_high in COUNT_BANDS_deg:
    for signal_column in ["nMuones_MC", "nMuones_REC"]:
        scan = radial_scan(proton_modules, signal_column, "r_core_MC", "phi_MC_deg", "theta_MC",
                           theta_low, theta_high)
        count_scans.append(scan)
count_comparison = pd.concat(count_scans, ignore_index=True)
count_comparison.to_csv(TABLE_DIR / "A1_UMD_conteo_MC_vs_REC.csv", index=False)

COUNT_STYLES = {
    "nMuones_MC": {"color": COLOR_UMD, "marker": "o", "linestyle": "-",
                   "label": "$N_\\mu^{MC}$ (inyectado)"},
    "nMuones_REC": {"color": COLOR_SD_TOTAL, "marker": "s", "linestyle": "--",
                    "label": "$N_\\mu^{REC}$ (reconstruido)"},
}
fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), sharey=True)
for ax, (theta_low, theta_high) in zip(axes, COUNT_BANDS_deg):
    for signal_column, style in COUNT_STYLES.items():
        scan = count_comparison[(count_comparison["theta_low"] == theta_low)
                                & (count_comparison["signal"] == signal_column)]
        points = plotted_points(scan)
        offset = 0.0
        if signal_column == "nMuones_REC":
            offset = 12.0
        ax.errorbar(points["r_centre"] + offset, points["A1"], yerr=points["A1_err"],
                    color=style["color"], marker=style["marker"], linestyle=style["linestyle"],
                    markeredgecolor="black", markeredgewidth=0.5, linewidth=1.6, label=style["label"])
    add_region_labels(ax)
    ax.set_title("${:.0f}^\\circ \\leq \\theta_{{MC}} < {:.0f}^\\circ$".format(theta_low, theta_high))
    ax.set_xlabel("$r_{MC}$ [m]")
    ax.set_xlim(100.0, 1600.0)
    ax.set_ylim(-0.14, 0.40)
    ax.legend(loc="upper left", fontsize=10)
axes[0].set_ylabel("$A_1$ (UMD)")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_conteo_MC_vs_REC.pdf")
plt.show()

# %%
paired = count_comparison.pivot_table(index=["theta_low", "r_low"], columns="signal", values="A1")
paired["ratio_REC_over_MC"] = paired["nMuones_REC"] / paired["nMuones_MC"]
print(paired.round(3).to_string())

# %% [markdown]
# ## 6. Figure 6.3 - UMD vs SD, MC geometry, 30-40 deg
#
# SD quantities on **one row per station** (de-duplicated). The SD stations of the parquet are
# only those with a reconstructed partner (`HasStation`), the selection discussed in Section 7.
# - SD total: reconstructed signal in VEM.
# - SD muons / SD EM: number of muons / electrons + photons crossing the tank (MC truth).

# %%
SD_SIGNALS = {
    "sdSignal_REC": {"color": COLOR_SD_TOTAL, "marker": "s", "label": "SD: señal total [VEM]"},
    "sd_nMuons_MC": {"color": COLOR_SD_MUON, "marker": "^", "label": "SD: número de muones (MC)"},
    "sd_nEM_MC": {"color": COLOR_SD_EM, "marker": "D", "label": "SD: número de $e^\\pm$ y $\\gamma$ (MC)"},
}
DETECTOR_BAND_deg = (30.0, 40.0)

detector_scans = []
umd_scan = radial_scan(proton_modules, "nMuones_MC", "r_core_MC", "phi_MC_deg", "theta_MC",
                       *DETECTOR_BAND_deg)
detector_scans.append(umd_scan)
for signal_column in SD_SIGNALS:
    scan = radial_scan(proton_stations, signal_column, "r_core_MC", "phi_MC_deg", "theta_MC",
                       *DETECTOR_BAND_deg)
    detector_scans.append(scan)
detector_comparison = pd.concat(detector_scans, ignore_index=True)
detector_comparison.to_csv(TABLE_DIR / "A1_UMD_vs_SD_30_40.csv", index=False)
print(detector_comparison.pivot_table(index="r_low", columns="signal", values="A1").round(3).to_string())

# %%
# Two panels: the EM count has an amplitude several times larger and would flatten the others.
# Left: the three muon-dominated observables. Right: the EM count, with the SD total for scale.
fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.0))
umd_points = plotted_points(umd_scan)
panel_signals = [["sdSignal_REC", "sd_nMuons_MC"], ["sdSignal_REC", "sd_nEM_MC"]]
for panel_index, ax in enumerate(axes):
    if panel_index == 0:
        ax.errorbar(umd_points["r_centre"], umd_points["A1"], yerr=umd_points["A1_err"], color=COLOR_UMD,
                    marker="o", markeredgecolor="black", markeredgewidth=0.5, linewidth=1.8,
                    label="UMD: número de muones (MC)")
    offset = 0.0
    for signal_column in panel_signals[panel_index]:
        style = SD_SIGNALS[signal_column]
        offset = offset + 10.0
        scan = detector_comparison[detector_comparison["signal"] == signal_column]
        points = plotted_points(scan)
        ax.errorbar(points["r_centre"] + offset, points["A1"], yerr=points["A1_err"], color=style["color"],
                    marker=style["marker"], markeredgecolor="black", markeredgewidth=0.5, linewidth=1.6,
                    label=style["label"])
    add_region_labels(ax)
    ax.set_xlabel("$r_{MC}$ [m]")
    ax.set_xlim(100.0, 1600.0)
axes[0].set_ylabel("$A_1$")
axes[0].set_title("(a) Observables dominados por muones")
axes[1].set_title("(b) Componente electromagnética del SD")
axes[0].legend(loc="lower left", fontsize=9.5)
axes[1].legend(loc="lower left", fontsize=9.5)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_UMD_vs_SD.pdf")
plt.show()

# %% [markdown]
# ## 7. Figure 6.4 - station selection and the SD inversion
#
# **(a)** $A_1$ of the SD muon count over every simulated station vs over the reconstructed ones
# (`HasStation`), with the UMD for reference. Values and paired-bootstrap errors (960 progenitor
# showers, 1200 replicas) from `comparacion_directa.csv`; the code that made them is
# `claude_work/revision_asimetrias_sd_umd/02_notebooks/03_sd_vs_umd/comparar_sd_umd.py`.
#
# **(b)** Why the mean changes. With $\varepsilon$ the fraction of stations retained in an
# $(r,\phi)$ cell and $\varepsilon_N$ the fraction of that cell's muons sitting in retained
# stations,
# $$\langle N_\mu\rangle_{\rm sel} = \langle N_\mu\rangle_{\rm todas}\,\varepsilon_N/\varepsilon .$$
# We measure $\varepsilon$ and $\varepsilon_N/\varepsilon$ in the early ($|\phi| < 60^\circ$) and
# late ($|\phi| > 120^\circ$) regions from `adst_counts_fast.csv` (every simulated SD station of
# the 30-40 deg window, with its `HasStation` flag).

# %%
selection_control = pd.read_csv(SELECTION_DIR / "02_notebooks" / "03_sd_vs_umd" / "resultados"
                                / "comparacion_directa.csv")
print(selection_control[["r_min", "r_max", "A_UMD_original", "sigma_boot_UMD", "A_SD_antes",
                         "sigma_boot_SD_antes", "A_SD_despues", "sigma_boot_SD_despues"]]
      .round(4).to_string(index=False))

# %%
all_sd_stations = pd.read_csv(SELECTION_DIR / "04_soporte" / "tablas" / "adst_counts_fast.csv",
                              dtype={"event_id": str, "source": str})
all_sd_stations["phi_deg"] = np.rad2deg(all_sd_stations["phi"])
all_sd_stations = all_sd_stations[(all_sd_stations["r"] >= 150.0) & (all_sd_stations["r"] < 1350.0)]

SELECTION_R_EDGES_m = np.arange(150.0, 1351.0, 150.0)
REGIONS = {
    "temprana": np.abs(all_sd_stations["phi_deg"]) < 60.0,
    "tardía": np.abs(all_sd_stations["phi_deg"]) > 120.0,
}
selection_rows = []
for region_name, in_region in REGIONS.items():
    region = all_sd_stations[in_region]
    for r_low, r_high in zip(SELECTION_R_EDGES_m[:-1], SELECTION_R_EDGES_m[1:]):
        cell = region[(region["r"] >= r_low) & (region["r"] < r_high)]
        retained = cell["has_rec"] == 1
        station_fraction = retained.mean()
        muon_fraction = cell.loc[retained, "mu"].sum() / cell["mu"].sum()
        mean_all = cell["mu"].mean()
        mean_retained = cell.loc[retained, "mu"].mean()
        selection_rows.append({
            "region": region_name, "r_low": r_low, "r_high": r_high, "r_centre": 0.5 * (r_low + r_high),
            "n_stations": len(cell), "epsilon": station_fraction, "epsilon_N": muon_fraction,
            "enrichment": muon_fraction / station_fraction,
            "mean_mu_all": mean_all, "mean_mu_retained": mean_retained,
            "mean_em_all": cell["em"].mean(), "mean_em_retained": cell.loc[retained, "em"].mean(),
        })
selection_factors = pd.DataFrame(selection_rows)
# The identity <N>_sel = <N>_all * eps_N / eps holds exactly, cell by cell.
identity_gap = selection_factors["mean_mu_retained"] - selection_factors["mean_mu_all"] * selection_factors["enrichment"]
assert np.allclose(identity_gap, 0.0)
selection_factors.to_csv(TABLE_DIR / "factores_seleccion_30_40.csv", index=False)
print(selection_factors[["region", "r_low", "n_stations", "epsilon", "enrichment", "mean_mu_all",
                         "mean_mu_retained"]].round(3).to_string(index=False))

# %% [markdown]
# Bootstrap errors for panel (b): resample progenitor showers.

# %%
all_sd_stations["shower_id"] = all_sd_stations["event_id"].str.replace(r":Use_\d+$", "", regex=True)
rng = np.random.default_rng(RANDOM_SEED)
enrichment_errors = []
for region_name, in_region in REGIONS.items():
    region = all_sd_stations[in_region]
    for r_low, r_high in zip(SELECTION_R_EDGES_m[:-1], SELECTION_R_EDGES_m[1:]):
        cell = region[(region["r"] >= r_low) & (region["r"] < r_high)]
        shower_code, unique_showers = pd.factorize(cell["shower_id"])
        retained = (cell["has_rec"] == 1).to_numpy(dtype=float)
        muons = cell["mu"].to_numpy(dtype=float)
        per_shower = {}
        for name, values in [("stations", np.ones(len(cell))), ("retained", retained),
                             ("muons", muons), ("retained_muons", muons * retained)]:
            totals = np.zeros(len(unique_showers))
            np.add.at(totals, shower_code, values)
            per_shower[name] = totals
        weights = rng.poisson(1.0, size=(N_BOOTSTRAP, len(unique_showers))).astype(float)
        epsilon = (weights @ per_shower["retained"]) / (weights @ per_shower["stations"])
        epsilon_n = (weights @ per_shower["retained_muons"]) / (weights @ per_shower["muons"])
        enrichment_errors.append({"region": region_name, "r_low": r_low,
                                  "epsilon_err": np.std(epsilon, ddof=1),
                                  "enrichment_err": np.std(epsilon_n / epsilon, ddof=1)})
selection_factors = selection_factors.merge(pd.DataFrame(enrichment_errors), on=["region", "r_low"])
selection_factors.to_csv(TABLE_DIR / "factores_seleccion_30_40.csv", index=False)

# %% [markdown]
# **Hypothesis check (supporting, not a proof).** If the EM component helps an early station to
# be retained, then at a *fixed* muon count the retention probability should be higher in the
# early region, and the retained early stations should not need as many muons. We compare
# $P(\mathrm{HasStation}\mid N_\mu)$ early vs late at large distance.

# %%
FAR_R_m = (900.0, 1350.0)
far = all_sd_stations[(all_sd_stations["r"] >= FAR_R_m[0]) & (all_sd_stations["r"] < FAR_R_m[1])]
retention_rows = []
for region_name, in_region in [("temprana", np.abs(far["phi_deg"]) < 60.0),
                               ("tardía", np.abs(far["phi_deg"]) > 120.0)]:
    region = far[in_region]
    for n_muons in range(0, 6):
        if n_muons < 5:
            cell = region[region["mu"] == n_muons]
            label = str(n_muons)
        else:
            cell = region[region["mu"] >= n_muons]
            label = ">=5"
        retention_rows.append({"region": region_name, "n_muons": label, "n_stations": len(cell),
                               "retention": (cell["has_rec"] == 1).mean(),
                               "mean_em": cell["em"].mean()})
retention_vs_muons = pd.DataFrame(retention_rows)
retention_vs_muons.to_csv(TABLE_DIR / "retencion_vs_muones_900_1350.csv", index=False)
print(retention_vs_muons.round(3).to_string(index=False))

# %%
SELECTION_STYLES = {
    "UMD": {"column": "A_UMD_original", "error": "sigma_boot_UMD", "color": COLOR_UMD, "marker": "o",
            "linestyle": "-", "label": "UMD (estaciones reconstruidas)", "offset": -12.0},
    "SD_all": {"column": "A_SD_antes", "error": "sigma_boot_SD_antes", "color": COLOR_SD_MUON,
               "marker": "^", "linestyle": "-", "label": "SD, muones: todas las estaciones", "offset": 0.0},
    "SD_selected": {"column": "A_SD_despues", "error": "sigma_boot_SD_despues", "color": COLOR_SD_TOTAL,
                    "marker": "v", "linestyle": "--", "label": "SD, muones: estaciones reconstruidas",
                    "offset": 12.0},
}
REGION_STYLES = {
    "temprana": {"color": COLOR_SD_MUON, "marker": "o", "linestyle": "-", "offset": -8.0},
    "tardía": {"color": COLOR_SD_TOTAL, "marker": "s", "linestyle": "--", "offset": 8.0},
}

fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.0))
ax = axes[0]
r_centres = selection_control["r_center"]
for curve in SELECTION_STYLES.values():
    ax.errorbar(r_centres + curve["offset"], selection_control[curve["column"]],
                yerr=selection_control[curve["error"]], color=curve["color"], marker=curve["marker"],
                linestyle=curve["linestyle"], markeredgecolor="black", markeredgewidth=0.5,
                linewidth=1.6, label=curve["label"])
add_region_labels(ax)
ax.set_xlabel("$r_{MC}$ [m]")
ax.set_ylabel("$A_1$")
ax.set_title("(a) Conteo de muones MC, $30^\\circ \\leq \\theta_{MC} < 40^\\circ$")
ax.set_xlim(100.0, 1400.0)
ax.legend(loc="lower left", fontsize=9.5)

ax = axes[1]
for region_name, style in REGION_STYLES.items():
    region = selection_factors[selection_factors["region"] == region_name]
    ax.errorbar(region["r_centre"] + style["offset"], region["enrichment"], yerr=region["enrichment_err"],
                color=style["color"], marker=style["marker"], linestyle=style["linestyle"],
                markeredgecolor="black", markeredgewidth=0.5, linewidth=1.6,
                label="región {} ($\\varepsilon_N/\\varepsilon$)".format(region_name))
ax.axhline(1.0, color="black", linewidth=0.9)
ax.set_xlabel("$r_{MC}$ [m]")
ax.set_ylabel("$\\varepsilon_N/\\varepsilon = \\langle N_\\mu\\rangle_{\\rm sel}/\\langle N_\\mu\\rangle_{\\rm todas}$")
ax.set_title("(b) Enriquecimiento en muones de las estaciones retenidas")
ax.set_xlim(100.0, 1400.0)
ax.legend(loc="upper left", fontsize=9.5)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_seleccion_estaciones.pdf")
plt.show()

# %% [markdown]
# ## 8. Figure 6.5 - UMD with the full reconstructed geometry
#
# Reconstructed muon number, reconstructed core distance $r_{REC}$, reconstructed azimuth and
# zenith bands in $\theta_{REC}$, as in Chapter 7. Only events with a reconstructed geometry.
# The last band is split at 55 deg, as in Chapter 7.

# %%
REC_ZENITH_BANDS_deg = [(0.0, 10.0), (10.0, 20.0), (20.0, 30.0), (30.0, 40.0), (40.0, 50.0),
                        (50.0, 55.0), (55.0, 65.0)]
proton_reconstructed = proton_modules[proton_modules["is_reconstructed"]]
rec_scans = []
for theta_low, theta_high in REC_ZENITH_BANDS_deg:
    scan = radial_scan(proton_reconstructed, "nMuones_REC", "r_core", "phi_REC_deg", "theta_REC",
                       theta_low, theta_high)
    rec_scans.append(scan)
umd_rec_geometry = pd.concat(rec_scans, ignore_index=True)
umd_rec_geometry.to_csv(TABLE_DIR / "A1_UMD_geometria_REC.csv", index=False)
print(umd_rec_geometry.pivot_table(index="r_low", columns="theta_low", values="A1").round(3).to_string())

# %% [markdown]
# Cross-check with the Chapter 7 grid (same cells; Chapter 7 also fits a $\sin\phi$ term and
# re-weights the simulated energy spectrum, so small differences are expected). The Chapter 7
# results are not tracked in git; the check runs only where they exist.

# %%
CHAPTER7_GRID = Path("/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA/Scripts/Procesamiento_Datos_Campo/"
                     "resultados_cap7/grilla_A1_17.5-18.0.csv")
if CHAPTER7_GRID.exists():
    chapter7 = pd.read_csv(CHAPTER7_GRID)
    chapter7 = chapter7[chapter7["sample"] == "sib_proton"]
    merged = umd_rec_geometry.merge(chapter7, left_on=["theta_low", "r_low"], right_on=["theta_lo", "r_lo"],
                                    suffixes=("_cap6", "_cap7"))
    merged["pull"] = (merged["A1_cap6"] - merged["A1_cap7"]) / merged["A1_err_cap7"]
    print("Cells compared:", len(merged))
    print("Pull (cap6 - cap7) / err_cap7: mean {:.2f}, std {:.2f}".format(merged["pull"].mean(),
                                                                         merged["pull"].std()))
    merged[["theta_low", "r_low", "A1_cap6", "A1_err_cap6", "A1_cap7", "A1_err_cap7", "pull"]].to_csv(
        TABLE_DIR / "cruce_con_cap7.csv", index=False)

# %%
rec_colors = zenith_band_colors(len(REC_ZENITH_BANDS_deg))
rec_markers = ["o", "s", "^", "D", "v", "P", "X"]
rec_panel_bands = [REC_ZENITH_BANDS_deg[:3], REC_ZENITH_BANDS_deg[3:]]

fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), sharey=True)
for ax, bands in zip(axes, rec_panel_bands):
    for theta_low, theta_high in bands:
        index = REC_ZENITH_BANDS_deg.index((theta_low, theta_high))
        scan = umd_rec_geometry[umd_rec_geometry["theta_low"] == theta_low]
        points = plotted_points(scan)
        style = {"color": rec_colors[index], "marker": rec_markers[index], "markersize": 6,
                 "markeredgecolor": "black", "markeredgewidth": 0.5, "linewidth": 1.6}
        label = "${:.0f}^\\circ \\leq \\theta_{{REC}} < {:.0f}^\\circ$".format(theta_low, theta_high)
        ax.errorbar(points["r_centre"], points["A1"], yerr=points["A1_err"], label=label, **style)
    ax.axvspan(600.0, 1200.0, color=COLOR_GRAY, alpha=0.08, zorder=0)
    add_region_labels(ax)
    ax.set_xlabel("$r_{REC}$ [m]")
    ax.set_xlim(100.0, 1600.0)
    ax.legend(loc="upper left", fontsize=10)
axes[0].set_ylabel("$A_1$ (UMD, $N_\\mu^{REC}$)")
axes[0].set_ylim(-0.12, 0.30)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_A1_vs_r_geometria_REC.pdf")
plt.show()

# %% [markdown]
# ## 9. Figure 6.6 - which reconstructed coordinate washes $A_1$ out?
#
# Same modules ($N_\mu^{MC}$) and the same zenith band in $\theta_{MC}$; only the coordinates
# change. Four combinations: $(r_{MC},\phi_{MC})$, $(r_{REC},\phi_{MC})$, $(r_{MC},\phi_{REC})$ and
# $(r_{REC},\phi_{REC})$.
#
# **Prediction from the core shift (Chapter 5).** The reconstructed core sits a distance $b$
# towards the early region, so an early station at true distance $r$ is assigned
# $r_{REC} \simeq r - b\cos\phi$. A cell at fixed $r_{REC}$ then holds early stations that are truly
# farther out and late stations that are truly closer. With a local lateral slope
# $\beta(r) = -\mathrm{d}\ln\rho/\mathrm{d}\ln r$:
# $$A_1^{(r_{REC})} \simeq A_1^{(r_{MC})} - \beta(r)\,\frac{b}{r}.$$
# $b$ comes from the Chapter 5 fit; $\beta(r)$ is measured here from the same modules.

# %%
DECOMPOSITION_BANDS_deg = [(20.0, 30.0), (30.0, 40.0), (40.0, 50.0)]
COORDINATE_CHOICES = [
    {"r_column": "r_core_MC", "phi_column": "phi_MC_deg", "key": "rMC_phiMC"},
    {"r_column": "r_core", "phi_column": "phi_MC_deg", "key": "rREC_phiMC"},
    {"r_column": "r_core_MC", "phi_column": "phi_REC_deg", "key": "rMC_phiREC"},
    {"r_column": "r_core", "phi_column": "phi_REC_deg", "key": "rREC_phiREC"},
]
decomposition_scans = []
for theta_low, theta_high in DECOMPOSITION_BANDS_deg:
    for choice in COORDINATE_CHOICES:
        scan = radial_scan(proton_reconstructed, "nMuones_MC", choice["r_column"], choice["phi_column"],
                           "theta_MC", theta_low, theta_high, extra_labels={"coordinates": choice["key"]})
        decomposition_scans.append(scan)
decomposition = pd.concat(decomposition_scans, ignore_index=True)

# %% [markdown]
# Local lateral slope $\beta(r)$: log-derivative of the mean module count vs $r_{MC}$, on 50 m
# bins, fitted with a quadratic in $\ln r$ per zenith band and evaluated at the band centres.

# %%
core_shift = pd.read_csv(CORE_SHIFT_TABLE)
core_shift = core_shift[core_shift["convention"] == "phi_euler_minus180"]

FINE_EDGES_m = np.arange(150.0, 1651.0, 50.0)
fine_centres = 0.5 * (FINE_EDGES_m[1:] + FINE_EDGES_m[:-1])
slope_rows = []
for theta_low, theta_high in DECOMPOSITION_BANDS_deg:
    band = proton_reconstructed[(proton_reconstructed["theta_MC"] >= theta_low)
                                & (proton_reconstructed["theta_MC"] < theta_high)]
    mean_counts = band.groupby(pd.cut(band["r_core_MC"], FINE_EDGES_m), observed=False)["nMuones_MC"].mean()
    log_r = np.log(fine_centres)
    log_rho = np.log(mean_counts.to_numpy())
    usable = np.isfinite(log_rho)
    quadratic = np.polyfit(log_r[usable], log_rho[usable], 2)
    zenith_label = "{:.0f}-{:.0f}".format(theta_low, theta_high)
    displacement = core_shift[core_shift["zenith_bin"] == zenith_label]["cos_amplitude_m"].iloc[0]
    displacement_err = core_shift[core_shift["zenith_bin"] == zenith_label]["cos_amplitude_err_m"].iloc[0]
    for r_low, r_high in zip(R_EDGES_m[:-1], R_EDGES_m[1:]):
        r_centre = 0.5 * (r_low + r_high)
        beta = -(2.0 * quadratic[0] * np.log(r_centre) + quadratic[1])
        slope_rows.append({"theta_low": theta_low, "r_low": r_low, "r_centre": r_centre, "beta": beta,
                           "b_m": displacement, "b_err_m": displacement_err,
                           "predicted_shift": -beta * displacement / r_centre})
slopes = pd.DataFrame(slope_rows)

wide = decomposition.pivot_table(index=["theta_low", "r_low"], columns="coordinates", values="A1")
wide_err = decomposition.pivot_table(index=["theta_low", "r_low"], columns="coordinates", values="A1_err")
wide_err.columns = [name + "_err" for name in wide_err.columns]
decomposition_table = wide.join(wide_err).reset_index().merge(slopes, on=["theta_low", "r_low"])
decomposition_table["observed_shift"] = decomposition_table["rREC_phiREC"] - decomposition_table["rMC_phiMC"]
decomposition_table["predicted_A1_REC"] = decomposition_table["rMC_phiMC"] + decomposition_table["predicted_shift"]
decomposition_table.to_csv(TABLE_DIR / "descomposicion_geometria_REC.csv", index=False)
print(decomposition_table[["theta_low", "r_low", "rMC_phiMC", "rREC_phiMC", "rMC_phiREC", "rREC_phiREC",
                           "beta", "observed_shift", "predicted_shift"]].round(3).to_string(index=False))

# %%
DECOMPOSITION_STYLES = {
    "rMC_phiMC": {"color": COLOR_UMD, "marker": "o", "linestyle": "-", "fill": True, "offset": -9.0,
                  "label": "$r_{MC}$, $\\phi_{MC}$"},
    "rMC_phiREC": {"color": COLOR_UMD, "marker": "o", "linestyle": ":", "fill": False, "offset": -3.0,
                   "label": "$r_{MC}$, $\\phi_{REC}$"},
    "rREC_phiMC": {"color": COLOR_SD_TOTAL, "marker": "s", "linestyle": ":", "fill": False, "offset": 3.0,
                   "label": "$r_{REC}$, $\\phi_{MC}$"},
    "rREC_phiREC": {"color": COLOR_SD_TOTAL, "marker": "s", "linestyle": "-", "fill": True, "offset": 9.0,
                    "label": "$r_{REC}$, $\\phi_{REC}$"},
}
fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.9), sharey=True)
for ax, (theta_low, theta_high) in zip(axes, DECOMPOSITION_BANDS_deg):
    band_table = decomposition_table[decomposition_table["theta_low"] == theta_low]
    band_table = band_table[band_table["rMC_phiMC_err"] < MAX_PLOTTED_ERROR]
    for key, style in DECOMPOSITION_STYLES.items():
        face_color = "white"
        if style["fill"]:
            face_color = style["color"]
        ax.errorbar(band_table["r_centre"] + style["offset"], band_table[key], yerr=band_table[key + "_err"],
                    color=style["color"], marker=style["marker"], markerfacecolor=face_color,
                    markeredgecolor=style["color"], linestyle=style["linestyle"], linewidth=1.4,
                    markersize=6, label=style["label"])
    ax.plot(band_table["r_centre"], band_table["predicted_A1_REC"], color="black", linestyle="--",
            linewidth=1.4, label="$A_1(r_{MC}) - \\beta\\, b/r$")
    add_region_labels(ax)
    ax.set_title("${:.0f}^\\circ \\leq \\theta_{{MC}} < {:.0f}^\\circ$, $b = {:.0f}$ m".format(
        theta_low, theta_high, band_table["b_m"].iloc[0]))
    ax.set_xlabel("$r$ [m]")
    ax.set_xlim(100.0, 1600.0)
axes[0].set_ylabel("$A_1$ (UMD, $N_\\mu^{MC}$)")
axes[0].legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_descomposicion_REC.pdf")
plt.show()

# %% [markdown]
# Same decomposition for the SD quantities at 30-40 deg (numbers for the text only). The EM
# lateral distribution is steeper, so its $\beta\,b/r$ term is larger in absolute value, but its
# $A_1$ is larger still.

# %%
proton_stations_reconstructed = proton_stations[proton_stations["is_reconstructed"]]
sd_decomposition_rows = []
for signal_column in ["sdSignal_REC", "sd_nMuons_MC", "sd_nEM_MC"]:
    for choice in [COORDINATE_CHOICES[0], COORDINATE_CHOICES[3]]:
        scan = radial_scan(proton_stations_reconstructed, signal_column, choice["r_column"],
                           choice["phi_column"], "theta_MC", 30.0, 40.0,
                           extra_labels={"coordinates": choice["key"]})
        sd_decomposition_rows.append(scan)
sd_decomposition = pd.concat(sd_decomposition_rows, ignore_index=True)
sd_decomposition.to_csv(TABLE_DIR / "descomposicion_SD_30_40.csv", index=False)
print(sd_decomposition.pivot_table(index="r_low", columns=["signal", "coordinates"], values="A1")
      .round(3).to_string())

# %% [markdown]
# ## 10. Figure 6.7 - primary mass
#
# p, He and Fe (SIBYLL 2.3e, same energy range). Top row: MC geometry and $N_\mu^{MC}$. Bottom
# row: full REC geometry and $N_\mu^{REC}$. Then the difference Fe - p with its error (the two
# samples are independent, so the errors add in quadrature).

# %%
MASS_BANDS_deg = [(30.0, 40.0), (40.0, 50.0)]
GEOMETRIES = {
    "MC": {"signal": "nMuones_MC", "r_column": "r_core_MC", "phi_column": "phi_MC_deg",
           "theta_column": "theta_MC", "only_reconstructed": False},
    "REC": {"signal": "nMuones_REC", "r_column": "r_core", "phi_column": "phi_REC_deg",
            "theta_column": "theta_REC", "only_reconstructed": True},
}
mass_scans = []
for sample_key in SAMPLES:
    modules = modules_by_sample[sample_key]
    for geometry_name, geometry in GEOMETRIES.items():
        table = modules
        if geometry["only_reconstructed"]:
            table = modules[modules["is_reconstructed"]]
        for theta_low, theta_high in MASS_BANDS_deg:
            scan = radial_scan(table, geometry["signal"], geometry["r_column"], geometry["phi_column"],
                               geometry["theta_column"], theta_low, theta_high,
                               extra_labels={"sample": sample_key, "geometry": geometry_name})
            mass_scans.append(scan)
mass_comparison = pd.concat(mass_scans, ignore_index=True)
mass_comparison.to_csv(TABLE_DIR / "A1_masa.csv", index=False)

# %%
proton_rows = mass_comparison[mass_comparison["sample"] == "proton"].set_index(["geometry", "theta_low", "r_low"])
iron_rows = mass_comparison[mass_comparison["sample"] == "hierro"].set_index(["geometry", "theta_low", "r_low"])
iron_minus_proton = pd.DataFrame({
    "delta_A1": iron_rows["A1"] - proton_rows["A1"],
    "delta_A1_err": np.sqrt(iron_rows["A1_err"] ** 2 + proton_rows["A1_err"] ** 2),
}).reset_index()
iron_minus_proton["pull"] = iron_minus_proton["delta_A1"] / iron_minus_proton["delta_A1_err"]
iron_minus_proton.to_csv(TABLE_DIR / "diferencia_Fe_menos_p.csv", index=False)
print(iron_minus_proton.round(3).to_string(index=False))


# %%
def inverse_variance_mean(values, errors):
    weights = 1.0 / errors ** 2
    mean = np.sum(weights * values) / np.sum(weights)
    return mean, 1.0 / np.sqrt(np.sum(weights))


# Summary over the region 450 <= r < 1200 m of both zenith bands, per geometry.
summary_rows = []
for geometry_name in GEOMETRIES:
    region = iron_minus_proton[(iron_minus_proton["geometry"] == geometry_name)
                               & (iron_minus_proton["r_low"] >= 450.0) & (iron_minus_proton["r_low"] < 1200.0)]
    region = region.dropna()
    mean, error = inverse_variance_mean(region["delta_A1"].to_numpy(), region["delta_A1_err"].to_numpy())
    chi2 = float(np.sum(region["pull"] ** 2))
    summary_rows.append({"geometry": geometry_name, "n_cells": len(region), "mean_delta_A1": mean,
                         "mean_delta_A1_err": error, "chi2_vs_zero": chi2, "ndf": len(region)})
mass_summary = pd.DataFrame(summary_rows)
mass_summary.to_csv(TABLE_DIR / "resumen_Fe_menos_p.csv", index=False)
print(mass_summary.round(4).to_string(index=False))

# %%
fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.6), sharex=True, sharey="row")
for row_index, geometry_name in enumerate(GEOMETRIES):
    for column_index, (theta_low, theta_high) in enumerate(MASS_BANDS_deg):
        ax = axes[row_index, column_index]
        for sample_key, style in PRIMARY_STYLES.items():
            scan = mass_comparison[(mass_comparison["sample"] == sample_key)
                                   & (mass_comparison["geometry"] == geometry_name)
                                   & (mass_comparison["theta_low"] == theta_low)]
            points = plotted_points(scan)
            offset = {"proton": -10.0, "helio": 0.0, "hierro": 10.0}[sample_key]
            ax.errorbar(points["r_centre"] + offset, points["A1"], yerr=points["A1_err"], color=style["color"],
                        marker=style["marker"], markeredgecolor="black", markeredgewidth=0.5, linewidth=1.5,
                        label=style["label"])
        add_region_labels(ax)
        theta_symbol = "\\theta_{MC}"
        if geometry_name == "REC":
            theta_symbol = "\\theta_{REC}"
        ax.set_title("Geometría {}, ${:.0f}^\\circ \\leq {} < {:.0f}^\\circ$".format(
            geometry_name, theta_low, theta_symbol, theta_high))
        if row_index == 1:
            ax.set_xlabel("$r$ [m]")
        ax.set_xlim(100.0, 1600.0)
    axes[row_index, 0].set_ylabel("$A_1$ (UMD)")
axes[0, 0].legend(loc="upper left", fontsize=10)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "cap6_masa.pdf")
plt.show()

# %% [markdown]
# ## 11. Energy: two sub-bands of the simulated half decade (MC geometry, proton and iron)

# %%
ENERGY_SUBBANDS = [(17.5, 17.75), (17.75, 18.0)]
energy_scans = []
for sample_key in ["proton", "hierro"]:
    modules = modules_by_sample[sample_key]
    for energy_low, energy_high in ENERGY_SUBBANDS:
        in_energy = (modules["logE_MC"] >= energy_low) & (modules["logE_MC"] < energy_high)
        for theta_low, theta_high in MASS_BANDS_deg:
            scan = radial_scan(modules[in_energy], "nMuones_MC", "r_core_MC", "phi_MC_deg", "theta_MC",
                               theta_low, theta_high,
                               extra_labels={"sample": sample_key, "energy_low": energy_low})
            energy_scans.append(scan)
energy_comparison = pd.concat(energy_scans, ignore_index=True)
energy_comparison.to_csv(TABLE_DIR / "A1_subbandas_energia.csv", index=False)

energy_rows = []
for sample_key in ["proton", "hierro"]:
    for energy_low, _ in ENERGY_SUBBANDS:
        region = energy_comparison[(energy_comparison["sample"] == sample_key)
                                   & (energy_comparison["energy_low"] == energy_low)
                                   & (energy_comparison["r_low"] >= 450.0) & (energy_comparison["r_low"] < 1200.0)]
        region = region.dropna(subset=["A1", "A1_err"])
        mean, error = inverse_variance_mean(region["A1"].to_numpy(), region["A1_err"].to_numpy())
        energy_rows.append({"sample": sample_key, "energy_low": energy_low, "n_cells": len(region),
                            "mean_A1": mean, "mean_A1_err": error})
energy_summary = pd.DataFrame(energy_rows)
energy_summary.to_csv(TABLE_DIR / "resumen_subbandas_energia.csv", index=False)
print(energy_summary.round(4).to_string(index=False))

# %% [markdown]
# ## 12. Key numbers for the text

# %%
def cell_value(table, **conditions):
    selection = table
    for column, value in conditions.items():
        selection = selection[selection[column] == value]
    return selection.iloc[0]


key_numbers = {
    "error_ratio_bootstrap_over_naive_median": float(error_ratio["50%"]),
    "error_ratio_bootstrap_over_naive_min": float(error_ratio["min"]),
    "error_ratio_bootstrap_over_naive_max": float(error_ratio["max"]),
    "convention_phi_max_deg": convention_check.set_index("azimuth")["phi_max_deg"].to_dict(),
    "selection_far_early_enrichment": float(cell_value(selection_factors, region="temprana", r_low=1200.0)["enrichment"]),
    "selection_far_late_enrichment": float(cell_value(selection_factors, region="tardía", r_low=1200.0)["enrichment"]),
    "selection_far_early_epsilon": float(cell_value(selection_factors, region="temprana", r_low=1200.0)["epsilon"]),
    "selection_far_late_epsilon": float(cell_value(selection_factors, region="tardía", r_low=1200.0)["epsilon"]),
    "mass_summary": mass_summary.to_dict(orient="records"),
    "energy_summary": energy_summary.to_dict(orient="records"),
}
with open(TABLE_DIR / "numeros_clave.json", "w") as handle:
    json.dump(key_numbers, handle, indent=2, ensure_ascii=False)
print(json.dumps(key_numbers, indent=2, ensure_ascii=False))
