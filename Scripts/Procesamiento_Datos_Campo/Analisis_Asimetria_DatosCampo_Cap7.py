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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Chapter 7 — Azimuthal asymmetry of the UMD muon density in field data
#
# This notebook produces every number, table and figure of Chapter 7
# (`Tesis - Latex/capitulos/07_datos_reales.tex`). It only reads parquet files that
# already exist; it never opens an ADST file, so it runs in the plain `venv/`
# (no PyROOT, no Auger Offline environment).
#
# **Inputs**
# - Field data: `~/Github/parquet_datos_campo/` (produced by `Procesamiento_Datos_Campo_v1`).
#   Phase I (2021–2023) and Phase II SPMT (2022–2026). The parquet on disk were written with
#   looser cuts than the processing notebook's config cell shows (lgE ≥ 16.5, θ ≤ 70°), so
#   every cut is re-imposed here.
# - Simulations: `~/Github/ADST_Alexey_module_v11/` — SIBYLL 2.3e p / He / Fe and
#   QGSJET-III He, lgE_MC ∈ [17.5, 18.0], θ ∈ [0°, 65°], Infill rows only
#   (`counterId ≥ 100000`). These are the same HasStation-selected parquets used in
#   Chapter 6, i.e. the same station selection the field data necessarily has.
#
# **Outputs**
# - Figures → `Tesis - Latex/capitulos/imagenes_capitulos/cap7/`
# - Tables (CSV/JSON) → `Scripts/Procesamiento_Datos_Campo/resultados_cap7/`
#
# **Logic of the chapter** (each section below is one step):
# 1. Load data and MC, apply the cuts, write the cut-flow table.
# 2. One A1 estimator, shared by data and MC (event-level bootstrap, A1 and B1).
# 3. Continuity checks: reproduce the earlier audit's replication cell, confirm the
#    MC azimuth convention, and compare with the Chapter 6 estimator.
# 4. Field-data results on a grid fixed in advance (Chapter 6 binning).
# 5. Null tests (B1, near-vertical showers, Phase I vs Phase II).
# 6. Global significance in a region fixed from the Chapter 6 MC.
# 7. Data vs MC, the near-core region, and the composition test.
# 8. Energy evolution in data.
# 9. Systematic variations.

# %%
import os
import glob
import json
import time
from dataclasses import dataclass, field, replace, asdict

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats as sps
from scipy.optimize import curve_fit

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

# Same HEP style as plots_seccion_6.py, so Chapter 6 and Chapter 7 figures match.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "axes.linewidth": 1.2,
    "legend.frameon": True, "legend.edgecolor": "black",
    "lines.linewidth": 1.6, "lines.markersize": 6,
    "xtick.labelsize": 12, "ytick.labelsize": 12,
    "axes.labelsize": 13,
    "figure.dpi": 110, "savefig.dpi": 200,
    "savefig.bbox": "tight",
})
print("Imports OK")

# %% [markdown]
# ## 1. Configuration
#
# Everything that defines the analysis lives in this cell. The binning is the
# Chapter 6 binning (Δr = 150 m starting at 150 m, Δθ = 10°), with the last zenith
# band split at 55° because the SD-750 energy calibration is standard only below
# about 55°: the 55–65° band is shown but flagged, and is not part of the main result.

# %%
REPO_DIR = "/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA"
DATA_DIR = "/home/lsilva/Github/parquet_datos_campo"
MC_DIR = "/home/lsilva/Github/ADST_Alexey_module_v11"

FIG_DIR = os.path.join(REPO_DIR, "Tesis - Latex", "capitulos", "imagenes_capitulos", "cap7")
RESULTS_DIR = os.path.join(REPO_DIR, "Scripts", "Procesamiento_Datos_Campo", "resultados_cap7")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

SUBSET_PHASE_I = "PhaseI"
SUBSET_PHASE_II = "PhaseIISPMTPhaseIIBeta"

# Event-level cuts for the field data.
MIN_LOGE_MAIN = 17.5          # SD-750 full trigger efficiency; also the lower edge of the MC library
MIN_LOGE_LOADED = 17.0        # 17.0-17.5 is kept in memory only for the energy-evolution figure
MAX_THETA_LOADED = 65.0
MAX_THETA_MAIN = 55.0         # main result; 55-65 deg is shown separately and flagged
PHASE_II_COMMISSIONING_YEAR = 2022   # 83% of SD stations rejected that year -> excluded

# Grid fixed in advance (Chapter 6 binning).
R_EDGES = np.arange(150, 1651, 150)
THETA_EDGES = np.array([0, 10, 20, 30, 40, 50, 55, 65])
ENERGY_BANDS = [
    {"name": "17.0-17.5", "lo": 17.0, "hi": 17.5},
    {"name": "17.5-18.0", "lo": 17.5, "hi": 18.0},
    {"name": "18.0-18.5", "lo": 18.0, "hi": 18.5},
    {"name": ">=18.5", "lo": 18.5, "hi": 20.5},
]
MAIN_ENERGY_BAND = ENERGY_BANDS[1]

# Region where the Chapter 6 REC-geometry MC says the asymmetry survives the
# reconstruction ("650-1200 m" for 20-40 deg, "600-1500 m" for 50-65 deg).
# It is fixed from the MC, not chosen by looking at the data.
GOLDEN_REGION = {"r_lo": 600, "r_hi": 1200, "theta_lo": 20, "theta_hi": MAX_THETA_MAIN}

# Estimator settings.
N_PHI_BINS = 12
N_BOOTSTRAP = 400
MIN_EVENTS_PER_CELL = 50
RANDOM_SEED = 20261004

# MC samples: label used in tables, folder, plotting style. Colors validated for
# colour-vision deficiency together with distinct markers and line styles.
MC_SAMPLES = [
    {"key": "sib_proton", "label": "p (SIBYLL 2.3e)", "folder": "parquet_sib_proton_17",
     "color": "#4169e1", "marker": "o", "linestyle": "-", "lnA": np.log(1)},
    {"key": "sib_helio", "label": "He (SIBYLL 2.3e)", "folder": "parquet_sib_helio_17",
     "color": "#2e8b57", "marker": "^", "linestyle": "-.", "lnA": np.log(4)},
    {"key": "sib_hierro", "label": "Fe (SIBYLL 2.3e)", "folder": "parquet_sib_hierro_17",
     "color": "#b22222", "marker": "s", "linestyle": "--", "lnA": np.log(56)},
    {"key": "qgs_helio", "label": "He (QGSJET-III)", "folder": "parquet_qgs_helio_17",
     "color": "#e08a00", "marker": "D", "linestyle": ":", "lnA": np.log(4)},
]
MC_STYLE = {}
for sample in MC_SAMPLES:
    MC_STYLE[sample["key"]] = sample

DATA_STYLE = {"color": "black", "marker": "o", "label": "Datos (Fase I + II)"}

print("Figures ->", FIG_DIR)
print("Tables  ->", RESULTS_DIR)

# %% [markdown]
# ## 2. Field data: load, cut flow, clean sample
#
# One row per UMD module per event. The cut flow counts events and modules after
# each cut, starting from what is on disk. The module-quality mask
# (`CLEAN_MASK` of the preliminary notebooks) keeps modules whose SD station and
# UMD counter are not rejected and whose status is `candidate`.

# %%
DATA_COLUMNS = [
    "event_id", "logE_REC", "theta_REC", "phi_REC", "core_x", "core_y",
    "counterId", "sdId", "moduleId", "nMuones_REC", "module_status",
    "r_core", "phi_plane_sp", "is_sd_rejected", "is_counter_rejected",
    "subset", "year", "month",
]


def load_field_data():
    """Read every field-data parquet; return (rows with lgE >= MIN_LOGE_LOADED, on-disk totals).
    The zenith cut is applied later so that the cut flow can count it."""
    files = sorted(glob.glob(os.path.join(DATA_DIR, "**", "*.parquet"), recursive=True))
    print(f"{len(files)} parquet files under {DATA_DIR}")

    on_disk_events = 0
    on_disk_modules = 0
    pieces = []
    t0 = time.time()
    for i, path in enumerate(files):
        table = pd.read_parquet(path, columns=DATA_COLUMNS)
        on_disk_events += table["event_id"].nunique()
        on_disk_modules += len(table)
        pieces.append(table[table["logE_REC"] >= MIN_LOGE_LOADED])
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(files)} files read ({time.time() - t0:.0f} s)")

    data = pd.concat(pieces, ignore_index=True)
    data["module_status"] = data["module_status"].astype("category")
    data["subset"] = data["subset"].astype("category")
    data["phi_deg"] = np.rad2deg(data["phi_plane_sp"])   # raw GetAzimuthSP(), see Section 4
    on_disk = {"events": on_disk_events, "modules": on_disk_modules}
    print(f"Loaded {len(data):,} module rows in {time.time() - t0:.0f} s")
    return data, on_disk


data_all, on_disk_totals = load_field_data()

# %%
def count_events_and_modules(table):
    return {"events": int(table["event_id"].nunique()), "modules": int(len(table))}


cut_flow = []
cut_flow.append({"cut": "En disco (6T5, lgE >= 16.5, theta <= 70)", **on_disk_totals})

step = data_all[data_all["logE_REC"] >= MIN_LOGE_MAIN]
cut_flow.append({"cut": "lgE_REC >= 17.5", **count_events_and_modules(step)})

step = step[step["theta_REC"] <= MAX_THETA_LOADED]
cut_flow.append({"cut": "theta_REC <= 65", **count_events_and_modules(step)})

