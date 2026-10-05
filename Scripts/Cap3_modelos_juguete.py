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
# # Chapter 3 toy model: which sign of $A_1$ should we expect?
#
# **Purpose.** This notebook does *not* try to reproduce simulated amplitudes. It answers one
# question for the argument of the thesis: putting together the mechanisms of Chapter 3
# (dilution, angular emission, attenuation, detector response), **is the muon density that
# reaches each detector expected to have a positive or a negative early-late asymmetry?**
#
# **Model** (Section `subsec:toy_models` of the chapter). A point source of muons on the shower
# axis, at distance $D$ from the core; muons travel in straight lines. For a muon of production
# momentum $p$ reaching the station at $(r, \phi)$ of the shower plane:
#
# $$ S(r,\phi\,|\,p) \propto \frac{1}{d^2}\; f(\alpha\,|\,p)\; e^{-d/\lambda(p)}\;
#    \mathcal{R}(\vartheta)\; \Theta_{\rm UMD} $$
#
# * $f$: angular emission of Cazón et al., $\propto \cos\alpha\, e^{-p\sin\alpha/Q}$, normalised;
# * $\lambda(p) = (p/m_\mu c)\,c\tau_\mu \simeq 6.2\,{\rm km}\times p/({\rm GeV}/c)$: effective
#   attenuation length, equal to the decay length of Eq. `eq:lambda_decaimiento` (energy loss is
#   not tracked: it is absorbed in effective parameters);
# * $\mathcal{R}$: detector response (plate for the UMD, tank silhouette for the SD muon count);
# * $\Theta_{\rm UMD}$: only for the UMD, the muon must have $p\cos\vartheta > p_{\rm UMD}$ to
#   cross the soil above the module. The SD has no relevant threshold at these energies.
#
# A population is the integral over a production spectrum $dN/dp \propto p^{-\gamma}$.
# $A_1$ is read from the early ($\phi=0$) and late ($\phi=\pi$) densities,
# $A_1 = (S_{\rm temprano} - S_{\rm tardio})/(S_{\rm temprano} + S_{\rm tardio})$, which is exact
# for a profile of the form $\langle S\rangle(1 + A_1\cos\phi)$.
#
# Runs with the repository `venv` in a few seconds; no ROOT and no simulation files.

# %%
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 0. Paths
#
# Figures go straight into the thesis image folder for Chapter 3; tables into a results folder
# next to this notebook. The repository root is found by walking up from the working directory.

# %%
def find_repo_root(start):
    folder = Path(start).resolve()
    while not (folder / "Tesis - Latex").is_dir():
        if folder.parent == folder:
            raise FileNotFoundError("Could not find the repository root from " + str(start))
        folder = folder.parent
    return folder


REPO_ROOT = find_repo_root(Path.cwd())
FIGURE_DIR = REPO_ROOT / "Tesis - Latex" / "capitulos" / "imagenes_capitulos" / "cap3"
TABLE_DIR = REPO_ROOT / "Scripts" / "resultados_cap3_modelos_juguete"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
print("Repository root:", REPO_ROOT)

# %% [markdown]
# ## 1. Constants and model parameters
#
# | Parameter | Central value | Meaning |
# |---|---|---|
# | `D_m` | 7500 m | distance from the production point to the core, along the axis |
# | `Q_GeV` | 0.15 GeV/c | scale of the transverse-momentum distribution $p_t e^{-p_t/Q}$ (mean $p_t = 2Q$) |
# | `gamma` | 2.6 | slope of the production spectrum $dN/dp \propto p^{-\gamma}$ |
# | `p_umd_GeV` | 1.0 GeV/c | effective momentum needed to cross the soil vertically (UMD) |
#
# $D = 7.5$ km corresponds roughly to a muon production depth of 500 g cm$^{-2}$ for a 35°
# shower at the altitude of the Observatory. Section 6 scans $D$, $Q$ and $\gamma$.

