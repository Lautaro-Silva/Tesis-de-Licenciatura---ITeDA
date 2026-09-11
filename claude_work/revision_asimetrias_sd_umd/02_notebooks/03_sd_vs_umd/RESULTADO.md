# ¿Coincide el SD antes del requisito de reconstrucción con el UMD?

Comparación directa con la curva UMD original, no con un UMD libre de selección.

A1 positivo = exceso temprano. Delta = SD antes − UMD.

| r [m] | UMD original | SD antes | SD después | Delta | IC puntual 95% de Delta |
|---|---:|---:|---:|---:|---:|
| 150–300 | +0.0620 | +0.0331 | +0.0331 | -0.0288 | [-0.0410, -0.0164] |
| 300–450 | +0.0933 | +0.0602 | +0.0602 | -0.0331 | [-0.0474, -0.0196] |
| 450–600 | +0.0853 | +0.0588 | +0.0588 | -0.0265 | [-0.0427, -0.0091] |
| 600–750 | +0.1147 | +0.0605 | +0.0593 | -0.0543 | [-0.0742, -0.0347] |
| 750–900 | +0.1148 | +0.0576 | +0.0402 | -0.0572 | [-0.0842, -0.0302] |
| 900–1050 | +0.0941 | +0.0660 | -0.0158 | -0.0281 | [-0.0607, +0.0063] |
| 1050–1200 | +0.1057 | +0.0683 | -0.0641 | -0.0374 | [-0.0804, +0.0050] |
| 1200–1350 | +0.0816 | +0.0689 | -0.1240 | -0.0127 | [-0.0897, +0.0555] |

Bootstrap pareado: 960 grupos de lluvia progenitora, 1200 réplicas, semilla 20260911. Se mantienen juntos módulos, estaciones y reutilizaciones.

Bandas cuyo intervalo simultáneo aproximado del 95% excluye Delta=0: 150–300 m, 300–450 m, 450–600 m, 600–750 m, 750–900 m.

La compatibilidad local no prueba igualdad. La comparación global no debe decidirse sólo por el último punto. Las bandas simultáneas están en comparacion_directa.csv.

Retirar HasStation elimina la inversión SD en esta muestra; no hace idénticas las dos curvas. UMD conserva la selección original. Esto no prueba un fallo de Offline ni identifica el origen físico de toda diferencia residual.

## Reproducción y procedencia

- Abrir comparar_sd_umd.ipynb y ejecutar todas las celdas con el venv del repo.
- Código fuente legible: comparar_sd_umd.py (jupytext). HTML: comparar_sd_umd.html.
- SD: ../../04_soporte/tablas/adst_counts_fast.csv, extracción de conteos por estación de los ADST originales; no contiene ajustes prefijados.
- UMD: parquet original de ADST_Alexey_module_v11/parquet_sib_proton_17/.
- Lector ADST documentado: ../01_seleccion/read_original_adst.py.
- Verificado: SD retenido coincide fila a fila con parquet; UMD reproduce la figura original; solución algebraica coincide con curve_fit en las 24 combinaciones.
- Ocho bandas radiales originales, 12 bins phi, ajuste ponderado; SD sin duplicados por módulo. Barras de la nueva figura: bootstrap, no errores formales independientes.
- No se ejecutó ROOT ni se modificó software, configuración o datos externos.

## Límite físico

Antes del requisito HasStation no equivale a ausencia de todo corte: se conservan los eventos guardados y estaciones simuladas disponibles. Falta UMD no seleccionado válido para separar de forma concluyente física del detector y selección residual.