is_commissioning = (step["subset"] == SUBSET_PHASE_II) & (step["year"] == PHASE_II_COMMISSIONING_YEAR)
step = step[~is_commissioning]
cut_flow.append({"cut": "Sin Fase II 2022 (puesta en marcha)", **count_events_and_modules(step)})

step = step[~step["is_sd_rejected"]]
cut_flow.append({"cut": "Estacion SD no rechazada", **count_events_and_modules(step)})

step = step[~step["is_counter_rejected"]]
cut_flow.append({"cut": "Contador UMD no rechazado", **count_events_and_modules(step)})

step = step[step["module_status"] == "candidate"]
cut_flow.append({"cut": "Modulo candidato", **count_events_and_modules(step)})

step_main = step[step["theta_REC"] < MAX_THETA_MAIN]
cut_flow.append({"cut": "theta_REC < 55 (resultado principal)", **count_events_and_modules(step_main)})

cut_flow_table = pd.DataFrame(cut_flow)
for subset_name in [SUBSET_PHASE_I, SUBSET_PHASE_II]:
    in_subset = step_main[step_main["subset"] == subset_name]
    print(f"{subset_name}: {in_subset['event_id'].nunique():,} events in the main sample")
cut_flow_table.to_csv(os.path.join(RESULTS_DIR, "cut_flow.csv"), index=False)
cut_flow_table

# %%
# Clean field-data sample, all energies >= 17.0 and theta <= 65 (the bands are
# selected later). Phase II 2022 is removed here once and for all.
is_clean_module = (
    (~data_all["is_sd_rejected"])
    & (~data_all["is_counter_rejected"])
    & (data_all["module_status"] == "candidate")
)
is_commissioning = (data_all["subset"] == SUBSET_PHASE_II) & (data_all["year"] == PHASE_II_COMMISSIONING_YEAR)
is_in_zenith_range = data_all["theta_REC"] <= MAX_THETA_LOADED
data_clean = data_all[is_clean_module & ~is_commissioning & is_in_zenith_range].copy()

# Number of modules each counter has in the clean sample (used by a systematic check:
# the MC always has 3 modules per counter, the field array has counters with 1-7).
modules_per_counter = data_clean.groupby("counterId")["moduleId"].nunique()
data_clean["counter_n_modules"] = data_clean["counterId"].map(modules_per_counter)

print(f"Clean field sample: {len(data_clean):,} modules, {data_clean['event_id'].nunique():,} events")
print("Modules per counter:", modules_per_counter.value_counts().sort_index().to_dict())

# %% [markdown]
# ## 3. Simulations
#
# Three details matter when the MC is compared with data:
#
# - **Energy.** The library covers lgE_MC ∈ [17.5, 18.0]. In these simulations the
#   reconstructed SD energy is about 0.14 below the true one, because the simulated showers have
#   fewer muons than real ones while the S(450)→E calibration comes from data.
#   Selecting MC by `logE_REC` would therefore pick a different sample. The MC is
#   selected by true energy (the whole library), the data by reconstructed energy
#   in the same interval.
# - **Spectrum.** The library is flat in lgE (E⁻¹). Each MC event gets weight
#   E⁻² so that the sample follows the steep (≈E⁻³) field spectrum within the bin.
# - **Geometry.** Everything else is REC level, as in the data: θ_REC, r from the
#   reconstructed core, and the azimuth GetAzimuthSP(). The Chapter 6 parquet stored
#   `phi_plane_sp = GetAzimuthSP() − φ_REC`, so `phi_plane_sp + φ_REC` gives back the
#   raw GetAzimuthSP() value that the field-data parquet stores directly (checked in Section 4).
#   Events whose reconstruction failed (θ_REC = 0 sentinel, about 3%) are dropped.

# %%
MC_COLUMNS = [
    "event_id", "logE_MC", "theta_MC", "logE_REC", "theta_REC", "phi_REC",
    "counterId", "moduleId", "nMuones_REC", "nMuones_MC", "module_status",
    "phi_plane_sp", "phi_plane_euler_MC_true_core", "r_core", "r_core_MC",
]


def to_degrees(series):
    """Some parquet columns are in radians, others in degrees."""
    if series.dropna().abs().max() < 7.0:
        return np.rad2deg(series)
    return series


def wrap_degrees(angle_deg):
    return (angle_deg + 180.0) % 360.0 - 180.0


def load_mc_sample(sample):
    files = sorted(glob.glob(os.path.join(MC_DIR, sample["folder"], "*.parquet")))
    pieces = []
    for path in files:
        table = pd.read_parquet(path, columns=MC_COLUMNS)
        pieces.append(table[table["counterId"] >= 100000])
    mc = pd.concat(pieces, ignore_index=True)

    reconstructed = (mc["theta_REC"] > 0) & mc["logE_REC"].notna()
    mc = mc[reconstructed & (mc["module_status"] == "candidate")].copy()

    mc["phi_deg"] = wrap_degrees(to_degrees(mc["phi_plane_sp"]) + mc["phi_REC"])
    mc["phi_true_deg"] = wrap_degrees(to_degrees(mc["phi_plane_euler_MC_true_core"]) - 180.0)
    mc["event_weight"] = 10.0 ** (-2.0 * (mc["logE_MC"] - 17.5))
    mc["counter_n_modules"] = 3
    mc["sample"] = sample["key"]
    return mc


mc_by_sample = {}
for sample in MC_SAMPLES:
    mc_by_sample[sample["key"]] = load_mc_sample(sample)
    n_events = mc_by_sample[sample["key"]]["event_id"].nunique()
    print(f"{sample['label']:>18}: {n_events:,} events, {len(mc_by_sample[sample['key']]):,} Infill modules")

# %% [markdown]
# ## 4. The A1 estimator (shared by data and MC)
#
# For one cell (energy band × θ band × r band):
#
# 1. Split the modules into `N_PHI_BINS` azimuthal bins of the shower-plane angle φ.
# 2. In each bin take the (event-weighted) mean of the muon number per module.
# 3. Fit the 12 bin means with ρ(φ) = ρ₀ (1 + A1 cos φ + B1 sin φ), weighted least
#    squares. A1 is the observable; B1 must vanish by symmetry, so it is a null test of
#    the azimuth convention and of the acceptance.
# 4. Errors: resample *events* (Poisson bootstrap), because the modules of one event,
#    and especially the three modules of one counter, are correlated. The same
#    bootstrap gives the error of each bin mean used in the weights and in χ²/ndf.
#
# This is the Chapter 6 estimator (bin means normalised by their average, first
# harmonic) plus the sin term and the bootstrap. Section 4c checks that the two agree.
#
# `signal_mode="ldf_ratio"` is a cross-check estimator. Each module is divided by a
# smooth φ-averaged reference ⟨n⟩(r, lgE) fitted within the θ band, before averaging. A
# per-bin mean is not biased by how many modules fall in each φ bin. It can be biased
# if the mix of r and energy inside the cell changes with φ, and the ratio removes that.

# %%
def harmonic_design_matrix(phi_centers_deg):
    phi = np.deg2rad(phi_centers_deg)
    return np.column_stack([np.ones_like(phi), np.cos(phi), np.sin(phi)])


def weighted_harmonic_fit(bin_means, bin_errors, design):
    """Return the coefficients (a, b, c) of a + b cos + c sin and the chi2."""
    weights = 1.0 / bin_errors ** 2
    normal_matrix = design.T @ (design * weights[:, None])
    coefficients = np.linalg.solve(normal_matrix, design.T @ (weights * bin_means))
    residuals = bin_means - design @ coefficients
    chi2 = float(np.sum(weights * residuals ** 2))
    return coefficients, chi2


def fit_cell(phi_deg, signal, event_id, event_weight=None, n_phi_bins=N_PHI_BINS,
             n_bootstrap=N_BOOTSTRAP, rng=None):
    """
    Fit the first harmonic in one cell. Returns a dict, or None if the cell has too
    few events or an empty azimuthal bin.
    """
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)
    if event_weight is None:
        event_weight = np.ones(len(signal))

    phi_edges = np.linspace(-180.0, 180.0, n_phi_bins + 1)
    phi_centers = 0.5 * (phi_edges[1:] + phi_edges[:-1])
    phi_bin = np.clip(np.digitize(phi_deg, phi_edges) - 1, 0, n_phi_bins - 1)

    event_code, unique_events = pd.factorize(event_id)
    n_events = len(unique_events)
    if n_events < MIN_EVENTS_PER_CELL:
        return None

    # Per-event, per-phi-bin sums. The bootstrap then only needs one matrix product.
    signal_sum = np.zeros((n_events, n_phi_bins))
    weight_sum = np.zeros((n_events, n_phi_bins))
    np.add.at(signal_sum, (event_code, phi_bin), event_weight * signal)
    np.add.at(weight_sum, (event_code, phi_bin), event_weight)

    total_weight = weight_sum.sum(axis=0)
    if np.any(total_weight <= 0):
        return None
    bin_means = signal_sum.sum(axis=0) / total_weight

    poisson_counts = rng.poisson(1.0, size=(n_bootstrap, n_events)).astype(float)
    boot_signal = poisson_counts @ signal_sum
    boot_weight = poisson_counts @ weight_sum
    replica_is_complete = np.all(boot_weight > 0, axis=1)
    if replica_is_complete.mean() < 0.9:
        return None
    boot_means = boot_signal[replica_is_complete] / boot_weight[replica_is_complete]
    bin_errors = boot_means.std(axis=0, ddof=1)
    if np.any(bin_errors <= 0):
        return None

    design = harmonic_design_matrix(phi_centers)
    coefficients, chi2 = weighted_harmonic_fit(bin_means, bin_errors, design)
    a1 = coefficients[1] / coefficients[0]
    b1 = coefficients[2] / coefficients[0]

    boot_a1 = []
    boot_b1 = []
    for replica_means in boot_means:
        replica_coefficients, _ = weighted_harmonic_fit(replica_means, bin_errors, design)
        boot_a1.append(replica_coefficients[1] / replica_coefficients[0])
        boot_b1.append(replica_coefficients[2] / replica_coefficients[0])

    return {
        "A1": float(a1), "A1_err": float(np.std(boot_a1, ddof=1)),
        "B1": float(b1), "B1_err": float(np.std(boot_b1, ddof=1)),
        "chi2_ndf": chi2 / (n_phi_bins - 3),
        "n_events": int(n_events), "n_modules": int(len(signal)),
        "phi_centers": phi_centers, "bin_means": bin_means / coefficients[0],
        "bin_errors": bin_errors / coefficients[0],
    }