# %%
MUON_MASS_GeV = 0.10566
MUON_CTAU_m = 658.6

TANK_RADIUS_m = 1.8
TANK_HEIGHT_m = 1.2


@dataclass
class ModelParameters:
    D_m: float = 7500.0
    Q_GeV: float = 0.15
    gamma: float = 2.6
    p_umd_GeV: float = 1.0
    p_min_GeV: float = 0.2
    p_max_GeV: float = 2000.0


CENTRAL = ModelParameters()

# Reference point used in the chapter: large radius, intermediate zenith.
REFERENCE_RADIUS_m = 1200.0
REFERENCE_ZENITH_deg = 35.0

# The model is evaluated at the early (phi = 0) and late (phi = pi) positions.
PHI_EARLY_LATE = np.array([0.0, np.pi])

# %% [markdown]
# ## 2. Geometry
#
# Seen in the plane that contains the axis and the early-late line (Figure
# `fig:divergencia_angular`), the ground point whose projection on the shower plane is
# $(r,\phi)$ sits a distance $r\tan\theta\cos\phi$ further *up* the axis than the shower plane
# (towards the source) on the early side, and the same distance *down* on the late side. Its
# distance to the source therefore has a component $D - r\tan\theta\cos\phi$ along the axis and
# $r$ across it, and by Pythagoras
#
# $$ d(\phi) = \sqrt{(D - r\tan\theta\cos\phi)^2 + r^2}, \qquad
#    \sin\alpha = r/d, \qquad \cos\vartheta = D\cos\theta / d . $$

# %%
def geometry(radius_m, zenith_deg, D_m, phi):
    zenith = np.deg2rad(zenith_deg)
    along_axis = D_m - radius_m * np.tan(zenith) * np.cos(phi)
    distance = np.sqrt(along_axis**2 + radius_m**2)
    table = pd.DataFrame({
        "phi": phi,
        "distance_m": distance,
        "sin_alpha": radius_m / distance,
        "cos_local_zenith": D_m * np.cos(zenith) / distance,
    })
    table["alpha_deg"] = np.rad2deg(np.arcsin(table["sin_alpha"]))
    table["local_zenith_deg"] = np.rad2deg(np.arccos(table["cos_local_zenith"]))
    return table


reference_geometry = geometry(REFERENCE_RADIUS_m, REFERENCE_ZENITH_deg, CENTRAL.D_m,
                              PHI_EARLY_LATE)
reference_geometry.index = ["early", "late"]
print(reference_geometry.round(3).to_string())

# %% [markdown]
# ## 3. The ingredients, one function each

# %%
def emission_distribution(sin_alpha, momentum_GeV, Q_GeV):
    """Cazón angular distribution, normalised over the forward hemisphere."""
    k = momentum_GeV / Q_GeV
    cos_alpha = np.sqrt(1.0 - sin_alpha**2)
    normalisation = k**2 / (2.0 * np.pi * (1.0 - (1.0 + k) * np.exp(-k)))
    return normalisation * cos_alpha * np.exp(-k * sin_alpha)


def attenuation(momentum_GeV, distance_m):
    """exp(-d / lambda(p)), with lambda(p) the muon decay length."""
    attenuation_length = momentum_GeV * MUON_CTAU_m / MUON_MASS_GeV
    return np.exp(-distance_m / attenuation_length)


def detector_response(cos_local_zenith, response):
    sin_local_zenith = np.sqrt(1.0 - cos_local_zenith**2)
    if response == "perpendicular":
        return np.ones_like(cos_local_zenith)
    if response == "plate":
        return cos_local_zenith
    if response == "tank_count":
        top = np.pi * TANK_RADIUS_m**2 * cos_local_zenith
        side = 2.0 * TANK_RADIUS_m * TANK_HEIGHT_m * sin_local_zenith
        return (top + side) / (np.pi * TANK_RADIUS_m**2)
    raise ValueError("Unknown response: " + response)


