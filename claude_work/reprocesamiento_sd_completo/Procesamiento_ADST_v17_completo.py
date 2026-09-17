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
# # Procesamiento ADST v17 **completo** — your v8-2 pipeline, without losing SD stations
#
# This notebook is `Scripts/Procesamiento_ADST_v8-2.ipynb` with the smallest set
# of changes needed to also keep the SD stations that were NOT reconstructed.
#
# **What you get per ROOT file** (instead of one parquet):
#
# | Output folder | One row per | What it is |
# |---|---|---|
# | `modulos/` | UMD module | Your old v17 table, same columns, **plus** `has_sd_rec`. `df[df.has_sd_rec]` == old parquet. |
# | `estaciones_sd/` | simulated SD station, per event | **New.** Every simulated SD station, reconstructed or not, with MC muon/EM counts and true shower-plane geometry. |
# | `resumen/` | file | Counts: events, rows, and every counter skipped (and why). |
#
# **Why two tables?** Removing the `HasStation` skip from the counter loop is not
# enough: Offline does not write UMD modules for SD stations that did not trigger,
# so those stations never appear in that loop (Astra's "flag" run recovered only
# 45 rows out of ~55,000 missing stations). They do appear in the list of
# *simulated* SD stations, and that is what table B reads.
# Full explanation: `CAMBIOS.md`.
#
# **All the reading code is in `lector_adst_v17_completo.py`** (next to this notebook),
# with every change vs v17 marked `# CHANGE N`. It lives in a `.py` module instead
# of a notebook cell so that this notebook, the multiprocessing workers and the pilot
# script all run literally the same code.
#
# ### How to run
# 1. Start JupyterLab from a terminal where you sourced the Offline version you
#    want (see the next cell).
# 2. Run cells 1–2.
# 3. Leave `PILOTO = True`, run the SIB proton cell: 1 file, 50 events, 1 worker,
#    written to a *separate* pilot folder. Look at the validation cell.
# 4. Set `PILOTO = False` and run the production cells you want.
#    ~30 min per production with 8 workers (same as your March run).
#
# **Do not "Run All"**: each production cell launches a full batch job on the shared server.

# %% [markdown]
# ## 0. Which Offline version? (read this once)
#
# Your ADST files are an **icrc2025-test7** production. Your March parquets (v11)
# were read with **4.0.1-icrc23-prod1-root6**. A pilot on Run010 (50 events)
# read with both versions gave:
#
# | Column group | 4.0.1-icrc23 | icrc2025-test7 |
# |---|---|---|
# | Rows, keys, `nMuones_MC`, `sd_nMuons_MC`, `sd_nEM_MC`, `r_core_MC`, `phi_plane_euler_MC_true_core`, `theta_MC` | identical to v11 | identical to v11 |
# | `sdMuonSignal_REC` | 0 everywhere (as in v11) | real values (mean ≈ 9.9 VEM) |
# | Warnings | TStreamerInfo schema mismatch + "no dictionary for MdSimScintillator::Particle" | TStreamerInfo only |
#
# So the zeros in `sdMuonSignal_REC` were the old library failing to read that
# field, not "Suele ser 0 en Reco estándar". **Recommended: icrc2025-test7-root6.**
# Nothing used in the SD/UMD asymmetry changes either way.
#
# Before launching JupyterLab:
# ```bash
# source /srv/software/amd64/ubuntu/24.04/auger/offline/icrc2025-test7-root6/bin/this-auger-offline.sh
# ```

# %%
# --- Celda 1: Importaciones y carga de librerías Offline ---
import os
import sys
import glob
import json
import time
from functools import partial
from multiprocessing import Pool

import pandas as pd

# The reader module sits next to this notebook. Make sure Python finds it no
# matter which folder JupyterLab was started from.
CARPETA_NOTEBOOK = os.path.abspath("")
if not os.path.exists(os.path.join(CARPETA_NOTEBOOK, "lector_adst_v17_completo.py")):
    raise FileNotFoundError(
        "Abrí este notebook desde su carpeta (claude_work/reprocesamiento_sd_completo/): "
        "no encuentro lector_adst_v17_completo.py al lado.")
sys.path.insert(0, CARPETA_NOTEBOOK)

import lector_adst_v17_completo as lector   # imports ROOT, like your v8-2 cell 1
import validaciones

# Same as your v8-2 cell 1: AUGEROFFLINEROOT -> load libRecEventKG.so.
# It prints the library path, so this notebook's output records which version read the data.
LIBRERIA_OFFLINE = lector.cargar_offline()

# %%
# --- Celda 2: configuración común ---

