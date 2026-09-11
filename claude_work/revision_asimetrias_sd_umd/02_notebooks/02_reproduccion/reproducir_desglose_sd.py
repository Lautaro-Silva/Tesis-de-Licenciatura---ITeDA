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
# # Reproducción exacta del desglose SD–UMD de plots_seccion_6
#
# Este cuaderno reproduce el gráfico solicitado con sus **mismos datos, bins,
# convención azimutal y ajuste ponderado**. Luego realiza una comparación
# independiente del antes/después de selección SD con ese mismo bineado.
#
# No modifica Scripts/plots_seccion_6.py, el PDF de referencia, los parquet,
# Offline, configuraciones del instituto ni la tesis. No importa ROOT ni ejecuta
# simulación o reconstrucción. Todas las salidas se guardan en esta carpeta.
#
# **Diferencia importante con el cuaderno anterior:** allí se usaron bandas más
# anchas y ajuste no ponderado. Aquí se conserva sigma=SEM por bin y
# absolute_sigma=True, tal como en la celda original. No hay que esperar los
# mismos números del ensayo anterior al cambiar esos dos elementos.
#
# La reproducción literal conserva también las filas por módulo UMD, con sus
# copias del conteo SD. No se cambia silenciosamente esa decisión estadística.
# Los errores de ese ajuste se reproducen; no se certifican como errores que
# incorporen las correlaciones entre módulos, estaciones y reutilizaciones.

# %%
import os
from pathlib import Path
import hashlib
import json
import re

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from threadpoolctl import threadpool_limits
from IPython.display import display, Markdown
import pdfplumber

thread_limit = threadpool_limits(limits=1)
REPO = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "CLAUDE.md").is_file())
HERE = REPO / "claude_work/revision_asimetrias_sd_umd/02_notebooks/02_reproduccion"
RESULTS = HERE / 'resultados'
RESULTS.mkdir(exist_ok=True)
AUDIT = REPO / "claude_work/revision_asimetrias_sd_umd/04_soporte/tablas"
DATA = Path("/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17")
REFERENCE = REPO / "claude_work/revision_asimetrias_sd_umd/04_soporte/referencias/SD_Desglose_Componentes_vs_UMD_original.pdf"
SOURCE = REPO / "Scripts/plots_seccion_6.py"
OFFLINE_SOURCE = Path("/opt/build/AugerOffline-icrc2025-test7")
pd.set_option("display.max_columns", 20)
pd.set_option("display.precision", 7)

