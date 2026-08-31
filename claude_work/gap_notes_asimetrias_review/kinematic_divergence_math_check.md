# Verification of Version_Vieja's kinematic-divergence derivation (Eq. 9)

## Prompt for this check

Following up on the familiarization pass (`thesis_review_familiarization_notes.md`), the author pushed back that the tank-volumetric confound raised there doesn't take away from the mathematical explanation of the kinematic-divergence effect itself, and relayed a specific comment from the thesis director on `[Version_Vieja]`'s Eq. (9):

> Es cierto que mirando este termino parece que cuando la diferencia angular es alta, que es para lo muones de baja energia, tambien pasa que la energia E es mas baja: los términos cinemáticos de "ganancia" solo son grandes cuando |α_early − α_late| es apreciable (i.e., α moderado), y E/(cQ) es apreciable (E ≳ pocos GeV??). Ninguna de estas dos condiciones se satisface simultáneamente para Población B. O al menos no queda claramente demostrado. Pero tambien hay que recordar que ahora el termino de la fraccion de cosenos tambien ayuda a la parte cinematica... vale la pena destacar que esto podria pasar pero que en la practica no pasa...

Task: check the math, reproduce it, verify the logic, consult the allowed bibliography (and beyond, if needed) to support or contradict, and report as far as the analysis can go.

## Setup

Version_Vieja §2.2 derives (Eqs. 4–9), for a fixed production distance $D$ along the shower axis, the ratio of ground muon density in the late vs. early azimuthal region at fixed radius $r$:

$$\frac{S_{late}}{S_{early}} \approx \underbrace{\left(\frac{d_{early}}{d_{late}}\right)^2}_{\text{spatial, always}<1} \cdot \underbrace{\left(\frac{\cos\alpha_{late}}{\cos\alpha_{early}}\right)}_{\text{phase-space, always}>1} \cdot \underbrace{\exp\!\left(\frac{(\sin\alpha_{early}-\sin\alpha_{late})E}{cQ}\right)}_{\text{exponential, always}>1,\text{ grows with }E}$$

with $\alpha_{early}>\alpha_{late}$ the geometrically required emission angles to reach radius $r$ in the early/late directions from a point source at distance $D$, and $Q$ the transverse-momentum scale of $dN/dp_t\propto p_t e^{-p_t/Q}$.

## Symbolic re-derivation

Re-derived $dN/d\Omega$ from $dN/dp_t\propto p_t e^{-p_t/Q}$ and $\sin\alpha\simeq p_t/E$ (sympy, see `Scripts/verificacion_eq9_kinematic_divergence.py`): matches the paper's own Eq. (8), $dN/d\Omega\propto\cos\alpha\, e^{-E\sin\alpha/Q}$ (up to an $E^2$ prefactor absorbed/dropped in the paper). The algebra is correct.

Checked $d/dE$ of the exponential factor: $\dfrac{\sin\alpha_{early}-\sin\alpha_{late}}{Q}\,e^{(\ldots)E/Q}$, strictly **positive** whenever $\alpha_{early}>\alpha_{late}$. So the exponential "gain" factor is monotonically *increasing* in $E$ — it is small near $E=0$ and only becomes large once $E$ is large enough (relative to $Q$ and the geometric angular separation). This confirms, algebraically, the director's point: the gain term needs $E$ to be *appreciable*, not small — it does not intrinsically favor low-$E$ muons.

## Numeric check with real parameters

Used Cazón et al. (2012)'s own *exact* geometric relation (their Eq. 7, $r=z/(\cos\zeta\tan\theta+1/\tan\alpha)$, more precise than Version_Vieja's small-angle $d(\phi)$ approximation) together with:

- $Q\approx0.2$ GeV — from Cazón (2012) Figs. 7–9 (median $c p_t$ of produced muons, roughly energy-independent) and their explicit statement "a 10 GeV (1 GeV) muon typically will span a 1° (10°) outgoing angle with respect to the shower axis," which independently gives $cQ\approx0.17$–$0.18$ GeV.
- $D\approx5$–$10$ km — from Cazón's own worked numerical example ("A muon produced at $z=10$ km from ground...") and Bertou & Billoir (GAP-2000-017, §7): "[muons] come roughly in straight line from the end of the hadronic cascade, at an altitude around 5 km above the ground."
- $r=1200$ m, $\theta=35°$ — the far-core point of the $\theta\in[30°,40°]$ reference bin used in both GAP notes' Table 2, where the reported SD-Muon(MC) inversion is $A_1=-0.10$.

**Result — crossover energy $E^*$ where the pure-kinematic term flips from early-favoring to late-favoring** (i.e. where $S_{late}/S_{early}=1$):

| $D$ | $E^*$ range over $Q\in[0.15,0.30]$ GeV |
|---|---|
| 5 km | 1.06 – 2.11 GeV |
| 7.5 km | 1.56 – 3.11 GeV |
| 10 km | 2.06 – 4.13 GeV |

