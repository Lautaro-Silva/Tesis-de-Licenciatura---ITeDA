# Revisión de asimetrías SD–UMD

Ésta es la carpeta única de entrega de esta conversación. Para navegar sin abrir
Jupyter, empezá por [INICIO.html](INICIO.html). No hace falta recorrer los CSV,
JSON ni los scripts de auditoría para entender los resultados.

**Para mostrar al director:** [resumen de una página (PDF)](RESUMEN_PARA_DIRECCION.pdf)
· [HTML](RESUMEN_PARA_DIRECCION.html) · [texto editable (Markdown)](RESUMEN_PARA_DIRECCION.md).
Separa el resultado demostrado, la hipótesis física y lo que sigue abierto.

## Qué abrir según tu pregunta

| Quiero… | Abrir |
|---|---|
| Entender atenuación, geometría, divergencia y qué añadió la revisión | [Explicación física](01_fisica/physics_explanation.html) |
| Entender de dónde salen los datos y qué hace el requisito de reconstrucción | [Notebook 1: selección paso a paso](02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.ipynb) · [HTML](02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.html) |
| Reproducir exactamente mi gráfico de cuatro componentes | [Notebook 2: reproducción](02_notebooks/02_reproduccion/reproducir_desglose_sd.ipynb) · [HTML](02_notebooks/02_reproduccion/reproducir_desglose_sd.html) |
| Ver si el SD sin ese requisito coincide con UMD | [Notebook 3: comparación directa](02_notebooks/03_sd_vs_umd/comparar_sd_umd.ipynb) · [HTML](02_notebooks/03_sd_vs_umd/comparar_sd_umd.html) |
| Reprocesar los ROOT conservando las estaciones SD sin reconstruir | [`reprocesamiento_sd_completo/`](../reprocesamiento_sd_completo/README.md) — versión ejecutada. Reemplaza a `02_notebooks/04_reprocesamiento/`, eliminada el 2026-09-29 (recuperable desde el commit `0a5dd5e`) |
| Revisar propuestas para los capítulos 3, 5 y 6 | [Guía de borradores](03_borradores_tesis/README.md) · [Vista previa PDF](03_borradores_tesis/preview.pdf) |
| Examinar derivaciones, literatura externa y auditoría de Offline | [Informe completo](01_fisica/report.html) · [Markdown](01_fisica/report.md) |

## Conclusión actual y alcance

Retirar el requisito de presencia de estación SD reconstruida elimina la inversión
del conteo SD en la muestra auditada. No demuestra que Offline reconstruya mal:
demuestra que ese requisito cambia la población promediada, incluso al usar
conteos y coordenadas MC.

La comparación más reciente muestra compatibilidad estadística entre el SD antes
de ese requisito y la curva UMD original a grandes radios, pero **no reproduce
toda la curva UMD**. El UMD conserva su selección original. No se dispone de
conteos UMD previos a selección válidos para todas las estaciones descartadas.
No hay que rellenar esa información ausente con ceros físicos.

Los números y sus intervalos están en [el resultado de la comparación directa](02_notebooks/03_sd_vs_umd/RESULTADO.md).
En toda la entrega, A₁ positivo significa exceso temprano; negativo, exceso tardío.

## Organización

```text
revision_asimetrias_sd_umd/
├── README.md + INICIO.html      Punto de entrada; no duplican los análisis
├── 01_fisica/                  Explicación conceptual e informe técnico
├── 02_notebooks/
│   ├── 01_seleccion/            Procedencia, selección y controles
│   ├── 02_reproduccion/         Tu gráfico original, sin cambiar el estimador
│   └── 03_sd_vs_umd/            Comparación directa que faltaba
├── 03_borradores_tesis/         Tres capítulos completos, diffs y preview
├── 04_soporte/
│   ├── codigo/                 Auditoría, verificadores y generadores
│   ├── tablas/                 Insumos ADST y resultados numéricos previos
│   ├── figuras/                Figura del informe técnico
│   ├── plantillas/             Plantilla y estilo del informe
│   ├── referencias/            PDF original para el cotejo numérico
│   └── organizacion/           Inventario y comprobaciones del traslado
```

