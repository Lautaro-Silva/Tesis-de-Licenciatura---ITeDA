# Minor corrections for Chapters 3 and 5

Corrections found on the author's final versions of `03_fenomenologia.tex` (6 Oct 2026) and
`05_anillo_denso.tex` (7 Oct 2026). Nothing has been applied to the thesis files: each item is a
**find -> replace** pair, and every "find" string occurs exactly once in those versions (checked by
script), so they can be applied one by one with a text search. Most items are wording, accents or
claims that say slightly more than the data show; items with a note explain why.

Both chapters compile with the `book` class after applying all items. Two issues that are not part
of this list showed up in that build:

- `anexo:linealizacion` is undefined: Chapter 3 refers to the linearisation appendix, which is not
  yet in `09_anexos.tex`.
- `capitulos/imagenes_capitulos/cap3/esquema_lluvia.jpeg` does not exist in the repository (only
  `esquema_lluvia.png` does).

## Chapter 3

### 3.1

*The station-selection discussion moved to Chapter 6; the intro still promised it.*

Find:
```latex
Luego se combinan los mecanismos en un único modelo analítico de juguete, que permite evaluar cualitativamente su competencia, y se discute la diferencia entre la densidad de muones que incide sobre el suelo y el promedio que se mide sobre una muestra de estaciones seleccionadas.
```
Replace with:
```latex
Luego se combinan los mecanismos en un único modelo analítico de juguete, que permite evaluar cualitativamente su competencia y anticipar el signo de la asimetría esperada.
```

### 3.2

Find:
```latex
Vale aclarar que este fenómeno ocurre tanto para la componente electromagnética como la muónica pero con mayor magnitud para la componente EM a causa de ser más interactuante, razón por la cual este mecanismo ya estaba caracterizado.
```
Replace with:
```latex
Vale aclarar que este fenómeno ocurre tanto en la componente electromagnética como en la muónica, pero con mayor magnitud en la EM por ser más interactuante, razón por la cual este mecanismo ya estaba caracterizado en el SD.
```

### 3.3

Find:
```latex
La constante $\lambda>0$ tiene unidades de longitud, después de recorrer
```
Replace with:
```latex
La constante $\lambda>0$ tiene unidades de longitud: después de recorrer
```

### 3.4

*Points to where the two effects are actually compared.*

Find:
```latex
Allí se considera que los muones provienen de una región de producción a distancia finita, y que el haz se sigue abriendo entre el plano de la lluvia y el suelo, pero estos efectos se compararán más adelante.
```
Replace with:
```latex
Allí se considera que los muones provienen de una región de producción a distancia finita, y que el haz se sigue abriendo entre el plano de la lluvia y el suelo; ambos efectos se comparan en la Sección~\ref{subsec:toy_models}.
```

### 3.5

Find:
```latex
el término de Bertou y Billoir \textit{es} la respuesta de un detector plano horizontal. Entonces afecta a la asimetría, con signo positivo.
```
Replace with:
```latex
el término de Bertou y Billoir \textit{es} la respuesta de un detector plano horizontal. Su efecto sobre la asimetría es, por lo tanto, positivo.
```

### 3.6

Find:
```latex
Tal como fue reportado empíricamente por Bradfield \cite{BradfieldThesis} la señal del SD
```
Replace with:
```latex
Tal como fue reportado empíricamente por Bradfield \cite{BradfieldThesis}, la señal del SD
```

### 3.7

*Q is a scale of the p_t distribution, not an upper bound on p_t.*

Find:
```latex
porque el momento transversal está acotado por la cinemática de las interacciones hadrónicas.
```
Replace with:
```latex
porque los momentos transversales grandes son cada vez menos probables en las interacciones hadrónicas.
```

### 3.8

Find:
```latex
Se puede dejar de lado el factor $p^2$ que no depende del ángulo y es constante a energía constante.
```
Replace with:
```latex
A energía fija, el factor $p^2$ no depende del ángulo y puede dejarse de lado.
```

### 3.9

*The old sentence said the sign shows which mechanism dominates and, in the same breath, that it does not.*

Find:
```latex
El signo de $A_1$ indica cuál de los mecanismos de la Sección~\ref{subsec:origen_fisico} domina en el balance, pero no identifica por sí solo a un mecanismo particular.
```
Replace with:
```latex
El signo de $A_1$ indica hacia qué región se inclina el balance de los mecanismos de la Sección~\ref{subsec:origen_fisico}, pero no identifica por sí solo cuál de ellos domina.
```

### 3.10

Find:
```latex
La pérdida de energía de los muones en el aire no se sigue explícitamente, queda absorbida en estos parámetros efectivos.
```
Replace with:
```latex
La pérdida de energía de los muones en el aire no se sigue explícitamente: queda absorbida en estos parámetros efectivos.
```

### 3.11

Find:
```latex
y para la distribución de momentos vale
```
Replace with:
```latex
y para la distribución de Cazón vale
```

