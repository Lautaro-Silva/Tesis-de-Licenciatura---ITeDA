#!/usr/bin/env bash
# Renders the compiled PDF into PNG pages and 2x2 contact sheets for review.
# Usage: scripts/revisar.sh OUTDIR [first last]
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-build/revision}; F=${2:-1}; L=${3:-$(pdfinfo coloquio_iteda.pdf | awk '/Pages/{print $2}')}
mkdir -p "$OUT"; rm -f "$OUT"/p-*.png "$OUT"/hoja_*.png
pdftoppm -r 115 -png -f "$F" -l "$L" coloquio_iteda.pdf "$OUT/p"
ls "$OUT"/p-*.png | sort > "$OUT/lista"
split -l 4 -d "$OUT/lista" "$OUT/grupo_"
for g in "$OUT"/grupo_*; do
  montage $(cat "$g") -tile 2x2 -geometry +4+4 -background '#888' "$OUT/hoja_$(basename "$g" | sed 's/grupo_//').png"
done
rm -f "$OUT"/grupo_* "$OUT/lista"
ls "$OUT"/hoja_*.png
