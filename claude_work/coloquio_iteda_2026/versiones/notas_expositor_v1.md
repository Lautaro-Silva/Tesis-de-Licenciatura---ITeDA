# Notas del expositor — «Huellas del universo»

**Rayos cósmicos, cosmología y neutrinos desde Argentina**
Coloquio ITeDA · Lautaro Silva Pizzi · 57 diapositivas principales + 9 de respaldo

Las notas siguen el orden de `coloquio_iteda.pdf`. Para cada diapositiva figuran la idea central, una explicación oral sugerida, los detalles físicos y números que conviene tener a mano, la transición y un tiempo orientativo. Las cifras están verificadas contra las fuentes de `fuentes_figuras.md`. Las marcadas con ⚠ conviene que las revises vos.

## Plan de tiempos

| Bloque | Diapositivas | Tiempo |
|---|---|---|
| Introducción | 1–2 | 2,5 min |
| Universo temprano, CMB y QUBIC | 3–15 | 9,5 min |
| Rayos cósmicos, espectro y fuentes | 16–23 | 9,5 min |
| Observatorio Pierre Auger | 24–33 | 12 min |
| Mi tesis | 34–40 | 8,5 min |
| Neutrinos, IceCube y multimensajero | 41–50 | 9 min |
| HERON y cierre | 51–57 | 5 min |
| **Total** | **57** | **≈ 56 min** |

**Si vas largo** (por orden de prioridad para recortar):

1. La 15 (interferometría bolométrica): una frase.
2. La 20 (Fermi) y la 21 (Hillas): fusionalas oralmente.
3. La 43 (Auger busca neutrinos): 30 s.
4. La 49 (Auger vs. IceCube): se anticipa en la 55.

Con estos recortes ganás unos 4 minutos. **Si vas corto**, el respaldo R1 (cuentas) y el R5 (desglose del SD) se pueden mostrar dentro de la charla.

Convención: en las notas, «temprano/tardío» se refiere a las regiones del plano de la lluvia (φ = 0 y φ = ±180°), como en la tesis.

---

## BLOQUE 0 — Introducción

### 1. Portada · 0,5 min
**Idea:** la imagen de fondo ya es la charla: una fuente, tres mensajeros, tres destinos.
**Oral:** «Esta imagen la van a volver a ver dentro de media hora, y para entonces va a tener sentido. Por ahora, quédense con que hay algo que acelera partículas, que de ahí salen cosas distintas y que no todas llegan igual a la Tierra.»
**Transición:** «Esta charla tiene dos hilos.»

### 2. Cuatro huellas, un mismo cielo · 2 min
**Idea:** dos motivaciones con el mismo peso: la física, y que esa física se hace desde la Argentina.
**Oral:** Recorré las cuatro preguntas de arriba hacia abajo y señalá el mapa en cada una. QUBIC en la Puna salteña, Auger en Malargüe, HERON en la precordillera sanjuanina e ITeDA en el Centro Atómico Constituyentes. IceCube está en el Polo Sur, sin participación argentina directa. Lo incluyo porque es el ejemplo extraordinario que abre la astronomía de neutrinos y nos lleva a HERON.
**Mensaje:** no es una competencia entre países. Estos experimentos sólo existen como colaboraciones internacionales, y la Argentina participa construyendo instrumentos, operándolos y analizando datos.
**Transición:** «Empecemos por la huella más antigua.»

---

## BLOQUE 1 — Universo temprano, CMB y QUBIC

### 3. Un universo que se enfría al expandirse · 0,8 min
**Idea:** la expansión enfría; la temperatura decide qué partículas existen libres.
**Oral:** «El Big Bang no es una explosión en un punto: es la descripción de un universo que, hacia atrás en el tiempo, era cada vez más caliente y denso.» La longitud de onda de cada fotón escala con el factor de escala a(t), así que T ∝ 1/a. En la era de radiación T ∝ t^(-1/2): el clásico «1 MeV a 1 segundo».
**Física (hitos del gráfico, órdenes de magnitud):**
- Transición electrodébil: ~100 GeV, ~10⁻¹¹ s.
- Confinamiento quark→hadrón: ~150 MeV, ~20 μs.
- Desacople de neutrinos: ~1 MeV, ~1 s. Queda un fondo de neutrinos de 1,95 K.
- Nucleosíntesis: ~0,1 MeV, ~3 min.
- Igualdad materia–radiación: z ≈ 3400, ~50.000 años.
- Última dispersión: z* ≈ 1090, T ≈ 2970 K, k_BT ≈ 0,26 eV, ~380.000 años. Planck da 373.000.
- Reionización: z ~ 7–8.
- Hoy: 13.800 millones de años.

**Aclarar:** el gráfico es una interpolación por tramos entre esos hitos, no una solución de Friedmann; por eso lleva la insignia.
**Transición:** «En la mayor parte de esa historia el universo era opaco. ¿Por qué?»

### 4. Un plasma opaco · 0,8 min
**Idea:** con electrones libres, los fotones no viajan: difunden.
**Oral:** La sección eficaz Thomson es chica, σ_T = 6,65×10⁻²⁵ cm², pero hay muchísimos electrones. A z ≈ 1100, con todo ionizado, n_e ≈ 300 cm⁻³ (físicos) y el camino libre medio es ~1–2 kpc. El horizonte de Hubble c/H en ese momento es ~200 kpc: un fotón se dispersa ~100 veces por tiempo de Hubble y hace un camino aleatorio. Es como mirar a través de niebla.
**Criterio de desacople:** la tasa de dispersión Γ_T = n_e σ_T c cae por debajo de la tasa de expansión H.
**Transición:** «¿Y cuándo desaparecen los electrones libres?»

### 5. Recombinación, desacople y última dispersión · 0,8 min
**Idea:** tres conceptos distintos que suelen confundirse.
**Oral:** Con la ecuación de Saha la fracción ionizada cae a 1/2 recién a z ≈ 1370, T ≈ 3700 K, k_BT ≈ 0,32 eV, aunque la energía de ligadura es 13,6 eV. La razón es que hay ~1,6×10⁹ fotones por barión, y la cola de Wien de la distribución de Planck sigue teniendo suficientes fotones ionizantes hasta que k_BT ~ B/40.
**Las tres palabras:**
- **Recombinación:** los electrones se ligan; x_e cae. Es un proceso.
- **Desacople:** Γ_T < H, los fotones dejan de interactuar. Es una condición dinámica.
- **Superficie de última dispersión:** la cáscara esférica, centrada en nosotros, desde donde los fotones se dispersaron por última vez. Es una geometría observacional. Tiene un espesor Δz ~ 100.

**Matiz que vale decir:** Saha supone equilibrio. La recombinación real es más lenta porque los fotones Lyman-α reexcitan los átomos, y se recombina vía la transición de dos fotones 2s→1s (Peebles 1968). Por eso x_e real a z* ≈ 1090 es ~10⁻¹, más alto que lo que da Saha.
**Transición:** «Esos fotones siguen viajando hasta hoy. Esto es lo que vemos.»

### 6. La fotografía más antigua del universo · 0,5 min
**Idea:** un mapa del cielo entero en microondas, con contrastes de una parte en cien mil.
**Oral:** Dejá la imagen y callate unos segundos. «Esto es el cielo completo, proyectado como un mapamundi. Ya restamos el dipolo por nuestro movimiento (~3 mK) y la emisión de la galaxia. Los colores son ±200 μK sobre 2,7 K.» Es una foto de cuando el universo tenía 380.000 años: lo más lejos que podemos ver con fotones.
**Transición:** «Antes de mirar las manchas, miremos el promedio.»

### 7. El cuerpo negro más perfecto que conocemos · 0,6 min
**Idea:** el espectro es un cuerpo negro perfecto. Eso confirma un pasado caliente y en equilibrio.
**Oral:** Los puntos son COBE/FIRAS (1990–96). Las barras de error son 400 veces más chicas que lo que se ve. Abajo están los residuos, en kJy/sr frente a un pico de ~380 MJy/sr: menos de 50 partes por millón.
**Por qué la expansión no deforma el espectro:** ν ∝ 1/a y T ∝ 1/a, así que hν/kT no cambia, y el número de ocupación tampoco. Un cuerpo negro sigue siendo un cuerpo negro, a temperatura menor.
**Distorsiones:** las cotas |μ| < 9×10⁻⁵ e |y| < 1,5×10⁻⁵ (Fixsen 1996) dicen que no hubo inyección grande de energía después de z ~ 10⁶. Hoy hay ~411 fotones del CMB por cm³.

### 8. Las anisotropías: ondas acústicas congeladas · 1,0 min
**Idea:** el espectro de potencia es la «partitura» de oscilaciones del plasma primordial.
**Oral:** Expandimos ΔT/T en armónicos esféricos. ℓ grande son escalas angulares chicas: θ ≈ 180°/ℓ. 𝒟_ℓ = ℓ(ℓ+1)C_ℓ/2π es la potencia por intervalo logarítmico.
- **Meseta de Sachs–Wolfe (ℓ < 30):** escalas más grandes que el horizonte de entonces. Reflejan directamente el potencial gravitatorio primordial.
- **Picos acústicos:** la materia oscura forma pozos; el fluido fotón–barión cae y la presión de radiación lo hace rebotar. Al desacople, cada modo queda congelado en una fase de su oscilación.
- **Primer pico ℓ ≈ 220:** el modo que llegó a su primera compresión máxima. Su escala angular θ* = r_s/D_A ≈ 0,6° (horizonte de sonido sobre distancia angular) mide la geometría: el universo es espacialmente plano.
- **Picos 2.º y 3.º:** su altura relativa mide los bariones y la materia oscura. Los bariones cargan el oscilador y realzan las compresiones.
- **Amortiguamiento de Silk:** la difusión de fotones borra las escalas chicas.