# %%
def add_ldf_reference(table, energy_column, theta_edges):
    """
    Add column `n_reference`: a smooth, phi-averaged muon LDF evaluated at each module,
        ln<n> = c0 + c1 x + c2 u + c3 u^2 + c4 x u ,  x = lgE - 17.75, u = ln(r / 600 m),
    fitted separately in each theta band to the means of fine (r, lgE) bins.
    """
    table = table.copy()
    table["n_reference"] = np.nan
    r_fine = np.arange(100, 1751, 50)
    e_fine = np.arange(17.0, 20.51, 0.1)
    for theta_lo, theta_hi in zip(theta_edges[:-1], theta_edges[1:]):
        in_band = (table["theta_REC"] >= theta_lo) & (table["theta_REC"] < theta_hi)
        band = table[in_band]
        if band.empty:
            continue
        grouped = band.groupby([pd.cut(band["r_core"], r_fine), pd.cut(band[energy_column], e_fine)],
                               observed=True)["nMuones_REC"].agg(["mean", "count"]).reset_index()
        grouped = grouped[(grouped["mean"] > 0) & (grouped["count"] >= 20)]
        x = np.array([interval.mid for interval in grouped[energy_column]]) - 17.75
        u = np.log(np.array([interval.mid for interval in grouped["r_core"]]) / 600.0)
        design = np.column_stack([np.ones_like(x), x, u, u ** 2, x * u])
        weights = np.sqrt(grouped["count"].to_numpy())
        coefficients, *_ = np.linalg.lstsq(design * weights[:, None],
                                           np.log(grouped["mean"].to_numpy()) * weights, rcond=None)
        x_rows = band[energy_column].to_numpy() - 17.75
        u_rows = np.log(np.clip(band["r_core"].to_numpy(), 50, None) / 600.0)
        design_rows = np.column_stack([np.ones_like(x_rows), x_rows, u_rows, u_rows ** 2, x_rows * u_rows])
        table.loc[in_band, "n_reference"] = np.exp(design_rows @ coefficients)
    return table


# %% [markdown]
# ### Grid driver
#
# `AnalysisOptions` holds everything a systematic variation may change. `scan_grid`
# returns a tidy DataFrame with one row per cell.

# %%
@dataclass
class AnalysisOptions:
    signal_mode: str = "mean"            # "mean" or "ldf_ratio"
    n_phi_bins: int = N_PHI_BINS
    r_edges: np.ndarray = field(default_factory=lambda: R_EDGES.copy())
    theta_edges: np.ndarray = field(default_factory=lambda: THETA_EDGES.copy())
    data_energy_shift: float = 0.0       # added to the data band edges (energy-scale systematic)
    phase: str = "both"                  # "both", "PhaseI" or "PhaseII"
    only_three_module_counters: bool = False
    clip_negative_counts: bool = False
    reweight_mc_spectrum: bool = True
    n_bootstrap: int = N_BOOTSTRAP


def select_field_sample(options, energy_band):
    lo = energy_band["lo"] + options.data_energy_shift
    hi = energy_band["hi"] + options.data_energy_shift
    table = data_clean[(data_clean["logE_REC"] >= lo) & (data_clean["logE_REC"] < hi)]
    if options.phase == "PhaseI":
        table = table[table["subset"] == SUBSET_PHASE_I]
    if options.phase == "PhaseII":
        table = table[table["subset"] == SUBSET_PHASE_II]
    return table


def prepare_signal(table, options, energy_column):
    """Return a copy with columns `signal` and `weight` filled according to the options."""
    table = table.copy()
    if options.only_three_module_counters:
        table = table[table["counter_n_modules"] == 3]
    signal = table["nMuones_REC"].to_numpy(dtype=float)
    if options.clip_negative_counts:
        signal = np.clip(signal, 0.0, None)
    table["signal"] = signal
    if options.signal_mode == "ldf_ratio":
        table = add_ldf_reference(table, energy_column, options.theta_edges)
        table["signal"] = table["signal"] / table["n_reference"]
        table = table[np.isfinite(table["signal"])]
    if "event_weight" in table and options.reweight_mc_spectrum:
        table["weight"] = table["event_weight"]
    else:
        table["weight"] = 1.0
    return table


def scan_grid(table, sample_label, options, energy_band_name, keep_profiles=False):
    """Fit every (theta, r) cell of an already-prepared table."""
    rng = np.random.default_rng(RANDOM_SEED)
    theta_index = np.digitize(table["theta_REC"].to_numpy(), options.theta_edges) - 1
    r_index = np.digitize(table["r_core"].to_numpy(), options.r_edges) - 1
    n_theta = len(options.theta_edges) - 1
    n_r = len(options.r_edges) - 1
    in_grid = (theta_index >= 0) & (theta_index < n_theta) & (r_index >= 0) & (r_index < n_r)
    table = table[in_grid].assign(theta_index=theta_index[in_grid], r_index=r_index[in_grid])

    rows = []
    for (t_i, r_i), cell in table.groupby(["theta_index", "r_index"]):
        result = fit_cell(cell["phi_deg"].to_numpy(), cell["signal"].to_numpy(),
                          cell["event_id"].to_numpy(), cell["weight"].to_numpy(),
                          n_phi_bins=options.n_phi_bins, n_bootstrap=options.n_bootstrap, rng=rng)
        if result is None:
            continue
        row = {
            "sample": sample_label, "energy_band": energy_band_name,
            "theta_lo": float(options.theta_edges[t_i]), "theta_hi": float(options.theta_edges[t_i + 1]),
            "r_lo": float(options.r_edges[r_i]), "r_hi": float(options.r_edges[r_i + 1]),
        }
        for key in ["A1", "A1_err", "B1", "B1_err", "chi2_ndf", "n_events", "n_modules"]:
            row[key] = result[key]
        if keep_profiles:
            row["profile"] = result
        rows.append(row)
    return pd.DataFrame(rows)


def scan_field_data(options, energy_band, label="data", keep_profiles=False):
    table = select_field_sample(options, energy_band)
    table = prepare_signal(table, options, "logE_REC")
    return scan_grid(table, label, options, energy_band["name"], keep_profiles)


def scan_mc(sample_key, options, keep_profiles=False):
    table = prepare_signal(mc_by_sample[sample_key], options, "logE_MC")
    return scan_grid(table, sample_key, options, MAIN_ENERGY_BAND["name"], keep_profiles)


# %% [markdown]
# ## 4b. Continuity check 1 — field data: reproduce the earlier audit's cell
#
# The data audit (`claude_work/auditoria_datos_campo_cap7/`) quoted, for Phase II,
# lgE ∈ [18.0, 18.5), θ ∈ [40°, 60°), r ∈ [750, 1050) m: A1 = +0.062 ± 0.014.

# %%
def field_cell(phase_subset, lge_lo, lge_hi, theta_lo, theta_hi, r_lo, r_hi):
    selection = (
        (data_clean["subset"] == phase_subset)
        & (data_clean["logE_REC"] >= lge_lo) & (data_clean["logE_REC"] < lge_hi)
        & (data_clean["theta_REC"] >= theta_lo) & (data_clean["theta_REC"] < theta_hi)
        & (data_clean["r_core"] >= r_lo) & (data_clean["r_core"] < r_hi)
    )
    return data_clean[selection]


replication = field_cell(SUBSET_PHASE_II, 18.0, 18.5, 40, 60, 750, 1050)
replication_fit = fit_cell(replication["phi_deg"].to_numpy(), replication["nMuones_REC"].to_numpy(),
                           replication["event_id"].to_numpy())
print(f"Phase II replication cell: A1 = {replication_fit['A1']:+.3f} ± {replication_fit['A1_err']:.3f}"
      f"   (audit: +0.062 ± 0.014),  B1 = {replication_fit['B1']:+.3f} ± {replication_fit['B1_err']:.3f},"
      f"  N_events = {replication_fit['n_events']}")

# %% [markdown]
# ## 4c. Continuity check 2 — MC azimuth convention and the Chapter 6 estimator
#
# (a) The REC azimuth `phi_deg` must track the true shower-plane azimuth (Chapter 6
#     `phi_MC_Truth`), apart from the reconstruction smearing.
# (b) With the Chapter 6 choices (θ_MC binning, no spectrum reweighting, fit of
#     1 + A1 cos φ with SEM errors), the Chapter 6 estimator and `fit_cell` must give
#     the same A1 within errors.

