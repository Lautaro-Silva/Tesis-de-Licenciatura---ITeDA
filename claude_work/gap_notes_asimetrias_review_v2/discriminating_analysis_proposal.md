# Proposal: discriminating tests for the SD-inversion mechanism and the UMD's own instrumental asymmetry

## Why

`kinematic_divergence_math_check.md` and `thesis_review_familiarization_notes.md` (this
session) show that neither mechanism GAP-2026-041 offers for the SD sign inversion
(kinematic-divergence attribution in §6 ¶2, tank/track-length in §6 ¶3) is supported in
the direction claimed, when checked against the note's own cited sources (Cazón 2012,
Luce ICRC-2021, Bertou & Billoir GAP-2000-017) and against an exact geometric theorem
(Cauchy mean chord). They also show the UMD's own $A_1$ has two unremoved, purely
instrumental positive contributions (flat-plane $A_{geo}$, azimuthally-modulated
overburden threshold) of the same order as the measured signal. All of this was
established analytically/with toy geometry, not from the group's actual MC. This
proposes what to check directly in the existing simulation to settle it.

## What's already available vs. what needs new extraction

Checked directly in `Scripts/Procesamiento_ADST_v8-2.ipynb` (the main MC ADST→parquet
pipeline) rather than assumed:

**Already extracted, no new ADST work needed:**
- Station-level MC muon count `simStation.GetNumberOfMuons()` (`sd_nMuons_MC`), plus
  `n_e`, `n_gamma` — this is exactly $N_{\mu,\mathrm{sup}}^{MC}$, $N_{EM}^{MC}$ from the
  GAP notes' Fig. "SD_Desglose_Componentes_vs_UMD".
- Station 3D position, MC/REC core position (`GetCoreSiteCS()`), MC/REC zenith
  (`GetZenith()`), and `GetAzimuthSP()` — everything needed to compute each station's
  **local incidence angle** $\theta_{loc}$ (angle between the muon's nominal arrival
  direction, i.e. the shower axis, and the station's own surface normal) purely from
  existing geometry, station by station. This is enough for check #1 below with zero new
  ADST-level extraction.
- UMD module-level `mdSimScintillator.GetNumberOfInjectedMuons()` — aggregate count per
  module, same situation as the SD muon count.

**Not currently extracted, needs checking against the ADST content first:**
- Per-muon energy at the point of tank/module incidence (needed for check #2's fixed
  energy threshold) — `GetNumberOfInjectedMuons()` is an aggregate; whether the
  `icrc2025-test7` production ADST retains a per-particle energy list at the SD/UMD
  boundary (vs. only aggregated multiplicities, which is common in production ADST to
  save space) has **not been verified in this session** and should be checked first in
  the Auger Offline environment (not available in this repo's venv per CLAUDE.md §10)
  before committing to check #2.
- Per-muon entry face (top vs. side) or local incidence angle at the WCD tank itself —
  same caveat; would need whatever "ground/tank particle" level of detail the production
  ADST carries, if any.

## Proposed checks, in order of what's cheap now

### 1. Recompute the UMD's flat-plane and threshold-modulation instrumental asymmetry directly on real MC geometry (feasible immediately, no new extraction)

This session's estimate ($A_{geo}\approx+0.11$, threshold-modulation $A_1\approx+0.11$ to
$+0.22$ at the reference point) used an idealized point-source geometry. The pipeline
already has everything needed to check this on the actual simulated shower ensemble:

- For each UMD module hit, compute $\theta_{loc}$ from the existing MC core + axis +
  module position (a few lines of vector algebra on columns already in the parquet
  output — no re-run of the ADST reader needed if `sd_nMuons_MC`-style geometry columns
  are already retained per station/module; otherwise a light re-extraction).
- Bin by $\phi$ (shower-plane azimuth, already computed) and refit $A_1$ using
  $\theta_{loc}$ (rather than $\cos\phi$ alone) as a control variable, to see whether the
  modelled azimuthal modulation is quantitatively consistent with the $\cos\theta_{loc}$
  aperture-projection prediction on top of the aggregate muon density trend.
- This directly tests whether the "UMD is attenuation-clean" claim survives contact with
  real MC geometry, independent of the SD-inversion question.

### 2. Fixed-energy-threshold UMD reprocessing (needs an ADST-content check first)

If per-muon energy at the UMD boundary is retained: reprocess the UMD $A_1$ using a
*fixed* $E_{thr}$ (independent of $\theta_{loc}$) instead of letting the soil overburden
threshold vary naturally with local incidence angle. Comparing this fixed-threshold
$A_1$ against the nominal one isolates exactly how much of the UMD's measured asymmetry
is the threshold-modulation effect from `kinematic_divergence_math_check.md`, vs.
genuine attenuation. If the ADST doesn't carry per-muon energy, the same test could be
done at the CORSIKA/Offline simulation level for a small dedicated re-run — worth
flagging the cost of that explicitly and asking before launching it (per CLAUDE.md §3,
shared-server compute).

### 3. SD muon $A_1$ from $F_\perp$ instead of tank-boundary count (needs an ADST-content check first)

If a per-particle entry face or local angle is available at the WCD boundary: recompute
$N_{\mu,\mathrm{sup}}^{MC}$'s contribution to $A_1$ as flux per unit area perpendicular
to the arrival direction ($F_\perp$), split top-entry vs. side-entry, and separately by
muon energy band. This would directly separate:
- the pure production-kinematics/divergence effect (this session's Sec. 1 finding: should
  be early-favoring below $E^*\approx2$–3 GeV, late-favoring above),
- the tank aperture/track-length effect (this session's finding: should integrate to
  exactly zero for the VEM response, by the Cauchy relation, regardless of energy), and
- any residual not explained by either — which would be the first genuinely new physics
  result to come out of this line of investigation.

If the ADST does not retain per-particle boundary information, this check is not free
and should be scoped as a small dedicated simulation/production study, not assumed
available in the existing `icrc2025-test7` files.

## Suggested order of work

1. Check #1 first — it's fully within the current pipeline and answers whether the UMD
   result itself needs qualifying before anything else.
2. In parallel, a short check (in the Auger Offline environment, not this venv) of
   whether `icrc2025-test7`'s ADST retains per-particle energy/entry-face information at
   the SD/UMD boundary, to scope checks #2 and #3 honestly before proposing them as
   "cheap."
3. Only after that: decide whether #2/#3 are a light reprocessing pass or need new
   simulation, and whether the cost is worth flagging to the director given shared-server
   compute constraints (CLAUDE.md §3).

None of this requires touching the thesis or GAP note text yet — it's aimed at
establishing what the group can actually claim before either document is revised to
reflect the corrected sign/open-mechanism framing from the other two notes in this
folder.