def umd_threshold(momentum_GeV, cos_local_zenith, p_umd_GeV):
    """1 if the muon crosses the soil (slant thickness grows as 1/cos(local zenith)), else 0."""
    return (momentum_GeV * cos_local_zenith > p_umd_GeV).astype(float)


def asymmetry_early_late(early, late):
    return (early - late) / (early + late)

# %% [markdown]
# ## 4. Model variants
#
# Each variant switches the ingredients on one at a time. They are dictionaries with named keys.

# %%
VARIANTS = {
    "kinematic": {"label": "Dilución × emisión angular", "response": "perpendicular",
                  "attenuation": False, "umd_threshold": False, "color": "tab:gray"},
    "with_attenuation": {"label": "+ atenuación", "response": "perpendicular",
                         "attenuation": True, "umd_threshold": False, "color": "tab:purple"},
    "UMD": {"label": "UMD", "response": "plate",
            "attenuation": True, "umd_threshold": True, "color": "tab:blue"},
    "SD_count": {"label": "SD (número de muones)", "response": "tank_count",
                 "attenuation": True, "umd_threshold": False, "color": "tab:orange"},
}


def density_matrix(variant, momenta_GeV, radius_m, zenith_deg, params, phi=PHI_EARLY_LATE):
    """Density for each production momentum (rows) at each azimuth (columns)."""
    geo = geometry(radius_m, zenith_deg, params.D_m, phi)
    sin_alpha = geo["sin_alpha"].to_numpy()[np.newaxis, :]
    distance = geo["distance_m"].to_numpy()[np.newaxis, :]
    cos_local_zenith = geo["cos_local_zenith"].to_numpy()[np.newaxis, :]
    momenta = np.asarray(momenta_GeV, dtype=float)[:, np.newaxis]

    density = emission_distribution(sin_alpha, momenta, params.Q_GeV) / distance**2
    if variant["attenuation"]:
        density = density * attenuation(momenta, distance)
    if variant["umd_threshold"]:
        density = density * umd_threshold(momenta, cos_local_zenith, params.p_umd_GeV)
    density = density * detector_response(cos_local_zenith, variant["response"])
    return density


def population_density(variant, radius_m, zenith_deg, params, phi=PHI_EARLY_LATE, n_momenta=3000):
    """Sum over the production spectrum dN/dp = p^-gamma, integrating in log(p)."""
    log_momenta = np.linspace(np.log(params.p_min_GeV), np.log(params.p_max_GeV), n_momenta)
    momenta = np.exp(log_momenta)
    step = log_momenta[1] - log_momenta[0]
    weights = momenta**(-params.gamma) * momenta * step
    return weights @ density_matrix(variant, momenta, radius_m, zenith_deg, params, phi)


def population_A1(variant, radius_m, zenith_deg, params):
    early, late = population_density(variant, radius_m, zenith_deg, params)
    return asymmetry_early_late(early, late)

# %% [markdown]
# ## 5. Muons of a single momentum
#
# At fixed momentum, dilution favours the early side and angular emission the late side. The late
# side wins only for **hard** muons, above $p^* \simeq 2QD/r$.

# %%
momenta_GeV = np.geomspace(0.3, 30.0, 150)
fixed_momentum = pd.DataFrame({"momentum_GeV": momenta_GeV})
for name in ["kinematic", "with_attenuation"]:
    density = density_matrix(VARIANTS[name], momenta_GeV, REFERENCE_RADIUS_m,
                             REFERENCE_ZENITH_deg, CENTRAL)
    fixed_momentum[name] = asymmetry_early_late(density[:, 0], density[:, 1])

crossing_index = np.argmax(fixed_momentum["kinematic"].to_numpy() < 0)
crossing_momentum = fixed_momentum["momentum_GeV"].iloc[crossing_index]
estimate_crossing = 2 * CENTRAL.Q_GeV * CENTRAL.D_m / REFERENCE_RADIUS_m
print("Kinematic term changes sign at p = {:.2f} GeV/c (estimate 2QD/r = {:.2f})".format(
    crossing_momentum, estimate_crossing))