# %%
proton = mc_by_sample["sib_proton"]
far_from_core = proton["r_core_MC"] > 400
azimuth_difference = wrap_degrees(proton["phi_deg"] - proton["phi_true_deg"])[far_from_core]
print(f"|phi_REC - phi_true| for r > 400 m: median {azimuth_difference.abs().median():.1f} deg, "
      f"{100 * (azimuth_difference.abs() < 20).mean():.1f}% within 20 deg")


def chapter6_style_fit(cell):
    """The estimator of plots_seccion_6.py: bin means / their average, fit 1 + A1 cos(phi), SEM errors."""
    phi_edges = np.linspace(-180, 180, 13)
    phi_centers = 0.5 * (phi_edges[1:] + phi_edges[:-1])
    binned = cell.groupby(pd.cut(cell["phi_deg"], phi_edges), observed=False)["nMuones_REC"].agg(["mean", "sem"])
    normalisation = np.nanmean(binned["mean"].to_numpy())
    y = binned["mean"].to_numpy() / normalisation
    y_err = binned["sem"].to_numpy() / normalisation

    def model(phi, a1):
        return 1.0 + a1 * np.cos(np.deg2rad(phi))

    best, covariance = curve_fit(model, phi_centers, y, sigma=y_err, absolute_sigma=True)
    return best[0], np.sqrt(covariance[0, 0])


continuity_rows = []
in_theta_mc = (proton["theta_MC"] >= 40) & (proton["theta_MC"] < 50)
for r_lo in [450, 600, 750, 900, 1050]:
    cell = proton[in_theta_mc & (proton["r_core"] >= r_lo) & (proton["r_core"] < r_lo + 150)]
    a1_ch6, err_ch6 = chapter6_style_fit(cell)
    ours = fit_cell(cell["phi_deg"].to_numpy(), cell["nMuones_REC"].to_numpy(), cell["event_id"].to_numpy())
    continuity_rows.append({"r_lo": r_lo, "A1_cap6": a1_ch6, "err_cap6_SEM": err_ch6,
                            "A1_this": ours["A1"], "err_this_bootstrap": ours["A1_err"]})
continuity_table = pd.DataFrame(continuity_rows)
continuity_table.to_csv(os.path.join(RESULTS_DIR, "continuidad_cap6.csv"), index=False)
continuity_table.round(3)

# %% [markdown]
# ## 5. Field-data results on the fixed grid
#
# Main energy band 17.5–18.0 (the MC band), Phase I and Phase II separately and
# combined; the other energy bands are used in Section 8.

# %%
main_options = AnalysisOptions()
t0 = time.time()
grid_data = scan_field_data(main_options, MAIN_ENERGY_BAND, label="data", keep_profiles=True)
grid_phase_i = scan_field_data(replace(main_options, phase="PhaseI"), MAIN_ENERGY_BAND, label="data_PhaseI")
grid_phase_ii = scan_field_data(replace(main_options, phase="PhaseII"), MAIN_ENERGY_BAND, label="data_PhaseII")

grid_mc_list = []
for sample in MC_SAMPLES:
    grid_mc_list.append(scan_mc(sample["key"], main_options, keep_profiles=True))
grid_mc = pd.concat(grid_mc_list, ignore_index=True)
print(f"Grid fitted in {time.time() - t0:.0f} s")

columns_to_save = ["sample", "energy_band", "theta_lo", "theta_hi", "r_lo", "r_hi",
                   "A1", "A1_err", "B1", "B1_err", "chi2_ndf", "n_events", "n_modules"]
grid_all = pd.concat([grid_data, grid_phase_i, grid_phase_ii, grid_mc], ignore_index=True)
grid_all[columns_to_save].to_csv(os.path.join(RESULTS_DIR, "grilla_A1_17.5-18.0.csv"), index=False)
grid_data[columns_to_save].round(3)

# %% [markdown]
# ## 6. Null tests
#
# - **B1** (sin term): consistent with zero cell by cell → pull distribution.
# - **Near-vertical showers** (θ < 10°): no early/late side, so A1 ≈ 0.
# - **Phase I vs Phase II**: disjoint events, partly different electronics → pulls.

# %%
def chi2_against_zero(values, errors):
    chi2 = float(np.sum((values / errors) ** 2))
    ndf = len(values)
    return {"chi2": chi2, "ndf": ndf, "p_value": float(sps.chi2.sf(chi2, ndf))}


useful = (grid_data["r_lo"] < 1350)          # beyond 1350 m the cells are sparse
b1_pulls = (grid_data["B1"] / grid_data["B1_err"])[useful]
b1_test = chi2_against_zero(grid_data["B1"][useful].to_numpy(), grid_data["B1_err"][useful].to_numpy())

vertical = grid_data[(grid_data["theta_hi"] <= 10) & useful]
vertical_test = chi2_against_zero(vertical["A1"].to_numpy(), vertical["A1_err"].to_numpy())

phases = grid_phase_i.merge(grid_phase_ii, on=["theta_lo", "theta_hi", "r_lo", "r_hi"], suffixes=("_I", "_II"))
phases = phases[phases["r_lo"] < 1350]
phase_pulls = (phases["A1_I"] - phases["A1_II"]) / np.sqrt(phases["A1_err_I"] ** 2 + phases["A1_err_II"] ** 2)
phase_test = chi2_against_zero((phases["A1_I"] - phases["A1_II"]).to_numpy(),
                               np.sqrt(phases["A1_err_I"] ** 2 + phases["A1_err_II"] ** 2).to_numpy())

null_tests = {
    "B1_all_cells": {**b1_test, "pull_mean": float(b1_pulls.mean()), "pull_std": float(b1_pulls.std())},
    "A1_theta_below_10": vertical_test,
    "PhaseI_vs_PhaseII": {**phase_test, "pull_mean": float(phase_pulls.mean()), "pull_std": float(phase_pulls.std())},
    "chi2_ndf_median_data": float(grid_data["chi2_ndf"][useful].median()),
}
print(json.dumps(null_tests, indent=2))

# %% [markdown]
# ## 7. Global significance in the region fixed from the MC
#
# Region: r ∈ [600, 1200) m, θ ∈ [20°, 55°). The two numbers quoted are
# - χ² of the data cells against A1 = 0 (does an asymmetry exist at all?), and
# - the inverse-variance mean A1 over the region (an average over different
#   (r, θ), so it is a summary number, not a physical constant).
#
# The same summary is computed for every MC sample.

# %%
def in_golden_region(grid):
    return (
        (grid["r_lo"] >= GOLDEN_REGION["r_lo"]) & (grid["r_hi"] <= GOLDEN_REGION["r_hi"])
        & (grid["theta_lo"] >= GOLDEN_REGION["theta_lo"]) & (grid["theta_hi"] <= GOLDEN_REGION["theta_hi"])
    )


def inverse_variance_mean(values, errors):
    weights = 1.0 / errors ** 2
    mean = float(np.sum(weights * values) / np.sum(weights))
    return mean, float(np.sqrt(1.0 / np.sum(weights)))


def golden_summary(grid):
    cells = grid[in_golden_region(grid)]
    mean, error = inverse_variance_mean(cells["A1"].to_numpy(), cells["A1_err"].to_numpy())
    test = chi2_against_zero(cells["A1"].to_numpy(), cells["A1_err"].to_numpy())
    return {"n_cells": int(len(cells)), "A1_mean": mean, "A1_mean_err": error,
            "significance_sigma": mean / error, **test}


golden_rows = []
golden_rows.append({"sample": "data", **golden_summary(grid_data)})
golden_rows.append({"sample": "data_PhaseI", **golden_summary(grid_phase_i)})
golden_rows.append({"sample": "data_PhaseII", **golden_summary(grid_phase_ii)})
for sample in MC_SAMPLES:
    golden_rows.append({"sample": sample["key"],
                        **golden_summary(grid_mc[grid_mc["sample"] == sample["key"]])})
golden_table = pd.DataFrame(golden_rows)
golden_table.to_csv(os.path.join(RESULTS_DIR, "region_dorada.csv"), index=False)
golden_table.round(4)

# %% [markdown]
# ### Phase I / Phase II tension and its effect on the combined number
#
# The Phase I − Phase II pulls (Section 6) scatter more than expected. A PDG-style
# scale factor S = sqrt(χ²/ndf) is applied to the Phase I errors and the two phases
# are re-combined, to see whether the combined golden-region value depends on it.

# %%
scale_factor = np.sqrt(phase_test["chi2"] / phase_test["ndf"])
golden_by_sample = golden_table.set_index("sample")
phase_i_value = golden_by_sample.loc["data_PhaseI", "A1_mean"]
phase_i_error = golden_by_sample.loc["data_PhaseI", "A1_mean_err"] * scale_factor
phase_ii_value = golden_by_sample.loc["data_PhaseII", "A1_mean"]
phase_ii_error = golden_by_sample.loc["data_PhaseII", "A1_mean_err"]
recombined_value, recombined_error = inverse_variance_mean(np.array([phase_i_value, phase_ii_value]),
                                                           np.array([phase_i_error, phase_ii_error]))
phase_combination = {
    "scale_factor_phase_I": float(scale_factor),
    "A1_recombined": recombined_value, "A1_recombined_err": recombined_error,
    "A1_joint_fit": float(golden_by_sample.loc["data", "A1_mean"]),
}
print(json.dumps(phase_combination, indent=2))

