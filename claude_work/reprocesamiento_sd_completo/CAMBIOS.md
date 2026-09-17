# What changed vs `Procesamiento_ADST_v8-2`, and why Astra's versions failed

This document is the long-form companion to the `# CHANGE N` comments in
`lector_adst_v17_completo.py`. Read it once; after that, the comments are enough.

---

## 1. The problem we are solving

Your thesis figure `SD_Desglose_Componentes_vs_UMD` shows the SD-muon A1 turning
negative at large r. Astra showed (with a separate, one-off extraction) that this
happens because the pipeline only keeps SD stations that have a **reconstructed**
station object: `sEvent.HasStation(sdId)`. At large r most stations are not
reconstructed, and the ones that are tend to be muon-rich on the late side.

To test that claim **with your own pipeline**, the parquet files must also contain
the SD stations that were **not** reconstructed. That is what this rewrite does.

---

## 2. Why "just remove the `HasStation` skip" is not enough

v17 loops over **UMD counters** (`MDEvent.CountersBegin()`) and looks up each
counter's SD partner. If Offline never wrote UMD modules for an SD station, that
station cannot show up in this loop — and Offline does not write UMD
modules/channels for SD stations that did not trigger
(`MdOptoElectronicSimulator.cc`, `MD2ADST.cc`; cited in
`revision_asimetrias_sd_umd/01_fisica/report.md` §2.3).

Measured, not assumed:

| Evidence | Numbers |
|---|---|
| Astra's "flag" run on the 20 SIB proton files (`04_reprocesamiento/AUDITORIA_FILAS.md`) | only **45** module rows with `has_sd_rec=False` came back |
| Stations missing from the old parquet in the 30–40°, 150–1800 m sample | **55,249** |
| This pilot, Run010, 50 events: non-reconstructed SD station occurrences | 10,398 |
| … of which the ADST has a UMD **counter object** for | 4,647 |
| … module rows those counters produced | **6** (the counters exist but have no modules) |
| This pilot, whole Run010: non-reconstructed SD station occurrences / module rows added | 249,220 / **81** |

So the missing stations are only reachable from the list of **simulated** SD
stations, `SDEvent.GetSimStationVector()`. Hence the second table.

---

## 3. Every change, one by one

| # | Where | What | Why |
|---|---|---|---|
| 0 | `cargar_offline()` | Cell-1 library loading moved into a function that returns and prints the library path. | So the notebook, the Pool workers and the pilot script run the same code, and every run records which Offline version read the data (it matters, see §5). |
| 1 | counter loop | `has_sd_rec = bool(sEvent.HasStation(sdId))` is stored as a column instead of `continue`. | Keep the counter. `df[df.has_sd_rec]` gives back exactly the old dataset. |
| 2 | counter loop | Getters of the **reconstructed** station are called only if it exists; otherwise NaN (`pd.NA` for `is_sd_saturated`): `IsLowGainSaturated`, `GetTotalSignal`, `GetTotalSignalError`, `GetMuonSignal`, `GetSPDistanceError`, `GetAzimuthSP`, and the Dense Ring `GetSPDistance`. | You cannot call methods on a station that does not exist. Missing ≠ zero. MC counts, Infill geometry and UMD sums never needed that object, so they are computed as before. |
| 3 | counter loop | The two v17 skips that remain (SD position not in `DetectorGeometry`, `simCounter is None`) are **counted** and printed/saved in `resumen/`. | Previously silent. In the pilot both counts were 0. |
| 4 | new loop, same event | Table B: one row per simulated SD station, reconstructed or not, with MC muon/EM counts, `has_sd_rec`, true shower-plane `r_core_MC` and `phi_plane_euler_MC_true_core`. | The sample needed for "SD before the requirement". Its geometry uses **the same function** (`_proyectar_al_plano_mc`) as table A, so both tables are guaranteed to use identical arithmetic (the pilot checks it). Dense Ring stations are kept but not projected: they are virtual and not in `DetectorGeometry`. |
| 5 | `process_file_wrapper` | Two parquets per ROOT file (`modulos/`, `estaciones_sd/`) + a JSON summary; each written to `.tmp` then renamed; skip only if **both** exist. | A crash mid-write could leave a truncated parquet that the old "skip if it exists" check would accept forever. |
| 6 | filename metadata | Regular expression instead of `split('_')`. | `EPOSLHC_R_...` has an underscore inside the model name; v17 silently lost `model_mc`, `e_min_mc`, … for that production. |
| 7 | reader | Optional `max_events` (default `None` = whole file). | Only for quick pilots. |
| — | `_posicion_con_fallback` | Your try/fallback for station positions written once; bare `except:` → `except Exception:`. | Same behaviour for C++ lookup errors; Ctrl-C is no longer swallowed. |
| — | notebook | The production block is written once as `correr_tanda()` instead of six copies; `imap_unordered(chunksize=1)` everywhere (your iron-cell improvement); a `PILOTO` switch writing to a separate folder. | Legibility, and a pilot can never leave a 50-event file where the full run would then skip it. |