### 3.12

*Without p_t ~ p r/D the identity exp(-p_t/Q) = exp(-p/p0) does not follow.*

Find:
```latex
Para llegar a $r$, un muón de momento $p$ necesita un momento transversal $p_t$, y la distribución
```
Replace with:
```latex
Para llegar a $r$, un muón de momento $p$ necesita un momento transversal $p_t \simeq p\,r/D$, y la distribución
```

### 3.13

Find:
```latex
Este resultado corrige una intuición adoptada en las etapas iniciales de este trabajo donde se propuso que
```
Replace with:
```latex
Este resultado corrige una intuición adoptada en las etapas iniciales de este trabajo, en las que se propuso que
```

### 3.14

Find:
```latex
Contrario a esto  la preferencia por la región tardía
```
Replace with:
```latex
Por el contrario, la preferencia por la región tardía
```

### 3.15

Find:
```latex
Repitiendo el cálculo para otros valores de $D$, $Q$ y $\gamma$ la asimetría resultó positiva
```
Replace with:
```latex
Repitiendo el cálculo para otros valores de $D$, $Q$ y $\gamma$, la asimetría resultó positiva
```

### 3.16

Find:
```latex
La conclusión que interesa es cualitativa, la densidad de muones
```
Replace with:
```latex
La conclusión que interesa es cualitativa: la densidad de muones
```

### 3.17

Find:
```latex
la explicación no parece poder explicarse en la propagación de los muones.
```
Replace with:
```latex
la explicación no parece estar en la propagación de los muones.
```

## Chapter 5

### 5.1

Find:
```latex
Este análisis se extendió usando también los datos de tanto la cantidad de muones inyectados por CORSIKA ($N^{\text{MC}}_\mu$) como la señal total
```
Replace with:
```latex
Este análisis se extendió usando también tanto la cantidad de muones inyectados por CORSIKA ($N^{\text{MC}}_\mu$) como la señal total
```

### 5.2

Find:
```latex
como la fuente de la diferencia ente los valores
```
Replace with:
```latex
como la fuente de la diferencia entre los valores
```

### 5.3

*The caption kept the old reasoning that the text already corrected.*

Find:
```latex
mientras que el SD presenta valores elevados debido a la alta precisión estadística de la muestra.}
```
Replace with:
```latex
mientras que el SD presenta valores elevados: con la precisión de su señal, el modelo de primer orden no describe todos los detalles del perfil.}
```

### 5.4

Find:
```latex
Este fenómeno de 'sobreconteo' es intrínseco a los algoritmos de reconstrucción.
```
Replace with:
```latex
Este fenómeno de \textit{sobreconteo} es una característica del algoritmo de reconstrucción.
```

### 5.5

Find:
```latex
Se intento ver si esta asimetría
```
Replace with:
```latex
Se intentó ver si esta asimetría
```

### 5.6

Find:
```latex
Para esto se construyo un modelo
```
Replace with:
```latex
Para esto se construyó un modelo
```

### 5.7

Find:
```latex
donde el sesgo de sobreconteo es máximamente superior al de la región temprana ($0^\circ$).}
```
Replace with:
```latex
donde el sesgo de sobreconteo es claramente mayor que en la región temprana ($0^\circ$).}
```

### 5.8

Find:
```latex
Físicamente, esto se debe a que en las zonas de menor densidad,
```
Replace with:
```latex
Físicamente, esto puede deberse a que en las zonas de menor densidad,
```

### 5.9

Find:
```latex
Este efecto actúa como un ruido coherente que 'lava' la asimetría física intrínseca de la cascada.
```
Replace with:
```latex
Este efecto actúa como un sesgo sistemático que \textit{lava} la asimetría física intrínseca de la cascada.
```

### 5.10

Find:
```latex
y captura con total fidelidad la cola asimétrica
```
Replace with:
```latex
y reproduce la cola asimétrica
```

### 5.11

Find:
```latex
El análisis de estos resultados demuestra que el \textit{Toy Model} logra reproducir
```
Replace with:
```latex
El análisis de estos resultados muestra que el \textit{Toy Model} logra reproducir
```

### 5.12

*From the toy-model figure: ~60 % at 44-49 deg, ~50 % at 54-59 deg, ~40 % at 59-65 deg.*

Find:
```latex
Si bien el sesgo direccional introducido logra explicar más del 50\% de la degradación observada
```
Replace with:
```latex
Si bien el sesgo direccional introducido logra explicar aproximadamente la mitad de la degradación observada
```

### 5.13

*ONLY NON-COSMETIC ITEM: restores the mechanism behind 'lava una parte sustancial' (dA1 ~ -beta b / r).*

