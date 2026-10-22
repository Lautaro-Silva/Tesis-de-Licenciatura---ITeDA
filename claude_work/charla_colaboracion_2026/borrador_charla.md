# Charla para la colaboración: borrador v1 (provisional)

**Para:** primera versión lista el lunes 26 de octubre de 2026.
**Estado:** esquema y diapositivas *provisionales*. Los tiempos están calculados para una charla de unos 20 minutos más preguntas, hasta que confirmes la duración real.
**Fuentes:** `Tesis - Latex/capitulos/05_anillo_denso.tex` y `06_infill.tex`, conclusiones (`08_conclusiones.tex`), y la defensa (`claude_work/presentacion_defensa_2026/guion.md` y su `.tex`). Las figuras están en `Tesis - Latex/capitulos/imagenes_capitulos/`. Todas las cifras que aparecen abajo están en esas fuentes. Las únicas excepciones son las de la diapositiva 13: son sumas y restas hechas sobre la Tabla 6.2.1 y están marcadas como derivadas.

**Deck:** `charla_colaboracion_2026.tex`, que compila con `./compilar.sh` y genera `charla_colaboracion_2026.pdf` (las slides) y `charla_colaboracion_2026_notas.pdf` (cada slide seguida de sus notas del orador). Usa la plantilla de la defensa (metropolis, paleta ITeDA). Las figuras están copiadas en `figuras/`. **Todas las figuras de datos tienen etiquetas en español** ("Lluvias de protón", "Geometría MC", "temprano/tardío", "todas las estaciones", "Tanques excluidos", "Datos", "Ajuste del primer armónico"…), así que para una charla en inglés conviene regenerarlas con etiquetas en inglés. Las principales salen de `Scripts/plots_seccion_6.py` (Cap. 6), `Scripts/validacion_rec_muones.py` (Anillo Denso) y `Scripts/Cap5_corrimiento_nucleo.py` (corrimiento del core).

**Revisión 5 (correcciones del autor, 22/10):** sin nota gris en la slide del observable; bullets del UMD antes que los del SD en la comparación del anillo denso; Test 2 más arriba; en "Recovering the asymmetry", el bullet "for data" explica las dos vías (parametrizar b(θ) en simulaciones y validarlo en simulaciones no vistas, o un ajuste de la LDF con término azimutal); conclusión 2 dice que la selección actúa estación por estación y que los tanques excluidos tienen "mostly" ≤ 1 μ; "Next steps" incluye la validación en simulaciones independientes.

**Revisión 4 (correcciones del autor, 22/10):** slide 2 distingue lluvia vertical (simetría circular) de inclinada (dos regiones); slide de simulaciones con tabla de modelos/primarios/energía/θ y un solo bullet del anillo denso; "Comparison: SD vs. UMD on the Dense Ring" con un bullet sobre N_REC vs N_MC; sin "True (MC) geometry" en la figura de A1(r); primer bullet de la comparación con el SD reescrito; "It is the SD muon component that inverts"; Test 1 sin la tabla ni la nota de errores (los números quedaron en las notas del orador); Test 2 con dos bullets (motivación y 95%/93%) y la figura más grande; tabla MC/REC con "A1 Monte Carlo" / "A1 Reconstructed" y "offset between the true and the reconstructed core positions"; slide del core con "can be fitted by" e "increasing with θ", sin b en las leyendas; tabla de recuperación sin la columna −βb/r (la predicción quedó en las notas).

**Revisión 3 (correcciones del autor, 22/10):** slide 2 describe las regiones temprana y tardía (en lugar de las configuraciones y MC/REC); ejemplo del anillo denso con "≈17% peak to peak (±8%)", sin nota gris; A1(r) del UMD ordenado por θ (<10° compatible con cero; 10–40° crece y se amesta; ≥40° crece); sección "The SD inversion and the selection bias"; Test 1 sin el bullet de fracciones retenidas (pasó al Test 2); Test 2 rehecho alrededor de la motivación (si es trigger, los tanques descartados deben tener ≤ 1 μ); tabla MC/REC con dos columnas y el azimut mencionado en un bullet; slide del core con figura más grande y "moving the core toward the early side, where there is more signal"; tabla de −βb/r sin "geom." ni "observed". Figuras nuevas en inglés: `Selection_Test1_EN.pdf`, `Selection_Test2_EN.pdf`, `Core_Shift_EN.pdf` (`scripts/figuras_ingles_seleccion_core.py`; reproducen 42%/18%, 95%/93%, 0.35/0.46, 1.49/1.69, b = 9.3/15.5/21.1 m).

**Revisión 2 (correcciones del autor, 21/10):** el deck (`charla_colaboracion_2026.tex`) es ahora la referencia para los textos de las slides; las secciones 4–5 de abajo describen la v1. Cambios:
- Slide 2 sin el bullet "isolated muon signal".
- Slide nueva "Simulations and the Dense Ring" (antes del ejemplo) y "The Infill array: two geometries" (entre A1 vs θ y A1(r)), traducidas de la defensa.
- Ejemplo del anillo denso con N_μ^MC (A1 = 0.083 ± 0.005). La figura de la tesis era N_μ^REC (A1 = 0.068 ± 0.006, que coincide con la curva REC del último bin).
- A1 vs θ: el SD queda por debajo del UMD solo a θ ≳ 60°; se eliminó el bullet "muons and EM carry different asymmetries".
- A1(r) del UMD: bullets reordenados, aclarado que es solo el UMD, "θ ≥ 40°: grows with r (40–50°: beyond ~1200 m)".
- Slide del SD retitulada "The SD comparison: inversion far from the core"; frase de la hipótesis de selección reescrita.
- Figuras de las slides 4, 5, 7, 8 y 9 regeneradas en inglés con `scripts/figuras_ingles.py` (mismos datos, bines y ajuste que el código de la tesis; los A1 reproducen los de la tesis).

Convención de este documento: lo que va en la diapositiva y en las notas del orador está en inglés. Los comentarios para vos están en español, con la marca **[ES]**.