**Las fluctuaciones iniciales:** casi invariantes de escala, n_s ≈ 0,965, consistente con inflación. Son las semillas de toda la estructura posterior: galaxias, cúmulos, nosotros.
**Transición:** «Además de intensidad, esa luz tiene polarización.»

### 9. Polarización: la huella de las ondas gravitacionales · 0,9 min
**Idea:** la polarización tiene una componente (modos B) que la densidad no puede generar.
**Oral:** La dispersión Thomson polariza la luz perpendicular al plano de dispersión. Si un electrón ve la misma intensidad desde todas las direcciones, la luz sale sin polarizar. Si ve un **cuadrupolo** (más caliente en un eje que en el otro), sale linealmente polarizada. Ese cuadrupolo sólo existe cerca de la última dispersión, cuando el camino libre medio es finito: por eso la polarización es ~10 veces más chica que la intensidad.
**E y B:** el campo de polarización se descompone en una parte de gradiente (E, paridad par: patrones radiales o tangenciales) y una de rotor (B, paridad impar: remolinos). Las perturbaciones **escalares** de densidad sólo generan E. Las **tensoriales** (ondas gravitacionales del período inflacionario) generan E y B. Medir B primordiales sería ver gravedad cuantizada inflacionaria y fijar la escala de energía de la inflación: V^(1/4) ≈ 1,04×10¹⁶ GeV (r/0,01)^(1/4).
**Estado:** r < 0,036 (95%, BICEP/Keck 2021). Los modos B por lente gravitacional (E convertidos en B por la estructura intermedia) ya se midieron. Son un contaminante, igual que el polvo polarizado de la galaxia.
**No profundizar.** Basta con que se entienda por qué hace falta una sensibilidad enorme.

### 10. QUBIC: cosmología a 4.869 m en la Puna salteña · 0,8 min
**Idea:** un experimento de frontera, instalado y funcionando en la Argentina.
**Oral:** QUBIC, Q&U Bolometric Interferometer for Cosmology. Q y U son los parámetros de Stokes de la polarización lineal. Está en Alto Chorrillos, cerca de San Antonio de los Cobres. Las fuentes dan 4.869 m en los artículos y «casi 5.000 m» en los comunicados.
**Por qué ahí:** el vapor de agua emite y absorbe en milimétricas. A esa altura y en ese clima, la profundidad óptica cenital a 210 GHz es < 0,1 la mitad del tiempo. El sitio comparte la zona con el radiotelescopio LLAMA.
**Cronología** (F. Sánchez, abr. 2026):
- Demostrador integrado en París (APC) en 2020; llega a la Argentina en julio de 2021.
- Integración y pruebas en el laboratorio de la CNEA en Salta (2021–22); instalación e inauguración en noviembre de 2022.
- Torre de calibración en 2024; en 2025 ITeDA completa la montura (carros auxiliares fabricados en el CAC, rotación de hasta 440°).
- **11 de marzo de 2026: primer barrido de la Luna desde el sitio**, con el análisis en curso.

**ITeDA:** infraestructura y montura, análisis de datos y desarrollo de nuevos sensores (microbolómetros magnéticos, con KIT). Colaboración de 6 países.
⚠ Hay nevadas que dificultan la toma regular de datos: no prometas resultados científicos todavía.

### 11. Qué significa medir decenas de nanokelvin · 0,8 min
**Idea:** la señal buscada es una parte en 10⁸ de la potencia que llega.
**Cuenta** (tenela lista):
- Un modo, una polarización, 150 GHz, Δν/ν = 25%: P = ∫hν n(ν) dν. Con x = hν/kT = 2,64 y n = 0,077, P ≈ 0,3 pW.
- dlnP/dlnT = x eˣ/(eˣ−1) ≈ 2,8, así que 30 nK producen δP/P ≈ 3×10⁻⁸, es decir, δP ~ 10⁻²⁰ W.
- Son ~3×10⁹ fotones por segundo: **no se cuentan fotones**. El ruido de llegada de fotones y el de fonones del detector se miden como potencia equivalente de ruido (NEP, W/√Hz). En los TES de QUBIC el NEP de fonones es ~5×10⁻¹⁷ W/√Hz. Para promediar ~10⁻²⁰ W hacen falta miles de detectores integrando durante años.

**El gráfico:** √𝒟_ℓ para TT, EE y BB de lente. La línea punteada marca el orden de magnitud de los B primordiales con r ~ 0,01. La banda naranja es el rango angular de QUBIC (ℓ ~ 30–200, el «pico de recombinación» de los B).

### 12. Bolómetros y sensores de borde de transición (TES) · 0,8 min
**Idea:** un bolómetro mide potencia por calentamiento; el TES es un termómetro extraordinariamente sensible.
**Oral:** Un absorbente con capacidad calorífica C, unido a un baño a T_b por una conductancia térmica débil G. En equilibrio ΔT = ΔP/G, con constante de tiempo τ = C/G. El ruido fundamental es el de fonones, NEP ≈ √(4k_BT²G): enfriar baja el ruido.
**El TES:** una película superconductora (en QUBIC, NbSi, T_c ≈ 410 mK) operada **en el medio** de su transición. Allí α = d lnR/d lnT es del orden de 10² o más: un cambio de microkelvin produce un cambio grande de resistencia.
**Truco clave:** polarizar a **tensión** constante. Si sube T, sube R, baja P_J = V²/R: es la realimentación electrotérmica negativa, que fija el punto de operación y acelera la respuesta. La señal es la **corriente**: δI ≈ −δP/V.
**No confundir:** el TES no detecta fotones individuales en este régimen. Integra potencia.

### 13. SQUIDs: interferencia cuántica para leer el TES · 0,8 min
**Idea:** el TES produce corrientes de nanoamperes, y para leerlas sin agregar ruido se usa un dispositivo cuántico.
**Oral:** Una juntura Josephson son dos superconductores separados por una barrera delgada. Pasa una supercorriente I = I_c sin φ, donde φ es la diferencia de fase de los condensados. Con tensión, la fase avanza como φ̇ = 2eV/ħ.
**SQUID DC:** un anillo superconductor con dos junturas. El flujo que atraviesa el anillo desfasa una rama respecto de la otra: interferencia, igual que una doble rendija pero con pares de Cooper. La corriente crítica total es 2I_c|cos(πΦ/Φ₀)|, con Φ₀ = h/2e = 2,07×10⁻¹⁵ Wb, el **cuanto de flujo**. Polarizado por encima de I_c, la tensión es periódica en Φ. Operándolo en la pendiente, con realimentación de flujo, resulta un amperímetro de ruido bajísimo: la corriente del TES pasa por una bobina acoplada al anillo.
**En QUBIC:** 128 SQUIDs a 1 K, multiplexados 128:1 en el dominio temporal; un ASIC de SiGe a 40 K amplifica y controla el multiplexado.
**Frase para fijar:** «El TES mide; el SQUID lee.»

### 14. Criogenia: el detector no está a la temperatura del CMB · 0,6 min
**Idea:** son dos escalas de temperatura distintas. No mezclarlas.
**Oral:** A la izquierda, las etapas del instrumento:
- 300 K ambiente.
- 40 K y 4 K, con tubo de pulsos: ASIC, pantallas, cornetas y lámina de media onda.
- 1 K con sorción de ⁴He: óptica fría y SQUIDs.
- ~300 mK con sorción de ³He: el plano focal, con los TES en su transición a ~410 mK.

A la derecha, lo que se mide en el cielo: 2,725 K de fondo, ~70 μK de anisotropías, μK en modos E, ~0,3 μK en B de lente y decenas de nK en B primordiales.
**Por qué tan frío:** el ruido de fonones escala como T√G, la transición superconductora tiene que estar por encima del baño, y además hay que eliminar la emisión térmica propia de la óptica.
**Mensaje:** el detector a 0,3 K mide una diferencia de **potencia** que llega del cielo. No «tiene» la temperatura del CMB.

### 15. Interferometría bolométrica: lo nuevo de QUBIC · 0,6 min
**Idea:** QUBIC combina la sensibilidad del bolómetro con el control de sistemáticos de un interferómetro.
**Oral:** Un arreglo de cornetas (400 en el instrumento final, 64 en el demostrador) funciona como muchas aperturas. Cada par es una línea de base. Un combinador óptico (dos espejos) superpone los haces sobre el plano focal: cada TES ve una figura de interferencia, el «haz sintetizado» con varios picos.
- Los interruptores en las cornetas permiten **autocalibrar** líneas de base redundantes.
- La separación entre picos del haz es ∝ λ, lo que da **imágenes espectrales**: varias sub-bandas dentro de cada banda física, útiles para separar el polvo galáctico.

