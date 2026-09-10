# A unified model of the azimuthal muon-density asymmetry, and a verdict on the SD/UMD sign-inversion derivation

**Second correction notice, read this first.** The first version of this report did not read `claude_work/kinematic_divergence_explainer_and_thesis_updates/` in full, despite the task explicitly listing it as required reading — corrected in the second version, which credited that prior work and reproduced its result. That second version then proposed a "muon attenuation sign correction," sourced from Bertou & Billoir (GAP-2000-017)'s own muon-density-vs-depth measurement, as a real (if partial, ~20%) contribution toward the SD's missing physics. **That candidate is now retracted, not just re-quantified.** Bertou & Billoir's measurement is from a paper about the SD, using an essentially unthresheld muon population (near-zero energy cutoff, the SD's own sensitivity) — not the UMD's hard ~1.22 GeV threshold — and combining it into a UMD-side prediction, as the previous version did, mixed a population the UMD never sees into the UMD's own number. Worse: B&B's own text ("the total number of muons decreases, but their spread increases") describes a lateral-spreading phenomenon that is very plausibly the *same* physical effect Cazón's kinematic-divergence term already models — properly, spectrum-weighted, energy-differential — in the explainer notebook's §8 (already-credited prior work). If so, adding B&B's cruder, energy-integrated, decades-old number on top of the kinematic term already in the combined prediction double-counts the same physics, with the opposite sign, from the less reliable of the two sources. §3 below documents this candidate as a **retracted, dead-end lead**, in the same spirit CLAUDE.md §6 documents the Fast-MC attempt — so a future session doesn't retread it — rather than deleting the record of having tried it.

**Session scope.** This is the fifth pass on this question (four prior review passes live in `claude_work/gap_notes_asimetrias_review_v4/`; the explainer notebook and its chapter drafts are a later, separate body of prior work in `claude_work/kinematic_divergence_explainer_and_thesis_updates/`; this folder is a sixth, sibling piece of work). The brief was binary: either give a mathematical account of (1) why the SD muon-density asymmetry inverts sign at large core distance and (2) why the UMD is much less affected, or recommend cutting the analytic derivation from the thesis. A third option is offered only where the evidence genuinely demanded it — see the verdict below.

**What is already established by prior work (not this session), and properly credited here:**

- **The single most important number in this whole investigation**, from `explainer_kinematic_divergence_simulator.py` §8 / `spectrum_weighting_correction.html`: a *properly* spectrum-weighted (ratio-of-integrals, not average-of-ratios; ADF correctly normalised) kinematic-divergence term, combined multiplicatively with each detector's own geometric response, predicts **UMD +0.13 (observed +0.11 — a good match)** and **SD +0.19 (observed −0.10 — badly wrong, off by 0.29, and the wrong sign)**. Reproduced exactly in §2 below as a cross-check.
- This localises the unexplained physics specifically to the SD side. The UMD-as-kinematic-filter narrative in both GAP notes is "doubly unsupported": wrong population *and* wrong detector ordering.
- The already-drafted chapter revisions (`03_fenomenologia_DRAFT.tex`, `06_infill_DRAFT.tex`) already incorporate this corrected picture and the $A_{geo}$ sign fix.

**What this session adds, on top of that — after two rounds of self-correction:**

1. A single, unified closed-form model — Armbruster (GAP-2020-066) / Luce (ICRC2021-435)'s $a=(2-\gamma+d/\lambda)\varepsilon\tan\theta$ — validated term-by-term against the exact geometry, and the identification that Bertou & Billoir's $A_{geo}$ *is* the bracket's aperture term, not an addition on top of it (§1).
2. A candidate muon-attenuation-sign correction, sourced from Bertou & Billoir's own muon-density-vs-depth measurement — **tried, and retracted** (§3), for reasons that are themselves a useful, documented result: it conflates the SD's own detector/threshold context with the UMD's, and likely double-counts physics the kinematic term already models. This retraction is this session's most load-bearing finding, not a footnote.
3. Cazón (2012) explicitly rejects the single fixed-$(Q,D)$ approximation every version of this derivation, including the explainer notebook, uses (§4).
4. The first direct audit of the real MC parquet output, surfacing a real confound (zero exposure normalisation in the pipeline) and killing it with a direct causal test (§5).