---

## 0. Antes de armar las diapositivas: lo que encontré en las fuentes

**[ES] Son cosas que cambian lo que la charla puede afirmar. Conviene resolverlas antes del lunes.**

1. **El "procedimiento de recuperación" no está aplicado en la tesis.** La tesis hace tres cosas: (i) mide el corrimiento del core, Δr = a + b cos φ, con b ≈ 9, 15 y 21 m; (ii) deriva ΔA1 ≃ −β·b/r a partir de ρ ∝ r^(−β); (iii) verifica en la Tabla 6.2.1 (450–600 m, tres bines de θ) que esa predicción coincide con la pérdida observada. Después dice que el efecto "podría corregirse o incluirse en la comparación con los datos" (§6.3 y conclusiones). Nunca se corrió el core por b para recalcular r, y no hay una curva A1(r) "corregida". Por eso, en el borrador, la diapositiva de recuperación es un **test de cierre analítico**: A1_REC + β·b/r comparado con A1_MC, con números derivados de la tabla. No la presento como una corrección aplicada. Si tenés resultados posteriores a la tesis en los que corriste el core, pasámelos y reescribo esa diapositiva.
   - Con esos números, el cierre da 0.062 vs 0.062, 0.083 vs 0.086 y 0.100 vs 0.108. El modelo explica el 100%, el 96% y el 93% de la pérdida.
   - **Ojo:** el test usa el número de muones **inyectado** (N_μ^MC). El sesgo del conteo reconstruido (N_μ^REC, entre un 5 y un 23% menos de A1 con geometría MC) es otro efecto y no está incluido en la corrección.

2. **β tiene dos procedencias que no coinciden.** La Tabla 6.2.1 usa β = 2.9, 2.7 y 2.5. El script commiteado, `Scripts/Cap5_corrimiento_nucleo.py` (ajuste entre 300 y 650 m), da β = 2.63, 2.46 y 2.37, y evalúa la predicción en r = 450 m: −0.054, −0.085, −0.111 (`resultados_cap5_corrimiento_nucleo/estimacion_lavado_A1.csv`). La predicción de la tabla se reproduce con los β de la tabla evaluados en r ≈ 520 m, el centro del bin. Si se usan los β del script en el centro del bin, la predicción baja a −0.047, −0.073 y −0.095. Es decir, **el acuerdo depende del rango del ajuste de β y del r efectivo del bin en un 10–15%.** En una charla para la colaboración alguien lo va a preguntar. Recomendación: mostrar números cuyo origen puedas abrir en pantalla. Lo más honesto es decir "agreement at the 10% level" y no presentarlo como exacto. No encontré el origen de los β de la tabla en el repo.

3. **"HasStation" es la condición de "forma parte del evento reconstruido".** En el pipeline es `sEvent.HasStation(sdId)` (`Procesamiento_ADST_v8-2.py:182`, `readADST_data_v19.py:157`). La tesis advierte que ese requisito resume el disparo, la lectura y la reconstrucción de la estación, y que esas etapas **no se separaron**. Por eso el borrador dice "selection", no "trigger", en lo que se presenta como establecido.

4. **Umbral de trigger.** La tesis dice que los triggers están "configurados en 1 VEM". Esta audiencia conoce los triggers (T1/T2 por umbral, ToT y, en el Infill, ToTd/MoPS), y el propio `guion.md` marcaba esa frase como dudosa (por ejemplo, T1 ≈ 1.75 VEM pico, según Abraham et al., NIM A 613 (2010) 29). **No pongas un número de VEM en la diapositiva sin verificarlo.** El borrador lo formula como "a tank crossed by at most one muon, with little EM signal, is unlikely to pass the station trigger", que no depende del valor exacto.

5. **"Sin HasStation se recupera algo parecido al UMD" tiene un matiz.** Sin la selección, los muones del SD vuelven a ser positivos en todo r (entre +0.03 y +0.07). Pero entre 150 y 900 m el UMD queda 0.03–0.06 por encima, y esa diferencia excluye el cero al 95%. Hay que decir "same sign and trend", no "same values". Además, la curva del UMD también está calculada sobre estaciones con HasStation, y no se tiene su conteo en las estaciones no retenidas.

6. **La figura del Anillo Denso no es "MC pura".** La figura de ejemplo (`cap5/Ajuste_UMD_REC_Bin9.pdf`) usa N_μ^REC. Las estaciones están a 450 m del eje **verdadero**, así que el radio es MC, y el azimut se rota ~b/r ≈ 2°. La figura de A1 vs θ (`cap5/Evolucion_Asimetria_vs_Theta.pdf`) muestra MC (verde) y REC (azul). Si querés que la primera diapositiva sea solo N_μ^MC, habría que regenerar el ejemplo con `Scripts/validacion_rec_muones.py`. Ver la decisión D2.

7. **Los parámetros de la posible extensión.** "β" es la pendiente local log-log de la LDF muónica del UMD (ρ ∝ r^(−β)). El otro parámetro que entra en la corrección es **b**, la amplitud del término en coseno de Δr(φ) = a + b cos φ, es decir, el corrimiento medio del core hacia la región temprana. Mi suposición es que "el otro parámetro" de tus notas es **b**, pero **confirmámelo** (podría ser "a", el término constante del mismo ajuste). Para la diapositiva de trabajo futuro: b = 9.3, 15.5 y 21.1 m en 20–30°, 30–40° y 40–50° (`ajuste_corrimiento_nucleo.csv`). Con solo esos tres puntos, b/tan θ ≈ 20, 22 y 21 m, o sea que b crece aproximadamente como tan θ. **Es una observación sobre tres valores, no una parametrización validada.** La pongo en las notas, no en la diapositiva. La energía está integrada en 17.5 ≤ lg E < 18.0, así que no corresponde hablar de dependencia con la energía.

