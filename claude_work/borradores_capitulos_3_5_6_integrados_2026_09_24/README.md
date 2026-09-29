# Borradores integrados: capítulos 3, 5 y 6

Versión de trabajo del 24 de septiembre de 2026, para revisión del autor y sus directores.

**Empezar por [la vista previa en PDF](compilacion/vista_previa.pdf).** Contiene los tres capítulos, con su numeración original, las figuras existentes y la bibliografía. No reemplaza ni modifica la tesis.

## Archivos de lectura

| Capítulo | Texto propuesto | Cambios y procedencia |
|---|---|---|
| 3. Fenomenología | [03_fenomenologia_DRAFT.tex](03_fenomenologia_DRAFT.tex) | [03_NOTAS.md](03_NOTAS.md) |
| 5. Anillo Denso | [05_anillo_denso_DRAFT.tex](05_anillo_denso_DRAFT.tex) | [05_NOTAS.md](05_NOTAS.md) |
| 6. Infill y selección | [06_infill_DRAFT.tex](06_infill_DRAFT.tex) | [06_NOTAS.md](06_NOTAS.md) |

Un subagente redactó cada capítulo. La revisión integradora comprobó signos, ecuaciones, referencias cruzadas, alcance de los resultados y consistencia con RAFA. Las trece figuras originales del capítulo 5 se conservan. El capítulo 6 agrega el control SD antes/después sin volver a copiar la figura del núcleo ya incluida en el capítulo 5. Las imágenes se enlazan a sus originales: no se regeneraron ni alteraron.

## El hilo físico que queda

1. **Los mecanismos originales siguen siendo válidos:** pérdidas pasivas, proyección del flujo y competencia entre distribución angular y dilución espacial. Se desarrolla la geometría con radio en el plano de la lluvia, la distribución angular derivada de un espectro transversal, el cruce a momento fijo y el promedio espectral correcto. No se presenta la aproximación como una predicción cuantitativa validada de ambos detectores.
2. **El tanque no agrega el exceso tardío invocado anteriormente.** La identidad área proyectada × cuerda media = volumen cancela esa dependencia geométrica de la señal ideal de muones pasantes, dirección por dirección. No cancela el flujo incidente, no se aplica al conteo sin ponderación y no elimina selección o umbrales.
3. **La inversión SD de la muestra auditada aparece al condicionar por `HasStation`.** Esto se demuestra con los mismos conteos MC y coordenadas, incluyendo ahora las estaciones simuladas antes ausentes. No demuestra que Offline funcione mal ni que todo flujo al suelo invierta su signo.
4. **La interpretación del mecanismo de selección tiene un límite:** ayuda electromagnética temprana y enriquecimiento muónico de las estaciones tardías retenidas explican plausiblemente el signo; no se ha aislado una etapa electrónica como causa única. La población UMD anterior a la selección no se recupera rellenando ausencias con cero.
5. **El sesgo del núcleo es otro problema.** Se conserva el resultado geométrico mostrado en RAFA, separado del remuestreo de residuos de conteo y de la selección de estaciones.

## Qué cambia respecto de RAFA y de los borradores antiguos

La charla presentó el control `HasStation` como una hipótesis en verificación. Aquí se actualiza a resultado comprobado **en los veinte archivos SIBYLL-protón y los intervalos declarados**, manteniendo como hipótesis la explicación detallada del disparo. No se extrapola el control automáticamente al Anillo Denso, a otros modelos ni a datos reales.

Se retira la afirmación de que un coeficiente negativo exige siempre un mecanismo distinto de la divergencia: el término angular puede superar la dilución bajo condiciones apropiadas. Lo que no estaba justificado era atribuir el resultado seleccionado concreto a una población blanda sin verificar los pesos y la selección.

También se precisa una cuestión importante del capítulo 5: el código del gráfico **MF ≈ 2.5** usa errores de amplitudes ajustadas a muestras, no anchos de una distribución de amplitudes por lluvia. Se conserva el resultado como separación entre estimaciones de muestras; no como capacidad demostrada de clasificación evento a evento.

