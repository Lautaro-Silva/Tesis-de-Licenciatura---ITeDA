---
title: "Capítulo 3: respuestas y criterios del nuevo borrador"
date: "30 de septiembre de 2026"
lang: es
---

Este documento acompaña al borrador y está dirigido al autor. No forma parte del texto propuesto para la tesis. El borrador está en `03_fenomenologia_DRAFT.tex`; su PDF es `capitulo_3.pdf`.

## 1. Qué conservé y qué cambié

La base de la exposición es **CINEMÁTICA y la GAP vieja**, especialmente el recorrido plano de la lluvia → temprano/tardío → atenuación → proyección → divergencia. Conservé esa manera de introducir el problema. En los párrafos iniciales corregí la redacción y tres puntos concretos: los muones no se producen todos en la primera interacción; la simetría vertical requiere las aproximaciones indicadas; y no corresponde identificar sin más la región de producción muónica con el máximo electromagnético.

Conservé la secuencia de las cuatro ecuaciones principales de CINEMÁTICA: proyección (3.1), dilución por ángulo sólido (3.2), distribución angular a energía fija (3.3) y cociente tardío/temprano (3.4). Las expresiones explicativas añadidas antes de ellas no llevan número. La ecuación **3.4 conserva su número**.

Después de esa ecuación retiré la derivada respecto de la energía, las poblaciones A/B, la energía de cruce y el salto a predicciones numéricas para SD y UMD. Queda una interpretación breve de sus tres factores, seguida por una subsección que explica cómo combinar energías. No reinstalé la afirmación de la GAP vieja de que la ganancia angular necesariamente domina la dilución: la ecuación no permite concluirlo sin especificar los parámetros y la población.

Usé el archivo del esquema que está en la GAP: **2810 × 1504 píxeles**, frente a los **495 × 265** del esquema anterior de la tesis. Es una copia del archivo existente, no una figura redibujada ni una ampliación artificial.

## 2. Atenuación: de dónde sale cada expresión

### La exponencial de Armbruster

En el PDF que señalaste, Armbruster escribe

$$f_{\mathrm{att}}(L)=\exp(-L/\lambda).$$

Está en la sección 2.3.2, ecuación (2.11), página impresa 13. El denominador es **lambda**, una longitud de atenuación. El exponente **gamma** aparece después en la distribución angular, $\mathrm{ADF}(\alpha)\propto\alpha^{-\gamma}$, ecuación (2.19). Son parámetros distintos.

La exponencial resulta de suponer una tasa de pérdida constante por unidad de distancia: si sobreviven $N$ partículas, al recorrer un pequeño tramo se pierde una fracción proporcional a $N$:

$$\frac{\mathrm dN}{\mathrm dL}=-\frac{N}{\lambda}.$$

La solución es $N(L)=N(0)e^{-L/\lambda}$. No hace falta añadir una ley nueva para obtenerla. La hipótesis está en tratar esa longitud como constante y adecuada para la población estudiada.

### La integral que había puesto en INTEGRADO

Esa integral se refería específicamente al **decaimiento del muón**. La supervivencia en un pequeño intervalo de tiempo propio es $\mathrm dP/P=-\mathrm dt_{\mathrm{propio}}/\tau_\mu$. Durante un recorrido $\mathrm ds$,

$$\mathrm dt_{\mathrm{propio}}=\frac{\mathrm ds}{\beta_\mu\gamma_\mu c}.$$

Si la energía permanece constante, se obtiene

$$P_{\mathrm{dec}}(L)=e^{-L/(\beta_\mu\gamma_\mu c\tau_\mu)}.$$

Es la misma forma exponencial, con una longitud de decaimiento definida físicamente. Si la energía disminuye durante el vuelo, $\beta_\mu\gamma_\mu$ cambia y hay que sumar la tasa de decaimiento a lo largo de toda la trayectoria:

$$P_{\mathrm{dec}}(L)=\exp\left[-\int_0^L\frac{\mathrm ds}{\beta_\mu(s)\gamma_\mu(s)c\tau_\mu}\right].$$