### What was deliberately NOT changed

- `if simCounter is None:` — see §4.1. This is the line Astra broke.
- The channel sum for `nMuones_MC`, including its 0 start value.
- The v17 skip when an SD position is not in `DetectorGeometry`.
- All rotations, the historical +π in `phi_plane_euler_MC*`, the Darko columns.
- Column names and meanings of the module table.
- No cuts on θ, r, energy, signal or saturation inside the reader.

---

## 4. Why each of Astra's reprocessing attempts failed

All in `claude_work/revision_asimetrias_sd_umd/02_notebooks/04_reprocesamiento/`.

### 4.1 `Procesamiento_ADST_v8-2_flag` — lost 63,747 rows

The change `if simCounter is None:` → `if simCounter is None or not simCounter:`
looks like a safety check. It is not neutral: PyROOT returns a **null proxy** (not
`None`) when there is no simulated counter. v17 kept those counters (their modules
have no channels, so `simCounter` is never dereferenced and `nMuones_MC` stays 0,
while the SD columns are valid). The extra `not simCounter` dropped them: 63,747
rows, all with `nMuones_MC = 0`, 52,452 with a positive SD muon count
(`AUDITORIA_FILAS.md` §1–2). And as §2 above explains, removing `HasStation` from
the counter loop could only ever recover ~45 rows.

### 4.2 `Procesamiento_ADST_dos_rutas` — never produced data

Two outputs (A with the cut, B without) from the same counter loop: same universe
problem as 4.1, so B ≈ A. It was also marked as never run on real ADST.

### 4.3 `Procesamiento_ADST_SD_UMD` (v18) — right idea, aborted on file 1

It did add a loop over `GetSimStationVector()`. It failed because:

- it compared its output to your March parquet with a strict
  `pd.testing.assert_frame_equal` on **all** columns and raised on the first
  difference: `sdMuonSignal_REC`, a column the comparison does not use and that
  differs only because of the Offline library (§5);
- it asked `DetectorGeometry` for Dense Ring positions (90xxx), which do not exist,
  flooding the log (120 errors in 10 events);
- 57 KB of densely hedged code made it hard to see what it actually did.

Here, validation is a separate step that reports every difference and only
*requires* identity on the columns the analysis uses.

---

## 5. Offline library mismatch (found while doing this)

Your ADSTs are an **icrc2025-test7** production. Your March v11 parquets were read
with **4.0.1-icrc23-prod1-root6** (the pilot with that library reproduces v11 in
every column, including the suspicious ones). Pilot, Run010, 50 events:

| | 4.0.1-icrc23 | icrc2025-test7 |
|---|---|---|
| Rows / keys vs v11 | identical | identical |
| `nMuones_MC`, `sd_nMuons_MC`, `sd_nEM_MC`, `r_core_MC`, `phi_plane_euler_MC_true_core`, `theta_MC` | identical | identical |
| `sdMuonSignal_REC` (reconstructed stations) | 0 everywhere, as in v11 | mean ≈ 9.9 VEM, max ≈ 715 |
| Extra warnings | `no dictionary for class MdSimScintillator::Particle` | — |
| Time for 50 events (1 process) | 13.5 s | 25.5 s |

Interpretation: the 4.0.1 dictionary cannot read that data member of a test7 ADST
(schema evolution), so it returns 0. The v17 comment "Suele ser 0 en Reco estándar"
was describing this read failure, not physics. **Recommendation: read test7 files
with icrc2025-test7-root6.** It does not affect the SD/UMD asymmetry result, but
any future use of `sdMuonSignal_REC` from v11 parquets would be wrong. Note test7
reads more slowly in this pilot (it actually deserialises more data), so the full
run may take somewhat longer than your March run.

---

## 6. How we know nothing was lost (pilot results)

See the README, "Validation status", for the numbers of the pilot run.