Find:
```latex
las estaciones tempranas aparecen más cerca del núcleo de lo que están y las tardías más lejos. Entonces este corrimiento del núcleo lava una parte sustancial de la asimetría reconstruida en el \textit{Infill}.
```
Replace with:
```latex
las estaciones tempranas aparecen más cerca del núcleo de lo que están y las tardías más lejos. Como la densidad cae con la distancia, las tempranas registran menos señal de la que corresponde a su distancia aparente y las tardías más, lo que agrega una modulación de signo opuesto a la física, de tamaño $\sim\beta\,b/r$ (con $\beta\simeq2.5$ la pendiente logarítmica de la LDF; $\approx0.05$--$0.1$ a $450$~m). Este corrimiento lava, por lo tanto, una parte sustancial de la asimetría reconstruida en el \textit{Infill}.
```

### 5.14

Find:
```latex
Se estudio también el comportamiento del detector y el parámetro de asimetría, al enfrentarse a situaciones en las que, al ser circunstancia donde la física es la misma especialmente considerando los efectos de la atenuación atmosférica, no se espera ver cambios en su performance.
```
Replace with:
```latex
Se estudió también el comportamiento del detector y del parámetro de asimetría en situaciones en las que la física, en particular la atenuación atmosférica, es la misma, y por lo tanto no se esperan cambios en su desempeño.
```

### 5.15

Find:
```latex
en función del angulo de incidencia de la lluvia y se repitio el análisis explicando en la sección
```
Replace with:
```latex
en función del ángulo de incidencia de la lluvia y se repitió el análisis explicado en la Sección
```

### 5.16

Find:
```latex
En la Figura \ref{fig:robustez_phi} se analizo el dataset de protones
```
Replace with:
```latex
En la Figura \ref{fig:robustez_phi} se analizó el \textit{dataset} de protones
```

### 5.17

Find:
```latex
Se ve que el valor ajustado del parametro de asimetría $A_1$ no depende del angulo de incidencia de la lluvia, como era esperado. Esto es una buena prueba de estrés para los fundamentos del trabajo y que garantiza que se puede avanzar en el análisis en pos de hacer discriminacion de masa. Nuevamente aparece la discrepancia entre los valores absolutos de asimetria usando los muones inyectados y los reconstruidos.
```
Replace with:
```latex
Se ve que el valor ajustado del parámetro de asimetría $A_1$ no depende del ángulo de incidencia de la lluvia, como era esperado. Esta es una buena prueba de estrés para los fundamentos del trabajo, que permite avanzar en el análisis en pos de hacer discriminación de masa. Nuevamente aparece la discrepancia entre los valores absolutos de asimetría usando los muones inyectados y los reconstruidos.
```

### 5.18

Find:
```latex
Este resultado confirma empíricamente que la amplitud de la asimetría azimutal $A_1$ es un observable robusto.
```
Replace with:
```latex
Este resultado indica, para helio y los dos modelos comparados, que la amplitud de la asimetría azimutal $A_1$ es un observable robusto.
```

### 5.19

*Only helium with two hadronic models was tested.*

Find:
```latex
se utilizo como métrica de evaluación
```
Replace with:
```latex
se utilizó como métrica de evaluación
```

### 5.20

Find:
```latex
sino también su dispersión estadística.
```
Replace with:
```latex
sino también su incertidumbre.
```

### 5.21

*sigma in the merit factor is the fit uncertainty, not the event-by-event spread.*

Find:
```latex
es en modulo tan pequeña
```
Replace with:
```latex
es en módulo tan pequeña
```

### 5.22

Find:
```latex
sino que introduce un ruido correlacionado masivo que dispara el tamaño de las desviaciones estándar ($\sigma$), reduciendo
```
Replace with:
```latex
sino que aumenta la incertidumbre de cada ajuste ($\sigma$), reduciendo
```

### 5.23

*Same as above.*

Find:
```latex
no es un resultado estadístico aislado, sino la manifestación en superficie de la evolución longitudinal intrínseca de la cascada atmosférica.
```
Replace with:
```latex
es consistente con la evolución longitudinal intrínseca de la cascada atmosférica.
```

### 5.24

*The next sentence calls it a working hypothesis.*

Find:
```latex
logaritmo de la energia del primario.
```
Replace with:
```latex
logaritmo de la energía del primario.
```

### 5.25

Find:
```latex
La distancia recorrida de atmosfera hasta llegar al máximo es lo que se denomina $X_{max}$.}
```
Replace with:
```latex
La profundidad atmosférica a la que se alcanza el máximo es lo que se denomina $X_{max}$.}
```

### 5.26

Find:
```latex
sigue de cerca el perfil longitudinal del cascada hadrónica
```
Replace with:
```latex
sigue de cerca el perfil longitudinal de la cascada hadrónica
```

### 5.27

*X_max is an atmospheric depth (g/cm^2), not a distance.*

Find:
```latex
donde cualquier diferencia de proyección geométrica induce fluctuaciones grandes en las densidades relativas de muones.
```
Replace with:
```latex
donde cualquier diferencia de proyección geométrica induce diferencias grandes en las densidades relativas de muones.
```
