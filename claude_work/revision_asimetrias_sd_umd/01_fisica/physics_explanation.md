# What changed in the physical explanation of the SD–UMD asymmetry?

## The answer first

I did not discover an additional atmospheric interaction that creates a late-side muon excess. The new ingredient was **selection through the surface detector's response**. It can turn an early-favoring incident population into a late-favoring *mean muon count among retained stations*, without moving or creating any muons.

Your original three ingredients remain relevant: atmospheric survival, geometric projection, and kinematic divergence. However, they must be separated correctly. In particular, the Bertou–Billoir projection coefficient is not the same thing as the late-favoring angular-distribution effect.

This note explains the mechanisms, not their fitted magnitudes. It introduces no new toy-model calculation. The numerical tests, precise source audit and their limitations remain in [the full report](report.md).

Convention throughout: the same shower-plane radius is compared on the early side, \(\phi=0\), and late side, \(\phi=\pi\). Positive \(A_1\) means an early excess; negative means a late excess. “Late” is a spatial region here, not a label for delayed secondary pulses.

## 1. Atmospheric attenuation: what survives the extra path?

Compare a fixed population of produced muons propagating along an early and a late path. In the usual inclined-shower geometry, the late path is longer and traverses more atmosphere. Muons can decay in flight, lose energy, stop, or arrive below the energy needed to penetrate the soil.

These **passive survival and range losses favor the early side**. No sign reversal of muon absorption was introduced in the new analysis. Low-energy muons are generally more vulnerable to decay and range losses, but the contributing energy and production-distance distributions must be conditioned on the observation point.

For the electromagnetic cascade after its maximum, the extra depth generally depletes the ordinary EM component strongly. That supplies an early–late difference in the *tank's selecting signal*, even if the muon intensity changes much less. EM particles are also regenerated, so “every EM count measures only attenuation” is too strong.

Two qualifications matter for your earlier interpretation:

- An early UMD excess does **not**, by its sign alone, show that atmospheric attenuation dominates it. Geometric projection can have the same sign.
- A measured change of local muon density with atmospheric depth is not a pure survival probability. It includes lateral transport into/out of that radius, possible new production, and energy-cut effects. Adding that entire derivative as “attenuation” on top of a divergence calculation can count the spreading twice.

Thus the passive attenuation intuition is sound; the claims of dominance and of an independent negative attenuation term are not established.

## 2. Geometric projection: how much detector area does the muon flux see?

The local muon directions are not exactly parallel to the shower axis. Consequently, the ground plane intercepts the outward-moving flux differently on opposite sides of an inclined shower.

For the plane-projection effect, using an upward shower-axis coordinate and appropriate shower-normal crossing-flux weighting,

\[
A_{\rm geo}=\left\langle\frac{p_r}{-p_z}\right\rangle\tan\theta.
\]

For the usual outward-moving, descending population, \(p_r>0\) and \(p_z<0\). This contribution is **positive: early-favoring**. Making \(-p_z\) smaller does not turn a positive ratio negative. Inward radial momenta can exist, but a net negative signed radial-flow contribution must be demonstrated; it does not follow from low energy.

This directly contradicts the wording in the current thesis that a small longitudinal momentum makes the Bertou–Billoir term “explode” with negative sign. It also contradicts identifying that expression with the late-favoring ADF effect discussed next. If the divergence becomes large, the small-angle/first-harmonic approximation may itself fail; an extrapolation outside that limit is not evidence of an inversion.

A useful picture is a horizontal plate: for a common axial source, early-arriving trajectories are more vertical, so the plate presents a larger projected area to them. Merely projecting a circular footprint into an ellipse is not itself this effect: for an ideal parallel beam, a consistent shower-plane coordinate/area projection does not generate the claimed first harmonic.

### What changes for a water tank?

The tank has a top and side walls. A more inclined late-side trajectory sees less top area but more side area. The side contribution therefore opposes the top-only early preference. **That does not imply that their sum is late-favoring.** Their balance depends on direction and tank geometry.

There is another distinction between *counts* and *signal*. A through-going muon crossing more water produces more light, but the mean water path and projected aperture compensate for an ideal uniform through-going flux:

\[
A_{\rm projected}\,\langle\ell_{\rm water}\rangle=V_{\rm water}.
\]

This cancels that particular aperture dependence in the ideal muonic signal. It does not cancel the incident flux asymmetry, and it does not apply without qualification to stopping tracks or thresholded signals. It also does not create additional incident muons. Armbruster's original signal derivation uses this cancellation; the muon-count observable must instead retain its own aperture.

## 3. Kinematic divergence: which emission angles populate the same radius?