**Imagen:** primer barrido de la Luna desde el sitio, 11/03/2026. Se ven los picos del haz sintetizado.
**Cierre del bloque:** «Desde la Puna, la Argentina participa en la búsqueda de una señal de una parte en cien millones de la radiación más antigua del universo.»
**Transición:** «Pasemos del universo más antiguo a los fenómenos más violentos del universo actual.»

---

## BLOQUE 2 — Rayos cósmicos

### 16. Rayos cósmicos: aceleradores naturales · 1,0 min
**Idea:** núcleos cargados con energías extraordinarias; el campo magnético borra la dirección.
**Oral:** Hess, 1912: la ionización crece con la altura, así que viene de arriba. Hoy sabemos que a GeV los primarios son ~90% protones, ~9% helio y ~1% núcleos más pesados, más ~1% de electrones.
**Radio de Larmor:** r_L ≈ 1,1 kpc · (E/EeV)/(Z·B/μG). El campo galáctico es de ~3 μG, así que un protón de 10¹⁹ eV gira en un radio de ~3,6 kpc: comparable al grosor del disco. Un hierro de la misma energía tiene un radio 26 veces más chico.
**Los tres mensajeros** (las tarjetas):
- Los núcleos cargados llegan desviados.
- Los gamma se absorben por producción de pares sobre la luz de fondo. A PeV el horizonte es de unos pocos kpc, sobre el CMB, y a TeV se absorben en la luz infrarroja extragaláctica.
- Los neutrinos llegan derechos pero casi no interactúan.

**Transición:** «¿Cuántos llegan?»

### 17. Treinta órdenes de magnitud en flujo · 1,0 min
**Idea:** el flujo cae como E^(−2,7). A las energías más altas llega casi nada.
**Oral:** El gráfico es una compilación clásica de muchos experimentos. Son 12 décadas en energía y más de 30 en flujo. Recorré la tabla, con flujos **integrales** por encima de E:
- 10¹¹ eV: una partícula por m² por segundo.
- Rodilla, ~3×10¹⁵ eV: una por m² por año.
- ~10¹⁹ eV: ~una por km² por año.
- ~5×10¹⁹ eV: ~una por km² por siglo.

⚠ La tesis y la defensa dicen «1 por km² por siglo para E > 10¹⁹». Con la exposición de Auger, por encima de 10 EeV la tasa integral es del orden de una por km² por año. Uso ~5×10¹⁹ eV para «por siglo». Revisalo si querés mantener la frase original.
**Consecuencia:** por encima de ~100 TeV no hay detector en satélite que junte estadística. Hay que usar la atmósfera como calorímetro.
**Flechas del gráfico:** la energía de Tevatron y del LHC. Ojo: ese gráfico marca 14 TeV para el LHC. La conversión correcta se ve en la 25.

### 18. El espectro como mapa de la física · 1,5 min
**Idea:** cada quiebre del espectro es una pista sobre fuentes y propagación.
**Oral:** Multiplicar por E^2,6 aplana la tendencia y deja ver los quiebres. Es un esquema: las pendientes son las medidas, pero la normalización es arbitraria.
- **Rodilla (~3×10¹⁵ eV, γ: 2,7→3,1):** fin de la aceleración de protones en las fuentes galácticas, o pérdida de confinamiento. Ambos mecanismos dependen de la **rigidez** E/Z, así que E_rodilla(Z) ≈ Z·E_rodilla(p).
- **Segunda rodilla (~10¹⁷ eV):** el hierro (Z = 26) llega a su máximo. Encaja con 26 × 3 PeV ≈ 8×10¹⁶ eV.
- **Transición galáctico–extragaláctico** entre 10¹⁷ y el tobillo (banda rayada): dónde ocurre exactamente es un debate abierto.
- **Tobillo (5×10¹⁸ eV):** endurecimiento del espectro.
- **Supresión (>4×10¹⁹ eV).**

**Abajo:** qué experimento mira cada rango.
- Satélites y globos hasta ~100 TeV: AMS-02, DAMPE, CALET.
- Arreglos de superficie: LHAASO, IceTop, KASCADE.
- Arreglos densos y telescopios a alta elevación en 10¹⁶–10¹⁸ eV: KASCADE-Grande, TALE, y en Auger los arreglos densos de AMIGA y HEAT.
- Auger y TA a las energías más altas.

**La línea roja:** el √s del LHC (13,6 TeV) equivale a E_lab ≈ 10¹⁷ eV en blanco fijo. Por encima, las simulaciones de lluvias **extrapolan** los modelos hadrónicos. Esto vuelve en el enigma de los muones.

### 19. Zoom en ultra alta energía · 1,2 min
**Idea:** la precisión de Auger reveló una estructura fina por encima del tobillo.
**Oral:** Es la figura del PDG con Auger y TA, en E³J. Los parámetros son de Auger (PRL 2020):
- Tobillo en E₁₂ = 5,0 EeV, donde la pendiente pasa de 3,29 a 2,51.
- *Instep* en E₂₃ = 13 EeV, donde pasa a 3,05.
- Supresión en E₃₄ = 46 EeV, donde pasa a 5,1.
- Significancia de la supresión: más de 20σ.

**Lo que no se sabe:** si la supresión es propagación (GZK o fotodesintegración) o el límite de energía de las fuentes. La forma sola no lo dice, porque espectros de inyección distintos más propagación pueden dar formas parecidas.
**Auger y TA:** coinciden en la forma, pero la normalización y la región más alta difieren algo (TA ve el corte un poco más arriba). Se estudia conjuntamente; dejalo como abierto.

### 20. Cómo se acelera: el mecanismo de Fermi en choques · 1,2 min
**Idea:** un choque es una máquina que da una ley de potencia universal.
**Oral:** En el sistema del choque, el material de río arriba llega a u₁ y el de río abajo se aleja a u₂ = u₁/4 (choque fuerte, gas monoatómico, compresión r = 4). Una partícula difunde en las irregularidades magnéticas a ambos lados. Cada ciclo cruza el choque de ida y vuelta y siempre ve centros dispersores que se le acercan: gana ⟨ΔE/E⟩ = (4/3)(u₁−u₂)/c. **Es de primer orden en u/c**, por eso es eficiente.
**Por qué una ley de potencia:** en cada ciclo la partícula escapa río abajo con probabilidad P_esc = 4u₂/c. Ganancia multiplicativa con escape constante da N(>E) ∝ E^(−P_esc/β), y el índice diferencial es s = (r+2)/(r−1) = 2 para r = 4. No hay parámetros ajustables.
**Del 2 al 2,7:** en la galaxia la difusión depende de la energía (D ∝ E^δ, δ ≈ 0,3–0,6). Los más energéticos escapan antes, y lo que vemos en la Tierra es E^(−2−δ).
**Remanentes de supernova:** la energía cinética de las supernovas galácticas (~10⁵¹ erg cada ~30 años) alcanza si ~10% va a rayos cósmicos (argumento de Ginzburg–Syrovatskii). Su energía máxima ronda el PeV, por la amplificación de campo.

### 21. Criterio de Hillas: ¿quién llega a 10²⁰ eV? · 1,3 min
**Idea:** para acelerar hay que confinar. Eso exige B·R grande.
**Oral:** La partícula tiene que quedar adentro mientras se acelera: r_L ≲ R. Con un choque de velocidad βc, E_max ≈ Z·β·(B/μG)·(R/kpc)·10¹⁸ eV. Para un protón a 10²⁰ eV, B·R ≳ 3×10¹⁷ G·cm: es la línea llena, y la línea punteada es el hierro. Las cajas son órdenes de magnitud de B y R de cada tipo de fuente.
**Lectura del gráfico:**
- Los SNR y el disco galáctico quedan muy por debajo: no llegan a 10²⁰.
- Estrellas de neutrones, GRB, núcleos y jets de AGN, puntos calientes y lóbulos de radiogalaxias y cúmulos quedan cerca de la línea o por encima.

**Limitaciones (importantes):**
- Es condición necesaria, no suficiente. Hay pérdidas en la fuente: sincrotrón (∝ B²), fotoproducción e interacción con el gas. Los objetos compactos de campo enorme pierden por sincrotrón.
- El tiempo de aceleración tiene que ser menor que la edad de la fuente.
- Luminosidad: la fuente tiene que tener ≳10⁴⁵ erg/s en campo magnético (criterio de Waxman–Lovelace).

**No decir** que ya se identificaron fuentes. Son candidatos.

### 22. El viaje no es gratis: efecto GZK y fotodesintegración · 1,3 min
**Idea:** el CMB hace opaco el universo para las partículas más energéticas, y de ahí nacen neutrinos.
**Oral:** El mismo CMB del primer bloque reaparece acá. Un protón de ~10²⁰ eV ve los fotones de 6×10⁻⁴ eV como rayos gamma de ~300 MeV en su sistema: excita la resonancia Δ(1232).
**Umbral en choque frontal:** E_th = m_π(2m_p+m_π)/(4ε) ≈ 1,1×10²⁰ eV. La cola de alta energía de Planck lo baja a ~5×10¹⁹. Cada interacción le quita ~20%, y el horizonte por encima de ~6×10¹⁹ eV es de ~50–100 Mpc.
**Productos:** p γ → Δ⁺ → n π⁺ o p π⁰.
- π⁰ → γγ.
- π⁺ → μ⁺ν_μ, y luego μ⁺ → e⁺ ν_e ν̄_μ: son los **neutrinos cosmogénicos**, objetivo de HERON.

