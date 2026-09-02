# Verification of Version_Vieja's kinematic-divergence derivation (Eq. 9)

## Revision note (this pass)

This file supersedes the previous version of itself. The prior pass mixed two different
geometric approximations — Cazón (2012)'s exact $\alpha(r,D,\theta,\zeta)$ relation
together with Version_Vieja's own small-angle $d(\phi)\approx D\mp r\sin\theta$, which is
internally inconsistent with Cazón's own $\alpha$ (see "Geometry fix" below) — and it
read Bertou & Billoir (GAP-2000-017) and Luce et al. (ICRC-2021, #435) only in summary.
Both are now read in full and cited directly; both changed the numbers and, in Luce's
case, the framing of the whole section. The corrected calculation is
**stronger**, not weaker, than the original conclusion. New material: §"Cross-check
against Luce (2021)", §"Geometry fix", and a full replacement of the tank/side-wall
section, which previously endorsed GAP-2026-041's Sec. 6 track-length argument without
checking it quantitatively — that argument turns out to be wrong in sign.

## Prompt for this check

Following up on the familiarization pass (`thesis_review_familiarization_notes.md`), the author pushed back that the tank-volumetric confound raised there doesn't take away from the mathematical explanation of the kinematic-divergence effect itself, and relayed a specific comment from the thesis director on `[Version_Vieja]`'s Eq. (9):

> Es cierto que mirando este termino parece que cuando la diferencia angular es alta, que es para lo muones de baja energia, tambien pasa que la energia E es mas baja: los términos cinemáticos de "ganancia" solo son grandes cuando |α_early − α_late| es apreciable (i.e., α moderado), y E/(cQ) es apreciable (E ≳ pocos GeV??). Ninguna de estas dos condiciones se satisface simultáneamente para Población B. O al menos no queda claramente demostrado. Pero tambien hay que recordar que ahora el termino de la fraccion de cosenos tambien ayuda a la parte cinematica... vale la pena destacar que esto podria pasar pero que en la practica no pasa...

Task: check the math, reproduce it, verify the logic, consult the allowed bibliography (and beyond, if needed) to support or contradict, and report as far as the analysis can go.

## Setup

Version_Vieja §2.2 derives (Eqs. 4–9), for a fixed production distance $D$ along the shower axis, the ratio of ground muon density in the late vs. early azimuthal region at fixed radius $r$:

$$\frac{S_{late}}{S_{early}} \approx \underbrace{\left(\frac{d_{early}}{d_{late}}\right)^2}_{\text{spatial, always}<1} \cdot \underbrace{\left(\frac{\cos\alpha_{late}}{\cos\alpha_{early}}\right)}_{\text{phase-space, always}>1} \cdot \underbrace{\exp\!\left(\frac{(\sin\alpha_{early}-\sin\alpha_{late})E}{cQ}\right)}_{\text{exponential, always}>1,\text{ grows with }E}$$

with $\alpha_{early}>\alpha_{late}$ the geometrically required emission angles to reach radius $r$ in the early/late directions from a point source at distance $D$, and $Q$ the transverse-momentum scale of $dN/dp_t\propto p_t e^{-p_t/Q}$.

## Symbolic re-derivation

Re-derived $dN/d\Omega$ from $dN/dp_t\propto p_t e^{-p_t/Q}$ and $\sin\alpha\simeq p_t/E$ (see `verificacion_eq9_kinematic_divergence.py`; `sympy` is not part of this repo's `venv` per CLAUDE.md §10, so the script does the symbolic check with `sympy` if available and otherwise falls back to the equivalent hand derivation — nothing was installed into the shared environment): matches the paper's own Eq. (8), $dN/d\Omega\propto\cos\alpha\, e^{-E\sin\alpha/Q}$ (up to an $E^2$ prefactor absorbed/dropped in the paper). The algebra is correct.

$d/dE$ of the exponential factor is $\dfrac{\sin\alpha_{early}-\sin\alpha_{late}}{Q}\,e^{(\ldots)E/Q}$, strictly **positive** whenever $\alpha_{early}>\alpha_{late}$. So the exponential "gain" factor is monotonically *increasing* in $E$ — it is small near $E=0$ and only becomes large once $E$ is large enough (relative to $Q$ and the geometric angular separation). This confirms, algebraically, the director's point: the gain term needs $E$ to be *appreciable*, not small — it does not intrinsically favor low-$E$ muons.

## Geometry fix

The previous pass combined Cazón (2012) Eq. 7's $\alpha(r,D,\theta,\zeta)$ (exact) with Version_Vieja's own small-angle $d\approx D\mp r\sin\theta$ (approximate, and not the $d$ implied by Cazón's own $\alpha$). This version instead builds one self-consistent exact 3D geometry — production point at distance $D$ along the shower axis, ground point at shower-plane radius $r$, azimuth $\phi\in\{0,\pi\}$ — and derives $d$, $\alpha$, and the local zenith angle $\theta_{loc}$ from it directly (see `geometry()` in the script). The convention (production point leaning toward the *early* side, so $d_{early}<d_{late}$ and $\theta_{loc,early}<\theta_{loc,late}$) is fixed by matching both GAP notes' own qualitative statements, and reproduces Bertou & Billoir's Fig. 2/3 picture. This is used consistently for all three checks below.

## Numeric check with real parameters

Parameters, sourced as before:

- $Q\approx0.2$ GeV — from Cazón (2012) Figs. 7–9 (median $c p_t$ of produced muons, roughly energy-independent) and their explicit statement "a 10 GeV (1 GeV) muon typically will span a 1° (10°) outgoing angle with respect to the shower axis," which independently gives $cQ\approx0.17$–$0.18$ GeV.
- $D\approx5$–$10$ km — from Cazón's own worked numerical example ("A muon produced at $z=10$ km from ground...") and Bertou & Billoir (GAP-2000-017, §7): "[muons] come roughly in straight line from the end of the hadronic cascade, at an altitude around 5 km above the ground."
- $r=1200$ m, $\theta=35°$ — the far-core point of the $\theta\in[30°,40°]$ reference bin used in both GAP notes' Table 2, where the reported SD-Muon(MC) inversion is $A_1=-0.10$.

**Result — crossover energy $E^*$ where the pure-kinematic term flips from early-favoring to late-favoring** (i.e. where $S_{late}/S_{early}=1$), with the corrected exact geometry:

| $D$ | $E^*$ range over $Q\in[0.15,0.30]$ GeV |
|---|---|
| 5 km | 1.23 – 2.45 GeV |
| 7.5 km | 1.86 – 3.72 GeV |
| 10 km | 2.49 – 4.98 GeV |

These are ~15–20% *higher* than the previous pass's numbers — the exact geometry makes the effect harder to trigger, not easier. For **every** combination tried, $E^*$ sits at or above the UMD's own effective threshold, $E_\mu\gtrsim1\,\mathrm{GeV}/\cos\theta\approx1.22$ GeV at $\theta=35°$. This means: for muon energies at or below Population B's defining range ($E\lesssim1$ GeV), Eq. (9) evaluated with realistic parameters predicts a **positive** (early-favoring) net kinematic contribution — the *same* sign as atmospheric attenuation, not an opposing one. Only once $E$ climbs into the few-GeV range does the term turn late-favoring — an energy range the UMD's threshold does **not** exclude.

**$D$-scan (does $E^*$ ever drop into Population B's range?)**, $Q=0.2$ GeV, $r=1200$ m, $\theta=35°$:

| $D$ | 2 km | 3 km | 5 km | 7.5 km | 10 km |
|---|---|---|---|---|---|
| $E^*$ | 0.57 GeV | 0.95 GeV | 1.64 GeV | 2.48 GeV | 3.32 GeV |

So the narrative is not falsified for *all* production heights — only for the $D\gtrsim5$ km typically quoted in the cited literature. Rescuing it for Population B specifically would require an anticorrelation between production height and muon energy (very low-$E$ muons produced unusually close to the ground) that neither GAP note invokes or checks, and that isn't obviously true: pion/kaon decay kinematics don't strongly correlate decay height with the daughter muon's own energy in this way on their own — it would need to be demonstrated, not assumed.

**Sanity check at $r=450$ m** (near-core reference point, Table 2), corrected geometry: the model predicts a positive kinematic term across the whole 0.1–3 GeV range ($A_1\approx+0.04$ to $+0.12$ depending on $D$), consistent in sign and rough magnitude with the actually-reported SD-Muon(MC) value of $+0.05$. This confirms the model/implementation is sound — it just tells a different story than the paper's prose once evaluated at $r=1200$ m.

**On the cosine-ratio term** the director raised: confirmed real and always $>1$ (favors late, energy-independent), but numerically small at these radii — under 0.1% at $r=1200$ m with the corrected geometry — much smaller than the spatial $(d_{early}/d_{late})^2$ term ($\sim0.7$–$0.9$, a 10–30% early-favoring effect at these $D$). It does not rescue the low-$E$ regime.

## Cross-check against Luce et al. (ICRC 2021, #435)

Read in full this pass (`Bibliografia/ICRC2021_435.pdf`; cited as `Luce_ICRC2021` in both GAP notes' `bibliografia.bib`, identical entry in both). This is the decisive independent check, for two reasons.

**First, it already publishes the same mechanism, with the sign resolved correctly.** Their §2.2 models the geometrical effect with $\Delta\Omega\propto1/d^2$ and an angular distribution function $\mathrm{ADF}(\delta)\propto(\delta/\delta_0)^{-\gamma}$, giving (their text, unnumbered equation, §2.2, referencing their Ref. [6] for the full derivation) an asymmetry amplitude

$$\alpha \propto 2-\gamma+d(\theta)/\lambda,$$

and they state explicitly: "at large distances, the value of the exponent $\gamma$ of the ADF can be large enough to compensate the attenuation and produce a negative amplitude of the asymmetry." This is term-for-term Version_Vieja's Eq. (9): $+2$ is the $(d_{early}/d_{late})^2$ factor, $-\gamma$ is the angular/kinematic gain, $+d/\lambda$ is attenuation. Version_Vieja's exponential ADF is a special case, with a *local* logarithmic slope $\gamma_{eff}=E\alpha/(cQ)$ instead of Luce's constant $\gamma$ — which is exactly what exposes the energy-dependence the director flagged, and Version_Vieja re-derives it from scratch (§2.2) citing `Luce_ICRC2021` only for the *observation* of the SD inversion (Version_Vieja Introduction), never as prior art for its own model. Reproducing $2-\gamma_{eff}$ numerically (script, using the mean of $\alpha_{early},\alpha_{late}$) gives a sign flip at essentially the same $E^*\approx2.5$ GeV found above at $D=7.5$ km — an independent confirmation from a differently-parametrized model in an already-refereed proceedings paper.

**Second, and previously missed entirely: Luce's own simulated data directly measures the muon-only amplitude, and it does not support Version_Vieja's magnitude.** Their §2.2/Fig. 3 (EPOS-LHC, proton, $\theta=15$–$55°$, out to 2 km) states plainly: "the amplitude for the muonic component is almost null ($\le0.05$)." Their Fig. 3 (left) shows the muon points scattered around zero with large error bars, never approaching $-0.10$. GAP-2026-041's own Table 2 reports SD-Muon(MC) $=-0.10$ at $r=1200$ m — twice Luce's own stated ceiling, in a note that cites Luce as supporting evidence. This is a second, independent tension beyond the sign argument above (see also "Tension with cited sources" in the familiarization notes for the companion issue with Bertou & Billoir's own total-signal number).

## Why the paper missed this

Version_Vieja's own text around Eq. (9) never computes $E^*$. It asserts that the cosine and exponential gains "easily overcome" the spatial $1/d^2$ loss because "hadronic collisions overwhelmingly produce particles... at small emission angles," then cites the *observed* SD sign inversion itself as confirmation that this gain dominates — which is circular: the thing to be explained is used as evidence that the explanation is correct, without ever independently checking at what $E$ the crossover actually occurs, or whether that $E$ overlaps with the "Population B" (low-$E$) range invoked in the surrounding prose. It also never engages with Luce (2021) §2.2 as a quantitative predecessor, despite citing the same paper elsewhere.

## Verdict

The director's skepticism is not merely "not clearly demonstrated" — a direct evaluation of the paper's own equation, using exact geometry and parameters sourced from its own cited references, shows the *opposite* sign from the narrative for most of Population B's actual energy range, with the crossover to late-favoring behavior landing at or above the UMD's own threshold for every $D\gtrsim5$ km tried. This is corroborated independently by Luce (2021)'s own published model and its own simulated muon-component amplitude. It is a stronger and more specific problem than the tank/volumetric confound raised in the first pass — it is internal to the kinematic argument itself, independent of any detector-geometry effect, and it means the argument silently duplicates (and gets a sign wrong relative to) already-published, refereed work.

**Caveats:**
- This uses the same idealized single-point-production ($D$ fixed) geometry that both Cazón's formula and Version_Vieja assume; real muon production is spread over a range of depths (Cazón's $h(X)$, Fig. 3), not a single point. A production-height-integrated calculation could shift $E^*$, and the $D$-scan above shows this matters: $D\lesssim2$–3 km brings $E^*$ below the UMD threshold.
- $Q$ and $D$ were never pinned to explicit numbers in either GAP note; the values used here are independently sourced from the cited literature and bracketed generously (0.15–0.30 GeV, 5–10 km) — the qualitative conclusion (crossover near/above UMD threshold for $D\gtrsim5$ km) is stable across that whole bracket.
- This checks only the pure-kinematic/geometric term in isolation, as the director's comment does — not the full observed asymmetry (which also includes attenuation and, see below, the tank/track-length effect — which this pass shows does *not* rescue the narrative either).

## Clarification on "is the interpretation correct"

Following up, the author asked whether this means "the physical interpretation and analysis are correct" (modulo needing simulation to pin down exactly when the effect kicks in). Worth being precise about what is and isn't confirmed, since these are two different claims:

1. **The general mechanism categories and the algebra are confirmed.** Attenuation, geometric flux projection, and kinematic divergence are all real, independently derivable effects; the derivation from $dN/dp_t\propto p_t e^{-p_t/Q}$ to Eq. (9) is algebraically correct; the qualitative logic — collimation grows with energy, low-energy muons have broader angular spread — is standard and matches Cazón (2012) exactly, and matches Luce (2021)'s independently published $2-\gamma+d/\lambda$ model.
2. **The specific causal claim is not confirmed, and is contradicted in sign over most of the relevant range, by two independent checks.** The claim that *Population B specifically* (the low-energy, sub-GeV muons) produces the late-region excess, and that the UMD's ~1 GeV threshold "collapses this contribution to a negligible level," is what both the direct numeric check and the Luce cross-check argue *against*. For essentially all of Population B's own energy range (below $E^*$, which sits at or above the UMD threshold for realistic $D$), Eq. (9) predicts an *early*-favoring contribution, the same sign as attenuation — and Luce's own simulated muon amplitude never reaches the magnitude Version_Vieja/GAP-2026-041 report for the same observable.

So the appropriate caveat is not "needs simulation to see when it happens" (which implies the effect is real and just imprecisely located) but something closer to: *the paper's own equation, evaluated with parameters from its own cited sources, points at a different population than the one named as responsible, and its own cited reference's simulated muon-only amplitude does not reach the magnitude reported for the same quantity.* A dedicated simulation (real per-particle production kinematics, not the point-source toy geometry used here) could in principle still vindicate the original narrative for some sub-range of $D$ — the caveats above are exactly what such a simulation would need to resolve — but as things stand, neither the equation nor the cited literature supports it as written.

## The 3D SD tank vs. 2D UMD: does the side-wall/track-length effect rescue the argument? No.

Read Bertou & Billoir (GAP-2000-017) in full this pass (previously only summarized). This section replaces the previous pass's conclusion, which endorsed GAP-2026-041 Sec. 6's track-length argument without checking it quantitatively. It does not survive the check.

**The physical setup.** Auger's SD stations are Cherenkov *tanks* — cylindrical volumes of water with a top surface and a vertical side wall — not flat scintillator planes. Bertou & Billoir derive the resulting asymmetry from the same $(p_r,p_z)$ projection formalism used for their $\mathcal{A}_{geo}$ term (their §6):

$$\mathcal{A}_{side} = \sqrt{\left(\frac{p_z}{p_r}\right)^2\sin^2\theta - \cos^2\Phi\sin^2\theta} \;+\; \frac{p_z}{p_r}\cos\Phi\sin2\theta$$

With their sign convention ($p_z<0$ downward, $p_r>0$), the second term is **positive** for $\Phi\approx\pi$ (late region): "we can expect an *increase* in the signal from the $(p_z/p_r)\cos\Phi\sin2\theta$ term for $\Phi\approx\pi$. Therefore, the 'late' region is enhanced with respect to the 'early' one." Top entries are favored early, side entries are favored late.

**But their own conclusion for muons is compensation, not inversion — and this is a factually different claim from what GAP-2026-041 attributes to them.** Their §6, verbatim: "the signal of a muon is roughly proportional to the length of water crossed, the side signal per muon will be much stronger than the top one (the factor 2.4 being reversed). This compensates the surface factor, and **we expect the 'early' muonic signal to be the same as the 'late' one**." Their own quantitative MC check (§6–7, Fig. 6, $10^{20}$ eV, $\theta=30°$) shows the *total*-signal late/early ratio flattening at **$\approx0.79$–$0.82$ out to 2.4 km** — i.e. $A_1\approx+0.11$ to $+0.13$, staying positive, never crossing zero — down from a top-surface-only ratio around 0.47–0.52 at the same distances. Their §7 explicitly caps the total signal asymmetry at "less than a factor of 1.4 at 40°" (i.e. $|A_1|\lesssim0.17$), even under the older, buggy QGSJET showers that gave their worst case. **Nothing in GAP-2000-017 predicts a sign inversion of the muonic signal.** GAP-2026-041 §6 ¶3 cites this reference for a mechanism that "contributes negatively to the overall harmonic asymmetry" and helps drive the SD inversion to $A_1=-0.10$ — that is an extrapolation past what the cited source establishes, structurally the same kind of over-claim that got Version_Vieja's §2.2 cut.

**Quantitative check of the track-length claim itself (this pass, not in B&B or GAP-2026-041): it is exactly zero, not negative, by a general theorem.** For a parallel beam of unit flux crossing a convex body, the Cauchy mean-chord relation gives the total path length integrated over all crossing particles as $F_\perp\cdot V$ (incident flux perpendicular to the beam, times the body's volume) — **independent of incidence angle**, because the projected-aperture gain and the mean-chord-length gain cancel exactly. Applied to the WCD ($R=1.8$ m, $H=1.2$ m; projected-area ratio $\pi R^2/(2RH)=2.36$, matching B&B's quoted 2.4): the tank's **muon VEM response is angle-independent, exactly**. Using the exact geometry above at $r=1200$ m, $\theta=35°$, $D=7.5$ km ($\theta_{loc}=24.8°$ early / $43.2°$ late):

| detector response | $A_1$ (pure geometry, no attenuation/kinematics) |
|---|---|
| flat horizontal plane (UMD-like) | $+0.109$ |
| WCD tank, particle count | $+0.031$ |
| WCD tank, muon VEM (track-length weighted) | $0.000$ (exact) |

The tank **suppresses** the flat-plane geometric term toward zero — from $+0.109$ (what the UMD retains) down to $+0.031$ (count) or exactly $0$ (VEM) — it does not reverse its sign. The $1/\cos\theta_{loc}$ track-length gain GAP-2026-041 invokes for top-entering late-region muons exactly cancels the $\cos\theta_{loc}$ aperture-projection loss it's layered on top of; it is not an "additional artificial enhancement," it is the other half of a ratio that is identically 1. **Neither of GAP-2026-041's two offered mechanisms (kinematic-divergence attribution, §6 ¶2; volumetric/track-length, §6 ¶3) is supported in the direction claimed by this pass's quantitative check.**

**A caveat, symmetric to the one above:** both B&B's side-wall derivation and this pass's Cauchy-theorem check are toy calculations for an idealized cylinder and a uniform parallel beam; the real muon flux at a tank has some angular spread of its own (from the kinematic-divergence mechanism discussed above), which is not accounted for here and could reintroduce a small angle-dependence. B&B's own explicit MC validation (§5, Fig. 4) checks only the EM ground-density projection, not the muon side-wall claim, which is asserted from the projected model alone. So this is not a closed case — but the burden has shifted: GAP-2026-041's specific claim that the track-length term is negative is now contradicted by both the cited reference's own numbers and an exact independent theorem, not merely unconfirmed.

## What is actually established, going into the next task

Both GAP-2026-041's offered explanations for the SD inversion — the kinematic-divergence attribution inherited from Version_Vieja, and the new volumetric/track-length argument — point the wrong way when checked quantitatively against the note's own cited sources. Meanwhile, the observed inversion in the MC (Table 2, $A_1=-0.10$ at $r=1200$ m for SD-Muon(MC)) is presumably real (it's the note's own simulation output, not itself in question) but its magnitude exceeds what either Luce (2021) or Bertou & Billoir (2000) would predict for a purely geometric/kinematic origin. This leaves the SD inversion's physical origin more open than either GAP note states, and raises the further, previously unexamined question of whether the *UMD's* own asymmetry is as clean as claimed — see the companion familiarization notes for the flat-plane $A_{geo}$ and overburden-threshold estimates, which are the same order of magnitude as the measured UMD $A_1$.

## Reproducibility

Full derivation, exact geometry, $D$-scan, Luce cross-check, and tank/threshold calculations: `verificacion_eq9_kinematic_divergence.py` (same folder; run with the repo's `venv`: `venv/bin/python claude_work/gap_notes_asimetrias_review/verificacion_eq9_kinematic_divergence.py`; needs `numpy`, `scipy`; `sympy` optional, not installed in this repo's venv).
