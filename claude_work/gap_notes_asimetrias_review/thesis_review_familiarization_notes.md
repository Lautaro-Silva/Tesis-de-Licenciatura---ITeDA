# Familiarization pass: thesis vs. GAP notes on azimuthal asymmetries

## Context

This is a research/reading task, not a code-implementation plan. The ask was to act as an EPJC-level peer reviewer, read the thesis PDF, the `[Version_Vieja]` GAP note, and the published `GAP2026_041` note, and get thoroughly familiar with the physics before receiving specific follow-up tasks. The one substantive question already asked was whether removing the kinematic-divergence anti-asymmetry argument (present in Version_Vieja, cut before publication) was justified. This file is the familiarization report and that opinion.

## What was read

- `Tesis - Latex/main.pdf` (85 pp, all chapters + appendices + references)
- `GAP_Notes_Latex/[Version_Vieja]GAP_41/...pdf` (17 pp, in full)
- `GAP_Notes_Latex/GAP2026_041/...pdf` (15 pp, in full)
- `Bibliografia/GAP2000_017.pdf` — Bertou & Billoir, "On the origin of the asymmetry of ground densities in inclined showers" (2000), cited as ref. [3] in both GAP notes and central to the disputed argument
- Cazón (2012) and Bradfield's thesis were not deep-read line-by-line; the GAP notes' own derivations/quotes from them were relied on, which are internally consistent and standard. Worth reading in full if a future task needs it.

## Thesis: important caveat before any review

The thesis PDF as it stands is a **draft, not a finished document**: Chapter 7 (experimental data analysis) and Chapter 8 (conclusions) contain only section headers with no body text, the abstract/acknowledgements pages are empty placeholders, and page 63 (end of §6.3) contains unedited planning notes-to-self left in the typeset text ("DESPUES PASAMOS A HABLAR DE LO MISMO PERO USANDO CORE Y ANGULOS REC...", "IDEAS: VER SI PUEDO AGREGAR..."). Any further review should treat Chapters 1–6 + Annexes as the reviewable content, and flag the missing chapters explicitly rather than silently working around them. (This matches the CLAUDE.md status table for `Tesis - Latex/capitulos/`: chapters 7 and 8 "not started," chapter 6 "partially done.")

## Thesis vs. GAP notes: a pre-existing inconsistency, not just the kinematic-divergence removal

The kinematic-divergence removal is the main difference between Version_Vieja and GAP2026_041, but there's also a physics inconsistency **inside the thesis itself**, which the GAP notes (both versions) quietly fix:

- Thesis §3.2.2 (Eq. 3.3) introduces Billoir's geometric term $\mathcal{A}_{geo} = \langle p_r/-p_z\rangle \tan\theta$ and states it "posee signo opuesto necesariamente" (has necessarily the opposite sign) to atmospheric attenuation — i.e., the thesis treats this term as capable of going *negative* for low-energy (Population B) muons, and it's this same term that's invoked in Ch. 6 to explain the SD's far-core sign inversion.
- Both GAP notes' §2.1.2, quoting the *same* Bertou–Billoir formula, state explicitly: "Since $p_t$ and $\tan\theta$ are also positive, the amplitude $\mathcal{A}_{geo}$ is **strictly positive**... Thus, the geometric flux projection acts additively with atmospheric attenuation to drive a positive asymmetry." This matches the original Bertou & Billoir (2000) note itself, which derives the same $\mathcal{A}(r,\phi)=\langle p_r/-p_z\rangle\tan\theta\cos\phi$ and treats it purely as a positive, early-region-enhancing term.
- The GAP notes resolve this by treating "geometric flux projection" (Bertou–Billoir, always positive, local plane-wave effect) and "kinematic divergence" (Cazón transport model, can dominate negatively for low-energy muons, global far-field effect) as two **distinct** mechanisms, rather than one formula that mysteriously flips sign. This is a real, well-motivated correction of the thesis, independent of the kinematic-divergence removal question, and worth noting explicitly in any thesis-text review (§3.2.2, §6.1.2).

## The core question: was cutting the kinematic-divergence argument justified?

**Independent assessment: yes, and there's a specific, citable reason for it that goes beyond "needed more review."**

Version_Vieja's central claim was that the SD's far-core sign inversion is driven by the kinematic divergence of low-energy "Population B" muons, and that this was empirically confirmed by decomposing the MC-truth SD signal into EM and muon components (§4.3, Fig. 6, Table 2): the "SD-Muon (MC)" component's $A_1$ goes from +0.05 at 450 m to −0.10 at 1200 m, matching the sign flip predicted by the Cazón-model derivation in §2.2. The conclusion was stated with strong, unhedged language: "this artefact is not a Monte Carlo failure," "demuestra de manera irrefutable," "collapses the kinematic divergence contribution... to a negligible level."

