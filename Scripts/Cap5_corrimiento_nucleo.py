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
# # Chapter 5: direction of the reconstructed-core shift
#
# **Why this notebook exists.** Figure `fig:bias_core_azimut` of Chapter 5
# (`error_radial_azimut.jpg`) was produced in `validacion_asimetria_infill_sd_mu_v2.py`
# (cell "CHEQUEO DE DESFASE CORE REC vs CORE MC (CON ERRORES)") using
# `phi_plane_euler_MC_true_core` as the azimuth **without** removing the +180 deg offset that the
# same notebook removes everywhere else (`vals_euler - 180`, and `phi_MC_Truth`). If that offset
# is real, the figure's early and late regions are swapped, and the core shift goes towards the
# **early** side, not the late side as written in the chapter.
#
# This notebook settles it without trusting any convention a priori:
#
# 1. **Which azimuth column puts the early region at phi = 0?** The SD signal has a large,
#    well-established positive early-late asymmetry. With the correct convention, the maximum of
#    the azimuthal SD-signal profile must sit at phi ~ 0.
# 2. With the validated convention, measure the radial error
#    $\Delta r = r_{\rm MC} - r_{\rm REC}$ versus azimuth and fit
#    $\Delta r(\phi) = a + b\cos\phi$. If $b > 0$, early stations are reconstructed closer to the
#    core than they are ($r_{\rm REC} < r_{\rm MC}$), i.e. the reconstructed core is displaced
#    towards the early region by $\simeq b$.
# 3. Redraw the thesis figure with the validated azimuth.
#
# Data: the same parquet files as the original figure (SIBYLL 2.3e protons, lg E = 17.5-18.0).
# Runs in well under a minute with the repository `venv`.

# %%
import glob
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 0. Paths and selection

# %%
def find_repo_root(start):
    folder = Path(start).resolve()
    while not (folder / "Tesis - Latex").is_dir():
        if folder.parent == folder:
            raise FileNotFoundError("Could not find the repository root from " + str(start))
        folder = folder.parent
    return folder


REPO_ROOT = find_repo_root(Path.cwd())
FIGURE_DIR = REPO_ROOT / "Tesis - Latex" / "capitulos" / "imagenes_capitulos" / "cap5"
TABLE_DIR = REPO_ROOT / "Scripts" / "resultados_cap5_corrimiento_nucleo"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

# Same simulation set as the original figure (this machine's local path).
PARQUET_FOLDER = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/"

# Same selection as the original figure: Infill stations, 0 < r_REC < 1400 m.
R_MAX_m = 1400.0
# The original figure used theta_MC in [20, 30) deg; we also show steeper bins.
ZENITH_BINS_deg = [(20.0, 30.0), (30.0, 40.0), (40.0, 50.0)]

# %% [markdown]
# ## 1. Load: one row per SD station per event
#
# Each parquet row is a UMD module; several modules share one SD station. The radial distances
# and the SD signal are station quantities, so we keep one row per (event, station).

# %%
COLUMNS = ["event_id", "run_number", "theta_MC", "counterId", "sdId", "sdSignal_REC",
           "r_core", "r_core_MC", "phi_plane_euler_MC_true_core"]

tables = []
for path in sorted(glob.glob(PARQUET_FOLDER + "*.parquet")):
    tables.append(pd.read_parquet(path, columns=COLUMNS))
modules = pd.concat(tables, ignore_index=True)

infill = modules[modules["counterId"] >= 100000]
stations = infill.drop_duplicates(subset=["run_number", "event_id", "sdId"]).copy()
stations = stations[(stations["r_core"] > 0) & (stations["r_core"] < R_MAX_m)]
print("Modules: {:,}   stations (one per event): {:,}".format(len(infill), len(stations)))


def wrap_degrees(angle_deg):
    return (angle_deg + 180.0) % 360.0 - 180.0


def to_degrees(series):
    values = series.to_numpy(dtype=float)
    if np.nanmax(np.abs(values)) < 7.0:   # stored in radians
        values = np.rad2deg(values)
    return values


# The two candidate conventions for the Euler azimuth, wrapped to [-180, 180):
#   phi_euler_raw      - as used in the original figure;
#   phi_euler_minus180 - removing the +180 deg offset, as in the rest of the original notebook.
stations["phi_euler_raw"] = wrap_degrees(to_degrees(stations["phi_plane_euler_MC_true_core"]))
stations["phi_euler_minus180"] = wrap_degrees(stations["phi_euler_raw"] - 180.0)