fixed_momentum.to_csv(TABLE_DIR / "A1_momento_fijo.csv", index=False)

# %% [markdown]
# ## 6. Populations: expected sign for each detector versus radius

# %%
radii_m = np.linspace(200.0, 1800.0, 33)
zenith_angles_deg = [35.0, 50.0]
rows = []
for zenith in zenith_angles_deg:
    for radius in radii_m:
        row = {"zenith_deg": zenith, "radius_m": radius}
        for name, variant in VARIANTS.items():
            row[name] = population_A1(variant, radius, zenith, CENTRAL)
        rows.append(row)
population_vs_radius = pd.DataFrame(rows)
population_vs_radius.to_csv(TABLE_DIR / "A1_poblacion_vs_radio.csv", index=False)

selected_radii = population_vs_radius["radius_m"].isin([400.0, 800.0, 1200.0, 1600.0])
print(population_vs_radius[selected_radii].round(3).to_string(index=False))

# %% [markdown]
# **Check of the early-late estimator.** For the profiles of this model, the two-point
# expression agrees with the first Fourier coefficient of the full profile to a few percent.

# %%
phi_full = np.linspace(0.0, 2.0 * np.pi, 72, endpoint=False)
rows = []
for name, variant in VARIANTS.items():
    profile = population_density(variant, REFERENCE_RADIUS_m, REFERENCE_ZENITH_deg, CENTRAL,
                                 phi=phi_full)
    fourier = 2.0 * np.mean(profile * np.cos(phi_full)) / np.mean(profile)
    two_point = asymmetry_early_late(profile[0], profile[36])
    rows.append({"variant": name, "A1_two_point": two_point, "A1_fourier": fourier})
estimator_check = pd.DataFrame(rows)
print(estimator_check.round(3).to_string(index=False))

# %% [markdown]
# ## 7. Is the sign robust? Parameter scan
#
# The amplitudes depend on $D$, $Q$, $\gamma$; only the **sign** is meant to survive into the
# thesis. For every combination of a coarse grid we compute $A_1$ for the UMD and the SD muon
# count at three radii and two zenith angles.

# %%
SCAN = {
    "D_m": [4000.0, 6000.0, 7500.0, 10000.0, 12000.0],
    "Q_GeV": [0.10, 0.15, 0.20, 0.25],
    "gamma": [2.4, 2.6, 2.8, 3.0],
}
SCAN_RADII_m = [600.0, 1200.0, 1800.0]
SCAN_ZENITHS_deg = [35.0, 50.0]

rows = []
for D in SCAN["D_m"]:
    for Q in SCAN["Q_GeV"]:
        for gamma in SCAN["gamma"]:
            params = replace(CENTRAL, D_m=D, Q_GeV=Q, gamma=gamma)
            for zenith in SCAN_ZENITHS_deg:
                for radius in SCAN_RADII_m:
                    row = {"D_m": D, "Q_GeV": Q, "gamma": gamma,
                           "zenith_deg": zenith, "radius_m": radius}
                    for name in ["kinematic", "UMD", "SD_count"]:
                        row[name] = population_A1(VARIANTS[name], radius, zenith, params)
                    rows.append(row)
scan = pd.DataFrame(rows)
scan.to_csv(TABLE_DIR / "A1_barrido_parametros.csv", index=False)

summary_rows = []
for name in ["kinematic", "UMD", "SD_count"]:
    values = scan[name]
    summary_rows.append({"variant": name, "n_cases": len(values),
                         "A1_min": values.min(), "A1_median": values.median(),
                         "A1_max": values.max(), "fraction_negative": (values < 0).mean()})