8. **La tesis tiene un bin del dato de campo inconsistente** (solo importa si incluís datos de campo, ver D3). La leyenda de la Fig. 6.4.2 dice 40–60° y 750–1050 m. El código, el resumen y las conclusiones dicen 50–60° y 750–1250 m (A1 = 0.063 ± 0.017).

---

## 1. Mensaje central

> **In simulations, the muon density measured by the UMD has a robust positive early–late asymmetry. What an analysis actually measures depends on two analysis-level effects: the station selection, which flips the sign of the SD muon asymmetry far from the core, and the reconstructed core position, which nearly cancels the UMD asymmetry near the core. The second effect follows a simple, predictable form, ΔA1 ≈ −β b/r. Accounting for it brings the reconstructed asymmetry back to the Monte Carlo reference.**

[ES] En una frase para decir en voz alta: *"The asymmetry is there; the selection and the core position hide it, and we understand how."*

## 2. Título

**Recomendado:**
> **Early–late asymmetry of the muon density with the UMD: selection bias, core reconstruction, and how to recover it**

Alternativas:
- *Where does the muon asymmetry go? Station selection and core reconstruction in the UMD and SD*
- *The muon early–late asymmetry seen by the UMD: from simulation truth to reconstructed geometry*

## 3. Esquema narrativo (provisional)

Cada bloque termina con la pregunta que abre el siguiente.

| Bloque | Qué establece | Pregunta que deja abierta |
|---|---|---|
| A. Reference | Con geometría MC, el UMD ve A1 > 0, que crece con θ (Anillo Denso, r = 450 m). | ¿Cómo depende de r? |
| B. Radial dependence | Infill con geometría MC: A1 crece con r para θ ≥ 50° y es positiva y ~plana para 30–50°. | ¿El SD ve lo mismo? |
| C. SD inversion | El SD total se invierte lejos del core, y la inversión viene de sus muones. | ¿Física o análisis? |
| D. Selection bias | Sin HasStation, la inversión desaparece. Los tanques excluidos tienen ≤ 1 μ. | Con eso entendido: ¿qué pasa con cantidades REC? |
| E. REC geometry | Mismas estaciones, mismos muones: con r_REC, A1 desaparece en 450–600 m. | ¿Por qué? |
| F. Core shift | El core REC se corre ~b hacia la región temprana. En la LDF eso da ΔA1 ≈ −βb/r. | ¿Se puede deshacer? |
| G. Recovery | A1_REC + βb/r ≈ A1_MC al nivel de ~10%. Qué necesita y qué falta para aplicarlo a datos. | (Trabajo futuro: b(θ), β(θ)) |

## 4. Gráficos

**Esenciales (diapositivas principales):**

| Figura | Archivo (`imagenes_capitulos/…`) | Diapositiva |
|---|---|---|
| Ajuste armónico en el Anillo Denso | `cap5/Ajuste_UMD_REC_Bin9.pdf` (o regenerada con N_μ^MC, ver D2) | 3 |
| A1 vs θ, Anillo Denso (UMD MC/REC, SD) | `cap5/Evolucion_Asimetria_vs_Theta.pdf` | 4 |
| A1(r) por bin de θ, Infill, geometría MC | `cap6/Global_A1_vs_R_Theta_MC.pdf` | 5 |
| UMD vs SD total, 30–40° | `cap6/UMD_vs_SD_Total_Asymmetry.pdf` | 6 |
| Desglose del SD (EM / μ) vs UMD | `cap6/SD_Desglose_Componentes_vs_UMD.pdf` | 7 |
| Con y sin HasStation | `cap6/SD_Seleccion_Estaciones_vs_UMD.pdf` | 9 |
| Muones en tanques excluidos/retenidos | `cap6/SD_Muones_Tanques_Excluidos.pdf` | 10 |
| Tabla MC/REC (r, φ intercambiados) | Tabla 6.2.1 (rehacer como tabla en la diapositiva) | 11 |
| Δr vs φ con ajuste a + b cos φ | `cap5/corrimiento_nucleo_azimut.pdf` | 12 |
| Predicción vs observado, y cierre | Tabla 6.2.1 + columna derivada | 13 |

**Respaldo:**
- Grillas de ajustes, MC y REC (`anexo/Anexo_Grilla_MC_*.pdf`, `Anexo_Grilla_REC_*.pdf`): para "show me the fits".
- UMD N_μ^MC vs N_μ^REC con geometría MC (`cap6/UMD_Asymmetry_MC_vs_REC.pdf`), sesgo direccional del conteo (`cap5/directional_bias.pdf`) y toy model bootstrap (`cap5/toy_model.pdf`): el *otro* efecto de la reconstrucción.
- χ²_ν de los ajustes del Anillo Denso (`cap5/Chi2_Reduced_Fits.pdf`).
- Robustez: φ_shower (`cap5/DenseRing_Systematics_Isotropy.pdf`) y modelos hadrónicos (`cap5/Hadronic_Uncertainty_Helium.pdf`).
- Resolución de la reconstrucción (`cap4/energy_bias.pdf`, `phi_bias.pdf`, `theta_bias.pdf`).
- Procedencia de β (diapositiva con los dos conjuntos de valores, ver punto 0.2).
- (Opcional, D3) Datos de campo PRELIMINARES: `claude_work/presentacion_defensa_2026/figuras/datos_campo_preliminar.pdf` y `cap6/cap7_A1_vs_r_datos_vs_mc.pdf`.

---

## 5. Diapositivas (provisionales)

Tiempos orientativos para unos 20 minutos de contenido. Muestra común a todo, salvo que se indique otra cosa: protones, SIBYLL 2.3e, 17.5 ≤ lg(E/eV) < 18.0, producción oficial CORSIKA + Offline ("icrc2025-test7").

---

### Slide 1: Title (0.3 min)

**Title:** Early–late asymmetry of the muon density with the UMD: selection bias, core reconstruction, and how to recover it

**On slide:** name, affiliations (ITeDA / UBA), meeting and date.

