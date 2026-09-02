# What actually happens with the SD, and why the UMD is less affected

## Why this file exists

The two prior notes (`kinematic_divergence_math_check.md`, `thesis_review_familiarization_notes.md`) are almost entirely negative: they show that Version_Vieja's kinematic-divergence attribution and GAP-2026-041's tank/track-length attribution both point the wrong way when checked quantitatively. The author read that and pushed back, correctly: a referee report that only says "your explanations are wrong" without offering an account of what *is* going on isn't finished, and the eventual goal of this line of work is a paper that explains what happens with the SD and why the UMD is measurably less affected. This file is that attempt — built from the same exact-geometry toolkit as the other two notes (`verificacion_eq9_kinematic_divergence.py`, sections 3-5), pushed further specifically in response to that request.

**Status of what follows: some of it is established (the tank/VEM result), some is a model-based inference with a stated uncertainty (the implied true-flux number), and the central mechanism — what actually makes the true muon flux late-favoring at large r — is not identified.** Read the last two sections first if short on time; they say plainly what is and isn't nailed down.

**v4 addition (Part 4):** the author asked directly for a candidate physical mechanism, checked against bibliography not yet used in this review. In-flight atmospheric multiple Coulomb scattering — sourced from Grieder (2010), a text already in the repo but never cited by either GAP note or the thesis — is the first mechanism found with the qualitatively correct sign. Quantified honestly, it is about an order of magnitude too small on its own; Part 4 explains why it isn't discarded anyway and what would settle it.

## Confirmed this pass, independent of anything in this file: the effect is physical

The author's own analysis — Dense Ring and Infill topologies, MC and REC geometry, four independent combinations — reproduces the SD-inverts/UMD-doesn't pattern consistently. That settles the question the two earlier notes had left open (whether the reported magnitudes might reflect a bug or a fragile MC-truth definition): they don't. What remains open is the physical origin, not the existence, of the effect.

## Part 1 — What the WCD tank actually does, worked through completely

### The exact result

For a parallel beam of muons (fixed arrival direction, number flux $F_\perp$ per unit area perpendicular to that direction) crossing a convex body, two quantities:

$$\text{count} = F_\perp \cdot A_\perp(\theta_{loc}) \qquad \text{mean chord} = V / A_\perp(\theta_{loc})$$

where $A_\perp(\theta_{loc})$ is the body's projected area as seen from the beam direction. This holds **region by region**, for whatever the true flux $F_\perp$ happens to be in that region — it does not require an azimuthally uniform flux. Multiplying:

$$\text{total path length} = \text{count} \times \text{mean chord} = F_\perp \cdot A_\perp(\theta_{loc}) \cdot \frac{V}{A_\perp(\theta_{loc})} = F_\perp \cdot V$$

The aperture term cancels **exactly**, at every angle. Since the WCD's VEM signal is (to good approximation, for relativistic muons well above minimum-ionizing threshold) proportional to path length in water, **the muon VEM signal is a clean, undistorted tracer of the true incident muon flux ratio.** The tank's own 3D geometry contributes zero net bias to it — not "suppresses toward zero," which is what the previous pass said; it is exactly zero, and this is a general result, not a special case of an idealized uniform-flux toy model.

This directly matches the physical intuition the author raised (grazing entries deposit more energy per particle — true, and never in dispute) while showing why it doesn't produce a net late-region excess in the *energy-weighted* signal: the number of grazing hits is correspondingly smaller (smaller projected aperture at the more extreme angle), and the two effects cancel exactly when summed over the whole beam. The per-particle intuition is correct; it's incomplete on its own.

### What does NOT cancel: the raw count

A raw particle count (no energy weighting) only carries the aperture term, not the compensating chord-length term:

$$\text{count ratio (late/early)} = \frac{F_{\perp,late}}{F_{\perp,early}} \times \frac{A_\perp(\theta_{loc,late})}{A_\perp(\theta_{loc,early})}$$

At the reference point (r = 1200 m, θ = 35°, D = 7.5 km), the tank's own aperture ratio gives $A_1 = +0.031$ — small, and *early*-favoring, i.e. it fights against an inversion rather than causing one. This is what `tank_response()` (§3 of the script) already established, restated here more precisely: the tank aperture is not a candidate cause of the count inversion — it's a small headwind against it.

### Backing out the true flux ratio

GAP-2026-041's Table 2 reports SD-Muon(MC) $A_1 = -0.10$ — a raw MC-truth count. Since count = flux × aperture, and the aperture factor here is +0.031 (early-favoring):

$$A_1^{\text{true flux}} \approx -0.13$$