**Otros procesos:**
- Producción de pares e⁺e⁻: umbral más bajo, pérdida más lenta, forma la depresión del tobillo en algunos modelos.
- Para núcleos: **fotodesintegración** (resonancia dipolar gigante) en el CMB y la luz infrarroja. El umbral por núcleo escala ∝ A, así que un hierro aguanta hasta energías mayores que un protón.

**Mensaje crítico:** no son explicaciones excluyentes. Hay que medir espectro, composición y anisotropías a la vez.

### 23. Composición y direcciones de llegada · 1,2 min
**Idea:** dos resultados de Auger cambiaron el panorama.
**Izquierda (X_max):** ⟨X_max⟩ y su dispersión frente a la energía, con las predicciones de protón (arriba) y hierro (abajo) de tres modelos. Hasta ~2–3 EeV se va haciendo más liviano; arriba, cada vez más pesado y con menos fluctuaciones. Está en la tesis (Cap. 5).
**Derecha (dipolo):** el mapa en coordenadas galácticas por encima de 8 EeV tiene un dipolo de amplitud ~7%. La significancia fue de 5,4σ en 2017 y ahora es de 6,8σ (ICRC 2025). Apunta a más de 100° del centro galáctico: **origen extragaláctico**. Es la primera anisotropía firme a estas energías.
**Interpretación combinada:** los ajustes conjuntos de espectro y composición favorecen fuentes con rigidez máxima baja (de unos pocos EV) y composición mixta: cada elemento corta a Z·R_max. Sería más un límite de las fuentes que GZK puro. Esto depende de los modelos hadrónicos.
**Transición:** «¿Cómo se mide todo esto si llega una partícula por km² por siglo?»

---

## BLOQUE 3 — Pierre Auger

### 24. ¿Cómo se mide algo que llega una vez por km² por siglo? · 0,8 min
**Idea:** el número de eventos es flujo × área × ángulo sólido × tiempo, y la única palanca es el área.
**Oral:** N = J·A·Ω·T. No podemos cambiar el flujo; podemos hacer A enorme y esperar. Son ~3000 km², unas 15 veces la Ciudad de Buenos Aires (203 km²). La foto es una estación en la Pampa Amarilla: noten la escala de las personas.
**Número:** ~50.000 eventos por encima de 8 EeV en 19 años, con una exposición de ~1,2×10⁵ km² sr año (ICRC 2025). Por km² y por año se mide ~1 evento por encima de 8 EeV.

### 25. Una partícula con la energía de una pelota de béisbol · 1,2 min
**Idea:** energía macroscópica en un núcleo, y la diferencia entre E_lab y √s.
**Cuentas:**
- 10²⁰ eV × 1,602×10⁻¹⁹ J/eV = 16 J.
- Pelota de béisbol: 0,145 kg (reglamentaria, 142–149 g) a 90 km/h = 25 m/s. ½mv² = ½·0,145·625 = 45 J ≈ 2,8×10²⁰ eV.
- Fly's Eye (15/10/1991): 3,2×10²⁰ eV ≈ 51 J. Amaterasu (TA, 27/05/2021): 2,4×10²⁰ eV ≈ 39 J.

**Laboratorio y centro de masa:** el LHC choca dos haces de 6,8 TeV, así que √s = 13,6 TeV. Un rayo cósmico choca un nucleón del aire en reposo: √s = √(2E m_p c²). Para igualar el √s del LHC hace falta E_lab ≈ (13,6 TeV)²/(2·0,938 GeV) ≈ 10¹⁷ eV. Un primario de 10²⁰ eV da √s ≈ 430 TeV, ~30 veces el LHC.
**Frase:** «La energía es macroscópica en el laboratorio; en el centro de masa es "sólo" 30 LHC, pero aun así, totalmente fuera de nuestro alcance.»

### 26. El Observatorio Pierre Auger, en Malargüe · 1,0 min
**Idea:** el observatorio más grande del mundo para rayos cósmicos, con sede en la Argentina.
**Oral (mencioná a Pierre Auger sin detenerte):** en 1938–39 Pierre Auger detectó coincidencias entre detectores separados cientos de metros y descubrió las lluvias atmosféricas extensas. El observatorio que lleva su nombre lo propusieron Jim Cronin y Alan Watson (1991–92) para zanjar la controversia AGASA–HiRes sobre la supresión.
- Construcción 2002–2008; datos desde 2004.
- 1660 tanques en una red triangular de 1500 m: ~3000 km².
- 4 sitios con 24 telescopios de fluorescencia, más los 3 de HEAT.
- Arreglos más densos de 750 y 433 m, donde está AMIGA.
- ~400 científicos de 17 países.

**Rol argentino:** la Argentina es el país sede, con la sede en Malargüe. Hay grupos argentinos en el diseño, la construcción, la operación y el análisis. ITeDA tiene un rol central en AMIGA y en el UMD (diseño, electrónica, despliegue y análisis).

### 27. Lluvias atmosféricas extensas · 1,4 min
**Idea:** el primario se convierte en una cascada de miles de millones de partículas.
**Oral:** La primera interacción ocurre a ~15–20 km (la longitud de interacción de un protón en el aire es ~50 g/cm² a esta energía). Un tercio de los piones son π⁰, que decaen enseguida (cτ = 25 nm) en dos fotones: alimentan la cascada **electromagnética** (pares y bremsstrahlung), que se lleva ~90% de la energía. Los π^± siguen interactuando hasta que su energía baja tanto que decaen antes de interactuar (energía crítica ξ_c^π ~ 20 GeV): ahí producen **muones**.
**Heitler–Matthews:**
- X_max ∝ ln(E/A): el hierro se comporta como 56 lluvias de energía E/56, llega a su máximo ~100 g/cm² antes y fluctúa menos.
- N_μ ∝ A^(1−β)E^β con β ≈ 0,9: el hierro tiene ~1,5 veces más muones.
- Esto hace de X_max y N_μ los dos observables de masa.

**Perfil abajo:** el evento de Fly's Eye. Se ve crecer, llegar al máximo y atenuarse.
**Cuánto llega al suelo:** a 10¹⁹ eV, unas 10¹⁰ partículas en el máximo. El disco de partículas tiene varios km de radio y un espesor de metros.

### 28. Detección híbrida: el suelo y el cielo · 1,1 min
**Idea:** dos técnicas complementarias; una calibra a la otra.
- **FD:** las partículas cargadas excitan el N₂, que emite UV (300–430 nm) de forma isótropa, ~4 fotones por metro y por electrón. Se ve el perfil longitudinal: la integral da la energía calorimétrica y el máximo da X_max. Sólo funciona en noches oscuras y despejadas: ~15% del tiempo.
- **SD:** tanques de 3,6 m de diámetro, 1,2 m de alto, 12.000 l de agua ultrapura y 3 PMT de 9 pulgadas. Muestrean el frente de partículas en el suelo ~100% del tiempo. Dan la dirección (por tiempos) y el tamaño S(1000).
- **Híbridos:** la energía del FD calibra el estimador S(1000) del SD **sin depender de simulaciones**. La escala de energía tiene ~14% de incerteza sistemática.

### 29. AugerPrime y AMIGA: separar electrones de muones · 1,0 min
**Idea:** el SD ve una mezcla, y para la masa hay que separar componentes.
- **SSD:** centellador plástico de 3,8 m² sobre cada tanque. Un centellador delgado responde casi igual a un electrón y a un muón, mientras que el tanque profundo responde mucho más al muón. La combinación separa las componentes **estadísticamente**.
- **RD:** antena de radio de 30–80 MHz en cada estación, para la componente EM en lluvias inclinadas.
- **SPMT y la electrónica nueva (UUB):** más rango dinámico cerca del núcleo y muestreo más rápido.
- **UMD:** muones **bajo tierra**. La separación es **física**: la tierra absorbe lo electromagnético.

**Transición:** «Antes de hablar del UMD, quiero detenerme en cómo un tanque de agua ve partículas.»

### 30. El efecto Cherenkov: un «estampido sónico» de luz · 1,6 min
**Idea:** una partícula más rápida que la luz **en el medio** emite un cono de luz.
**Oral:**
1. **Onda de choque sonora:** un avión emite ondas esféricas a v_s. Si va más rápido (v > v_s), las ondas se superponen en un cono con sin α = v_s/v. Ahí se concentra la energía: el estampido. La foto del F/A-18 muestra la condensación por la expansión detrás del choque; no es el cono de Mach en sí, pero ilustra el régimen supersónico.
2. **Cherenkov:** en agua, la luz viaja a c/n = 2,25×10⁸ m/s (n = 1,33). Un electrón o un muón relativista puede ir a βc > c/n **sin violar la relatividad**: c es el límite en el vacío, no en un medio. La partícula polariza las moléculas a su paso. Cuando β > 1/n, las ondas de cada punto de la trayectoria interfieren constructivamente en un cono con cos θ_C = 1/(βn). Para β → 1 en agua, θ_C = 41°.
3. **Umbral:** β > 1/n, o sea γ > 1,52. Para electrones T > 0,26 MeV; para muones T > 54 MeV.
4. **Cantidad:** la fórmula de Frank–Tamm da ~300 fotones por cm entre 300 y 600 nm: unos 30.000 fotones por cada 1,2 m de un muón vertical. Los PMT ven una fracción después de varias reflexiones en el Tyvek.

