"""
correr_piloto.py -- run the new reader on ONE file, in ONE process.

Purpose: prove that lector_adst_v17_completo works on a real ADST and produces
the same module table as the old v17 parquet, before anyone launches the full
8-worker run.

It calls exactly the same `process_file_wrapper` the notebook uses, so the
pilot also exercises the parquet writing. Output goes ONLY to
    piloto/<etiqueta>/modulos/, piloto/<etiqueta>/estaciones_sd/, piloto/<etiqueta>/resumen/
(ignored by git).

The Offline version is whatever AUGEROFFLINEROOT points to, as in your
notebooks. Example (icrc2025-test7-root6), from the repository root:

    source /srv/software/amd64/ubuntu/24.04/auger/offline/icrc2025-test7-root6/bin/this-auger-offline.sh
    venv/bin/python claude_work/reprocesamiento_sd_completo/piloto/correr_piloto.py \
        --etiqueta test7_50ev --max-events 50
"""

import argparse
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.dirname(AQUI)                  # claude_work/reprocesamiento_sd_completo
sys.path.insert(0, CARPETA)                      # so that `import lector_adst_v17_completo` works

import lector_adst_v17_completo as lector       # noqa: E402  (imports ROOT)

ARCHIVO_POR_DEFECTO = (
    "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/"
    "SIB23e/17.5_18.0/proton/SIB23e_175_180_proton_MdSdInfill_CORSIKA78010_FLUKA_Run010.root"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archivo", default=ARCHIVO_POR_DEFECTO, help="ADST .root to read")
    parser.add_argument("--etiqueta", required=True,
                        help="name of the output subfolder inside piloto/ (must be new)")
    parser.add_argument("--max-events", type=int, default=None,
                        help="stop after N events (default: whole file)")
    args = parser.parse_args()

    salida = os.path.join(AQUI, args.etiqueta)
    if os.path.exists(salida):
        parser.error(f"{salida} ya existe: elegí otra etiqueta (no se sobreescribe nada).")

    lector.cargar_offline()
    inicio = time.time()
    mensaje = lector.process_file_wrapper(args.archivo, salida, max_events=args.max_events)
    print(mensaje)
    print(f"Tiempo total del piloto: {time.time() - inicio:.1f} s")
    if "❌" in mensaje:
        sys.exit(1)


if __name__ == "__main__":
    main()