The true incident flux has to be *more* inverted than the raw count shows, because the tank's own geometry is partially masking it. **This produces a falsifiable prediction that costs nothing new to check:** an isolated muon-only VEM signal (not currently reported separately in either GAP note — only total VEM and muon MC-truth count are shown) should, per the exact cancellation above, show a *larger* inversion than the muon count, not a smaller one. If it doesn't, something in this picture — most likely the assumption that all muons in a region arrive along one nominal direction, see the caveat below — is wrong.

**Caveat on the -0.13 number specifically (not on the cancellation theorem, which is exact):** it assumes every muon in a given azimuthal region arrives along a single nominal direction set by shower geometry alone. Real muons have their own angular spread around that nominal direction — which is exactly the kinematic-divergence effect — so the aperture factor computed here is a first-order approximation, not an exact deconvolution. A fully rigorous version would need to convolve the aperture response over the true per-region angular distribution, not a delta function at $\theta_{loc}$.

## Part 2 — Does kinematic divergence survive being done properly? No.

The obvious next move is: if the tank doesn't cause the inversion, does kinematic divergence explain the *true flux* being late-favoring, once correctly attributed (not to sub-GeV Population B, which §1 of the math-check note already ruled out, but to whatever energy range actually matters once you weight by the real muon spectrum)?

Tested directly (`spectrum_weighted_kinematic_A1()`, §5 of the script): take the same pure-kinematic ratio $\rho(E)$ derived and verified earlier, and average it over a power-law muon spectrum $dN/dE \propto E^{-\gamma}$ ($\gamma = 2.0$–$3.0$, bracketing Cazón's quoted production index and typical steepening after propagation losses):

| $D$ | $\gamma=2.0$, $E\in[0.05,20]$ GeV | $\gamma=2.6$ | $\gamma=3.0$ |
|---|---|---|---|
| 5 km | $A_1=-0.05$ | $A_1=+0.26$ | $A_1=+0.28$ |
| 7.5 km | $A_1=+0.17$ | $A_1=+0.20$ | $A_1=+0.21$ |
| 10 km | $A_1=+0.15$ | $A_1=+0.16$ | $A_1=+0.16$ |

Over every physically reasonable range, the spectrum-weighted term is **early-favoring** — the opposite sign from what's needed. It only flips sharply negative if the integral is extended to tens or hundreds of GeV, and that's not a physical result: $\rho(E) \sim e^{kE}$ with $k \approx 0.17\,\text{GeV}^{-1}$ at the reference point, which grows faster than *any* power-law spectrum falls, so the integral is formally divergent for an unbounded spectrum — a single hypothetical 200 GeV muon would formally outweigh $\sim10^{15}$ early-region ones in this toy model. That's the idealized single-production-point, single-slope-$Q$ model breaking down outside its domain, not a discovery.

**This retracts a specific hypothesis raised in conversation** — that a rare high-energy tail above the crossover $E^*$ might dominate a properly-weighted average and explain the inversion. Checked directly, it doesn't hold up. Kinematic divergence, as modeled by Cazón's parametrization and evaluated honestly rather than at a single convenient point, does not obviously produce a late-favoring net effect for a realistic muon spectrum at either detector.

## Part 3 — What that leaves: the true mechanism is not identified

Summing up every analytically-tractable candidate checked across both notes and this one:

| Candidate mechanism | Checked how | Result |
|---|---|---|
| Kinematic divergence, Population B attribution (Version_Vieja §2.2) | Exact crossover-energy calc | Wrong population — early-favoring below $E^*\approx2$–4 GeV |
| Kinematic divergence, spectrum-weighted | Power-law-averaged $\rho(E)$ | Still early-favoring over any bounded range |
| Tank/track-length (GAP-2026-041 §6¶3) | Cauchy mean-chord theorem, exact | Contributes exactly zero to VEM, not negative |
| Tank aperture on raw count | Exact tank geometry | Early-favoring (+0.031), not negative |

None of them produces a late-favoring net effect anywhere near the size needed. **The honest state of this investigation is that the true physical origin of the SD's inferred flux-level inversion (≈ −0.13 at the reference point) is not identified by anything derivable from the cited literature's analytic toy models.** This is a stronger and more useful statement than either GAP note makes — both assert a mechanism; the evidence assembled here says neither asserted mechanism survives, and nothing else analytic has been found to replace it.

That points toward needing real per-particle production kinematics (height, angle, and energy jointly, from actual CORSIKA output) rather than an idealized single-production-point, fixed-$Q$ analytic model — the same wall the abandoned Fast-MC toy model hit (CLAUDE.md §6), but arrived at now for a more specific reason: the analytic mechanisms have been excluded rather than simply not yet attempted. Whether that's worth revisiting, given the earlier attempt's data-availability problems, is a scope question for the group, not something this note can settle.

## Part 5 — Why the UMD looks cleaner: the best defensible answer available, stated as a hypothesis

Since the true late-favoring mechanism isn't identified, "the UMD filters out mechanism X" cannot currently be claimed — there's no confirmed X to filter. What *can* be defended, independent of that open question, is this:

The UMD carries two of its own instrumental terms, both robustly **early-favoring**, both derived from simple geometry/threshold facts about its construction rather than from any assumption about the unresolved flux mechanism:

1. **Flat-plane aperture** ($A_{geo}$-type projection): $A_1 \approx +0.109$ at the reference point.
2. **Azimuthally modulated overburden threshold** ($\theta_{loc}$ larger late $\Rightarrow$ higher effective $E_{thr}$ there): $A_1 \approx +0.11$ to $+0.22$ depending on the assumed spectral index.

Both are the *same kind* of quantity as the SD's own +0.031 aperture bias — small, geometric, provably early-favoring — except an order of magnitude larger, and (unlike the SD's tank) **not cancelled by anything**, because the UMD's headline observable is a raw particle count (digital scintillator hit counting), not an energy-integrated signal. There is no Cauchy-cancellation available to the UMD the way there is to the WCD's VEM — a thin, flat, particle-counting detector doesn't have the compensating "more counts are lost to a smaller aperture exactly as much as the survivors' path length grows" structure that made the WCD's VEM term vanish; it only has the aperture-loss half of that pair.