**Honestidad con la analogía:** la analogía es cinemática (superposición de ondas en un cono). El mecanismo no es el mismo: en el sonido la fuente empuja el aire; en Cherenkov es la polarización del dieléctrico, que es emisión electromagnética coherente.
**Foto del reactor:** el brillo azul son electrones de decaimientos beta en la pileta. Es azul porque la emisión crece como 1/λ².
**Conexión con Auger:** el VEM es la carga de la luz Cherenkov de un muón vertical que atraviesa el centro del tanque.
**Recordatorio:** «Este concepto vuelve con IceCube.»

### 31. Qué medimos realmente: trazas, tiempos y una función lateral · 1,3 min
**Idea:** del primario sólo tenemos trazas digitalizadas. Todo lo demás es inferencia.
**Oral (evento real, NIM 2015, Fig. 17):** ~3×10¹⁹ eV, θ = 28°, 8 estaciones.
- **Trazas (abajo):** la señal del PMT digitalizada cada 25 ns (40 MHz), en VEM. A 650 m del núcleo (S = 315 VEM) hay un pulso grande y corto, dominado por la componente EM y muchos muones. A 1780 m (S = 11 VEM) se ven pulsos discretos: muones individuales, cada uno ~1 VEM, más una cola EM.
- **Mapa (arriba a la izquierda):** tamaño ∝ señal, color = tiempo. El gradiente de tiempos de llegada da la dirección (~1° de resolución a estas energías).
- **LDF (arriba a la derecha):** la función de distribución lateral ajustada da S(1000), la señal a 1000 m, poco sensible a fluctuaciones y a la forma de la LDF. Corregida por atenuación según θ y calibrada con el FD, da la **energía**.

**Mensaje:** nunca vemos el primario. Hay incertezas estadísticas (Poisson, fluctuaciones de la lluvia) y sistemáticas (escala de energía, modelos hadrónicos, respuesta del detector).

### 32. Muones: mensajeros de la cascada hadrónica · 1,3 min
**Idea:** los muones vienen directamente del esqueleto hadrónico, y los modelos no los reproducen.
**Oral:**
- **Origen:** decaimiento de π^± (cτ = 7,8 m) y K^±. Un pión decae o interactúa según su energía y la densidad del aire: por eso la producción de muones depende de la altura.
- **Supervivencia:** cτ_μ = 659 m, pero con γ = 10 (1 GeV) son ~6,6 km. Además pierden ~2 MeV por g/cm² por ionización, ~2 GeV en atravesar la atmósfera vertical. Casi no hacen bremsstrahlung (m_μ/m_e = 207), así que conservan trayectorias casi rectas desde donde nacieron. Su distribución en el suelo es una «proyección» de la región de producción.
- **Masa:** N_μ ∝ A^(1−β)E^β.
- **Física hadrónica:** los muones son la huella de interacciones a √s ~ 100 TeV y de la región frontal (*forward*), que el LHC mide poco.

**Enigma de los muones (Auger, PRL 2016):** en eventos híbridos inclinados de 6–16 EeV, la señal hadrónica medida es 1,33 ± 0,16 veces la predicha por EPOS-LHC y 1,61 ± 0,21 la de QGSJet-II-04. Otros experimentos también ven exceso por encima de ~10¹⁶ eV (metaanálisis WHISP). No hay explicación aceptada.

### 33. El detector subterráneo de muones (UMD) · 1,3 min
**Idea:** el UMD **cuenta** muones con centelladores enterrados. No es Cherenkov.
**Oral:**
- **Estación:** 3 módulos de 10 m² (30 m²) enterrados a 2,3 m junto al tanque. Son ~540 g/cm² de tierra, equivalentes a más de media atmósfera vertical.
- **Blindaje:** absorbe la componente EM hasta un nivel despreciable en las distancias relevantes. Impone un umbral de ~1 GeV para muones verticales, ~1 GeV/cos θ para inclinados (la columna de tierra crece).
- **Detector:** cada módulo tiene 64 tiras de **centellador plástico** (4 m × 4,1 cm × 1 cm) con fibra óptica corredora de onda, leídas por 64 SiPMs (fotomultiplicadores de silicio).
- **Mecanismo:** el muón ioniza el plástico y el plástico **centellea**. La luz viaja por la fibra al SiPM. No hay umbral de velocidad como en Cherenkov.
- **Modo binario (la figura):** el pulso se discrimina (V_thr) y se muestrea cada 3,125 ns (320 MHz). Un patrón «1x1» en tres muestras es un muón. Luego hay una ventana de inhibición (~22 ns) para no contar dos veces el mismo pulso. Contar tiras en ventanas temporales y corregir por apilamiento (estadística de Poisson sobre 64 tiras) da N_μ por módulo. A densidades altas, cerca del núcleo, se usa el modo integrador (carga ADC).
- **Resultado:** la densidad de muones en cada estación, que es lo que usa mi tesis.

**Diferencia con el tanque (decila explícitamente):** el tanque mide luz Cherenkov total, en VEM, de electrones, fotones convertidos y muones de cualquier energía por encima de ~50 MeV. El UMD cuenta partículas que atravesaron 2,3 m de tierra: muones de más de ~1 GeV.

---

## BLOQUE 4 — Mi tesis

### 34. ¿Se ve la asimetría con muones puros? · 1,2 min
**Idea:** la pregunta de la tesis.
**Oral:** En una lluvia inclinada definimos el **plano de la lluvia** (perpendicular al eje) y el azimut φ en ese plano. φ = 0 es la región **temprana**: la parte del suelo que la lluvia alcanza primero, más cerca de la región de producción. φ = ±180° es la **tardía**. Aunque proyectemos al plano de la lluvia, la densidad no es circular. Se parametriza con el primer armónico, ρ(φ) = ρ₀(1 + A₁ cos φ); A₁ es el observable central.
**Antecedentes:** en el SD, la asimetría de la señal total se estudia desde Pryke (1998) y Bertou–Billoir (2000), y Bradfield (2022) estudió su relación con la masa. Correlaciona con X_max, pero mezcla componentes EM y muónica, con comportamientos ambiguos (inversiones de signo a gran distancia).
**Lo nuevo:** el UMD permite estudiarla con **muones aislados**, cosa que no se había hecho.
**Mecanismos (Cap. 3):** dilución geométrica con la distancia a la región de producción, atenuación atmosférica, respuesta del detector (proyección del área según el ángulo de incidencia) y divergencia cinemática de la emisión. El campo geomagnético es una distorsión aparte.
**Objetivo:** A₁ en función de r, θ, E y del primario; y si sirve para separar masas.

### 35. Cómo lo estudié · 1,1 min
**Idea:** simulaciones completas, desde la lluvia hasta la reconstrucción, y dos niveles de realismo.
**Oral:**
- Producción oficial de Auger: CORSIKA para la lluvia y Offline para la respuesta del detector y la reconstrucción, igual que en los datos.
- Primarios p, He, O y Fe en 10^17,5–10^18 eV, con SIBYLL 2.3e como modelo principal; QGSJET-III.01 y EPOS-LHC-R para comparar.
- Lectura de los archivos con Python (PyROOT → parquet), densidad de muones por módulo en bines de (r, θ) y ajuste del primer armónico con errores *bootstrap* sobre lluvias.
- **Anillo Denso:** 12 estaciones virtuales a 450 m en el plano de la lluvia, cada 30°. Es un laboratorio ideal, sin la geometría irregular del arreglo.
- **Arreglo de 750 m:** la geometría real.
- **MC frente a REC:** con el núcleo y la dirección verdaderos, o con los reconstruidos por Offline. La diferencia mide qué pierde el experimento real.

**La figura:** Anillo Denso, protones, 59–65°, N_μ reconstruido. El coseno ajusta con χ²/ndf ≈ 1. A₁ = 0,068 ± 0,006, o sea ±7%: una diferencia temprana–tardía de ~14%.

### 36. La asimetría sobrevive en los muones · 1,3 min
**Idea:** sí, la asimetría está en los muones, y es mayor para lluvias livianas.
**Izquierda:** A₁ frente a θ en el Anillo Denso, para el UMD con N_μ inyectado, el UMD reconstruido y la señal total del SD. Crece con la inclinación hasta A₁ ~ 0,09–0,10 a 45–55°. **La componente EM no es necesaria** para la asimetría.
**Derecha:** protón (azul) frente a hierro (rojo). El protón queda por encima en casi todos los bines. La métrica de la tesis (diferencia de medias en unidades de la incerteza combinada) llega a ~2,5 en 40–55°.
⚠ **Cuidado con la frase:** es la significancia de una diferencia de **medias** con la estadística simulada. No es separación evento a evento, porque la dispersión de A₁ lluvia a lluvia no se evaluó. Si alguien pregunta «¿sirve para composición?», la respuesta honesta es «la sensibilidad está; falta cuantificar con cuántos eventos».
**Interpretación (fenomenológica):** A₁ ∝ (r/D)·tan θ, donde D es la distancia entre la región de producción de muones y el suelo. Un primario liviano (o más energético) penetra más, D baja y A₁ sube. Esto explica que la tendencia con X_max del UMD sea **opuesta** a la del SD, donde domina la componente EM y la asimetría sigue el gradiente del perfil longitudinal. Robustez: A₁ no depende del azimut de llegada, y SIBYLL frente a QGSJET-III para helio difieren en ±10%.