# %% [markdown]
# ## 8. Data vs MC and the composition test
#
# For every MC sample: χ² of (data − MC) over the golden cells, with data and MC
# errors added in quadrature (MC statistics are comparable to data statistics here,
# so they cannot be neglected).
#
# **Composition test.** A1 is modelled as linear in lnA between p and Fe,
# A1(lnA) = A1_p + (A1_Fe − A1_p) · lnA / ln 56, cell by cell. The χ²(lnA) profile
# then gives a best value and an interval (Δχ² = 1). The test can only discriminate if
# that interval is clearly narrower than the p–Fe range [0, 4.03]. He is a
# consistency check, since it should sit near lnA = 1.39.

# %%
def compare_with_mc(data_grid, mc_grid, sample_key):
    keys = ["theta_lo", "theta_hi", "r_lo", "r_hi"]
    merged = data_grid[in_golden_region(data_grid)].merge(
        mc_grid[mc_grid["sample"] == sample_key], on=keys, suffixes=("_data", "_mc"))
    difference = merged["A1_data"] - merged["A1_mc"]
    combined_error = np.sqrt(merged["A1_err_data"] ** 2 + merged["A1_err_mc"] ** 2)
    return chi2_against_zero(difference.to_numpy(), combined_error.to_numpy())


def composition_scan(data_grid, mc_grid):
    keys = ["theta_lo", "theta_hi", "r_lo", "r_hi"]
    proton_cells = mc_grid[mc_grid["sample"] == "sib_proton"]
    iron_cells = mc_grid[mc_grid["sample"] == "sib_hierro"]
    merged = data_grid[in_golden_region(data_grid)].merge(proton_cells, on=keys, suffixes=("", "_p"))
    merged = merged.merge(iron_cells, on=keys, suffixes=("", "_fe"))

    lna_grid = np.linspace(-2.0, 7.0, 901)
    chi2_profile = []
    for lna in lna_grid:
        fraction = lna / np.log(56.0)
        prediction = merged["A1_p"] + (merged["A1_fe"] - merged["A1_p"]) * fraction
        prediction_err2 = ((1 - fraction) * merged["A1_err_p"]) ** 2 + (fraction * merged["A1_err_fe"]) ** 2
        chi2 = np.sum((merged["A1"] - prediction) ** 2 / (merged["A1_err"] ** 2 + prediction_err2))
        chi2_profile.append(chi2)
    chi2_profile = np.array(chi2_profile)
    best_index = int(np.argmin(chi2_profile))
    inside = lna_grid[chi2_profile <= chi2_profile[best_index] + 1.0]

    separation = merged["A1_fe"] - merged["A1_p"]
    separation_err = np.sqrt(merged["A1_err_p"] ** 2 + merged["A1_err_fe"] ** 2)
    separation_test = chi2_against_zero(separation.to_numpy(), separation_err.to_numpy())
    mean_separation, mean_separation_err = inverse_variance_mean(separation.to_numpy(), separation_err.to_numpy())
    return {
        "lnA_best": float(lna_grid[best_index]),
        "lnA_interval_lo": float(inside.min()), "lnA_interval_hi": float(inside.max()),
        "chi2_min": float(chi2_profile[best_index]), "n_cells": int(len(merged)),
        "Fe_minus_p_mean": mean_separation, "Fe_minus_p_mean_err": mean_separation_err,
        "Fe_vs_p_chi2": separation_test["chi2"], "Fe_vs_p_p_value": separation_test["p_value"],
        "lnA_grid": lna_grid, "chi2_profile": chi2_profile,
    }


comparison_rows = []
for sample in MC_SAMPLES:
    comparison_rows.append({"sample": sample["key"], **compare_with_mc(grid_data, grid_mc, sample["key"])})
comparison_table = pd.DataFrame(comparison_rows)
comparison_table.to_csv(os.path.join(RESULTS_DIR, "datos_vs_mc.csv"), index=False)

composition = composition_scan(grid_data, grid_mc)
composition_summary = {key: value for key, value in composition.items() if not isinstance(value, np.ndarray)}
print(comparison_table.round(3))
print(json.dumps(composition_summary, indent=2))

# %% [markdown]
# ### Near-core region: why A1 < 0 there, in data and in MC
#
# In the MC the true and reconstructed distances of each station are both known.
# The mean of r_REC − r_MC as a function of the true azimuth shows which way the
# reconstructed core moves. If it moves towards the early side (φ = 0), the early
# stations look closer than they are. In a fixed bin of reconstructed r they are
# then truly farther away, and so carry fewer muons. That pushes A1 down, most
# strongly near the core, where the LDF is steepest in ln r.

# %%
core_shift_rows = []
phi_edges_core = np.linspace(-180, 180, 13)
for key in ["sib_proton", "sib_hierro"]:
    table = mc_by_sample[key]
    for theta_lo, theta_hi in [(20, 40), (40, 55)]:
        stations = table[(table["theta_MC"] >= theta_lo) & (table["theta_MC"] < theta_hi)
                         & (table["r_core_MC"] > 200) & (table["r_core_MC"] < 1200)]
        stations = stations.drop_duplicates(["event_id", "counterId"])
        shift = (stations["r_core"] - stations["r_core_MC"]).groupby(
            pd.cut(stations["phi_true_deg"], phi_edges_core), observed=True).mean()
        for interval, value in shift.items():
            core_shift_rows.append({"sample": key, "theta": f"{theta_lo}-{theta_hi}",
                                    "phi_true_center": interval.mid, "mean_r_rec_minus_r_mc": value})
core_shift_table = pd.DataFrame(core_shift_rows)
core_shift_table.to_csv(os.path.join(RESULTS_DIR, "corrimiento_nucleo_mc.csv"), index=False)
core_shift_table.pivot_table(index="phi_true_center", columns=["sample", "theta"],
                             values="mean_r_rec_minus_r_mc").round(1)

# %% [markdown]
# ## 9. Energy evolution (field data only)
#
# The MC exists only at 17.5–18.0, so the other bands are data alone. The
# 17.0–17.5 band is below full SD-750 efficiency and is shown only to document why
# the earlier energy-integrated scan looked different.

# %%
energy_grids = []
for band in ENERGY_BANDS:
    energy_grids.append(scan_field_data(main_options, band, label="data"))
grid_energy = pd.concat(energy_grids, ignore_index=True)
grid_energy[columns_to_save].to_csv(os.path.join(RESULTS_DIR, "grilla_A1_bandas_energia.csv"), index=False)

energy_rows = []
for band in ENERGY_BANDS:
    band_grid = grid_energy[grid_energy["energy_band"] == band["name"]]
    energy_rows.append({"energy_band": band["name"], **golden_summary(band_grid)})
energy_table = pd.DataFrame(energy_rows)

# Same summary with the LDF-ratio estimator, which removes the r / energy mixing
# inside each cell: if the rise with energy were a mixing artefact it would change here.
ratio_options = AnalysisOptions(signal_mode="ldf_ratio")
ratio_values = []
ratio_errors = []
for band in ENERGY_BANDS:
    ratio_grid = scan_field_data(ratio_options, band, label="data")
    ratio_summary = golden_summary(ratio_grid)
    ratio_values.append(ratio_summary["A1_mean"])
    ratio_errors.append(ratio_summary["A1_mean_err"])
energy_table["A1_mean_ldf_ratio"] = ratio_values
energy_table["A1_mean_err_ldf_ratio"] = ratio_errors
energy_table.to_csv(os.path.join(RESULTS_DIR, "region_dorada_por_energia.csv"), index=False)
energy_table.round(4)

# %% [markdown]
# ### Is the rise with energy also in the MC?
#
# The MC cannot follow the data above 18.0, but the library is half a decade wide,
# so the slope can be compared *inside* 17.5–18.0. Both halves of the band are fitted
# for the data (by reconstructed energy) and for p and Fe (by true energy). The MC
# slope includes the improvement of the reconstruction with energy, as the data does.

# %%
def scan_mc_energy_slice(sample_key, options, lge_lo, lge_hi):
    table = mc_by_sample[sample_key]
    table = table[(table["logE_MC"] >= lge_lo) & (table["logE_MC"] < lge_hi)]
    table = prepare_signal(table, options, "logE_MC")
    return scan_grid(table, sample_key, options, f"{lge_lo}-{lge_hi}")


HALF_BANDS = [{"name": "17.50-17.75", "lo": 17.5, "hi": 17.75}, {"name": "17.75-18.00", "lo": 17.75, "hi": 18.0}]
slope_rows = []
for half in HALF_BANDS:
    data_half = scan_field_data(main_options, half, label="data")
    slope_rows.append({"sample": "data", "band": half["name"], **golden_summary(data_half)})
    for key in ["sib_proton", "sib_hierro"]:
        mc_half = scan_mc_energy_slice(key, main_options, half["lo"], half["hi"])
        slope_rows.append({"sample": key, "band": half["name"], **golden_summary(mc_half)})
slope_table = pd.DataFrame(slope_rows)

slope_summary = []
for sample_label in ["data", "sib_proton", "sib_hierro"]:
    low = slope_table[(slope_table["sample"] == sample_label) & (slope_table["band"] == "17.50-17.75")].iloc[0]
    high = slope_table[(slope_table["sample"] == sample_label) & (slope_table["band"] == "17.75-18.00")].iloc[0]
    difference = high["A1_mean"] - low["A1_mean"]
    difference_err = np.hypot(high["A1_mean_err"], low["A1_mean_err"])
    slope_summary.append({"sample": sample_label, "A1_low": low["A1_mean"], "A1_high": high["A1_mean"],
                          "delta_A1_per_quarter_decade": difference, "delta_err": difference_err})
