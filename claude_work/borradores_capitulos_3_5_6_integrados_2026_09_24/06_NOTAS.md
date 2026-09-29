# Capítulo 6: alcance del nuevo borrador

Texto completo propuesto: `06_infill_DRAFT.tex`. No se modificó la tesis autorizada ni sus figuras.

## Qué cambia

- Mantiene las cuatro figuras originales y las tendencias medidas. Reescribe sus leyendas para distinguir conteo MC, coordenadas MC y selección instrumental.
- Sustituye la explicación causal por muones blandos/proyección negativa por el control de selección `HasStation` sobre estaciones SD simuladas. No atribuye el resultado a un fallo de Offline ni a un umbral único identificado.
- Introduce una identidad exacta de media condicionada. El enriquecimiento muónico tardío por menor ayuda electromagnética queda explícitamente como hipótesis física, no como una etapa del trigger ya aislada.
- Explica que la cancelación apertura–cuerda es local y por dirección para señal muónica ideal: no una cancelación de flujo, de conteos o de selección. Retira el supuesto aporte negativo autónomo del recorrido en agua.
- Agrega la figura antes/después con los mismos bins y una tabla de la corona `[1200,1350)` con errores bootstrap por lluvia. No mezcla estos números con el punto nominal `1200 m` de la charla y las notas GAP.
- Separa la selección de estaciones del error direccional del núcleo mostrado en RAFA y del modelo de remuestreo de residuos de conteo del capítulo 5. Remite a la figura del núcleo ya incluida en ese capítulo, sin duplicarla ni presentarla como un análisis nuevo.
- Retira afirmaciones no demostradas: dominancia universal de atenuación; inmunidad del UMD; inexistencia de armónicos superiores; MC como cota superior y REC como cota inferior universales; equivalencia entre ausencia de verdad UMD y cero físico.
- Convierte las notas inconclusas finales en límites y trabajo pendiente, sin inventar resultados de masa, energía, nuevos primarios o datos reales.

## Procedencia precisa

1. Original y ambos borradores leídos completos: `Tesis - Latex/capitulos/06_infill.tex`; `claude_work/kinematic_divergence_explainer_and_thesis_updates/06_infill_DRAFT.tex`; `claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/06_infill_DRAFT.tex`.
2. Física actualizada: `revision_asimetrias_sd_umd/01_fisica/physics_explanation.md` y `report.md`, especialmente definición del contador previo al agua, media condicionada y falta de verdad UMD anterior a electrónica.
3. Análisis previo: `gap_notes_asimetrias_review_v4/{kinematic_divergence_math_check,sd_umd_synthesis,discriminating_analysis_proposal}.md`. Algunas afirmaciones históricas están superadas: la inversión seleccionada NO obliga a una inversión del flujo no seleccionado; el promedio antiguo de cocientes de espectros no debe recuperarse como validación. La cancelación geométrica se conserva con sus hipótesis.
4. RAFA: `presentacion_rafa_2026/presentacion_rafa_2026.tex` y `guion.md`. Se actualiza el estado de la inversión por selección respecto de la etiqueta preliminar de la charla. No se copia la frase «EM casi no cambia»: el coeficiente sí se modifica, aunque conserva signo positivo. Tampoco se copia que el remuestreo de residuos prueba la causalidad completa de la LDF sobre el núcleo.
5. Valores de la figura: `revision_asimetrias_sd_umd/02_notebooks/02_reproduccion/resultados/seleccion_mismos_bins_ajuste_ponderado.csv`. En el último bin, SD previo `0.06886682701219773`, seleccionado `-0.12399013006585334`; `12212` y `3694` registros respectivamente. Son ajustes ponderados, no los anteriores controles no ponderados de `[1050,1400)`.
6. Tabla e intervalo pareado: `revision_asimetrias_sd_umd/02_notebooks/03_sd_vs_umd/resultados/comparacion_directa.csv`, reproducido por `comparar_sd_umd.py`. Último bin: SD previo `0.06886682694668678`, SD seleccionado `-0.12399013051395794`, UMD `0.08159722791326351`; desviaciones bootstrap `0.015682400928115528`, `0.018569803476739772`, `0.0343698306401132`. Diferencia SD previo menos UMD `-0.012730400966576738`, IC puntual `[-0.0896726076577414, 0.05549185458501617]`. La discrepancia del orden de precisión numérica entre los dos CSV proviene de la solución algebraica frente a `curve_fit`; no cambia cifras publicadas. La banda simultánea disponible es más ancha y no se intercambia con el intervalo puntual.
7. La preservación de los `1589487` registros de módulos y el conjunto SD de `106280 = 51031 + 55249` registros en la ventana extensa se contrastan en la validación independiente del presente directorio. Las filas de módulo y las de estación son unidades distintas.

## Advertencias editoriales y de trazabilidad

El directorio mencionado en la revisión anterior, `claude_work/reprocesamiento_sd_completo/`, no existe en este checkout al 24-09-2026. No se restauró ni se modificó ningún procesamiento para este borrador. Sus parquet v13 permanecen disponibles y pueden contrastarse directamente con v11 y las tablas de referencia; la validación del directorio de borradores documenta esa comparación. Antes de publicación conviene archivar el lector exacto usado por el autor y su versión de biblioteca. El capítulo no presume que una inspección de fuentes locales certifique el binario completo de producción.

El conteo `sd_nMuons_MC` no es la magnitud `sdMuonSignal_REC`: esta última no se emplea en la prueba de inversión. No convertir la coincidencia de conteos en una validación indiscriminada de señales opcionales dependientes del entorno de lectura.

Las nuevas imágenes se enlazan a sus archivos existentes; no se duplican ni regeneran. El documento de vista previa necesita resolver rutas tanto desde `Tesis - Latex/` como desde la raíz del repositorio. Las nuevas etiquetas propias llevan prefijo `infill2026`; se preservan las etiquetas antiguas para referencias cruzadas.

La comparación bootstrap mantiene juntas las reutilizaciones reconocidas por el identificador disponible. No constituye una certificación completa de genealogía CORSIKA, ni incorpora incertidumbre sistemática de respuesta o modelo. La figura antes/después mantiene las barras formales originales para reproducción; la tabla distingue explícitamente sus barras bootstrap.

No se ejecutó producción ROOT, propagador ni simulación nueva al redactar. No se modificaron `Tesis - Latex/`, `GAP_Notes_Latex/`, Offline ni configuraciones institucionales. Los cambios científicos pendientes están expresados como pendientes, no como resultados.
