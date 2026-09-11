# Borradores de los capítulos 3, 5 y 6

Propuesta editorial independiente, 10 de septiembre de 2026. No se modificaron los capítulos originales, las notas GAP ni los borradores anteriores. No se ejecutaron simulaciones nuevas, procesamiento ADST ni ajustes sobre el parquet durante esta preparación.

## Qué leer

- [03_fenomenologia_DRAFT.tex](03_fenomenologia_DRAFT.tex): capítulo completo, con separación explícita de atenuación, proyección, distribución angular, respuesta y selección.
- [05_anillo_denso_DRAFT.tex](05_anillo_denso_DRAFT.tex): capítulo completo basado en el actual, conservando sus figuras y el estudio empírico MC–REC, con interpretaciones físicas y estadísticas acotadas.
- [06_infill_DRAFT.tex](06_infill_DRAFT.tex): capítulo completo propuesto, con el control de selección SD incorporado y las tareas inconclusas identificadas como pendientes.
- [preview.pdf](preview.pdf): vista previa **en el contexto de la tesis completa**, sustituyendo únicamente estos tres capítulos. Los demás capítulos, carátulas y anexos conservan su contenido original, incluidos sus pendientes. No es una versión final revisada de toda la tesis.
- [cambios_03.diff](cambios_03.diff), [cambios_05.diff](cambios_05.diff), [cambios_06.diff](cambios_06.diff): diferencias contra los capítulos actuales, no contra los borradores anteriores.

El formato reproduce la idea de `kinematic_divergence_explainer_and_thesis_updates`: archivos completos para revisar y eventualmente reemplazar manualmente. No conserva las afirmaciones de ese borrador que la auditoría posterior corrigió. Se preservaron todas las imágenes referenciadas: dos en el capítulo 3, trece en el 5 y cuatro en el 6. Se revisaron los epígrafes cuando atribuían una causa no demostrada.

## Cambios físicos centrales

### Capítulo 3

1. Se fija la convención: radio en el plano de la lluvia; `A1 > 0` temprano, `A1 < 0` tardío.
2. La supervivencia pasiva favorece temprano para una misma población producida. Esto no demuestra que domine el UMD.
3. El término de Bertou–Billoir para flujo radial saliente es positivo. Un momento longitudinal pequeño no cambia su signo. Se distingue esta proyección del efecto de distribución angular.
4. La región tardía requiere menor ángulo de emisión, lo que puede favorecerla, pero también sufre más dilución espacial. No se presupone cuál gana.
5. Se muestra el cambio de variables desde el espectro transversal de Cazón, con sus supuestos. No se añaden barridos ni magnitudes de modelos ilustrativos.
6. Se distingue apertura de placa, apertura del tanque, conteo y señal. La compensación ideal entre apertura y longitud de traza no es una cancelación de la asimetría incidente.
7. Se introduce la identidad del promedio condicionado por selección. No se presenta como un proceso atmosférico adicional.

### Capítulo 5

Se conservan los resultados y figuras del Anillo Denso, incluido su remuestreo empírico exitoso. Éste se interpreta como una prueba descriptiva de transferencia MC–REC, no como validación independiente del origen físico de sus residuos.

Se eliminan la identificación `A1 positivo = atenuación dominante`, la acumulación tardía obligatoria de muones blandos y la afirmación de que el conteo UMD sea forzado para compensar una LDF. La degeneración entre asimetría y núcleo se mantiene como posibilidad, no como cadena causal ya demostrada.

La relación con energía y masa queda como hipótesis de producción/transporte. Se corrige `sin(theta)` por `tan(theta)` a radio fijo en el plano de la lluvia, pero la fórmula resultante se identifica como **sólo dilución**, no como la asimetría muónica completa. Se distingue el máximo de producción muónica del máximo electromagnético. No se reutiliza la estimación anterior basada en una tasa de elongación como validación cuantitativa.

**Corrección adicional que requiere atención del autor:** en `Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py`, la función `get_a1` devuelve la incertidumbre de la covarianza del ajuste; `df_res['Err']` almacena esa incertidumbre y el bloque que genera `Mass_Discrimination_MF.pdf` la usa en el denominador. Por tanto, el MF graficado no utiliza dispersión intrínseca de A1 por lluvia. Se mantiene el valor reportado, pero se describe separación entre estimaciones de muestras, no clasificación evento a evento. Este cambio es independiente de la explicación de la inversión; no implica que desaparezca la sensibilidad de las medias a la composición. Revisar la procedencia exacta de la figura final si fue generada con otro código.

### Capítulo 6

Se sustituye la explicación determinista por muones blandos por dos niveles claramente distintos:

- **Resultado de MC:** en el control de veinte archivos, aplicar presencia de estación SD reconstruida cambia el signo del conteo medio a grandes radios.
- **Hipótesis física:** una contribución EM temprana mayor puede ayudar a retener tanques poco muónicos; la retención tardía puede enriquecer la muestra en tanques con más muones. No se ha aislado cada etapa del disparo/reconstrucción ni demostrado que la ayuda EM sea la única causa.