En el límite relativista, el integrando es $m_\mu c^2/[c\tau_\mu E_\mu(s)]$. Ésta es la conexión con el tratamiento de Cazón y colaboradores, sección 3.2. La expresión exacta en términos de $\beta_\mu\gamma_\mu$ es la derivación cinemática que se explica aquí; no se la atribuye literalmente a Armbruster.

**Lo que faltaba en mi explicación anterior era distinguir sus alcances.** Una longitud efectiva para una población no es automáticamente la longitud de decaimiento de un único muón. Además, la supervivencia frente al decaimiento no calcula por sí sola el alcance en el suelo, la energía final ni la aceptación del detector. Tampoco una variación de densidad lateral con la profundidad mide solamente pérdidas: puede contener cambios de producción y dispersión espacial.

En el borrador se parte ahora de la exponencial de Armbruster y se llega a la integral en ese orden. No se fija un valor de $\lambda$ para UMD ni se afirma que este mecanismo domine su asimetría.

## 3. Proyección de Billoir: qué quedó pendiente de tu lectura

La fórmula está comprobada directamente en **GAP-2000-017, sección 4, ecuación (4), página 4**. El texto conserva su idea: la dirección de las partículas determina cómo interceptan el suelo, incluso después de proyectar las posiciones al plano de la lluvia.

Las precisiones respecto a CINEMÁTICA son que $p_r$ es una componente radial **con signo**, y que el promedio debe corresponder al flujo de cruce del plano perpendicular al eje. En una población radialmente saliente el término favorece temprano. El hecho de que un muón tenga poca energía no vuelve negativo ese término. No reemplacé esta discusión por una derivación larga, para que puedas compararla con la anterior.

La simple proyección de posiciones de un haz paralelo no basta para producir este efecto. Por eso retiré expresiones como «asimetría espuria por el mapeo», que confundían el cambio de coordenadas con una diferencia física de incidencia.

## 4. Las ponderaciones después de la ecuación 3.4

La ecuación 3.4 compara dos direcciones para **una misma energía**. Para una mezcla, cada energía aporta un número distinto de muones a cada región. Hay que sumar esas contribuciones y formar el cociente al final.

Este ejemplo es **aritmético e inventado**, no un resultado de simulación:

| Grupo de energía | Contribución temprana | Contribución tardía | Cociente tardío/temprano |
|---|---:|---:|---:|
| 1 | 100 | 80 | 0,8 |
| 2 | 1 | 4 | 4 |
| Total | 101 | 84 | $84/101\simeq0,832$ |

El promedio simple de los dos cocientes sería $2,4$: sugeriría un exceso tardío. Pero la suma de partículas da un exceso temprano. El grupo con cociente grande casi no contribuye a la densidad temprana, y no debe recibir el mismo peso que el grupo que aporta 100.

En general, si $R(E)=S_{\mathrm T}(E)/S_{\mathrm E}(E)$,

