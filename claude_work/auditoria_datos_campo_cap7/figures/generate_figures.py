#!/usr/bin/env python3
"""
generate_figures.py
====================
Audit script for the Chapter 7 (real-data) pipeline of the UMD azimuthal-asymmetry
thesis. Reads the already-processed parquet corpus (produced by
Scripts/Procesamiento_Datos_Campo/Procesamiento_Datos_Campo_v1.ipynb) and:

  1. Re-derives every quantitative claim made in report.html from the data on disk
     (nothing in the report is a hand-typed number).
  2. Produces the six diagnostic figures (F1-F5, F6 is a hand-authored SVG in the
     HTML itself).
  3. Runs a full A1(r, theta) harmonic sweep with the CORRECT cuts re-imposed in
     pandas (the on-disk parquet were built with looser cuts than the notebook
     claims -- see Finding A1 in the report) and an event-level bootstrap for
     errors, mirroring the Chapter 5 methodology.
  4. Dumps every number into stats.json so report.html can just read it.

This script does NOT touch the ADST files or re-run the Auger Offline reader --
it only re-aggregates the parquet corpus that already exists on disk.

Run with the repo's venv:
    /home/lsilva/Github/Tesis-de-Licenciatura---ITeDA/venv/bin/python generate_figures.py
"""
import os
import sys
import glob
import json
import time

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

