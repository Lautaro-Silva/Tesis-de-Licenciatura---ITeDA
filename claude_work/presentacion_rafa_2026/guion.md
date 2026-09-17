# Speaker script and timing — RAFA 2026 talk

Deck: `presentacion_rafa_2026.pdf` (Spanish, 16:9 Beamer/metropolis, ITeDA palette).
Target: 25 minutes. This note is in English per the repo convention; the deck itself is
entirely in Spanish. **RAFA 2026 runs Sept 15–18 in Catamarca — this is the third and
current revision, addressing a full pass of the author's own review.**

## Structure note: automatic section dividers

The metropolis theme auto-inserts a one-line "section title" slide for every `\section{}`
in the source — theme default behavior. There are 9 of them now, so the PDF has 44 pages
for 35 written content frames. Treat each divider as a **5–10 second beat** — just say the
block title aloud and move on.

## Per-slide timing (35 content frames, subtotal ≈28.7 min; + ~0.9 min of divider beats ≈ 29.6 min)

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
| **NUEVO** Mecanismo 3: divergencia cinemática (Cazón) | 1.25 |
| **NUEVO** ¿Positivo o negativo? La energía de cruce | 1.5 |
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
| ¿Qué explica la inversión del SD? (HasStation, preliminar) | 1.25 |
| Motivación (residuo de conteo) | 1.0 |
| El núcleo se corre en el eje temprano-tardío | 1.25 |
| Por qué: LDF simétrica + \emph{Toy Model} | 1.0 |
| Primera señal en datos reales (merged) | 1.5 |
| Conclusiones | 0.75 |
| ¡Gracias! | 0.1 |
| **Subtotal** | **28.7** |

Plus ~0.9 min of section-divider beats ⇒ **≈29.6 min total** — this is now noticeably
over the 25-min slot (~4.5 min), the direct cost of the two new Cazón/kinematic-divergence
slides (~2.75 min) on top of filling in the former blank slide (+1.15 min vs. its old
placeholder). If time is tight, the cleanest single cut is the "¿Positivo o negativo?"
slide's three-factor equation walkthrough — the punchline (mostly positive, but not enough
to explain the SD alone) can be stated in one sentence while flipping past it, with the
full derivation available if an audience member asks. The two long-standing fallback cuts
(skip "Robustez del observable," skip "AugerPrime") still apply on top of that if needed.

## What's on slides 15–16 and 23 now (all added across recent rounds)

- **Mecanismo 3 / "¿Positivo o negativo?"** (new this round): the Cazón kinematic-
  divergence derivation — muon production kinematics, the angular emission spectrum
  (ADF), and the three-factor early/late density ratio. The key, slightly
  counter-intuitive result: the kinematic-gain term is *positive* (early-favoring, same
  sign as attenuation) across most of the relevant muon energy range, and only flips
  negative above a threshold energy $E^*$ of a few GeV — contrary to the original
  "kinematic filter" story in the thesis text. This is presented as settled, correctly-
  derived physics (teal "DESARROLLO ANALÍTICO" badge) — distinct from the orange
  "HIPÓTESIS" badge on slide 23, which is a live, unverified lead.
- **"¿Qué explica la inversión del SD?"** (filled in two rounds ago): the `HasStation`
  selection-bias finding — before the SD reconstruction-selection flag, the SD's muonic
  count tracks the UMD's positive asymmetry; after the flag, it inverts, while the EM
  component is essentially unaffected. Orange "HIPÓTESIS — EN VERIFICACIÓN" badge — the
  author was still actively checking this as of the last update, so don't present it as
  confirmed.

## Talking points per block

**Bloque 1 (Motivación).** Open with the flux number (1/km²/century). Land on: "we can't
isolate composition from the spectrum alone; we need $X_\text{max}$, and Auger's main mass
tracer only works 15% of the time."

**Bloque 2 (Auger).** Keep brief. Land: AugerPrime's SSD unscrambles EM/muon
*statistically*, not physically — the setup for why the UMD is different in kind.

**Bloque 3 (Física).** The conceptual core. Mecanismo 2 is phrased around the ground
*incidence angle* ($\theta_{early}\neq\theta_{late}$, the new θ_early/θ_late figure) rather
than the production-angle/α picture — this matches the framing used later for the UMD/SD
reconciliation, so keep the two consistent if asked to elaborate. Land the "why does
$A_1<0$ ever happen" question — it's the hook for the whole second half.

**Bloque 5 (Anillo Denso).** The safest, most polished part. The MF≈2.5 number is real;
say plainly it's from the idealized Dense Ring (fixed geometry) so it isn't over-read —
the explicit "cota superior" note was removed from the slide itself this round, so this
caveat now lives only in what you say, not on screen. Don't skip saying it.

**Bloque 6 (Infill / SD inversion).** The most novel physics result. "Desglosando la señal
del SD" is the last slide with real content before the blank one — land the EM/muon
component split clearly, since the story pauses right after it.

**Bloque: Un segundo sistemático (el sesgo del núcleo).** The core-reconstruction bias
itself isn't presented as newly discovered (the author asked that framing removed, since
it's unverified whether this was known before) — it's presented as *one of the central
results of this analysis*. Say the causal chain plainly: Offline's LDF is fit assuming
azimuthal symmetry → the real signal isn't → the only free handle is the core position →
it drags toward the late region → that independently washes out the very $A_1$ being
measured. The Toy Model slide is the payoff: exact match below θ≈35°, over half explained
above it. Don't assert what accounts for the remainder — that causal link was deliberately
removed as unconfirmed; if asked, say it's an open question, not "the core shift."

**Bloque 7 (Datos reales).** One merged slide now — region, plot, and the number, framed
plainly as preliminary real-Auger-data results. The φ-exposure systematic that used to
follow immediately is now backup-only; if you want the audience to know the 4.8σ number
isn't fully clean yet, say so verbally (a sentence, not a slide) or pull up the backup
slide if asked.

**Conclusiones.** Three results bullets, unchanged from the prior revision. "Próximos
pasos" no longer references thesis chapters — it's phrased as completing the parameter-
space scan on real data and closing the SD-inversion question, per the author's request
not to frame this as thesis housekeeping.

## Anticipated questions from advisors

- *"What happened to the mechanism discussion / the ruled-out list?"* — Still exists, now
  backup-only (the elimination table backup slide was removed too, per the author's
  request — if asked live, the honest answer is "we evaluated and ruled out several
  candidates, none survive quantitatively" without the itemized table on hand).
- *"Is the MF=2.5 achievable with real reconstruction?"* — No — idealized Dense Ring bound,
  REC-geometry core smearing degrades it. Say this explicitly; it's no longer on the slide.
- *"How confident are you in the 4.8σ real-data number?"* — Explicitly preliminary, single
  cell, φ-exposure correction not yet applied (now a backup slide, not a follow-up in the
  main flow — bring it up verbally).
- *"Isn't core-reconstruction bias already known? What's new here?"* — Careful: the deck
  no longer claims the axis-alignment is novel outright (that assertion was removed as
  unverified). The honest answer is: this analysis establishes the alignment as a central,
  quantified result; whether it was previously known in this specific form hasn't been
  checked against the literature.
