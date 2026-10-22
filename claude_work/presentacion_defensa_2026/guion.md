# Speaker script — thesis defense, 16 Oct 2026

Deck: `presentacion_defensa_2026.pdf` (Spanish, 16:9 Beamer/metropolis, ITeDA palette).
Build: `./compilar.sh` (two pdflatex passes). Source: `presentacion_defensa_2026.tex`.
Target: 40–45 min (≈28 min of content since revision 20). This note is in English per the repo convention; the lines to say
aloud are quoted in Spanish.

All data figures are copied from `Tesis - Latex/capitulos/imagenes_capitulos/`, so every
plot on screen is the exact one in the thesis — except two redrawn from the same data and
cuts: the mass slide (19, `scripts/figura_masa.py`, same A1 values without the significance
S) and the field-data slide (33, `scripts/figura_datos_campo.py`, same A1 and χ²). The slides do not cite thesis figure or
equation numbers (author's request); the "Thesis" column below keeps that mapping for you,
in case the jury asks where something is in the document. Third-party images keep a
one-line source credit (PDG, Botti, Haungs, Luce, Pierre Auger Collaboration).

Slide numbers are the frame counter shown on screen (`n/35`); the 8 section-title pages
are not counted, and slide 25 has two PDF pages (the meme appears on the second).
Simulation slides carry a badge saying which topology they use: "SIMULACIONES -- ANILLO
DENSO" or "SIMULACIONES -- INFILL".

## Timing (≈28 min of content + ≈0.5 min of section dividers)

Revision 20 cut the deck from 53 to 35 slides (directors' and jury's corrections), so the
talk is now well inside the 40–45 min window; the spare time is for questions.

| # | Slide | Thesis | min |
|---|---|---|---|
| 1 | Portada | — | 0.3 |
| 2 | ¿Qué son los UHECR? | Fig. 1.1.1 | 0.8 |
| 3 | Estructuras del espectro | Fig. 1.1.2 | 0.4 |
| 4 | Anatomía de una lluvia y X_max | Fig. 1.2.1 + N(X) sketch | 0.8 |
| 5 | El Observatorio | Fig. 2.0.1 | 0.7 |
| 6 | AugerPrime | §2.1 (photo: arXiv:2507.07762) | 0.4 |
| 7 | AMIGA / UMD | Fig. 2.4.1 | 0.7 |
| 8 | ¿Por qué el UMD es distinto? | §2.4 | 0.6 |
| 9 | Índice | — | 0.3 |
| 10 | Plano de la lluvia | Fig. 3.1.1 | 0.8 |
| 11 | El observable A1 | Ec. 3.3.1 | 0.6 |
| 12 | Mecanismos: atenuación y respuesta del detector | Ec. 3.2.1–3.2.5, §3.2.2 | 1.2 |
| 13 | Mecanismos: divergencia cinemática | Fig. 3.2.1 (redrawn), Ec. 3.2.6–3.2.10 | 1.8 |
| 14 | Un modelo de juguete (+ geomagnético) | §3.2.4, Ec. 3.4.1, 3.4.6, Anexo A | 1.1 |
| 15 | La predicción del modelo | Fig. 3.4.1 (b) | 0.7 |
| 16 | Simulaciones | Cap. 4, Tabla 4.1.1 | 0.8 |
| 17 | Anillo Denso: ejemplo | Fig. 5.1.1 | 0.6 |
| 18 | A1 vs θ: UMD y SD | Fig. 5.1.2 | 0.8 |
| 19 | ¿Discrimina la masa? Protón vs. hierro | Fig. 5.5.1 (redrawn without S) | 0.8 |
| 20 | Dependencia con la energía | Fig. 5.4.1 | 0.5 |
| 21 | El arreglo Infill: dos geometrías | Cap. 6 (intro), §6.2 | 0.8 |
| 22 | El UMD en el Infill | Fig. 6.1.1 | 0.7 |
| 23 | UMD vs. SD total | Fig. 6.1.3 | 0.7 |
| 24 | Desglose del SD | Fig. 6.1.4 | 0.9 |
| 25 | ¿Qué estamos viendo? (2 pages: + meme) | Fig. 6.1.4 | 0.7 |
| 26 | Promedio por región | §6.1.3 | 1.1 |
| 27 | Prueba 1: sacando la selección de estaciones | Fig. 6.1.5 | 1.1 |
| 28 | Prueba 2: muones en los tanques excluidos | Fig. 6.1.6 | 1.0 |
| 29 | Discusión | §6.1.3 (end) | 1.3 |
| 30 | Con la geometría REC, la asimetría desaparece | Tabla 6.2.1 | 0.7 |
| 31 | El core reconstruido se corre hacia la temprana | Fig. 5.2.5 | 0.9 |
| 32 | El efecto sobre A1 | Ec. 6.2.1, Tabla 6.2.1 | 1.0 |
| 33 | Datos de campo (PRELIMINAR) | Fig. 6.4.2 (redrawn) | 0.8 |
| 34 | Conclusiones | Cap. 7 | 1.2 |
| 35 | ¡Gracias! | — | — |

Backups, in order: La pregunta (REC < MC), ¿Es un problema de los ajustes?, El residuo,
El error depende de la región, bootstrap por región (these five were main slides 42–46
until revision 19), incertezas de A1 y S, grillas MC/REC, conteo REC vs. MC, A1(r) en
datos vs. simulaciones (the A1(r) panel that left the data slide), datos de campo — región
de referencia y fases, muestra de datos de campo, reconstrucción de energía y dirección,
ajuste del SD en el Anillo Denso.

## Talking points

**1–4 Rayos cósmicos.** Open with the flux (1/km²/siglo). Three open questions; "hoy
nos importa la composición". Slide 4: two components, X_max as the depth of the maximum
*number* of particles (the N(X) sketch), ⟨X_max⟩ ∝ ln(E/A).

**5–8 Auger.** Keep brief. Slide 5 gives the duty cycles (SD ~100%, FD ~15%). Slide 6: the
photo is a real upgraded station (SSD on top of the tank, radio antenna above it). Only say
that WCD+SSD does not separate the two components physically. On 7, say "más de media
atmósfera" (540 g/cm² vs ≈870 g/cm² vertical at Auger). On 8, the threshold depends on the
*local* angle of each muon, so it is higher for late muons — the soil attenuation is not
modelled anywhere else in the talk, so do not promise to come back to it.

**9 Índice.** Just read the six items. (The objectives slide was removed: "es como poner
las conclusiones antes".)

**10–11 Plano y observable.** The observable comes before the mechanisms so that each
mechanism can be labelled "favorece temprana / tardía". "El signo de A1 dice qué domina,
no identifica a un mecanismo."

**12 Atenuación y respuesta del detector.** Attenuation: f_att = e^(−d/λ); the late region
travels a longer path, so attenuation *always* favours the early region. For muons it is
mostly survival against decay (λ_dec ≈ 6.2 km × p/GeV), if asked. Detector response: the
sketch shows that the *local* incidence angles ϑ are not the same in the two regions — the
late muons arrive more inclined. Projected onto the ground, the same number of particles is
spread over a larger area (∝ 1/cos ϑ) on the late side, so a flat detector sees a lower
density there: it favours early. The block on the right: in the model this enters with a
weight κ — 1 for the UMD plate, 0 for the SD tank signal. If asked why κ = 0 for the tank:
where more muons enter the tank they cross less water, and number × track ≈ volume, so the
signal is not modulated (the tank-count κ ≈ 0.3 and the Bertou & Billoir first-order
expression are no longer on the slides; have them ready).

**13 Divergencia cinemática (the core of the physics part).** The diagram is a redrawn
version of Luce et al.'s figure (ICRC 2021) — the credit line was removed from the slide, so
**say it aloud**: "la figura está adaptada de Luce et al.". θ_sh ≈ 52°, both stations at the
same r (red arrows, drawn slightly offset along the axis with dotted reference lines), the
local zenith angles ϑ_temp ≈ 19° / ϑ_tard ≈ 66°. The arrows at the axis are the transverse
momenta p_t opening outwards, in the colour of each region; the momentum p along the axis is
not drawn — say it: "el muón sale con un momento p a lo largo del eje y un p_t que lo abre".
The two p_t are to scale for the same p: the late station needs a much smaller one (α_tard ≈
14° vs α_temp ≈ 33°). Bullets: the divergence angle is defined by sin α = p_t/p ≃ c p_t/E;
Cazón's dN/dp_t ∝ p_t e^(−p_t/Q), small p_t most probable; same r ⇒ the late region is
farther (dilution, favours early) but needs a smaller α (favours late). The boxed function is
called F^div (not S, which is reserved for the total signal): "el efecto da algo como esto";
in the ratio F^div_tard / F^div_temp the first factor favours early and the two under the
single brace favour late. Do **not** discuss energy dependence or a possible sign flip — it
does not happen.

**14–15 Modelo de juguete.** 14 opens with the geomagnetic field: another effect that
exists — the Lorentz force would separate μ+ and μ− — but it is second order for these θ_sh
(dominant only at θ ≳ 70°) and is not included. Then "podemos construir un modelo de juguete con" one point source of muons on the axis at distance D that
combines the mechanisms (divergence, attenuation, response, UMD threshold). "Analizando la
asimetría y linealizándola a primer orden en r/D" gives the bracket: one term per mechanism,
only −s is negative. Say aloud that this generalises Armbruster (2018), whose expression is
the κ = 0 case (cited by Luce et al., ICRC 2021) — it is no longer on the slide. 15: the
prediction: A1 > 0 in UMD and SD, growing with r and θ_sh. Frame it as a starting point:
"nos sirve para ver cómo esperamos que se comporte la asimetría y probar qué tanto se ajusta
al modelo que propusimos" — and anticipate that it will *not* fully hold (e.g. the UMD
asymmetry flattens with r instead of growing at intermediate θ, 30°–50°). (Model parameters, if asked:
D = 7.5 km, Q = 0.15 GeV/c, p_UMD = 1 GeV/c, γ = 2.6. The amplitudes depend on them and are
not a prediction.)

**16 Simulaciones.** Official production, CORSIKA + Offline, SD-750 + UMD. SIBYLL 2.3e
(main), QGSJET-III.01 and EPOS-LHC-R; p, He, O, Fe; 10^17.5–10^18 eV; θ ≤ 65°. The Dense
Ring: 12 virtual stations at r = 450 m from the *true* axis, every 30° in the shower plane;
the radius is fixed, so there is no geometric difference between MC and REC here (the
reconstructed core only rotates φ by ~b/r ≈ 2°). Say "MC es la verdad de la
simulación; REC, lo que entrega la reconstrucción" the first time REC appears (slide 17).

**17–20 Anillo Denso.** 17: positive, as predicted. 18: SD above UMD at low θ (EM), below at
θ ≳ 50° (κ = 0 vs κ = 1, if asked). The REC < MC difference is no longer discussed in the
main talk (backups "La pregunta" … "bootstrap por región"). Robustness (φ_sh, hadronic
models) was removed: if asked, φ_sh-independent and SIBYLL vs QGSJET-III within ±10% over
almost the whole range (thesis §5.3). 19: we wanted to know whether A1 could be used for mass
discrimination, and it cannot: marginally ⟨A1^p⟩ ≳ ⟨A1^Fe⟩, but the difference is ≲ 0.01 and
only in some θ bins, so the two primaries are comparable. The figure no longer shows the
significance S (author's request); if a juror asks for a number, the maximum was S ≈ 2.5 at
40–55°, and it is a difference of *means* (grows as √N), not an event-by-event separation.
20: "también se analizó la dependencia de A1 con la energía incidente de la lluvia" —
protons, 40–60°, five bins of reconstructed energy; A1 grows only slightly with E, which
justifies integrating 17.5–18.0. (The X_max interpretation slides were
removed; do not bring it up unless asked.)

**21 El arreglo Infill: dos geometrías.** Still simulations (the badge says SIMULACIONES --
INFILL): now the Infill stations: their distances to
the axis vary, so we can look at A1(r). r and φ of each station depend on where the axis is.
Two geometries: MC (true core and direction) and REC (reconstructed). The main difference
between them is the **core** position. Say "core" throughout, never "núcleo".

**22–25 UMD vs SD.** 22: MC geometry. Read the curves by θ: below 10° it is small
(compatible with zero within ~2σ); at 10°–30° it grows slowly with r; at 30°–50° it rises to
≈0.1 by ~600 m and then stays **constant** with r (the 40°–50° curve only rises again beyond
~1200 m, where the statistics are poor); at θ ≥ 50° it grows with r out to 1500 m. So it is
positive but does not always grow with r — a discrepancy with the model, say it explicitly. 23
(30–40°, MC geometry, both written on the plot): the SD total inverts far from the core; already
reported (Bradfield 2022), never explained. 24: split by component — the EM is positive
everywhere; the SD muons are what inverts. (The right-hand "A1 (VEM)" twin axis was cropped
out: it duplicates the left scale and A1 is dimensionless.) 25: same shower, same region —
but the particles crossing each detector are not the same ones. Same quantity (muons
crossing the detector, MC count), completely different behaviour. Next click: the meme.

**26–29 Sesgo de selección (central result — the most time).**
26: the analysis averages only stations that triggered and belong to the reconstructed
event. Present it as a proposal: if the probability of entering depends on the station's
muon content, and differently in each region, the average is biased. The cartoon is
illustrative.
27: same counts, coordinates and fit; only which stations enter changes. Without the
selection the inversion disappears. +0.069 ± 0.016 (all) vs −0.124 ± 0.019 (selected) at
1200–1350 m; errors from a bootstrap over the 960 showers, if asked.
28: if it is a trigger effect — knowing the SD is calibrated — the excluded tanks should
hold at most one muon: 95% / 93%, means 0.35 / 0.46. "A lo sumo uno", not "alrededor de
uno". If asked for the retained fractions: 42% of the early and 18% of the late stations
enter (1200–1350 m).
29, *Discusión*: without selection the SD muons are positive again but do not reach the
UMD; candidates already in the model: plate vs tank response (κ) and the UMD threshold.
Then: the UMD has no trigger of its own — it depends on the SD trigger, a module is read only
if the tank of its station triggers. So why is its average not biased the same way? First
sub-bullet: the SD is selected *on its own particles* — a tank enters when its own count
fluctuates upward, so its average is pulled up; that fluctuation need not repeat in the UMD
because the two detectors do not measure the same particles ("imaginate que son partículas
distinguibles, con nombre"). Second: from the start the UMD covers a different surface and
is not exactly under the tank, so the muons crossing it are other muons, and they also have
to cross the equivalent of more than half an atmosphere of soil. The tank triggering decides
which station enters, not how many muons the UMD sees: the expected UMD count is still the
local density. If a juror pushes ("¿entonces el UMD no tiene ningún sesgo?"): a residual
effect remains through what the two share — the station's position inside the r bin and the
muon content of each shower — second order and not quantified. (Removed from the slide by
the author's choice; I agree it is better said orally than written, but have it ready.)

**30–32 La posición del core reconstruido.** 30: A1 of the *same* injected muons with the
true (MC) and reconstructed (REC) geometry, 450–600 m: with REC geometry it almost
disappears (0.108 → −0.002 at 40–50°). 31: the reconstruction LDF is symmetric in φ, so the
only way to absorb the early excess is to move the core toward the early side; the fit
Δr = a + b cos φ gives b = 9, 15, 21 m, growing with θ. 32: approximating and fitting the LDF as
ρ ∝ r^−β, the correction to the LDF from the core shifted by b along the early–late
direction is a cos φ modulation: ρ(r + b cos φ) ≈ ρ(r)[1 − β(b/r) cos φ]
⇒ ΔA1 ≈ −β b/r. Point at the table: simulation vs −βb/r. Conclusion of the slide (now written on it): with
this model we reproduce the loss of asymmetry seen in the simulations when going from the MC
to the REC geometry. β is the local log-log slope of
the UMD muon LDF, measured on the same simulations. **Check before the defense:** the β
values (2.9, 2.7, 2.5) are thesis Table 6.2.1, but the committed
`Scripts/Cap5_corrimiento_nucleo.py` fits 300–650 m and gives 2.63, 2.46, 2.37; with those the
prediction at 450 m is −0.054, −0.085, −0.111 — same conclusion, but know where each number
comes from. If asked about φ: the shift also rotates the azimuth seen from the REC core by
~b/r ≈ 2°, much less than the 30° bins (0.108 → 0.107); only the distance matters.

**33 Datos de campo.** What we see: the UMD muon density as a function of φ, normalised to
its mean, for Phase II showers with the cuts in the box, and the fit 1 + A1 cos φ. The
maximum at φ ≈ 0 means an excess in the early region, as in the simulations. Preliminary:
the core-position correction we just saw exists has not been applied. If asked for the number: A1 = 0.063 ± 0.017, 18.0 ≤ lg E <
18.5, **50–60°, 750–1250 m** (the caption of thesis Fig. 6.4.2 says 40–60° / 750–1050 m;
the code, the abstract and the conclusions say 50–60° / 750–1250 m — the slide figure was
regenerated from the code and reproduces A1 = 0.063 ± 0.017, χ²/ndf = 15.5/11). No
systematics yet, and no MC above 10^18 eV for this bin. The A1(r) data-vs-MC panel is now a
backup.

**34 Conclusiones.** Four points: (1) the azimuthal asymmetry of the muon density was
analysed with the UMD — early excess in simulations and a first, preliminary observation in
field data; (2) the analytic model gets the sign but is not complete — e.g. at intermediate θ (30°–50°) the
UMD asymmetry flattens with r instead of growing; (3) the SD sign inversion far from the core is a
selection bias — only the stations that trigger are averaged, and on the late side those are
mostly the ones with more muons than the mean; averaging over all stations, the SD muon
asymmetry is positive again, like the UMD's; (4) a systematic error in the core (shower-axis)
position along the early–late direction was observed: the reconstructed core moves toward
the early region, which reduces A1 as ΔA1 ≈ −β b/r. Future work is no longer a slide: if asked, the kinematic
production + transport model (thesis §6, "Perspectiva") and the core correction in data.

## Revision log

**Revision 23 (author's corrections 1–3):** slide 8 — "la contribución de e±/γ queda muy
reducida y la señal es principalmente muónica" (no S_EM + S_μ). Slide 12 — "del lado tardío
los muones llegan más inclinados" and "la densidad en el piso es n cos ϑ" removed (said
aloud). Slide 22 — the "crece, con una meseta" bullet rewritten per θ range to match the
figure: 10°–30° grows slowly with r; 30°–50° reaches ≈0.1 near 600 m and then stays constant;
θ ≥ 50° grows out to 1500 m. This also corrects the old "θ ≥ 40°: crecimiento monótono", which
the 40°–50° curve does not show; conclusion 2 now says "a θ intermedios (30°–50°)" instead of
"θ ≲ 40°".

**Revision 22 (author's corrections 1–11):** slide 4 — "se absorbe más rápido", "llega al
suelo" removed. Slide 12 — the projection bullet starts from "un haz de n partículas por unidad
de área" and ends with the ground density n cos ϑ (no "un detector plano ve menos densidad");
κ block on two lines. Slide 13 — Luce credit line and the p arrow removed (both said aloud),
late r arrow raised, "salen con un ángulo de divergencia definido como", the divergence
function renamed F^div, ratio equation lowered. Slide 14 — "Podemos construir un modelo de
juguete con…". Slide 16 — temprana/tardía labels removed from the sketch, "no hay diferencia
de geometría entre MC y REC". Slide 17 — figure shifted left. Slide 21 — bigger sketch.
Slide 25 — bullets reordered, "misma cantidad" in bold. Slide 26 — "el promedio por región
se sesga". Slide 29 — no parenthesis; sub-bullets rewritten (not the same particles; other
surface, not exactly under the tank, more than half an atmosphere of soil); residual-effect
sub-bullet removed. Slide 32 — conclusion line added.

**Revision 21 (author's corrections 1–17):** slide 4 — one bullet per component. Slide 12 —
figure at the top of the right column, κ in a block below it, and the ground-projection
argument back (same particles over a larger area ∝ 1/cos ϑ on the late side). Slide 13 —
diagram redrawn with the production point higher (ϑ_temp ≈ 19°, visible), p_t arrows and
labels in the colour of each region, the early r arrow offset along the axis, α_temp label
moved outside the wedge; bullets: sin α = p_t/p ≃ c p_t/E, Cazón's distribution in its own
bullet; the geomagnetic line moved to the start of slide 14. Slide 19 — figure redrawn
without S (`scripts/figura_masa.py`, same A1 as thesis Fig. 5.5.1), first bullet "Buscamos si
podíamos usar la asimetría A1 para hacer discriminación de masa". Slide 20 — first bullet
replaced. Slide 21 — SIMULACIONES -- INFILL badge. Slide 22 — "discrepancia con el modelo".
Slide 23 — first bullet removed. Slide 24 — right frame line restored (crop 58 pt instead of
66). Slide 27 — table right under its bullet. Slide 28 — bigger plot, the ≤1-muon bullet
moved to the right column. Slide 29 — UMD "depende del trigger del SD"; decorrelation
argument rewritten (selection on the SD's own particles vs. independent UMD fluctuation;
residual through shared position/shower content). Slide 31 — wider plot, bullets and caption
lower. Slide 32 — "aproximando y ajustando la LDF … corrección por el core corrido en la
dirección temprana–tardía". Slide 33 — two-column layout with an explanation of the plot.
Slide 34 — conclusions 3 and 4 rewritten. Plots enlarged on 17, 18, 19, 20, 22, 23, 24, 27.

**Revision 20 (directors' and jury's corrections — "sacar mucho texto"):** 53 → 35
slides. Removed: objectives, robustness, the two X_max slides, the SD-trigger slide, "¿Qué
estaciones entran, en cada región?", "Dos reconstrucciones", future work, and the old
mechanism/toy-model sequence (13–24 → 4 slides). Moved to backups: the five
counting-reconstruction slides (old 42–46). New: "Mecanismos: atenuación y respuesta del
detector" (f_att, local angles, κ = 1/0), "Mecanismos: divergencia cinemática" (Luce's figure
redrawn in TikZ with p along the axis, p_t opening outwards to scale, local ϑ_temp/ϑ_tard; α
≃ p_t/p and Cazón's p_t distribution; the boxed S(d, α); the three-factor ratio with a single
brace under the two late-favouring factors; a one-line geomagnetic note), "Un modelo de
juguete" (equation + linearised bracket, no Armbruster box), "La predicción del modelo"
(panel b + prediction box, framed as a starting point), "Simulaciones" (what used to be
"Herramientas", with a Dense Ring sketch), "El arreglo Infill: dos geometrías" (MC vs REC,
the core position is the main difference). AugerPrime: new photo of an upgraded station
(SSD + radio antenna; Pierre Auger Collaboration, arXiv:2507.07762), only "no las separa
físicamente". Slide 4 lost the multiplication bullet and "no es geométrico"; slide 8 lost
"lo retomamos en la fenomenología". Mass slide rebuilt around "no discrimina: los primarios
son comparables". Infill: "como el modelo" removed; figures enlarged on 23, 24 (right twin
axis cropped) and 27; "¿Qué estamos viendo?" says the particles are not the same, no
questions box; "Promedio por región" (no HIPÓTESIS badge, phrased as a proposal, last bullet
removed); Prueba 2 retitled, trigger-calibration phrasing, "lo esperado" removed;
"Discusión" with the UMD–SD decorrelation argument. Section titles renamed; "núcleo" →
"core" everywhere. REC-geometry slide retitled, first bullet removed; core-shift slide with
a bigger figure and the "¿Por qué?" folded into the first bullet; β slide reduced to one
bullet + table. Field-data slide: only the regenerated azimuthal profile
(`scripts/figura_datos_campo.py`: no fit result in the legend, "Fase II" in the cuts box,
PRELIMINAR watermark) and one sentence; the A1(r) panel became a backup. Conclusions
replaced by four points, no "Además". Slide numbers in revisions ≤ 19 below refer to the
53-slide version.

**Revision 19:** Pierre Auger Observatory logo added to the title slide, next to UBA and
ITeDA (`figuras/logo_auger.png`, rasterised from the official SVG served by the KIT Auger
site, iap.kit.edu/pierre-auger-observatory/img/auger-logo.svg).

**Revision 18 (final):** closing slide redone — full-screen background `figuras/auger_cr.jpg`
(shower over an SD tank with the Milky Way), "¡Gracias!" and "¿Preguntas?" top right with a
soft shadow. The image was replaced by the 1440×656 px version distributed by EurekAlert
(multimedia 770927: artist's impression by A. Chantelauze, S. Staffi, L. Bret, Pierre Auger
Observatory; usage "only with appropriate caption or credit"), and the credit line is on
the slide.

**Revision 17:** slide 49 trimmed — "En un rango razonable de r, la LDF de la reconstrucción
se puede aproximar como ρ ∝ r^−β", "recibe menos muones de los que le corresponde", "Es una
modulación en φ de signo opuesto a la física:", and the azimuth bullet no longer quotes
0.108 → 0.107 (have the numbers ready if asked).

**Revision 16 (final pass):** slide 49 — no "1%" phrasing; β presented as the local log-log
slope of any LDF (like those used in the reconstruction), measured on the same simulations;
the spurious modulation spelled out as "tempranas reciben menos, tardías más: modulación en
cos φ de signo opuesto que se resta a la verdadera"; the azimuth bullet rephrased as a
small parallax (~b/r ≈ 2°); first bullet folded into the second, one-line derivation.
Conclusions — p* removed; the analytic/toy model is described as confirmed by the
simulations, "una descripción fenomenológica bastante completa del signo y de las
tendencias".

**Revision 15:** slide 40 — table footnote removed, "A1 se invierte (A1 < 0)". Slide 49 —
"cerca de r" and "en un bin centrado en r" rewritten: ρ is the UMD muon density, β is the
log-log slope ("si r crece 1%, ρ baja β%"), measured on the same simulations; stations are
grouped by their *reconstructed* distance, an early one is really farther (r + b) and a late
one really closer (r − b). Flagged in the talking points: the table's β (2.9/2.7/2.5) does
not match the committed script's β (2.63/2.46/2.37, 300–650 m).

**Revision 14 (author's corrections 1–3):** slide 47 top-aligned (bullets higher); slide 48
plot raised, a bit of space before the bullets; slide 40 back to three steps — the key one
says the stations that enter carry more muons than their region's mean, with a much larger
excess on the late side, and the hypothesis is phrased as "little EM ⇒ hard to trigger ⇒ only
muon-rich stations get in".

**Revision 13 (author's corrections 1–4):** slide 40 redesigned again — retitled "¿Qué
estaciones entran, en cada región?", table reordered ("de cada 100 estaciones, forman parte
del evento", muons in the ones that enter / are left out, EM in the ones left out), the
"sin muones" row dropped, four numbered steps. Slide 47 says explicitly that the
*asymmetry* is computed with both geometries and names the table columns. Slide 48 states
the conclusion (core error along the early–late axis; b from the fit) instead of
describing the axes. Slide 49 explains where β comes from, adds b to the table, labels
simulation vs prediction, and drops the repeated bullets.

**Revision 12 (author's corrections 1–7):** slide 35 — bullets on the left, the questions
and a bigger meme appear together on the second page. Slide 36 — "sobre todo si cruza el
tanque de costado" removed. Slide 38 — 42%/18% bullet removed (moved into the table on
slide 40). Slide 39 — columns rebalanced, radial range removed from the caption. Slide 40 —
redesigned: centred table with the retained fraction, short bold phrases, the EM framed as
a working hypothesis, and the Simpson-type explanation of why late > early in both
subgroups but early > late overall. Slide 41 — "excluye el cero al 95%" removed, "el UMD no
tiene trigger propio" added. Slide 45 — "media global" removed.

**Revision 11 (author's corrections 1–3):** slide 34 — text column wider (bullets start
further left), the SD-muon bullet now says "desde ~600 m empiezan a disminuir y a partir de
~900 m son negativos", and the last bullet says it is the *total SD signal* that follows its
muons. Slide 35 — the meme is now small, in the top-right corner, and the text block is a
bit narrower so everything stays readable on the meme page. Slide 36 — caption removed.

**Revision 10 (author's corrections 1–7):** slide 35 without the small plot, centred, and a
second page where the "confused physics" meme pops up on top. New slide 36 on how an SD
station triggers (light → PMTs → threshold of the order of 1 VEM). Prueba 1 renamed
("sacando la selección de estaciones"), its second bullet now says the inversion
disappears and the SD muons behave like the UMD, no "bootstrap" mention, and the 42%/18%
bullet explains what it shows. Prueba 2 loses the "señal mínima" bullet. The medias slide
bullets now each point at a table row. Captions removed from Prueba 1 and the residual
slide. "(40°–65°)" removed from the error-by-region slide (45); the 35° split on the
bootstrap slide (46) was kept, since it is the result.

**Revision 9:** slide 34's bullets and conclusion moved up, away from the slide number
(top-aligned frame; the corner badge leaves an empty line at the top of every frame, which
is compensated on this slide).

**Revision 8 (author's corrections 1–2):** slide 30 drops "(no en esta tesis)" and its last
bullet now just says the trend agrees with the linearised model, which goes as r/D ⇒ A1
grows as D decreases (the term-by-term argument stays in the talking points above, for
questions). Slide 33's last bullet: with MC geometry it is not a core or coordinate error,
nor a mix-up of the stations' φ positions.

**Revision 7 (author's corrections 1–2):** slide 27 no longer says "puntuales hasta 15%"
("dentro de ±10% en casi todo el rango"). Slide 30 rewritten: the X_max plot is labelled as
an external Auger measurement, and the "smaller D ⇒ larger A1" step is spelled out (Δd ≈
2r tan θ_sh does not depend on D; dilution and response ∝ 1/D; attenuation independent of D;
s ≈ 1 for the muons that reach r).

**Revision 6 (author's corrections 1–3):** slide 9's "Herramientas" is a single paragraph and
sits lower. Slide 14 rebuilt on the v4 version: tan α again (it is what B&B use), the two
early/late bullets merged, the "ϑ: ángulo cenital…" bullet dropped, the plate bullet as
requested ("ve a una placa horizontal de área A como: A cos ϑ ⇒ la atraviesan N = nA cos ϑ
partículas"), the v4-style "Bertou & Billoir" box, and a new sketch in the style of the
kinematic-divergence figure (θ_sh = 50°, high production point, ϑ_early ≈ 0, same r marked
on the shower plane). Slide 15: no formula in the tank-count bullet, which now explains
why the top favours early and the side late; the signal bullet keeps its formula and gets
back "donde entran más muones, recorren menos agua".

**Revision 5 (author's corrections 1–5):** slide 9's "Herramientas" block simplified
(several hadronic models and primaries, Anillo Denso and Infill, + field data; no MC/REC
definition on screen). The two Bertou & Billoir slides were merged back into one (slide
14): sin α instead of tan α, a new rotated sketch (same r on both sides, ϑ = 12° vs 48°),
the plate bullet reworded ("la atraviesan N = nA cos ϑ partículas"), ρ and the effect on
the same slide, and the arrow-beam sketch dropped. Slide 15 (tank) gets the small
formulas A(ϑ) = tapa + costado and señal ∝ A · V/A = V. The box on slide 18 now just says
that a model has to include the real momentum spectrum of the muons. Slide numbers in
revisions 3–4 below refer to older versions.

**Revision 4 (author's corrections 1–2):** the "Simulaciones y reconstrucción" slide is
gone; its content (Anillo Denso, Infill, MC vs REC, production) moved into the
"Herramientas" block of slide 9. The shower-plane figure on slide 11 was moved down to
sit centred next to the text. Slide numbers in revision 3 below refer to the 54-slide
version.

**Revision 3 (author's corrections 1–8):** mechanism 2 now in three slides — why ϑ differs
early/late (ϑ = θ_sh ∓ α, with a sketch), how the plate geometry gives cos ϑ / cos θ_sh and,
to first order, Bertou & Billoir's ⟨p_t/(−p_z)⟩ tan θ_sh (same result, other variables), and
plate/tank/threshold with the tank explained in words; "¿Y con muones de todas las
energías?" box rewritten; the population-sign argument moved to its own slide (24) with a
sketch; "las amplitudes, no" removed; resolution/bias line removed from the simulation
slide; simulation badges now say ANILLO DENSO or INFILL (four titles shortened to fit);
"como en el modelo" removed from slide 28.

**Revision 2 (author's corrections 1–10):** thesis figure/equation numbers removed from all
slides (third-party credits kept); slide 4 rewritten (no FD, no X_max-vs-E plot, X_max
explained as particle number with an N(X) sketch, bigger components figure); FD duty cycle
on slide 5; neutral index; low-momentum attenuation sentence rewritten; mechanism 2 split;
"D finita" bullet now says why it matters; "reemplazando p_t"; ANALÍTICO badges removed;
toy model split into "ecuación" and "población", run parameters removed.

**Revision 1 vs. the RAFA deck:**
- Core-shift slide: the RAFA used `error_radial_azimut.jpg`, whose sign is **opposite** to
  thesis Fig. 5.2.5 (Δr ≈ −10 m early vs +9…+21 m). Only the thesis figure is consistent
  with Table 6.2.1 (if the core moved toward the late side, swapping r would *raise* A1).
- RAFA slide 28 mixed the LDF/core explanation with the counting bootstrap. Now separate.
- "MF" → S, from the thesis version of the figure.
- SD inversion is no longer "en verificación (HasStation)": it is the thesis's
  station-level analysis (Figs. 6.1.5, 6.1.6).
- Field-data number and bin replaced (RAFA: 0.067 ± 0.014, 4.8σ, 17.5–18.0, 750–900 m).
- "Una atmósfera completa" → "más de media atmósfera"; "extinguen por completo" →
  "despreciable"; geomagnetic 80° → 70°; removed "nacidos en las primeras generaciones".
- RAFA R24's component table was dropped: its numbers could not be traced to the thesis.

## To verify before the 16th

1. SD station-trigger thresholds, if the trigger comes up on slide 28: the thesis says
   "del orden de 1 VEM"; as far as I recall T1 ≈ 1.75 VEM peak and T2 ≈ 3.2 VEM peak plus
   time-over-threshold — check Abraham et al., NIM A 613 (2010) 29.
2. "Se empezó a instalar en 2018" — if you say the UMD deployment year aloud, check it.
3. β on slide 32: thesis table (2.9/2.7/2.5) vs committed script (2.63/2.46/2.37); see the
   talking points.
4. The 0.005 / 0.03 early/late residuals on the "error depende de la región" backup are read
   off thesis Fig. 5.2.3; the global mean 0.019 is printed on the plot.
5. Backup "datos de campo — región de referencia y fases" uses numbers from
   `Scripts/Procesamiento_Datos_Campo/resultados_cap7/` that are **not in the thesis**. Use
   it only if asked.
6. Slide 6 photo credit: taken from the arXiv source of "The Scintillator Surface Detector of
   the Pierre Auger Observatory" (arXiv:2507.07762, Fig. 1 right). Journal reference not
   checked; the slide cites the arXiv number only.
7. Slide 29's argument (the UMD fluctuation is independent of the tank's, so the SD trigger
   does not bias the UMD average to first order) is qualitative; the residual effect through
   position-in-bin and shower muon content is not quantified in the thesis.

## Likely questions (short answers)

- **¿Qué tan confiable es S ≈ 2.5?** σ(A1) comes from the fit with per-bin standard errors,
  treating stations of one shower (and the 5 Dense Ring resamplings) as independent. χ²≈1
  doesn't fully validate it. A shower-level bootstrap (as done in Ch. 6) is pending. →
  Backup "incertezas de A1".
- **¿La sensibilidad a la masa sobrevive en el Infill?** Not at this statistics with REC
  geometry: in the reference region p, He, Fe all ≈0.02. The Dense Ring result is the
  ideal-geometry one. → Backup "datos de campo — región de referencia".
- **¿El sobreconteo tardío es del algoritmo o del estimador?** The mean of (REC−MC)/MC is
  biased upward when N_MC is small, and the late side has fewer muons; part of the effect
  could be the estimator. Candidate for the >35° remnant (not tested): late muons arrive
  more inclined and cross more strips.
- **¿El modelo de juguete excluye toda explicación por propagación?** It is a point source at
  fixed D. Deeper production (smaller D) lowers p*. Answer: "dentro del modelo y para
  parámetros razonables".
- **¿Y Luce et al., que ven A1 levemente negativa para muones a 1500–2000 m?** Smaller and
  farther than here (thesis mentions it); whether their average used only triggered
  stations is worth knowing.
- **¿Por qué A1 crece al bajar D en la expresión lineal, si −s también crece?** The muons that
  reach r have p ~ QD/r, so s ~ pr/(QD) is roughly D-independent; the bracket stays ~fixed
  and A1 ∝ 1/D (the attenuation term gives r/λ, D-independent).
- **El UMD tiene umbral de ~1 GeV/c y p0 ≈ 0.95 GeV/c: ¿no quedan los muones del UMD cerca
  del cruce?** With attenuation and the plate response the crossover moves to ≈3.2 GeV/c
  (thesis Fig. 3.4.1 a), well above the UMD population; the full numerical model with the
  threshold still gives A1 > 0. The thesis also notes that raising the threshold makes A1
  *less* positive, not negative.
- **Exposición en φ en datos.** The cos φ exposure term is similar in data and MC (0.22 vs
  0.24 at 900–1200 m), so the data–MC comparison is like for like.
- **Fase I vs Fase II.** Cell-by-cell χ² = 103/53; Phase I has much less statistics. Open.
