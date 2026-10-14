# Speaker script — thesis defense, 16 Oct 2026

Deck: `presentacion_defensa_2026.pdf` (Spanish, 16:9 Beamer/metropolis, ITeDA palette).
Build: `./compilar.sh` (two pdflatex passes). Source: `presentacion_defensa_2026.tex`.
Target: 40–45 min. This note is in English per the repo convention; the lines to say
aloud are quoted in Spanish.

All data figures are copied from `Tesis - Latex/capitulos/imagenes_capitulos/`, so every
plot on screen is the exact one in the thesis. The slides do not cite thesis figure or
equation numbers (author's request); the "Thesis" column below keeps that mapping for you,
in case the jury asks where something is in the document. Third-party images keep a
one-line source credit (PDG, Botti, Haungs, Luce, Yushkov).

Slide numbers are the frame counter shown on screen (`n/53`); the 9 section-title pages
are not counted. "R#" = RAFA 2026 content slide number (the author's own counting).
Simulation slides carry a badge saying which topology they use: "SIMULACIONES -- ANILLO
DENSO" or "SIMULACIONES -- INFILL".

## Timing (≈43.7 min of content + ≈0.5 min of section dividers)

This is at the top of the 40–45 min window. The cut list below the table saves ≈3 min.

| # | Slide | Origin | Thesis | min |
|---|---|---|---|---|
| 1 | Portada | R1, modified | — | 0.3 |
| 2 | ¿Qué son los UHECR? | R2 | Fig. 1.1.1 | 0.8 |
| 3 | Estructuras del espectro | R3 (quick) | Fig. 1.1.2 | 0.4 |
| 4 | Anatomía de una lluvia y X_max | R5 + R4, rewritten | Fig. 1.2.1 + N(X) sketch | 1.2 |
| 5 | El Observatorio | R6 | Fig. 2.0.1 | 0.7 |
| 6 | AugerPrime | R7 | Fig. 2.1.1 | 0.4 |
| 7 | AMIGA / UMD | R8, fixed | Fig. 2.4.1 | 0.7 |
| 8 | ¿Por qué el UMD es distinto? | R9, fixed | §2.4 | 0.7 |
| 9 | Objetivos (+ herramientas) | new; absorbs R16/R17 | §1.3, Tabla 4.1.1 | 1.1 |
| 10 | Índice | new | — | 0.3 |
| 11 | Plano de la lluvia | R10 | Fig. 3.1.1 | 0.8 |
| 12 | El observable A1 | R15, moved up | Ec. 3.3.1 | 0.7 |
| 13 | Mecanismo 1: atenuación | R11 + math | Ec. 3.2.1–3.2.3 | 1.0 |
| 14 | Mecanismo 2: respuesta del detector | R12, rewritten (merged) | Ec. 3.2.4, §3.2.2 | 1.3 |
| 15 | Mecanismo 2: placa, tanque y umbral | R12, split (3/3) | Ec. 3.2.5, §3.2.2 | 1.0 |
| 16 | Divergencia: la producción | R13, rewritten | Ec. 3.2.6–3.2.7, Fig. 3.2.1 | 1.0 |
| 17 | Divergencia: del momento al ángulo | new | Ec. 3.2.8–3.2.9 | 1.2 |
| 18 | Divergencia: ¿temprana o tardía? | R14, rewritten | Ec. 3.2.10 | 1.2 |
| 19 | Campo geomagnético | new | §3.2.4 | 0.3 |
| 20 | Modelo de juguete | new | Ec. 3.4.1, 3.4.3, 3.4.4 | 1.0 |
| 21 | Del muón a la población | new | Ec. 3.4.2, 3.4.5 | 0.8 |
| 22 | Linealización | new | Ec. 3.4.6, Anexo A | 0.9 |
| 23 | ¿Qué signo tiene la población? | new | Ec. 3.4.7–3.4.8, §3.4.1 (end) | 1.0 |
| 24 | Resultados del modelo: la predicción | new | Fig. 3.4.1 | 1.0 |
| 25 | Anillo Denso: ejemplo | R18 | Fig. 5.1.1 | 0.6 |
| 26 | A1 vs θ: UMD y SD | R19 | Fig. 5.1.2 | 0.9 |
| 27 | Robustez | R20 (φ_sh + models) | Figs. 5.3.1, 5.3.2 | 0.5 |
| 28 | Protón vs. hierro | R21 → thesis figure | Fig. 5.5.1, Ec. 5.5.1 | 1.0 |
| 29 | Dependencia con la energía | from R20 | Fig. 5.4.1 | 0.5 |
| 30 | Interpretación: X_max | new | Fig. 5.6.1, Ec. 5.6.2 | 0.9 |
| 31 | ¿Por qué el SD va al revés con X_max? | new | Fig. 5.6.2, Ec. 5.6.1 | 1.0 |
| 32 | El UMD en el Infill | R22 | Fig. 6.1.1 | 0.7 |
| 33 | UMD vs. SD total | R23 | Fig. 6.1.3 | 0.7 |
| 34 | Desglose del SD | R24 (table removed) | Fig. 6.1.4 | 0.9 |
| 35 | ¿Qué estamos viendo? (2 pages: + meme) | new | Fig. 6.1.4 | 0.9 |
| 36 | ¿Cuándo dispara una estación del SD? | new | §2.1, §6.1.3 | 0.8 |
| 37 | Hipótesis de selección | new | §6.1.3 | 1.2 |
| 38 | Prueba 1: sacando la selección de estaciones | new, replaces R25 | Fig. 6.1.5 | 1.2 |
| 39 | Prueba 2: los tanques que quedan afuera | new | Fig. 6.1.6 | 1.2 |
| 40 | ¿Qué estaciones entran, en cada región? | new | §6.1.3 (text) | 1.0 |
| 41 | Qué queda abierto | new | §6.1.3 (end) | 0.6 |
| 42 | La pregunta (REC < MC) | R19 repeated | Fig. 5.1.2 | 0.5 |
| 43 | ¿Son los ajustes? | RAFA backup B1 | Fig. 5.2.1 | 0.6 |
| 44 | El residuo | R26, fixed | Fig. 5.2.2 | 0.9 |
| 45 | El error depende de la región | RAFA backup B2 | Fig. 5.2.3 | 0.7 |
| 46 | Bootstrap por región | R28, LDF text removed | Fig. 5.2.4 | 0.8 |
| 47 | En el arreglo real: segunda reconstrucción | new | Tabla 6.2.1 | 0.8 |
| 48 | El núcleo se corre hacia la temprana | R27 with thesis figure | Fig. 5.2.5 | 0.9 |
| 49 | El modelo de β | new | Ec. 6.2.1, Tabla 6.2.1 | 1.2 |
| 50 | Dos reconstrucciones, dos efectos | new | §6.3 | 0.6 |
| 51 | Datos de campo | R29, thesis numbers | Figs. 6.4.2, 6.4.3 | 1.0 |
| 52 | Conclusiones | new (by objective) | Cap. 7 | 1.0 |
| 53 | Trabajo futuro | new | Cap. 7 (last paragraph) | 0.5 |

If running long, cut in this order: 6 (AugerPrime), 3 (spectrum zoom), 27 (robustness →
backup), 19 (say it in one line on slide 18), 41 (one sentence at the end of 40),
43 (one sentence on 42). That saves ≈3 min.

## Talking points

**1–4 Rayos cósmicos.** Open with the flux (1/km²/siglo). Three open questions; "hoy
nos importa la composición". Slide 4 explains X_max with the N(X) sketch: first each
interaction multiplies the particles; once their energy drops below a critical value they
stop multiplying and the number falls. "X_max no es algo geométrico: la lluvia se sigue
abriendo como un cono después del máximo; lo que cae es la cantidad de partículas."
Close with ⟨X_max⟩ ∝ ln(E/A): deeper for higher energy and lighter primaries. The X_max vs
energy plot (Yushkov) appears only on slide 30, where it is used.

**5–8 Auger.** Keep brief. Slide 5 gives the duty cycles (SD ~100%, FD ~15%). On 7, say
"más de media atmósfera" (540 g/cm² vs ≈870 g/cm² vertical at Auger). On 8, the threshold
depends on the *local* angle of each muon, so it is higher for late muons: this seeds the
detector-response term.

**9–10 Objetivos e índice.** Three objectives as in the author's plan. Say aloud that
objective (c), the analytic model, came later: "surgió a posteriori, cuando vimos la
inversión del SD y necesitábamos entender qué esperar". The index is deliberately neutral:
just read the six items.
Slide 9 also carries the "Herramientas" block, which replaced the separate simulation
slide: official simulations with several hadronic models and primaries, in the Anillo Denso
(12 virtual stations at 450 m) and in the real Infill array, plus field data. MC vs REC is
no longer written on any slide (author's choice): say it aloud the first time it appears
(slide 26, A1 vs θ): "MC es la verdad de la simulación; REC, lo que entrega la
reconstrucción". If asked for details: SIBYLL 2.3e (main), QGSJET-III.01 and EPOS-LHC-R;
p/He/O/Fe; 10^17.5–10^18 eV.

**11–12 Plano y observable.** The observable comes before the mechanisms so that each
mechanism can be labelled "favorece temprana / tardía". "El signo de A1 dice qué domina,
no identifica a un mecanismo."

**13 Atenuación.** For muons, attenuation = survival against decay; λ_dec = 6.2 km × p/GeV.
"Como λ crece con el momento, un muón blando decae en un recorrido más corto; el camino
extra del lado tardío se lleva una fracción mayor de muones blandos que de energéticos."
λ in practice is effective. Favours early.

**14–15 Mecanismo 2 (respuesta del detector), two slides.**
14: Bertou & Billoir (2000, GAP-2000-017 — not Armbruster) assume a stationary shower. The
particles open out from the axis by an angle α, with tan α ≈ p_t/(−p_z) — the variable that
appears in their expression. (The kinematic-divergence slides use sin α = p_t/p: it is the
same angle written with another function, and to first order they coincide.) Opening outward
tilts the track toward the vertical on the early side, ϑ = θ_sh − α, and lays it down on the
late side, ϑ = θ_sh + α. The sketch exaggerates on purpose: a very inclined axis (θ_sh = 50°)
and a production point high up, so the early track arrives almost vertical (ϑ ≈ 0) and the
late one very inclined (~67°); the grey segments with tick marks on the shower plane show
that both points are at the same r — say it aloud, it is not written. (The sketch uses a
single production point, like the kinematic-divergence picture, to make the angles visible;
under B&B's stationary hypothesis the opening angle belongs to each particle, but the
geometric consequence — more vertical early, more inclined late — is the same.)
Then the plate: "un haz … ve a una placa horizontal de área A como A cos ϑ ⇒ la atraviesan
N = nA cos ϑ partículas". Projected along the axis, the plate covers A cos θ_sh of the
shower plane, so ρ = n cos ϑ / cos θ_sh (larger early, smaller late) — say this step aloud,
it is not on the slide. The Bertou & Billoir box: to first order in α,
cos(θ_sh ∓ α)/cos θ_sh ≈ 1 ± α tan θ_sh, which averaged over the particles gives their
⟨p_t/(−p_z)⟩ tan θ_sh: "el mismo resultado, en otras variables". Be ready to do the
expansion on the board.
15, *plate, tank, threshold.* The plate (UMD) feels the full effect. The tank is a 3D body.
Its top is horizontal, so it intercepts more muons the more vertically they arrive — the
early side; its side wall is vertical, so it intercepts more the more inclined they arrive —
the late side. They pull in opposite directions and almost cancel (κ ≈ 0.3). For the *signal*, each muon gives
light in proportion to its track in the water; where more muons enter, they cross less
water, and number × track = volume, so the signal is not modulated (κ = 0). Plus the UMD
threshold, higher on the late side.

**16–18 Divergencia cinemática (the core of the physics part).** Take your time.
16: "el mecanismo anterior trata a la lluvia como estacionaria; acá los muones nacen a una
distancia D sobre el eje, y entonces los puntos temprano y tardío quedan a distancias
distintas de la fuente". Cazón's p_t distribution, density ∝ 1/d². Same r ⇒ the late region
is farther and needs a smaller angle.
17: the Jacobian — the linear p_t cancels; then "reemplazando p_t = p sin α" and adding 1/d².
18: three factors. Dilution favours early; the two emission factors favour late. "El signo
lo decide la energía del muón." The box: a detector sums all energies; energetic muons come
out in a narrow cone and concentrate density where they land; so the sign depends on which
energies dominate among the muons that reach r, and that is what the toy model answers.

**19 Geomagnético.** One line: elliptical deformation, small projection on cos φ, adds
scatter; dominant only at θ ≳ 70°.

**20–24 Modelo de juguete.**
20: the equation; d(φ) is the distance from the source to the station that enters the
divergence and attenuation terms; α enters the emission factor, ϑ the response and the
threshold. "El muón llega al centellador si su momento alcanza para atravesar la tierra a
lo largo de su trayectoria; del lado tardío llega más inclinado, atraviesa más tierra y
necesita más momento."
21: the production spectrum is an inverse power law, p^−2.6: many soft muons, few energetic
ones; each region sums its own muons. The A1 box: S ∝ 1 + A1 cos φ gives ⟨S⟩(1+A1) early
and ⟨S⟩(1−A1) late, so A1 = (S_temp − S_tard)/(S_temp + S_tard).
22: the linearised bracket, one term per mechanism. Only −s is negative and it grows with
the muon momentum. Armbruster's expression (cited by Luce et al. ICRC 2021) is the κ = 0
case.
23: the sign of the population, in three steps. (1) A single muon flips to A1 < 0 only
above the crossover momentum p* = 2QD/r (≈1.9 GeV/c at 1200 m); attenuation and response
push it higher. (2) To reach r, a muon needs p_t ≈ p r/D, and Cazón suppresses large p_t as
e^(−p/p0), with p0 = QD/r. (3) p0 = p*/2: the muons that do arrive are below the crossover,
so the population gives A1 > 0. "Los muones que favorecerían a la región tardía son
justamente los que casi no llegan lejos del eje." The sketch shows exactly this.
24: results and the prediction box: "con esto en la mano, vamos a las simulaciones". The
sign survived varying D, Q and γ. (Model parameters, off the slides, if asked: D = 7.5 km,
Q = 0.15 GeV/c, p_UMD = 1 GeV/c, reference point r = 1200 m, θ = 35°. The amplitudes depend
on them and are not a prediction — say this only if asked.)

**25–26 Anillo Denso.** Say that these slides are in the Anillo Denso (the badge says it
too). 25: positive, as predicted. 26: SD above UMD at low θ (EM), below
at θ ≳ 50°. If asked why: κ = 0 for the tank signal vs κ = 1 for the plate. Plant: "fíjense
que REC está por debajo de MC — volvemos a esto".

**27 Robustez.** φ_sh-independent; SIBYLL vs QGSJET-III within ±10% over almost the whole
range (helium only). If asked: a few isolated bins reach 15% (thesis §5.3.2).

**28 Protón vs. hierro.** No "factor de mérito", no "composición de masa". S is a
difference of means in units of the combined uncertainty; it grows as √N. "No es una
separación evento a evento." Max ~2.5 at 40–55°.

**29–31 Energía y X_max.** p > Fe and A1 rising with E both point to a deeper X_max.
Slide 30: say first that the X_max plot is a published Auger FD measurement, not part of
this thesis. Then the argument, step by step: a deeper shower produces its muons closer to
the ground (smaller D). The path difference between the late and the early region,
d_tardío − d_temprano ≈ 2 r tan θ_sh (from d(φ) ≈ D − r tan θ_sh cos φ), is fixed by the
geometry and does **not** depend on D; what matters is how big it is compared with D. In the
linearised model, A1 ≈ [2 − s + D/λ + κ](r/D) tan θ_sh: the dilution and detector-response
terms go as Δd/D ∝ 1/D; the attenuation term is r tan θ_sh/λ, independent of D (it compares
Δd with λ, not with D); and the emission term s, at fixed momentum, would grow as 1/D² — but
the muons that actually reach r have p ~ QD/r, so s ≈ 1 for the arriving population and the
bracket stays roughly fixed. Net result: A1 ∝ 1/D, it grows when D shrinks. If someone
pushes: this is the point-source toy model, so it is a qualitative argument, not a
prediction of how much A1 changes between p and Fe. Slide 31: the EM component
follows the *gradient* of the longitudinal profile (→0 near the maximum, so it falls as the
shower gets deeper); the muons follow the *distance* (rises). Opposite trends with X_max,
consistent with what was reported for the SD (Bradfield). Present it as an interpretation
(HIPÓTESIS badge), not as a disagreement with Bradfield.

**32–34 SD (now in the Infill — say so).** 32: Infill, MC geometry, the UMD behaves as
predicted. 33: the SD total inverts far from the core; already reported, never explained;
appears with MC geometry, so it is not a core or coordinate error, nor a mix-up of the
stations' φ: r and φ are exact here. "Si la geometría está descartada, lo que queda es qué
medimos y sobre qué estaciones promediamos" — that sets up the next slides. 34: split by component — the EM is
positive everywhere; the SD muons are what inverts. Stop here.

**35 ¿Qué estamos viendo?** "Es la misma lluvia; uno está enterrado debajo del otro;
miramos lo mismo, los muones que cruzan el detector; el UMD coincide con el modelo, el SD
no." Next click (same frame, second page): the orange "Preguntas" box and the meme appear
together on the right. Ask the three questions, let the meme land, then move on.

**36 ¿Cuándo dispara una estación del SD?** Particles crossing the tank emit Cherenkov
light; three PMTs collect it; the signal is measured in VEM (the signal of a vertical muon
crossing the whole tank); if it passes a minimum threshold the station triggers and can
enter the event reconstruction. The slide says the threshold is "del orden de la señal de un
muón vertical (1 VEM)". Say it that way, not "exactly 1 VEM": as far as I recall the SD
station triggers are a threshold trigger of order 1.75 VEM peak in coincidence of the
three PMTs (T1) and 3.2 VEM peak (T2), plus time-over-threshold — check Abraham et al.,
NIM A 613 (2010) 29 before the defense. With the real values the argument is even stronger:
a lone muon often does not trigger. (The "sobre todo si cruza de costado" remark was removed
from the slide: it is not well founded — an inclined muon crossing the whole tank has a
*longer* track, so one could argue the opposite. Only corner-clipping muons have short
tracks. Don't bring it up.)

**37–41 Sesgo de selección (central result — the most time).**
37: the analysis averages only stations that triggered and belong to the reconstructed
event. The cartoon is illustrative: on the late side only the more muon-rich stations
enter, so the selected mean goes up and A1 flips "sin crear ni mover ningún muón".
Label it a working hypothesis.
38: the cleanest test — same counts, coordinates and fit; only the averaged population
changes. Without the selection the inversion disappears and the SD muons behave like the
UMD, positive at every r. +0.069 ± 0.016 (all) vs −0.124 ± 0.019 (selected) at 1200–1350 m.
Errors are a bootstrap over the 960 showers, if asked. (The 42% / 18% retained fractions
moved to the table on slide 40, where they are actually used.)
39: if it is selection, the excluded tanks should hold at most one muon (the trigger was
explained on slide 36): 95% / 93%, means 0.35 / 0.46. Say "a lo sumo uno", not "alrededor
de uno" — most have zero. "Being part of the event" also includes event-level triggers and
station rejection, not only the station trigger.
40, *¿Qué estaciones entran, en cada región?* Read the table top to bottom: of every 100
stations, 42 enter on the early side and only 18 on the late side (1200–1350 m band); the
ones that enter carry 1.49 and 1.69 muons; the ones left out carry 0.35 and 0.46; the late
ones left out have half the EM (14 vs 28). Then the three numbered steps:
(1) far fewer stations enter on the late side (18 of 100 vs 42);
(2) the stations that enter carry more muons than the mean of their region, and on the late
side that excess is much larger — so much that the late ones that enter even have more
muons than the early ones. The average over the stations that enter therefore overestimates
the late region, and that is what flips A1. The size of the excess, illustratively: the
regional means over all stations are early ≈ 0.42 × 1.49 + 0.58 × 0.35 ≈ 0.83 and late ≈
0.18 × 1.69 + 0.82 × 0.46 ≈ 0.68, so the selected early stations carry ~1.8× their regional
mean and the selected late ones ~2.5×. Caveat: the 42/18 fractions are from 1200–1350 m and
the means from 900–1500 m, so these ratios are only illustrative; the thesis states it
qualitatively ("las estaciones tardías retenidas están más enriquecidas en muones").
(3) working hypothesis: on the late side very little EM is left, so it is hard for a station
to trigger, and only the ones with far more muons than their region's mean get in. The
thesis says this does not prove the mechanism. Supporting number, not on the slide (the
author was not convinced by that row): between 900 and 1350 m, a station with zero muons
still enters 39% of the time on the early side and 18% on the late side.
The footer note is the band caveat plus "entrar = disparo + lectura + reconstrucción".
41: what remains — UMD still 0.03–0.06 above the SD muons at 150–900 m (if asked: the
difference excludes zero at 95% CL). The model predicts UMD > SD through κ. Third bullet:
the UMD has no trigger of its own — a module is read out only if the tank of its station
triggers, so the UMD curve is also built on selected stations. Back-of-envelope (not in the thesis, verify before quoting):
Δκ·(r/D)·tan θ ≈ 0.7 × 0.08 × 0.7 ≈ 0.04.

**42–50 La reconstrucción del UMD.** The story has two layers; keep them separate (the
badges help: 42–46 are Anillo Denso, 47–49 are Infill).
42–46 are the *counting* layer: fits are fine (χ²_ν ≈ 1); the residual has mean 0.013 and
**width** σ = 0.20 (say "ancho", not "±"); it is cut at −1 and unbounded upwards; a global
bootstrap fails; the residual depends on φ (≈0.005 early, ≈0.03 late; the 40–65° selection and the
global mean 0.019 are printed on the plot); a
φ-dependent bootstrap explains everything up to 35° and more than half above. "El
remanente queda abierto."
47–49 are the *geometry* layer. 47: we compute A1 of the *same* injected muons with the
true (MC) and the reconstructed (REC) geometry; with REC geometry the asymmetry almost
disappears (0.108 → −0.002 at 40–50°, 450–600 m). 48: the core position error points along
the same direction as the early–late axis — the reconstructed core moves toward the early
region — so early stations look closer to the REC core and late ones farther; the fit
Δr = a + b cos φ gives b = 9, 15, 21 m, growing with θ. Why: the LDF is symmetric in φ and
the only way to absorb the early excess is to move the core. 49: the β model. ρ is the UMD
muon density in the Infill (mean number of injected muons per station, MC truth), as a
function of the distance to the axis — the muon LDF. Near the bin it is approximated by a
power law ρ ∝ r^−β, so ln ρ = const − β ln r: β is the slope of ln ρ vs ln r, i.e. the
relative drop of density per relative increase of distance ("si r crece un 1%, ρ baja un
β%"). It is measured on the same set of simulated showers (per θ bin), exactly like b,
which also comes from the set (the fit of the mean Δr vs φ profile): neither is an
event-by-event quantity. How it is done in `Scripts/Cap5_corrimiento_nucleo.py`: mean muon
count per station in bins of *true* distance, then a straight-line fit of ln(count) vs
ln(r). In a REC radial bin the early station is really farther, at r + b (fewer muons), and
the late one really closer, at r − b (more muons), so ρ picks up a fake −β(b/r) cos φ and
ΔA1 ≈ −β b/r. **Check before the defense:** the β values on the slide (2.9, 2.7, 2.5) are
the thesis Table 6.2.1 values for the 450–600 m bin, but the committed script fits 300–650
m and gives β = 2.63, 2.46, 2.37 (`Scripts/resultados_cap5_corrimiento_nucleo/
estimacion_lavado_A1.csv`); I could not find the script that produced the table's β. With
the script's β the prediction at r = 450 m is −0.054, −0.085, −0.111, which agrees with the
simulation just as well, so the conclusion does not change — but know where each number
comes from if asked. The table now labels which column is the simulation (ΔA1 measured as REC −
MC geometry) and which is the prediction (−β b/r), and includes b: −0.110 vs −0.102 at
40–50°. Swapping only φ does nothing (0.108 → 0.107); it is the distance that kills it.
50: the core does **not** explain the counting bias — a module's muon count does not use
the core position. In the Dense Ring the stations sit at the true 450 m and the shift only
rotates φ by ~2°, the same for MC and REC.

**51 Datos de campo.** Use the thesis numbers: A1 = 0.063 ± 0.017, Phase II, 18.0–18.5,
**50–60°, 750–1250 m** (the caption of thesis Fig. 6.4.2 says 40–60° / 750–1050 m; the
code, the abstract and the conclusions say 50–60° / 750–1250 m). Max in the early region.
The A1(r) panel follows the reconstructed MC, including the negative near-core cells at
high θ — the β effect. Preliminary: no systematics yet, and no MC above 10^18 eV for the
headline bin.

**52–53 Conclusiones y futuro.** One block per objective, then the two instrumental
results. On the analytic model, the slide says its predictions (A1 > 0, growing with r and
θ, UMD above SD) were confirmed by the simulations and that it "parece una descripción
fenomenológica bastante completa del signo y de las tendencias". Keep that qualifier if
asked: the toy model predicts signs and trends, not amplitudes, and the SD inversion is not
a prediction of the model — it is a selection effect, which the model is consistent with
(propagation alone cannot produce a late excess). Future work is taken from the last
paragraph of `08_conclusiones.tex`.

**49, extra notes.** Is ρ ∝ r^−β "the LDF the Observatory uses"? Not literally: the
reconstruction LDFs are not pure power laws (the SD one is NKG-like). But over a narrow
range like 450–600 m any smooth LDF is well approximated by a power law, and β is its local
log-log slope; here it was measured directly on the simulated UMD muon counts, not taken
from the official LDF parameters. The approximation is first order in b/r ≈ 2–4%. The φ
bullet: the core shift also changes the azimuth seen from the reconstructed core (a
parallax), but only by ~b/r ≈ 2°, much smaller than the 30° φ bins, so using the
reconstructed φ does not change A1 (0.108 → 0.107); only the distance matters.

## Revision log

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

1. SD station-trigger thresholds (see slide 36 note).
2. "Se empezó a instalar en 2018" — if you say the UMD deployment year aloud, check it.
3. The 0.005 / 0.03 early/late residuals on slide 45 are read off thesis Fig. 5.2.3 (the
   text of the thesis does not quote them); the global mean 0.019 is printed on the plot.
4. Backup "datos de campo — región de referencia y fases" uses numbers from
   `Scripts/Procesamiento_Datos_Campo/resultados_cap7/` that are **not in the thesis**. Use
   it only if asked.
5. Slide 14's first-order step (ϑ = θ_sh ∓ α and the expansion behind the B&B box) is a re-derivation
   of Bertou & Billoir's result written for the talk; the thesis text (§3.2.2) gives the
   plate argument and the final expression but not the expansion step. It is standard, but
   be ready to do it on the board.

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
  (slide 24, panel a), well above the UMD population; the full numerical model with the
  threshold still gives A1 > 0. The thesis also notes that raising the threshold makes A1
  *less* positive, not negative.
- **Exposición en φ en datos.** The cos φ exposure term is similar in data and MC (0.22 vs
  0.24 at 900–1200 m), so the data–MC comparison is like for like.
- **Fase I vs Fase II.** Cell-by-cell χ² = 103/53; Phase I has much less statistics. Open.