El resultado previo a selección corresponde a estaciones simuladas disponibles en eventos ADST escritos, después de regeneración; no es toda la población CORSIKA ni todos los eventos generados. Tampoco se extrapola ese control a la señal VEM, otros rangos, otros primarios o el Anillo Denso.

El UMD conserva distintas ponderaciones de energía, dirección, apertura y correlación con el disparo SD. No se declara que el suelo elimine toda geometría. La falta de resúmenes UMD previos a selección se mantiene como límite: un registro ausente no se reemplaza por cero sin demostrar que sea un cero físico.

Las notas inconclusas del final del capítulo original se convierten en comentarios `PENDIENTES EDITORIALES` y una discusión del método necesario. No se inventaron análisis de composición, energía ni transferencias MC–REC aún no completados.

## Evidencia y procedencia

La base física y la auditoría de código están en [el informe completo](../01_fisica/report.md) y [la explicación conceptual](../01_fisica/physics_explanation.md), también disponible en [HTML](../01_fisica/physics_explanation.html). Esos documentos distinguen resultados, inferencias de modelos e hipótesis e incluyen las referencias externas y los límites del cotejo con Offline.

Los números **nuevos** del capítulo 6 proceden de:

- `../04_soporte/tablas/selection_closure_fits.csv`: coeficientes del control final de veinte archivos y cantidad de estaciones.
- `../04_soporte/tablas/selection_paired_bootstrap.csv`: intervalos pareados por grupos de lluvia.
- `../04_soporte/codigo/selection_closure.py`: cálculo reproducible de esos resultados desde las extracciones ya guardadas.
- `../04_soporte/tablas/selection_match_summary.json`: emparejamiento exacto con parquet.
- `../04_soporte/tablas/umd_selection_check.json` y `report.md`, sección 2.3: alcance del piloto UMD y por qué no proporciona el control equivalente.

**No confundir** los archivos finales `selection_closure_*` con los resultados anteriores de un solo archivo `adst_selection_*`. Tampoco equiparar los intervalos anchos del control con el punto nominal de las notas GAP.

Se conservaron las cifras ya presentes en el capítulo 5 para describir sus figuras; esta edición no repitió sus ajustes ni certifica todos sus errores estadísticos. Las diferencias de geometría y población se explicitan en lugar de sustituirlas por nuevas predicciones numéricas. No se necesitan claves bibliográficas nuevas: todos los `\cite` de los borradores existen en la bibliografía actual. Los resultados propios de la auditoría se documentan aquí con su procedencia reproducible.

## Verificación y uso

Desde la raíz del repositorio:

```bash
venv/bin/python claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/prepare_and_check.py
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=claude_work/revision_asimetrias_sd_umd/03_borradores_tesis claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/preview.tex
biber --input-directory=claude_work/revision_asimetrias_sd_umd/03_borradores_tesis --output-directory=claude_work/revision_asimetrias_sd_umd/03_borradores_tesis preview
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=claude_work/revision_asimetrias_sd_umd/03_borradores_tesis claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/preview.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=claude_work/revision_asimetrias_sd_umd/03_borradores_tesis claude_work/revision_asimetrias_sd_umd/03_borradores_tesis/preview.tex
```

El script genera sólo la envoltura de compilación, los diffs y verificaciones dentro de esta carpeta; no regenera ni sobrescribe los tres borradores. Comprueba imágenes, entornos LaTeX, etiquetas y citas en el documento compuesto, y compara las cifras nuevas con los CSV finales. `validation.json` guarda los resultados y hashes. `protected_sources_sha256.json` permite verificar que los fuentes protegidos no cambian entre verificaciones; si cambian por trabajo del autor, el script se detiene en lugar de reemplazar silenciosamente la instantánea.

Los comentarios de cabecera apuntan a `preview.tex`, una envoltura generada que utiliza rutas absolutas locales. Al trasladar la carpeta a otra máquina hay que ejecutar el script nuevamente, teniendo disponible el árbol de tesis y los resultados de auditoría. Los capítulos propiamente dichos conservan las rutas relativas de figuras originales y son las propuestas a revisar; **no hay un paso de instalación automática en la tesis**.

## Decisiones pendientes del autor

- Aprobar la incorporación del control de selección SD como resultado nuevo y revisar su alcance con los directores.
- Confirmar que el procedimiento y las figuras finales del capítulo 5 corresponden a los scripts inspeccionados, especialmente el MF.
- Decidir cuánto detalle de la auditoría queda en el cuerpo del capítulo 6 y cuánto se traslada a un anexo.
- Completar las comparaciones Infill todavía pendientes y validar incertidumbres correlacionadas antes de una afirmación de significancia o clasificación de masa.

No se modificaron ni ejecutaron los notebooks. No se prepararon commits ni se ejecutaron `git add`, `commit` o `push`.