### 37. Hallazgo 1: un sesgo de selección en el SD · 1,6 min
**Idea:** una asimetría puede invertirse sin que se mueva un solo muón, sólo por qué estaciones entran al promedio.
**Oral:**
- **El fenómeno conocido:** la asimetría de la señal del SD alcanza un máximo, baja y se **invierte** lejos del núcleo. En simulaciones, el responsable es su componente muónica. El UMD no lo hace.
- **La prueba (figura):** mismos conteos MC de muones del SD, mismas coordenadas, mismo ajuste. Lo único que cambia es si se promedia sobre **todas** las estaciones simuladas o sólo sobre las que **forman parte del evento reconstruido** (el criterio estándar del análisis, `HasStation`). Con todas, A₁ > 0 a toda distancia. Con las seleccionadas, la curva cae a −0,124 ± 0,019 en 1200–1350 m, frente a +0,069 ± 0,016 con todas.
- **El mecanismo (dibujo):** la componente EM es más intensa del lado temprano, así que allí disparan estaciones aunque tengan 0 o 1 muón. Del lado tardío, con la mitad de partículas EM, sólo entran estaciones ricas en muones. En esa banda entra el 42% de las tempranas y el 18% de las tardías. Las tardías retenidas terminan con **más** muones promedio (1,69 frente a 1,49), aunque la densidad que llega al suelo es mayor del lado temprano.
- **Evidencia adicional (respaldo R4):** los tanques excluidos tienen ≤ 1 muón en el 95% (tempranos) y el 93% (tardíos) de los casos.

**Qué es un sesgo de selección:** el promedio sobre una muestra elegida según una variable correlacionada con lo que se mide no es el promedio verdadero. Si la probabilidad de selección depende distinto del contenido de muones en cada región, el promedio seleccionado deja de representar la densidad incidente.
**Alcance (decilo):**
- El mecanismo es **compatible**, no está demostrado. «Formar parte del evento» resume disparo, lectura y reconstrucción, y esas etapas no se separaron.
- Aun sin selección, entre 150 y 900 m el UMD queda 0,03–0,06 por encima de los muones del SD (excluye cero al 95%). Esa diferencia queda abierta.
- La curva del UMD también usa estaciones seleccionadas: se espera un efecto menor, pero no se puede descartar lejos del núcleo.

**Implicancia:** toda comparación entre detectores, o entre simulación y datos, tiene que usar la misma selección.

### 38. Hallazgo 2: el núcleo reconstruido se corre · 1,3 min
**Idea:** un sesgo sistemático de la reconstrucción, estimable, borra la asimetría cerca del eje.
**Oral:**
- **Figura:** diferencia entre la posición radial verdadera y la reconstruida de cada estación, en función del azimut, para tres bandas de θ. Es una sinusoide: el núcleo reconstruido está corrido hacia la región **temprana**, con b ≈ 9, 15 y 21 m para θ = 20–30°, 30–40° y 40–50°.
- **Causa propuesta:** la reconstrucción ajusta una LDF azimutalmente **simétrica** a una señal que no lo es. El ajuste «explica» el exceso temprano acercando el núcleo a esas estaciones. Es una hipótesis consistente, no una demostración del algoritmo.
- **Efecto sobre A₁:** dentro de un bin radial, las estaciones tempranas vienen en realidad de más lejos (menos muones) y las tardías de más cerca. Con ρ ∝ r^(−β), ΔA₁ ≃ −β b/r.
- **Prueba (tabla, 450–600 m):** reemplazando por separado la distancia y el azimut verdaderos por los reconstruidos, el azimut no cambia nada y la distancia explica casi toda la pérdida: −0,110 observado frente a −0,102 predicho en 40–50°.

**Consecuencias:** con geometría reconstruida, A₁ del UMD cae a 0,01–0,05 entre 600 y 1050 m (frente a ≈ 0,11 con MC). Como es un sesgo estimable y no ruido, se puede corregir o modelar: mejorar el núcleo, por ejemplo con una LDF que incluya modulación azimutal, es tan importante como el detector.
⚠ El acuerdo entre la predicción y lo observado depende en un 10–15% de cómo se ajusta β y de qué r se usa en el bin (lo notamos al preparar la charla de la colaboración). Decí «acuerdo a nivel del 10%».
**Otro efecto (respaldo R3):** sesgo direccional en N_μ reconstruido. Explica la degradación hasta 35°; arriba, de la mitad a dos tercios.

### 39. Primera mirada a los datos de campo · 1,1 min
**Idea:** la modulación aparece en datos reales, con la fase esperada.
**Oral:**
- **Datos:** UMD en el arreglo de 750 m, producción v4r2. Fase I va de abril de 2021 a abril de 2023 y Fase II (SPMT) de febrero de 2022 a mayo de 2026, excluyendo la puesta en marcha de 2022. Selección 6T5, lg E ≥ 17,5 y rechazo de estaciones y contadores marcados.
- **Resultado:** en Fase II, 18,0 ≤ lg E < 18,5, 50° ≤ θ < 60° y 750 ≤ r < 1250 m, A₁ = 0,063 ± 0,017, con el máximo en φ ≈ 0. Hasta donde sabemos, es la primera observación de esta asimetría con una señal muónica aislada de la EM.

⚠ **Alcance:**
- Es preliminar y no es un resultado oficial de la Colaboración.
- No hay estudio de sistemáticos.
- Las simulaciones llegan sólo hasta 10¹⁸ eV, y este bin está en 18,0–18,5.
- La significancia estadística es ~3,7σ para ese bin, elegido con criterio físico (alta inclinación, alta energía), pero sin una corrección por elecciones de bin.

**Otras bandas (respaldo R6):** en general siguen las simulaciones reconstruidas, incluida la A₁ negativa cerca del núcleo en las más inclinadas, que es el corrimiento del núcleo de la diapositiva anterior.
⚠ En la tesis, el texto de la sección dice 40–60° y el pie de la figura 50–60°. Acá uso lo de la figura y las conclusiones (50–60°). Verificalo antes de la charla.

### 40. Detectar no alcanza · 0,8 min
**Idea:** el mensaje metodológico, y que hacer ciencia acá abre puertas.
**Oral:** Leé el recuadro. Después, los tres ejemplos de la tesis: la **señal** (contar muones bajo tierra no es medir luz Cherenkov), la **selección** (el promedio sobre estaciones elegidas puede invertir el signo) y la **reconstrucción** (un núcleo corrido 20 m borra casi toda la asimetría cerca del eje).
**Recorrido (rápido, sin currículum):** empecé en ITeDA en agosto de 2025; presenté avances en la Colaboración; fui a RAFA 2026 en Catamarca (septiembre); defendí en FCEN el 16 de octubre; la nota interna sigue en curso. El 4 de noviembre presento en el UMD Foundations Meeting de la Colaboración. Mencioná las conferencias en Brasil sólo si las tenés confirmadas.
⚠ **Revisá las fechas:** vos me dijiste «una presentación en marzo», pero el cuaderno de trabajo (`Trabajo.tex`) dice «UMD Foundations Meeting (Feb 2026)». En la slide puse «mar. 2026 — presentación en la Colaboración Auger». Corregilo si fue en febrero. No encontré en el material el nombre, la fecha ni la sede de las conferencias en Brasil. Decí lo que sepas oralmente o sacá esa línea. La nota GAP aparece en el repo como GAP2026_041: confirmá el número antes de mostrarlo (en la slide sólo dice «nota interna GAP»).
**Transición:** «Todo esto con partículas cargadas. Pero las cargadas se desvían. ¿Cómo encontramos las fuentes?»

---

## BLOQUE 5 — Neutrinos e IceCube

### 41. ¿Por qué neutrinos? La portada, explicada · 1,0 min
**Idea:** el cierre de la imagen inicial: cada mensajero tiene un destino distinto.
**Oral:** Volvé a la imagen de la portada:
- El **protón** (curva) se desvía en campos magnéticos.
- El **gamma** (recta blanca que se corta) se absorbe al producir pares con fotones de fondo.
- El **neutrino** (línea celeste) llega derecho y sin absorberse.

**Ventajas físicas, más allá de la línea recta:**
- Interactúa sólo débilmente: escapa de ambientes **opacos** a la luz, como núcleos de AGN o el interior de una estrella colapsando.
- Se produce casi sólo en interacciones **hadrónicas**: un neutrino de alta energía es una firma de protones o núcleos acelerados.
- Viaja desde distancias cosmológicas sin perder energía.