For **every** combination tried, $E^*$ sits at or above the UMD's own effective threshold, $E_\mu\gtrsim1\,\mathrm{GeV}/\cos\theta\approx1.22$ GeV at $\theta=35°$ — and in most cases well above it. This means: for muon energies at or below Population B's defining range ($E\lesssim1$ GeV), Eq. (9) evaluated with realistic parameters predicts a **positive** (early-favoring) net kinematic contribution — the *same* sign as atmospheric attenuation, not an opposing one. Only once $E$ climbs into the few-GeV range does the term turn late-favoring — an energy range the UMD's threshold does **not** exclude.

**Sanity check at $r=450$ m** (near-core reference point, Table 2): the model predicts a positive kinematic term across the whole 0.1–3 GeV range ($+0.03$ to $+0.10$ depending on $D$), consistent in sign and rough magnitude with the actually-reported SD-Muon(MC) value of $+0.05$. This confirms the model/implementation is sound — it just tells a different story than the paper's prose once evaluated at $r=1200$ m.

**On the cosine-ratio term** the director raised: confirmed real and always $>1$ (favors late, energy-independent), but numerically small at these radii — 0.1–2% at $r=1200$ m — an order of magnitude smaller than the spatial $(d_{early}/d_{late})^2$ term ($\sim0.6$–$0.76$, a 25–40% early-favoring effect). It does not rescue the low-$E$ regime.

## Why the paper missed this

Version_Vieja's own text around Eq. (9) never computes $E^*$. It asserts that the cosine and exponential gains "easily overcome" the spatial $1/d^2$ loss because "hadronic collisions overwhelmingly produce particles... at small emission angles," then cites the *observed* SD sign inversion itself as confirmation that this gain dominates — which is circular: the thing to be explained is used as evidence that the explanation is correct, without ever independently checking at what $E$ the crossover actually occurs, or whether that $E$ overlaps with the "Population B" (low-$E$) range invoked in the surrounding prose.

## Verdict

The director's skepticism is not merely "not clearly demonstrated" — a direct evaluation of the paper's own equation, using parameters sourced from its own cited references, shows the *opposite* sign from the narrative for most of Population B's actual energy range, with the crossover to late-favoring behavior landing uncomfortably close to (and often above) the UMD's own threshold. This is a stronger and more specific problem than the tank/volumetric confound raised earlier — it is internal to the kinematic argument itself, independent of any detector-geometry effect.

**Caveats:**
- This uses the same idealized single-point-production ($D$ fixed) geometry that both Cazón's formula and Version_Vieja assume; real muon production is spread over a range of depths (Cazón's $h(X)$, Fig. 3), not a single point. A production-height-integrated calculation could shift $E^*$.
- $Q$ and $D$ were never pinned to explicit numbers in either GAP note; the values used here are independently sourced from the cited literature and bracketed generously (0.15–0.30 GeV, 5–10 km) — the qualitative conclusion (crossover near/above UMD threshold) is stable across that whole bracket, but a narrower/better-justified choice could move $E^*$ further from or closer to the threshold.
- This checks only the pure-kinematic term in isolation, as the director's comment does — not the full observed asymmetry (which also includes attenuation and, per GAP2026_041 §5, the tank/track-length effect).

## Clarification on "is the interpretation correct"

Following up, the author asked whether this means "the physical interpretation and analysis are correct" (modulo needing simulation to pin down exactly when the effect kicks in). Worth being precise about what is and isn't confirmed, since these are two different claims:

1. **The general mechanism categories and the algebra are confirmed.** Attenuation, geometric flux projection, and kinematic divergence are all real, independently derivable effects; the derivation from $dN/dp_t\propto p_t e^{-p_t/Q}$ to Eq. (9) is algebraically correct (verified symbolically above); the qualitative logic — collimation grows with energy, low-energy muons have broader angular spread — is standard and matches Cazón (2012) exactly.
2. **The specific causal claim is not confirmed, and is contradicted in sign over most of the relevant range.** The claim that *Population B specifically* (the low-energy, sub-GeV muons) produces the late-region excess, and that the UMD's ~1 GeV threshold "collapses this contribution to a negligible level," is what the numeric check argues *against* — not merely "hasn't pinned down precisely." For essentially all of Population B's own energy range (below $E^*$, which itself sits at or above the UMD threshold in every parameter combination tried), Eq. (9) predicts an *early*-favoring contribution, the same sign as attenuation. The muons that do produce a late-favoring kinematic bias are the ones *above* the crossover — which the UMD does not filter out.

So the appropriate caveat is not "needs simulation to see when it happens" (which implies the effect is real and just imprecisely located) but something closer to: *the paper's own equation, evaluated with parameters from its own cited sources, points at a different population than the one named as responsible, and undermines the specific "UMD cleanly filters out the cause" framing.* A dedicated simulation (real per-particle production kinematics, not the point-source toy geometry used here) could in principle still vindicate the original narrative — the caveats below are exactly what such a simulation would need to resolve — but as things stand, the equation itself does not support it.

## The 3D SD tank vs. 2D UMD: the Bertou–Billoir side-wall/track-length mechanism