slope_summary = pd.DataFrame(slope_summary)
slope_summary.to_csv(os.path.join(RESULTS_DIR, "pendiente_energia_17.5-18.0.csv"), index=False)
slope_summary.round(4)

# %% [markdown]
# ## 10. Systematic variations
#
# Each variation reruns the golden-region summary for data, p and Fe with one
# option changed. Reported: the shift of the data mean A1 with respect to the
# nominal analysis, and whether the data–MC conclusion changes.

# %%
VARIATIONS = [
    {"name": "Nominal", "options": AnalysisOptions()},
    {"name": "Estimador: cociente a LDF media", "options": AnalysisOptions(signal_mode="ldf_ratio")},
    {"name": "8 bines en phi", "options": AnalysisOptions(n_phi_bins=8)},
    {"name": "16 bines en phi", "options": AnalysisOptions(n_phi_bins=16)},
    {"name": "Bordes en r desplazados 75 m", "options": AnalysisOptions(r_edges=R_EDGES + 75)},
    {"name": "Escala de energia +14%", "options": AnalysisOptions(data_energy_shift=+0.057)},
    {"name": "Escala de energia -14%", "options": AnalysisOptions(data_energy_shift=-0.057)},
    {"name": "Solo contadores de 3 modulos", "options": AnalysisOptions(only_three_module_counters=True)},
    {"name": "Conteos negativos -> 0", "options": AnalysisOptions(clip_negative_counts=True)},
    {"name": "Solo Fase I", "options": AnalysisOptions(phase="PhaseI")},
    {"name": "Solo Fase II", "options": AnalysisOptions(phase="PhaseII")},
    {"name": "MC sin repesar espectro", "options": AnalysisOptions(reweight_mc_spectrum=False)},
]

systematic_rows = []
t0 = time.time()
for variation in VARIATIONS:
    options = replace(variation["options"], n_bootstrap=250)
    variation_data = scan_field_data(options, MAIN_ENERGY_BAND)
    variation_mc = pd.concat([scan_mc("sib_proton", options), scan_mc("sib_hierro", options)], ignore_index=True)
    data_summary = golden_summary(variation_data)
    proton_summary = golden_summary(variation_mc[variation_mc["sample"] == "sib_proton"])
    iron_summary = golden_summary(variation_mc[variation_mc["sample"] == "sib_hierro"])
    versus_proton = compare_with_mc(variation_data, variation_mc, "sib_proton")
    versus_iron = compare_with_mc(variation_data, variation_mc, "sib_hierro")
    systematic_rows.append({
        "variation": variation["name"],
        "A1_data": data_summary["A1_mean"], "A1_data_err": data_summary["A1_mean_err"],
        "A1_p": proton_summary["A1_mean"], "A1_p_err": proton_summary["A1_mean_err"],
        "A1_Fe": iron_summary["A1_mean"], "A1_Fe_err": iron_summary["A1_mean_err"],
        "data_vs_p_chi2_ndf": versus_proton["chi2"] / versus_proton["ndf"],
        "data_vs_Fe_chi2_ndf": versus_iron["chi2"] / versus_iron["ndf"],
    })
    print(f"  {variation['name']:<36} done ({time.time() - t0:.0f} s)")

systematics_table = pd.DataFrame(systematic_rows)
nominal_a1 = systematics_table.loc[0, "A1_data"]
systematics_table["shift_data"] = systematics_table["A1_data"] - nominal_a1
systematics_table.to_csv(os.path.join(RESULTS_DIR, "sistematicos.csv"), index=False)
systematics_table.round(4)

# %% [markdown]
# ## 11. Figures for the thesis
#
# Every figure is written to `FIG_DIR` as PDF. Axis labels are in Spanish because
# the figures go into the thesis.

# %%
def save_figure(figure, name):
    path = os.path.join(FIG_DIR, name)
    figure.savefig(path)
    print("saved", path)


# ---- Figure 1: dataset overview ------------------------------------------------
events_main = data_clean[(data_clean["logE_REC"] >= MIN_LOGE_MAIN)].drop_duplicates("event_id")

figure, axes = plt.subplots(1, 3, figsize=(15, 4.2))
monthly = events_main.groupby(["subset", "year", "month"], observed=True).size().reset_index(name="n")
monthly["date"] = pd.to_datetime(dict(year=monthly["year"], month=monthly["month"], day=15))
subset_style = {
    SUBSET_PHASE_I: {"color": "#4169e1", "label": "Fase I"},
    SUBSET_PHASE_II: {"color": "#b22222", "label": "Fase II (SPMT)"},
}
for subset_name, style in subset_style.items():
    rows = monthly[monthly["subset"] == subset_name].sort_values("date")
    axes[0].plot(rows["date"], rows["n"], marker="o", markersize=3, color=style["color"], label=style["label"])
axes[0].set_xlabel("Fecha")
axes[0].set_ylabel(r"Eventos por mes ($\lg E \geq 17.5$)")
axes[0].legend()
axes[0].tick_params(axis="x", rotation=30)

energy_edges = np.arange(17.5, 19.61, 0.1)
for subset_name, style in subset_style.items():
    energies = events_main.loc[events_main["subset"] == subset_name, "logE_REC"]
    axes[1].hist(energies, bins=energy_edges, histtype="step", linewidth=1.6, color=style["color"], label=style["label"])
axes[1].set_yscale("log")
axes[1].set_xlabel(r"$\lg(E_\mathrm{REC}/\mathrm{eV})$")
axes[1].set_ylabel("Eventos")
axes[1].legend()

cos2_edges = np.linspace(np.cos(np.deg2rad(65)) ** 2, 1, 21)
for subset_name, style in subset_style.items():
    theta = events_main.loc[events_main["subset"] == subset_name, "theta_REC"]
    axes[2].hist(np.cos(np.deg2rad(theta)) ** 2, bins=cos2_edges, histtype="step", linewidth=1.6,
                 color=style["color"], label=style["label"])
axes[2].axvline(np.cos(np.deg2rad(55)) ** 2, color="gray", linestyle="--", linewidth=1)
axes[2].text(np.cos(np.deg2rad(55)) ** 2, axes[2].get_ylim()[1] * 0.9, r" $\theta=55^\circ$", color="gray")
axes[2].set_xlabel(r"$\cos^2\theta_\mathrm{REC}$")
axes[2].set_ylabel("Eventos")
axes[2].legend(loc="lower right")
figure.tight_layout()
save_figure(figure, "cap7_dataset.pdf")
plt.show()

# %%
# ---- Figure 2: azimuthal exposure (module counts per phi bin) -------------------
exposure_sample = data_clean[(data_clean["logE_REC"] >= 17.5) & (data_clean["logE_REC"] < 18.0)
                             & (data_clean["theta_REC"] >= 20) & (data_clean["theta_REC"] < 55)]
phi_edges = np.linspace(-180, 180, 13)
phi_centers = 0.5 * (phi_edges[1:] + phi_edges[:-1])
exposure_bands = [(300, 600), (600, 900), (900, 1200), (1200, 1500)]
exposure_colors = ["#9ecae1", "#4292c6", "#08519c", "#08306b"]   # one hue, light -> dark (magnitude of r)

# The same exposure in the proton MC (REC level, spectrum-weighted). If the MC
# reproduces it, the station selection imposed by the SD trigger is modelled.
exposure_mc = mc_by_sample["sib_proton"]
exposure_mc = exposure_mc[(exposure_mc["theta_REC"] >= 20) & (exposure_mc["theta_REC"] < 55)]


def first_harmonic_of_exposure(phi_deg, weights):
    return float(2.0 * np.sum(weights * np.cos(np.deg2rad(phi_deg))) / np.sum(weights))


exposure_rows = []
figure, axes = plt.subplots(1, 2, figsize=(12, 4.2))
for (r_lo, r_hi), color in zip(exposure_bands, exposure_colors):
    in_band = exposure_sample[(exposure_sample["r_core"] >= r_lo) & (exposure_sample["r_core"] < r_hi)]
    counts, _ = np.histogram(in_band["phi_deg"], bins=phi_edges)
    axes[0].plot(phi_centers, counts / counts.mean(), marker="o", color=color, label=f"{r_lo}-{r_hi} m")
    in_band_mc = exposure_mc[(exposure_mc["r_core"] >= r_lo) & (exposure_mc["r_core"] < r_hi)]
    counts_mc, _ = np.histogram(in_band_mc["phi_deg"], bins=phi_edges, weights=in_band_mc["event_weight"])
    axes[0].plot(phi_centers, counts_mc / counts_mc.mean(), linestyle="--", color=color, linewidth=1.2)
    exposure_rows.append({
        "r_band": f"{r_lo}-{r_hi}",
        "c1_data": first_harmonic_of_exposure(in_band["phi_deg"], np.ones(len(in_band))),
        "c1_mc_proton": first_harmonic_of_exposure(in_band_mc["phi_deg"], in_band_mc["event_weight"]),
    })
    mean_r = in_band.groupby(pd.cut(in_band["phi_deg"], phi_edges), observed=False)["r_core"].mean()
    axes[1].plot(phi_centers, mean_r - mean_r.mean(), marker="o", color=color, label=f"{r_lo}-{r_hi} m")