def sha256(path):
    """Huella de contenido, sólo lectura."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

reference_hash = sha256(REFERENCE)
source_hash = sha256(SOURCE)

# %% [markdown]
# ## 1. Confirmación de integridad: qué se puede comprobar
#
# En el trabajo anterior se leyeron código/configuraciones y ADST existentes.
# No se editaron ni compilaron librerías Offline, no se instalaron paquetes allí,
# no se cambiaron umbrales/configuraciones de producción y no se reescribieron
# archivos ROOT. Las variables de entorno del lector ROOT se aplicaron al
# proceso lanzado, no a archivos persistentes de configuración.
#
# Disponemos además de huellas de contenido de los fuentes relevantes tomadas
# durante la auditoría. Aquí se comparan con sus contenidos actuales. Esto
# comprueba esos archivos desde la instantánea; **no es una auditoría global de
# toda la instalación ni una garantía de que ningún otro usuario cambió nada**.
#
# El manifiesto anterior se usa sólo para esta comprobación de integridad.
# Ningún coeficiente del gráfico se lee desde JSON.

# %%
saved_hashes = json.loads((AUDIT / "offline_source_manifest.json").read_text())
integrity_rows = []
for entry in saved_hashes:
    filename = OFFLINE_SOURCE / entry["file"]
    exists = filename.is_file()
    integrity_rows.append({
        "fuente_Offline": entry["file"],
        "existe": exists,
        "contenido_igual_a_instantanea": exists and sha256(filename) == entry["sha256"],
    })
integrity = pd.DataFrame(integrity_rows)
display(integrity)
integrity.to_csv(RESULTS / "integridad_fuentes_offline.csv", index=False)
print("Fuentes idénticos a la instantánea:",
      integrity["contenido_igual_a_instantanea"].sum(), "de", len(integrity))
if not integrity["contenido_igual_a_instantanea"].all():
    print("ATENCIÓN: revisar diferencias; esta prueba no atribuye quién hizo un cambio.")

# %% [markdown]
# ## 2. Misma muestra y mismo estilo que la celda original
#
# Se leen todos los parquet de la carpeta de protones y se aplica counterId>=100000,
# como en el inicio de plots_seccion_6.py. Se cargan sólo las columnas necesarias
# para disminuir I/O y memoria; esto no cambia la selección.
#
# No se agrega corte de saturación, estado de módulo, señal positiva ni Nmu>0.
# La energía pertenece a la banda de la producción: se verifica, no se introduce
# un corte que no estaba en la celda original.
#
# La primera figura conserva el ajuste sobre filas de módulos, incluso para
# SD. La segunda comparación deduplica SD y lo indica expresamente.

# %%
needed_columns = [
    "counterId", "event_id", "sdId", "moduleId", "theta_MC", "logE_MC",
    "r_core_MC", "phi_plane_euler_MC_true_core", "nMuones_MC",
    "sd_nEM_MC", "sd_nMuons_MC", "sdSignal_REC",
]
parts = []
for filename in sorted(DATA.glob("*.parquet")):
    table = pd.read_parquet(filename, columns=needed_columns)
    table["source"] = filename.with_suffix(".root").name
    parts.append(table)
assert parts, "No hay archivos parquet en la ruta indicada."
df_guia = pd.concat(parts, ignore_index=True)
df_infill = df_guia.loc[df_guia["counterId"] >= 100000].copy()
print("Archivos:", len(parts), "| filas de módulos Infill:", len(df_infill))
display(df_infill[["theta_MC", "logE_MC"]].agg(["min", "max"]))

# Copia del estilo HEP del comienzo de plots_seccion_6.py.
plt.rcdefaults()
hep_style = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "axes.linewidth": 1.2,
    "legend.frameon": True, "legend.shadow": True, "legend.edgecolor": "black",
    "lines.linewidth": 2, "lines.markersize": 8,
    "xtick.labelsize": 14, "ytick.labelsize": 14,
}
plt.rcParams.update(hep_style)
COLORS = {"Proton": "royalblue", "Iron": "firebrick"}

def ensure_degrees(series):
    """La misma función heurística del script original."""
    if series.dropna().abs().max() < 7.0:
        return np.rad2deg(series)
    return series

def harmonic_model(phi_deg, A1):
    """La misma función: ángulo en grados, A1 positivo = temprano."""
    return 1.0 + A1 * np.cos(np.deg2rad(phi_deg))

th_min, th_max = 30, 40
df_th = df_infill.loc[
    (df_infill["theta_MC"] >= th_min) & (df_infill["theta_MC"] < th_max)
].copy()

r_edges = np.array([150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
r_centers = (r_edges[1:] + r_edges[:-1]) / 2
phi_bin_edges = np.linspace(-180, 180, 13)
phi_centers = (phi_bin_edges[1:] + phi_bin_edges[:-1]) / 2

# EXACTAMENTE la conversión de la celda original.
euler_mc_true = ensure_degrees(df_th["phi_plane_euler_MC_true_core"])
euler_abs = (euler_mc_true - 180) % 360
df_th["phi_MC_Truth"] = (euler_abs + 180) % 360 - 180

signals = [
    {"col": "nMuones_MC", "label": "UMD", "color": "mediumblue", "marker": "s"},
    {"col": "sd_nEM_MC", "label": "SD Electromagnetic", "color": "darkorange", "marker": "^"},
    {"col": "sd_nMuons_MC", "label": "SD Muonic", "color": "forestgreen", "marker": "v"},
    {"col": "sdSignal_REC", "label": "SD Total Signal", "color": "firebrick", "marker": "o"},
]

# %% [markdown]
# ## 3. El ajuste, explicitado y sin cambiar sus reglas
#
# Para cada población y banda radial:
#
# 1. Al menos quince filas no nulas.
# 2. Doce bins azimutales mediante pd.cut con sus defaults originales:
#    intervalos abiertos a izquierda/cerrados a derecha; -180° exacto queda fuera.
# 3. Media y SEM por bin.
# 4. Normalizar por la media de las medias azimutales, ignorando bins NaN.
# 5. Usar sólo bins con media y SEM válidos, y SEM positivo; al menos cinco.
# 6. curve_fit ponderado por SEM normalizado, absolute_sigma=True y límites [-2,2].
# 7. Si el error supera 0.5, no mostrar el ajuste.
#
# No cambiamos estas reglas por las del cuaderno anterior. Sólo se agrega una
# tabla de diagnóstico para que un ajuste fallido no quede oculto en un except.
# El rango de límites reproduce el código; no es una afirmación de que cualquier
# A1 permitido produzca una densidad física no negativa en todo phi.

# %%
def fit_one_band(table, column):
    """Reproduce la lógica de la celda recibida y añade sólo diagnósticos."""
    result = {
        "A1": np.nan, "error": np.nan, "n_rows": len(table),
        "n_nonnull": len(table.dropna(subset=[column])),
        "valid_phi_bins": 0, "status": "menos de 15 filas",
    }
    if result["n_nonnull"] < 15:
        return result

    local = table.copy()
    local["bin_phi"] = pd.cut(local["phi_MC_Truth"], bins=phi_bin_edges)
    statistics = local.groupby("bin_phi", observed=False)[column].agg(["mean", "sem"])
    y_means, y_errs = statistics["mean"].values, statistics["sem"].values
    norm = np.nanmean(y_means)
    result["status"] = "normalización no positiva"
    if not (norm > 0 and not np.isnan(norm)):
        return result
    y_norm, y_err_norm = y_means / norm, y_errs / norm
    valid = ~np.isnan(y_norm) & ~np.isnan(y_err_norm) & (y_err_norm > 0)
    result["valid_phi_bins"] = int(valid.sum())
    result["status"] = "menos de cinco bins válidos"
    if valid.sum() < 5:
        return result
    try:
        popt, pcov = curve_fit(
            harmonic_model, phi_centers[valid], y_norm[valid],
            sigma=y_err_norm[valid], absolute_sigma=True, bounds=(-2.0, 2.0),
        )
        A1, error = popt[0], np.sqrt(np.diag(pcov))[0]
        if error > 0.5:
            result["status"] = "error superior a 0.5"
        else:
            result.update(A1=float(A1), error=float(error), status="ok")
    except Exception as exc:
        result["status"] = type(exc).__name__ + ": " + str(exc)
    return result

fit_rows = []
for signal in signals:
    for r_min, r_max in zip(r_edges[:-1], r_edges[1:]):
        radial = df_th.loc[
            (df_th["r_core_MC"] >= r_min) & (df_th["r_core_MC"] < r_max)
        ]
        fit_rows.append({
            "observable": signal["label"], "column": signal["col"],
            "r_min": r_min, "r_max": r_max, "r_center": (r_min + r_max) / 2,
            **fit_one_band(radial, signal["col"]),
        })
fits = pd.DataFrame(fit_rows)
display(fits.pivot(index="r_center", columns="observable", values="A1"))
display(fits[["observable", "r_min", "r_max", "error", "valid_phi_bins", "status"]])
fits.to_csv(RESULTS / "ajustes_reproducidos.csv", index=False)

# %%
# Mismos colores, marcadores, límites, anotaciones y escala automática.
fig, ax = plt.subplots(figsize=(10, 7))
for signal in signals:
    rows = fits.loc[fits["column"] == signal["col"]]
    ax.errorbar(
        r_centers, rows["A1"], yerr=rows["error"], fmt=f"-{signal['marker']}",
        color=signal["color"], label=signal["label"], markersize=8,
        linewidth=2.5, capsize=4, markeredgecolor="black", markeredgewidth=0.5,
    )
ax.axhline(0, color="black", linestyle="--", linewidth=1.5, alpha=0.8)
ax.set_xlabel(r"$r_{\mathrm{MC}}$ [m]", fontsize=16)
ax.set_ylabel(r"$A_1$", fontsize=16)
ax.set_xlim(100, 1400)
ax.set_xticks(r_edges)
ax.grid(True, which="major", linestyle="-", alpha=0.5)
ax.grid(True, which="minor", linestyle=":", alpha=0.3)
ax.minorticks_on()
ax.legend(fontsize=12, loc="upper left", framealpha=0.9)
ax.text(0.96, 0.88, r"$\mathbf{Proton\ Showers}$", transform=ax.transAxes,
        fontsize=14, va="top", ha="right", color=COLORS["Proton"])
ax.text(0.96, 0.81, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes,
        fontsize=14, va="top", ha="right", color="purple")
ax.text(0.96, 0.74, rf"$\mathbf{{{th_min}^\circ < \theta_{{\mathrm{{MC}}}} < {th_max}^\circ}}$",
        transform=ax.transAxes, fontsize=13, va="top", ha="right")
ax.text(0.96, 0.68, r"$\mathbf{True\ MC\ Geometry}$", transform=ax.transAxes,
        fontsize=13, va="top", ha="right", color="dimgray")
plt.tight_layout()
REPRODUCED = RESULTS / "SD_Desglose_Componentes_vs_UMD_reproducido.pdf"
fig.savefig(REPRODUCED, dpi=300)
fig.savefig(RESULTS / "SD_Desglose_Componentes_vs_UMD_reproducido.png", dpi=160)
plt.show()

# %% [markdown]
# ## 4. Comparar contra el PDF que proporcionaste
#
# Se usa una copia inalterada en 04_soporte/referencias para que el
# cotejo también funcione en un clon nuevo. El original de Scripts no se modifica.
#
# El PDF conserva sus curvas como vectores, no como una imagen. Eso permite
# extraer las posiciones de sus ocho puntos por curva y de las barras de error.
#
# La escala vertical se obtiene de las etiquetas del eje y sus líneas de grilla,
# **sin ajustar esa escala a los resultados que queremos comprobar**. Se usan
# colores para identificar curvas y coordenadas coincidentes para sus barras.
# La precisión está limitada por el redondeo de coordenadas del PDF.
#
# Este apéndice no interviene en los ajustes. Primero calculamos los números
# desde parquet; después los contrastamos con el gráfico existente.

# %%
def color_matches(value, target):
    """pdfplumber representa algunos colores grises como escalares."""
    try:
        return np.shape(value) == (3,) and np.allclose(value, target, atol=1e-8)
    except TypeError:
        return False

def extract_vector_results(pdf_path):
    """Extrae A1/error de este tipo de PDF Matplotlib mediante sus ejes."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        # Etiquetas decimales del eje izquierdo, no texto dentro del gráfico.
        y_labels = [
            w for w in words
            if w["x1"] < page.width * 0.12
            and re.fullmatch(r"[−-]?\d+\.\d+", w["text"])
        ]
        horizontal = [
            line for line in page.lines
            if line["width"] > page.width * 0.5 and line["height"] < 1e-7
        ]
        if len(y_labels) < 3 or not horizontal:
            raise ValueError("No se reconoce la escala vertical de este PDF.")
        grid_positions, tick_values = [], []
        for word in y_labels:
            center = (word["top"] + word["bottom"]) / 2
            nearest = min(horizontal, key=lambda line: abs(line["top"] - center))
            if abs(nearest["top"] - center) > 5:
                raise ValueError("No se puede asociar una etiqueta a su grilla.")
            grid_positions.append(nearest["top"])
            tick_values.append(float(word["text"].replace("−", "-")))
        slope, intercept = np.polyfit(grid_positions, tick_values, 1)
        assert np.max(np.abs(np.polyval([slope, intercept], grid_positions) - tick_values)) < 1e-7
        results = []
        for signal in signals:
            rgb = plt.matplotlib.colors.to_rgb(signal["color"])
            curves = [
                curve for curve in page.curves
                if color_matches(curve.get("stroking_color"), rgb)
                and len(curve["pts"]) == len(r_centers)
                and np.ptp(np.asarray(curve["pts"])[:, 0]) > page.width * 0.5
            ]
            if len(curves) != 1:
                raise ValueError(f"No se identifica de forma única la curva {signal['label']}.")
            points = np.asarray(curves[0]["pts"])
            assert np.all(np.diff(points[:, 0]) > 0)
            for radius, (x, y) in zip(r_centers, points):
                bars = [
                    line for line in page.lines
                    if color_matches(line.get("stroking_color"), rgb)
                    and line["width"] < 1e-7 and line["height"] > 0
                    and abs(line["x0"] - x) < 1e-4
                ]
                if len(bars) != 1:
                    raise ValueError("No se identifica de forma única una barra de error.")
                results.append({
                    "observable": signal["label"], "r_center": radius,
                    "A1_pdf": slope * y + intercept,
                    "error_pdf": abs(slope) * bars[0]["height"] / 2,
                })
    return pd.DataFrame(results)