**Speaker notes:**
"This talk is about the azimuthal asymmetry of the muon density, measured underground with the UMD. I'll show that the asymmetry is clearly there in simulations, then show two analysis effects that can hide it or even flip its sign, and finally how we can account for one of them."

**Transition:** "Let me first say what we measure."

---

### Slide 2: The observable: A1 in the shower plane (1.2 min)

**Goal:** fijar convenciones y el marco (MC vs REC) en un minuto, para una audiencia que conoce el detector pero no el análisis.

**Figure:** shower-plane sketch with early (φ = 0) and late (φ = ±180°) regions (podés reutilizar el de la defensa: `cap3/esquema_lluvia.jpeg`).

**On slide:**
- Fit the azimuthal profile of the muon density at fixed r:
  ρ(φ) = ⟨ρ⟩ (1 + A1 cos φ)
- φ: station azimuth in the shower plane; φ = 0 is the early region.
- A1 > 0: early excess. A1 < 0: late excess.
- Known for the total SD signal; here, for the first time, with an isolated muon signal (UMD).
- **MC** = true core and direction; **REC** = Offline reconstruction.

**Speaker notes:**
"The asymmetry of the total SD signal in inclined showers is well known. The question here is what happens with muons alone, which is what the UMD gives us: shielded, so free of the electromagnetic component. The observable is the first-harmonic amplitude A1 of the muon density in the shower plane. A positive A1 means more muons on the early side. A1 is fitted on an ensemble of showers, not event by event. Throughout the talk I'll use 'MC' for the true core and direction from the simulation, and 'REC' for what the reconstruction gives us, which is what we have in real data."

**Transition:** "We start in the cleanest setup we have."

---

### Slide 3: Reference: a clear modulation on the Dense Ring (1.2 min)

**Goal:** que la audiencia *vea* la asimetría antes de cualquier complicación.

**Figure:** `cap5/Ajuste_UMD_REC_Bin9.pdf`: 12 virtual stations, 59.3° ≤ θ < 65°, harmonic fit.
[ES] Esta figura usa N_μ^REC. Si la mantenés, decilo en voz alta (ver D2).

**On slide:**
- Dense Ring: 12 virtual UMD stations at r = 450 m from the **true** axis, every 30° in the shower plane.
- Fixed r: no LDF gradient inside the ring.
- Clear first-harmonic modulation: early–late difference ≈ 14% (±7% around the mean).

**Speaker notes:**
"To isolate the effect we use a synthetic setup: twelve virtual stations placed in the simulation at 450 meters from the true shower axis, every thirty degrees. The radius is fixed, so the steep fall of the lateral distribution cannot fake a modulation. In the most inclined bin the muon density on the early side is about fourteen percent higher than on the late side, and a single cosine describes it well."
[ES] Si es la figura con N_μ^REC: "These are reconstructed muon numbers; with the injected ones the amplitude is somewhat larger, as the next plot shows."

**Transition:** "How does it change with zenith angle?"

---

### Slide 4: A1 grows with zenith angle, and the UMD and SD differ (1.0 min)

**Figure:** `cap5/Evolucion_Asimetria_vs_Theta.pdf`.

**On slide:**
- UMD: A1 > 0, growing with θ.
- SD total signal: larger A1 at low θ (EM-dominated), drops below the UMD at θ ≳ 50°.
- Muons and EM particles carry different asymmetries.

**Speaker notes:**
"The muon asymmetry is positive and grows with inclination. The SD total signal starts much higher, because at low zenith angles it is dominated by the electromagnetic component, which is strongly attenuated after the shower maximum. At large angles the electromagnetic part is mostly absorbed and the SD asymmetry falls to the level of the UMD or below. The gap between the green and blue UMD curves comes from the muon-counting reconstruction; I won't discuss it today, but it's in the backup."

**Transition:** "The ring only gives us one radius. To study the radial dependence we need the real Infill array."

---

### Slide 5: Radial dependence on the Infill (MC geometry) (1.5 min)

**Goal:** establecer la referencia A1(r, θ) con la que se compara todo lo que sigue.

**Figure:** `cap6/Global_A1_vs_R_Theta_MC.pdf`.

**On slide:**
- Real SD-750 / UMD stations; r and φ computed from the **true** core and direction.
- Bins: Δr = 150 m (r < 150 m excluded), 12 bins of 30° in φ, θ in 10° bins (last one 50–65°).
- θ ≥ 50°: A1 grows with r out to 1500 m.
- 30–50°: A1 ≈ 0.1 by ~600 m, then roughly flat.
- θ < 10°: compatible with zero.

**Speaker notes:**
"Now we use the real Infill stations, still in simulations and still with the true core and direction. The distance to the axis now varies, so we can follow A1 as a function of r. For very inclined showers the asymmetry keeps growing all the way out to fifteen hundred meters. At intermediate angles, thirty to fifty degrees, it is positive and rises to about 0.1 near six hundred meters, then stays roughly flat. Near-vertical showers show no significant asymmetry. This is our reference: what an ideal analysis should find."

[ES] Notas:
- Lo de "aproximadamente plana" sale de leer la figura: lo corregiste así en la revisión 23 de la defensa. El texto de la tesis (§6.1) dice "crecimiento monótono" para 40–65°, pero la curva de 40–50° solo vuelve a subir más allá de ~1200 m, donde la estadística es baja. Si te preguntan, contestá con la figura.
- Si alguien pregunta por el toy model del Cap. 3: predice que A1 crece con r. La meseta de 30–50° es una discrepancia con el modelo, y la tesis la declara.

**Transition:** "What does the surface detector see in the same showers?"

---

### Slide 6: The SD total signal inverts far from the core (1.0 min)

**Figure:** `cap6/UMD_vs_SD_Total_Asymmetry.pdf` (30–40°, MC geometry).

**On slide:**
- Same showers, same MC geometry, 30° ≤ θ < 40°.
- UMD: positive at all distances.
- SD total: maximum, then decreases and becomes **negative** far from the core.
- MC geometry → not a core or direction error.

