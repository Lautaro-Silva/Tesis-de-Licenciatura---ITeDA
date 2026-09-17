"""
validar_piloto.py -- run the three checks of validaciones.py on a pilot output.

Pandas only (no ROOT). Example, from this folder's parent:

    venv/bin/python piloto/validar_piloto.py --etiqueta test7_run010_completo

Checks:
  1. modulos[has_sd_rec] vs your old v11 parquet (same rows, identical analysis columns)
  2. estaciones_sd vs Astra's extraction adst_counts_fast.csv (same stations, counts, geometry)
  3. modulos (deduplicated) vs estaciones_sd (consistent counts and geometry)
If the pilot read only N events, the old parquet is restricted to those events.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
CARPETA = AQUI.parent
sys.path.insert(0, str(CARPETA))
import validaciones as v   # noqa: E402

RUN_POR_DEFECTO = "SIB23e_175_180_proton_MdSdInfill_CORSIKA78010_FLUKA_Run010"
V11 = Path("/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17")
CSV_ASTRA = CARPETA.parent / "revision_asimetrias_sd_umd/04_soporte/tablas/adst_counts_fast.csv"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--etiqueta", required=True, help="pilot subfolder inside piloto/")
    p.add_argument("--run", default=RUN_POR_DEFECTO, help="file stem, without extension")
    p.add_argument("--eventos-parciales", action="store_true",
                   help="the pilot read only some events: restrict the comparisons to them")
    args = p.parse_args()

    base = AQUI / args.etiqueta
    mod = pd.read_parquet(base / "modulos" / f"{args.run}.parquet")
    est = pd.read_parquet(base / "estaciones_sd" / f"{args.run}.parquet")
    viejo = pd.read_parquet(V11 / f"{args.run}.parquet")
    eventos = mod.event_id.unique() if args.eventos_parciales else None

    print(f"Piloto: {base}")
    print(f"  módulos: {len(mod)} | estaciones SD: {len(est)} | eventos: {mod.event_id.nunique()}\n")

    v.comparar_modulos_con_parquet_viejo(mod, viejo, eventos=eventos)
    print()

    astra = pd.read_csv(CSV_ASTRA, dtype={"event_id": str})
    astra = astra[astra.source == args.run + ".root"]
    if eventos is not None:
        astra = astra[astra.event_id.isin(set(map(str, eventos)))]
    v.comparar_estaciones_con_extraccion_astra(est, astra)
    print()

    v.consistencia_modulos_estaciones(mod, est)
    print()

    meta = ["model_mc", "e_min_mc", "e_max_mc", "primary_name_mc", "run_number"]
    print("Metadatos (módulos):", mod[meta].iloc[0].to_dict())
    print("Metadatos (estaciones_sd):", est[meta].iloc[0].to_dict())
    tipos = {c: (str(viejo[c].dtype), str(mod[c].dtype)) for c in viejo.columns
             if c in mod.columns and str(viejo[c].dtype) != str(mod[c].dtype)}
    print("Columnas con dtype distinto al parquet viejo:", tipos or "ninguna")


if __name__ == "__main__":
    main()