**The hypothesis this suggests:** the UMD isn't cleaner because it removes the cause of the SD's inversion — it's cleaner because its own construction happens to inject a positive instrumental bias large enough (comparable to its entire reported signal, +0.11) to swamp whatever the true, still-unidentified late-favoring effect is doing at $E_\mu \gtrsim 1\,\text{GeV}/\cos\theta$ — while the SD's construction happens (by the Cauchy accident) to expose that same effect with no comparable protection in its VEM channel.

This is stated as a hypothesis, not a finding, because it hasn't been tested — but it is falsifiable, cheaply, with the existing simulation.

## Part 4 — A new candidate: in-flight atmospheric scattering (checked, and found insufficient on its own)

Prompted directly by the author asking for a plausible physical mechanism and to check bibliography beyond what either GAP note cites. Two sources not previously used anywhere in this review, both already in the repo's `Bibliografia/`:

**Grieder, *Extensive Air Showers: High Energy Phenomena and Astrophysical Aspects* (2010)**, `Bibliografia/Papers sin citar/Grieder2010.pdf`, §3.1: "Coulomb scattering of muons *in conjunction with* the initial nuclear scattering of the parent hadrons at production cause the less energetic muons to be deflected significantly from the shower axis." Grieder treats **in-flight Coulomb scattering during propagation** as additive to and distinct from **production-kinematics scattering** — the only mechanism any analytic model in this whole investigation (Cazón's, Version_Vieja's, Parts 1–3 above) actually computes. Every one of them assumes ballistic straight-line propagation from production to ground; none include this.

**García Pinto (2010, GAP-2010-054)**, `Bibliografia/Papers sin citar/`, §2.7.4: "Muons travel almost in straight lines... almost unaffected by scattering" — read in isolation this looks like it rules the hypothesis out, but in context it's a *comparative* statement (muons vs. the far-lower-energy EM component, made to explain why the muon signal arrives in a compact time window in risetime analysis), not a claim that muon scattering is negligible in absolute terms.

**Why it has the right sign, derived rather than asserted.** Using the exact geometry already in this script plus the standard Highland multiple-scattering formula (general to any charged particle via its own $p,\beta$ — Grieder's Eq. 4.34–4.35, derived for electrons, generalizes directly): late-region muons traverse **~25% more slant depth** than early-region ones at the reference point (568 vs. 708 g/cm², from `slant_depth()` using an isothermal-atmosphere altitude estimate — cross-checked against the exact geometry's own $d_{early}/d_{late}$ ratio, agreeing to 3%). More path means more scattering, which — convolving Cazón's exponential-tailed angular distribution with this region-dependent extra smearing, via an exponential-tilt argument verified against a direct numerical convolution — **multiplicatively boosts the late/early density ratio**: $\text{boost} = \exp\!\big(k^2(\sigma_{late}^2-\sigma_{early}^2)/2\big)$, $k=E/Q$.

**Where it falls short, quantified (`scattering_boost_factor()`, §6 of the script).** Across the whole relevant energy range (0.3–5 GeV), the boost factor is only **1.01–1.02** — a 1–2% enhancement. Turning the pure-kinematic term's early-favoring prediction into the implied $\approx-0.13$ true-flux inversion needs something closer to a 30% correction. This mechanism, quantified the straightforward way, is roughly an order of magnitude too small on its own.

