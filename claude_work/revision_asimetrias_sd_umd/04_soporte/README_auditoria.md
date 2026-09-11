# SD–UMD asymmetry forensic review

Start with [the report](../01_fisica/report.md), or its [HTML version](../01_fisica/report.html).
The [selection figure](figuras/selection_audit.svg) and all numerical tables are local.
Positive A₁ means an early-region excess; zero azimuth is early.

The principal new result is a direct twenty-file ADST counterfactual: the far-bin
SD truth-count coefficient is +0.0676 before station-reconstruction selection and
−0.0945 afterward. This is not a complete first-principles explanation of both
detectors. The report separates the demonstrated selection contribution, the
remaining approximate-model discrepancy, and the UMD serialization limitation.

## Scope and safety

All code writes only to this folder. Input parquet, raw ADST, Offline source,
thesis and GAP files are read-only. No simulation/reconstruction production was
launched; all calculations and readers are single-process. No staging, commit or
push was performed by this review.

The review started on `codex/sd-muon-asymmetry-forensic-review`. During the long
session another session changed the shared checkout to
`claude/presentacion-rafa-2026` and made presentation commits. Those checkout and
commit changes were left untouched; this review's files remain untracked in this
new folder. Do not assume the current branch is the review branch before any
future staging. Existing unrelated edits were preserved.

## Reproduce with the existing cached audit outputs

From the repository root, use the existing virtual environment. These commands
need neither ROOT nor Offline initialization. No dependency installation is needed.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/verify.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/transport_checks.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/statistical_checks.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/parent_bootstrap.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/selection_closure.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/selection_robustness.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/umd_selection_check.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/derivation_checks.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/build_report.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/validate_artifacts.py
```

`verify.py` also reads the existing parquet at
`/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/`.
The transport calculation is a deterministic sensitivity scan, not a calibrated
shower generator. Its input assumptions are in the script and report §5.3.

The HTML uses the previous report's stylesheet as a build-time input and MathJax
from a CDN for browser-side equation rendering. Text and tables are readable
without network access; the Markdown preserves all original TeX.

## Optional: regenerate the raw-ADST audit

These are read-only extractions from existing production, not new physics jobs.
The ROOT version in the default venv is not the correct ROOT6 runtime for these
ADST libraries. Use the following environment for **each** raw reader:

```bash
PYTHONPATH=/srv/software/amd64/ubuntu/24.04/external/root/6.30.04/lib LD_LIBRARY_PATH=/srv/software/amd64/ubuntu/24.04/external/root/6.30.04/lib:/opt/auger/offline/icrc2025-test7-root6/lib /usr/bin/python3 -u claude_work/revision_asimetrias_sd_umd/04_soporte/codigo/adst_counts_fast.py --files 20
```

The count-only reader took about four minutes for the twenty files in this run;
the elapsed time and filenames are recorded in `adst_counts_fast_summary.json`.
It overwrites `adst_counts_fast.csv`; running `--files 1` would replace the full
sample with the pilot, so rerun the statistical/report builders afterward and
check their recorded file counts.

To reproduce bounded pilots, substitute `read_adst_audit.py --files 1`,
`umd_selection_read.py --files 1`, or `adst_metadata.py` into the same environment
command. The full SD-particle pilot took several minutes, whereas the UMD-summary
pilot took about half a minute in this run. Neither timing is a guarantee on the
shared server. Do not scale the full-particle reader to a large production without
first estimating I/O cost. Header extraction is allowlisted to avoid exporting
personal host/user configuration.

## Which files are authoritative?

| Result | Outputs | Producer |
|---|---|---|
| Legacy corrected integral | `analytic_legacy.csv`, `analytic_summary.json` | `verify.py` |
| Existing selected parquet fits | `mc_fits.csv`, `mc_summary.json`, `far_bin_diagnostics.csv` | `verify.py` |
| Selected-parquet standardization | `standardized_fits.csv`, `primary_azimuth_fits.csv` | `statistical_checks.py` |
| Conservative parquet uncertainty | `parent_cluster_bootstrap.json` | `parent_bootstrap.py` |
| Transport sensitivity | `transport_sensitivity.csv`, `transport_convergence.csv` | `transport_checks.py` |
| Twenty-file raw SD counts | `adst_counts_fast.csv`, `adst_counts_fast_summary.json` | `adst_counts_fast.py --files 20` |
| Exact selection matching and paired test | `selection_closure_fits.csv`, `selection_closure_bins.csv`, `selection_paired_bootstrap.csv`, `selection_match_summary.json` | `selection_closure.py` |
| Common-covariate raw comparison | `selection_standardized.json`, `selection_narrow_bins.csv`, `selection_composition.csv` | `selection_robustness.py` |
| UMD serialization audit | `umd_selection_raw.csv`, `umd_selection_raw_summary.json`, `umd_selection_check.json` | UMD reader and checker |
| Geometry, normalization, scale checks | `unit_checks.json`, `derivation_numbers.json` | `derivation_checks.py` |
| Offline implementation fingerprints | `offline_source_manifest.json` | `derivation_checks.py` |
| Final narrative and figure | `report.md`, `report.html`, `selection_audit.svg` | `build_report.py` |

`adst_station_audit.csv`, `adst_selection_*.csv`, and
`adst_cluster_bootstrap.json` are **single-file exploratory pilot** results,
not the final twenty-file result. `has_md=-1` in the SD-only extraction means
not read; it must never be interpreted as a measured false/zero value.
`cluster_bootstrap.json` uses file/event clusters and is superseded for the main
uncertainty claim by the conservative parent grouping. `energy_strata.csv` is
exploratory, not a calibrated energy-conditional inference.

Local `.txt` files are reading caches extracted from repository PDFs.
`bertou_billoir.txt` has broken font encoding and was **not** used to establish
its equations; the original PDF was inspected through rendered pages.

No per-muon production tuples have been recovered. Existing SD injection
particle lists are a different and useful data product. Empty untriggered UMD
ADST scintillator lists must not be imputed as zero physical injection.