This is the genuine late-favoring possibility already present in your work.

Take a muon source on the shower axis. To reach a fixed radius:

- The early trajectory travels a shorter distance, so it needs a larger emission angle relative to the axis.
- The late trajectory travels farther, so it can reach the same radius with a smaller emission angle.

The angular distribution is usually denser closer to the shower axis. The late point therefore samples a more populated part of that angular distribution. **This angular-distribution contribution favors the late side.**

But a second effect acts simultaneously: the more distant late point suffers greater inverse-square dilution. That contribution favors the early side. For an illustrative fixed source and momentum, before aperture and survival are applied,

\[
\frac{\rho_{\rm late}}{\rho_{\rm early}}
=\underbrace{\left(\frac{L_{\rm early}}{L_{\rm late}}\right)^2}_{\text{favors early}}
\underbrace{\frac{f(\alpha_{\rm late})}{f(\alpha_{\rm early})}}_{\text{favors late if }f\text{ decreases}}.
\]

Here \(f=dN/d\Omega\). The **combined divergence/ADF effect has no universal sign**. A late excess requires the angular gain to exceed the spatial dilution and the other early-favoring contributions. Your description of the competing factors is physically meaningful; the assertion that the angular gain necessarily overwhelms the others is the unsupported step.

### Why “soft muons are more divergent” is not sufficient

Soft muons generally have broader angular distributions. But the asymmetry is controlled by the *relative change* of the distribution between two nearby angles, not just by its width. A broad, fairly flat distribution can change little between those angles. A narrower distribution sampled in its steep tail can change strongly.

The separable transverse-momentum law used in the previous calculations gives

\[
f(\alpha\mid p)\propto\cos\alpha\,
\exp[-(p/Q)\sin\alpha].
\]

At fixed geometry and fixed transverse-momentum scale, its exponential late/early gain grows with momentum, not with decreasing momentum. This statement does not determine a full shower's asymmetry: real production distances, energies and survival weights are correlated. It does show why one cannot deduce “soft muons cause the inversion, and the soil removes it” from angular width alone.

Also distinguish production energy from ground energy. A soft ground muon may have been produced with appreciably more energy. A UMD ground threshold cannot be substituted directly for a production-energy threshold.

## 4. The original physical effects in one expression

For a fixed illustrative source/momentum contribution, write the unselected count as

\[
N_d(\phi)\propto
\underbrace{P_{\rm survival}(\phi)}_{\text{passive attenuation}}
\underbrace{\mathcal A_d(\vartheta(\phi))}_{\text{detector projection}}
\underbrace{\frac{f(\alpha(\phi))}{L(\phi)^2}}_{\text{ADF and spatial dilution}}.
\]

For a shower, sum/integrate these contributions with the joint production distribution and detector-specific energy/range response. The factors multiply for each contribution; their harmonic amplitudes add only to first order when the modulations are sufficiently small.

This expression contains the three mechanisms you asked about. It contains no new atmospheric process. The inverse-square factor must not be added again if already included in the divergence calculation, and the plate-projection factor must not be added again after using the projected plate area.

With a local power-law ADF, the familiar bracket makes the separation visible:

\[
A_{1,d}\simeq
\left[\underbrace{2}_{\text{dilution}}
-\underbrace{\gamma_{\rm ADF}}_{\text{angular preference}}
+\underbrace{D/\lambda}_{\text{passive attenuation}}
+\underbrace{\kappa_d}_{\text{aperture}}\right]
\frac{r}{D}\tan\theta.
\]

This is a small-angle, fixed-source approximation with a passive exponential survival law, not a general fitted shower law. For an ideal plate the aperture coefficient is unity; for ideal through-going muon signal it vanishes after the chord cancellation; tank counts require their own coefficient. Armbruster's signal bracket has the inverse-square contribution, not an already-included plate-aperture contribution.

## 5. What I added: the same atmosphere can select different tank populations

Your plotted SD truth mean is calculated only for stations with a reconstructed SD partner. A tank's ability to enter that sample depends on its response to **both muons and the electromagnetic component**.

The physical interpretation to test is:

1. Early stations receive a larger EM contribution.
2. That EM contribution can help a station satisfy the signal/trigger conditions even when its local muon count is small.
3. Late stations receive less EM help.
4. Among late stations, retaining a station can then preferentially select those with a larger muon contribution.
5. Consequently, retained late stations can have a larger *mean muon count per retained station*, even when the unselected late-side muon intensity is smaller.

**There are not necessarily more muons on the late side. There can be fewer retained late stations, with those retained stations being more muon-rich.** This is the central distinction.

