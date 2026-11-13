# Roadmap: from the thesis to an ICRC 2027 contribution (and the PhD)

Status: 13 Nov 2026. Everything that is open after the thesis, the UMD Foundations Meeting talk
(4 Nov 2026), the supervisor's review and the jury's comments, organized around the two results
that matter. The thesis text is frozen; corrections go into GAP notes and the proceeding.

Legend: **[now]** can be started with the data and code that already exist · **[ICRC]** needed
for a sound ICRC 2027 contribution · **[PhD]** longer-term line · **[fix]** small inconsistency
found while preparing the talks.

Collaboration process: an Auger ICRC contribution goes through the collaboration's internal review,
normally on top of GAP notes. Check the 2027 abstract and proceeding deadlines and the internal
review calendar early; nothing below assumes specific dates.

---

## 0. The fronts

**Front A — the asymmetry is seen in field data, but the core must be corrected.** The
reconstructed core is shifted systematically toward the early region, and the shift suppresses A1
as −βb/r. Correcting it should recover the asymmetry at all distances, in data and in REC-level
simulations, and open the question of mass discrimination with the full radial range.

**Front B — the SD inversion is compatible with a station-selection effect.** Turn the
consistency tests into a correction: remove the selection from the SD average using what the
simulations tell us about the selection, and find out which stage of HasStation is responsible.

**Front C — event by event.** Everything so far fits A1 on ensembles of showers. The ideal is a
per-event estimator. It is also the natural place to solve fronts A and B inside one fit: the core
fitted with an azimuthally modulated LDF, and the selection in the likelihood.

Proposed ICRC 2027 contribution, built on two GAP notes:

> Azimuthal asymmetry of the muon density with the AMIGA Underground Muon Detector: station
> selection, core-reconstruction bias, and field data.

---

## 1. Front A: core correction, field data and mass

A.1 **[now] Parametrize b(θ) and β(θ) from simulations, in a form applicable to field data.**
This is the step everything else in front A depends on, and it needs some thought:
- *b* is measured with MC truth (Δr = r_MC − r_REC = a + b cos φ), so in data it can only come from
  simulations. Fit b as a function of θ (first look, three points: b/tan θ ≈ 20–22 m, so b grows
  roughly as tan θ, not validated), and check its dependence on energy and on r.
- **b may depend on the primary.** The shift is caused by the asymmetry itself (a symmetric LDF
  absorbs the early excess), so primaries with a larger asymmetry may have a larger b. Measure b
  for p, He, Fe and both models before deciding whether a single b(θ) can be applied. If b depends
  on composition, a composition-averaged correction could partly wash out, or fake, a mass
  separation in A.3.
- *β* is the local slope of the muon LDF, β = −d ln ρ/d ln r, and it steepens with r. In the
  simulations it is measured on the true distance; in data it can be measured on the field LDF
  itself (on r_REC, where the shift smears it slightly). Decide which one to use and check that
  the two agree in the simulations.
- Validate on simulations not used to build the parametrization (train/test split): other
  showers, other primaries, other hadronic models. This tests model and composition dependence,
  not data–MC differences (muon deficit).

A.2 **[now] Apply the correction to the REC-level Infill simulations and to field data**, over the
whole radial range: either move the reconstructed core by b toward the late side and recompute r
and φ, or add βb/r to A1 bin by bin. In the simulations, the target is the A1(r) with MC geometry;
check the range of validity of the first-order formula (it should fail very near the core, where
b/r is not small). In data, check how much of the near-core suppression is recovered.

A.3 **[now] Asymmetry vs primary mass with the corrected REC geometry.** With the correction, the
full radial range becomes usable, and A1 grows with r. Compare p, He and Fe (SIBYLL 2.3e, and He
with QGSJET-III) as a function of r and θ, and ask whether the separation is clearer far from the
core, e.g. "above 1000 m the corrected asymmetry discriminates primaries". To make that statement:
- use errors from an event-level bootstrap;
- quantify the separation with the spread of A1 between independent sub-samples of showers, since
  A1 is not measurable event by event; the Dense Ring S ≈ 2.5 is a difference of means that
  grows as √N, not a merit factor;