**Speaker notes:**
"Same showers, same true geometry. The UMD stays positive at all distances. The total SD signal does something very different: it peaks, then decreases, and far from the core it becomes clearly negative, with an excess on the late side. Since the core and direction are the true ones, this cannot be a reconstruction error."

**Transition:** "Which part of the tank signal is responsible?"

---

### Slide 7: It is the SD muons that invert (1.0 min)

**Figure:** `cap6/SD_Desglose_Componentes_vs_UMD.pdf`.

**On slide:**
- EM component of the SD: positive at all r.
- Muons in the SD (MC count): positive near the core, negative beyond ~900 m.
- Same quantity, muons crossing a detector, with the opposite behaviour in the UMD and the SD.

**Speaker notes:**
"Splitting the tank signal with the simulation truth, the electromagnetic part is positive everywhere. The muon part is what inverts, and the total SD signal follows it far from the core. So we are comparing the same physical quantity, muons crossing a detector, and getting opposite signs in the UMD and in the SD. Our analytic model of muon propagation does not produce a negative asymmetry at these distances, so we looked at how the observable is built."

[ES] El argumento del toy model (p* ≃ 2QD/r, términos de propagación positivos) va en las notas, no en la diapositiva. Una inversión parecida, más chica y a mayor distancia (|A1| ≲ 0.05 a 1500–2000 m), la reportan Luce et al. (ICRC 2021). Bradfield 2022 también ve la inversión del SD.

**Transition:** "The key point: we never average over all stations."

---

### Slide 8: Hypothesis: the station selection biases the average (1.2 min)

**Goal:** plantear la hipótesis como propuesta, con el mecanismo genérico.

**Figure:** esquema (el cartoon de la diapositiva "Promedio por región" de la defensa, o uno nuevo): región temprana con todas las estaciones retenidas; región tardía con solo las ricas en muones.

**On slide:**
- A station enters the analysis only if it **belongs to the reconstructed event** (`HasStation`).
- If the probability of entering depends on the station's own muon content, and differently on the early and late sides, the regional averages are biased.
- Late side: weaker EM signal, so mainly muon-rich stations enter, and the late average is pulled up.
- This can flip the sign without moving a single muon.

**Speaker notes:**
"Every curve so far is an average over stations that are part of the reconstructed event. For the UMD that seemed natural, since it has no trigger of its own. But suppose the chance that a station is kept depends on how many muons it has. On the early side the electromagnetic signal is strong enough that almost every station is kept, whatever its muon content. On the late side the electromagnetic part is more attenuated, so mostly the stations with more muons survive. The late average is pulled up, and the measured asymmetry can change sign, although no muon was created or moved. This is a hypothesis; the next two slides test it."

**Transition:** "The direct test is to remove the requirement."

---

### Slide 9: Test 1: without HasStation, the inversion disappears (1.5 min)

**Figure:** `cap6/SD_Seleccion_Estaciones_vs_UMD.pdf`.

**On slide:**
- Same MC muon counts, same coordinates, same fit; only the set of stations changes.
- All simulated stations: SD muons positive at all r (+0.03 to +0.07).
- HasStation only: 1200–1350 m: **−0.124 ± 0.019** vs **+0.069 ± 0.016** over all stations.
- Fraction kept at 1200–1350 m: 42% early, 18% late.
- Errors: bootstrap over the 960 showers (stations of a shower kept together).

**Speaker notes:**
"Here we take exactly the same Monte Carlo muon counts in the tanks, the same coordinates and the same fit, and only change which stations enter. Over all simulated stations the SD muon asymmetry is positive at all distances, between plus three and plus seven percent. Requiring the station to be in the reconstructed event changes nothing up to about 750 meters, where practically every station is kept, and then drives the asymmetry down to minus 0.12 at twelve to thirteen hundred meters. In that band only forty-two percent of the early stations and eighteen percent of the late ones are kept. The errors come from a bootstrap over showers. So the sign flip is a property of the station sample."

[ES] Matiz que conviene decir en voz alta: sin selección, los muones del SD tienen el mismo signo y la misma tendencia que el UMD, pero no los mismos valores. Entre 150 y 900 m el UMD está 0.03–0.06 por encima (excluye el cero al 95%). Una candidata es la respuesta de un detector plano frente a la de un tanque, más el umbral del UMD; está abierto. Lo pongo en la diapositiva 10.

**Transition:** "If this is a selection effect, the stations we lose should be the ones with very few muons. Let's check."

---

### Slide 10: Test 2: the excluded tanks hold at most one muon (1.5 min)

**Goal:** mostrar la evidencia de plausibilidad y separar explícitamente lo observado de su interpretación.

**Figure:** `cap6/SD_Muones_Tanques_Excluidos.pdf` (excluded vs retained, early |φ| < 60°, late |φ| > 120°, 900 ≤ r < 1500 m).

**On slide (dos columnas):**

*Observed*
- Excluded tanks: ≤ 1 muon in 95% (early) / 93% (late) of cases; mean 0.35 / 0.46.
- Retained tanks: mean 1.49 (early) / 1.69 (late): late > early, opposite to the true density.
- Excluded late tanks have about half the EM particles of excluded early ones (14 vs 28).
- 900–1350 m: a tank with **zero** muons is kept in 39% (early) vs 18% (late) of cases.

*Interpretation (hypothesis)*
- A tank crossed by at most one muon, with little EM signal, is unlikely to pass the station trigger.
- The EM signal decides which stations are kept; on the late side only muon-rich tanks survive.
- **Not proven:** HasStation combines trigger, readout and station reconstruction; we did not separate these stages.

**Speaker notes:**
"We count the Monte Carlo muons crossing the tanks that are left out. Ninety-five percent of the excluded early tanks and ninety-three percent of the late ones have at most one muon. The excluded late tanks actually have slightly more muons than the early ones, but about half the electromagnetic particles. So on the late side we lose tanks that on the early side would have been kept thanks to their electromagnetic signal. As a result, among the kept tanks the late ones carry more muons than the early ones, even though the true muon density is higher on the early side. This is what we observe. The interpretation, that these tanks fail the trigger, is plausible: one muon and little electromagnetic signal is not much for a station to trigger. But HasStation also includes readout and reconstruction, and we have not separated them, so I present the trigger as a hypothesis, not as a demonstrated mechanism."

