# Capítulo 5: alcance y trazabilidad del borrador

Propuesta completa de reemplazo: `05_anillo_denso_DRAFT.tex`. No se modificó el capítulo original, los scripts de análisis, los datos ni la presentación RAFA. Se conservan las trece figuras originales, sus rutas y etiquetas; no se generaron resultados numéricos nuevos.

## Resultado que conserva

El Anillo Denso presenta una modulación UMD positiva, diferencias entre conteos MC y REC, respuesta parcial del modelo empírico de residuos y sensibilidad de las amplitudes medias a energía y primario. La selección `HasStation` demostrada en Infill no invalida estos resultados ni proporciona una corrección automática para el anillo.

## Cambios físicos y metodológicos

- **Signos:** positivo significa exceso temprano; negativo, tardío. Ninguno de esos signos identifica por sí solo el mecanismo dominante. Se retira la supuesta frontera universal de 200 m entre mecanismos.
- **Conteo, geometría y selección:** se distinguen conteos MC/REC, coordenadas MC/REC y estaciones retenidas. Un conteo MC puede pertenecer a una muestra seleccionada mediante reconstrucción.
- **Tanque:** se incorpora `área proyectada × cuerda media = volumen`, válida dirección por dirección para haz localmente uniforme y trayectorias atravesantes. Cancela el factor de apertura en la señal ideal lineal, no el flujo incidente, los conteos ni la selección por señal. No se extrapola a toda respuesta instrumental real.
- **Modelo de residuos:** conserva su éxito descriptivo, pero no lo presenta como predicción causal independiente. El código remuestrea errores relativos por bin azimutal; no inyecta desplazamientos de núcleo. Se explicita que una distribución marginal de residuos no conserva necesariamente la correlación entre residuo y conteo. Se elimina la atribución automática del remanente al núcleo o a trayectorias de borde.
- **Núcleo/LDF:** se muestra mediante expansión de primer orden por qué un desplazamiento produce un dipolo radial y puede imitar una asimetría. El núcleo no es el único parámetro disponible para un ajuste y el patrón no demuestra que los muones blandos sean su causa. La expansión supone dirección fija y desplazamiento pequeño.
- **Masa y energía:** se conserva la interpretación longitudinal como hipótesis; no se identifica el máximo electromagnético con el máximo de producción muónica. Se conserva `2 r tan(theta)/D` únicamente como término de dilución de una fuente axial, no como fórmula completa del UMD. No se reutiliza la estimación histórica de elongación como prueba cuantitativa cerrada.
- **MF:** el código que produce la figura utiliza errores del ajuste, no dispersión intrínseca evento a evento. Se conserva el valor aproximado presentado en RAFA, pero como separación entre estimaciones de muestras en geometría idealizada. No se afirma clasificación de una lluvia individual, desempeño alcanzado en datos reales ni cota superior matemática.
- **Estadística:** un chi cuadrado elevado no queda justificado por tener mucha estadística. Se mantienen los resultados gráficos con advertencias precisas sobre covarianzas y reutilización de lluvias; no se inventa un nuevo presupuesto de incertidumbres.

## Fuentes locales consultadas

1. `Tesis - Latex/capitulos/05_anillo_denso.tex`: capítulo completo, resultados y figuras originales.
2. `claude_work/kinematic_divergence_explainer_and_thesis_updates/05_anillo_denso_DRAFT.tex`: propuesta histórica y estimación de elongación que no se conserva como demostración.
3. `claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/05_anillo_denso_DRAFT.tex`: base estructural de la revisión, ya corregida en varios puntos.
4. `claude_work/gap_notes_asimetrias_review_v4/kinematic_divergence_math_check.md`, `sd_umd_synthesis.md` y `thesis_review_familiarization_notes.md`: geometría, signos y compensación del tanque. Sus inferencias antiguas de inversión del flujo no seleccionado y su promedio de cocientes NO se adoptan: quedaron superadas por el pesaje correcto y por el control de selección.
5. `claude_work/revision_asimetrias_sd_umd/01_fisica/physics_explanation.md` y secciones de observables/control MC de `report.md`: distinción entre transporte, respuesta y selección; alcance limitado del ensayo Infill.
6. `claude_work/presentacion_rafa_2026/presentacion_rafa_2026.tex`, bloques Anillo Denso y sesgos, y `guion.md` completo: hilo de resultados y cautelas de la charla. Se conserva el hilo, no las afirmaciones causales más fuertes del guion.
7. `Scripts/validacion_rec_muones.py`, bloque «TOY MONTE CARLO DIRECCIONAL»: remuestreo de residuos por azimut multiplicando el conteo MC, sin perturbación de núcleo.
8. `Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py`: `extract_a1`/ajustes alrededor de las líneas 170–191 y figura «DISCRIMINACIÓN DE MASA» alrededor de 900–959. `Err` procede de la covarianza de `curve_fit`; ése es el denominador del MF.

## Procedencia de las cifras mantenidas

| Cifra | Procedencia ya existente | Uso en el nuevo texto |
|---|---|---|
| Doce estaciones, radio nominal 450 m | Configuración original y capítulo 5 | Diseño idealizado |
| Modulación pico a pico ~14 %, bin 59.3–65 grados | `Ajuste_UMD_REC_Bin9.pdf`; RAFA | Lectura aproximada de la figura |
| Caída del SD a partir de ~50 grados | `Evolucion_Asimetria_vs_Theta.pdf`; RAFA | Tendencia descriptiva, no causa aislada |
| Chi cuadrado UMD cercano a uno y SD de orden diez | `Chi2_Reduced_Fits.pdf` | Diagnóstico bajo errores del ajuste original |
| Acuerdo aproximado del toy por debajo de ~35 grados | `toy_model.pdf`; código direccional | Acuerdo empírico, no prueba de causa |
| Diferencias de modelos ~10 %, puntuales ~15 % | `Hadronic_Uncertainty_Helium.pdf` | Sólo comparación de helio ensayada |
| Variación energética de A1 ~0.015 | `DenseRing_Systematics_Energy.pdf`; RAFA | Media década 17.5–18.0, no década completa |
| MF ~2.5, ventana ~40–55 grados | `Mass_Discrimination_MF.pdf`; código indicado arriba | Separación de amplitudes de muestras |
| Energía del ejemplo Fly's Eye ~3.2 × 10^20 eV | Figura original `ammount_xmax.jpg`, cita `FlysEye1995` | Ilustración longitudinal, no nueva medición |

Las cifras son las reportadas previamente y se conservan a su precisión aproximada; no se han vuelto a ajustar las muestras. No se reutiliza «más del 50 %» como cifra causal universal del toy, porque la figura no establece una descomposición independiente de mecanismos.

## Qué queda por cerrar antes de una versión definitiva

- Verificar el anillo con igual trazabilidad de población y selección que el nuevo lector Infill; la auditoría Infill no sustituye ese control.
- Evaluar covarianzas por lluvia/lluvia progenitora para las incertidumbres de A1 y la interpretación del MF.
- Para identificar el papel del núcleo, alternar sólo geometría conservando estaciones y conteos, o ensayar reconstrucciones controladas. Un remuestreo marginal de residuos no realiza esa intervención.
- Para atribuir a desarrollo longitudinal las tendencias de masa/energía, contrastarlas con el perfil de producción muónica y sus pesos de energía/ángulo, en lugar de inferirlo únicamente del orden protón–hierro.

Las nuevas etiquetas propias usan el prefijo `dense2026`; se mantienen etiquetas históricas para evitar romper referencias desde otros capítulos.