- estimate how many field events per cell such a separation would need, and compare with the
  field-data statistics at r > 1000 m.
Then put the corrected field data on the same plot (the golden-region numbers today, uncorrected:
data 0.023 ± 0.003; p 0.017, He 0.022, Fe 0.019 with SIBYLL; He 0.028 with QGSJET-III).

A.4 [ICRC] **Test −βb/r as a function of r** with β bin by bin (proposal 2 of `README.md`): a
panel of A1^MC − A1^REC vs r with βb/r on top. Expected to hold at 450–1200 m and to fail at the
ends; state the range of validity. This is the validation of A.2.

A.5 [ICRC] **Confirm the cause of the shift**: refit the core with an LDF that includes a cos φ term
and check that b goes to zero. If it does, the same fit is an alternative correction (at least for
the high-multiplicity events), done in the reconstruction instead of afterwards.

A.6 [ICRC] **Errors of the core shift from an event-level bootstrap**: stations of one shower share
the core error, so the current 0.1–0.2 m are underestimated.

## 2. Front B: station selection

B.1 **[now] Remove the selection with Bayes, using the simulations** (jury proposal,
`Correccion_seleccion_trigger_A1.pdf`, item 5 of `README.md`). The measured quantity is
E[N | x, T = 1], not E[N | x]; the selection efficiency ε(n, x) = P(T = 1 | N = n, x), which depends on
φ through the EM signal, can be measured in the simulations, where N and HasStation are known for
every station. Steps:
1. tabulate or parametrize ε(n, n_EM, r, θ) from the simulations (in the notes, a logistic);
2. fit A1 with the truncated and the censored likelihoods (the censored one also uses the stations
   that were not kept, which the SD records);
3. closure test in the simulations: does it recover the all-stations A1 (+0.069 ± 0.016 at
   1200–1350 m) from the selected stations (−0.124 ± 0.019)? In the jury's toy MC the censored
   likelihood recovers +0.070 from a naive −0.098, and is much more robust than the truncated one to
   a ±15% error in the EM model;
4. only then apply it to field data, with ε from the simulations (systematics: model, threshold,
   EM). Involve the statistician the co-director suggests.
For the UMD this does not apply directly: UMD zeros are real zeros, not failed triggers
(co-director). Section 3 of the notes has a hierarchical extension where tank and module share the
local density.

B.2 [ICRC/PhD] **Play with the trigger configuration in Offline**: re-run the SD reconstruction of
the simulations with modified station-trigger settings and check whether the far-core inversion
follows. This is the direct test of "it is the trigger", and it separates the trigger from readout
and reconstruction. Needs Offline runs on the server: estimate the CPU and disk cost before
launching.

B.3 [ICRC] **Separate trigger, readout and station reconstruction inside HasStation** with the
station trigger flags (T1/T2, ToT, ToTd, MoPS). Verify the thresholds before quoting any number
(e.g. Abraham et al., NIM A 613 (2010) 29); the thesis says "about 1 VEM".

B.4 [ICRC] **Generalize the tests**: today only 30–40°, protons, SIBYLL 2.3e.

B.5 [ICRC] **The UMD's own selection**: argued null to first order, with a residual through the
shared local density. Measuring it needs the UMD counts of the non-selected stations, not stored in
the production used. Check whether `~/Github/ADST_Alexey_module_v13/` (`estaciones_sd/`, `modulos/`,
`resumen/`) is the SD-station-preserving reprocessing of `claude_work/reprocesamiento_sd_completo/`
and contains them.

B.6 [PhD] **SD without selection vs UMD**: the UMD stays 0.03–0.06 higher at 150–900 m (excludes
zero at 95%). Candidates: flat-plate vs tank response, UMD threshold.