All numbers are reproduced by `unified_model_verification.py` in this folder; raw console output is in `run_output.txt`. Sign convention throughout: $A_1>0$ means an early-region excess, matching both GAP notes and the explainer notebook.

---

## 1. The unified model: (i)–(iii) are one bracket, not three toy models

Armbruster (Bachelor thesis, KIT 2018; circulated as GAP-2020-066; Luce et al.'s Ref. [6], mislabelled "master thesis" in ICRC2021-435) derives, expanding the exact conical-apex geometry to first order in $\varepsilon=r/d(\theta)$:

$$
S(r,\psi) = S(r)\,(1+a\cos\psi), \qquad
a = \left(2-\gamma+\frac{d(\theta)}{\lambda}\right)\frac{r}{d(\theta)}\tan\theta
$$

Luce et al. (ICRC2021-435, §2.2) republish exactly this, compressed to $\alpha\propto 2-\gamma+d(\theta)/\lambda$. The "+2" is the geometric $1/d^2$ solid-angle projection, "$-\gamma$" is the kinematic/ADF divergence term, "$+d/\lambda$" is attenuation — three additive terms inside **one** bracket. This is the union (i)–(iii) asked for.

Checked against the exact 3D geometry, at the reference point ($r=1200$ m, $\theta=35°$, $D=7.5$ km):

| Bracket piece | Linearised (Armbruster) | Exact geometry |
|---|---|---|
| "+2" (solid angle, $1/d^2$) | $+0.224$ | $+0.216$ (3.7% rel. err.) |
| "+1" (flat-plane aperture) | $+0.112$ | $+0.109$ |
| WCD tank particle count | $+0.034$ | $+0.032$ |
| WCD tank muon VEM | — | $0.000$ exact (Cauchy mean-chord theorem) |

**Correction this forces on any UMD "instrumental floor" accounting:** Bertou & Billoir's $A_{geo}=\langle p_r/-p_z\rangle\tan\theta \approx (r/d)\tan\theta$ is numerically **identical** to the linearised "+1" aperture term (both $=0.112$). Any account that lists $A_{geo}\approx+0.11$ and a separate "flat-plane aperture" term as two additive contributions is double-counting — they are the same object.

---

## 2. Cross-check: reproducing the explainer notebook's decisive result

`explainer_kinematic_divergence_simulator.py` §8 fixes two errors in the original (v4) spectrum-weighted calculation: (1) it takes a *ratio of integrals* — weighting each region by how many muons of that energy actually *arrive there* — rather than an *average of ratios* weighted by the raw production spectrum (which discards the very selection effect being measured); (2) it keeps the angular distribution's own $k^2\equiv(E/cQ)^2$ normalisation, which cancels in the ratio at fixed $E$ but *not* under a spectrum integral, since it controls which energies dominate.

Corrected, the kinematic term alone gives $A_1\approx+0.16$ at the reference point ($\gamma=2.6$) — early-favoring, stable over four decades in $E_{max}$. **The decisive test varies only the detection threshold:** raising it from the SD's effective floor (0.155 GeV) to the UMD's (1.22 GeV at this angle) drives $A_1$ *down*, crossing zero near 2 GeV — the model predicts the UMD should be *less* early-favoring than the SD, the opposite of what's measured.

Folding in each detector's own geometric response (flat-plane $+0.109$ for the UMD, tank aperture $+0.031$ for the SD), reproduced independently in this session's script and matching exactly:

| $\gamma$ | UMD predicted | UMD observed | SD predicted | SD observed |
|---|---|---|---|---|
| 2.0 | $+0.110$ | $+0.11$ | $+0.151$ | $-0.10$ |
| 2.6 | $+0.133$ | $+0.11$ | $+0.191$ | $-0.10$ |
| 3.0 | $+0.145$ | $+0.11$ | $+0.205$ | $-0.10$ |

**This is the sharpest existing statement of the problem: the framework explains the UMD essentially correctly and fails only, specifically, and by a large amount ($\sim0.29$) on the SD.** `spectrum_weighting_correction.html` §10 already poses the sharp follow-up question this points to: is the SD's MC-truth muon count at the tank boundary (`GetNumberOfMuons()`) genuinely a count of incident muons, or does it carry a detector-level selection the toy model can't represent?

---

## 3. A retracted lead: the muon-attenuation-sign candidate, and why it doesn't survive

### 3.1 The candidate, as originally proposed

Neither GAP note, nor the explainer notebook (which explicitly omits an attenuation term), checks whether muon attenuation is early-favoring the way the EM component's is. Bertou & Billoir's own explicit MC (GAP-2000-017, Fig. 1, particles extracted at 900/1000/1100/1200 g/cm² of vertical atmospheric depth, for $10^{19}$–$10^{20}$ eV **vertical** proton showers) reports, verbatim: *"the muonic density is increasing, at least up to 1200 g.cm⁻² (of course, the total number of muons decreases, but their spread increases)… the contribution of muons reduces, and possibly reverses, the asymmetry."* This looked, at first, like a real, sourced, correctly-signed candidate: a late-region ground point samples a larger effective depth than an early-region one, and if muon density is still rising with depth at that point, the naive "attenuation always favors early" assumption is backwards for muons specifically.

### 3.2 Why it's retracted — two compounding problems, found by direct questioning

**Problem 1 — population/threshold mismatch (the decisive one).** B&B's Fig. 1 is drawn from AIRES's raw particle output at fixed atmospheric depths — essentially the *entire* muon energy spectrum down to the simulation's own low-energy cutoff, the same population the SD's water-Cherenkov tank is sensitive to (a near-zero energy threshold). The UMD only ever sees muons above $E_\mu\gtrsim1.22$ GeV at this reference angle. §2's own combined prediction already shows the kinematic-divergence term is highly threshold-sensitive — raising the effective threshold from the SD's floor to the UMD's flips its sign. B&B's curve, dominated by soft muons, is therefore almost certainly measuring a population the UMD's soil shielding removes entirely. Applying that same correction factor to *both* detectors' predictions — as the previous version of this report did — mixes a population the UMD doesn't sample into the UMD's own number. That is wrong independent of anything about detector material.

**Problem 2 — likely double-counting with the kinematic term already in the model.** B&B's own description — a declining total muon population spreading to a larger radius as depth increases — is a description of *lateral spread*, which is exactly the physical quantity Cazón's kinematic-divergence term (already included in §2's combination, spectrum-weighted properly) is a model of. If B&B's Fig. 1 trend and Cazón's kinematic term are two measurements of the same underlying phenomenon — plausible, given B&B's own wording — then adding B&B's factor on top of the kinematic term already present double-counts that physics, and does so with the *opposite* sign from the far more careful, energy-differential, already-validated calculation in §2, using the cruder of the two sources to overrule the better one.

**A third, compounding but secondary problem, from the first round of correction:** B&B's four calibration points (900–1200 g/cm²) sit above the reference point's own slant depths (568–708 g/cm², computed from the exact geometry) — any use of their fit requires both an extrapolation outside the calibrated range and an unjustified transfer across shower energies two orders of magnitude apart (B&B's $10^{19}$–$10^{20}$ eV vertical showers vs. the thesis's $10^{17.5-18}$ eV inclined ones), without correcting for how $X_{max}$ itself shifts with energy.

**None of these three problems is fatal on its own to using B&B's finding *for the SD alone, with the population and depth-range issues resolved*.** Together, applied the way the previous version of this report applied them, they are fatal to the specific $+0.14$/"$\sim20\%$ of the gap" numbers that version reported. Whether a population-matched, depth-correct, double-counting-checked version of this idea survives is now an open question for future work (§6, item 5) — not something this report can currently quantify or credit.

### 3.3 What this retraction establishes

**No candidate mechanism found across this session, or any of the five prior passes, survives scrutiny as an independent, correctly-attributed contribution to the SD gap — not even partially.** This is a stronger, cleaner negative result than the previous version of this report reached, and it makes the case for cutting the current thesis derivation more solid, not less: there is no remaining partial analytic account to point to, only the sharp, specific, already-known-from-prior-work open question about the SD's own observable definition (§2, §6 item 1).

---

## 4. Cazón's own $Q$ uncertainty

`cazon2012.pdf` never states a numerical $Q$; the commonly-used $Q=0.2$ GeV isn't supportable from this citation — Cazón's Fig. 8 median $cp_t\approx0.20$–0.22 GeV implies, via $\text{median}=1.678\,Q$ (verified here), $Q\approx0.12$–0.13 GeV, a factor-1.6 discrepancy. More consequentially, Cazón's own point is that a single $Q$ or $D$ is inadequate — $h(X)$ has FWHM $\sim600$–700 g/cm². This affects every number in §2, including the explainer notebook's own.

---

## 5. New this pass: a real-MC acceptance audit, run and killed

Direct pipeline audit (`Scripts/Procesamiento_ADST_v8-2.py`, `Scripts/plots_seccion_6.py`) found the A1 fit is an **unweighted mean per $\phi$ bin** over however many real 750 m-array stations happen to project into that bin — no exposure or livetime normalisation exists anywhere in the pipeline; quality flags (`module_status`, `is_sd_saturated`) are computed but never used as cuts; the SD and UMD columns have different NaN-drop patterns on nominally the same rows.

**Measured directly on the actual `icrc2025-test7` SIBYLL 2.3e proton MC** (read-only, existing parquet, no new processing job):

- Table 2 reproduces well: $A_1^{UMD}(r{=}1200)=+0.068$, $A_1^{SDmu}=-0.093$, vs published $+0.11/-0.10$.
- The **raw station count per $\phi$ bin** carries a large, $r$-growing modulation: $-0.02$ at $r{=}450$ m to $-0.32$ at 1200 m to $-0.58$ at 1600 m — a pure acceptance artifact, not a density measurement.
- Across 42 $(\theta,r)$ cells, this modulation is **strongly anti-correlated with the reported $A_1^{SDmu}$** ($r=-0.89$, $p=1.6\times10^{-15}$) and **uncorrelated with $A_1^{UMD}$** ($r=-0.08$) — exactly the pattern that would make a referee suspect the inversion is this artifact.

**The direct causal test kills this:** equalising the per-bin sample count via bootstrap resampling (300 draws, common minimum bin count) and re-fitting $A_1$ leaves both observables essentially unchanged at every radius tested — shifts of $+0.0002$ (r≈1200 m), $+0.0001$ (r≈800 m), $+0.0018$ (r≈1600 m, the worst bin), all inside the bootstrap's own statistical spread. **The correlation is real; it is not causal for this estimator.** This is a genuine, useful negative result: it closes off, with a direct measurement, a candidate fifth mechanism no prior pass tested — because none worked with the real parquet.

---

## 6. Q4 — What settles this, ranked

1. **[Already done, prior work] The corrected spectrum-weighted kinematic+geometry combination** (§2) — the sharpest existing statement of the problem, reproduced and verified here.
2. **[Done this session] Confirm the reported inversion is not a sampling artifact** (§5) — negative result, write up as a stated check in the thesis.
3. **[Sharpest open question, from `spectrum_weighting_correction.html` §10, not yet answered] Is `GetNumberOfMuons()` at the tank boundary genuinely a count of incident muons, or does it carry an unrepresented detector-level selection?** The framework explains the UMD and fails only on the SD — which makes the SD-side observable *definition* the first thing to re-examine. Needs reading the Offline reconstruction/simulation module, not the ADST reader.
4. **[Cheap, not done] Recompute the UMD's threshold-modulation term on real MC geometry** — needs per-station local incidence angle $\theta_{loc}$, not currently stored. ~10–15 lines added to the existing reader, no new simulation.
5. **[Speculative, blocked on resolving §3's problems first] Revisit a population-matched, depth-correct version of the muon-attenuation-sign idea** on `icrc2025-test7` — this would need muon density vs. slant depth measured separately *by energy band* (so the UMD-relevant, $E>1.22$ GeV population can be isolated from the soft population B&B's curve is dominated by), and a direct check of whether it's numerically distinct from Cazón's kinematic term once both are evaluated on the same footing. Only worth attempting if items 1–4 don't resolve the gap first — this session's experience is a caution against it being an easy win.
6. **[Blocked] Isolate muon-only VEM vs muon MC-truth count** — still blocked on an unconfirmed ADST-content question.
7. **[Expensive, last resort] Per-muon production kinematics** (the Fast-MC dead end in CLAUDE.md §6) — most expensive, least certain to be available.

---

## 7. Overall verdict and recommendation for the thesis text

**Direct answer to the director's binary question: cut the current derivation. This session did not find a way to avoid that conclusion — it found two candidates (a decisive one from prior work, a speculative one of its own) and neither survives.**

- **The derivation as currently written in `06_infill.tex` / GAP-2026-041 (Population B / kinematic-filter attribution, and the volumetric/track-length mechanism) should not go into the thesis as an explanation.** Now the conclusion of five independent passes: the mechanism doesn't just fail to reach the right magnitude, it predicts the *detector ordering backwards*.
- **The UMD side (Q2) is essentially already explained** by prior work this session verifies and credits: kinematic divergence, properly spectrum-weighted, plus the flat-plane $A_{geo}$ term reproduce the measured $+0.11$ to within $0.02$. No unidentified physics is needed there.
- **The SD side (Q1) remains genuinely open.** This session tried one new candidate and retracted it, for reasons documented in §3 rather than silently dropped — that retraction is itself useful, because it rules out (for now) a plausible-looking shortcut and leaves the one sharp, specific, actionable open question from prior work (§6 item 3: does the SD's own muon-count observable carry an unrepresented instrumental selection?) as the most promising next step, not a fifth analytic toy model.
- **Recommended reduced claim for the thesis:** present the SD inversion and UMD stability as a robust, real, MC result, shown not to be a pipeline artifact (§5). State that the UMD's asymmetry is well-reproduced by kinematics + flat-plane geometry — no unidentified physics needed. State plainly that the SD's inversion is not reproduced by the same framework, that no analytic mechanism checked across six passes of this investigation (including a specifically-tried muon-attenuation-sign correction, documented as a dead end) closes that gap, and that the sharpest remaining lead is a code-level question about the SD's own observable definition, not another analytic model.

**What I would NOT do:** claim the muon-attenuation-sign idea (§3) explains any part of the SD inversion, even partially. Two rounds of trying to quantify it — first overclaiming a "comparable to the gap" swing, then a "~20% of the gap" figure — both turned out to rest on errors a moment's more scrutiny caught. The lesson recorded here, and in the memory file this session's correction produced, is to check whether a borrowed number depends on the source detector's own construction (mass, threshold) before reusing it across detectors — not to keep re-quantifying a candidate that hasn't earned it.

---

## Reproducibility

`unified_model_verification.py` (this folder): `venv/bin/python claude_work/unified_asymmetry_model_v1/unified_model_verification.py`. §7 of the script still contains the B&B combination code, clearly labeled as a retracted/exploratory calculation (kept for reproducibility and so a future session can see exactly what was tried and why it was retracted, not because its numbers should be trusted). Full console output: `run_output.txt`. §5 reads the existing MC parquet at `/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/` (read-only; no processing job launched, per CLAUDE.md §3).

Prior work reused and credited, not superseded: `claude_work/gap_notes_asimetrias_review_v4/` (exact geometry toolkit, $E^*$ crossover, Cauchy mean-chord theorem) and, decisively, `claude_work/kinematic_divergence_explainer_and_thesis_updates/` (the corrected spectrum-weighted kinematic+geometry combination that is this whole investigation's sharpest result, and the draft chapter revisions already reflecting it).
