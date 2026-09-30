# Capítulo 3 unificado — notas del borrador (30/09/2026)

Borrador para revisar. **No modifica `Tesis - Latex/`**. Leer el PDF `vista_previa.pdf`
(sólo el capítulo 3, 17 páginas) junto con estas notas.

## Contenido de la carpeta

| Archivo | Qué es |
|---|---|
| `03_fenomenologia.tex` | El capítulo. Se puede copiar tal cual a `Tesis - Latex/capitulos/` (ver "Cómo integrarlo"). |
| `vista_previa.tex` / `vista_previa.pdf` | Compilación del capítulo solo (pdflatex + biber, sin referencias indefinidas). |
| `capitulos/imagenes_capitulos/cap3/` | Figuras con las mismas rutas que en la tesis: el esquema de la GAP (`esquema_lluvia_gap.jpeg`), la figura de Luce, y las tres figuras nuevas de los modelos de juguete. |
| `toy_models/toy_models_cap3.py` | Genera las tres figuras y todos los números de la Sección 3.4. Sólo numpy/matplotlib, corre en segundos en cualquier máquina, no usa datos. `toy_models_cap3_salida.txt` es su salida. |
| `bibliografia_adicional.bib` | Dos entradas nuevas: `Armbruster2018` (GAP-2020-066) y `Billoir2002b` (GAP-2002-074). |

## Estructura y de dónde viene cada parte

| Sección del borrador | Origen |
|---|---|
| Intro del capítulo | CINEMATICA, con una oración nueva que anuncia 3.4 y 3.5. |
| 3.1 Plano de la lluvia, regiones temprana/tardía | CINEMATICA textual (sólo typos). **Figura cambiada por la de la GAP** (caption nuevo: ya no hace falta la aclaración de ζ). |
| 3.2 intro | CINEMATICA + un párrafo nuevo que define `d(φ)` para una fuente puntual (lo usan todas las subsecciones). |
| 3.2.1 Atenuación | CINEMATICA + párrafo nuevo **"Modelado analítico"** (Armbruster). Dos frases suavizadas, ver "Cambios de texto". |
| 3.2.2 Efectos geométricos (Billoir) | CINEMATICA textual + dos párrafos nuevos: relación de A_geo con cos ϑ, y **"La respuesta depende del detector"** (el argumento de Billoir 2002 del tanque). |
| 3.2.3 Divergencia cinemática | CINEMATICA hasta su Ec. 3.4 (cociente tardío/temprano), **con la derivación de dN/dΩ de la GAP vieja** (dΩ, regla de la cadena, cancelación de p_t). Todo lo que seguía después de la Ec. 3.4 en CINEMATICA se eliminó (E\*, derivada respecto de E, Poblaciones A/B, el filtro, los números +0.16/+0.02). Se reemplazó por un párrafo corto sobre qué factor gana, y otro corto **"De un muón a una población"** (la ponderación, sin fórmulas). |
| 3.2.4 Geomagnético | CINEMATICA textual (ver punto de réferi abajo). |
| 3.3 Parametrización armónica | CINEMATICA, movida antes de los modelos de juguete (porque éstos usan A1). Dos frases corregidas. Los dos párrafos históricos del final se movieron a 3.6. |
| **3.4 Modelos de juguete** | Nueva. Reemplaza lo que había después de la Ec. 3.4 en CINEMATICA y la sección 3.2.5 de INTEGRADO. |
| **3.5 Del flujo incidente al observable seleccionado** | Nueva versión, simplificada, de la 3.3 de REVISION/INTEGRADO. Marcada como propuesta. |
| 3.6 Antecedentes y motivación | Los dos últimos párrafos de CINEMATICA, sin cambios. |

**Numeración de ecuaciones:** la "Ec. 3.4" de CINEMATICA (el cociente tardío/temprano) ahora es
la **Ec. 3.11**, porque se agregaron las ecuaciones de la atenuación y la derivación de la GAP.