B.7 [ICRC] **Literature**: find out whether Luce et al. (ICRC 2021, small negative muon A1 at
1500–2000 m) and Bradfield (2022, SD inversion) averaged over triggered stations only.

## 3. Front C: event by event

**How much information one event carries** (protons and iron, SIBYLL 2.3e, 17.5–18.0, Infill,
stations at 300–1500 m, injected muons): a median of 8–12 stations and 35–100 muons per event
(fewer for protons and at 50–65°). From Poisson statistics alone, σ(A1) ≈ √(2/N_μ) ≈ 0.15–0.29 per
event, larger than A1 itself (~0.1) and about ten times the p–Fe difference (≲ 0.01–0.02 on the
Dense Ring). This is optimistic: it ignores the per-event LDF normalization, shower-to-shower
fluctuations and the UMD counting resolution. A free 12-bin harmonic per event does not work at
these energies (as the thesis says).

C.1 **[now] One physical parameter per event, not a free harmonic.** Fit an LDF with an azimuthal
modulation of fixed shape, e.g. the Ch. 3 toy model A1 ≈ κ (r/D) tan θ, leaving free only the
normalization and the asymmetry scale (or D, the distance to the muon production region, which is
what carries the mass sensitivity). Use the likelihood of the real UMD counting (segmented
scintillators), not a Gaussian. First step, doable now: MC with the true core, to measure the
per-event resolution and bias of the parameter as a function of E, θ and multiplicity, and the
event-level merit factor |⟨x⟩_p − ⟨x⟩_Fe| / √(σ_p² + σ_Fe²), which the thesis could not compute.

C.2 [ICRC/PhD] **Fit the core in the same likelihood.** Per event, a core shift along the
early–late direction is nearly degenerate with A1, but their radial shapes differ: the spurious
term falls as βb/r, the physical one grows with r. A joint SD+UMD fit with modulated LDFs can
separate them with stations over a wide range of r. This is the same fit as A.5, so one tool serves
both fronts.

C.3 [ICRC/PhD] **Put the selection in the same likelihood**: the censored likelihood of B.1, with
the silent stations as censored observations, is a per-event likelihood by construction.

C.4 [PhD] **Hierarchical Bayesian model.** With weak information per event, give each event its own
parameter drawn from a population distribution that depends on (θ, E, composition). This yields
per-event posteriors and the population distribution together, and mass discrimination is then
measured on per-event estimates.

C.5 [PhD] **Higher energies.** The error scales as 1/√N_μ, and N_μ grows roughly as E: rough
estimate σ(A1) ≈ 0.1 at 10^18.5 and 0.05–0.06 at 10^19 eV. Field data have events above 10^18.5;
the MC does not (S.1).

C.6 [PhD] **Hybrid events.** Correlate the per-event asymmetry parameter with the FD X_max of hybrid
events over the Infill (Coihueco/HEAT), event by event, in data: the direct test of the X_max
interpretation of Ch. 5, which today is a hypothesis.

Expectation: at 10^17.5–18 eV a per-event A1 alone will not discriminate mass. More likely uses are
as one input of a multivariate per-event estimator (with N_μ, the SD asymmetry, the risetime), at
the highest energies, or through the hierarchical model. The per-event fit is still worth building,
because it handles the core shift (fitted instead of corrected afterwards) and the selection
(censored likelihood) in the right way.

## 4. Own simulations (serve all fronts)

S.1 [ICRC] **More energies and primaries.** The library stops at 10^18 eV, while the headline Phase
II cell is 18.0–18.5; a helium sample at 18.0–18.5 (12 ADST files) exists and was not used (Ch. 4).
More energies are also needed for b(E) (A.1) and for the mass study (A.3); EPOS-LHC-R is in the
production and unused.

S.2 [PhD] **Dedicated CORSIKA runs with production-level information**, in the spirit of Cazón's
work: muon momentum distributions, transverse momenta and production heights, per particle. This
is what the earlier fast-MC attempt lacked (`Scripts/Intento Toy Model para Inversion Fallido/`:
the ADST only has the ground footprint). With it, the kinematic production and transport model of
thesis Ch. 6 ("Perspectiva") becomes possible: F(X, E, p_t) → Cazón's transport → detector responses,
thresholds and station selection, comparing amplitudes, not only signs. It also allows a direct test
of the kinematic-divergence term of the Ch. 3 toy model.