pdf_values = extract_vector_results(REFERENCE)
pdf_comparison = fits.merge(pdf_values, on=["observable", "r_center"], validate="one_to_one")
pdf_comparison["delta_A1"] = pdf_comparison["A1"] - pdf_comparison["A1_pdf"]
pdf_comparison["delta_error"] = pdf_comparison["error"] - pdf_comparison["error_pdf"]
display(pdf_comparison[["observable", "r_center", "A1", "A1_pdf", "delta_A1", "delta_error"]])
pdf_comparison.to_csv(RESULTS / "comparacion_numerica_con_PDF.csv", index=False)
max_delta_A1 = pdf_comparison["delta_A1"].abs().max()
max_delta_error = pdf_comparison["delta_error"].abs().max()
print("Máxima diferencia A1 contra el PDF:", max_delta_A1)
print("Máxima diferencia en error contra el PDF:", max_delta_error)
print("La comparación es numérica; no se exige identidad binaria de dos PDFs.")

# %% [markdown]
# ## 5. Ahora sí: antes y después de selección, con estos mismos bins
#
# Esta segunda figura **no sustituye** la reproducción literal anterior.
# Usa los conteos SD de la extracción ADST y conserva:
#
# - los ocho intervalos radiales de 150 m;
# - doce bins phi;
# - el mismo ajuste ponderado y criterios de validez.
#
# Aquí la unidad es una ocurrencia SD por evento, sin repetirla por módulos.
# Para el control se comprueba que la selección HasStation coincide con el
# parquet deduplicado. Las copias por módulo pueden cambiar las SEM y, con
# ajuste ponderado, también ligeramente A1; no se confunde eso con el efecto
# de incorporar estaciones ausentes del parquet.
#
# No dibujamos UMD ni señal VEM "antes de selección": no disponemos de esos
# observables equivalentes para las estaciones ausentes. El UMD positivo y el
# SD Total del primer gráfico conservan su selección original.
#
# Las barras de esta comparación son las incertidumbres formales del ajuste
# solicitado, no el bootstrap por lluvias del cuaderno anterior.