$$\frac{\int S_{\mathrm T}(E)\,\mathrm dE}{\int S_{\mathrm E}(E)\,\mathrm dE}
=\int w_{\mathrm E}(E)R(E)\,\mathrm dE,
\qquad
w_{\mathrm E}(E)=\frac{S_{\mathrm E}(E)}{\int S_{\mathrm E}(E')\,\mathrm dE'}.$$

Un promedio del cociente sí puede hacerse, **si se usan esos pesos**. El error era usar únicamente el espectro de producción como si coincidiera con las contribuciones que llegan. No se trata de agregar un nuevo mecanismo físico: se trata de sumar correctamente los muones del mecanismo ya descrito.

El segundo punto de la imagen adjunta es la normalización angular. Una distribución más estrecha necesita una altura mayor para mantener probabilidad total uno. Por eso el factor de normalización depende de la energía. Se cancela en un cociente a energía fija; dentro de una suma sobre energías hay que conservarlo. En el borrador la idea aparece en el texto, y la fórmula completa del factor queda en una nota al pie.

No daría por establecido que corregir las ponderaciones «no modifica significativamente» todos los resultados de los modelos. El ejemplo anterior muestra que puede incluso cambiar el signo. La importancia numérica en un cálculo concreto se debe verificar para ese cálculo. Esto es independiente de que un modelo, corregido, siga sin reproducir el contraste medido entre SD y UMD.

## 5. Qué son los modelos exploratorios de esa carpeta

En el script `explainer_kinematic_divergence_simulator.py` hay, entre otros, tres cálculos que conviene distinguir:

1. **Una fuente y una energía.** Las funciones `geometry`, `factors` y `ratio` construyen las dos trayectorias y evalúan el cociente de la ecuación 3.4. No generan una lluvia. Cambiar la energía manteniendo fija la geometría muestra la competencia entre dilución y distribución angular.
2. **Una fuente y un espectro.** `adf`, `region_weight` y `spectrum_weighted_A1` integran las contribuciones de distintas energías. En esa parte se adopta un espectro de producción como potencia y no se calcula el transporte completo entre producción y suelo.
3. **Respuestas de detectores idealizados.** `tank_response` distingue placa, conteo en tanque y señal proporcional a longitud de traza. Otras celdas añaden cortes o estimaciones exploratorias; no convierten al cálculo en una simulación completa de SD y UMD.

La función `A1_from_ratio` transforma un cociente entre dos extremos en un contraste $(1-R)/(1+R)$. Esa cantidad coincide con el coeficiente armónico si el perfil es puramente cosinusoidal; no es, en general, el mismo estimador que ajustar todos los intervalos azimutales de una simulación.

**Esta entrega no vuelve a ejecutar esos modelos ni adopta sus conclusiones numéricas.** El propio modelo a energía fija puede dar cocientes mayores que uno. Por ello no incorporé al capítulo una afirmación general de que los modelos «no pueden invertir» la asimetría. La pregunta concreta sería si reproducen simultáneamente los observables y las poblaciones efectivamente medidos por SD y UMD.

Si ese estudio se incorpora después a la tesis, coincido con el criterio que marcaste: necesita una subsección propia, definición de entradas y aproximaciones, gráficos que separen cada factor y una comparación de observables equivalentes. Tendría que distinguir energía de producción y al suelo, documentar la distribución conjunta de producción y verificar la normalización angular. El artículo de Cazón advierte explícitamente, en su sección 2, que extrapolar una única potencia del espectro hasta bajas energías no describe el espectro real de producción.

No se reintentó el Fast-MC histórico de `Intento Toy Model para Inversion Fallido`, ni se lo confundió con el remuestreo del Anillo Denso del capítulo 5. Este último es otro estudio y queda fuera de esta revisión.

## 6. Por qué la forma del tanque se compensa en la señal muónica

Tu referencia de 2002 es pertinente: **GAP-2002-074, sección 2, páginas 1–2**, lo explica en términos del volumen de agua. La discusión también está en GAP-2000-017, sección 6, y la identidad explícita aparece en Armbruster, ecuaciones (2.14)–(2.16).

Imaginá cortar el tanque en muchos tubos delgados paralelos a la dirección incidente. Cada tubo tiene volumen «área de su sección × longitud de agua». Al sumar todos los tubos recuperás el mismo volumen del tanque, lo mires desde donde lo mires:

$$A_{\mathrm{ef}}\langle\ell\rangle=V.$$

Para un flujo dado, el área efectiva determina cuántos muones entran; la longitud media determina cuánta señal produce cada uno. Si aumenta el primer factor, disminuye el segundo de modo compensatorio. La señal total ideal queda proporcional al flujo y al volumen.

Esto requiere muones pasantes, respuesta lineal en longitud y un flujo aproximadamente uniforme sobre la escala del tanque. **No afirma que toda asimetría del SD desaparezca.** Si hay más flujo de un lado, la señal conserva esa diferencia. Tampoco elimina la apertura geométrica de un **conteo** de muones: ese conteo no está multiplicado por la longitud de las trazas. El borrador desarrolla ahora primero esta imagen y después las dos ecuaciones.

## 7. Para qué sirve recuperar Armbruster

La nueva subsección tiene sólo ese propósito: comprobar que las piezas desarrolladas conducen a un resultado conocido. Se toma una fuente efectiva, una distribución angular como potencia y la atenuación exponencial. La expansión queda

$$A_1\simeq\left(2-\gamma_{\mathrm{ADF}}+\frac{D}{\lambda}\right)\frac{r}{D}\tan\theta.$$

El **+2** viene de expandir $d^{-2}$; el término **$-\gamma_{\mathrm{ADF}}$**, de la distribución angular; y **$D/\lambda$**, de la atenuación. El capítulo muestra las tres expansiones antes de reunirlas. No introduce la pendiente logarítmica general ni una nueva familia de respuestas instrumentales.

La correspondencia con Armbruster es: nuestro $D$ = su distancia axial $d$; nuestro recorrido $d(\phi)$ = su $L$; nuestro $\phi$ = su $\psi$. Se recupera su ecuación (2.33), dentro de sus aproximaciones. El $+2$ no es el término de proyección de una placa; la respuesta de señal muónica del tanque ya incluye la compensación anterior.

## 8. Qué era la sección 3.3 y qué aporta

Era una advertencia sobre **a qué conjunto de estaciones pertenece la media**. No era un cuarto mecanismo de producción o transporte.

Otro ejemplo **inventado**, sólo para entender la operación:

| Región | Conteos de todas las estaciones | Media antes de seleccionar | Conteos retenidos | Media seleccionada |
|---|---|---:|---|---:|
| Temprana | 0, 0, 4, 4 | 2 | 0, 0, 4, 4 | 2 |
| Tardía | 0, 0, 1, 5 | 1,5 | 5 | 5 |

Antes de seleccionar hay un exceso temprano en la media. Después hay uno tardío, aunque no se creó ningún muón ni se modificó ningún conteo. Cambió qué estaciones entran al promedio. Una posible relación con el SD sería que una contribución electromagnética ayudase a retener estaciones tempranas con pocos muones, mientras que las tardías retenidas fuesen más muónicas. **Ese relato es una hipótesis de mecanismo, no algo demostrado por la tabla.**

La fórmula de eficiencias de REVISION e INTEGRADO era una identidad para escribir esa operación. Si se retienen una fracción $\epsilon$ de las estaciones y una fracción $\epsilon_N$ de la suma de sus muones, la media retenida es la media original multiplicada por $\epsilon_N/\epsilon$. En el ejemplo tardío, $\epsilon=1/4$ y $\epsilon_N=5/6$; por eso $1,5\times(5/6)/(1/4)=5$.

Lo que aporta es impedir que se atribuya automáticamente una inversión de la **media seleccionada** a la física de la **población incidente**. También explica por qué usar conteos MC exactos no soluciona una selección no representativa. Perder estaciones al azar reduce la estadística; seleccionar preferentemente según su conteo puede cambiar la media.

Mi propuesta editorial para este borrador es dejar en el capítulo 3 **tres párrafos conceptuales**, sin la fórmula de eficiencias ni números de la auditoría. La comparación antes/después y la investigación de la causa quedan para el capítulo 6. Es una propuesta para tu revisión; no se modificó ese capítulo ni se trasladó automáticamente texto a él.

## Referencias cotejadas

- Armbruster, *Asymmetries of the Lateral Distribution of Particles at the Ground*: portada; secciones 2.2.2, 2.3.2, 2.4 y 2.6; ecuaciones (2.11), (2.14)–(2.21) y (2.33). El documento dice **Bachelor Thesis, junio de 2018**; el número GAP es 2020-066. Luce lo enumera como «master thesis», pero la entrada nueva sigue la portada del documento primario.
- Bertou y Billoir, GAP-2000-017: páginas 3–4 para la proyección y página 7 para la compensación muónica. Se leyeron páginas renderizadas porque la extracción de texto de ese PDF es defectuosa.
- Billoir, Da Silva y Bertou, GAP-2002-074: páginas 1–2, efecto geométrico y señal por volumen. Se agrega esta clave a la bibliografía complementaria.
- Cazón y colaboradores (2012), secciones 2 y 3.2: espectro transversal, correlaciones de producción y decaimiento. [Artículo](https://doi.org/10.1016/j.astropartphys.2012.05.017).
- Luce y colaboradores, ICRC 2021, contribución 435: geometría, parametrización y referencia a Armbruster. [Actas](https://pos.sissa.it/395/435/).

La lectura y la comprobación algebraica respaldan las precisiones de este borrador; no equivalen a una nueva validación cuantitativa de los resultados de simulación de la tesis.
