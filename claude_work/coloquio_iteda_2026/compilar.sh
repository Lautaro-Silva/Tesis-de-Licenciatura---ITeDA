#!/usr/bin/env bash
# Compila la presentación con LuaLaTeX (dos pasadas para overlays y numeración)
# y deja el resultado en coloquio_iteda.pdf.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex > build/pasada1.log
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex > build/pasada2.log
cp build/main.pdf coloquio_iteda.pdf
echo "OK: coloquio_iteda.pdf ($(pdfinfo coloquio_iteda.pdf | awk '/Pages/{print $2}') páginas)"
grep -c "Overfull" build/main.log | xargs echo "Overfull boxes:"