# %%
raw = pd.read_csv(AUDIT / "adst_counts_fast.csv", dtype={"event_id": str, "source": str})
assert raw["theta"].between(30, 40, inclusive="left").all()
raw["phi_MC_Truth"] = np.rad2deg(raw["phi"])
raw["r_core_MC"] = raw["r"]
raw["sd_nMuons_MC"] = raw["mu"]
raw["sd_nEM_MC"] = raw["em"]
key = ["source", "event_id", "sdId"]
df_th["event_id"] = df_th["event_id"].astype(str)
unique_sd = df_th.drop_duplicates(key)
unique_sd = unique_sd.loc[unique_sd["r_core_MC"].between(150, 1800, inclusive="left")]
assert not raw.duplicated(key).any()
matched = raw.merge(
    unique_sd[key + ["sd_nMuons_MC", "sd_nEM_MC", "phi_MC_Truth", "r_core_MC"]],
    on=key, how="outer", validate="one_to_one", indicator=True,
    suffixes=("_raw", "_parquet"),
)
assert not matched["_merge"].eq("right_only").any()
assert np.array_equal(matched["has_rec"].eq(1), matched["_merge"].eq("both"))
both = matched.loc[matched["_merge"] == "both"]
for col in ["sd_nMuons_MC", "sd_nEM_MC"]:
    assert np.array_equal(both[col + "_raw"], both[col + "_parquet"])
