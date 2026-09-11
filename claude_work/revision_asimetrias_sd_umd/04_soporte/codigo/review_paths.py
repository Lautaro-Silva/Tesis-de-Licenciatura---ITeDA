"""Explicit locations for the consolidated legacy audit scripts."""
from pathlib import Path

CODE = Path(__file__).resolve().parent
PACKAGE = CODE.parents[1]
REPO = next(p for p in PACKAGE.parents if (p / 'CLAUDE.md').is_file())
TABLES = PACKAGE / '04_soporte/tablas'
PHYSICS = PACKAGE / '01_fisica'
FIGURES = PACKAGE / '04_soporte/figuras'
TEMPLATES = PACKAGE / '04_soporte/plantillas'
