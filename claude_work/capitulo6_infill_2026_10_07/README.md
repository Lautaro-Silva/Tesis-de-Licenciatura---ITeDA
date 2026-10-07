# Chapter 6 revision (2026-10-07), second attempt

Branch: `claude/capitulo6-infill` (worktree). Nothing committed.

The chapter was edited **in place** from the author's `capitulos/06_infill.tex`. Every change is marked
in the source with `% REVISAR:` and the replaced text with `% ORIGINAL:` (35 marks).

| What | Where |
|---|---|
| Edited chapter (book class) | `Tesis - Latex/DRAFTS/06_infill.tex` |
| Chapter PDF | `Tesis - Latex/DRAFTS/06_infill_BORRADOR.pdf`, copy at repo root |
| Full-thesis preview (book class; DRAFTS 03, 05, 06) | `vista_previa_tesis.pdf` (this folder, main checkout only; 8.6 MB, not committed; regenerate with `construir_vista_previa.py`) |
| External literature search: notes, quotes, proposed sentences, candidate BibTeX | `bibliografia_externa/` (nothing inserted in the chapter) |
| Chapter PDF with Claude's changes in blue | `Tesis - Latex/DRAFTS/06_infill_MARCADO.pdf`, copy at repo root |
| New figures | `imagenes_capitulos/cap6/SD_Seleccion_Estaciones_vs_UMD.pdf` and `SD_Muones_Tanques_Excluidos.pdf` (last two cells of `Scripts/plots_seccion_6.py`) |
| Preview builder | `construir_vista_previa.py` (`--marcado` builds the coloured version) |
| Marked-copy generator (wraps changed paragraphs in blue) | `marcar_cambios.py` → `DRAFTS/06_infill_marcado.tex` (generated, do not edit) |
| Numbers from the discarded first attempt, used for the table and the mass/energy section | `referencia_intento_descartado/` |

The first attempt (full rewrite plus a separate notebook) was discarded at the author's request;
only its numeric results and the notebook that produced them are kept in `referencia_intento_descartado/`.

## What changed in the chapter

- Sectioning promoted for the book class; all labels kept (`cap:infill`, `subsec:infill_mc`,
  `subsec:infill_rec` are used by Ch. 7).
- Removed or rewritten, per final Ch. 3/5: Población B, A_geo "explota", UMD as "filtro
  cinemático", lim p_z→∞, "no es artefacto de reconstrucción", "irrefutable/contundente", the
  `subsubsec:divergencia` misuse, "cota superior / lower bound", "smearing angular".
- New subsection `subsec:seleccion_estaciones` (Eq. `eq:seleccion` + Poisson example from the old
  Ch. 3, HasStation control, new figure, hypothesis paragraph, open SD–UMD gap).
- Selection-hypothesis check (author's request): histogram of MC muons crossing each SD tank that
  is excluded (HasStation = False) vs retained, early vs late, 900–1500 m, 30–40°
  (`fig:muones_tanques_excluidos`). Excluded tanks: ≤ 1 muon in 95 % (early) / 93 % (late),
  mean 0.35 / 0.46; retained: mean 1.49 / 1.69. Late excluded tanks have more muons but half
  the EM (14 vs 28) of early excluded ones. Data: `adst_counts_fast.csv` (only 30–40° exists).
- New subsection `subsec:lavado_nucleo` (Eq. `eq:lavado_nucleo`, table `tab:lavado_nucleo`):
  REC wash-out comes from r_REC, matches −βb/r.
- Fast-MC subsection disabled with `\iffalse`, text intact; suggested sentence for Ch. 8 in a comment.
- CAPS notes replaced by: performance comparison (three contributions) and
  `sec:infill_masa` (p/He/Fe in MC and REC geometry, two energy sub-bands, incidence azimuth stated).

## Open items for the author

- Mass/energy numbers come from a different estimator (event bootstrap, θ_REC in REC) than
  `plots_seccion_6.py` (SEM, θ_MC). If kept, they should be redone as a cell in the author's script.
- Check the definition of the "REC geometry" (r_core uses MC angles in v8-2; θ bands in θ_MC).
- Values for the new 40–50° REC bullet are approximate; confirm with the Annex REC 40–50 grid.
- `DRAFTS/03` line 8 still promises the selection discussion inside Ch. 3; `anexo:linealizacion`
  is undefined; `esquema_lluvia.jpeg` does not exist (only `.png`).