Cada notebook tiene su `.py` editable, `.ipynb` y `.html` para lectura.
Los tres primeros están ejecutados. La carpeta cuarta contiene el procesamiento
simple recomendado y la versión auditada anterior, ambos **sin ejecutar**, con
pruebas sintéticas de código, no de ROOT real.
Sus figuras y tablas están en `resultados/` (o `exports/` en el recorrido inicial).
Son formatos de un mismo análisis, no tres versiones científicas distintas.

## Qué figura es cuál — no mezclar sus números

| Figura de referencia | Definición | Uso |
|---|---|---|
| [Comparación SD–UMD](02_notebooks/03_sd_vs_umd/resultados/SD_sin_corte_vs_UMD.pdf) | Bins originales de 150 m, ajuste ponderado; errores bootstrap pareados | **La figura principal para la pregunta más reciente** |
| [Cuatro componentes originales](02_notebooks/02_reproduccion/resultados/SD_Desglose_Componentes_vs_UMD_reproducido.pdf) | Filas originales por módulo; mismos SEM y ajuste de `plots_seccion_6.py` | Reproducción literal del gráfico entregado por el autor |
| [SD muones y EM antes/después](02_notebooks/02_reproduccion/resultados/SD_antes_despues_mismos_bins.pdf) | Mismos bins y ajuste ponderado, una fila por SD; errores formales | Control adicional de la reproducción |
| [Evolución inicial de selección](02_notebooks/01_seleccion/exports/05_evolucion_radial.pdf) | Bandas más anchas, ajuste no ponderado y bootstrap | Explicación inicial de cómo se identificó la inversión |

No se eliminaron curvas de distintas definiciones como si fueran duplicados.
Las versiones PDF y PNG son exportaciones complementarias; las imágenes dentro
del notebook/HTML permiten leerlo sin depender de una galería externa.

Los borradores y el informe físico preceden a la comparación directa más reciente.
Se preserva su contenido científico: el control de bandas anchas que citan no debe
reemplazarse silenciosamente por números de otro ajuste.

## Reproducir y editar

Desde la raíz del repositorio, con el `venv` existente:

```bash
venv/bin/jupyter lab
```

Abrí el notebook deseado y ejecutá sus celdas. Los tres recorridos principales
leen tablas existentes; **no lanzan ROOT, Offline ni simulaciones nuevas**.
Necesitan el parquet original en la ruta indicada al comienzo de cada notebook.
La extracción SD ya está guardada una sola vez en `04_soporte/tablas/`.

El notebook 4 es distinto: prepara una nueva lectura de tus ROOT, que ejecutás vos.
La versión simple conserva el lector v8-2 y guarda `has_sd_rec` en UN dataset:
comparás todas sus filas con el subconjunto True. No hay auxiliares nuevos ni
inventario SD en ese lector. La versión auditada anterior queda preservada aparte.
No sustituye silenciosamente los datos de los notebooks anteriores. Seguí su guía
y probá un archivo antes de toda la producción. Ejecutar su celda de procesamiento
inicia una lectura real: está preparada para que la corras vos, no ejecutada aquí.

Para editar, modificá el `.py` y sincronizá con `venv/bin/jupytext --sync ruta/al/cuaderno.py`.
No borres ni ignores el `.ipynb`: conserva las salidas que el autor necesita.
El lector ROOT es opcional y está documentado en el notebook 1; no ejecutarlo para
una simple lectura de resultados. La auditoría antigua queda en soporte, no es
la ruta recomendada para empezar ni un procesamiento automático.

## Conservación y seguridad

Los cinco directorios de esta conversación se trasladaron aquí. No se tocaron
los análisis previos `gap_notes_asimetrias_review_v4`,
`kinematic_divergence_explainer_and_thesis_updates` ni `unified_asymmetry_model_v1`.
Tampoco se modificaron la tesis original, las notas GAP, Offline, datos de
producción ni configuraciones del instituto.

Se conserva un [inventario de origen, destino y huella de contenido](04_soporte/organizacion/inventario_traslado.csv).
La copia local de los originales y los intermedios (`99_archivo_local/`) se eliminó
el 2026-09-29; el inventario conserva origen, destino y huella de cada archivo.
No se eliminó trabajo científico para reducir el número de archivos.

Los cambios ajenos ya presentes en el repositorio quedan fuera de este commit.
La validación de rutas y resultados está en [VALIDACION.md](04_soporte/organizacion/VALIDACION.md).
