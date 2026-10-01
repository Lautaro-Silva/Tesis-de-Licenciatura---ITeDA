#!/usr/bin/env bash
# Compila únicamente los documentos de esta carpeta. No modifica la tesis.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p compilacion
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -output-directory=compilacion vista_previa.tex > compilacion/paso1.txt 2>&1
biber --input-directory=compilacion --output-directory=compilacion vista_previa > compilacion/biber.txt 2>&1
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -output-directory=compilacion vista_previa.tex > compilacion/paso2.txt 2>&1
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -output-directory=compilacion vista_previa.tex > compilacion/paso3.txt 2>&1
cp compilacion/vista_previa.pdf capitulo_3.pdf
pandoc RESPUESTAS_Y_CRITERIOS.md --standalone --pdf-engine=pdflatex \
  -V geometry:margin=2.5cm -V fontsize=11pt -V colorlinks=true \
  -o RESPUESTAS_Y_CRITERIOS.pdf > compilacion/respuestas.txt 2>&1
printf '%s\n' 'Listos: capitulo_3.pdf y RESPUESTAS_Y_CRITERIOS.pdf'
