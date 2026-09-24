# Reprocessing ADST without losing SD stations (v17 completo)

Your `Procesamiento_ADST_v8-2` pipeline, changed only as much as needed so that the
parquet files also contain the SD stations that were **not** reconstructed. With it,
the SD-muon "before/after `HasStation`" vs UMD comparison (Astra's
`03_sd_vs_umd/comparar_sd_umd`) can be produced **entirely from your own pipeline**.

Branch: `claude/reprocesamiento-sd-completo`. Nothing outside this folder was modified.

## Files

| File | What it is |
|---|---|
| `lector_adst_v17_completo.py` | The reader: your v17, every change marked `# CHANGE N`. Produces two tables per ROOT file. |
| `Procesamiento_ADST_v17_completo.ipynb` / `.py` | Runner notebook, laid out like v8-2 (one cell per production) + a validation cell. |
| `comparar_sd_umd_reprocesado.ipynb` / `.py` | SD muons before/after the requirement vs UMD, with the paired bootstrap. Input switch `FUENTE` (`reprocesado_v13` by default; `insumos_astra` re-runs the same code on Astra's inputs as a cross-check). |
| `desglose_sd_mc_vs_rec.ipynb` / `.py` | The last figure of `plots_seccion_6` (UMD + SD EM + SD muons + SD total VEM, twin axes), with each SD MC curve drawn **both** with and without the reconstruction requirement. |
| `validaciones.py` | Pandas-only checks used by the notebook and the pilot (PASS/FAIL with numbers). |
| `CAMBIOS.md` | **Read first.** Every change vs v8-2 with its reason; why each Astra attempt failed; the Offline library finding. |
| `piloto/correr_piloto.py` | Runs the reader on one file in one process (outputs in `piloto/<label>/`, git-ignored). |
| `resultados/` | Outputs of the comparison notebook (one set per `FUENTE`). |

## Output of the reprocessing

For each production, under `/home/lsilva/Github/ADST_Alexey_module_v13/<production>/`:

| Folder | One row per | Notes |
|---|---|---|
| `modulos/` | UMD module | Your v17 columns + `has_sd_rec`. `df[df.has_sd_rec]` == your old v11 parquet. |
| `estaciones_sd/` | simulated SD station per event | New. Reconstructed or not. MC `sd_nMuons_MC`, `sd_nEM_MC`, `has_sd_rec`, true-plane `r_core_MC`, `phi_plane_euler_MC_true_core` (same definitions as `modulos`). No cuts. |
| `resumen/` | ROOT file | Events, rows, skipped counters by reason. |

Your v10/v11 parquets are not touched. Pilots go to `ADST_Alexey_module_v13_piloto/`.

## How to run (in order)

1. **Terminal, before JupyterLab**, load the Offline version matching the production:
   ```bash
   source /srv/software/amd64/ubuntu/24.04/auger/offline/icrc2025-test7-root6/bin/this-auger-offline.sh
   ```
   (Why test7 and not your usual 4.0.1-icrc23: `CAMBIOS.md` §5. Analysis columns are identical with both.)
2. Open `Procesamiento_ADST_v17_completo.ipynb`, run cells 1–3.
3. With `PILOTO = True`, run the **Sibyl-Proton** cell (1 file, 50 events, a few seconds), then the
   validation cell. Expect `RESULTADO GLOBAL: PASS`.
4. Set `PILOTO = False`, re-run cell 2 and the **Sibyl-Proton** cell. 8 workers; ~30–50 min for 20 files
   (test7 reads slower than 4.0.1, see below). Then the validation cell again.
5. Other productions: same, one cell each, whenever you want.
6. Open `comparar_sd_umd_reprocesado.ipynb` and run all (pandas only, ~2 min). With
   `FUENTE = "reprocesado_v13"` section 6 must print `PASS`: the result from your own pipeline
   equals Astra's.
7. Open `desglose_sd_mc_vs_rec.ipynb` and run all (~3 min) for the signal-breakdown figure.

Do not "Run All" the processing notebook: each production cell is a batch job on the shared server.

## Validation status (done before handing over)

All run on 2026-09-17 on this server, single process. Reproduce with
`piloto/correr_piloto.py` + `piloto/validar_piloto.py`.

**A. Both Offline libraries, Run010, first 50 events** (`piloto/test7_50ev`, `piloto/icrc23_50ev`)

| | 4.0.1-icrc23-prod1-root6 | icrc2025-test7-root6 |
|---|---|---|
| Module rows with SD REC vs v11 | 3306 = 3306, 0 lost | 3306 = 3306, 0 lost |
| Analysis columns vs v11 | identical | identical |
| Other columns vs v11 | none differ | only `sdMuonSignal_REC` (real values instead of 0) |
| Time | 13.5 s | 25.5 s |

**B. Whole Run010 with icrc2025-test7-root6** (`piloto/test7_run010_completo`, 1198 events, 549 s)

| Check | Result |
|---|---|
| Module rows with SD REC vs your v11 parquet | 78,960 = 78,960; **0 lost, 0 extra** |
| `theta_MC`, `r_core_MC`, `phi_plane_euler_MC_true_core`, `nMuones_MC`, `sd_nMuons_MC`, `sd_nEM_MC` | identical in every row |
| Module rows added by the flag (no SD REC) | 81 |
| SD station table vs Astra's `adst_counts_fast.csv` (her cuts) | 5,296 = 5,296 stations; muon counts and `has_sd_rec` identical; r within 4.6e-13 m, φ within 1.8e-15 rad |
| Reconstructed stations: module table vs station table | 12,183 / 12,183 present, counts and geometry identical |
| Skipped counters (v17 rules) | 0 |
| Metadata columns | present in both tables |
| Notebook validation cell, run verbatim on this output | `RESULTADO GLOBAL: PASS` |

**C. Analysis notebook** (`comparar_sd_umd_reprocesado`, `FUENTE="insumos_astra"`)

| Check | Result |
|---|---|
| Closed-form fit vs `curve_fit`, 24 band×sample combinations | max difference 4.5e-10 |
| All 17 columns of Astra's `comparacion_directa.csv` | reproduced to ≤ 1e-16 (float rounding) |

**D. The full 20-file run (done, 2026-09-17, by the author, 8 workers)**

Every file read cleanly; no counter skipped anywhere. The per-file module counts with
`has_sd_rec` reproduce the March run file by file (79710, 79305, 78960, 79020, 79953, …).
Totals in the analysis band (30 ≤ θ < 40°): 156,633 UMD modules and 1,045,964 SD station
occurrences, of which 52,211 have a reconstructed station and **993,753 do not** — the
population the old pipeline could not see.

Running `comparar_sd_umd_reprocesado` with `FUENTE="reprocesado_v13"`, i.e. entirely from
this pipeline, reproduces Astra's `comparacion_directa.csv` in **all 17 columns to 1e-16**.
The 270 UMD module rows recovered by the flag change the UMD curve by 0.00000 in every band,
confirming they are irrelevant for that curve (they are not what the rewrite was for).

Signal breakdown (`desglose_sd_mc_vs_rec`), A1 in the outermost band 1200–1350 m:

| Curve | with SD REC | MC only (whole array) |
|---|---:|---:|
| SD muonic | **−0.124** | **+0.069** |
| SD electromagnetic | +0.448 | +0.518 |

The muon inversion at large r is present only when a reconstructed SD station is required.
Same showers, same MC counts, same geometry.

**Runtime note:** with test7 one file took 549 s in a single process. Your March run
(4.0.1 library, 8 workers) took ~600 s per file. Expect roughly 30–50 min for the 20 files with
8 workers; the extra SD-station loop adds little.

## What this does *not* change

- Physics: no new cuts, no changed rotations or conventions, no changed counters.
- The UMD curve: it stays the selected one. Offline does not write UMD truth for SD stations
  that did not trigger, so an unselected UMD curve cannot be built from these ADSTs
  (`CAMBIOS.md` §2).
- Nothing is committed or pushed until you say so.