assert np.max(np.abs(both["r_core_MC_raw"] - both["r_core_MC_parquet"])) < 1e-6
assert np.max(np.abs(
    (both["phi_MC_Truth_raw"] - both["phi_MC_Truth_parquet"] + 180) % 360 - 180
)) < 1e-6

selection_rows = []
for column in ["sd_nMuons_MC", "sd_nEM_MC"]:
    for sample, table in [
        ("Antes de HasStation", raw),
        ("HasStation=True", raw.loc[raw["has_rec"] == 1]),
        ("Parquet, SD sin duplicados", unique_sd),
    ]:
        for r_min, r_max in zip(r_edges[:-1], r_edges[1:]):
            band = table.loc[table["r_core_MC"].between(r_min, r_max, inclusive="left")]
            selection_rows.append({
                "column": column, "sample": sample,
                "r_min": r_min, "r_max": r_max, "r_center": (r_min + r_max) / 2,
                **fit_one_band(band, column),
            })
selection_fits = pd.DataFrame(selection_rows)
selection_fits.to_csv(RESULTS / "seleccion_mismos_bins_ajuste_ponderado.csv", index=False)
display(selection_fits.pivot(index=["column", "r_center"], columns="sample", values="A1"))

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
for axis, column, title in zip(
    axes, ["sd_nMuons_MC", "sd_nEM_MC"], ["SD muonic count", "SD electromagnetic count"]
):
    for sample, color, marker in [
        ("Antes de HasStation", "royalblue", "s"),
        ("HasStation=True", "firebrick", "o"),
    ]:
        rows = selection_fits.loc[
            selection_fits["column"].eq(column) & selection_fits["sample"].eq(sample)
        ]
        axis.errorbar(rows["r_center"], rows["A1"], yerr=rows["error"],
                      color=color, marker=marker, capsize=3, label=sample)
    axis.axhline(0, color="black", ls="--", lw=1)
    axis.set_xlabel(r"$r_{\mathrm{MC}}$ [m]", fontsize=14)
    axis.set_ylabel(r"$A_1$", fontsize=14)
    axis.set_title(title)
    axis.grid(alpha=0.3)
    axis.legend(fontsize=10)
