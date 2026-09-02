# CLAUDE.md — Tesis de Licenciatura: Asimetrías Azimutales del UMD (Auger)

Context file for Claude sessions working in this repo. Read this fully before doing anything else.

## 1. Project identity

**Title:** "Asimetrías Azimutales de la Densidad de Muones en Lluvias Atmosféricas Extensas con el Detector Subterráneo de Muones del Observatorio Pierre Auger" (Licenciatura en Ciencias Físicas, FCEN-UBA — a Licenciatura from UBA is the Argentine equivalent of a Master's degree, not a Bachelor's).

- **Author:** Lautaro Silva Pizzi (lautarosilvapizzi@gmail.com)
- **Director:** Dr. Juan Manuel Figueira (CONICET/UNSAM) · **Co-director:** Dr. Federico Sánchez (CONICET/UNSAM)
- **Institution:** ITeDA (CNEA-CONICET-UNSAM), Centro Atómico Constituyentes
- **Cover date in the LaTeX source:** Agosto 2026 — the thesis is at/near its intended submission time now.

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
| `Bibliografia/Papers sin citar/` | 2 uncited-but-relevant PDFs (García Pinto PhD thesis, Grieder EAS textbook) — arguably should be promoted to cited. |
| `Notas  - Latex/` (note: double space in the folder name) | Informal working notes, separate from the thesis. `main.tex` includes `Notas Iniciales.tex` (Q&A-style reading notes on foundational papers) and `Trabajo.tex` (a dated lab notebook, Oct 2025–Feb 2026, chronicling pipeline development, bugs found/fixed — see §6). Has its own `Referencias.bib`, distinct from the thesis bibliography. |
| `Tesis - Latex/` | The actual thesis LaTeX source. See §5. |
| `Scripts/` | All analysis/processing code. See §7–8. |
| `SDenseStationList.xml` | Auger Offline config defining 12 virtual "Dense Ring" muon stations at r=450m, spaced 30° apart in shower-plane azimuth — the synthetic detector geometry behind Ch. 5. |
| `Comandos.odt`, `Notas.odt` | Binary LibreOffice docs (not readable by the Read tool). Likely a command cheatsheet and an early/parallel notes doc. Ask the user directly if their content is ever needed. |
| `venv/` | Python 3.12.3 virtualenv. See §10. |

## 5. Thesis status (`Tesis - Latex/`)

Main file: `Tesis - Latex/main.tex` → `\input`s `capitulos/01..09_*.tex` in order, bibliography via biblatex/biber (`bibliografia.bib`).