[ES] No pongas "1 VEM" sin verificarlo (punto 0.4).

**Transition:** "So far we have used the true core and direction. In real data we only have the reconstructed ones. What happens then?"

---

### Slide 11: With the reconstructed geometry, the UMD asymmetry vanishes near the core (1.5 min)

**Goal:** aislar el efecto de la geometría: mismos módulos, mismos muones inyectados, mismas condiciones de selección; solo cambia de dónde salen r y φ.

**Figure:** tabla rehecha a partir de la Tabla 6.2.1 (UMD, N_μ^MC, 450 ≤ r < 600 m):

| θ | (r_MC, φ_MC) | (r_MC, φ_REC) | (r_REC, φ_MC) | (r_REC, φ_REC) |
|---|---|---|---|---|
| 20–30° | 0.062 | 0.061 | 0.011 | 0.011 |
| 30–40° | 0.086 | 0.084 | 0.002 | 0.002 |
| 40–50° | 0.108 | 0.107 | −0.001 | −0.002 |

**On slide:**
- Same modules, same injected muons; only the geometry changes.
- Reconstructed azimuth: no effect.
- Reconstructed **distance**: the asymmetry is lost almost completely.
- Farther out (40–50°, 600–1050 m): A1 ≲ 0.05 with REC vs ≈ 0.11 with MC.

**Speaker notes:**
"Now we take the same UMD modules and the same injected muon numbers, and only change the geometry used to compute each station's distance and azimuth. Swapping in the reconstructed azimuth does essentially nothing. Swapping in the reconstructed distance wipes out the asymmetry: at forty to fifty degrees it goes from 0.108 to zero. Farther from the core it survives, but reduced to less than half. So the loss is not a random smearing of the azimuth: it comes from the distance to the reconstructed core."

[ES] Para respaldo: grillas REC (`anexo/Anexo_Grilla_REC_*.pdf`) y A1 REC por régimen (§6.2). Ventana donde A1_REC sigue siendo medible: 600 ≤ r < 1200 m, 20° ≤ θ < 55°.

**Transition:** "So where is the reconstructed core?"

---

### Slide 12: The reconstructed core is shifted toward the early region (1.5 min)

**Figure:** `cap5/corrimiento_nucleo_azimut.pdf`.

**On slide:**
- Radial error of each Infill station, Δr = r_MC − r_REC, vs its true shower-plane azimuth (r_REC < 1400 m).
- Clear cosine modulation: Δr(φ) = a + b cos φ.
- Early stations reconstructed closer to the core, late stations farther away.
- b ≈ 9, 15, 21 m for θ = 20–30°, 30–40°, 40–50°: it grows with θ, comparable to the core resolution.
- Likely cause: the reconstruction LDF is symmetric in φ, so it absorbs the early excess by moving the core.

**Speaker notes:**
"For each station we compare its distance to the true and to the reconstructed core, as a function of its true azimuth. If the core error were random, this would be flat. Instead it follows a cosine: early stations are placed closer to the core than they are, late stations farther. That is the signature of a systematic shift of the reconstructed core toward the early side. The amplitude b of the cosine fit is the mean size of that shift: about nine, fifteen and twenty-one meters, growing with zenith angle. A likely reason is that the LDF used in the reconstruction is symmetric in azimuth. Faced with more signal on the early side, the only thing the fit can do is move the core toward it."

[ES] La causa (LDF simétrica) es una propuesta de la tesis ("Se propuso como causa…"), no una demostración. Por eso dice "likely cause".

**Transition:** "What does a shift of this size do to the LDF, and to A1?"

---

### Slide 13: A shifted core adds a cos φ term to the LDF: ΔA1 ≈ −β b/r (2.0 min)

**Goal:** la derivación en una línea, el test cuantitativo y el cierre (recuperación).

**On slide:**
- Locally ρ ∝ r^(−β). A station at reconstructed distance r is really at r + b cos φ:
  ρ(r + b cos φ) ≈ ρ(r) [1 − β (b/r) cos φ]
- This spurious modulation has the opposite sign: **ΔA1 ≈ −β b/r**.

| θ | A1 (MC geom.) | A1 (REC geom.) | ΔA1 observed | −β b/r | A1_REC + β b/r * |
|---|---|---|---|---|---|
| 20–30° | 0.062 | 0.011 | −0.051 | −0.051 | 0.062 |
| 30–40° | 0.086 | 0.002 | −0.084 | −0.081 | 0.083 |
| 40–50° | 0.108 | −0.002 | −0.110 | −0.102 | 0.100 |

\* Derived from the thesis table (450 ≤ r < 600 m, injected muons).

- The shift explains 93–100% of the loss; adding it back recovers the MC reference to within ≲ 0.01.

**Speaker notes:**
"Locally the muon LDF falls as a power law with slope beta, between about 2.4 and 2.9 at these distances. If the reconstructed core is shifted by b toward the early side, a station that we place at distance r on the early side is really at r plus b, so it has fewer muons than we think, and a late station has more. To first order this multiplies the LDF by one minus beta b over r times cos phi: a cosine modulation with the opposite sign to the physical one. So the reconstructed asymmetry should be lower by beta times b over r. With b from the previous slide and beta measured on the same simulations, the prediction matches the observed loss in the three zenith bins. Read the other way, if we add beta b over r back to the reconstructed value, we recover the Monte Carlo reference within about 0.01."

[ES] Antes del lunes: resolvé la procedencia de β (punto 0.2). Si mostrás los β del script, la columna de predicción cambia (−0.054/−0.085/−0.111 a 450 m; −0.047/−0.073/−0.095 en el centro del bin). Mi recomendación para la diapositiva: "agreement at the ~10% level", y no "exact".