# PILOTO = True  -> 1 file, 50 events, 1 worker, output to a SEPARATE pilot folder.
# PILOTO = False -> all files of the production, full events, n_workers processes.
#
# Why a separate pilot folder: the worker skips files whose parquets already exist.
# If a 50-event pilot wrote into the real output folder, the full run would later
# SKIP that file and you would silently keep a 50-event file. So pilots never share
# a folder with real runs.
PILOTO = True

n_workers = 8  # Ajustar como sea necesario

# Same data root as v8-2
BASE_DATOS = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA"

# New output root (v13). Your v10/v11 parquets are NOT touched.
SALIDA_REAL = "/home/lsilva/Github/ADST_Alexey_module_v13"
SALIDA_PILOTO = "/home/lsilva/Github/ADST_Alexey_module_v13_piloto"
SALIDA = SALIDA_PILOTO if PILOTO else SALIDA_REAL

print("MODO:", "PILOTO (1 archivo, 50 eventos, 1 worker)" if PILOTO else f"COMPLETO ({n_workers} workers)")
print("Salida:", SALIDA)


# %%
# --- Celda 3: la tanda completa, escrita UNA sola vez ---
#
# In v8-2 this block was copy-pasted once per production (six copies). It is the
# same code here, written once as a function, and each production cell below just
# calls it with its two paths. Behaviour is the same as your iron cell, which was
# the most recent one: imap_unordered + chunksize=1 ("CAMBIO CRÍTICO": workers take
# files one at a time, so none sits idle).