**Why it isn't discarded.** The Highland formula describes only the Gaussian *core* of the Molière scattering distribution. Grieder's own text (same section) distinguishes this "narrow-angle" regime from a separate "wide-angle" one driven by rare large single scatters — and this investigation has already hit exactly this shape of problem once (Part 2: the spectrum-weighted kinematic integral was dominated by a thin high-energy tail the power-law bulk couldn't represent). A naive RMS/core estimate is precisely the kind of calculation that would miss a real tail-driven contribution. The Molière tail itself has not been computed here.

**What to do instead of a fourth analytic toy model.** CORSIKA already simulates real multiple scattering — it is a full transport code, not a ballistic point-source model. The direct test needs no new physics machinery: compare each muon's *actual* simulated ground-arrival direction against what Cazón's production-kinematics-only formula predicts for that same muon (needs per-muon production height/angle/energy — the same data-availability question already flagged as unconfirmed in `discriminating_analysis_proposal.md`). The gap between the two *is* the propagation-scattering contribution, measured directly rather than modeled, and whether it's asymmetric early/late the way this hypothesis needs becomes a direct read of real data instead of another approximation.

## Part 6 — Concrete next steps, ranked by how decisively they'd settle this

1. **Isolate muon-only VEM and compare its $A_1$ to the muon MC-truth count's $A_1$.** Tests Part 1's exact cancellation directly. Prediction: VEM shows a *larger* inversion than count (roughly −0.13 vs. −0.10). Fully within the existing MC-truth pipeline.
2. **Recompute UMD $A_1$ with the two instrumental terms stripped out** — a *fixed* energy threshold (not $1\,\text{GeV}/\cos\theta_{loc}$) and flux-per-perpendicular-area instead of raw aperture count. Tests Part 5's hypothesis directly. Prediction: the de-instrumented UMD signal should shrink substantially, possibly toward zero or negative at large $r$. This is check #1 from `discriminating_analysis_proposal.md`, now with a sharper purpose.
3. **Check the reconstruction-level track-length bias the author raised independently**: does the algorithm converting WCD VEM signal to an estimated $N_\mu^{REC}$ correct for the angle-dependence of track length? If not, grazing late-region entries could bias $N_\mu^{REC}$ upward on top of whatever the MC-truth level already shows — a distinct mechanism from everything above, since it only touches reconstructed (not MC-truth) quantities, and needs looking at the actual Offline unfolding module rather than analytic geometry.
4. **Compare each muon's actual simulated ground-arrival direction to Cazón's production-kinematics-only prediction**, per Part 4 above — the direct, empirical test of whether in-flight scattering supplies the missing boost, and whether it's the right size and asymmetric the needed way. Needs the same per-muon production kinematics as check below, not confirmed available yet.
5. **Revisit per-particle CORSIKA-level extraction**, now motivated by exclusion (the analytic mechanisms don't work) rather than by not having tried the analytic route yet. Scope and cost (compute, and whether the needed granularity exists in the current production ADST) should be checked before committing to this — see `discriminating_analysis_proposal.md` for what's already confirmed unavailable in the current pipeline.

## What this file does and doesn't establish

**Established, not just modeled:** the tank's geometric term cancels exactly for VEM (Part 1, general theorem, holds for any incident flux); the tank's aperture bias on raw count is early-favoring and small (+0.031, exact tank geometry); the spectrum-weighted kinematic term stays early-favoring over any physically reasonable energy range (Part 2, direct calculation).

**Model-based inference, stated with its own uncertainty:** the ≈−0.13 true-flux number (Part 1) and everything built on it, including the UMD "floor" hypothesis in Part 5 — both should be read as the best current account, not a settled result, until the checks in Part 6 are run against the actual simulation. The scattering-boost calculation in Part 4 is likewise model-based (isothermal atmosphere, Gaussian-core scattering), and by its own numbers is insufficient — it's kept in because it's ruled out *quantitatively*, not dismissed on intuition, and because the wide-angle tail it can't capture is flagged explicitly as the open piece.

**Not established at all:** what physically makes the true muon flux late-favoring at large $r$. That is the actual open question this whole line of work has been circling, and this file does not answer it — it only narrows, more precisely than before, what the answer is not. In-flight atmospheric scattering (Part 4) is the first candidate mechanism found in this investigation with the qualitatively correct sign, sourced from bibliography not previously used here (Grieder 2010) — but quantified with the standard core approximation, it is roughly an order of magnitude too small, and the tail behavior that might close that gap is untested.