| # | File | Status |
|---|---|---|
| 1 | `01_introduccion.tex` | Done — UHECR flux/spectrum, EAS/X_max phenomenology, Heitler-Matthews model, objectives. |
| 2 | `02_observatorio.tex` | Done — Auger Observatory, AugerPrime, AMIGA/UMD design. |
| 3 | `03_fenomenologia.tex` | Done (recently revised) — the three asymmetry mechanisms (attenuation, geometric/divergence, geomagnetic), harmonic parametrization. |
| 4 | `04_metodologia.tex` | Done — CORSIKA+Offline chain, MC production ("icrc2025-test7": SIBYLL 2.3e, QGSJET-III.01, EPOS-LHC-R), Dense Ring config, reconstruction bias figures. |
| 5 | `05_anillo_denso.tex` | Done — most mature chapter. Dense Ring A1 results, SD-vs-UMD comparison, bootstrap toy model (successful, unlike §6's toy model), mass discrimination via Merit Factor (~2.5 sweet spot at θ=40–55°). The thesis's strongest positive result. |
| 6 | `06_infill.tex` | **Partially done.** First ~60% is finished prose (MC-geometry A1 results, the SD "asymmetry inversion" explained via a soft/divergent low-energy muon population, REC-geometry results). The back half (mass/energy dependence for Infill, MC-vs-REC performance comparison) is raw outline notes in Spanish caps, not prose — genuinely unfinished. Contains the abandoned Fast-MC dead end, see §6 below. |
| 7 | `07_datos_reales.tex` | **Not started.** Only section headers (real-data selection, asymmetry extraction, comparison vs MC). This is the final validation step of the whole thesis. |
| 8 | `08_conclusiones.tex` | **Not started.** Only section headers, zero body text. |
| 9 | `09_anexos.tex` | Mostly done — Appendix A (Dense Ring fits) finished, Appendix B (Infill fit galleries, 12 figures) structurally complete. |

**Also unfinished:** the abstract (`Resumen`) is a placeholder ("Aca va el resumen"), acknowledgments are a bare bullet list of names (not prose), and the FCEN cover-sheet fields are blank.

**Orphaned file:** `Tesis - Latex/anexos/A_parametros_corsika.tex` is empty (0 bytes) and not `\input`'d anywhere — dead/superseded stub, actual appendix content lives in `capitulos/09_anexos.tex`.

**Build artifacts:** `main.bbl-SAVE-ERROR` / `main.bcf-SAVE-ERROR` exist in `Tesis - Latex/` — remnants of a failed biber compile at some point; not necessarily current, but worth checking if bibliography rendering ever breaks.

**Likely near-term priorities (for orientation, not a mandate):** finish Ch. 6's back half, write Ch. 7 using the already-mature `Procesamiento_Datos_Campo/` real-data pipeline, write Ch. 8, and fill in the front-matter placeholders.

## 6. Known dead end — do not blindly re-attempt

`Scripts/Intento Toy Model para Inversion Fallido/` (`mc_model_muonic_divergence_v1.ipynb`, `v2.ipynb`) was a phenomenological Fast-MC muon propagator meant to explain, from first-principles kinematics, the SD-signal azimuthal asymmetry "inversion" at large core distance described in `06_infill.tex`. It generated muons analytically (gamma-distributed production height, power-law energy, transverse momentum) with geometric + relativistic-decay weighting, rather than tracking real per-particle production kinematics from CORSIKA. It did not reproduce the discrepancy convincingly. Git commit `6d6b97b` ("update de que no voy a poder hacer el modelo MC para explicar la discrepancia") records the author concluding this approach is out of scope for the thesis; `06_infill.tex` now frames it as deferred future work (4-step roadmap: extract F(X,E,p_t) from dedicated CORSIKA runs → propagate via Cazón's transport model → project geometrically → apply instrumental thresholds). **If asked to revisit this, first read that section of `06_infill.tex` and the two notebooks — the core limitation was data availability (ADST gives only the ground footprint, not per-muon production kinematics), not a fixable bug.**

Note this is distinct from the *dense-ring* bootstrap toy model in `validacion_rec_muones.py`, which **did** work and is written up successfully in Ch. 5.

## 7. Framework bug history — one real, one ruled out

Documented in `Notas  - Latex/Trabajo.tex`:

1. **Dense Ring φ double-subtraction** (~Nov 2025, real bug, fixed): the reader was subtracting the shower azimuth twice for Dense Ring stations, since `GetAzimuthSP()` already returns the shower-plane-relative angle for those synthetic stations. Washed the asymmetry out to noise. Fixed in pipeline v7.
2. **Infill `GetAzimuthSP()` — investigated, then ruled out, not a live issue** (~Jan–Feb 2026): at the time, `GetAzimuthSP()` was suspected of returning ground-plane angles instead of true shower-plane angles for real Infill stations, and a manual 3D Euler-rotation workaround (`readADST_surface_v11`/`v12`) was built around that suspicion. This line of investigation was subsequently tested and found to be **not actually a problem** — `GetAzimuthSP()` behaves correctly, and this deprecated concern only survives in `Trabajo.tex` because that work path was abandoned early, before the retest. **Do not treat this as a confirmed Offline bug or reintroduce the Euler-rotation workaround on the assumption it's still needed** — verify current behavior directly if azimuth-convention issues resurface, rather than trusting the old notes entry.

## 8. Code/data pipeline (`Scripts/`)

**Data flow:** ADST (Auger Offline ROOT format) → PyROOT reader (parallelized via `multiprocessing.Pool`) → parquet → pandas/numpy analysis → harmonic fit (`scipy.optimize.curve_fit`) for A1 → matplotlib figures / auto-generated PDF reports (fpdf2 + pdfplumber).

**Active notebooks are `.py` files (jupytext, percent format), not `.ipynb`.** See
`Scripts/README_notebooks.md` for the full rationale and workflow. In short: the `.ipynb`
outputs (base64 figures) made the files too heavy to edit as text and bloated git; the `.py`
is the tracked source of truth, opens as a normal cell-by-cell notebook in JupyterLab/VS Code
(with jupytext installed in `venv/`), and a paired local `.ipynb` (gitignored) holds outputs.
When editing one of these, edit the `.py` — that's what's in git.

**Active / current** (build on these):
- `Scripts/Procesamiento_ADST_v8-2.py`, `Scripts/Procesamiento_ADST_Campo_v9.py` — main MC ADST→parquet pipelines.
- `Scripts/Procesamiento_Datos_Campo/` — the **real-data pipeline**, most actively maintained (updated through Aug 2026): `ADST2ASCII/` (compiled Auger Offline C++ user module reading raw production ADST from the collaboration's data server, cuts configured in `Config.xml.in`), `readADST_data_v19.py` (Python/pandas port of the same cuts: `readADST_surface_data_v19(fname, only_6T5=True, min_logE=17.0, max_theta_deg=60.0, ...)`), plus notebooks for orchestration (`Procesamiento_Datos_Campo_v1.py`) and exploratory analysis (`Analisis_Preliminar_DatosCampo_Phase1/Phase2.py`).
- `Scripts/analisis_infill_sims.py`, `Scripts/validacion_asimetria_infill_sd_mu_v2.py`, `Scripts/validacion_rec_muones.py` (best-documented notebook, has the working dense-ring toy model), `Scripts/plots_seccion_6.py` (largest, most recently modified — generates the Ch. 6 figures).
- `Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py` — curated highlight-reel figures for an Auger "Foundations" collaboration-meeting talk.
- `Scripts/Pruebas Infill/` — debugging notebooks (still `.ipynb`, not converted) for the φ-convention bug (§6.2 above); useful if similar geometry bugs resurface.

**Deprecated / historical** (provenance only, do not build on): `Scripts/Codigo Viejo V1/`, `Codigo Viejo V2/`, `Scripts/Cosas Random Mayo 2026/`, `Scripts/Test Iniciales/`, `Scripts/Reportes Viejos/`. `Scripts/Reportes Feb 2026/` holds the current valid PDF reports.

**Unrelated:** `Scripts/calculador_puntaje_conicet.ipynb` is a personal CONICET scholarship-score calculator, not physics — ignore for thesis work.

## 9. Domain conventions

- **A1**: amplitude of the first-harmonic azimuthal fit `ρ(φ) = ρ₀(1 + A1·cos φ)` — the thesis's central observable.
- **θ** = zenith angle, **φ** = azimuth (shower-plane, wrapped to [-180°, 180°]).
- **MC vs REC** suffixes = Monte Carlo truth vs Offline-reconstructed (e.g. `A1_UMD_MC` vs `A1_UMD_REC`).
- **Dense Ring** (synthetic, fixed shower-plane azimuth, `SDenseStationList.xml`) vs **Infill** (real array, needs geometric projection, φ bug history in §7).
- **Module IDs**: simulation 0–5, real data 100–115. **Counter IDs**: simulation = stationId + 100000 (the standard `counterId ≥ 100000` filter for Infill/simulated UMD).
- **Hadronic models**: SIBYLL 2.3e, QGSJET-III.01, EPOS-LHC-R (current MC production "icrc2025-test7"). **Note:** the work-plan PDF references SIBYLL 2.1 / QGSJET-II-04 — outdated relative to what's actually used; worth flagging/reconciling if writing methodology text.
- **Primaries**: proton, helium, oxygen, iron. **Real-data cuts**: 6T5 fiducial trigger, logE ≥ 17.0, θ ≤ 60°, station-rejection flags (`is_sd_rejected`, `is_counter_rejected`).

## 10. Environment

- Python venv at `venv/` (Python 3.12.3). Has: numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, pyarrow, fpdf2, pdfplumber, jupyter/jupyterlab, ipython, jupytext. **Does NOT have PyROOT or uproot.**
- ADST/ROOT reading requires the separate **Auger Offline environment**, sourced outside this venv (`AUGEROFFLINEROOT` env var, `source .../this-auger-offline.sh`, `aug_set_version offline 4.0.1-icrc23-prod1-root6`, manual `ROOT.gSystem.Load(".../libRecEventKG.so")`). Don't assume `venv/bin/python` alone can open ADST files — check which environment/kernel a notebook actually needs before running it.
- Local dataset paths hardcoded in some notebooks (e.g. `/home/lsilva/Github/ADST_Alexey_module_v9/`, `parquet_sib_proton_17/`) are this machine's own paths, not portable — expected to need re-pointing if run elsewhere, not a bug.

## 11. Bibliography quick reference (`Bibliografia/`)

**Core asymmetry lineage (GAP notes + theses)** — read in this order for background: GAP-1998-034 (Pryke, foundational early-late effect) → GAP-2000-017 (Bertou & Billoir, origin of ground-density asymmetry) → GAP-2002-073 / GAP-2002-074 (Billoir & Da Silva, LDF asymmetry parametrization / checking origin) → GAP-2007-054 (Dembinski, Hebbeker, Leuthold — MC muon maps vs near-horizontal showers; **filename on disk is `GAP2007_124.pdf`, a mislabel — content confirmed as GAP-2007-054**) → García Pinto 2009 PhD thesis (`Bibliografia/Papers sin citar/`, matches GAP-2010-054, arguably should be promoted to cited) → Bradfield 2022 PhD thesis / GAP-2022-023 (closest prior work: SD-based asymmetry + composition with AugerPrime).

**Hadronic interaction models:** Pierog 2015 (EPOS-LHC), Ostapchenko 2011 (QGSJET-II) and 2024 (QGSJET-III), Riehn 2020 (SIBYLL 2.3d) — see §9 for the version-consistency caveat vs. what's actually simulated.

**UMD/AMIGA & muon content:** `UMD_Design2016.pdf` (JINST, prototype design), `auger2020umd_infill.pdf` (first direct UMD muon measurement), Botti PhD thesis (KIT/UNSAM — detailed AMIGA composition-analysis methodology template, valuable to mirror).

**Mass composition / muon puzzle:** `augerComposition2017.pdf`, `yushkov2019mass.pdf`, `auger2016muon_deficit.pdf` (the "muon deficit" PRL).

**Simulation/software tools:** `heck1998corsika.pdf` (CORSIKA), `argiro2007offline.pdf` (Offline framework), `efron1979bootstrap.pdf` (bootstrap statistics — the only stats-methodology reference present; thin coverage if more rigorous error propagation is needed).

**Coverage gaps a referee would flag:** no dedicated reference on geomagnetic-deflection asymmetry (despite it being one of the three mechanisms discussed in Ch. 3); no modern statistics/fitting reference beyond Efron 1979; the uncited García Pinto thesis and Grieder textbook sit unused in "Papers sin citar" despite clear relevance.

## 12. Quick file-path reference

- Thesis entry point: `Tesis - Latex/main.tex`; chapters: `Tesis - Latex/capitulos/0{1..9}_*.tex`; bibliography: `Tesis - Latex/bibliografia.bib`.
- Work plan: `Plan_de_trabajo_tesis_de_licenciatura_02.pdf`.
- Informal lab notebook: `Notas  - Latex/Trabajo.tex`.
- Real-data pipeline: `Scripts/Procesamiento_Datos_Campo/readADST_data_v19.py`, `Scripts/Procesamiento_Datos_Campo/ADST2ASCII/`.
- Most recent analysis notebook: `Scripts/plots_seccion_6.py`.
- Dense-ring geometry config: `SDenseStationList.xml`.