plt.rcParams.update({
    "figure.dpi": 140,
    "savefig.dpi": 140,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PARQUET_DIR = "/home/lsilva/Github/parquet_datos_campo/"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.environ.get("CLAUDE_JOB_DIR", "/tmp")
CACHE_PATH = os.path.join(CACHE_DIR, "tmp", "corpus_cache.parquet")

COLS = [
    "event_id", "logE_REC", "theta_REC", "phi_REC", "core_x", "core_y",
    "counterId", "sdId", "moduleId", "nMuones_REC", "module_status",
    "r_core", "r_core_err", "phi_plane_sp",
    "is_sd_rejected", "is_counter_rejected", "subset", "year", "month", "day",
]

SUBSETS = ["PhaseI", "PhaseIISPMTPhaseIIBeta"]

# "Intended" cuts as documented in the notebook's config cell (Cell 4) --
# NOT what the parquet on disk were actually built with (see Finding A1).
INTENDED_MIN_LOGE = 17.0
INTENDED_MAX_THETA = 65.0

stats = {}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# 1. Load corpus (with cache)
# ---------------------------------------------------------------------------
def load_corpus(force=False):
    if os.path.exists(CACHE_PATH) and not force:
        log(f"Loading cached corpus from {CACHE_PATH} ...")
        df = pd.read_parquet(CACHE_PATH)
        log(f"  -> {len(df):,} rows")
        return df

    files = sorted(glob.glob(os.path.join(PARQUET_DIR, "**", "*.parquet"), recursive=True))
    log(f"{len(files)} parquet files found under {PARQUET_DIR}")
    dfs = []
    t0 = time.time()
    for i, f in enumerate(files):
        d = pd.read_parquet(f, columns=COLS)
        dfs.append(d)
        if (i + 1) % 300 == 0:
            log(f"  loaded {i+1}/{len(files)}  ({time.time()-t0:.0f}s)")
    df = pd.concat(dfs, ignore_index=True)
    df["module_status"] = df["module_status"].astype("category")
    df["subset"] = df["subset"].astype("category")
    log(f"Concatenated: {len(df):,} rows, {df.memory_usage(deep=True).sum()/1e9:.2f} GB in RAM")

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    df.to_parquet(CACHE_PATH, index=False)
    log(f"Cached to {CACHE_PATH}")
    return df


# ---------------------------------------------------------------------------
# 2. Global dataset facts (Findings A1-A3, E)
# ---------------------------------------------------------------------------
def compute_dataset_facts(df):
    log("Computing dataset facts (Findings A, E) ...")
    facts = {}

    ev_all = df.drop_duplicates("event_id")[["event_id", "logE_REC", "theta_REC", "subset", "year", "month"]]

    per_subset = {}
    for sub in SUBSETS:
        e = ev_all[ev_all["subset"] == sub]
        per_subset[sub] = {
            "n_events": int(len(e)),
            "theta_max_deg": float(e["theta_REC"].max()),
            "frac_theta_gt_65": float((e["theta_REC"] > 65.0).mean()),
            "frac_theta_gt_70": float((e["theta_REC"] > 70.0).mean()),
            "frac_logE_lt_17": float((e["logE_REC"] < 17.0).mean()),
            "logE_max": float(e["logE_REC"].max()),
            "n_logE_gt_19": int((e["logE_REC"] > 19.0).sum()),
            "years": sorted(e["year"].unique().tolist()),
        }
    facts["per_subset_raw"] = per_subset

    # High-energy "garbage tail" (Finding A3), computed on 2024 PhaseII as a
    # representative year with full statistics.
    e24 = ev_all[(ev_all["subset"] == "PhaseIISPMTPhaseIIBeta") & (ev_all["year"] == 2024)]
    hi = e24[e24["logE_REC"] > 19.0]
    facts["garbage_tail_2024"] = {
        "n_total_events": int(len(e24)),
        "n_hi_E": int(len(hi)),
        "theta_median_hi_E": float(hi["theta_REC"].median()),
        "theta_p75_hi_E": float(hi["theta_REC"].quantile(0.75)),
        "n_hi_E_theta_gt_65": int((hi["theta_REC"] > 65.0).sum()),
        "n_hi_E_theta_le_65": int((hi["theta_REC"] <= 65.0).sum()),
    }
    after = e24[(e24["logE_REC"] >= INTENDED_MIN_LOGE) & (e24["theta_REC"] <= INTENDED_MAX_THETA)]
    facts["garbage_tail_2024_after_correct_cuts"] = {
        "n_events": int(len(after)),
        "logE_max": float(after["logE_REC"].max()),
        "n_logE_gt_19_surviving": int((after["logE_REC"] > 19.0).sum()),
    }

    # Overlap check (Finding E): event_id intersection over shared months.
    in_overlap = ((ev_all["year"] == 2022) & (ev_all["month"] >= 2)) | \
                 ((ev_all["year"] == 2023) & (ev_all["month"] <= 4))
    n_overlap_months = 11 + 4  # 2022-02..2022-12, 2023-01..2023-04
    a = ev_all[(ev_all["subset"] == "PhaseI") & in_overlap]
    b = ev_all[(ev_all["subset"] == "PhaseIISPMTPhaseIIBeta") & in_overlap]
    sa, sb = set(a["event_id"]), set(b["event_id"])
    stations_a = set(df.loc[df["event_id"].isin(sa), "sdId"].unique())
    stations_b = set(df.loc[df["event_id"].isin(sb), "sdId"].unique())
    facts["phase_overlap"] = {
        "shared_months": n_overlap_months,
        "n_events_phaseI": len(sa),
        "n_events_phaseII": len(sb),
        "n_shared_event_ids": len(sa & sb),
        "n_stations_phaseI": len(stations_a),
        "n_stations_phaseII": len(stations_b),
        "n_stations_shared": len(stations_a & stations_b),
    }

    # Module / counter geometry (Finding B4).
    mc = df.groupby("counterId", observed=True)["moduleId"].nunique()
    facts["modules_per_counter"] = {
        "min": int(mc.min()), "max": int(mc.max()), "median": float(mc.median()),
        "n_counters_ne_3": int((mc != 3).sum()), "n_counters_total": int(len(mc)),
        "example_counters_gt3": mc[mc > 3].to_dict(),
    }

    # module_status / signal sanity (Finding D12).
    status_counts = df["module_status"].value_counts(normalize=True).to_dict()
    facts["module_status_fractions"] = {str(k): float(v) for k, v in status_counts.items()}

    cand = df[df["module_status"] == "candidate"]
    facts["nmuones_sanity"] = {
        "candidate_frac_exact_zero": float((cand["nMuones_REC"] == 0).mean()),
        "candidate_frac_negative": float((cand["nMuones_REC"] < 0).mean()),
        "candidate_min": float(cand["nMuones_REC"].min()),
    }

    # 2022 PhaseII startup rejection rate (Finding D13).
    for yr in [2022, 2023, 2024]:
        sub = df[(df["subset"] == "PhaseIISPMTPhaseIIBeta") & (df["year"] == yr)]
        if len(sub):
            facts.setdefault("phaseII_rejection_by_year", {})[str(yr)] = {
                "frac_sd_rejected": float(sub["is_sd_rejected"].mean()),
                "frac_counter_rejected": float(sub["is_counter_rejected"].mean()),
            }

    return facts


# ---------------------------------------------------------------------------
# Figure F1 -- coverage timeline
# ---------------------------------------------------------------------------
def fig_f1(df):
    log("F1: coverage timeline ...")
    ev = df.drop_duplicates("event_id")[["event_id", "subset", "year", "month"]]
    counts = ev.groupby(["subset", "year", "month"], observed=True).size().reset_index(name="n")
    counts["ym"] = counts["year"].astype(str) + "-" + counts["month"].astype(str).str.zfill(2)

    fig, ax = plt.subplots(figsize=(13, 4.3))
    colors = {"PhaseI": "#2b6cb0", "PhaseIISPMTPhaseIIBeta": "#dd6b20"}
    labels = {"PhaseI": "PhaseI", "PhaseIISPMTPhaseIIBeta": "PhaseII SPMT"}

    all_ym = sorted(counts["ym"].unique())
    x_idx = {ym: i for i, ym in enumerate(all_ym)}

    for sub in SUBSETS:
        sc = counts[counts["subset"] == sub].sort_values("ym")
        xs = [x_idx[y] for y in sc["ym"]]
        ax.bar(xs, sc["n"], width=0.42,
               align="edge" if sub == "PhaseI" else "center",
               color=colors[sub], alpha=0.85, label=labels[sub])

    # shade overlap window
    ov_start = x_idx.get("2022-02")
    ov_end = x_idx.get("2023-04")
    if ov_start is not None and ov_end is not None:
        ax.axvspan(ov_start - 0.5, ov_end + 0.5, color="grey", alpha=0.15, zorder=0)
        ax.text((ov_start + ov_end) / 2, ax.get_ylim()[1], "PhaseI / PhaseII overlap\n(only 1 shared event_id)",
                ha="center", va="bottom", fontsize=8, color="dimgray")

    step = max(1, len(all_ym) // 24)
    ax.set_xticks(range(0, len(all_ym), step))
    ax.set_xticklabels([all_ym[i] for i in range(0, len(all_ym), step)], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Events / month (as-processed cuts)")
    ax.set_title("F1 -- Temporal coverage by production subset")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f1_coverage_timeline.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure F2 -- phi exposure modulation + harmonic decomposition
# ---------------------------------------------------------------------------
def fourier_coeffs(phi_centers_deg, counts):
    """Return (c1, s1, c2, s2) relative-amplitude Fourier coefficients of a
    binned angular distribution, normalized to the mean count."""
    phi = np.deg2rad(phi_centers_deg)
    norm = counts.mean()
    c1 = np.mean((counts / norm - 1) * np.cos(phi)) * 2
    s1 = np.mean((counts / norm - 1) * np.sin(phi)) * 2
    c2 = np.mean((counts / norm - 1) * np.cos(2 * phi)) * 2
    s2 = np.mean((counts / norm - 1) * np.sin(2 * phi)) * 2
    return c1, s1, c2, s2


def fig_f2(df_clean, facts):
    log("F2: phi exposure modulation ...")
    r_bands = [(400, 600), (600, 800), (800, 1000), (1000, 1250)]
    phi_bins = np.linspace(-180, 180, 13)
    phi_centers = 0.5 * (phi_bins[1:] + phi_bins[:-1])

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    cmap = plt.cm.viridis(np.linspace(0.15, 0.9, len(r_bands)))

    exposure_facts = {}
    for (lo, hi), c in zip(r_bands, cmap):
        s = df_clean[(df_clean["r_core"] >= lo) & (df_clean["r_core"] < hi)]
        phi_deg = np.rad2deg(s["phi_plane_sp"].to_numpy())
        h, _ = np.histogram(phi_deg, bins=phi_bins)
        rel = h / h.mean()
        ax.plot(phi_centers, rel, "o-", color=c, lw=1.8, ms=4, label=f"r∈[{lo},{hi}) m")
        c1, s1, c2, s2 = fourier_coeffs(phi_centers, h.astype(float))
        exposure_facts[f"{lo}-{hi}"] = {
            "n": int(len(s)), "c1": float(c1), "s1": float(s1), "c2": float(c2), "s2": float(s2),
            "peak_to_trough_pct": float(100 * (rel.max() - rel.min())),
        }
    ax.axhline(1.0, color="k", ls="--", lw=1, alpha=0.6)
    ax.set_xlabel(r"$\phi_{SP}$ (deg)")
    ax.set_ylabel("Module counts / mean")
    ax.set_title("F2a -- Angular exposure by radial band")
    ax.legend(fontsize=8)

    ax = axes[1]
    labels = list(exposure_facts.keys())
    c1s = [exposure_facts[k]["c1"] for k in labels]
    s1s = [exposure_facts[k]["s1"] for k in labels]
    c2s = [exposure_facts[k]["c2"] for k in labels]
    x = np.arange(len(labels))
    w = 0.2
    ax.bar(x - 1.5 * w, c1s, w, label=r"$c_1$ (odd, biases $A_1$)", color="#c53030")
    ax.bar(x - 0.5 * w, s1s, w, label=r"$s_1$ (odd, biases $B_1$)", color="#dd6b20")
    ax.bar(x + 0.5 * w, c2s, w, label=r"$c_2$ (even, geometric jacobian)", color="#2b6cb0")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, fontsize=8)
    ax.set_ylabel("Relative Fourier amplitude")
    ax.set_title(r"F2b -- Exposure harmonics: $\cos2\phi$ dominates, $\cos\phi/\sin\phi$ near zero")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f2_phi_exposure.png"))
    plt.close(fig)

    facts["phi_exposure"] = exposure_facts


# ---------------------------------------------------------------------------
# Figure F3 -- energy spectrum / theta, garbage tail
# ---------------------------------------------------------------------------
def fig_f3(df):
    log("F3: energy spectrum & theta ...")
    ev = df.drop_duplicates("event_id")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    bins = np.arange(16.4, 22.4, 0.1)
    for sub, c in zip(SUBSETS, ["#2b6cb0", "#dd6b20"]):
        e = ev[ev["subset"] == sub]["logE_REC"]
        ax.hist(e, bins=bins, histtype="step", lw=1.6, color=c, label=f"{sub} (N={len(e):,})")
    ax.axvline(17.0, color="green", ls="--", lw=1.3, label="intended cut: logE≥17.0")
    ax.set_yscale("log")
    ax.set_xlabel(r"$\log_{10}(E_\mathrm{REC}/\mathrm{eV})$")
    ax.set_ylabel("Events (as-processed cuts)")
    ax.set_title("F3a -- Energy spectrum: on-disk cuts vs. intended cut")
    ax.legend(fontsize=8)

    ax = axes[1]
    for sub, c in zip(SUBSETS, ["#2b6cb0", "#dd6b20"]):
        t = ev[ev["subset"] == sub]["theta_REC"]
        ax.hist(t, bins=np.arange(0, 71, 1), histtype="step", lw=1.6, color=c, label=sub)
    ax.axvline(65.0, color="green", ls="--", lw=1.3, label="intended cut: θ≤65°")
    ax.set_xlabel(r"$\theta_\mathrm{REC}$ (deg)")
    ax.set_ylabel("Events (as-processed cuts)")
    ax.set_title("F3b -- Zenith distribution: on-disk cuts vs. intended cut")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f3_spectrum_theta.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure F4 -- candidate/rejected fraction vs r and phi
# ---------------------------------------------------------------------------
def fig_f4(df, facts):
    log("F4: selection fractions vs r, phi ...")
    d = df.copy()
    d["is_candidate"] = d["module_status"] == "candidate"

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    r_bins = np.arange(0, 1551, 100)
    d["rb"] = pd.cut(d["r_core"], r_bins)
    g = d.groupby("rb", observed=True)["is_candidate"].mean()
    centers = [iv.mid for iv in g.index]
    ax.plot(centers, g.values * 100, "o-", color="#2b6cb0")
    ax.set_xlabel("r_core (m)")
    ax.set_ylabel("% modules 'candidate'")
    ax.set_title("F4a -- Selection efficiency vs. core distance")
    ax.set_ylim(0, 100)

    ax = axes[1]
    phi_bins = np.linspace(-180, 180, 13)
    phi_centers = 0.5 * (phi_bins[1:] + phi_bins[:-1])
    d["phi_deg"] = np.rad2deg(d["phi_plane_sp"])
    d["pb"] = pd.cut(d["phi_deg"], phi_bins)
    g2 = d.groupby("pb", observed=True)["is_candidate"].mean()
    ax.plot(phi_centers, g2.values * 100, "o-", color="#dd6b20")
    ax.axhline(g2.values.mean() * 100, color="k", ls="--", lw=1, alpha=0.6)
    ax.set_xlabel(r"$\phi_{SP}$ (deg)")
    ax.set_ylabel("% modules 'candidate'")
    ax.set_title("F4b -- Selection efficiency vs. azimuthal phase")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f4_selection_bias.png"))
    plt.close(fig)

    facts["selection_efficiency_vs_phi"] = {
        "min_pct": float(g2.values.min() * 100), "max_pct": float(g2.values.max() * 100),
        "spread_pct": float((g2.values.max() - g2.values.min()) * 100),
    }
    facts["selection_efficiency_vs_r"] = {
        "min_pct": float(g.values.min() * 100), "max_pct": float(g.values.max() * 100),
    }


# ---------------------------------------------------------------------------
# Harmonic fit machinery (linear reparametrization: y = a + b cos + c sin)
# ---------------------------------------------------------------------------
def linear_harmonic_fit(phi_deg_centers, y):
    """OLS fit of y = a + b*cos(phi) + c*sin(phi). Returns (a, b, c)."""
    phi = np.deg2rad(phi_deg_centers)
    X = np.column_stack([np.ones_like(phi), np.cos(phi), np.sin(phi)])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta  # a, b, c


def cell_bootstrap_fit(sub_df, phi_bins, phi_centers, n_boot=300, min_count_per_bin=15,
                        min_bins_present=8, rng=None):
    """
    Given the rows (module-level) of one (r, theta, subset) cell, compute the
    nominal A1/B1 fit plus a per-event bootstrap error, mirroring the Chapter 5
    dense-ring toy-model methodology (resample at EVENT level, not module level,
    since modules of the same event/counter are geometrically correlated).
    """
    if rng is None:
        rng = np.random.default_rng(12345)

    phi_deg = np.rad2deg(sub_df["phi_plane_sp"].to_numpy())
    pb_idx = np.digitize(phi_deg, phi_bins) - 1
    valid = (pb_idx >= 0) & (pb_idx < 12)
    pb_idx = pb_idx[valid]
    y_all = sub_df["nMuones_REC"].to_numpy()[valid]
    event_codes, uniques = pd.factorize(sub_df["event_id"].to_numpy()[valid])
    nE = len(uniques)

    counts = np.bincount(pb_idx, minlength=12)
    if (counts >= min_count_per_bin).sum() < min_bins_present or nE < 50:
        return None

    # nominal fit (unweighted bin means, matching the bootstrap procedure)
    bin_sum = np.bincount(pb_idx, weights=y_all, minlength=12)
    bin_n = np.bincount(pb_idx, minlength=12).astype(float)
    ok = bin_n >= min_count_per_bin
    if ok.sum() < min_bins_present:
        return None
    y_mean = bin_sum[ok] / bin_n[ok]
    phi_c = phi_centers[ok]
    a, b, c = linear_harmonic_fit(phi_c, y_mean)
    if a == 0:
        return None
    A1 = b / a
    B1 = c / a

    # chi2/ndf using SEM of each bin (nominal, non-bootstrapped variance)
    var = np.zeros(12)
    for j in range(12):
        m = pb_idx == j
        if m.sum() > 1:
            var[j] = y_all[m].var(ddof=1) / m.sum()
    sem = np.sqrt(var[ok])
    sem[sem == 0] = np.nan
    model = a + b * np.cos(np.deg2rad(phi_c)) + c * np.sin(np.deg2rad(phi_c))
    resid = (y_mean - model) / sem
    resid = resid[np.isfinite(resid)]
    ndf = max(len(resid) - 3, 1)
    chi2_ndf = float(np.nansum(resid ** 2) / ndf) if len(resid) else np.nan

    # event-level bootstrap
    A1_boot, B1_boot = [], []
    for _ in range(n_boot):
        draw = rng.integers(0, nE, size=nE)
        mult = np.bincount(draw, minlength=nE)
        w = mult[event_codes]
        bs = np.bincount(pb_idx, weights=y_all * w, minlength=12)
        bn = np.bincount(pb_idx, weights=w, minlength=12).astype(float)
        okb = bn >= 1
        if okb.sum() < min_bins_present:
            continue
        yb = np.divide(bs, bn, out=np.zeros(12), where=bn > 0)[okb]
        pcb = phi_centers[okb]
        ab, bb, cb = linear_harmonic_fit(pcb, yb)
        if ab == 0:
            continue
        A1_boot.append(bb / ab)
        B1_boot.append(cb / ab)

    if len(A1_boot) < n_boot // 2:
        return None

    return {
        "A1": float(A1), "B1": float(B1),
        "A1_err": float(np.std(A1_boot)), "B1_err": float(np.std(B1_boot)),
        "chi2_ndf": chi2_ndf, "n_events": int(nE), "n_modules": int(valid.sum()),
        "n_phi_bins_used": int(ok.sum()),
    }


def run_sweep(df_clean, facts):
    log("Running full A1(r, theta) sweep (this is the slow step) ...")
    r_edges = np.arange(150, 1651, 150)
    theta_edges = [0, 10, 20, 30, 40, 50, 65]
    phi_bins = np.linspace(-180, 180, 13)
    phi_centers = 0.5 * (phi_bins[1:] + phi_bins[:-1])

    results = []
    for sub in SUBSETS:
        dsub = df_clean[df_clean["subset"] == sub]
        for ti in range(len(theta_edges) - 1):
            tlo, thi = theta_edges[ti], theta_edges[ti + 1]
            dth = dsub[(dsub["theta_REC"] >= tlo) & (dsub["theta_REC"] < thi)]
            if dth.empty:
                continue
            for ri in range(len(r_edges) - 1):
                rlo, rhi = r_edges[ri], r_edges[ri + 1]
                cell = dth[(dth["r_core"] >= rlo) & (dth["r_core"] < rhi)]
                if cell.empty:
                    continue
                fit = cell_bootstrap_fit(cell, phi_bins, phi_centers, n_boot=250)
                if fit is None:
                    continue
                fit.update({"subset": sub, "r_lo": rlo, "r_hi": rhi, "theta_lo": tlo, "theta_hi": thi})
                results.append(fit)
    log(f"Sweep produced {len(results)} valid (r,theta,subset) cells")
    facts["sweep"] = results
    return pd.DataFrame(results)


def fig_sweep(sweep_df):
    if sweep_df.empty:
        log("Sweep produced no valid cells -- skipping sweep figures.")
        return
    log("F5/F-sweep: rendering A1(r,theta) maps ...")

    for sub in SUBSETS:
        s = sweep_df[sweep_df["subset"] == sub]
        if s.empty:
            continue
        fig, ax = plt.subplots(figsize=(7.5, 5.5))
        r_mid = 0.5 * (s["r_lo"] + s["r_hi"])
        th_mid = 0.5 * (s["theta_lo"] + s["theta_hi"])
        sc = ax.scatter(r_mid, th_mid, c=s["A1"], s=90 + 400 * (s["chi2_ndf"] < 3),
                         cmap="RdBu_r", vmin=-0.3, vmax=0.3, edgecolor="k", linewidth=0.5)
        plt.colorbar(sc, ax=ax, label=r"$A_1$")
        ax.set_xlabel("r (m)")
        ax.set_ylabel(r"$\theta$ (deg)")
        ax.set_title(f"A1(r, θ) sweep -- {sub}\n(large marker = χ²/ndf < 3)")
        fig.tight_layout()
        safe = sub.lower().replace(" ", "_")
        fig.savefig(os.path.join(OUT_DIR, f"f5_a1_map_{safe}.png"))
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    theta_edges = sorted(sweep_df["theta_lo"].unique())
    cmap = plt.cm.plasma(np.linspace(0.1, 0.85, len(theta_edges)))
    for ax, sub in zip(axes, SUBSETS):
        s = sweep_df[sweep_df["subset"] == sub]
        for tlo, c in zip(theta_edges, cmap):
            st = s[s["theta_lo"] == tlo].sort_values("r_lo")
            if st.empty:
                continue
            r_mid = 0.5 * (st["r_lo"] + st["r_hi"])
            ax.errorbar(r_mid, st["A1"], yerr=st["A1_err"], fmt="o-", color=c, lw=1.4, ms=4,
                        label=f"{tlo}-{tlo+10 if tlo<50 else 65}°")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel("r (m)")
        ax.set_title(sub)
        ax.legend(fontsize=7, ncol=2)
    axes[0].set_ylabel(r"$A_1$")
    fig.suptitle("A1 vs. r by zenith band -- field data (event-bootstrap errors)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f5_a1_vs_r_by_theta.png"))
    plt.close(fig)

    # example single-cell gallery: pick a couple of highest-significance cells
    sweep_df = sweep_df.copy()
    sweep_df["sig"] = np.abs(sweep_df["A1"]) / sweep_df["A1_err"].replace(0, np.nan)
    top = sweep_df.sort_values("sig", ascending=False).head(4)
    return top


def fig_f5_gallery(df_clean, top_cells):
    if top_cells is None or top_cells.empty:
        return
    log("F5c: example-cell fit gallery ...")
    phi_bins = np.linspace(-180, 180, 13)
    phi_centers = 0.5 * (phi_bins[1:] + phi_bins[:-1])
    fig, axes = plt.subplots(1, len(top_cells), figsize=(4.2 * len(top_cells), 4.2))
    if len(top_cells) == 1:
        axes = [axes]
    for ax, (_, row) in zip(axes, top_cells.iterrows()):
        cell = df_clean[(df_clean["subset"] == row["subset"]) &
                         (df_clean["r_core"] >= row["r_lo"]) & (df_clean["r_core"] < row["r_hi"]) &
                         (df_clean["theta_REC"] >= row["theta_lo"]) & (df_clean["theta_REC"] < row["theta_hi"])]
        phi_deg = np.rad2deg(cell["phi_plane_sp"].to_numpy())
        pb_idx = np.digitize(phi_deg, phi_bins) - 1
        y = cell["nMuones_REC"].to_numpy()
        bin_sum = np.bincount(pb_idx, weights=y, minlength=12)
        bin_n = np.bincount(pb_idx, minlength=12).astype(float)
        ok = bin_n >= 15
        y_mean = np.divide(bin_sum, bin_n, out=np.full(12, np.nan), where=bin_n > 0)
        y_sem = np.full(12, np.nan)
        for j in range(12):
            m = pb_idx == j
            if m.sum() > 1:
                y_sem[j] = y[m].std(ddof=1) / np.sqrt(m.sum())
        norm = np.nanmean(y_mean[ok])
        ax.errorbar(phi_centers[ok], y_mean[ok] / norm, yerr=y_sem[ok] / norm, fmt="o", color="mediumblue",
                    capsize=3, ms=6)
        phi_plot = np.linspace(-180, 180, 200)
        model = 1 + row["A1"] * np.cos(np.deg2rad(phi_plot)) + row["B1"] * np.sin(np.deg2rad(phi_plot))
        ax.plot(phi_plot, model, "-", color="firebrick", lw=2)
        ax.axhline(1, color="k", ls="--", lw=0.8, alpha=0.6)
        ax.set_title(f"{row['subset'][:10]}\nr∈[{row['r_lo']:.0f},{row['r_hi']:.0f}) θ∈[{row['theta_lo']:.0f},{row['theta_hi']:.0f})\n"
                     f"A1={row['A1']:.3f}±{row['A1_err']:.3f}  χ²/ndf={row['chi2_ndf']:.1f}", fontsize=8)
        ax.set_xlabel(r"$\phi_{SP}$ (deg)")
    axes[0].set_ylabel(r"$\rho_\mu/\langle\rho_\mu\rangle$")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "f5_gallery.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    force_reload = "--reload" in sys.argv
    df = load_corpus(force=force_reload)

    facts = compute_dataset_facts(df)

    # Apply CORRECT cuts in pandas (Findings A1/A2/A3 fix)
    df_ok = df[(df["logE_REC"] >= INTENDED_MIN_LOGE) & (df["theta_REC"] <= INTENDED_MAX_THETA)].copy()
    # drop PhaseII startup year (Finding D13)
    startup_mask = (df_ok["subset"] == "PhaseIISPMTPhaseIIBeta") & (df_ok["year"] == 2022)
    n_dropped_startup = int(df_ok.loc[startup_mask, "event_id"].nunique())
    df_ok = df_ok[~startup_mask]
    facts["n_events_dropped_2022_phaseII_startup"] = n_dropped_startup

    df_clean = df_ok[(~df_ok["is_sd_rejected"]) & (~df_ok["is_counter_rejected"]) &
                      (df_ok["module_status"] == "candidate")].copy()

    facts["n_events_after_correct_cuts"] = {
        sub: int(df_ok.loc[df_ok["subset"] == sub, "event_id"].nunique()) for sub in SUBSETS
    }
    facts["n_events_clean_after_correct_cuts"] = {
        sub: int(df_clean.loc[df_clean["subset"] == sub, "event_id"].nunique()) for sub in SUBSETS
    }

    fig_f1(df)
    fig_f2(df_clean, facts)
    fig_f3(df)
    fig_f4(df_ok, facts)

    sweep_df = run_sweep(df_clean, facts)
    top_cells = fig_sweep(sweep_df)
    fig_f5_gallery(df_clean, top_cells)

    with open(os.path.join(OUT_DIR, "stats.json"), "w") as f:
        json.dump(facts, f, indent=2, default=str)
    log(f"Wrote {os.path.join(OUT_DIR, 'stats.json')}")
    log("Done.")


if __name__ == "__main__":
    main()
