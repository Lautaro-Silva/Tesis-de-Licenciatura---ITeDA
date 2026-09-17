"""
validaciones.py -- pandas-only checks of the new tables (no ROOT needed).

Used by the pilot AND by the last cell of Procesamiento_ADST_v17_completo, so
the same checks run in both places. Every check prints PASS or FAIL with the
numbers behind it. Nothing here stops the program: a FAIL is information for
you to read, not an exception that hides where things went wrong.

Three questions are answered:

1. comparar_modulos_con_parquet_viejo
   Is `modulos[has_sd_rec]` the SAME table as the old v17 parquet?
   - same set of rows (key: event_id, counterId, moduleId, sdId)
   - identical values in the columns the SD/UMD asymmetry analysis uses
   - every other column: reported (how many rows differ), not failed,
     because some REC-station columns depend on the Offline library version
     (see CAMBIOS.md, "Offline library mismatch").

2. comparar_estaciones_con_extraccion_astra
   Does the new SD-station table contain the same stations and counts as the
   CSV Astra extracted (adst_counts_fast.csv), after applying Astra's cuts?

3. consistencia_modulos_estaciones
   For reconstructed stations, do table A (deduplicated to one row per
   station) and table B agree on counts and geometry?
"""

import numpy as np
import pandas as pd

# Columns that enter the SD/UMD asymmetry comparison. These MUST be identical.
COLUMNAS_ANALISIS = ["theta_MC", "r_core_MC", "phi_plane_euler_MC_true_core",
                     "nMuones_MC", "sd_nMuons_MC", "sd_nEM_MC"]
CLAVE_MODULO = ["event_id", "counterId", "moduleId", "sdId"]
CLAVE_ESTACION = ["event_id", "sdId"]


def _estado(ok):
    return "PASS" if ok else "FAIL"


def _iguales(a, b, tolerancia):
    """Element-wise equality treating NaN == NaN as equal."""
    a = pd.to_numeric(a, errors="coerce").to_numpy(dtype=float)
    b = pd.to_numeric(b, errors="coerce").to_numpy(dtype=float)
    ambos_nan = np.isnan(a) & np.isnan(b)
    if tolerancia == 0:
        return (a == b) | ambos_nan
    return np.isclose(a, b, rtol=0, atol=tolerancia) | ambos_nan


def _iguales_objetos(a, b):
    """
    Element-wise equality for text / boolean columns, treating missing == missing.

    Careful with pandas >= 3: comparing two missing values (pd.NA) gives
    "missing", not True, and `astype(str)` does not help either. So: compare
    the present values, then explicitly count "both missing" as equal.
    """
    a = pd.Series(a).reset_index(drop=True).astype(object)
    b = pd.Series(b).reset_index(drop=True).astype(object)
    ambos_faltan = a.isna() & b.isna()
    presentes_iguales = pd.Series([x == y if not (pd.isna(x) or pd.isna(y)) else False
                                   for x, y in zip(a, b)], dtype=bool)
    return (presentes_iguales | ambos_faltan).to_numpy()


def comparar_modulos_con_parquet_viejo(df_nuevo, df_viejo, eventos=None, tolerancia_geometria=1e-9,
                                       imprimir=True):
    """
    Check 1. `eventos`: optional list of event_id to restrict the OLD parquet to
    (used by short pilots that only read the first N events of a file).
    Returns a dict with the numbers, and prints a readable report.
    """
    log = print if imprimir else (lambda *args, **kwargs: None)
    viejo = df_viejo.copy()
    nuevo = df_nuevo.copy()
    viejo["event_id"] = viejo["event_id"].astype(str)
    nuevo["event_id"] = nuevo["event_id"].astype(str)
    if eventos is not None:
        viejo = viejo[viejo["event_id"].isin(set(map(str, eventos)))]

    nuevo_con_rec = nuevo[nuevo["has_sd_rec"]]
    nuevo_sin_rec = nuevo[~nuevo["has_sd_rec"]]

    union = nuevo_con_rec.merge(viejo, on=CLAVE_MODULO, how="outer",
                                suffixes=("_nuevo", "_viejo"), indicator=True)
    solo_nuevo = int((union["_merge"] == "left_only").sum())
    solo_viejo = int((union["_merge"] == "right_only").sum())
    ambos = union[union["_merge"] == "both"]

    log("── Check 1: módulos nuevos con has_sd_rec=True vs parquet v17 viejo")
    log(f"   filas viejas: {len(viejo)} | nuevas con SD REC: {len(nuevo_con_rec)} "
          f"| nuevas SIN SD REC (añadidas por el flag): {len(nuevo_sin_rec)}")
    filas_ok = (solo_nuevo == 0) and (solo_viejo == 0)
    log(f"   [{_estado(filas_ok)}] mismas filas: sólo en nuevo={solo_nuevo}, "
          f"sólo en viejo (PERDIDAS)={solo_viejo}")

    resultado = {"filas_viejas": len(viejo), "filas_nuevas_con_rec": len(nuevo_con_rec),
                 "filas_nuevas_sin_rec": len(nuevo_sin_rec), "perdidas": solo_viejo,
                 "sobrantes": solo_nuevo, "columnas_analisis_ok": True, "otras_columnas": {}}

    for col in COLUMNAS_ANALISIS:
        tol = tolerancia_geometria if col in ("r_core_MC", "phi_plane_euler_MC_true_core") else 0
        distintos = int((~_iguales(ambos[col + "_nuevo"], ambos[col + "_viejo"], tol)).sum())
        ok = distintos == 0
        resultado["columnas_analisis_ok"] &= ok
        log(f"   [{_estado(ok)}] {col}: filas distintas = {distintos} (tolerancia {tol})")

    # Every other shared column: report only.
    otras = [c for c in viejo.columns if c not in CLAVE_MODULO and c not in COLUMNAS_ANALISIS
             and c + "_nuevo" in ambos.columns]
    for col in otras:
        x, y = ambos[col + "_nuevo"], ambos[col + "_viejo"]
        if pd.api.types.is_numeric_dtype(y) and not pd.api.types.is_bool_dtype(y):
            distintos = int((~_iguales(x, y, 1e-9)).sum())
        else:
            distintos = int((~_iguales_objetos(x, y)).sum())
        resultado["otras_columnas"][col] = distintos
    cambiadas = {c: n for c, n in resultado["otras_columnas"].items() if n}
    log(f"   [INFO] otras columnas con diferencias (no usadas en el análisis): "
          f"{cambiadas if cambiadas else 'ninguna'}")
    return resultado


