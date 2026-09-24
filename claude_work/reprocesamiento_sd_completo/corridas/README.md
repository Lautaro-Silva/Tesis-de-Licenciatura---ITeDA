# Run records

Executed copies of `Procesamiento_ADST_v17_completo.ipynb`, kept for provenance: they show
exactly what was run, when, and what it printed. The notebook in the parent folder stays as the
**template** (`PILOTO = True`, no outputs), so that opening it and running everything can never
launch a production batch by accident.

## `corrida_20260917_sib_proton_17.ipynb`

The SIBYLL 2.3e proton production, 17.5–18.0, 20 files, run by the author on 2026-09-17 with
`PILOTO = False` and 8 workers. Output went to
`/home/lsilva/Github/ADST_Alexey_module_v13/parquet_sib_proton_17/`.

From its output:

- 20 files, ~1200 events each, ~650 s per file.
- Module rows with `has_sd_rec` reproduce the March v11 counts file by file
  (79710, 79305, 78960, 79020, 79953, …).
- `Counters descartados: {'counter_sin_posicion_sd_en_geometria': 0, 'counter_con_simCounter_None': 0}`
  in every file — nothing dropped.

**Which Offline library read it.** The log records
`AUGEROFFLINEROOT: .../auger/offline/4.0.1-icrc23-prod1-root6`, not the `icrc2025-test7-root6`
recommended in the README. What that means for this dataset, from the two-library pilot
(`CAMBIOS.md` §5):

- Everything the asymmetry analysis uses is **unaffected**: `nMuones_MC`, `sd_nMuons_MC`,
  `sd_nEM_MC`, `sdSignal_REC`, `r_core_MC`, `phi_plane_euler_MC_true_core`, `theta_MC` are
  identical with either library. The v13 results reproduce Astra's numbers exactly, which
  confirms this end to end.
- The single exception is **`sdMuonSignal_REC`, which is 0 in every row** of this v13 dataset,
  because the 4.0.1 dictionary cannot read that member of a test7 ADST. It is the same artifact
  that made the column 0 in the March v11 parquets. No analysis here uses it.

So this dataset is fine as it stands. Only if `sdMuonSignal_REC` is ever needed would the
production have to be re-read with `icrc2025-test7-root6`.

The validation cell at the end of the notebook was not executed in this run. The equivalent
checks were done separately on a full file (`README.md`, "Validation status", section B) and
again implicitly by the exact reproduction of Astra's numbers from this data.