Los documentos históricos de `gap_notes_asimetrias_review_v4/` contienen inferencias posteriormente corregidas. En particular, no se conserva el promedio de cocientes temprano/tardío con un espectro sin los pesos de llegada, ni la inferencia de flujo no seleccionado negativo a partir del conteo seleccionado. El resultado reproducible del espectro corregido no valida la extrapolación de una potencia a bajas energías ni la identificación de energías de producción y suelo.

La comprobación directa del documento de Armbruster separa el `+2` de dilución de la apertura de placa. La ecuación de señal de ese trabajo ya utiliza la compensación apertura–cuerda; no contiene un `+1` adicional de placa. El capítulo 3 evita ambos modos de doble conteo.

## Verificación numérica incorporada

[verificar_seleccion.py](verificar_seleccion.py) compara los parquet v13 existentes con v11 y con las tablas detrás del PDF de control. Se ejecutó en un proceso, sin ROOT ni reprocesamiento. Resultado guardado en [verificacion_seleccion.json](verificacion_seleccion.json):

- Veinte pares de archivos; **1 589 487** filas seleccionadas de módulos preservadas, con igualdad exacta de todas las columnas originales (permitiendo cambios de dtype).
- **106 280 = 51 031 + 55 249** registros SD en la ventana `[30,40)` grados, `[150,1800)` m, antes/con/sin la condición correspondiente.
- Los **32 ajustes** muónicos y electromagnéticos antes/después reproducen estimaciones, errores formales y tamaños de muestra de la referencia.
- Para `[1200,1350)` m, SD antes **+0.0689**, SD seleccionado **−0.1240**, UMD seleccionado **+0.0816**; positivo significa exceso temprano.

La tabla del capítulo 6 usa las incertidumbres del bootstrap pareado previo de 1200 réplicas y 960 grupos de lluvia, identificadas por separado de los errores formales del PDF. **Ese bootstrap no se volvió a ejecutar en esta sesión.** La validación nueva vuelve a calcular los ajustes centrales y formales, no una nueva estimación de sistemáticos. Las cifras antiguas del Anillo Denso se conservan como resultados de sus figuras y scripts originales, sin ejecutar nuevamente aquel análisis.

Para reproducir la comprobación desde la raíz del repositorio:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python \
  claude_work/borradores_capitulos_3_5_6_integrados_2026_09_24/verificar_seleccion.py
```

Requiere los parquet locales v11/v13; no ejecuta el lector ADST. El directorio `claude_work/reprocesamiento_sd_completo/` mencionado en la revisión anterior no está presente en este checkout; sus datos v13 sí permanecen accesibles. Por ello la validación independiente de este directorio es la evidencia reproducible de preservación utilizada aquí. Antes de publicación conviene archivar el lector exacto y su entorno.

## Compilar y eventualmente integrar

```bash
bash claude_work/borradores_capitulos_3_5_6_integrados_2026_09_24/compilar.sh
```

La compilación escribe sólo en `compilacion/`. Los tres fragmentos están preparados para el estilo `article` de la tesis. `vista_previa.tex` resuelve las imágenes desde la raíz y desde `Tesis - Latex/`, conservando su ubicación actual. Las referencias a los anexos enlazan notas de esta vista previa: los anexos no se reproducen ni se reescriben.

Si el autor acepta los borradores, debe decidir su incorporación. Será necesario añadir la entrada de [bibliografia_adicional.bib](bibliografia_adicional.bib) y resolver la nueva figura del control SD desde la ubicación definitiva. Armbruster es una tesis de junio de **2018**, circulada como GAP-2020-066; el número de la nota no es el año de la tesis.

Quedan coordinaciones fuera del encargo: el anexo original justifica de forma demasiado fuerte los chi cuadrados elevados y deberá armonizarse con el nuevo capítulo 5; las conclusiones, el resumen y las afirmaciones de discriminación deberán conservar los mismos límites. No se redactaron resultados nuevos para secciones aún pendientes ni se trasladó la señal preliminar de datos reales a estos capítulos de simulación.

## Seguridad y alcance

Trabajo en la rama `codex/borradores-fisica-seleccion-20260924`. No se modificaron `Tesis - Latex/`, `GAP_Notes_Latex/`, la presentación, los lectores existentes, Offline ni configuraciones institucionales. No se ejecutaron nuevas simulaciones, producción ROOT, `git add`, commit o push.