**Transition:** "So what would it take to apply this to real data?"

---

### Slide 14: Recovering the asymmetry: what it needs and what is missing (1.5 min)

**Goal:** decir con claridad qué es establecido, qué depende de MC y qué falta para aplicarlo a datos.

**On slide:**

*What the correction needs*
- **b(θ)**: the mean core shift along the early–late direction. *Currently measured with MC truth* (r_MC − r_REC).
- **β**: the local slope of the muon LDF. *Currently from MC*; in principle measurable from the UMD LDF in data.
- Two equivalent ways to apply it: move the core back by b, or add β b/r to A1.

*What is established*
- The loss is systematic, not a resolution effect, and its size is predicted by β b/r (tested at 450–600 m, 20–50°).

*What is not yet done*
- Moving the core and recomputing A1(r) over the full radial range.
- Other primaries, hadronic models and energies (tested: p, SIBYLL 2.3e, 17.5–18.0).
- The muon-counting bias (N_μ^REC vs N_μ^MC, 5–23% at fixed geometry) is a separate effect, not included.
- For data: b without MC truth, from simulations matched to data, or by removing the shift at the source with an LDF fit that includes an azimuthal term.

**Speaker notes:**
"The correction has two ingredients. The slope beta is a property of the lateral distribution and could in principle be measured from the data themselves. The shift b is the delicate part: so far we measure it by comparing with the true core, which only exists in simulations. So to apply this to data we either take b from simulations that reproduce the data, which brings a model and composition dependence we haven't studied yet, or we remove the shift at its origin, with a reconstruction LDF that allows an azimuthal modulation. At Infill energies the station multiplicity makes that hard event by event, but it is worth trying for the most energetic events. I also want to be clear about the scope: the test is done in one radial bin, for protons with one hadronic model, and with injected muon numbers. The counting bias of the UMD reconstruction is a separate, smaller effect."

[ES] "Moving the core back by b" es la forma de aplicar la corrección que pediste en el punto 6. La tesis **no** la ejecutó (punto 0.1). Si llegás a calcularla antes del lunes, esta diapositiva y la 13 pasan a mostrar A1(r) corregida vs MC.

**Transition:** "Let me summarize."

---

### Slide 15: Conclusions (1.2 min)

**On slide:**
1. In simulations the UMD muon density has a positive early–late asymmetry; it grows with r for inclined showers and is roughly flat at intermediate angles.
2. The SD muon asymmetry inverts far from the core only when averaging over stations in the reconstructed event (HasStation). Over all stations it is positive. The excluded tanks hold ≤ 1 muon: consistent with a trigger effect, not yet proven.
3. With the reconstructed geometry the UMD asymmetry nearly vanishes near the core, because the reconstructed core is shifted toward the early region by b ≈ 9–21 m.
4. This loss is predicted by ΔA1 ≈ −β b/r, and adding it back recovers the MC reference at the ~10% level. Applying it to data requires b without MC truth.

**Speaker notes:**
"Four points. The muon asymmetry is there, and it behaves as expected with zenith angle and distance. What we measure depends on how we build the observable: which stations we average over can flip the sign, and the reconstructed core can erase it. The second effect is simple and predictable, so it can be accounted for, and the comparison between data and simulation must use the same station selection and the same geometry. The open step is to determine the core shift without Monte Carlo truth."

**Transition:** → Slide 16 (future work) o directamente a preguntas.

---

### Slide 16 (opcional / cierre): Future work (0.8 min)

**On slide:**
- Parametrize the correction parameters as a function of zenith angle: b(θ) and β(θ) (at fixed energy, 17.5 ≤ lg E < 18.0).
- Apply the full correction (core shift + LDF term) over the whole radial range and compare with the MC reference.
- Check the dependence on primary and hadronic model.
- Separate trigger, readout and reconstruction inside HasStation.
- Apply to field data.

**Speaker notes:**
"The natural next step is to parametrize b and beta as functions of zenith angle, so that the correction can be applied without a per-bin Monte Carlo comparison. Our sample is at a single energy range, so this would be a zenith-angle parametrization only, not an energy one."

[ES] b/tan θ ≈ 20–22 m en los tres bines (punto 0.7): si te preguntan, es una observación sobre tres puntos. Confirmame el nombre del segundo parámetro.

---

## 6. Respaldo sugerido (en orden)

1. **Counting reconstruction:** `cap6/UMD_Asymmetry_MC_vs_REC.pdf` (geometría MC, N_μ^MC vs N_μ^REC, 40–50°): 5–23% menos de A1, misma forma. Más `cap5/directional_bias.pdf` y `cap5/toy_model.pdf` (el bootstrap reproduce REC hasta θ ≈ 35°; por encima explica la mitad o dos tercios de la degradación, y el remanente queda abierto).
2. **Fit grids:** MC y REC, 30–40° y 40–50°.
3. **Fit quality:** `cap5/Chi2_Reduced_Fits.pdf`.
4. **Robustness:** φ_shower; SIBYLL vs QGSJET-III dentro de ±10% en casi todo el rango.
5. **Reconstruction performance:** energía y dirección.
6. **β provenance:** los dos conjuntos de valores y sus predicciones.
7. **Dense Ring and the core shift:** por qué el corrimiento del core *no* afecta al anillo (estaciones a 450 m del eje verdadero; solo rota φ en ~b/r ≈ 2°).
8. (D3) **Field data, PRELIMINARY.**

---

## 7. Preguntas probables de la colaboración

**Trigger y selección**