# %% [markdown]
# ## 2. Which convention puts the early region at phi = 0?
#
# For each convention we fit the SD signal with a free-phase first harmonic
# $1 + a\cos\phi + b\sin\phi$ and report the azimuth of the maximum,
# $\phi_{\max} = \operatorname{atan2}(b, a)$. The correct convention gives $\phi_{\max}\simeq 0$.
#
# The signal is normalised **within each event**: each station is divided by the mean signal of
# the stations of the same event in the same 100 m radial band (bands with fewer than three
# stations are dropped). Normalising across events would let the energy spread of the showers
# dominate the profile. The bands use the **true** distance $r_{\rm MC}$ (200-1000 m): with
# $r_{\rm REC}$, the very core shift under study mixes distances within a band and washes the
# profile out.

# %%
def free_phase_harmonic(phi_deg, values):
    phi = np.deg2rad(phi_deg)
    design = np.column_stack([np.ones_like(phi), np.cos(phi), np.sin(phi)])
    coefficients, _, _, _ = np.linalg.lstsq(design, values, rcond=None)
    constant, cos_term, sin_term = coefficients
    return {"amplitude": np.hypot(cos_term, sin_term) / constant,
            "phi_max_deg": np.rad2deg(np.arctan2(sin_term, cos_term))}


RADIAL_BAND_EDGES_m = np.arange(200.0, 1001.0, 100.0)
check = stations[(stations["r_core_MC"] > 200.0) & (stations["r_core_MC"] < 1000.0)].copy()
check["radial_band"] = pd.cut(check["r_core_MC"], RADIAL_BAND_EDGES_m)
event_band = check.groupby(["run_number", "event_id", "radial_band"], observed=True)
band_mean = event_band["sdSignal_REC"].transform("mean")
band_count = event_band["sdSignal_REC"].transform("count")
check["sd_signal_normalised"] = check["sdSignal_REC"] / band_mean
check.loc[(band_count < 3) | (band_mean <= 0), "sd_signal_normalised"] = np.nan

rows = []
for zenith_low, zenith_high in ZENITH_BINS_deg:
    in_bin = (check["theta_MC"] >= zenith_low) & (check["theta_MC"] < zenith_high)
    subset = check[in_bin & check["sd_signal_normalised"].notna()]
    for column in ["phi_euler_raw", "phi_euler_minus180"]:
        fit = free_phase_harmonic(subset[column].to_numpy(),
                                  subset["sd_signal_normalised"].to_numpy())
        rows.append({"zenith_bin": "{:.0f}-{:.0f}".format(zenith_low, zenith_high),
                     "convention": column, "n_stations": len(subset),
                     "sd_amplitude": fit["amplitude"],
                     "phi_of_maximum_deg": fit["phi_max_deg"]})
convention_check = pd.DataFrame(rows)
convention_check.to_csv(TABLE_DIR / "chequeo_convencion_azimut.csv", index=False)
print(convention_check.round(3).to_string(index=False))

# %% [markdown]
# ## 3. Radial error versus azimuth with the validated convention
#
# Fit $\Delta r(\phi) = a + b\cos\phi$ (least squares on all stations of the bin). With
# $\Delta r = r_{\rm MC} - r_{\rm REC}$, $b > 0$ means early stations are reconstructed closer
# to the core than they are: the reconstructed core sits on the **early** side, about $b$ away.

# %%
VALIDATED = "phi_euler_minus180"
stations["delta_r_m"] = stations["r_core_MC"] - stations["r_core"]


def cosine_fit(phi_deg, values):
    phi = np.deg2rad(phi_deg)
    design = np.column_stack([np.ones_like(phi), np.cos(phi)])
    coefficients, residuals, _, _ = np.linalg.lstsq(design, values, rcond=None)
    n_points = len(values)
    sigma2 = residuals[0] / (n_points - 2) if len(residuals) else np.nan
    covariance = sigma2 * np.linalg.inv(design.T @ design)
    return {"offset_m": coefficients[0], "cos_amplitude_m": coefficients[1],
            "cos_amplitude_err_m": np.sqrt(covariance[1, 1])}