It is not a fluctuation caused merely by having unequal numbers of stations per azimuth bin. It changes *which particle populations* survive the selection. Nor does it mean EM particles were incorrectly counted as muons. The muon truth counts can be exact while the stations carrying those counts are selected through an EM-sensitive instrument.

The mathematical distinction is simply

\[
\underbrace{\mathbb E[N_\mu\mid\phi]}_{\text{before station selection}}
\ne
\underbrace{\mathbb E[N_\mu\mid\phi,\ \text{station retained}]}_{\text{plotted selected mean}}.
\]

**Established by the preceding raw-ADST test:** applying the station-presence condition changes the sign in the tested sample. **Physically motivated interpretation, not yet separately established:** the EM-help/muon-enrichment sequence above explains why such a condition can produce that direction of change. The audit has not isolated a particular trigger algorithm or demonstrated that EM help is the only contributor. The truth accessor itself is an upstream geometric muon counter, not a water-light counter.

Thus the new ingredient is *shower physics coupled to detector response and selection*, not a fourth propagation mechanism. Atmospheric attenuation can even participate indirectly: an early EM advantage can help generate a late excess in the selected muon mean. This does not reverse the sign of muon survival losses.

## 6. What this means for UMD

Soil removes the EM component and imposes an energy/range filter on muons. UMD also samples a different sensitive area and underground crossing population. These are genuine physical differences. They change the geometric, angular and survival weights, but they do not prove that geometric effects vanish or that attenuation must dominate.

The SD muons contribute directly to the tank signal used for station selection. Muons counted underground need not contribute to that same tank signal: a muon hitting a nearby buried module is not generally the muon that triggered the tank. Consequently, selection can correlate much more directly with the tank's own count than with the underground count. Correlations through the common shower and local particle density still exist; independence has not been established.

This is a plausible reason why the **selected SD count** can invert without a corresponding UMD inversion. It is not yet a complete causal explanation of the UMD coefficient. The UMD pilot found that untriggered scintillator truth is not populated in the relevant ADST summaries, so its pre-selection counterpart cannot be inferred by treating missing records as zero.

## 7. What to retain, and what to withdraw, from the old narrative

| Statement | Physical verdict |
|---|---|
| Extra passive propagation losses favor early over late. | Retain, for a fixed produced population. |
| Nonparallel muon trajectories generate a plane-projection effect. | Retain, with the signed-momentum convention. |
| A smaller emission angle can make the late point sample a denser angular population. | Retain. |
| That angular advantage must overpower spatial dilution. | Not established; it is a competition. |
| Small longitudinal momentum makes the usual outward-flow projection coefficient negative. | Incorrect sign argument. |
| Soil filtering proves the late-favoring contribution disappears in UMD. | Not established. |
| A negative SD truth-count harmonic proves negative unselected ground density. | Incorrect when station selection is uncontrolled. |
| A positive UMD harmonic proves attenuation dominates. | Not established from the sign alone. |

**Bottom line:** the old mechanisms can produce a genuine physical competition at ground. What the new work added was a demonstrated change of the sampled observable under detector selection. It did not establish a new atmospheric source of late muons, or prove that the old low-energy-divergence narrative explains this inversion.

## Sources and scope

The comparison above was checked against the current thesis Chapters 3 and 6, the prior [kinematic check](../../gap_notes_asimetrias_review_v4/kinematic_divergence_math_check.md), and the exact source audit in the [full report](report.md). The old documents contain claims that were subsequently corrected; citing them here identifies the argument under review, not blanket endorsement.

- Bertou & Billoir, GAP-2000-017, plane/top/side projection discussion: internal GAP note, used with explicit sign conventions.
- Armbruster, GAP-2020-066 / Bachelor thesis, §2.4, Eqs. (2.12)–(2.21): distinguishes particle counts from muon track-length signal. Its Eq. (2.33) is the signal bracket.
- Cazon et al. (2012), *Astroparticle Physics* 36, 211–223, §§2–4: production distributions and transport. The separable angular law above is an approximation, not the full correlated 2012 model. [DOI](https://doi.org/10.1016/j.astropartphys.2012.05.017)
- IceCube Collaboration (2022), *Physical Review D* 106, 032010, §IV.B, Eqs. (4)–(6): independently illustrates why track-length response and low-signal trigger efficiency must enter a tank-based muon analysis. It does not establish the specific Auger selection mechanism or license transferring IceTop thresholds to UMD. [Author manuscript](https://arxiv.org/pdf/2201.12635)

No thesis/GAP files were changed. No new simulation or magnitude scan was run for this explanation.