scan_summary = pd.DataFrame(summary_rows)
scan_summary.to_csv(TABLE_DIR / "A1_barrido_resumen.csv", index=False)
print(scan_summary.round(3).to_string(index=False))

# %% [markdown]
# ## 8. Does a higher threshold make the asymmetry more positive?
#
# An argument used early in this work was that the UMD shielding acts as a "kinematic filter"
# that removes soft muons and therefore *preserves* a positive asymmetry. Test: same response
# (perpendicular density, with attenuation), uniform cut on the production momentum, increasing.

# %%
thresholds_GeV = np.array([0.2, 0.5, 1.0, 1.5, 2.0, 3.0])
log_momenta = np.linspace(np.log(CENTRAL.p_min_GeV), np.log(CENTRAL.p_max_GeV), 600)
momenta = np.exp(log_momenta)
weights = momenta**(-CENTRAL.gamma) * momenta * (log_momenta[1] - log_momenta[0])
density = density_matrix(VARIANTS["with_attenuation"], momenta, REFERENCE_RADIUS_m,
                         REFERENCE_ZENITH_deg, CENTRAL)
rows = []
for threshold in thresholds_GeV:
    above = (momenta > threshold).astype(float)
    early, late = (weights * above) @ density
    rows.append({"threshold_GeV": threshold, "A1": asymmetry_early_late(early, late)})
threshold_scan = pd.DataFrame(rows)
threshold_scan.to_csv(TABLE_DIR / "A1_vs_umbral.csv", index=False)
print(threshold_scan.round(3).to_string(index=False))

# %% [markdown]
# ## 9. Figure for the chapter
#
# (a) muons of a single momentum; (b) populations, expected $A_1$ versus radius for the UMD and
# the SD muon count, at 35° and 50°.

# %%
fig, (ax_momentum, ax_radius) = plt.subplots(1, 2, figsize=(10.0, 4.0))

for name in ["kinematic", "with_attenuation"]:
    variant = VARIANTS[name]
    ax_momentum.plot(fixed_momentum["momentum_GeV"], fixed_momentum[name],
                     color=variant["color"], label=variant["label"])
ax_momentum.axhline(0.0, color="black", linewidth=0.8)
ax_momentum.axvline(crossing_momentum, color="tab:gray", linestyle=":", linewidth=1.0)
ax_momentum.set_xscale("log")
ax_momentum.set_ylim(-1.0, 0.6)
ax_momentum.set_xlabel("Momento del muón en la producción $p$ [GeV/$c$]")
ax_momentum.set_ylabel("$A_1$")
ax_momentum.set_title("(a) Muones de un único momento", fontsize=10)
ax_momentum.legend(fontsize=8, frameon=False, loc="lower left")

for name in ["UMD", "SD_count"]:
    variant = VARIANTS[name]
    for zenith in zenith_angles_deg:
        subset = population_vs_radius[population_vs_radius["zenith_deg"] == zenith]
        style = {"color": variant["color"], "linewidth": 1.6}
        if zenith == 35.0:
            style["linestyle"] = "-"
        else:
            style["linestyle"] = "--"
        style["label"] = variant["label"] + ", $\\theta = {:.0f}^\\circ$".format(zenith)
        ax_radius.plot(subset["radius_m"], subset[name], **style)
ax_radius.axhline(0.0, color="black", linewidth=0.8)
ax_radius.set_xlabel("$r$ [m]")
ax_radius.set_ylabel("$A_1$")
ax_radius.set_title("(b) Población con espectro $p^{-2.6}$", fontsize=10)
ax_radius.legend(fontsize=8, frameon=False, loc="upper left")

fig.tight_layout()
fig.savefig(FIGURE_DIR / "modelo_juguete.pdf")
plt.show()

# %% [markdown]
# ## 10. What goes to the chapter
#
# Only **signs and trends**: the model is a point source at fixed $D$, without shower-to-shower
# fluctuations, so its amplitudes are not expected to match the simulations.
