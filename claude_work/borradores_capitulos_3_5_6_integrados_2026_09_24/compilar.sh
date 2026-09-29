#!/usr/bin/env bash
# Ejecutar desde cualquier directorio. Sólo escribe dentro de esta carpeta.
# No compila ni modifica Tesis - Latex/main.tex.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p compilacion
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=compilacion vista_previa.tex
biber --input-directory=compilacion --output-directory=compilacion vista_previa
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=compilacion vista_previa.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=compilacion vista_previa.tex