rows = []
for zenith_low, zenith_high in ZENITH_BINS_deg:
    in_bin = (stations["theta_MC"] >= zenith_low) & (stations["theta_MC"] < zenith_high)
    subset = stations[in_bin & stations["delta_r_m"].notna()]
    for column in ["phi_euler_raw", VALIDATED]:
        fit = cosine_fit(subset[column].to_numpy(), subset["delta_r_m"].to_numpy())
        rows.append({"zenith_bin": "{:.0f}-{:.0f}".format(zenith_low, zenith_high),
                     "convention": column, "n_stations": len(subset), **fit})
shift_fits = pd.DataFrame(rows)
shift_fits.to_csv(TABLE_DIR / "ajuste_corrimiento_nucleo.csv", index=False)
print(shift_fits.round(2).to_string(index=False))

# %% [markdown]
# ## 4. Figure for the chapter
#
# One panel per zenith bin. Each panel shows every station as a point (the cloud), the mean
# radial error per azimuthal bin with error bars of $\pm 1\sigma$ (the spread of the stations
# in that bin; the standard error of the mean is smaller than the markers), and the fitted
# $a + b\cos\phi$, where $b$ is the displacement of the reconstructed core towards the early
# region.

# %%
AZIMUTH_BIN_EDGES_deg = np.linspace(-180.0, 180.0, 19)
azimuth_centres = 0.5 * (AZIMUTH_BIN_EDGES_deg[1:] + AZIMUTH_BIN_EDGES_deg[:-1])
phi_curve_deg = np.linspace(-180.0, 180.0, 361)

ZENITH_STYLES = {
    "20-30": {"color": "tab:blue", "marker": "o"},
    "30-40": {"color": "tab:orange", "marker": "s"},
    "40-50": {"color": "tab:red", "marker": "^"},
}

profile_rows = []
fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.4), sharey=True)
for ax, (zenith_low, zenith_high) in zip(axes, ZENITH_BINS_deg):
    label_bin = "{:.0f}-{:.0f}".format(zenith_low, zenith_high)
    style = ZENITH_STYLES[label_bin]
    in_bin = (stations["theta_MC"] >= zenith_low) & (stations["theta_MC"] < zenith_high)
    subset = stations[in_bin & stations["delta_r_m"].notna()].copy()

    # Cloud: every station of the bin.
    ax.scatter(subset[VALIDATED], subset["delta_r_m"], s=2, alpha=0.08, color=style["color"],
               rasterized=True)

    # Mean +- 1 sigma per azimuthal bin.
    subset["azimuth_bin"] = pd.cut(subset[VALIDATED], AZIMUTH_BIN_EDGES_deg)
    grouped = subset.groupby("azimuth_bin", observed=False)["delta_r_m"]
    means = grouped.mean().to_numpy()
    spreads = grouped.std().to_numpy()
    standard_errors = (grouped.std() / np.sqrt(grouped.count())).to_numpy()
    for centre, mean, spread, error in zip(azimuth_centres, means, spreads, standard_errors):
        profile_rows.append({"zenith_bin": label_bin, "phi_deg": centre,
                             "delta_r_mean_m": mean, "delta_r_std_m": spread,
                             "delta_r_sem_m": error})
    ax.errorbar(azimuth_centres, means, yerr=spreads, color="black",
                markerfacecolor=style["color"], marker=style["marker"], markersize=5,
                capsize=2, linewidth=1.0, linestyle="none", label="media $\\pm 1\\sigma$")

    # Fitted a + b cos(phi).
    fit_row = shift_fits[(shift_fits["zenith_bin"] == label_bin)
                         & (shift_fits["convention"] == VALIDATED)].iloc[0]
    curve = fit_row["offset_m"] + fit_row["cos_amplitude_m"] * np.cos(np.deg2rad(phi_curve_deg))
    ax.plot(phi_curve_deg, curve, color="black", linewidth=1.4, linestyle="--",
            label="ajuste $a + b\\cos\\phi$, $b = {:.0f}$ m".format(fit_row["cos_amplitude_m"]))

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlim(-180.0, 180.0)
    ax.set_ylim(-80.0, 80.0)
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.grid(True, alpha=0.3)
    ax.set_title("$\\theta_{{MC}} \\in [{:.0f}^\\circ, {:.0f}^\\circ)$".format(zenith_low,
                                                                         zenith_high),
                 fontsize=11)
    ax.set_xlabel("$\\phi_{MC}$ [grados]")
    ax.text(0.5, 0.97, "temprano", transform=ax.transAxes, ha="center", va="top", fontsize=8,
            color="dimgray")
    ax.text(0.02, 0.97, "tardío", transform=ax.transAxes, ha="left", va="top", fontsize=8,
            color="dimgray")
    ax.text(0.98, 0.97, "tardío", transform=ax.transAxes, ha="right", va="top", fontsize=8,
            color="dimgray")
    ax.legend(fontsize=8, frameon=True, framealpha=0.9, loc="lower center")
