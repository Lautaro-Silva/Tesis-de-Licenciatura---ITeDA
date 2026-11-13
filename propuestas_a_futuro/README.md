# Future proposals

Ideas, extensions and checks that came up after the thesis was submitted (supervisor's review of
the UMD Foundations Meeting talk, jury and co-director comments, November 2026). None of these is
in the thesis or required for the talk. Quotes are verbatim (Spanish); the rest is a working note.

**Start here:** `hoja_de_ruta_ICRC2027.md` is the complete, prioritized list of open items
(this file, the thesis future-work lines, and what came out of the talks), organized toward an
ICRC 2027 contribution. The sections below keep the detailed proposals and the original messages.

Related material:
- `claude_work/charla_colaboracion_2026/sugerencias_charla_foundations.odt`: the supervisor's full
  review of the talk.
- `claude_work/charla_colaboracion_2026/figuras_charla.py`: all talk figures. Its
  `rec_geometry` block already computes A1(r) with the true and the reconstructed core, the local
  slope β and the prediction −βb/r.

---

## 1. A1(r) with the true and the reconstructed core in one panel

Proposed by the supervisor as a replacement for the 450–600 m table of the "REC geometry" slide:

> Un detalle práctico: en vez de la tabla, mostraría un gráfico de A₁ vs. r con las dos curvas,
> geometría MC y REC, superpuestas en el mismo panel, para 40°–50°. Así el patrón se ve en lugar
> de enunciarse: las curvas se separan cerca del núcleo y convergen hacia afuera, y la brecha entre
> ellas es el sesgo, que visiblemente se cierra con r. Eso es exactamente lo que predice βb/r, y el
> lector lo lee de un vistazo. Tiene además la ventaja de la continuidad con la diapositiva 7, que
> ya muestra la curva MC: repetir ese panel con la REC encima hace la comparación inmediata y
> justifica retrospectivamente el "this is our reference".
>
> Un solo bin cenital, el de 40°–50°, que es donde el efecto es mayor y donde tenés la grilla del
> backup para respaldar; las seis curvas de zenit harían el panel ilegible. El eje y tiene que
> incluir valores negativos y conviene marcar el cero con una línea, porque el cambio de signo
> cerca del núcleo es parte del mensaje. Los tres números de 450–600 m (0,108 → −0,002) no los
> perdería: son el caso más dramático y quedan bien como anotación sobre el gráfico o como un
> bullet, porque un valor concreto ancla lo que la curva muestra cualitativamente.

Status: a candidate figure exists,
`claude_work/charla_colaboracion_2026/figuras/Rec_vs_MC_A1_vs_r_40_50_EN.pdf` (injected muons,
40–50°, 150–1500 m). With the true core A1 ≈ 0.07–0.12 up to 1200 m; with the reconstructed core
−0.03 below 450 m, −0.002 at 450–600 m, 0.03–0.04 at 600–1200 m, and the two curves approach each
other beyond 1200 m (0.09 vs 0.15, 0.18 vs 0.25). Whether it replaces the table in the talk is
still to be decided.

## 2. Test −βb/r as a function of r, not in one bin

Supervisor, explicitly as an exploration, not for the talk:

> Una cosa más, pero planteada como exploración y no como algo que tenga que estar en la charla:
> valdría la pena probar un panel inferior con la diferencia A₁^MC − A₁^REC en función de r, con
> la curva βb/r superpuesta. Hoy la verificación de la fórmula está hecha a un solo radio —la
> tabla es toda a 450–600 m—, así que extenderla en r sería un resultado nuevo y bastante más
> convincente que tres números en un bin.

His caveats, from the same review: the expansion is first order in b/r and breaks near the core
(0–150 m, b/r ≈ 0.28, and the reconstructed core can fall inside the bin); β is not constant (the
muon LDF steepens with r), so it must be evaluated bin by bin; and beyond ~1200 m the errors on A1
are 0.03–0.11, comparable to ΔA1 itself. Expected outcome: agreement in 450–1200 m, failure at the
ends, and the slide should then state the range of validity.

