# El gráfico solicitado, reproducido y cotejado

Abrí [reproducir_desglose_sd.ipynb](reproducir_desglose_sd.ipynb), o su [HTML ejecutado](reproducir_desglose_sd.html).

- [Reproducción del PDF original](resultados/SD_Desglose_Componentes_vs_UMD_reproducido.pdf): cuatro curvas, mismos bins de 150 m, conversión de phi, filas por módulo y ajuste ponderado por SEM que la celda de `Scripts/plots_seccion_6.py`.
- [Comparación adicional antes/después SD](resultados/SD_antes_despues_mismos_bins.pdf): misma banda cenital, bins radiales y ajuste ponderado; aquí se usa una fila por estación SD/evento y se declara esa diferencia.
- [Resultado de las verificaciones](RESULTADO.md): coincidencia numérica con los puntos y barras del PDF original, e integridad de fuentes registrados.

El PDF original se lee desde `Scripts/SD_Desglose_Componentes_vs_UMD.pdf`, no desde una versión potencialmente distinta guardada en la tesis. No se sobrescribe.

## Confirmación sobre Offline y configuraciones del instituto

En el trabajo realizado no se editaron fuentes, librerías, configuraciones de producción ni otros archivos del instituto fuera del repositorio. Se inspeccionaron fuentes/configuraciones y se abrieron archivos ADST existentes para lectura. No se recompiló Offline ni se reescribieron archivos ROOT.

Las variables `PYTHONPATH` y `LD_LIBRARY_PATH` usadas en el lector ROOT afectaban solamente al proceso lanzado. No se modificaron archivos de configuración persistentes, scripts de inicialización ni la instalación de Auger. Tampoco se aplicaron las modificaciones de versiones de clase sugeridas por los avisos de ROOT: esas advertencias se documentaron, no se ejecutaron como instrucciones.

El notebook compara el contenido actual de los trece fuentes relevantes de Offline contra las huellas registradas durante la auditoría. Ese cotejo aporta evidencia sobre esos archivos y ese intervalo temporal; no se presenta como una auditoría universal de todo el servidor ni como garantía de lo que puedan modificar otras personas. La tabla legible está en `integridad_fuentes_offline.csv` y su resumen en `RESULTADO.md`.

En esta reproducción no se ejecuta ROOT en absoluto. Se leen los parquet originales y la extracción previa por estación. El código original de gráficos, el PDF aportado y los insumos se mantienen intactos.

## Qué se conserva y qué no se debe confundir

La reproducción literal mantiene las copias de conteos SD en las filas de módulos UMD porque eso es lo que hace la celda recibida. También mantiene los errores formales del ajuste. Reproducir esos errores no equivale a afirmar que incluyan correlaciones entre módulos, estaciones o reutilizaciones de lluvias.

La auditoría anterior usaba bandas más anchas y ajuste no ponderado. No se sustituyen sus coeficientes en este gráfico. Se recalculan todos los valores con la receta solicitada.

Para el antes/después de selección se deduplica SD. Se comprueba que `HasStation=True` reproduce el parquet deduplicado. No se construyen curvas de UMD ni señal VEM previas a selección: no se dispone de esos observables equivalentes para las estaciones descartadas.

## Cómo se coteja el PDF

Se extraen las curvas vectoriales y barras de error del PDF de referencia. La escala vertical se obtiene de sus etiquetas y grilla, sin calibrarla contra los valores recalculados. Se comparan los 32 puntos y 32 errores y se informa la diferencia máxima, limitada por el redondeo del PDF.

Los datos recalculados están en `ajustes_reproducidos.csv`; el cotejo en `comparacion_numerica_con_PDF.csv`. Ambos se muestran como tablas dentro del notebook, no hace falta leer los CSV para seguir el resultado.

## Ejecutar

Usá el kernel del venv y Run All, o desde la raíz del repositorio:

```bash
venv/bin/jupytext --sync claude_work/revision_asimetrias_sd_umd/02_notebooks/02_reproduccion/reproducir_desglose_sd.py
venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 claude_work/revision_asimetrias_sd_umd/02_notebooks/02_reproduccion/reproducir_desglose_sd.ipynb
venv/bin/jupyter nbconvert --to html --embed-images claude_work/revision_asimetrias_sd_umd/02_notebooks/02_reproduccion/reproducir_desglose_sd.ipynb
```

El `.py` documentado es la fuente emparejada; no se edita manualmente el JSON del notebook. Todo el cómputo numérico se limita a un hilo. Reejecutar sólo reemplaza salidas generadas en esta carpeta. No se ejecutó `git add`, `commit` ni `push`.