axes[0].set_ylabel("$\\Delta r = r_{MC} - r_{REC}$ [m]")
pd.DataFrame(profile_rows).to_csv(TABLE_DIR / "perfil_corrimiento_nucleo.csv", index=False)

fig.tight_layout()
fig.savefig(FIGURE_DIR / "corrimiento_nucleo_azimut.pdf", dpi=200)
plt.show()

# %% [markdown]
# ## 5. What the displacement implies for $A_1$
#
# A core displaced by $\delta$ towards the early region places each station, as seen from the
# reconstructed core, at the wrong distance: early stations look closer than they are, late
# ones farther. When the asymmetry is measured with the **reconstructed geometry** (Infill
# analysis with $r_{\rm REC}$), the falling lateral distribution $\rho\propto r^{-\beta}$ then
# adds a spurious modulation of the opposite sign,
# $\Delta A_1 \simeq -\beta\,\delta/r$. We measure $\beta$ from the muon counts of the same
# stations between 300 and 650 m (true distance) and evaluate the estimate at 450 and 1000 m.
#
# This does **not** apply to the Dense Ring: its stations are placed during the simulation at
# 450 m from the *true* core, so the displacement only changes the azimuth assigned to them, by
# at most $\delta/r \approx 2$--$3^\circ$, and it affects $N^{\rm MC}_\mu$ and $N^{\rm REC}_\mu$
# in the same way.

# %%
muon_columns = ["event_id", "run_number", "theta_MC", "counterId", "sdId", "nMuones_MC",
                "r_core_MC"]
muon_tables = []
for path in sorted(glob.glob(PARQUET_FOLDER + "*.parquet")):
    muon_tables.append(pd.read_parquet(path, columns=muon_columns))
muon_modules = pd.concat(muon_tables, ignore_index=True)
muon_modules = muon_modules[muon_modules["counterId"] >= 100000]
muon_stations = muon_modules.groupby(["run_number", "event_id", "sdId"], as_index=False).agg(
    theta_MC=("theta_MC", "first"), r_core_MC=("r_core_MC", "first"),
    n_muons_MC=("nMuones_MC", "sum"))

SLOPE_EDGES_m = np.linspace(300.0, 650.0, 8)
slope_centres = 0.5 * (SLOPE_EDGES_m[1:] + SLOPE_EDGES_m[:-1])
rows = []
for zenith_low, zenith_high in ZENITH_BINS_deg:
    label_bin = "{:.0f}-{:.0f}".format(zenith_low, zenith_high)
    in_bin = (muon_stations["theta_MC"] >= zenith_low) & (muon_stations["theta_MC"] < zenith_high)
    near = muon_stations[in_bin & (muon_stations["r_core_MC"] > 300.0)
                         & (muon_stations["r_core_MC"] < 650.0)]
    mean_counts = near.groupby(pd.cut(near["r_core_MC"], SLOPE_EDGES_m),
                               observed=False)["n_muons_MC"].mean().to_numpy()
    beta = -np.polyfit(np.log(slope_centres), np.log(mean_counts), 1)[0]
    displacement = shift_fits[(shift_fits["zenith_bin"] == label_bin)
                              & (shift_fits["convention"] == VALIDATED)]["cos_amplitude_m"].iloc[0]
    rows.append({"zenith_bin": label_bin, "ldf_slope_beta": beta, "displacement_m": displacement,
                 "delta_A1_at_450m": -beta * displacement / 450.0,
                 "delta_A1_at_1000m": -beta * displacement / 1000.0})
washing_estimate = pd.DataFrame(rows)
washing_estimate.to_csv(TABLE_DIR / "estimacion_lavado_A1.csv", index=False)
print(washing_estimate.round(3).to_string(index=False))