**El precio:** σ_νN(1 PeV) ~ 10⁻³³ cm², λ ~ 2×10⁴ km en hielo. En 1 km de hielo interactúa uno de cada ~20.000. Hacen falta volúmenes de km³.
⚠ A PeV la Tierra es **opaca** a los neutrinos que la atraviesan por el diámetro. Por eso IceCube mira los de alta energía cerca del horizonte o desde arriba. No digas que «atraviesan la Tierra sin interactuar» para estas energías.

### 42. De dónde salen los neutrinos astrofísicos · 1,0 min
**Idea:** los mismos piones dan neutrinos y gammas.
**Oral:**
- Un protón acelerado choca con gas (pp) o con fotones (pγ) del entorno y produce piones. π⁰ → γγ; π^± → μν_μ y después μ → eνν.
- Cada neutrino se lleva ~1/20 de la energía del protón y cada gamma ~1/10.
- Sabores en la fuente ν_e:ν_μ:ν_τ ≈ 1:2:0. Tras oscilar en distancias astronómicas, ≈ 1:1:1 en la Tierra. Por eso llegan ν_τ aunque casi no se produzcan, y eso es clave para HERON.

**Consecuencia:** si la fuente es transparente, por cada neutrino hay gammas de energía comparable. Si vemos neutrinos sin los gammas esperados, la fuente es **opaca** (los gammas se reabsorben y cascadean a energías menores): ese es el caso de NGC 1068.
**Matiz:** los gammas también pueden venir de electrones (Compton inverso). Por eso un gamma no prueba aceleración hadrónica y un neutrino sí.

### 43. Auger también busca neutrinos · 0,8 min
**Idea:** Auger no es un telescopio de neutrinos, pero busca firmas de neutrinos en lluvias muy inclinadas.
**Oral:** Un rayo cósmico muy inclinado atraviesa mucha atmósfera: al suelo llega una lluvia **vieja**, sólo muones con frente plano y trazas cortas. Un neutrino puede interactuar cerca del suelo y producir una lluvia **joven**, con mucha componente EM, frente curvo y trazas largas en los tanques. Dos canales:
- **Descendente:** cualquier sabor, θ > 60°.
- **Rozando la Tierra:** un ν_τ entra apenas por debajo del horizonte, en la Tierra o en los Andes. Produce un τ (cτ ≈ 50 m · E/PeV) que sale y decae en el aire.

**Resultados:** sin candidatos. Son límites de los más restrictivos a energías de EeV. También hubo búsquedas en coincidencia con ondas gravitacionales, por ejemplo GW170817.
**Honestidad:** su aceptación para neutrinos empieza en ~10¹⁷ eV y es mucho menor que para rayos cósmicos. No es equivalente a IceCube.

### 44. IceCube: un kilómetro cúbico de hielo antártico · 0,8 min
**Idea:** un detector que usa el hielo del Polo como medio.
**Oral:**
- 86 cuerdas, perforadas con agua caliente, con 60 módulos ópticos digitales (DOM) cada una: 5160 sensores entre 1450 y 2450 m de profundidad. A esa profundidad la presión cierra las burbujas de aire.
- Separación de 17 m en vertical y ~125 m entre cuerdas. DeepCore es más densa y baja el umbral a ~10 GeV.
- El hielo es extraordinariamente transparente: longitud de absorción de ~100–250 m, scattering ~25 m.
- Completado en diciembre de 2010. Arriba, IceTop es un arreglo de tanques de hielo que mide lluvias.
- La foto es el laboratorio IceCube bajo una aurora austral.

### 45. Premio Nobel de Física 2026: Francis Halzen · 0,8 min
**Idea:** el Nobel reconoce el nacimiento de la astronomía de neutrinos de alta energía.
**Oral:** El 6 de octubre de 2026 la Real Academia Sueca otorgó el Nobel a Francis Halzen «por sus contribuciones decisivas al Observatorio de Neutrinos IceCube y al descubrimiento de neutrinos de alta energía de origen astrofísico». La traducción es mía.
- **Historia:** Markov propuso en 1960 usar agua profunda y la luz Cherenkov. Halzen impulsó usar el hielo del Polo, primero con AMANDA (1990s) y después con IceCube.
- **El descubrimiento:** en 2013 se identificó un flujo de neutrinos de TeV–PeV que no puede ser atmosférico.

**Por qué es un cambio:** es una nueva ventana para mirar el universo, como lo fue la astronomía en rayos X. Además es una ventana a los procesos hadrónicos, que con luz no se ven directamente.
La foto es la colaboración IceCube: otra vez, ciencia de colaboración.

### 46. Otra vez Cherenkov, ahora en el hielo · 1,0 min
**Idea:** el mismo efecto que en el tanque de Auger, pero el hielo es a la vez blanco y detector.
**Oral:**
- **El neutrino no emite luz:** es neutro. Interactúa con un núcleo del hielo, ν_μ + N → μ + X por corriente cargada, y la partícula cargada secundaria emite Cherenkov.
- Para un muón de TeV la luz es un cono de ~41° (n_hielo ≈ 1,31) a lo largo de kilómetros. Además pierde energía estocásticamente (bremsstrahlung, pares, interacciones fotonucleares), con emisión secundaria.
- Cada DOM (inserto) tiene un PMT de 10″ y digitaliza la forma de onda con resolución de ~2 ns.
- Los **tiempos de llegada** en los distintos DOMs, con el ángulo de Cherenkov conocido, dan la dirección. La **carga total** da la energía depositada.

**Contraste con Auger:** en Auger el agua sólo muestrea una lluvia producida en el aire. En IceCube el hielo es donde ocurre la interacción y donde se mide la luz.

### 47. Trazas y cascadas · 0,8 min
**Idea:** dos topologías con ventajas complementarias.
- **Traza:** ν_μ por corriente cargada. El muón recorre kilómetros y la traza larga da muy buena dirección (≲1°, hasta ~0,3° a alta energía). Pero sólo se ve parte de su energía: el muón entra o sale del volumen.
- **Cascada:** ν_e por corriente cargada, ν_τ (salvo a muy alta energía) y corriente neutra. La lluvia hadrónica o EM mide ~10 m: vista desde 125 m, es casi una esfera de luz. Contiene casi toda la energía (~10–15% de resolución), pero la dirección es de ~10° o peor.
- **Bonus:** el «doble estallido» del ν_τ (producción y decaimiento del τ) y la resonancia de Glashow (ν̄_e + e⁻ → W⁻ a 6,3 PeV), observada en 2021.

### 48. Una década de descubrimientos · 1,3 min
**Idea:** de un flujo difuso a fuentes individuales.
- **2013 — flujo difuso:** neutrinos de TeV–PeV de origen astrofísico, con un espectro ~E^(−2,5). Se ve con trazas y con cascadas. La flecha marca el evento Glashow.
- **2017 — TXS 0506+056:** el neutrino IC-170922A (~290 TeV) llegó en coincidencia con un blazar en erupción gamma (Fermi, MAGIC), a ~3σ. Un análisis de archivo encontró además un exceso en 2014–15.
- **2022 — NGC 1068:** ~80 neutrinos de una galaxia de Seyfert cercana (14 Mpc), a 4,2σ, sin la emisión gamma de TeV esperada. El núcleo es opaco y los neutrinos vienen de muy cerca del agujero negro (corona).
- **2023 — Vía Láctea:** emisión de neutrinos del plano galáctico (4,5σ), compatible con rayos cósmicos que interactúan con el gas interestelar, la misma física que los gamma de Fermi.

**Mensaje:** la fuente más clara en neutrinos no es la más brillante en gammas.

### 49. Auger e IceCube: dos instrumentos, dos problemas · 0,7 min
**Idea:** no son competidores; resuelven problemas distintos.
**Oral:** Recorré la tabla.
- La **aceptación** sale del producto entre el blanco disponible y la probabilidad de detección. Para rayos cósmicos el blanco es la atmósfera: interactúan seguro y Auger necesita área. Para neutrinos el blanco tiene que ser denso y enorme, porque la probabilidad de interacción en 1 km de hielo a 1 PeV es ~5×10⁻⁵, y por eso IceCube necesita volumen.
- Auger ve rayos cósmicos y busca neutrinos inclinados; IceCube ve neutrinos y también mide muones atmosféricos y lluvias (IceTop).

### 50. Astronomía multimensajero · 0,9 min
**Idea:** cada mensajero aporta información distinta de la misma fuente.
**Oral:** Los rayos cósmicos se desvían, los fotones pueden absorberse, y los neutrinos y las ondas gravitacionales llegan directo. Juntos reconstruyen el acelerador: su geometría, su contenido de hadrones y su mecanismo.
**GW170817 (17/08/2017):**
- Fusión de dos estrellas de neutrones a ~40 Mpc. Primero las ondas gravitacionales (LIGO–Virgo).
- +1,7 s: GRB 170817A (Fermi-GBM, INTEGRAL).
- +11 h: kilonova en NGC 4993.
- +9 días: rayos X; +16 días: radio.
- Nucleosíntesis de elementos pesados (proceso r) y una medición independiente de H₀.
- IceCube, ANTARES y Auger buscaron neutrinos y no encontraron ninguno. Es compatible con un chorro visto fuera del eje.