**Imagen que mencionaste:** en el mensaje no llegó ninguna imagen adjunta. Interpreté "algo tipo lo
de la imagen" como un párrafo corto, sin fórmulas, después del cociente. Es el párrafo
**"De un muón a una población"** (pág. 8). Si la imagen mostraba otra cosa, pasámela y lo ajusto.

## Ronda 2 (30/09/2026, tras tus comentarios sobre la Sección 3.2)

Nueva estructura de la 3.2:

| Sub | Título | Qué cambió |
|---|---|---|
| intro | — | Se sacó el párrafo "Para fijar ideas… fuente puntual". La fórmula de d(φ) pasó a la divergencia cinemática, donde la tenía la GAP vieja (con `tanθ` en vez de `sinθ`, explicado en una nota al pie). |
| 3.2.1 | Atenuación atmosférica | Se sacó el párrafo "Si bien los muones poseen un gran poder de penetración…". Se sacó el subtítulo "Modelado analítico", la integral de supervivencia, la fórmula con pérdida de energía y la ecuación de A1_att. Queda: exponencial de Armbruster (Ec. 3.1), de dónde sale para muones y cuánto vale λ (Ec. 3.2), λ como parámetro efectivo, y una frase: la atenuación pesa más en los muones blandos. |
| 3.2.2 | Proyección geométrica del flujo | Antes estaba dentro de "Efectos geométricos". Ec. 3.3 escrita como en tu imagen, con ⟨⟩_⊥ y dependencia en θ. Se sacó "Conviene remarcar… nunca en su contra". El párrafo "Físicamente…" se reescribió sin el modelo de fuente puntual, apoyándose en θ_early > θ_late de la figura nueva. |
| 3.2.3 | Respuesta del detector: conteo y señal | Nueva subsección. Tres casos (UMD plano / conteo en tanque / señal VEM del tanque) y una síntesis. |
| 3.2.4 | Divergencia cinemática | Título cambiado. Empieza con el párrafo de Bradfield/Luce (antes al final de Billoir). Texto sin cambios hasta la Ec. 3.10, salvo la inserción de d(φ) (Ec. 3.9). "De un muón a una población" queda pendiente de discutir. |
| 3.2.5 | Geomagnético | Sin cambios. |

- Figura 3.2: ahora es la de la GAP (`divergencia_angular_gap.png`), con α_early/α_late,
  d_early/d_late y θ_early/θ_late.
- El cociente tardío/temprano (tu "Ec. 3.4" de CINEMATICA) ahora es la **Ec. 3.10**.
- Las etiquetas LaTeX viejas (`subsubsec:divergencia`, etc.) se conservaron: el Cap. 6 actual las
  referencia. `subsubsec:divergencia` ahora apunta a la proyección geométrica, que es a lo que se
  refería.

---

## 1. Atenuación: de dónde sale el modelado analítico

Tenés razón en que Armbruster (GAP-2020-066, Sec. 2.3.2, Ec. 2.11) sólo usa

    f_att(L) = exp(−L/λ)

con λ una longitud de atenuación. (Ojo: es **−L/λ, no −L/γ**. En Armbruster, γ es el exponente de
la distribución angular, ADF ∝ α^−γ. Son dos parámetros distintos.) Armbruster no deriva esa
exponencial: la toma como hipótesis y usa λ = 29–36 km, citando al PDG.

La integral que aparecía en REVISION/INTEGRADO,
`P = exp[−∫ ds / (βγ(s) c τ_μ)]`, es la **probabilidad de que un muón no decaiga** en su trayecto
(modelo de transporte de Cazón 2012). No es un modelo distinto: es de donde sale la exponencial de
Armbruster.

- Si el muón no pierde energía, βγ = p/(m_μ c) es constante, la integral da `d / (βγ c τ)`, y queda
  exactamente `exp(−d/λ)` con `λ = (p/m_μc)·cτ_μ ≈ 6.2 km × (p / 1 GeV/c)`.
- Si pierde energía (≈ 2 MeV por g/cm² en aire), βγ baja a lo largo del camino y la integral ya no
  es una exponencial simple. Por eso el λ de Armbruster es un **parámetro efectivo**: junta
  decaimiento, pérdida de energía y muones que quedan bajo el umbral. Billoir et al. (GAP-2002-074)
  dan 5–10 km para los muones, compatible con muones de 1–2 GeV/c.

