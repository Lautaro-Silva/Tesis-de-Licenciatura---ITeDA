# CLAUDE.md — Tesis de Licenciatura: Asimetrías Azimutales del UMD (Auger)

Context file for Claude sessions working in this repo. Read this fully before doing anything else.

## 1. Project identity

**Title:** "Asimetrías Azimutales de la Densidad de Muones en Lluvias Atmosféricas Extensas con el Detector Subterráneo de Muones del Observatorio Pierre Auger" (Licenciatura en Ciencias Físicas, FCEN-UBA — a Licenciatura from UBA is the Argentine equivalent of a Master's degree, not a Bachelor's).

- **Author:** Lautaro Silva Pizzi (lautarosilvapizzi@gmail.com)
- **Director:** Dr. Juan Manuel Figueira (CONICET/UNSAM) · **Co-director:** Dr. Federico Sánchez (CONICET/UNSAM)
- **Institution:** ITeDA (CNEA-CONICET-UNSAM), Centro Atómico Constituyentes
- **Status: finished and submitted.** Cover date Octubre 2026; FCEN cover sheet lists start Agosto 2025, end Octubre 2026, exam date 16 de Octubre 2026. The final compiled PDF is committed as `Tesis - Latex/main.pdf` (commit `779f5f2`). Treat the thesis text as frozen: any further edit to it should be an explicitly requested correction (e.g. from the jury), not unprompted polishing.

**Physics question:** Surface-detector (SD) studies of Pierre Auger have long shown the lateral distribution function of *total* signal is azimuthally asymmetric for inclined showers (an "early-late" effect from atmospheric attenuation + shower-front geometry), and this asymmetry correlates with X_max (mass-sensitive). This has never been checked with a *pure muon* signal. This thesis is the first application of muon-map/asymmetry analysis to UMD (AMIGA) data — muons measured in isolation, shielded underground (~2.3 m soil, ~1 GeV threshold), free of EM contamination. Central observable: the first-harmonic amplitude **A1** in `ρ(φ) = ρ₀(1 + A1·cos φ)`, fit per radial/zenith bin.

**Objectives (from `Plan_de_trabajo_tesis_de_licenciatura_02.pdf`):** build muon maps in the shower plane from UMD data; determine if azimuthal asymmetry survives in muon-only density; characterize it (dependence on r, zenith angle θ, energy, primary mass); investigate its physical origin (attenuation vs. geometry); evaluate A1 as a mass-composition discriminator; validate with CORSIKA MC (proton/iron) before applying to real AMIGA data; compare against QGSJET-II-04/EPOS-LHC/SIBYLL predictions.

## 2. How to work in this repo — role

Act as a **physics collaborator and referee**, not just an executor. When reviewing analysis code, plots, or thesis text, hold it to the standard of a referee for *Astroparticle Physics* or *EPJC*: question statistical treatment (error bars, bootstrap validity, fit quality, look-elsewhere effects), demand systematics be stated or at least flagged, check consistency with the cited literature (see §9), and push back on hand-wavy physics claims or unjustified conclusions — including ones already written in the thesis. Don't just implement what's asked; say when a result looks fragile, a fit is under-constrained, or a claim outruns the evidence. That said, still do the concrete engineering work (Python, LaTeX, plots) competently and efficiently when asked — the reviewer mindset is additive, not a reason to withhold help.

## 3. Server safety — read before running anything

This session runs on the **institute's shared server**, not a disposable sandbox. Be conservative:

- **No destructive operations without asking first:** `rm -rf`, `git reset --hard`, `git clean`, force-push, overwriting data files — confirm before any of these, even inside this repo.
- **Never touch paths outside this repo** — in particular, do not modify anything under the Auger Offline installation (referenced e.g. in `SDenseStationList.xml`'s schema path) or any other user's home/workspace directory that may appear in configs or scripts.
- **Be mindful of shared compute.** The ADST→parquet pipelines use `multiprocessing.Pool` across many workers, and CORSIKA/Offline runs can be long and I/O-heavy. Don't launch large parallel jobs or long-running batch processing without flagging the expected cost and asking first — other people share this machine's CPU/disk.
- **Treat internal collaboration server paths/usernames as sensitive.** `Scripts/Procesamiento_Datos_Campo/ADST2ASCII/run.sh` and `ADSTReader.cc` hardcode an internal Auger data-server path containing a collaborator's username. Don't paste it verbatim into chat, commits, or any shared output — refer to it generically ("the internal collaboration data server path in `run.sh`").
- **Always work on a separate branch (e.g. `claude/<short-description>`), never on local `main`.** This applies from the start of any task that will touch tracked files — don't make edits on `main` and only branch off at push time. If a change ends up committed on local `main` before this is realized, move it: branch off the current `main` tip, push that branch, then reset local `main` back to match `origin/main`.
- **Get changes ready — edits made, staged if useful, described to the user — and then wait for the user's explicit command before running `git add`, `commit`, or `push`.** The user reviews all of Claude's output — code, analysis, comments, thesis text — before it enters version control, precisely so nothing wrong or half-baked gets committed. Don't run those commands on an implicit "sounds good" or as part of finishing a task unprompted; wait for an explicit go-ahead.
- **Never push to `main`, ever — always push the branch.** Once the user gives the go-ahead, push the branch from the first bullet so they can review the diff and merge it themselves via a pull request on GitHub.

## 4. Repository map

| Path | Contents |
|---|---|
| `Plan_de_trabajo_tesis_de_licenciatura_02.pdf` | Official work plan: objectives, methodology, ~1-year timeline, feasibility. The authoritative task list — see §1. |
| `Bibliografia/` | 34 cited PDFs (papers, GAP notes, textbooks). See §9. |
| `Bibliografia/Papers sin citar/` | 3 uncited PDFs: García Pinto PhD thesis (GAP-2010-054), GAP-2020-066, Grieder EAS textbook. |
| `Notas  - Latex/` (note: double space in the folder name) | Informal working notes, separate from the thesis. `main.tex` includes `Notas Iniciales.tex` (Q&A-style reading notes on foundational papers) and `Trabajo.tex` (a dated lab notebook, Oct 2025–Feb 2026, chronicling pipeline development, bugs found/fixed — see §7). Has its own `Referencias.bib`, distinct from the thesis bibliography. |
| `Tesis - Latex/` | The thesis LaTeX source and the final compiled `main.pdf`. See §5. |
| `GAP_Notes_Latex/` | LaTeX sources for an Auger GAP note derived from the thesis (`GAP2026_041/` current, `[Version_Vieja]GAP_41/` older, `[UNFINISHED]GAP_Core_REC/` an unfinished second note). |
| `Scripts/` | All analysis/processing code. See §7–8. |
| `claude_work/` | Output of earlier Claude/Codex sessions: reviews (`REVIEW_ASTRA/`, `revision_asimetrias_sd_umd/`, `revision_codex_2026_10_07/`, `gap_notes_asimetrias_review_v4/`, `unified_asymmetry_model_v1/`, `kinematic_divergence_explainer_and_thesis_updates/`), the Ch. 7 field-data audit (`auditoria_datos_campo_cap7/`), the SD-station-preserving reprocessing (`reprocesamiento_sd_completo/`), a talk (`presentacion_rafa_2026/`), and a backup of a longer, unused Ch. 7 draft (`respaldo_pull_2026_10_07/`). Supporting material, not thesis source. Some of it contains claims that were later retracted or superseded — check against the final thesis text before reusing anything. |
| `AGENTS.md` | Tells Codex sessions to follow this file. |
| `README.md` | Short public README. Outdated (cites SIBYLL 2.1 / QGSJET-II-04 and the old objectives wording). |
| `SDenseStationList.xml` | Auger Offline config defining 12 virtual "Dense Ring" muon stations at r=450m, spaced 30° apart in shower-plane azimuth — the synthetic detector geometry behind Ch. 5. |
| `Comandos.odt`, `Notas.odt` | Binary LibreOffice docs (not readable by the Read tool). Likely a command cheatsheet and an early/parallel notes doc. Ask the user directly if their content is ever needed. |
| `venv/` | Python 3.12.3 virtualenv. See §10. |

## 5. Thesis status (`Tesis - Latex/`)

**The thesis is complete** (see §1). Main file: `Tesis - Latex/main.tex`, bibliography via biblatex/biber (`bibliografia.bib`, 41 entries). Figures live in `Tesis - Latex/capitulos/imagenes_capitulos/<capN|anexo>/`; logos in `Tesis - Latex/imagenes/`.

`main.tex` `\input`s, in this order: `01_introduccion`, `02_observatorio`, `03_fenomenologia`, `04_metodologia`, `05_anillo_denso`, `06_infill`, `08_conclusiones`, and then `09_anexos` inside an `appendices` environment (renamed "Anexo"). **File numbers no longer match compiled chapter numbers:** there is no `07_*.tex` file (the planned real-data chapter was folded into Ch. 6), so `08_conclusiones.tex` compiles as Chapter 7. The appendices are chapters inside `09_anexos.tex`. There is no separate `anexos/` folder anymore.

| Compiled | File | Content |
|---|---|---|
| Ch. 1 | `01_introduccion.tex` | UHECR spectrum/composition, EAS and X_max, motivation and objectives. |
| Ch. 2 | `02_observatorio.tex` | Auger SD/FD, AugerPrime, AMIGA/UMD. |
| Ch. 3 | `03_fenomenologia.tex` | Shower plane and symmetry breaking. Four mechanisms: atmospheric attenuation, detector response, kinematic divergence of muon emission, geomagnetic field. First-harmonic parametrization. Analytic toy model for the sign of A1, with the crossover momentum p* ≃ 2QD/r above which divergence favors the late region. |
| Ch. 4 | `04_metodologia.tex` | CORSIKA+Offline chain, official production ("icrc2025-test7": SIBYLL 2.3e, QGSJET-III.01, EPOS-LHC-R), Dense Ring, shower-plane geometry, reconstruction performance (energy bias, angular resolution). |
| Ch. 5 | `05_anillo_denso.tex` | Dense Ring A1. MC-vs-REC systematics (directional bias, empirical bootstrap toy model, reconstructed-core shift). Robustness (φ_sh invariance, hadronic models). Energy dependence. p-vs-Fe separation (max ~2.5σ of the combined fit uncertainty at θ=40–55°). X_max interpretation and contrast with the SD. The thesis's strongest result. |
| Ch. 6 | `06_infill.tex` | Infill with MC geometry (UMD vs SD total, signal breakdown, SD sign inversion and station selection). Infill with REC geometry (degradation from the core shift, EM resilience, SD inversion under REC). UMD MC-vs-REC performance. Kinematic production+transport model left as future work (§6 below). **Final section "Datos de campo: trabajo en curso" (`\label{sec:datos_reales}`)** holds the real-data analysis: v4r2 Phase I + Phase II SPMT, 6T5, lgE ≥ 17.5. First observation of the modulation in field data, A1 = 0.063 ± 0.017 (Phase II, 18.0–18.5, 40–60°, 750–1050 m). A1(r) data vs MC (p/He/Fe). Systematics and quantitative comparison stated as pending. |
| Ch. 7 | `08_conclusiones.tex` | Conclusions (full prose). |
| Anexo A | `09_anexos.tex` | First-order expansion of the toy model. |
| Anexo B | `09_anexos.tex` | Dense Ring harmonic fits. |
| Anexo C | `09_anexos.tex` | Infill fit grids (MC and REC geometry, θ bins 0–65°). |

The front matter is complete: FCEN cover sheet, Resumen in prose, and Agradecimientos.

**Known scope limits stated in the thesis itself** (useful if writing a paper/GAP note from it): no composition estimate is made from data; the field-data result is preliminary (no systematics study, MC only up to 10^18 eV while the headline data bin is 18.0–18.5).

## 6. Known dead end — do not blindly re-attempt

`Scripts/Intento Toy Model para Inversion Fallido/` (`mc_model_muonic_divergence_v1.ipynb`, `v2.ipynb`) was a phenomenological Fast-MC muon propagator meant to explain, from first-principles kinematics, the SD-signal azimuthal asymmetry "inversion" at large core distance described in `06_infill.tex`. It generated muons analytically (gamma-distributed production height, power-law energy, transverse momentum) with geometric + relativistic-decay weighting, rather than tracking real per-particle production kinematics from CORSIKA. It did not reproduce the discrepancy convincingly. Git commit `6d6b97b` ("update de que no voy a poder hacer el modelo MC para explicar la discrepancia") records the author concluding this approach is out of scope for the thesis. The final `06_infill.tex` frames it as deferred future work in the subsection "Perspectiva: un modelo cinemático de producción y transporte": extract F(X,E,p_t) from dedicated CORSIKA runs, propagate with Cazón's transport model, project onto the detectors, and apply responses/thresholds/station selection. The analytic toy model in Ch. 3 is a different, qualitative tool that *is* in the thesis. **If asked to revisit this, first read that subsection of `06_infill.tex` and the two notebooks — the core limitation was data availability (ADST gives only the ground footprint, not per-muon production kinematics), not a fixable bug.**

Note this is distinct from the *dense-ring* bootstrap toy model in `validacion_rec_muones.py`, which **did** work and is written up successfully in Ch. 5.

## 7. Framework bug history — one real, one ruled out

Documented in `Notas  - Latex/Trabajo.tex`:

1. **Dense Ring φ double-subtraction** (~Nov 2025, real bug, fixed): the reader was subtracting the shower azimuth twice for Dense Ring stations, since `GetAzimuthSP()` already returns the shower-plane-relative angle for those synthetic stations. Washed the asymmetry out to noise. Fixed in pipeline v7.
2. **Infill `GetAzimuthSP()` — investigated, then ruled out, not a live issue** (~Jan–Feb 2026): at the time, `GetAzimuthSP()` was suspected of returning ground-plane angles instead of true shower-plane angles for real Infill stations, and a manual 3D Euler-rotation workaround (`readADST_surface_v11`/`v12`) was built around that suspicion. This line of investigation was subsequently tested and found to be **not actually a problem** — `GetAzimuthSP()` behaves correctly, and this deprecated concern only survives in `Trabajo.tex` because that work path was abandoned early, before the retest. **Do not treat this as a confirmed Offline bug or reintroduce the Euler-rotation workaround on the assumption it's still needed** — verify current behavior directly if azimuth-convention issues resurface, rather than trusting the old notes entry.

## 8. Code/data pipeline (`Scripts/`)

**Data flow:** ADST (Auger Offline ROOT format) → PyROOT reader (parallelized via `multiprocessing.Pool`) → parquet → pandas/numpy analysis → harmonic fit (`scipy.optimize.curve_fit`) for A1 → matplotlib figures / auto-generated PDF reports (fpdf2 + pdfplumber).

**Active notebooks are paired `.py` + `.ipynb` (jupytext, percent format). Both are tracked
in git. Claude edits only the `.py` — never write to the `.ipynb` directly.** See
`Scripts/README_notebooks.md` for the full workflow. The `.ipynb` outputs (base64 figures)
made these files heavy and unpleasant to edit as raw text, which is why the `.py` — plain
Python with `# %%` cell markers — is what Claude reads and edits. But the user's own
workflow is interactive: they open and run the `.ipynb` in JupyterLab, and its outputs
(figures, tables) are real thesis artifacts they don't want silently deleted by a git
operation in some other checkout. **Do not `git rm --cached` these `.ipynb` files or add
them to `.gitignore`** — that was tried once (2026-09-02) and it deleted the user's local
figures the moment they pulled the change into their own checkout, because `git rm --cached`
only spares the working tree in the repo where it's run; every other checkout that pulls the
resulting commit has the file removed from disk too, regardless of `.gitignore`. Keeping
both tracked means the `.ipynb` half of a commit diff is large/unreadable when outputs
change — that's an accepted tradeoff, not a bug to fix by untracking it again.

**Active / current** (build on these):
- `Scripts/Procesamiento_ADST_v8-2.py`, `Scripts/Procesamiento_ADST_Campo_v9.py` — main MC ADST→parquet pipelines.
- `Scripts/Procesamiento_Datos_Campo/` — the **real-data pipeline**: `ADST2ASCII/` (compiled Auger Offline C++ user module reading raw production ADST from the collaboration's data server, cuts configured in `Config.xml.in`), `readADST_data_v19.py` (Python/pandas port of the same cuts: `readADST_surface_data_v19(fname, only_6T5=True, min_logE=17.0, max_theta_deg=60.0, ...)`), plus notebooks for orchestration (`Procesamiento_Datos_Campo_v1.py`) and exploratory analysis (`Analisis_Preliminar_DatosCampo_Phase1/Phase2.py`). `Analisis_Asimetria_DatosCampo_Cap7.py` (only the `.py` is tracked) produces the field-data numbers, tables and figures, written to `resultados_cap7/`. Its header still says it feeds `07_datos_reales.tex`, but that chapter no longer exists. What made it into the thesis is the final section of Ch. 6 (§5). It reads existing parquet only and runs in the plain `venv/`.
- `Scripts/Cap3_modelos_juguete.py` (Ch. 3 analytic toy model → `resultados_cap3_modelos_juguete/`), `Scripts/Cap5_corrimiento_nucleo.py` (Ch. 5 reconstructed-core-shift study → `resultados_cap5_corrimiento_nucleo/`).
- `Scripts/analisis_infill_sims.py`, `Scripts/validacion_asimetria_infill_sd_mu_v2.py`, `Scripts/validacion_rec_muones.py` (best-documented notebook, has the working dense-ring toy model), `Scripts/plots_seccion_6.py` (largest — generates the Ch. 6 figures).
- `Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py` — curated highlight-reel figures for an Auger "Foundations" collaboration-meeting talk.
- `Scripts/Pruebas Infill/` — debugging notebooks (still `.ipynb`, not converted) for the φ-convention investigation (§7.2 above); useful if similar geometry bugs resurface.

**Deprecated / historical** (provenance only, do not build on): `Scripts/Codigo Viejo V1/`, `Codigo Viejo V2/`, `Scripts/Cosas Random Mayo 2026/`, `Scripts/Test Iniciales/`, `Scripts/Reportes Viejos/`. `Scripts/Reportes Feb 2026/` holds the current valid PDF reports.

**Unrelated:** `Scripts/calculador_puntaje_conicet.ipynb` is a personal CONICET scholarship-score calculator, not physics — ignore for thesis work.

## 9. Domain conventions

- **A1**: amplitude of the first-harmonic azimuthal fit `ρ(φ) = ρ₀(1 + A1·cos φ)` — the thesis's central observable.
- **θ** = zenith angle, **φ** = azimuth (shower-plane, wrapped to [-180°, 180°]).
- **MC vs REC** suffixes = Monte Carlo truth vs Offline-reconstructed (e.g. `A1_UMD_MC` vs `A1_UMD_REC`).
- **Dense Ring** (synthetic, fixed shower-plane azimuth, `SDenseStationList.xml`) vs **Infill** (real array, needs geometric projection, φ bug history in §7).
- **Module IDs**: simulation 0–5, real data 100–115. **Counter IDs**: simulation = stationId + 100000 (the standard `counterId ≥ 100000` filter for Infill/simulated UMD).
- **Hadronic models**: SIBYLL 2.3e, QGSJET-III.01, EPOS-LHC-R (current MC production "icrc2025-test7"). **Note:** the work-plan PDF references SIBYLL 2.1 / QGSJET-II-04 — outdated relative to what's actually used; worth flagging/reconciling if writing methodology text.
- **Primaries**: proton, helium, oxygen, iron. **Real-data cuts**: 6T5 fiducial trigger, logE ≥ 17.0, θ ≤ 60°, station-rejection flags (`is_sd_rejected`, `is_counter_rejected`). The defaults in `readADST_data_v19` are those. The thesis's field-data section uses lgE ≥ 17.5 and excludes the Phase II commissioning period in 2022.

## 10. Environment

- Python venv at `venv/` (Python 3.12.3). Has: numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, pyarrow, fpdf2, pdfplumber, jupyter/jupyterlab, ipython, jupytext. **Does NOT have PyROOT or uproot.**
- ADST/ROOT reading requires the separate **Auger Offline environment**, sourced outside this venv (`AUGEROFFLINEROOT` env var, `source .../this-auger-offline.sh`, `aug_set_version offline 4.0.1-icrc23-prod1-root6`, manual `ROOT.gSystem.Load(".../libRecEventKG.so")`). Don't assume `venv/bin/python` alone can open ADST files — check which environment/kernel a notebook actually needs before running it.
- Local dataset paths hardcoded in some notebooks (e.g. `/home/lsilva/Github/ADST_Alexey_module_v9/`, `parquet_sib_proton_17/`) are this machine's own paths, not portable — expected to need re-pointing if run elsewhere, not a bug.

## 11. Bibliography quick reference (`Bibliografia/`)

**Core asymmetry lineage (GAP notes + theses)** — read in this order for background: GAP-1998-034 (Pryke, foundational early-late effect) → GAP-2000-017 (Bertou & Billoir, origin of ground-density asymmetry) → GAP-2002-073 / GAP-2002-074 (Billoir & Da Silva, LDF asymmetry parametrization / checking origin) → GAP-2007-054 (Dembinski, Hebbeker, Leuthold — MC muon maps vs near-horizontal showers; **filename on disk is `GAP2007_124.pdf`, a mislabel — content confirmed as GAP-2007-054**) → García Pinto 2009 PhD thesis (`Bibliografia/Papers sin citar/`, matches GAP-2010-054, not cited in the final thesis) → Bradfield 2022 PhD thesis / GAP-2022-023 (closest prior work: SD-based asymmetry + composition with AugerPrime).

**Hadronic interaction models:** Pierog 2015 (EPOS-LHC), Ostapchenko 2011 (QGSJET-II) and 2024 (QGSJET-III), Riehn 2020 (SIBYLL 2.3d) — see §9 for the version-consistency caveat vs. what's actually simulated.

**UMD/AMIGA & muon content:** `UMD_Design2016.pdf` (JINST, prototype design), `auger2020umd_infill.pdf` (first direct UMD muon measurement), Botti PhD thesis (KIT/UNSAM — detailed AMIGA composition-analysis methodology template, valuable to mirror).

**Mass composition / muon puzzle:** `augerComposition2017.pdf`, `yushkov2019mass.pdf`, `auger2016muon_deficit.pdf` (the "muon deficit" PRL).

**Simulation/software tools:** `heck1998corsika.pdf` (CORSIKA), `argiro2007offline.pdf` (Offline framework), `efron1979bootstrap.pdf` (bootstrap statistics — the only stats-methodology reference present; thin coverage if more rigorous error propagation is needed).

**Also cited in the final bibliography:** `Luce_ICRC2021` (geomagnetic effect, figure in Ch. 3), `Cazon2012` (muon transport model, Ch. 6 outlook), `botti2019`. The `.bib` is the authoritative list. Not every entry has a PDF in `Bibliografia/`.

**Coverage gaps a referee would still flag:** no modern statistics/fitting reference beyond Efron 1979; the García Pinto thesis and Grieder textbook remain uncited.

## 12. Quick file-path reference

- Thesis entry point: `Tesis - Latex/main.tex`; final PDF: `Tesis - Latex/main.pdf`; chapters: `Tesis - Latex/capitulos/0{1..6,8,9}_*.tex` (no `07`); bibliography: `Tesis - Latex/bibliografia.bib`.
- Work plan: `Plan_de_trabajo_tesis_de_licenciatura_02.pdf`.
- Informal lab notebook: `Notas  - Latex/Trabajo.tex`.
- Real-data pipeline: `Scripts/Procesamiento_Datos_Campo/readADST_data_v19.py`, `Scripts/Procesamiento_Datos_Campo/ADST2ASCII/`; field-data analysis: `Scripts/Procesamiento_Datos_Campo/Analisis_Asimetria_DatosCampo_Cap7.py`.
- Ch. 6 figures: `Scripts/plots_seccion_6.py`.
- GAP note: `GAP_Notes_Latex/GAP2026_041/main.tex`.
- Dense-ring geometry config: `SDenseStationList.xml`.