- *"Are you sure it's the trigger and not the station reconstruction or the readout?"* No. HasStation mezcla las tres cosas y no las separamos. Lo que sí está establecido: (i) la inversión desaparece al promediar sobre todas las estaciones; (ii) las estaciones excluidas tienen ≤ 1 μ en el 93–95% de los casos y la mitad de partículas EM del lado tardío. Eso hace plausible el trigger, pero no lo demuestra. El próximo paso es mirar las flags de trigger de cada estación (T1/T2, ToT, ToTd, MoPS) y separar las estaciones disparadas de las reconstruidas.
- *"What trigger threshold are you assuming?"* Ninguno en particular. [ES] Verificá los umbrales actuales del SD-750 antes de citar números.
- *"Is the UMD also biased by the SD trigger?"* El UMD no tiene trigger propio: un módulo se lee si dispara el tanque de su estación. Pero la selección actúa sobre las partículas *del tanque*, no sobre los muones que cruzan el módulo enterrado (otra superficie, otra posición, bajo ~2.3 m de tierra). Al primer orden, entonces, el conteo esperado del UMD sigue siendo la densidad local. Puede quedar un efecto residual a través de lo que comparten (la posición dentro del bin de r y el contenido muónico de la lluvia), que no cuantificamos. Además, no tenemos el conteo del UMD en las estaciones no retenidas de esta producción.
- *"Does this explain the inversion seen by Luce et al. / Bradfield?"* Es una explicación candidata para cualquier análisis que promedie sobre estaciones disparadas. Luce et al. reportan una inversión más chica y a mayor distancia (|A1| ≲ 0.05, 1500–2000 m). Habría que saber si su promedio usó solo estaciones disparadas. No lo afirmamos.
- *"Only 30–40° and protons?"* Sí, el test de selección se hizo en ese bin y con esa muestra. Generalizarlo a otros θ, primarios y modelos está pendiente.

**Comparación de muestras**

- *"Are the MC and REC samples the same events and stations?"* Sí. La Tabla 6.2.1 usa los mismos módulos y el mismo número de muones inyectado, y solo cambia la geometría (r, φ). Las condiciones de selección no cambian.
- *"Why does the SD without selection still differ from the UMD?"* Entre 150 y 900 m el UMD está 0.03–0.06 por encima (excluye el cero al 95%). Candidatas: la respuesta de un detector plano frente a la de un tanque y el umbral del UMD, más alto para trayectorias tardías. Está abierto.
- *"How are the errors computed?"* Para el test de selección, bootstrap sobre las 960 lluvias, con las estaciones de cada lluvia juntas. En los ajustes del Infill y del Anillo Denso, el error de la media por bin, tratando las estaciones como independientes. [ES] Esto último es lo que un referee cuestionaría. La versión con bootstrap por lluvia en todos los ajustes está pendiente.
- *"Statistical significance of the core-shift fit?"* b tiene un error estadístico de ~0.13–0.16 m (ajuste sobre 42–54 mil estaciones); la dispersión estación a estación es ~19, 21 y 27 m (`perfil_corrimiento_nucleo.csv`).

**Uso de información Monte Carlo**

- *"Your correction uses the true core. How is that usable?"* Tal como está, b se mide con la verdad MC. Es un test de que entendemos la pérdida, no todavía una corrección para datos. Para datos: b tomado de simulaciones que reproduzcan los datos (con dependencia de modelo y composición, no estudiada) o eliminar el corrimiento desde la reconstrucción.
- *"Does b depend on composition / hadronic model?"* No lo sabemos: solo se midió en protones con SIBYLL 2.3e. Si la causa es la asimetría de la señal que la LDF simétrica no modela, cabría esperar que b dependa de la asimetría total del SD (y por lo tanto de θ y del contenido EM). Esto es una hipótesis.
- *"Where does β come from, and how sensitive is the closure to it?"* Pendiente lo del punto 0.2. Dependiendo del rango del ajuste de β y del r efectivo del bin, la predicción cambia ~10–15%.

**Aplicabilidad a datos reales**

- *"Have you applied it to data?"* No. [ES] Si incluís D3: en datos de Fase II hay una modulación positiva preliminar, A1 = 0.063 ± 0.017, sin corrección del core y sin estudio de sistemáticas.
- *"Could you fit an azimuthal term in the LDF directly?"* Es la vía que la tesis propone para eliminar el corrimiento desde el origen. La multiplicidad de estaciones del Infill a 10^17.5–10^18 eV lo hace difícil evento a evento; es razonable intentarlo con los eventos de mayor energía.
- *"Does the correction matter far from the core?"* Escala como 1/r. A 1000 m, con los valores del script: −0.024, −0.038, −0.050 (`estimacion_lavado_A1.csv`). Sigue siendo comparable a la señal, así que importa en todo el rango del Infill. [ES] Estos números salen del script, no del texto de la tesis.

---

## 8. Decisiones abiertas

- **D1. Duración.** ¿Cuánto dura la charla y si ese tiempo incluye preguntas? El borrador asume ~20 min de contenido (16 diapositivas). Para 12–15 min: fusionar 3+4, 6+7 y 13+14, y mandar la 16 a respaldo. Para 30 min: devolver al cuerpo la diapositiva del conteo REC (respaldo 1) y la de calidad de ajustes.
- **D2. Primera figura del Anillo Denso.** (a) Usar la de la tesis (N_μ^REC) y decirlo, o (b) regenerarla con N_μ^MC para que sea "MC pura", como pediste. La (b) produce una figura nueva que tendrías que revisar.
- **D3. Datos de campo.** Tu historia cierra con la recuperación y no incluye datos. Para una audiencia de la colaboración, una diapositiva final PRELIMINAR (o en respaldo) con la primera observación en el UMD es un gancho fuerte. Tiene el problema de bines del punto 0.8 y no tiene sistemáticas.
- **D4. ¿Corremos la corrección completa antes del lunes?** Con los parquet existentes (sin PyROOT, en el `venv`, minutos de CPU) se puede recalcular A1(r) con el core REC desplazado por b(θ) en la dirección tardía, en todos los bines radiales, y compararlo con MC. Las diapositivas 13 y 14 pasarían de un test analítico en un bin a una recuperación mostrada en todo el rango. Sería un resultado nuevo, no de la tesis, y tendrías que validarlo.
- **D5. Segundo parámetro de la extensión.** Confirmá si es b (amplitud del coseno en Δr) u otro.
