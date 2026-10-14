#!/usr/bin/env bash
# Build the defense deck with pdflatex (no latexmk on this machine: two passes).
set -euo pipefail
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error presentacion_defensa_2026.tex
pdflatex -interaction=nonstopmode -halt-on-error presentacion_defensa_2026.tex
echo "OK: presentacion_defensa_2026.pdf"