S.3 [PhD] Simulations above ~70° for the geomagnetic effect.

## 5. Blocking for the ICRC, independent of the fronts

X.1 [ICRC] **GAP 2026-041 is superseded on the SD inversion.** Its conclusions (Aug 2026)
attribute the inversion to the kinematic divergence of low-energy muons and to the side walls and
track lengths of the tank. The final thesis says otherwise: in Ch. 3 the divergence favours the late
region only above p* ≃ 2QD/r, which is rare at large r, and the tank geometry does not change the
asymmetry of the muon signal; in Ch. 6 the inversion disappears over all stations. Write an update
or a second note, and do not quote GAP 2026-041's explanation in the proceeding.

X.2 [ICRC] **Second GAP note on the core-reconstruction bias**: skeleton in
`GAP_Notes_Latex/[UNFINISHED]GAP_Core_REC/main.tex`, no content yet. Material: the talk and
`claude_work/charla_colaboracion_2026/figuras_charla.py` (blocks `core`, `rec_geometry`).

X.3 [ICRC] **Event-level bootstrap everywhere**: Dense Ring A1 and S, core shift b (A.6), Phase II
profile (0.063 ± 0.017 with SEM errors becomes ± 0.022, 2.8σ; see
`claude_work/charla_colaboracion_2026/revision_datos_campo/`).

X.4 [ICRC] **Fit quality in field data**: 14.5% of the data cells have χ²/ndf > 2 (10 of 69),
against 3–10% in the MC and about 4% expected for ndf = 9. Understand it before quoting a global
significance.

X.5 [ICRC] **Field-data systematics**: energy scale, Phase I vs Phase II (cell-by-cell
χ² = 103/53), counters with 1–7 modules vs 3 in the MC, azimuthal exposure (similar in data and
MC), the 55–65° band outside the standard energy calibration, the counting bias in data.

## 6. Other open lines [PhD]

- Counting reconstruction: the direction-dependent over-counting explains the Dense Ring REC–MC gap
  up to about 35°; above, half to two thirds; the remnant is open. Part of it may be the estimator
  (the mean of (REC − MC)/MC is biased upward at small N_MC).
- Correlation of A1 with X_max (proposed interpretation of the p > Fe ordering and of the energy
  trend; not tested).
- Effect of the muon deficit of the hadronic models on the analysis.
- Make the Ch. 3 toy model quantitative, or replace it with S.2.

## 7. Small inconsistencies found while preparing the talks [fix]

- Thesis Fig. 6.4.2 caption says 40–60° and 750–1050 m; the code, abstract and conclusions use
  50–60° and 750–1250 m.
- The script that drew the Phase II profile did not exclude the 2022 commissioning period
  (17 events): 0.0627 ± 0.0167 with them, 0.0623 ± 0.0168 without.
- Thesis Table 6.2.1: β is the local slope inside the 450–600 m bin (reproduced: 2.96, 2.72, 2.52);
  `Scripts/Cap5_corrimiento_nucleo.py` fits 300–650 m and gives 2.63, 2.46, 2.37. The recomputed A1
  values differ from the table by ≤ 0.001.
- In the regenerated Dense Ring fit-quality figure the SD χ²/ndf reaches ~8, not ~10 as in the text.
- `Analisis_Asimetria_DatosCampo_Cap7.py` still says it feeds `07_datos_reales.tex`, which no longer
  exists; `README.md` cites SIBYLL 2.1 / QGSJET-II-04.
- `ADST_Alexey_module_v9` and `v11` were archived in `~/Github/procesado_viejo/` (31 Oct 2026); the
  scripts that read them need the archive extracted (the talk scripts take `TALK_MC_ROOT`).