axes[0].axhline(1, color="gray", linewidth=1, linestyle=":")
axes[0].set_xlabel(r"$\phi$ en el plano de la lluvia [$^\circ$]")
axes[0].set_ylabel(r"Módulos por bin / media")
axes[0].plot([], [], color="gray", linestyle="-", marker="o", label="Datos")
axes[0].plot([], [], color="gray", linestyle="--", label="MC p (SIBYLL 2.3e)")
axes[0].legend(title=r"$r$", fontsize=9, ncol=2)
axes[1].axhline(0, color="gray", linewidth=1, linestyle=":")
axes[1].set_xlabel(r"$\phi$ en el plano de la lluvia [$^\circ$]")
axes[1].set_ylabel(r"$\langle r\rangle_\phi - \langle r\rangle$ [m]")
axes[1].legend(title=r"$r$", fontsize=10)
for axis in axes:
    axis.set_xlim(-180, 180)
    axis.set_xticks(np.arange(-180, 181, 60))
figure.tight_layout()
save_figure(figure, "cap7_exposicion_phi.pdf")
plt.show()
exposure_table = pd.DataFrame(exposure_rows)
exposure_table.to_csv(os.path.join(RESULTS_DIR, "exposicion_c1.csv"), index=False)
exposure_table.round(3)

# %%
# ---- Figure 3: one cell, data with fit, and the p / Fe fits ----------------------
EXAMPLE_CELL = {"theta_lo": 20.0, "r_lo": 750.0}


def find_profile(grid, sample_label):
    row = grid[(grid["sample"] == sample_label) & (grid["theta_lo"] == EXAMPLE_CELL["theta_lo"])
               & (grid["r_lo"] == EXAMPLE_CELL["r_lo"])].iloc[0]
    return row


figure, axis = plt.subplots(figsize=(7.5, 5))
data_row = find_profile(grid_data, "data")
profile = data_row["profile"]
axis.errorbar(profile["phi_centers"], profile["bin_means"], yerr=profile["bin_errors"], fmt="o",
              color="black", capsize=3, label="Datos")
phi_smooth = np.linspace(-180, 180, 300)
axis.plot(phi_smooth, 1 + data_row["A1"] * np.cos(np.deg2rad(phi_smooth)) + data_row["B1"] * np.sin(np.deg2rad(phi_smooth)),
          color="black", linewidth=1.6,
          label=rf"Ajuste datos: $A_1={data_row['A1']:.3f}\pm{data_row['A1_err']:.3f}$")
for key in ["sib_proton", "sib_hierro"]:
    mc_row = find_profile(grid_mc, key)
    style = MC_STYLE[key]
    axis.plot(phi_smooth, 1 + mc_row["A1"] * np.cos(np.deg2rad(phi_smooth)), color=style["color"],
              linestyle=style["linestyle"], linewidth=1.6,
              label=rf"{style['label']}: $A_1={mc_row['A1']:.3f}\pm{mc_row['A1_err']:.3f}$")
axis.axhline(1, color="gray", linewidth=1, linestyle=":")
axis.set_xlim(-180, 180)
axis.set_xticks(np.arange(-180, 181, 45))
axis.set_xlabel(r"$\phi$ en el plano de la lluvia [$^\circ$]")
axis.set_ylabel(r"$\langle N_\mu^\mathrm{REC}\rangle_\phi / \rho_0$")
axis.set_title(r"$17.5\leq\lg E<18.0$,  $20^\circ\leq\theta<30^\circ$,  $750\leq r<900$ m", fontsize=12)
axis.set_ylim(0.88, 1.22)
axis.legend(fontsize=9, loc="upper left")
figure.tight_layout()
save_figure(figure, "cap7_ejemplo_ajuste.pdf")
plt.show()

# %%
# ---- Figure 4: A1(r) by zenith band, data vs MC ---------------------------------
def plot_a1_vs_r(axis, grid, sample_label, style, offset, r_max=1350):
    rows = grid[(grid["sample"] == sample_label) & (grid["r_lo"] < r_max)].sort_values("r_lo")
    r_center = 0.5 * (rows["r_lo"] + rows["r_hi"]) + offset
    axis.errorbar(r_center, rows["A1"], yerr=rows["A1_err"], **style)


theta_bands = list(zip(THETA_EDGES[:-1], THETA_EDGES[1:]))
figure, axes = plt.subplots(2, 4, figsize=(17, 8), sharex=True, sharey=True)
axes = axes.ravel()
for panel_index, (theta_lo, theta_hi) in enumerate(theta_bands):
    axis = axes[panel_index]
    in_band_data = grid_data[grid_data["theta_lo"] == theta_lo]
    in_band_mc = grid_mc[grid_mc["theta_lo"] == theta_lo]
    offsets = {"sib_proton": -24, "sib_helio": -8, "sib_hierro": 8, "qgs_helio": 24}
    for sample in MC_SAMPLES:
        style = {"fmt": sample["marker"], "color": sample["color"], "markersize": 5, "capsize": 2,
                 "linestyle": "none", "alpha": 0.85, "label": sample["label"]}
        plot_a1_vs_r(axis, in_band_mc, sample["key"], style, offsets[sample["key"]])
    data_style = {"fmt": "o", "color": "black", "markersize": 6, "capsize": 3, "linestyle": "none",
                  "label": "Datos (Fase I + II)", "zorder": 5}
    if theta_lo >= MAX_THETA_MAIN:
        data_style["markerfacecolor"] = "white"
        data_style["label"] = "Datos (fuera de la calibración estándar)"
    plot_a1_vs_r(axis, in_band_data, "data", data_style, 0)
    axis.axhline(0, color="gray", linewidth=1, linestyle=":")
    if theta_lo >= GOLDEN_REGION["theta_lo"] and theta_hi <= GOLDEN_REGION["theta_hi"]:
        axis.axvspan(GOLDEN_REGION["r_lo"], GOLDEN_REGION["r_hi"], color="gold", alpha=0.12, linewidth=0)
    axis.set_title(rf"${theta_lo:.0f}^\circ \leq \theta < {theta_hi:.0f}^\circ$", fontsize=12)
    axis.set_ylim(-0.15, 0.25)
    if panel_index >= 4:
        axis.set_xlabel(r"$r$ [m]")
    if panel_index % 4 == 0:
        axis.set_ylabel(r"$A_1$")
handles, labels = axes[0].get_legend_handles_labels()
axes[-1].axis("off")
axes[-1].legend(handles, labels, loc="center", fontsize=11, title=r"$17.5\leq\lg E<18.0$")
figure.tight_layout()
save_figure(figure, "cap7_A1_vs_r_datos_vs_mc.pdf")
plt.show()

# %%
# ---- Figure 5: A1 vs zenith angle in a fixed radial range ------------------------
def a1_vs_theta(grid, sample_label, r_lo, r_hi):
    rows = []
    selection = grid[(grid["sample"] == sample_label) & (grid["r_lo"] >= r_lo) & (grid["r_hi"] <= r_hi)]
    for (theta_lo, theta_hi), cells in selection.groupby(["theta_lo", "theta_hi"]):
        mean, error = inverse_variance_mean(cells["A1"].to_numpy(), cells["A1_err"].to_numpy())
        rows.append({"theta_lo": theta_lo, "theta_hi": theta_hi, "A1": mean, "A1_err": error})
    return pd.DataFrame(rows)


RADIAL_RANGES = [(750, 1050), (300, 450)]
figure, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=False)
theta_offsets = {"sib_proton": -1.2, "sib_helio": -0.4, "sib_hierro": 0.4, "qgs_helio": 1.2}
a1_theta_tables = []
for axis, (r_lo, r_hi) in zip(axes, RADIAL_RANGES):
    for sample in MC_SAMPLES:
        rows = a1_vs_theta(grid_mc, sample["key"], r_lo, r_hi)
        rows["sample"] = sample["key"]
        rows["r_range"] = f"{r_lo}-{r_hi}"
        a1_theta_tables.append(rows)
        center = 0.5 * (rows["theta_lo"] + rows["theta_hi"]) + theta_offsets[sample["key"]]
        axis.errorbar(center, rows["A1"], yerr=rows["A1_err"], fmt=sample["marker"], color=sample["color"],
                      linestyle=sample["linestyle"], linewidth=1.2, markersize=5, capsize=2, alpha=0.85,
                      label=sample["label"])
    rows = a1_vs_theta(grid_data, "data", r_lo, r_hi)
    rows["sample"] = "data"
    rows["r_range"] = f"{r_lo}-{r_hi}"
    a1_theta_tables.append(rows)
    center = 0.5 * (rows["theta_lo"] + rows["theta_hi"])
    is_main = rows["theta_hi"] <= MAX_THETA_MAIN
    axis.errorbar(center[is_main], rows["A1"][is_main], yerr=rows["A1_err"][is_main], fmt="o", color="black",
                  markersize=7, capsize=3, zorder=5, label="Datos (Fase I + II)")
    axis.errorbar(center[~is_main], rows["A1"][~is_main], yerr=rows["A1_err"][~is_main], fmt="o", color="black",
                  markerfacecolor="white", markersize=7, capsize=3, zorder=5, label=r"Datos, $\theta\geq55^\circ$")
    axis.axhline(0, color="gray", linewidth=1, linestyle=":")
    axis.axvspan(MAX_THETA_MAIN, 65, color="gray", alpha=0.08, linewidth=0)
    axis.set_xlabel(r"$\theta_\mathrm{REC}$ [$^\circ$]")
    axis.set_ylabel(r"$A_1$")
    axis.set_title(rf"${r_lo}\leq r<{r_hi}$ m,  $17.5\leq\lg E<18.0$", fontsize=12)