El borrador lo presenta así: primero la exponencial de Armbruster, después de dónde sale y qué
significa λ. Agrega además una consecuencia útil. Como la región tardía está `≈ 2 r tanθ` más
lejos, la atenuación sola da

    A1_att ≈ r tanθ / λ

y **no depende de D**. Con r = 450 m y θ = 45° da 0.07 si λ = 6 km, y 0.01 si λ = 36 km. Como λ
crece con p, la atenuación pesa más para los muones blandos. Esto importa en la 3.4.

## 2. Término geométrico de Billoir

El texto de CINEMATICA está copiado textual, para que lo compares vos. El único cambio es que
"Dado que p_r > 0" pasó a "Para un flujo que diverge desde el eje, p_r > 0". p_r es la componente
radial con signo; REVISION/INTEGRADO insistían en eso con razón.

Se agregó un párrafo que conecta A_geo con la geometría de la fuente puntual. Un plano horizontal
recibe un flujo ∝ cos ϑ (ϑ = cenital local de la trayectoria). Con `⟨p_r/−p_z⟩ ≈ r/D`, ese factor
reproduce **exactamente** la Ec. de Billoir. O sea, A_geo es "el término de respuesta de un
detector plano". Eso permite meterlo en la fórmula común de la 3.4 sin contarlo dos veces.

## 3. Geometría del tanque (Billoir 2002): por qué no afecta la asimetría muónica