def correr_tanda(base_path, output_dir, piloto=PILOTO, n_workers=n_workers):
    print(f"--- INICIANDO {'PILOTO' if piloto else 'PROCESO PARALELO'} ---")
    start_total_time = time.time()

    os.makedirs(output_dir, exist_ok=True)
    print(f"Buscando archivos en: {base_path}")
    print(f"Los archivos .parquet se guardarán en: {output_dir}")

    all_root_files = sorted(glob.glob(os.path.join(base_path, "*.root")))
    if not all_root_files:
        print(f"¡Error! No se encontraron archivos .root en: {base_path}")
        return []
    print(f"Encontrados {len(all_root_files)} archivos .root.")

    if piloto:
        # One file, 50 events, in THIS process (no Pool): quick, and any error
        # traceback is printed right here instead of inside a worker.
        results = [lector.process_file_wrapper(all_root_files[0], output_dir, max_events=50)]
    else:
        # "Congelamos" el argumento 'output_dir' de la función trabajadora
        process_func = partial(lector.process_file_wrapper, output_dir=output_dir)
        print(f"Iniciando Pool con {n_workers} trabajadores...")
        with Pool(processes=n_workers) as pool:
            results = list(pool.imap_unordered(process_func, all_root_files, chunksize=1))

    print("\n\n--- Proceso Completado ---")

    # --- Resumen Final --- (same counting as v8-2)
    exitos = sum("✔ [Éxito]" in res for res in results)
    errores = sum("❌ [ERROR]" in res for res in results)
    for res in results:
        print(res)

    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(time.time() - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(results)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    if errores:
        print("⚠️  Hubo errores: leé los ❌ de arriba. Los archivos con error NO tienen parquet "
              "y se reintentan solos la próxima vez que corras esta celda.")
    print(f"¡Listo! Tus archivos están en: {output_dir}  (subcarpetas modulos/, estaciones_sd/, resumen/)")
    return results


# %% [markdown]
# # Paralelizacion -> Sibyl-Proton-17.5-18eV
# The production used for the SD/UMD comparison. **Run this one first.**

# %%
resultados_sib_proton_17 = correr_tanda(
    base_path=f"{BASE_DATOS}/SIB23e/17.5_18.0/proton",
    output_dir=f"{SALIDA}/parquet_sib_proton_17",
)

# %% [markdown]
# # Paralelizacion -> Sibyl-Hierro-17.5-18eV

# %%
resultados_sib_hierro_17 = correr_tanda(
    base_path=f"{BASE_DATOS}/SIB23e/17.5_18.0/iron",
    output_dir=f"{SALIDA}/parquet_sib_hierro_17",
)

# %% [markdown]
# # Paralelizacion -> Sibyl-Helio-17.5-18eV

# %%
resultados_sib_helio_17 = correr_tanda(
    base_path=f"{BASE_DATOS}/SIB23e/17.5_18.0/helium",
    output_dir=f"{SALIDA}/parquet_sib_helio_17",
)

# %% [markdown]
# # Paralelizacion -> Sibyl-Oxigeno-17.5-18eV

# %%
resultados_sib_oxigeno_17 = correr_tanda(
    base_path=f"{BASE_DATOS}/SIB23e/17.5_18.0/oxygen",
    output_dir=f"{SALIDA}/parquet_sib_oxigeno_17",
)

# %% [markdown]
# # Paralelizacion -> QGS-Helio-17.5-18eV

# %%
resultados_qgs_helio_17 = correr_tanda(
    base_path=f"{BASE_DATOS}/QGSIII01/17.5_18.0/helium",
    output_dir=f"{SALIDA}/parquet_qgs_helio_17",
)

# %% [markdown]
# # Paralelizacion -> EPOS-Helio-18-18.5eV
# Note: with v17 this production lost its metadata columns (`model_mc`, `e_min_mc`, ...),
# because the model name `EPOSLHC_R` contains "_" and broke `filename.split('_')`.
# Fixed in CHANGE 6.

# %%
resultados_epos_helio_18 = correr_tanda(
    base_path=f"{BASE_DATOS}/EPOSLHC_R/18.0_18.5/helium",
    output_dir=f"{SALIDA}/parquet_epos_helio_18",
)

# %% [markdown]
# # Validation: did we lose or change anything?
#
# Pandas only (no ROOT); safe to run any time after a production finishes.
# For every file in the chosen production it checks:
#
# 1. **Nothing lost.** `modulos[has_sd_rec]` has exactly the rows of your old parquet,
#    with identical values in the columns the asymmetry analysis uses. Other columns
#    that differ are listed (with icrc2025-test7, expect `sdMuonSignal_REC`).
# 2. **Tables agree.** Every reconstructed Infill station in `modulos` is in
#    `estaciones_sd`, with the same counts and geometry.
#
# In pilot mode the old parquet is restricted to the 50 events that were read.

# %%
PRODUCCION = "parquet_sib_proton_17"   # which production folder to validate
REFERENCIA_VIEJA = f"/home/lsilva/Github/ADST_Alexey_module_v11/{PRODUCCION}"   # your March parquets

filas = []
for path_mod in sorted(glob.glob(f"{SALIDA}/{PRODUCCION}/modulos/*.parquet")):
    nombre = os.path.basename(path_mod)
    mod = pd.read_parquet(path_mod)
    est = pd.read_parquet(f"{SALIDA}/{PRODUCCION}/estaciones_sd/{nombre}")
    fila = {"archivo": nombre.replace(".parquet", ""),
            "modulos": len(mod), "modulos_sin_sd_rec": int((~mod.has_sd_rec).sum()),
            "estaciones_sd": len(est), "estaciones_sin_sd_rec": int((~est.has_sd_rec).sum())}

    path_viejo = os.path.join(REFERENCIA_VIEJA, nombre)
    if os.path.exists(path_viejo):
        eventos = mod.event_id.unique() if PILOTO else None
        r1 = validaciones.comparar_modulos_con_parquet_viejo(
            mod, pd.read_parquet(path_viejo), eventos=eventos, imprimir=False)
        fila.update({"filas_perdidas_vs_viejo": r1["perdidas"],
                     "filas_sobrantes_vs_viejo": r1["sobrantes"],
                     "columnas_analisis_identicas": r1["columnas_analisis_ok"],
                     "otras_columnas_distintas": ", ".join(c for c, n in r1["otras_columnas"].items() if n)})
    else:
        fila["filas_perdidas_vs_viejo"] = "sin referencia vieja"

    r3 = validaciones.consistencia_modulos_estaciones(mod, est, imprimir=False)
    fila["estaciones_de_modulos_ausentes_en_tabla_sd"] = r3["faltan_en_b"]
    filas.append(fila)

tabla_validacion = pd.DataFrame(filas)
display(tabla_validacion)

if len(tabla_validacion):
    ok = (tabla_validacion.get("filas_perdidas_vs_viejo", pd.Series([0])).astype(str).isin(["0", "sin referencia vieja"]).all()
          and tabla_validacion["estaciones_de_modulos_ausentes_en_tabla_sd"].eq(0).all()
          and tabla_validacion.get("columnas_analisis_identicas", pd.Series([True])).fillna(True).all())
    print("RESULTADO GLOBAL:", "PASS — nada perdido, columnas de análisis idénticas" if ok
          else "FAIL — revisar la tabla de arriba (una fila por archivo)")
    print("Filas de módulos añadidas por el flag (sin SD REC):", int(tabla_validacion.modulos_sin_sd_rec.sum()))
    print("Estaciones SD sin SD REC recuperadas en la tabla nueva:", int(tabla_validacion.estaciones_sin_sd_rec.sum()))
