#!/usr/bin/env bash
# Builds notas_expositor.pdf (A4, printable "machete") from notas_expositor.md.
# Requires pandoc and LuaLaTeX.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
python3 scripts/notas_preprocesar.py notas_expositor.md build/notas_para_pdf.md
pandoc build/notas_para_pdf.md \
  --from markdown-auto_identifiers \
  --pdf-engine=lualatex \
  --include-in-header=scripts/notas_estilo.tex \
  -V documentclass=article -V papersize=a4 -V fontsize=11pt \
  -V geometry:margin=1.6cm \
  -V lang=es -V colorlinks=true \
  -o notas_expositor.pdf
echo "OK: notas_expositor.pdf ($(pdfinfo notas_expositor.pdf | awk '/Pages/{print $2}') páginas)"