The problem is the observable used to "confirm" this. GAP2026_041 §4.3 adds one sentence that Version_Vieja never states: the MC-truth "muon" count used in the decomposition, $N^{MC}_{\mu,\text{sup}}$, is the particle count incident on the **three-dimensional volumetric boundary of the WCD tank** — not an idealized flat 2D ground plane. That matters enormously, because Bertou & Billoir's own 2000 note (GAP-2000-017, §6–7, cited by both GAP notes as ref. [3]) already showed that Auger's cylindrical Cherenkov tanks have a **side-wall/track-length effect specific to muons**: since a muon's tank signal scales with the path length it travels through water, and side-entering muons (disproportionately common in the late region of inclined showers) traverse longer paths, this instrumental effect *independently* produces an asymmetry with the same sign structure the kinematic-divergence argument claims — and Bertou-Billoir's own Fig. 6 shows it can reduce or reverse the top-surface-only asymmetry.

So the observable Version_Vieja used to validate the kinematic-divergence hypothesis is degenerate: a late-region muon-signal deficit is exactly what *both* the kinematic-divergence mechanism (Population B production kinematics) *and* the tank side-wall/track-length mechanism (pure detector geometry, no production-kinematics input needed) would produce, using the *same* MC-truth variable as "evidence." Version_Vieja never isolated the two, and its equations (4)–(9), while internally consistent as an analytic derivation, were never actually tested against a variable that separates production-level kinematics from detector-volume effects. Given that the group's own foundational 2000 reference had already flagged and quantified this exact confound 26 years earlier, asserting the kinematic explanation as proven ("irrefutable," collapsing "to zero") outran what the analysis could support.

The published version's fix is the epistemically correct one: it demotes the claim to "two compounding mechanisms... Regardless of the relative quantitative weight of the kinematic and instrumental effects within the SD, our findings establish the UMD as..." — i.e., it keeps the empirically solid result (UMD stays positive, SD inverts) and drops the over-attributed causal story, explicitly stating the relative weight is undetermined. That is a more defensible, and more publishable, claim.

Also worth noting: this doesn't fully vindicate the published version either — it still hasn't run the controlled test that would settle the question (e.g., comparing SD-muon asymmetry computed from ground-plane MC truth vs. from the volumetric tank-entry MC truth, which the simulation framework should be able to produce). That would be a natural, well-scoped follow-up GAP note or thesis chapter — and it echoes the same "toy-model, future work" caveat the thesis itself (§6.1.3) already flagged and that CLAUDE.md §6 documents as an abandoned attempt (`Scripts/Intento Toy Model para Inversion Fallido/`), for a related but distinct reason (lack of per-muon production kinematics in the ADST ground footprint, not lack of a discriminating detector-geometry test).

## Other differences between Version_Vieja and GAP2026_041 worth flagging

- **Title/framing shift**: "A Phenomenological Study of Early–Late Azimuthal Asymmetries... with the UMD" (confident, solved-problem framing) → "...UMD–SD Comparison and Insights into the Surface-Detector Sign Inversion" (investigative, open-question framing). Consistent with the more cautious causal claims.
- **Iron cross-check dropped**: Version_Vieja's Table 1 lists "Proton, Iron (analysed independently)" and asserts iron shows "identical qualitative behaviour" — but no iron plot is ever shown in the note. GAP2026_041's Table 1 lists only "Proton." An asserted-but-unshown result was correctly removed rather than left as an unsupported claim.
- **New instrumental-mechanism section**: GAP2026_041 §5 adds a full derivation of the side-wall/track-length mechanism (the $A_{side}$ cross-term, and a new point about local incidence angle inflating VEM energy deposit even for top-entering late-region muons) that has no counterpart at all in Version_Vieja. This is genuinely new physics content, not just a deletion.
- **Numbers unchanged**: The actual simulated results (Figs. 2–5, Table 2) are numerically identical between the two versions. Nothing about the data or the fits changed — only the causal interpretation layered on top of them. That's a healthy sign: the empirical measurement is stable; what changed is the (correctly weakened) attribution of its cause.

## Overall opinion on the GAP notes generally

The published note (GAP2026_041) is tightly argued, appropriately hedged where the evidence doesn't support a stronger claim, and its central empirical result (UMD preserves a clean, monotonic, attenuation-only asymmetry; SD inverts at large $r$ due to some combination of kinematic and instrumental effects) is well supported by the MC decomposition shown. Its main remaining weakness is exactly the one it inherited from cutting Version_Vieja's argument: it now states two plausible mechanisms without a discriminating test between them, which is honest but leaves the note's "central puzzle" (per its own §4.2 framing) formally unresolved. Refereed at EPJC level, that would be the one substantive comment — not a rejection-level flaw, but a "how would you tell these two mechanisms apart" request that would strengthen the note considerably, and is a very natural next-step data analysis (splitting $N^{MC}_{\mu}$ by top-entry vs. side-entry, or by local incidence angle) given the simulation framework already used.

The thesis, once finished, will need to either adopt the published GAP note's more careful two-mechanism framing in Ch. 3/6 (dropping the "signo opuesto necesariamente" claim about $\mathcal{A}_{geo}$ itself, and being explicit that the Ch. 6 SD-inversion story is not fully disentangled from tank geometry), or explicitly justify why it diverges from the now-published, more authoritative account.

## Next steps

Open to direction on a structured referee report on the thesis chapters, a rewrite proposal for the affected thesis sections (§3.2.2, §6.1.2–6.1.3), or the discriminating-test analysis proposal for the GAP note's open mechanism question.