fig.suptitle("Same radial bins and weighted fit; one row per SD station/event\n"
             "Proton SIBYLL 2.3e, 30–40°, true MC geometry", fontsize=13)
fig.tight_layout()
fig.savefig(RESULTS / "SD_antes_despues_mismos_bins.pdf")
fig.savefig(RESULTS / "SD_antes_despues_mismos_bins.png", dpi=160)
plt.show()

# %% [markdown]
# ## 6. Comprobaciones de cierre
#
# La diferencia respecto del PDF se calcula para sus 32 puntos y sus 32 errores.
# Se usa una tolerancia pequeña pero no se exige precisión superior a la
# serialización vectorial del PDF. Si la comprobación falla, se informa una
# diferencia real por investigar: no se ajusta la curva a la imagen.
#
# También se comprueba que código original y PDF de referencia mantienen su hash.
# Ninguno fue sobrescrito. Las comprobaciones de integridad de Offline alcanzan
# los fuentes registrados en la instantánea, no toda la instalación.

# %%
assert len(pdf_comparison) == 32
assert fits["status"].eq("ok").all()
assert max_delta_A1 < 1e-6, "El gráfico no reproduce numéricamente el PDF de referencia."
assert max_delta_error < 1e-6, "Las barras de error difieren del PDF."
selected_check = selection_fits.pivot(
    index=["column", "r_center"], columns="sample", values=["A1", "error"]
)
for quantity in ["A1", "error"]:
    assert np.allclose(
        selected_check[quantity]["HasStation=True"],
        selected_check[quantity]["Parquet, SD sin duplicados"],
        atol=1e-8, rtol=0,
    )
assert sha256(REFERENCE) == reference_hash
assert sha256(SOURCE) == source_hash

report = f"""# Reproducción y comprobaciones

- PDF original: Scripts/SD_Desglose_Componentes_vs_UMD.pdf; intacto.
- Código original: Scripts/plots_seccion_6.py; intacto.
- Fuentes Offline con huella previa, actualmente idénticos: {int(integrity['contenido_igual_a_instantanea'].sum())}/{len(integrity)}.
- Archivos parquet: {len(parts)}. Ninguno reescrito.
- Curvas: cuatro; puntos y barras cotejados contra vectores del PDF: {len(pdf_comparison)}.
- Máxima diferencia absoluta en A1: {max_delta_A1:.3g}.
- Máxima diferencia absoluta en error de A1: {max_delta_error:.3g}.
- Bins y ponderación: los de la celda solicitada; filas por módulo en la reproducción literal.
- Comparación adicional SD antes/después: mismos bins y ajuste ponderado, una fila por SD.
- No se ejecutó ROOT, reconstrucción ni simulación en esta reproducción.

Los errores formales originales se reproducen, no se reinterpretan como errores
independientes de correlaciones. La comparación SD antes/después no produce
observables UMD o VEM previos a selección que no están disponibles.
"""
(HERE / "RESULTADO.md").write_text(report, encoding="utf-8")
display(Markdown(report))