axes[0].legend(fontsize=9, loc="upper left")
figure.tight_layout()
save_figure(figure, "cap7_A1_vs_theta.pdf")
plt.show()
pd.concat(a1_theta_tables).to_csv(os.path.join(RESULTS_DIR, "A1_vs_theta.csv"), index=False)

# %%
# ---- Figure 6: null tests ---------------------------------------------------------
figure, axes = plt.subplots(1, 3, figsize=(16, 4.4))
pull_edges = np.linspace(-4, 4, 17)
gaussian_x = np.linspace(-4, 4, 200)

axes[0].hist(b1_pulls, bins=pull_edges, color="#4169e1", alpha=0.75, edgecolor="white")
axes[0].plot(gaussian_x, len(b1_pulls) * (pull_edges[1] - pull_edges[0]) * sps.norm.pdf(gaussian_x), color="black")
axes[0].set_xlabel(r"$B_1/\sigma_{B_1}$ (datos, todas las celdas)")
axes[0].set_ylabel("Celdas")
axes[0].set_title(rf"media {b1_pulls.mean():+.2f}, ancho {b1_pulls.std():.2f}", fontsize=11)

axes[1].hist(phase_pulls, bins=pull_edges, color="#b22222", alpha=0.75, edgecolor="white")
axes[1].plot(gaussian_x, len(phase_pulls) * (pull_edges[1] - pull_edges[0]) * sps.norm.pdf(gaussian_x), color="black")
axes[1].set_xlabel(r"$(A_1^\mathrm{I}-A_1^\mathrm{II})/\sigma$")
axes[1].set_ylabel("Celdas")
axes[1].set_title(rf"Fase I vs. Fase II: media {phase_pulls.mean():+.2f}, ancho {phase_pulls.std():.2f}", fontsize=11)

vertical_rows = grid_data[(grid_data["theta_hi"] <= 10) & (grid_data["r_lo"] < 1350)]
axes[2].errorbar(0.5 * (vertical_rows["r_lo"] + vertical_rows["r_hi"]), vertical_rows["A1"],
                 yerr=vertical_rows["A1_err"], fmt="o", color="black", capsize=3)
axes[2].axhline(0, color="gray", linewidth=1, linestyle=":")
axes[2].set_xlabel(r"$r$ [m]")
axes[2].set_ylabel(r"$A_1$")
axes[2].set_title(rf"$\theta<10^\circ$: $\chi^2/\mathrm{{ndf}}={vertical_test['chi2']:.1f}/{vertical_test['ndf']}$", fontsize=11)
figure.tight_layout()
save_figure(figure, "cap7_tests_nulos.pdf")
plt.show()

# %%
# ---- Figure 7: golden-region mean A1, data vs every MC sample ---------------------
# The linear p-Fe interpolation of Section 8 is kept in the summary JSON, but it is
# not plotted: the p and Fe predictions coincide within errors, so a chi2(lnA)
# profile would only show MC fluctuations.
figure, axis = plt.subplots(figsize=(7.5, 3.8))
golden_by_sample = golden_table.set_index("sample")
data_mean = golden_by_sample.loc["data", "A1_mean"]
data_error = golden_by_sample.loc["data", "A1_mean_err"]
axis.axvspan(data_mean - data_error, data_mean + data_error, color="black", alpha=0.12, linewidth=0)
axis.axvline(data_mean, color="black", linewidth=1.6)
y_positions = np.arange(len(MC_SAMPLES), 0, -1)
for y_position, sample in zip(y_positions, MC_SAMPLES):
    row = golden_by_sample.loc[sample["key"]]
    axis.errorbar(row["A1_mean"], y_position, xerr=row["A1_mean_err"], fmt=sample["marker"],
                  color=sample["color"], markersize=8, capsize=4)
axis.errorbar(data_mean, 0, xerr=data_error, fmt="o", color="black", markersize=8, capsize=4)
labels = ["Datos (Fase I + II)"]
for sample in reversed(MC_SAMPLES):
    labels.append(sample["label"])
axis.set_yticks(np.arange(0, len(MC_SAMPLES) + 1))
axis.set_yticklabels(labels)
axis.set_ylim(-0.7, len(MC_SAMPLES) + 0.7)
axis.set_xlabel(r"$\langle A_1\rangle$ en la región dorada ($600\leq r<1200$ m, $20^\circ\leq\theta<55^\circ$)")
axis.minorticks_off()
figure.tight_layout()
save_figure(figure, "cap7_composicion.pdf")
plt.show()

# %%
# ---- Figure 8: energy evolution in data --------------------------------------------
energy_styles = [
    {"band": "17.0-17.5", "color": "#9ecae1", "marker": "v", "label": r"$17.0\leq\lg E<17.5$ (eficiencia incompleta)"},
    {"band": "17.5-18.0", "color": "#4292c6", "marker": "o", "label": r"$17.5\leq\lg E<18.0$"},
    {"band": "18.0-18.5", "color": "#08519c", "marker": "s", "label": r"$18.0\leq\lg E<18.5$"},
    {"band": ">=18.5", "color": "#08306b", "marker": "D", "label": r"$\lg E\geq18.5$"},
]
figure, axes = plt.subplots(1, 2, figsize=(13, 4.8))
for offset_index, style in enumerate(energy_styles):
    if style["band"] == ">=18.5":
        continue          # too few events per radial bin for this panel; shown in the right panel
    band_grid = grid_energy[grid_energy["energy_band"] == style["band"]]
    rows = []
    for (r_lo, r_hi), cells in band_grid[(band_grid["theta_lo"] >= 20) & (band_grid["theta_hi"] <= MAX_THETA_MAIN)].groupby(["r_lo", "r_hi"]):
        mean, error = inverse_variance_mean(cells["A1"].to_numpy(), cells["A1_err"].to_numpy())
        rows.append({"r": 0.5 * (r_lo + r_hi), "A1": mean, "A1_err": error})
    rows = pd.DataFrame(rows)
    rows = rows[rows["r"] < 1400]
    axes[0].errorbar(rows["r"] + (offset_index - 1.5) * 12, rows["A1"], yerr=rows["A1_err"], fmt=style["marker"],
                     color=style["color"], markersize=6, capsize=2, linestyle="none", label=style["label"])
axes[0].axhline(0, color="gray", linewidth=1, linestyle=":")
axes[0].set_xlabel(r"$r$ [m]")
axes[0].set_ylabel(r"$A_1$ (media en $20^\circ\leq\theta<55^\circ$)")
axes[0].set_ylim(-0.15, 0.15)
axes[0].legend(fontsize=9)

band_centers = {"17.0-17.5": 17.25, "17.5-18.0": 17.75, "18.0-18.5": 18.25, ">=18.5": 18.75}
for _, row in energy_table.iterrows():
    is_full_efficiency = row["energy_band"] != "17.0-17.5"
    marker_face = "black" if is_full_efficiency else "white"
    axes[1].errorbar(band_centers[row["energy_band"]], row["A1_mean"], yerr=row["A1_mean_err"], fmt="o",
                     color="black", markerfacecolor=marker_face, markersize=7, capsize=3)
for _, row in energy_table.iterrows():
    axes[1].errorbar(band_centers[row["energy_band"]] + 0.05, row["A1_mean_ldf_ratio"], yerr=row["A1_mean_err_ldf_ratio"],
                     fmt="s", color="gray", markerfacecolor="white", markersize=6, capsize=3)
axes[1].errorbar([], [], fmt="o", color="black", label="Datos, estimador nominal")
axes[1].errorbar([], [], fmt="s", color="gray", markerfacecolor="white", label="Datos, cociente a la LDF media")
golden_proton = golden_table.set_index("sample").loc["sib_proton"]
golden_iron = golden_table.set_index("sample").loc["sib_hierro"]
for summary, key in [(golden_proton, "sib_proton"), (golden_iron, "sib_hierro")]:
    style = MC_STYLE[key]
    axes[1].errorbar(17.75 + (0.04 if key == "sib_hierro" else -0.04), summary["A1_mean"], yerr=summary["A1_mean_err"],
                     fmt=style["marker"], color=style["color"], markersize=6, capsize=3, label=style["label"])
axes[1].axhline(0, color="gray", linewidth=1, linestyle=":")
axes[1].set_xlabel(r"$\lg(E/\mathrm{eV})$")
axes[1].set_ylabel(r"$\langle A_1\rangle$ región dorada")
axes[1].legend(fontsize=9, loc="upper left")
figure.tight_layout()
save_figure(figure, "cap7_evolucion_energia.pdf")
plt.show()

# %%
# ---- Summary JSON (every number quoted in the chapter text) -------------------------
summary = {
    "replication_cell": {key: replication_fit[key] for key in ["A1", "A1_err", "B1", "B1_err", "n_events"]},
    "azimuth_check_median_deg": float(azimuth_difference.abs().median()),
    "null_tests": null_tests,
    "golden_region": GOLDEN_REGION,
    "golden": golden_table.to_dict(orient="records"),
    "data_vs_mc": comparison_table.to_dict(orient="records"),
    "composition": composition_summary,
    "phase_combination": phase_combination,
    "energy_slope_inside_mc_band": slope_summary.to_dict(orient="records"),
    "exposure_c1": exposure_table.to_dict(orient="records"),
    "core_shift_mc": core_shift_table.to_dict(orient="records"),
    "energy_evolution": energy_table.to_dict(orient="records"),
    "cut_flow": cut_flow_table.to_dict(orient="records"),
}
with open(os.path.join(RESULTS_DIR, "resumen_cap7.json"), "w") as handle:
    json.dump(summary, handle, indent=2, default=float)
print("Summary written.")

