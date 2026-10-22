#!/usr/bin/env bash
# Build the collaboration talk with pdflatex (two passes each):
#   charla_colaboracion_2026.pdf        slides only
#   charla_colaboracion_2026_notas.pdf  slides + speaker notes
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error charla_colaboracion_2026.tex
done
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error -jobname=charla_colaboracion_2026_notas \
    "\def\withnotes{1}\input{charla_colaboracion_2026.tex}"
done
echo "OK: charla_colaboracion_2026.pdf, charla_colaboracion_2026_notas.pdf"
