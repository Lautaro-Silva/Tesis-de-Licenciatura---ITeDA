"""Verifica las cifras del capítulo 6 con los parquet ya existentes.

No importa ROOT, no reprocesa ADST y no cambia ningún dato de entrada.
Procesa un archivo a la vez en un solo proceso. Ejecutar desde la raíz:

  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python \
    claude_work/borradores_capitulos_3_5_6_integrados_2026_09_24/verificar_seleccion.py

La incertidumbre bootstrap se lee del análisis previo: este control reproduce
las muestras, estimaciones centrales y errores formales, NO repite el bootstrap.
Sólo escribe verificacion_seleccion.json, junto a este script.
"""

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
ANTERIOR = REPO / "claude_work/revision_asimetrias_sd_umd"
V11 = Path("/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17")
V13 = Path("/home/lsilva/Github/ADST_Alexey_module_v13/parquet_sib_proton_17")
CLAVE_MOD = ["event_id", "counterId", "moduleId", "sdId"]
CLAVE_SD = ["event_id", "sdId"]
GEOMETRIA = ["r_core_MC", "phi_plane_euler_MC_true_core"]


def main():
    # Usar LITERALMENTE el estimador que produjo el PDF de referencia.
    # Extraer sólo estas dos funciones evita ejecutar las celdas del notebook.
    fuente_ajuste = ANTERIOR / "02_notebooks/02_reproduccion/reproducir_desglose_sd.py"
    arbol = ast.parse(fuente_ajuste.read_text())
    funciones = [n for n in arbol.body if isinstance(n, ast.FunctionDef)
                 and n.name in ("harmonic_model", "fit_one_band")]
    assert len(funciones) == 2
    contexto = dict(np=np, pd=pd, curve_fit=curve_fit,
                    phi_bin_edges=np.linspace(-180, 180, 13),
                    phi_centers=np.arange(-165, 180, 30))
    exec(compile(ast.Module(body=funciones, type_ignores=[]), str(fuente_ajuste), "exec"), contexto)
    ajustar = contexto["fit_one_band"]

    ruta_raw = ANTERIOR / "04_soporte/tablas/adst_counts_fast.csv"
    raw = pd.read_csv(ruta_raw, dtype={"event_id": str})
    archivos = sorted((V13 / "modulos").glob("*.parquet"))
    nombres = {f.name for f in archivos}
    assert nombres, "No se encuentran los parquet v13."
    assert nombres == {f.name for f in V11.glob("*.parquet")}
    assert nombres == {f.name for f in (V13 / "estaciones_sd").glob("*.parquet")}
    assert {Path(n).with_suffix(".root").name for n in nombres} == set(raw.source)

    resumen = dict(archivos=len(archivos), filas_v11=0, filas_v13_seleccionadas=0,
                   filas_modulos_agregadas=0, estaciones_sd_totales=0,
                   eventos_escritos=0, max_diferencia_radio_m=0.0,
                   max_diferencia_phi_rad=0.0)
    partes_sd, partes_umd = [], []
    for archivo in archivos:
        mod = pd.read_parquet(archivo)
        est = pd.read_parquet(V13 / "estaciones_sd" / archivo.name)
        viejo = pd.read_parquet(V11 / archivo.name)
        assert not mod.duplicated(CLAVE_MOD).any()
        assert not est.duplicated(CLAVE_SD).any()
        seleccionado = mod[mod.has_sd_rec].set_index(CLAVE_MOD).sort_index()
        viejo = viejo.set_index(CLAVE_MOD).sort_index()
        # Igualdad de valores de TODAS las columnas viejas, no sólo de seis.
        # Se permite el cambio int -> bool nullable sin aceptar cambios de valor.
        pd.testing.assert_frame_equal(seleccionado[viejo.columns], viejo,
                                      check_dtype=False, check_exact=True)
        resumen["filas_v11"] += len(viejo)
        resumen["filas_v13_seleccionadas"] += len(seleccionado)
        resumen["filas_modulos_agregadas"] += int((~mod.has_sd_rec).sum())
        resumen["estaciones_sd_totales"] += len(est)
        resumen["eventos_escritos"] += est.event_id.nunique()

        # La ventana es la de la extracción previa, no toda la producción.
        ventana = est[est.theta_MC.between(30, 40, inclusive="left")
                      & (est.sdId > 2000) & (est.sdId < 90000)
                      & est.r_core_MC.between(150, 1800, inclusive="left")].copy()
        referencia = raw[raw.source == archivo.with_suffix(".root").name]
        union = ventana.merge(referencia, on=CLAVE_SD, how="outer",
                               indicator=True, validate="one_to_one")
        assert union._merge.eq("both").all()
        np.testing.assert_array_equal(union.sd_nMuons_MC, union.mu)
        np.testing.assert_array_equal(union.has_sd_rec.astype(int), union.has_rec)
        dr = np.abs(union.r_core_MC - union.r)
        # El parquet tiene +pi histórico; el CSV guarda atan2 sin ese giro.
        dp = np.abs((union.phi_plane_euler_MC_true_core - (union.phi + np.pi)
                     + np.pi) % (2 * np.pi) - np.pi)
        assert dr.max() < 1e-6 and dp.max() < 1e-9
        resumen["max_diferencia_radio_m"] = max(resumen["max_diferencia_radio_m"], float(dr.max()))
        resumen["max_diferencia_phi_rad"] = max(resumen["max_diferencia_phi_rad"], float(dp.max()))

        # Coherencia de las dos tablas sin confundir módulo con estación.
        a = mod[mod.has_sd_rec & (mod.counterId >= 100000)].drop_duplicates(CLAVE_SD).set_index(CLAVE_SD)
        b = est.set_index(CLAVE_SD).loc[a.index]
        for col in ["sd_nMuons_MC", "sd_nEM_MC", *GEOMETRIA]:
            np.testing.assert_allclose(a[col], b[col], rtol=0, atol=1e-12, equal_nan=True)
        partes_sd.append(ventana)
        partes_umd.append(mod[(mod.counterId >= 100000)
                             & mod.theta_MC.between(30, 40, inclusive="left")].copy())
        print(archivo.stem, "PASS", flush=True)

    sd = pd.concat(partes_sd, ignore_index=True)
    umd = pd.concat(partes_umd, ignore_index=True)
    for tabla in (sd, umd):
        tabla["phi_MC_Truth"] = np.rad2deg(tabla.phi_plane_euler_MC_true_core) % 360 - 180
    resumen.update(estaciones_ventana=len(sd), estaciones_ventana_con_rec=int(sd.has_sd_rec.sum()),
                   estaciones_ventana_sin_rec=int((~sd.has_sd_rec).sum()))

    filas = []
    for columna in ["sd_nMuons_MC", "sd_nEM_MC"]:
        for nombre, tabla in [("Antes de HasStation", sd), ("HasStation=True", sd[sd.has_sd_rec])]:
            for lo in range(150, 1350, 150):
                banda = tabla[tabla.r_core_MC.between(lo, lo + 150, inclusive="left")]
                filas.append(dict(column=columna, sample=nombre, r_min=lo, r_max=lo + 150,
                                  **ajustar(banda, columna)))
    ajustes = pd.DataFrame(filas)
    ruta_ref = ANTERIOR / "02_notebooks/02_reproduccion/resultados/seleccion_mismos_bins_ajuste_ponderado.csv"
    ref = pd.read_csv(ruta_ref)
    # La tabla incluye además una tercera muestra de control (parquet
    # deduplicado); el PDF antes/después utiliza estas dos muestras.
    ref = ref[ref['sample'].isin(['Antes de HasStation', 'HasStation=True'])]
    pares = ajustes.merge(ref, on=["column", "sample", "r_min", "r_max"],
                          suffixes=("_nuevo", "_ref"), validate="one_to_one")
    assert len(pares) == len(ref) == 32
    for col in ["A1", "error"]:
        np.testing.assert_allclose(pares[col + "_nuevo"], pares[col + "_ref"], rtol=0, atol=1e-8)
    assert pares.n_rows_nuevo.eq(pares.n_rows_ref).all()
    resumen["ajustes_pdf_verificados"] = len(pares)
    resumen["max_diferencia_A1"] = float((pares.A1_nuevo - pares.A1_ref).abs().max())

    far = umd[umd.r_core_MC.between(1200, 1350, inclusive="left")]
    resumen["UMD_1200_1350_seleccionado"] = ajustar(far[far.has_sd_rec], "nMuones_MC")
    resumen["UMD_1200_1350_todos_los_modulos_disponibles"] = ajustar(far, "nMuones_MC")
    resumen["SD_1200_1350"] = ajustes[(ajustes.column == "sd_nMuons_MC")
                                     & (ajustes.r_min == 1200)].to_dict("records")
    ruta_boot = ANTERIOR / "02_notebooks/03_sd_vs_umd/resultados/comparacion_directa.csv"
    bootstrap = pd.read_csv(ruta_boot)
    resumen["bootstrap_previo_1200_1350_NO_recalculado"] = bootstrap.iloc[-1].to_dict()
    resumen["sha256_fuentes"] = {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (fuente_ajuste, ruta_raw, ruta_ref, ruta_boot)}
    (AQUI / "verificacion_seleccion.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
