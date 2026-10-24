# Huellas del universo — ITeDA colloquium

Beamer deck (16:9, LuaLaTeX, metropolis + ITeDA palette, the same visual identity as the thesis defense and RAFA 2026 decks).

- `coloquio_iteda.pdf`: compiled deck, 57 main slides + 9 backup slides (66 pages).
- `notas_expositor.md`: speaker notes per slide (physics, numbers, transitions, timing), in Spanish.
- `fuentes_figuras.md`: provenance and licence of every figure and dataset.
- `references.bib`: references behind the numbers (reference list, not compiled into the deck).

## Build

```bash
./compilar.sh              # two LuaLaTeX passes -> coloquio_iteda.pdf (≈1–3 min)
scripts/notas_a_pdf.sh     # notas_expositor.md -> notas_expositor.pdf (A4, printable)
```

The FIFA logo on the cover is optional: drop it at `figures/logos/logo_fifa.png` and recompile. Previous versions of the deck and notes are kept in `versiones/`.

Requires TeX Live with LuaLaTeX, Fira Sans / Fira Math (shipped with TeX Live), metropolis, pgfplots, tcolorbox and fontawesome5. Intermediate files go to `build/`.

## Layout

```
main.tex                 preamble + \input of each block
sections/00_preambulo.tex   theme, colours, helper macros (\fondo, \velo, \credito, clave box, \geo map coords)
sections/01_intro.tex ... 07_heron_cierre.tex   one file per narrative block
sections/08_respaldo.tex    backup slides (after \appendix, not counted in the main numbering)
figures/{tesis,halzen,qubic,heron,externas,generadas,logos}/
data/                    tables read by PGFPlots (generated) and data/raw/ (downloaded originals)
scripts/preparar_datos.py   FIRAS, Planck and Saha tables -> data/*.dat
scripts/mapa_argentina.py   base map for slide 2 (Natural Earth)
scripts/revisar.sh          renders the PDF into PNG contact sheets for visual review
scripts/recortar.sh         centre-crops a photo to a given aspect ratio
```

Regenerating the data tables and the map needs only numpy and matplotlib (the thesis repo's `venv/` works):

```bash
python scripts/preparar_datos.py
python scripts/mapa_argentina.py
```

## Editing tips

- Each block's tag in the title bar is set with `\bloque{...}` before a frame.
- Full-bleed photo slides use `\fondo[darkening][w|h]{file}` plus `\velo[opacity]{l|b|t}` for a readable gradient.
- Credits: `\credito{}` (bottom right), `\creditoizq{}` (bottom left), `\creditoblanco{}` (on dark photos).
- `\esquematico` and `\preliminar` add the small "ILUSTRACIÓN ESQUEMÁTICA" / "PRELIMINAR" badges.
