#!/usr/bin/env bash
# Compila la presentación con pdflatex (no hay latexmk en esta máquina: dos pasadas).
set -euo pipefail
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error presentacion_rafa_2026.tex
pdflatex -interaction=nonstopmode -halt-on-error presentacion_rafa_2026.tex
echo "OK: presentacion_rafa_2026.pdf"