Requested as an addition, and well-supported directly from Bertou & Billoir (GAP-2000-017) §6–7, which both GAP notes cite as ref. [3] but which GAP2026_041 only summarizes briefly in its own §5.

**The physical setup.** Auger's SD stations are Cherenkov *tanks* — cylindrical volumes of water with a top surface and a vertical side wall — not flat scintillator planes. Some fraction of the detected signal comes from particles entering through the side wall rather than the top. Bertou & Billoir derive the resulting asymmetry directly from the same $(p_r,p_z)$ projection formalism used for their $\mathcal{A}_{geo}$ term (Eq. 2 of their paper, §4):

$$\mathcal{A}_{side} = \sqrt{\left(\frac{p_z}{p_r}\right)^2\sin^2\theta - \cos^2\Phi\sin^2\theta} \;+\; \frac{p_z}{p_r}\cos\Phi\sin2\theta$$

With their sign convention ($p_z<0$ downward, $p_r>0$), the second term $\frac{p_z}{p_r}\cos\Phi\sin2\theta$ is **positive** for $\Phi\approx\pi$ (late region), since $\cos\Phi\approx-1$ and $p_z/p_r<0$ make the product positive. Their own words: "As usually $p_z<0$ and $p_r>0$, we can expect an *increase* in the signal from the $\left(\frac{p_z}{p_r}\right)\cos\Phi\sin2\theta$ term for $\Phi\approx\pi$. Therefore, the 'late' region is enhanced with respect to the 'early' one." In plain terms: top entries are favored in the early region (particles there hit more perpendicular to the ground), side entries are favored in the late region (particles arrive more grazing relative to the tank).

**Why this affects muons and EM differently — and this is the key point for the UMD/SD comparison.** Bertou & Billoir work out both cases explicitly:

- **EM (electrons/photons):** signal is proportional to particle *count*, not path length, and the tank's top surface is 2.4× larger than its side surface. So even with more side-entries in the late region, the top-surface count still dominates the total, and the early/late asymmetry survives (weakened, not reversed): "the electrons and photons will give a strong asymmetry... the top signal will prevail over the side one, and we expect the electromagnetic signal to be higher in the 'early' region than in the 'late' one."
- **Muons:** signal is proportional to *path length crossed in water*, and a side-entering muon (near-horizontal relative to the tank) traverses a much longer path than a top-entering (near-vertical) one — the 2.4× area factor is "reversed" by an even larger path-length factor. Their own conclusion: "this compensates the surface factor, and we expect the 'early' muonic signal to be the same as the 'late' one." I.e., for muons specifically, the side-wall/track-length effect is strong enough to *erase* the early/late contrast from pure geometric projection — and, at large $r$/steep $\theta$ where geometric compression is more severe, there is no reason in this formalism why it should stop exactly at zero rather than overshoot into a net late excess, which is precisely what GAP2026_041 §5 argues.

**Bertou & Billoir's own quantitative MC check** (their §6–7, Fig. 6): for a 30° shower, "as the muonic part of the signal becomes more and more important (at large distance from the core), the asymmetry is compensated" — their own Fig. 6 shows the *top-only* signal asymmetry (ratio late/early climbing to ~0.8 at 2 km, i.e. a large early-favoring effect) reduced to a *total-signal* asymmetry that flattens around ~0.8 as well but from a much higher top-only baseline — concretely, their §7 reports the total asymmetry stays below ~10% at 30° and ~15% at 40°, down from a top-surface-only asymmetry that reaches a factor of ~5 for EM and ~2.5 for muons at 3 km/40°. This is the same physical mechanism GAP2026_041 revives 26 years later to explain why the *muonic* component of the modern SD signal can invert at large $r$, while the UMD — buried, essentially planar scintillator modules with no vertical side-wall exposure — has no analogous compensation term at all.

**A caveat worth flagging, symmetric to the one above:** Bertou & Billoir's side-wall derivation is, like Cazón's kinematic model, an analytically motivated *toy* calculation (a vertical shower rotated by $\theta$, using only the mean $(p_r,p_z)$ components, not a full per-particle inclined-shower simulation). Their own paper's explicit MC validation (§5, Fig. 4) checks the ground-density projection only for the EM component; the muon side-wall compensation claim in §6 is asserted from the projected model, not independently checked against real inclined-shower muon MC in their own paper. So neither of the two candidate mechanisms now on the table (Cazón kinematic divergence, Bertou-Billoir side-wall/track-length) has actually been validated against real per-muon production-and-transport kinematics in its original source — both are physically well-motivated extrapolations. That is precisely why GAP2026_041's "two compounding mechanisms, relative weight undetermined" framing is the honest one, and why a discriminating test (e.g., splitting the SD's own muon MC-truth by top-entry vs. side-entry, which the existing simulation framework should be able to produce directly) would settle more than further analytic argument on either side.

## Reproducibility

Full derivation and numeric scan: `verificacion_eq9_kinematic_divergence.py` (same folder; run with the repo's `venv`; needs `numpy`, `scipy`, `sympy`).