**Matiz:** la velocidad de las ondas gravitacionales resultó igual a c dentro de ~10⁻¹⁵.

---

## BLOQUE 6 — HERON y cierre

### 51. El problema de la ultra alta energía · 0,9 min
**Idea:** para neutrinos de EeV hacen falta cientos de km³ efectivos. Con luz no se puede.
**Oral:** N_ν = T∫dE Φ_ν(E)[AΩ]_ef(E). Hay que distinguir:
- **Sección eficaz:** propiedad de la interacción, crece ~E^0,36.
- **Probabilidad de interacción** en un espesor L: P ≈ nσL.
- **Volumen instrumentado:** donde hay sensores.
- **Volumen efectivo:** donde una interacción se detecta. Puede ser mucho mayor que el instrumentado, como en radio.
- **Aceptación:** volumen efectivo × probabilidad de interacción × ángulo sólido, en km² sr.
- **Exposición:** aceptación × tiempo.

**Por qué radio:** la luz óptica se absorbe en ~100 m de hielo, así que hacen falta sensores cada ~100 m. Llevar 1 km³ a 100 km³ requeriría cientos de miles de sensores. Las ondas de radio viajan km en hielo frío y decenas de km en aire, y como la emisión es coherente, la potencia crece como E². A cambio, el umbral es alto (~10¹⁶–10¹⁷ eV).
**El régimen existe:** KM3NeT detectó KM3-230213A, de ~220 PeV (*Nature*, 2025): el neutrino más energético observado.

### 52. Escuchar lluvias: dos mecanismos de emisión en radio · 1,0 min
**Idea:** en el aire domina el campo geomagnético; en medios densos, el exceso de carga.
- **Geomagnético (aire):** en el frente de la lluvia, la fuerza de Lorentz del campo terrestre separa e⁺ y e⁻ en sentidos opuestos. Aparece una **corriente transversal** cuya intensidad crece y decrece con el desarrollo de la lluvia, y su variación temporal irradia. Para λ mayor que el espesor del frente (~m, o sea ≲100 MHz), las contribuciones suman en fase: emisión **coherente**, con amplitud ∝ número de partículas ∝ E y potencia ∝ E². La polarización va según v × B, una firma reconocible.
- **Askaryan (medios densos):** en una cascada en hielo, sal o regolito, los electrones del medio se suman por Compton y por aniquilación de positrones. Queda un ~20% de **carga negativa neta**, y esa carga que se mueve más rápido que c/n emite un cono de Cherenkov en radio, coherente, a ~56° en hielo (n ≈ 1,78). La usan RNO-G e IceCube-Gen2 Radio.
- **En el aire también hay efecto Askaryan**, pero es subdominante (~10%) frente al geomagnético.

**HERON:** lluvias en el aire de τ que decaen; emisión principalmente geomagnética.

### 53. HERON · 0,9 min
**Idea:** una estrategia distinta: la montaña como blanco y el aire como calorímetro.
**Oral (sobre la figura del concepto):**
1. Un ν_τ que llega casi horizontal atraviesa la roca de la montaña o del valle e interactúa: ν_τ N → τ X.
2. El τ (cτ ≈ 50 m · E/PeV, ~5 km a 100 PeV) sale al aire y decae.
3. Se forma una lluvia casi horizontal, ascendente, que emite pulsos de radio.
4. Las antenas sobre la ladera (~1000 m sobre el valle) miran hacia abajo, hacia un volumen de aire enorme.

**Lo híbrido:** 24 estaciones **en fase** (tipo BEACON, 24 antenas cada una) suman las señales con retardos. Es *beamforming*: baja el umbral de disparo y discrimina el ruido. Además, 360 antenas **autónomas** dispersas (tipo GRAND, ~15 por estación) muestrean la huella de radio para reconstruir la dirección, la energía y la polarización, y rechazar fondos. En total son menos de 1000 antenas.
**Objetivo:** neutrinos de ~100 PeV, donde el flujo esperado es mayor que a EeV, y fuentes **transitorias**.

### 54. HERON desde San Juan · 0,7 min
**Idea:** un proyecto de I+D con sitio argentino y estado honesto.
- **Sitio:** provincia de San Juan, en la precordillera: una sierra de 72 km sobre un valle de 30–60 km entre los Andes y la Sierra de Valle Fértil. El ruido de radio humano es muy bajo; se midió in situ en abril de 2022.
- **Sensibilidad:** ~10 veces la sensibilidad instantánea de los instrumentos actuales. Ve el ~6% del cielo a la vez y ~70% por día.
- **Instituciones:** CNEA (con autores de ITeDA y del Centro Atómico Bariloche), IAP–Sorbonne (Francia), IGFAE (España) y Penn State (EE. UU.), con las colaboraciones BEACON y GRAND.
- **Estado:** proyecto de **I+D**, con diseño preliminar en optimización y sitio identificado. No hay fecha de despliegue publicada.

⚠ Las fuentes institucionales no detallan el rol específico de ITeDA. Si lo conocés, contalo oralmente; en la slide no lo especifiqué.
**Frase:** «No es un IceCube más grande: es otra idea.»

### 55. Tres soluciones experimentales a tres problemas físicos · 0,7 min
**Idea:** síntesis comparativa, sin competencia.
**Oral:** Cada experimento elige su blanco, su señal y su geometría según lo que quiere medir:
- **Auger:** superficie, porque las partículas cargadas interactúan seguro en la atmósfera.
- **IceCube:** volumen denso y transparente, porque los neutrinos casi no interactúan.
- **HERON:** montaña más aire más radio, porque a 100 PeV hace falta un volumen gigantesco y el radio puede vigilarlo con pocas antenas.

El eje de abajo marca los rangos aproximados de energía.

### 56. Cierre · 0,6 min
**Idea:** recuperar el hilo y dejar una frase.
**Oral:** Recorré la lista: Salta, Mendoza, mi tesis, el Polo Sur, San Juan. Después, la frase: «Las huellas del universo también se leen desde la Argentina». Cerrá con lo institucional en una oración: se puede hacer la ciencia más avanzada del mundo desde acá, colaborando internacionalmente y desarrollando localmente conocimiento, instrumentos, tecnología y recursos humanos.
**Foto:** una estación de Auger bajo la Vía Láctea, con lluvias dibujadas. Es la misma imagen con la que cerraste la defensa.

### 57. ¡Gracias! · —
Vuelve la imagen de la portada, que ahora se entiende. Dejala durante las preguntas.

---

## Respaldo

- **R0** — Separador.
- **R1 — Cuentas:** energía en julios, la pelota, √s, la tasa de Auger y la fórmula de Frank–Tamm. Útil si alguien pide las cuentas.
- **R2 — Modelo analítico (Cap. 3):** si preguntan por la inversión, el modelo predice A₁ > 0 en ambos detectores. La divergencia sólo favorece la región tardía para p > p* ≃ 2QD/r, y esos muones escasean lejos del núcleo, así que la propagación no explica la inversión.
- **R3 — Sesgo direccional de N_μ:** el sobreconteo es mayor del lado tardío. Si preguntan por qué REC < MC con la geometría fija.
- **R4 — Tanques excluidos:** la evidencia directa del mecanismo de selección.
- **R5 — Desglose del SD:** EM positiva, muones del SD que se invierten, la señal total arrastrada, y la diferencia UMD–SD de 0,03–0,06 que queda abierta.
- **R6 — A₁(r, θ) en el arreglo de 750 m:** MC, y datos frente a simulaciones reconstruidas.
- **R7 — Telescopios de neutrinos en el mundo y técnicas de ultra alta energía.**
- **R8 — Sensibilidad diaria de HERON y fuentes transitorias.**

## Preguntas probables y respuestas cortas

- **¿A₁ sirve para medir composición?** Hay sensibilidad en las medias (~2,5 en unidades de la incerteza combinada, en el Anillo Denso). Falta la dispersión evento a evento para saber cuántos eventos se necesitan.
- **¿El sesgo de selección afecta los resultados publicados del SD?** Afecta la asimetría promediada sobre estaciones seleccionadas lejos del núcleo. Cualquier comparación tiene que usar la misma selección. No evalué análisis específicos.
- **¿Por qué no se corrige el núcleo?** Se puede. Hay dos vías: parametrizar b(θ) en simulaciones y validarlo en simulaciones independientes, o ajustar una LDF con término azimutal. Las dos quedaron como trabajo futuro.
- **¿El déficit de muones de los modelos afecta a A₁?** Es una de las líneas abiertas de la tesis. A₁ es una modulación relativa, así que un factor global de escala no la cambia a primer orden, pero no lo verifiqué.
- **QUBIC frente a BICEP o Simons Observatory:** QUBIC es un demostrador tecnológico de interferometría bolométrica. Su objetivo de σ(r) ≈ 0,015 (instrumento final, 3 años, foregrounds perfectos) no compite hoy con BICEP/Keck. El aporte es la técnica: autocalibración e imágenes espectrales.
- **¿TES o SQUID?** El TES es el sensor (termómetro superconductor); el SQUID es el amplificador de su corriente.
- **¿Por qué IceCube no ve neutrinos de EeV?** El flujo es tan bajo que 1 km³ da tasas de ~0,1 por año o menos. Por eso se busca radio.
