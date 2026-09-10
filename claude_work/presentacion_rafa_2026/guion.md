# Speaker script and timing — RAFA 2026 talk

Deck: `presentacion_rafa_2026.pdf` (Spanish, 16:9 Beamer/metropolis, ITeDA palette).
Target: 25 minutes. This note is in English per the repo convention; the deck itself is
entirely in Spanish.

## Structure note: automatic section dividers

The metropolis theme auto-inserts a one-line "section title" slide for every `\section{}`
in the source — this is theme default behavior, not something added deliberately. There
are 10 of them (one per "Bloque"), so the PDF has 45 pages for 35 written content frames.
Treat each divider as a **5–10 second beat**, not a talking point — just say the block
title aloud while it's on screen and move on. They're useful as visual chapter markers
for the audience but add up to ~1 min if lingered on.

## Per-slide timing (35 content frames, subtotal ≈26.4 min; + ~1 min of divider beats)

| Slide (frame title) | min |
|---|---|
| Portada | 0.3 |
| ¿Qué son los UHECR? | 0.75 |
| Espectro de energía | 0.75 |
| El problema abierto: composición de masa | 0.75 |
| Anatomía de una lluvia | 0.75 |
| El Observatorio Pierre Auger | 1.0 |
| AugerPrime | 0.5 |
| AMIGA / UMD | 1.0 |
| ¿Por qué el UMD es distinto? | 0.75 |
| El plano de la lluvia | 1.0 |
| Mecanismo 1: atenuación | 0.75 |
| Mecanismo 2: proyección geométrica | 1.0 |
| El observable armónico | 0.75 |
| De CORSIKA a un valor de A₁ | 0.75 |
| Validación de la reconstrucción | 0.75 |
| Anillo Denso: ejemplo de ajuste | 1.0 |
| A₁ vs. θ: UMD y SD | 1.0 |
| Robustez del observable | 0.75 |
| Discriminación de masa (MF) | 1.0 |
| A₁(r,θ) del UMD (Infill) | 1.0 |
| El hallazgo: inversión de signo del SD | 1.25 |
| Desglosando la señal del SD | 1.25 |
| ¿Qué explica la inversión del SD? | 1.25 |
| **NUEVO** El núcleo se corre en el eje temprano-tardío | 1.25 |
| **NUEVO** Por qué: LDF simétrica + \emph{Toy Model} | 1.25 |
| Primera señal en datos reales | 1.25 |
| El sistemático a resolver | 1.0 |
| Notas GAP de la Colaboración | 0.75 |
| Conclusiones | 0.75 |
| ¡Gracias! | 0.1 |
| **Subtotal** | **26.4** |

Plus ~1 min of section-divider beats ⇒ **≈27.5 min total** — about 2.5 min over the
25-min slot. This is the direct cost of promoting the core-reconstruction-bias story
(two new slides, ~2.5 min) from backup into the main talk — see the note below on why
that trade was made deliberately. Claw back time with the same two cuts as before, in
order: fold "Robustez del observable" into one sentence on the prior slide (saves 0.75),
skip "AugerPrime" entirely (saves 0.5). That still leaves ~26.2 min; if the advisors want
it tighter, the next candidate to compress is "Desglosando la señal del SD" (the table
can be introduced verbally instead of read bullet-by-bullet).

## Talking points per block (what to actually say, not just read off the slide)

**Bloque 1 (Motivación).** Open with the flux number (1/km²/century) — it's the line that
makes a non-Auger physicist appreciate the experimental problem. Land Bloque 1 on: "we
can't isolate composition from the spectrum alone; we need $X_\text{max}$, and Auger's
main mass tracer only works 15% of the time."

**Bloque 2 (Auger).** Keep brief — this crowd likely knows what Auger is, at least by
name. The one non-obvious point to land: **AugerPrime's SSD unscrambles EM/muon
statistically, not physically**. That's the setup for why the UMD is different in kind,
not degree.

