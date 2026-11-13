#!/usr/bin/env bash
# Build a talk with pdflatex (two passes each):
#   <name>.pdf        slides only
#   <name>_notas.pdf  slides + speaker notes
# Usage: ./compilar.sh                          (UMD Foundations Meeting deck)
#        ./compilar.sh charla_malargue_2026     (short version, Auger Collaboration Meeting)
set -euo pipefail
cd "$(dirname "$0")"
name="${1:-charla_colaboracion_2026}"
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error "${name}.tex"
done
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="${name}_notas" \
    "\def\withnotes{1}\input{${name}.tex}"
done
echo "OK: ${name}.pdf, ${name}_notas.pdf"