First look (from the numbers in item 1, β held at its 450–600 m value of ≈ 2.5): the observed gap
is 0.089, 0.070, 0.062, 0.063, 0.061 at 675, 825, 975, 1125, 1275 m, while βb/r gives 0.078, 0.064,
0.054, 0.047, 0.041. The gap shrinks more slowly than 1/r, consistent with β growing with r. Not
checked with a bin-by-bin β yet.

## 3. Apply the core correction to field data

Once b(θ) and β(θ) are parametrized (or using the local slopes measured on the LDFs themselves),
correct the reconstructed core position in field data, event by event, by b toward the late side,
recompute A1(r), and check whether part of the asymmetry lost near the core is recovered — the
direct data counterpart of the simulation closure test. Open questions: b is today measured with
MC truth; its dependence on primary and hadronic model is unknown (validate the parametrization on
simulations not used to build it, as in a train/test split); and the field-data LDF slope may
differ from the simulated one (muon deficit).

## 4. Event-level bootstrap for the core-shift errors

The errors on b (0.1–0.2 m) come from a fit to the per-bin means weighted by the standard error of
the mean, which treats the stations as independent. Stations of one shower share the same core
error, so these errors are underestimated. Redo them with a bootstrap that resamples events, as is
already done for A1. The supervisor also asked for this; it does not change the conclusion (the
trend with θ is far larger than any plausible error) but it is the correct error.

## 5. Correct the trigger selection with a likelihood (jury recommendation)

File: `Correccion_seleccion_trigger_A1.pdf` (working notes from one of the jury members,
16 Oct 2026, 6 pages). Message that came with it, sent to the supervisor:

> Hola Juan
>
> Che, te paso por acá lo que comentaba sobre como corregir la reconstrucción sabiendo que lo que
> están mirando es una probabilidad condicionada a que dispare el tanque. Si le encontrás algún
> sentido y/o utilidad y querés charlarlo con más detalle avisame.

Summary of the notes: the measured quantity is E[N | x, T = 1] instead of E[N | x], and by Bayes
the difference is Cov(N, ε)/ε̄, where ε(n, x) is the selection efficiency; it depends on φ through
the electromagnetic component, which is what flips the sign of A1. Two likelihoods that model the
selection: a truncated one (only selected stations, each divided by its selection probability) and
a censored one (also uses the stations that did not trigger, as censored observations). A toy MC
tuned to the thesis retention fractions reproduces the inversion (Â1 = −0.098 with true A1 = 0.07)
and the censored likelihood recovers +0.070 ± 0.015; the censored version is also much more robust
to a ±15% error in the EM model of ε than the truncated one. The notes extend the model to the UMD
with a hierarchical model where the UMD and tank counts share the local muon density.

Co-director's reply:

> Uy, super interesante. Me da la sensación, en lectura diagonal, que en la reconstrucción del SD
> se usa lo que Dario llama en 2.2. la Verosimilitud censurada (completa). Pues incorpora las
> estaciones "silenciosas" en la likehood. Nosotros no podemos hacer eso pues no tenemos estaciones
> que simplemente no hayan superado una condición dada de trigger, pues no auto-triggereamos.
> Nuestros ceros, son ceros posta, como discutimos con Diego justo antes de la defensa.
>
> Es muy didáctico y me parece excelente idea tratar de incorporar esto. Para los detalles
> estadísiticos, incluyamos a Diego que de eso mangia mucho.

Note for whoever picks this up: the co-director's point is that the UMD cannot use the censored
form directly, because it has no trigger of its own — a UMD module that reads zero did not fail a
threshold, it saw zero muons. The jury notes' section 3 handles exactly this case: the selection
acts on the tank (N_S and the EM signal), and the UMD count enters only through the shared local
density; the non-selected stations need only be known to exist. Worth discussing with the
statistician the co-director mentions.
