# Proposal: discriminating tests for the SD-inversion mechanism and the UMD's own instrumental asymmetry

## Why

`kinematic_divergence_math_check.md` and `thesis_review_familiarization_notes.md` show
that neither mechanism GAP-2026-041 offers for the SD sign inversion (kinematic-divergence
attribution in §6 ¶2, tank/track-length in §6 ¶3) is supported in the direction claimed,
when checked against the note's own cited sources (Cazón 2012, Luce ICRC-2021, Bertou &
Billoir GAP-2000-017) and against an exact geometric theorem (Cauchy mean chord). They
also show the UMD's own $A_1$ has two unremoved, purely instrumental positive
contributions (flat-plane $A_{geo}$, azimuthally-modulated overburden threshold) of the
same order as the measured signal. `sd_umd_synthesis.md` (new) pushes this further,
directly in response to the author's review, which confirmed the SD/UMD split is
physical (reproduced with Dense Ring + Infill, MC + REC) and asked for an actual
account of what's driving it, not just a list of ruled-out mechanisms. That file backs
out an implied true-flux $A_1\approx-0.13$ from Table 2's reported count (§4 there), and
shows kinematic divergence doesn't survive being weighted over a realistic muon spectrum
either (§5 there) — meaning the true mechanism is not yet identified, and proposes a
hypothesis for the UMD/SD contrast that doesn't depend on identifying it. All of this was
established analytically/with toy geometry, not from the group's actual MC. This file
proposes what to check directly in the existing simulation to settle it, updated with the
two checks that synthesis directly motivates.

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

**Additionally not currently confirmed available (needed for new check #0 below):**
- A MC-truth muon-only energy-deposit/VEM variable at the SD station, separate from the
  total VEM signal and separate from the raw muon count. The pipeline reads
  `sdStation.GetMuonSignal()` at the *reconstructed* level, with the pipeline's own
  comment noting it's "usually 0 in standard Reco" — whether `simStation` (MC truth)
  exposes an equivalent muon-only deposited-energy accessor has **not been checked in
  this session** and needs verifying in the Offline environment before check #0 can be
  called cheap.

## Proposed checks, in order of what they'd settle

### 0. Isolate muon-only VEM signal and compare its $A_1$ to the muon MC-truth count's $A_1$ (needs an ADST-content check first — see above)

Motivated directly by `sd_umd_synthesis.md` Part 1: by the Cauchy mean-chord theorem, the
tank's own geometric term cancels *exactly* for an energy-weighted (VEM) signal but not
for a raw count — so the muon-only VEM's $A_1$ should come out **more negative** than the
muon count's reported $-0.10$ (this session's toy-geometry estimate: closer to $-0.13$).
This is the single most direct test of whether the tank/track-length mechanism is
correctly excluded as a cause: if muon-only VEM instead comes out *less* inverted than
the count, the cancellation argument is missing something and needs revisiting (most
likely the single-nominal-incidence-angle approximation flagged as this session's own
caveat). Whether this is actually cheap depends entirely on the ADST-content question
above.

### 1. Recompute the UMD's flat-plane and threshold-modulation instrumental asymmetry directly on real MC geometry (feasible immediately, no new extraction)

Sharpened by `sd_umd_synthesis.md` Part 4/5 into a specific test of the "instrumental
floor" hypothesis: strip out both UMD terms (fixed $E_{thr}$ instead of
$1\,\text{GeV}/\cos\theta_{loc}$, and flux-per-perpendicular-area instead of raw aperture
count) and see whether the de-instrumented UMD signal shrinks substantially, or even
inverts, at large $r$ — which is what the hypothesis predicts if the UMD's clean-looking
result is a byproduct of its own construction rather than evidence it filters out
whatever the SD sees. This session's estimate ($A_{geo}\approx+0.11$,
threshold-modulation $A_1\approx+0.11$ to $+0.22$ at the reference point) used an
idealized point-source geometry. The pipeline already has everything needed to check
this on the actual simulated shower ensemble:

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

### 4. Check the WCD signal-to-muon-count reconstruction for an angle-dependent bias (needs looking at the unfolding algorithm, not the ADST)

Raised directly by the author, independent of everything above: does whatever algorithm
converts WCD VEM signal into an estimated $N_\mu^{REC}$ correct for the angle-dependence
of muon track length? If a grazing (late-region) entry systematically produces more
signal per muon and the unfolding doesn't account for that, $N_\mu^{REC}$ would be biased
upward in the late region independent of the true muon count or the true flux — a
mechanism distinct from everything else in this proposal, since it only touches
*reconstructed* quantities and has no MC-truth-level counterpart. This needs reading the
actual Offline reconstruction module (not the ADST reader), scoped separately from the
MC-truth checks above.

## Suggested order of work

1. Check #1 first — it's fully within the current pipeline and answers whether the UMD
   result itself needs qualifying before anything else, and directly tests the
   "instrumental floor" hypothesis in `sd_umd_synthesis.md`.
2. In parallel, a short check (in the Auger Offline environment, not this venv) of
   whether `icrc2025-test7`'s ADST retains (a) a MC-truth muon-only VEM/energy-deposit
   variable at the SD station (needed for check #0) and (b) per-particle energy/entry-face
   information at the SD/UMD boundary (needed for checks #2 and #3) — to scope all three
   honestly before proposing them as "cheap."
3. Only after that: decide whether #0/#2/#3 are a light reprocessing pass or need new
   simulation, and whether the cost is worth flagging to the director given shared-server
   compute constraints (CLAUDE.md §3).
4. Check #4 (reconstruction unfolding) can proceed independently of the above at any
   point — it needs code review, not new data extraction.

None of this requires touching the thesis or GAP note text yet — it's aimed at
establishing what the group can actually claim before either document is revised to
reflect the corrected sign/open-mechanism framing from the other notes in this folder
(`kinematic_divergence_math_check.md`, `thesis_review_familiarization_notes.md`,
`sd_umd_synthesis.md`).