El argumento está en **GAP-2002-074** (Billoir, Da Silva, Bertou, "Checking the origin of the
Asymmetry of the Surface Detector signals"), no en la 073, que es la que la tesis cita como
`Billoir2002`. Agregué la 074 como `Billoir2002b`.

El argumento, en simple:
- La cantidad de muones que entran al tanque es ∝ al área que el tanque presenta en esa dirección,
  `A(ϑ) = πR² cos ϑ + 2RH sin ϑ`. Esa área cambia entre el lado temprano y el tardío.
- La luz de cada muón es ∝ a su longitud de traza en el agua. En promedio sobre el área proyectada,
  la traza media es `V / A(ϑ)` (volumen dividido área).
- Señal total ∝ (muones) × (traza media) = `A(ϑ) · V/A(ϑ) = V`. **No depende de la dirección.** Más
  área de un lado se compensa exactamente con trazas más cortas.

Por eso no hay asimetría geométrica de detector para la **señal** muónica del SD. Sí la hay para la
EM, que deposita cerca de la superficie. El borrador agrega la salvedad importante para esta tesis:
el **conteo** Monte Carlo de muones del SD es un conteo, no una señal. Ahí la compensación no
ocurre y el factor es A(ϑ): la tapa favorece el lado temprano y el lateral el tardío. Para el
tanque de Auger casi se cancelan: +0.03, contra +0.11 de un plano, en el punto de referencia.

## 4. "Una expresión común" (3.2.5 de INTEGRADO) → Sección 3.4.1

Se rehízo como la linealización de Armbruster (su Sec. 2.6), paso a paso, con un término por
mecanismo:

    A1 ≈ [ 2 − s + D/λ + κ ] (r/D) tanθ
          dilución  emisión angular  atenuación  respuesta del detector

Con κ = 0 (señal del SD) y ADF de ley de potencias (s = γ) queda **exactamente la fórmula de
Armbruster**, `(2 − γ + D/λ)(r/D)tanθ`. Esa es la consistencia con la bibliografía de la
Colaboración que querías mostrar. Cada término se identifica con una subsección de 3.2. El único
término negativo es la emisión angular. Con la distribución de Cazón su pendiente es
`s ≈ p r/(QD)`, lo que da directamente el momento de cruce `p* ≈ 2QD/r` (2.5 GeV/c en el punto de
referencia; el cálculo exacto da 2.48).

## 5. La sección "Del conteo incidente al promedio en estaciones seleccionadas"

**Qué dice.** Los conteos MC de muones son exactos, pero sólo se leen en las estaciones que entran
al análisis, por ejemplo las que tienen `HasStation` (estación SD reconstruida). Si la probabilidad
de que una estación entre depende de cuántos muones tiene, el promedio sobre las estaciones que
entran no es el promedio verdadero. Si esa dependencia es distinta en el lado temprano y en el
tardío, el perfil azimutal cambia, y **puede cambiar de signo**.

La identidad de REVISION/INTEGRADO dice exactamente eso:
`⟨N⟩_seleccionadas = ⟨N⟩_todas × ε_N/ε`. Aquí ε es la fracción de estaciones que entran y ε_N la
fracción de muones que queda en ellas. Si la selección no mira los muones, ε_N = ε y no pasa nada.

**Ejemplo (el mismo del borrador).** A un radio grande, temprano tiene 0.6 muones/estación y
tardío 0.5, así que A1 = +0.09. Temprano: la EM hace disparar a todas las estaciones, promedio 0.6.
Tardío: la EM está atenuada y sólo dispara la estación que tiene al menos un muón. Con Poisson eso
es el 39 % de las estaciones, que contienen todos los muones, y el promedio seleccionado da
0.5/0.39 = 1.27. **A1 medido = −0.36.** No se movió ningún muón: cambió sobre qué estaciones se
promedia.

**Qué suma.** Es la pieza que cierra el capítulo. La 3.4 muestra que la física de propagación no
produce inversión en la densidad incidente. La 3.5 explica por qué igual se ve una en el conteo del
SD. Coincide con el reprocesamiento que hiciste
(`claude_work/reprocesamiento_sd_completo/`): en 1200–1350 m, θ = 30–40°, el A1 muónico del SD es
−0.124 exigiendo SD reconstruida y +0.069 sin exigirlo, con las mismas lluvias y los mismos conteos.

**Mi recomendación.** Dejarla en el Cap. 3 en esta versión corta, sin la notación E[·|S, b]. El
control numérico va en el Cap. 6. Si preferís un Cap. 3 puramente físico, se puede mover entera al
Cap. 6. Está marcada con un comentario `% PROPUESTA`.

## 6. Los modelos de juguete, explicados

### 6a. Los de la Sección 3.4 (basados en la Ec. del cociente)

Todos usan **una fuente puntual** a distancia D sobre el eje, de donde salen los muones en línea
recta. Para una estación en (r, φ), la densidad es el producto de cuatro factores:

    S ∝ (1/d²) · f(α|p) · exp(−d/λ(p)) · R(ϑ)

Los dos primeros son exactamente la Ec. de Cazón de la 3.2.3. El tercero es Armbruster y el cuarto
la respuesta del detector de la 3.2.2. A1 se saca como coeficiente de Fourier del perfil en φ (360
puntos), que es lo mismo que el ajuste cos φ con bines iguales. Punto de referencia: r = 1200 m,
θ = 35° (donde el SD invierte en simulación), D = 7.5 km, Q = 0.2 GeV/c, espectro p^−2.6.

- **Modelo I, un solo momento (Fig. 3.3).** ¿Qué A1 tienen muones que tienen todos el mismo p? Los
  ángulos requeridos son 10.2° (temprano) y 8.2° (tardío). A p = 0.2 GeV/c la distribución angular
  es tan ancha que los dos ángulos son casi igual de probables (cociente 1.04). Gana la dilución,
  que vale 0.645, y A1 > 0. Recién por encima de p\* ≈ 2.5 GeV/c la distribución es tan angosta que
  la diferencia de 2° pesa, y A1 < 0. **Los muones blandos NO son los que dan exceso tardío; son los
  duros.** Es lo contrario de la narrativa de "Población B".
- **Modelo II, población con espectro (Fig. 3.4, Tabla 3.1).** ¿Qué A1 tiene la mezcla de todas las
  energías por encima de un umbral? Se integra cada región por separado y después se divide
  (cociente de integrales). Da positivo a umbral bajo y **baja** al subir el umbral: +0.16 a
  0.155 GeV/c, +0.02 a 1.22 GeV/c (UMD a 35°), y cruza cero cerca de 1.5 GeV/c. El motivo, en una
  línea: a radio r sólo llegan muones con p ≲ QD/r ≈ 1.25 GeV/c (necesitan p_t ≈ p r/D y p_t está
  acotado por Q). Los duros, los únicos con preferencia tardía, son exponencialmente raros lejos del
  núcleo. El umbral saca los blandos, que son los más "temprano-favorecidos" (poca pendiente y mucha
  atenuación), y por eso A1 baja.
  - La versión vieja (promediar el cociente con el espectro de producción) daba A1 → −1. No era
    física: ese promedio no está acotado. Se menciona en el texto como error a no cometer.
- **Modelo III, cada detector (Fig. 3.5).** SD = conteo en tanque con p > 0.2 GeV/c. UMD = plano
  horizontal con umbral **local** 1 GeV/(c cos ϑ). Los dos dan A1 > 0 a todo radio, creciente con r
  y θ, **sin inversión**. En la referencia, SD +0.22 y UMD +0.28. El UMD sale más positivo sólo por
  su respuesta: plano (κ = 1) más umbral local, que es más alto del lado tardío. Con umbral global
  1/cos θ, el UMD da +0.18 < SD. **Este número es nuevo:** el texto de CINEMATICA decía que la
  modulación del umbral local "no ha sido cuantificada"; en el toy vale +0.10. Probablemente está
  sobreestimado (ver punto de réferi c).

### 6b. Tu Fast‑MC (`Scripts/Intento Toy Model para Inversion Fallido/`) — no lo puse en el Cap. 3

Lo que hacían los notebooks: generar muones con altura z ~ Gamma, energía ~ E^−2.6, p_T ~ normal, y
radio `r = z·p_T/E`, con φ **uniforme**. Después se pesaba cada muón con
`w_geo = 1 − (r/z) tanθ cos φ` y con la supervivencia al decaimiento, y se ajustaba A1 por bines.

Por qué no podía decidir la pregunta (esto no se arregla corrigiendo un bug):
1. Como φ se sortea uniforme y r no depende de φ, **no hay competencia entre ángulos**: la selección
   angular de la Ec. de Cazón no está en el modelo. Toda la asimetría sale de los dos pesos que se
   ponen a mano.
2. `w_geo = 1 − (r/z)tanθ cos φ` favorece el lado **tardío** por construcción. Es el signo opuesto a
   A_geo de Billoir (que es +). El signo de la inversión estaba impuesto, no derivado.
3. En v1 el camino era `l = z + r tanθ cos φ`: más largo del lado **temprano** (signo invertido). En
   v2 se corrigió a `z − r tanθ cos φ`.
4. En v2, `pT = normal(0.03, 0.05)` recortado a ≥ 0.1 deja casi todos los p_T = 0.1 GeV/c.

Los modelos de la 3.4 hacen lo que el Fast‑MC quería hacer, pero con la geometría y la selección
angular explícitas. Sugiero dejar el Fast‑MC fuera del Cap. 3 y revisar su mención en el Cap. 6
(`subsec:fast_mc`) cuando lo reescribamos. Hay un comentario en el .tex al final de 3.4.5.

## 7. Cambios de texto respecto de CINEMATICA (para tu comparación)

- "no son recorren" → "no recorren"; comillas `'antes'` → `` `antes' ``.
- Atenuación: se sacaron "Este es el efecto dominante que afecta a la componente muónica..." y
  "consolidando la atenuación atmosférica como el efecto dominante para la componente muónica pura".
  Con la Ec. lineal, en la referencia la dilución (+2) pesa más que la atenuación (D/λ ≈ 0.4–1.2).
  "Dominante" no está demostrado. Si querés conservar la idea, se puede decir "una contribución
  positiva importante".
- Atenuación, blindaje del UMD: "filtro cinemático que elimina los muones sub-GeV que han sufrido
  atenuaciones extremas" → "elimina la componente EM y los muones que no alcanzan la energía
  necesaria para atravesarlo". La idea de "filtro cinemático" es justo la que el Modelo II refuta.
- Billoir: "estrictamente positivo" ahora dice "para un flujo que diverge desde el eje".
- Luce: "modelado cuantitativamente" → "modelado"; "Esto exige un tercer mecanismo" → "Esto
  motiva examinar un tercer mecanismo" (la 3.4 muestra que no lo explica).
- Divergencia: `sin α ≃ c p_t/E ≃ p_t/|p_z|` (GAP) → `sin α = p_t/p ≃ c p_t/E`. `p_t/|p_z|` es
  tan α, no sin α.
- Divergencia: la GAP vieja usa `d ≈ D − r sinθ cos φ`. Lo correcto, con r en el plano de la lluvia,
  es `r tanθ` (Armbruster Ec. 2.5). El borrador usa la forma exacta, Ec. 3.1.
- Divergencia: se mantiene el factor p² en dN/dΩ (la GAP lo absorbía en "∝") y se aclara que se
  cancela a energía fija.
- Parametrización: "A1 < 0 señala la dominancia de efectos geométricos" → "exceso en la región
  tardía" (los efectos geométricos de Billoir son positivos). "Esta parametrización asume que el
  mecanismo dominante es la atenuación... A1 positivos" → fijar φ0 = 0 no impone el signo.

## 8. Puntos de réferi abiertos (para decidir vos)

a. **Parámetros del toy.** Q = 0.2 GeV/c, D = 7.5 km y γ = 2.6 son los del memo anterior. Antes de
   entregar hay que verificar en Cazón 2012 el valor exacto de Q y el rango de D, y citar la
   página. Las conclusiones cualitativas no dependen de eso; los números de la Tabla 3.1 sí.
b. **Amplitudes del toy ~2× las de la simulación** (UMD +0.28 vs ≈ +0.11 en MC a 1200 m). Está dicho
   en 3.4.5. El texto usa el toy sólo para signos y tendencias. Conviene no citar sus números fuera
   del Cap. 3.
c. **Umbral local del UMD.** En el toy aporta +0.10 y es lo que ordena UMD > SD. Probablemente está
   sobreestimado (espectro p^−2.6 cerca del umbral, fuente puntual). Es una hipótesis
   **verificable** con la simulación: comparar el A1 del UMD con y sin corte en el cenital local, si
   el ADST lo permite. No lo afirmaría como explicación sin ese control.
d. **Geomagnético.** El texto de CINEMATICA dice que la deflexión "se manifiesta como una reducción
   espuria de A1". Un dipolo de orientación aleatoria respecto del eje temprano–tardío se promedia a
   cero sobre cos φ. Agrega dispersión, pero no es obvio que reduzca A1 sistemáticamente. Lo dejé
   textual, con un comentario `% NOTA (referi)` en el .tex.
e. **El Cap. 6 ahora contradice al Cap. 3.** El Cap. 6 actual explica la inversión del SD con la
   "Población B" y el filtro del UMD (secciones `subsec:infill_mc` y `subsec:fast_mc`). Es lo
   próximo a reescribir, con el control HasStation como resultado principal.
f. **Umbral aplicado al momento de producción** y sin pérdidas de energía: ambos umbrales efectivos
   en producción son más altos que los indicados. Está dicho en 3.4.3; mueve las dos curvas en la
   misma dirección.

## Cómo integrarlo a la tesis (cuando lo apruebes)

1. Copiar `03_fenomenologia.tex` a `Tesis - Latex/capitulos/`.
2. Copiar a `Tesis - Latex/capitulos/imagenes_capitulos/cap3/`: `esquema_lluvia_gap.jpeg`,
   `toy_momento_fijo.pdf`, `toy_umbral.pdf`, `toy_radio.pdf`.
3. Agregar las dos entradas de `bibliografia_adicional.bib` a `Tesis - Latex/bibliografia.bib`.
4. Agregar `\usepackage{cancel}` al preámbulo de `main.tex` (la derivación de la GAP usa `\cancel`).
5. Compilar la tesis completa: las referencias a `cap:infill`, `sec:cap_anillo_denso` y
   `subsec:fast_mc` ya existen en los capítulos 5 y 6.