**Bloque 3 (Física).** This is the conceptual core. Slides 10–11 intentionally follow
GAP-2026-041's own §2.2 framing (both attenuation and geometric projection give $A_1>0$
for an ideal plane) rather than the older "Population A/B, opposite-sign" account in the
current `06_infill.tex` text — that account is what later verification work
(`unified_asymmetry_model_v1`) showed orders the detectors backwards. Land the "why does
$A_1<0$ ever happen" question explicitly — it's the hook for the whole second half.

**Bloque 5 (Anillo Denso).** This is the safest, most polished part of the thesis —
deliver it with confidence. The MF≈2.5 number is real but say explicitly it's an
**idealized upper bound** (fixed-geometry Dense Ring) before moving on, so it isn't
over-read.

**Bloque 6 (Infill / SD inversion).** The most novel physics result. On "¿Qué explica la
inversión del SD?": be plain that the UMD side is solved and the SD side is not — this is
the deliberately honest framing agreed on for this talk, matching the reduced claim in
`unified_asymmetry_model_v1/report.md`. It survives a skeptical question far better than
either overclaiming a mechanism or hiding the ≈0.29 gap. Land it on the door-open line
("hacen falta más efectos... ¿qué más está pasando a lo largo de este mismo eje?") — it's
the hook into the next block, not a dead end. If an advisor pushes on "what IS the
mechanism then," the answer is on the backup slide: eight candidates evaluated, none
survives quantitatively; current best lead is whether the SD's own MC-truth muon count
already carries an unrepresented detector-level selection.

**Bloque: Un segundo sistemático (el sesgo del núcleo).** This block exists because you
asked for it explicitly: the core-reconstruction bias is not new to Auger, but that it's
*systematically aligned with the early-late axis itself* is. Say that distinction out
loud on the first of these two slides — it's the whole point of promoting this out of
backup. The causal chain to land clearly: Offline's LDF is fit assuming azimuthal
symmetry → real signal isn't symmetric → the fitter's only free handle left is the core
position → it drags the core toward the late region → that drag independently washes out
the very $A_1$ being measured. The Toy Model slide's number is the payoff: bootstrap
injection of the directional counting residual reproduces the REC/MC gap *exactly* below
$\theta\approx35°$, and accounts for just over half of it above — the remainder is the
geometric core-shift shown on the previous slide, which the Toy Model alone (a purely
directional-counting model, no spatial displacement) can't capture. This pairs with the
in-prep GAP note on core-reconstruction bias, named explicitly on the GAP-notes slide
right after.

**Bloque 7 (Datos reales).** Flag clearly that this is a preliminary audit output, not
written into the thesis yet (Cap. 7 is still empty headers) — say so out loud, don't let
the slide's badge do all the work. The exposure systematic slide right after is what
keeps the 4.8σ number honest; don't skip it even under time pressure.

**Conclusiones.** Three results bullets map directly to the thesis's three original
objectives (Cap. 1): characterize the UMD asymmetry, validate the UMD against the SD,
and check its resolving power for mass discrimination. Close on the concrete next step
(exposure correction → Cap. 7/8) rather than a general "future work" gesture.

## Anticipated questions from advisors

- *"Why doesn't Ch. 6 already say this about the SD inversion?"* — Because the six/eight
  mechanism checks that rule out the current written explanation happened after that text
  was drafted (`claude_work/unified_asymmetry_model_v1/`, Sept 7). Worth a one-line thesis
  revision note, separate from this talk.
- *"Is the MF=2.5 achievable with real reconstruction?"* — No, stated as an idealized
  Dense Ring bound; REC-geometry core smearing degrades it (Ch. 6 §6.2). Already flagged
  on slide 18's small-print note.
- *"How confident are you in the 4.8σ real-data number?"* — Explicitly preliminary,
  single cell, exposure correction not yet applied; that's exactly why the exposure
  systematic slide right after it exists.
- *"Isn't core-reconstruction bias already known? What's actually new here?"* — The bias
  itself, yes. What's new is that it isn't generic scatter: it's systematically aligned
  with the same early-late axis the physics analysis depends on, which is why it partly
  masquerades as (and partly compounds) a loss of physical asymmetry rather than just
  adding noise. That's the whole reason it's now a main-talk slide instead of a backup
  footnote, and the subject of the second, in-prep GAP note.
