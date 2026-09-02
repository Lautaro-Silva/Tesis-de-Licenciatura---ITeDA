"""
Verifica que la conversion .ipynb -> .py (jupytext, formato percent) fue
puramente de formato: que el contenido de cada celda (codigo y markdown)
es identico, caracter por caracter, entre el notebook original (tal como
estaba comiteado en git antes de la conversion) y el .py convertido.

Uso:
    venv/bin/python claude_work/notebooks_a_py/verificar_roundtrip.py [--base-ref HEAD]

No modifica nada; solo lee del working tree y de git, y escribe archivos
temporales de comparacion bajo $CLAUDE_JOB_DIR/tmp (o /tmp si no esta
definida esa variable).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import jupytext

NOTEBOOKS = [
    "Scripts/plots_seccion_6.ipynb",
    "Scripts/validacion_rec_muones.ipynb",
    "Scripts/analisis_infill_sims.ipynb",
    "Scripts/validacion_asimetria_infill_sd_mu_v2.ipynb",
    "Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.ipynb",
    "Scripts/Procesamiento_ADST_v8-2.ipynb",
    "Scripts/Procesamiento_ADST_Campo_v9.ipynb",
    "Scripts/Procesamiento_Datos_Campo/Procesamiento_Datos_Campo_v1.ipynb",
    "Scripts/Procesamiento_Datos_Campo/Analisis_Preliminar_DatosCampo_Phase1.ipynb",
    "Scripts/Procesamiento_Datos_Campo/Analisis_Preliminar_DatosCampo_Phase2.ipynb",
]


def cell_sources(nb_dict):
    """Lista de (cell_type, source_texto) para las celdas de codigo y markdown."""
    out = []
    for cell in nb_dict["cells"]:
        ctype = cell["cell_type"]
        if ctype not in ("code", "markdown"):
            continue
        src = cell["source"]
        if isinstance(src, list):
            src = "".join(src)
        out.append((ctype, src))
    return out


def original_cells_from_git(repo_root, rel_path, base_ref):
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{rel_path}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    nb = json.loads(result.stdout)
    return cell_sources(nb)


def converted_cells_from_py(repo_root, py_path):
    nb = jupytext.read(os.path.join(repo_root, py_path))
    # jupytext.read returns a notebook object (dict-like, NotebookNode)
    return cell_sources(nb)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="git ref donde esta el .ipynb original antes de la conversion (default: HEAD)",
    )
    args = parser.parse_args()

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    tmp_dir = os.environ.get("CLAUDE_JOB_DIR")
    tmp_dir = os.path.join(tmp_dir, "tmp") if tmp_dir else tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)

    all_ok = True
    report_lines = []
    report_lines.append(f"base_ref = {args.base_ref}")
    report_lines.append("")

    for ipynb_rel in NOTEBOOKS:
        py_rel = ipynb_rel[: -len(".ipynb")] + ".py"
        try:
            original = original_cells_from_git(repo_root, ipynb_rel, args.base_ref)
        except subprocess.CalledProcessError as e:
            all_ok = False
            msg = f"[ERROR] {ipynb_rel}: no se pudo leer de git ({args.base_ref}): {e.stderr.strip()}"
            print(msg)
            report_lines.append(msg)
            continue

        try:
            converted = converted_cells_from_py(repo_root, py_rel)
        except Exception as e:
            all_ok = False
            msg = f"[ERROR] {py_rel}: no se pudo leer/convertir: {e!r}"
            print(msg)
            report_lines.append(msg)
            continue

        if len(original) != len(converted):
            all_ok = False
            msg = (
                f"[DIFF ] {ipynb_rel}: distinto numero de celdas "
                f"(original={len(original)}, convertido={len(converted)})"
            )
            print(msg)
            report_lines.append(msg)
            continue

        diffs = []
        for i, ((ot, os_), (ct, cs)) in enumerate(zip(original, converted)):
            if ot != ct:
                diffs.append(f"  celda {i}: tipo distinto ({ot} vs {ct})")
            elif os_ != cs:
                diffs.append(f"  celda {i} ({ot}): fuente distinta")

        if diffs:
            all_ok = False
            msg = f"[DIFF ] {ipynb_rel}: {len(diffs)} celda(s) con diferencias"
            print(msg)
            report_lines.append(msg)
            report_lines.extend(diffs)
        else:
            msg = f"[OK   ] {ipynb_rel}  <->  {py_rel}  ({len(original)} celdas, fuente identica)"
            print(msg)
            report_lines.append(msg)

    report_path = os.path.join(tmp_dir, "roundtrip_report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")

    print()
    print(f"Reporte completo en: {report_path}")
    if all_ok:
        print("RESULTADO: 0 diferencias en los 10 notebooks. Conversion verificada.")
        sys.exit(0)
    else:
        print("RESULTADO: hay diferencias. Revisar antes de continuar.")
        sys.exit(1)


if __name__ == "__main__":
    main()