def comparar_estaciones_con_extraccion_astra(df_estaciones, df_astra, imprimir=True):
    """
    Check 2. `df_astra` = rows of adst_counts_fast.csv for the SAME file(s).
    Astra's extraction applied: 30 <= theta < 40, 2000 < sdId < 90000,
    150 <= r < 1800. We apply the same cuts to the new table, then compare.
    """
    log = print if imprimir else (lambda *args, **kwargs: None)
    nuevo = df_estaciones.copy()
    nuevo["event_id"] = nuevo["event_id"].astype(str)
    nuevo = nuevo[nuevo["theta_MC"].between(30, 40, inclusive="left")
                  & (nuevo["sdId"] > 2000) & (nuevo["sdId"] < 90000)
                  & nuevo["r_core_MC"].between(150, 1800, inclusive="left")]

    astra = df_astra.copy()
    astra["event_id"] = astra["event_id"].astype(str)
    # Astra stored phi WITHOUT the +pi, in (-pi, pi]. Convert to the pipeline's
    # convention [0, 2pi) with +pi so both can be compared directly.
    astra["phi_mas_pi"] = (astra["phi"] + np.pi + 2*np.pi) % (2*np.pi)

    union = nuevo.merge(astra, on=CLAVE_ESTACION, how="outer", indicator=True)
    solo_nuevo = int((union["_merge"] == "left_only").sum())
    solo_astra = int((union["_merge"] == "right_only").sum())
    ambos = union[union["_merge"] == "both"]

    log("── Check 2: estaciones SD nuevas vs extracción de Astra (adst_counts_fast.csv)")
    log(f"   estaciones Astra: {len(astra)} | nuevas (mismos cortes): {len(nuevo)}")
    ok_filas = solo_nuevo == 0 and solo_astra == 0
    log(f"   [{_estado(ok_filas)}] mismas estaciones: sólo nuevo={solo_nuevo}, sólo Astra={solo_astra}")
    mu_dist = int((ambos["sd_nMuons_MC"].to_numpy(float) != ambos["mu"].to_numpy(float)).sum())
    rec_dist = int((ambos["has_sd_rec"].astype(int).to_numpy() != ambos["has_rec"].to_numpy()).sum())
    r_max = float(np.max(np.abs(ambos["r_core_MC"] - ambos["r"]))) if len(ambos) else 0.0
    dphi = np.abs((ambos["phi_plane_euler_MC_true_core"] - ambos["phi_mas_pi"] + np.pi) % (2*np.pi) - np.pi)
    phi_max = float(dphi.max()) if len(ambos) else 0.0
    log(f"   [{_estado(mu_dist == 0)}] muones SD idénticos: filas distintas = {mu_dist}")
    log(f"   [{_estado(rec_dist == 0)}] has_sd_rec idéntico: filas distintas = {rec_dist}")
    log(f"   [{_estado(r_max < 1e-6)}] r: máxima diferencia = {r_max:.2e} m")
    log(f"   [{_estado(phi_max < 1e-9)}] phi: máxima diferencia = {phi_max:.2e} rad")
    return {"solo_nuevo": solo_nuevo, "solo_astra": solo_astra, "mu_distintos": mu_dist,
            "rec_distintos": rec_dist, "r_max": r_max, "phi_max": phi_max}


def consistencia_modulos_estaciones(df_modulos, df_estaciones, imprimir=True):
    """
    Check 3. Table A has one row per MODULE, so the same SD station repeats
    (once per module). Deduplicate to one row per station and compare with
    table B for reconstructed Infill stations.
    """
    log = print if imprimir else (lambda *args, **kwargs: None)
    a = df_modulos[df_modulos["has_sd_rec"] & (df_modulos["counterId"] >= 100000)].copy()
    a["event_id"] = a["event_id"].astype(str)
    a = a.drop_duplicates(CLAVE_ESTACION)
    b = df_estaciones.copy()
    b["event_id"] = b["event_id"].astype(str)

    union = a.merge(b, on=CLAVE_ESTACION, how="left", suffixes=("_A", "_B"), indicator=True)
    faltan_en_b = int((union["_merge"] == "left_only").sum())
    ambos = union[union["_merge"] == "both"]
    log("── Check 3: estaciones de la tabla A (dedup.) presentes y consistentes en la tabla B")
    log(f"   [{_estado(faltan_en_b == 0)}] estaciones de A ausentes en B: {faltan_en_b} de {len(a)}")
    for col, tol in [("sd_nMuons_MC", 0), ("sd_nEM_MC", 0),
                     ("r_core_MC", 1e-9), ("phi_plane_euler_MC_true_core", 1e-12)]:
        distintos = int((~_iguales(ambos[col + "_A"], ambos[col + "_B"], tol)).sum())
        log(f"   [{_estado(distintos == 0)}] {col}: filas distintas = {distintos}")
    return {"faltan_en_b": faltan_en_b}
