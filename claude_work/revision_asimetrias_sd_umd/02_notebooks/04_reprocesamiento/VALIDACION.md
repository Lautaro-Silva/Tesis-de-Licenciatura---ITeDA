# Validación del lector de dos rutas

**Estado: plantilla preparada, no ejecutada sobre ROOT/ADST reales.**
No se releyó ni reprocesó la producción icrc2025-test7. No se importó ROOT en
las pruebas; se inyectó una API artificial escrita en Python. No se modificaron
Offline, sus configuraciones, el lector original ni los parquet del autor.

## Pruebas reproducibles

Desde la raíz del repositorio:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/02_notebooks/04_reprocesamiento/test_dos_rutas_sin_root.py
```

Resultado de la ejecución de desarrollo: **13 pruebas pasadas**.

- A coincide con todas las columnas históricas emitidas por la función original
  `readADST_surface_v17` en el caso artificial construido. Se ejecutan sus
  definiciones originales, extraídas con AST, no el módulo completo ni sus tandas.
- A es exactamente el subconjunto de B con `has_sd_rec=True`.
- Si todas las estaciones elegibles tienen SD REC, A=B.
- Las estaciones SD sin counter UMD aparecen sólo en el inventario, no como
  módulos inventados de B. Se comprueban también simCounter y geometría ausentes.
- Una suma UMD nula con resúmenes completos se distingue de suma histórica nula
  por ausencia de canales/resúmenes. Un resumen parcial tampoco se acepta completo.
- Un puntero simCounter falso pero distinto de `None` no se desreferencia.
- La ausencia de geometría de anillo sin REC no se sustituye por coordenadas inventadas.
- Las rutas vacías mantienen sus columnas; una muestra sin counters no fabrica UMD.
- El límite de eventos es común a las rutas. Una lectura prematuramente fallida
  no se acepta como terminación normal.
- El cotejo detecta valores y filas diferentes; distingue referencia de piloto
  y referencia de archivo completo, incluyendo eventos presentes sólo en ésta.
- Un fallo de referencia impide el marcador global de tanda completa y conserva
  el informe de diferencias para inspección.
- Los metadatos admiten un nombre de modelo con guion bajo.
- La escritura/lectura parquet artificial funciona; se rechaza reutilizar una
  carpeta de tanda y se detecta una modificación posterior de un parquet mediante hash.

Los archivos de prueba son temporales, bajo `/tmp`. Un nombre terminado en `.root`
en estas pruebas es una ruta ficticia vacía que recibe la API artificial: **no
contiene ni lee datos ROOT**. Los únicos parquet escritos por estas pruebas son
los sintéticos temporales.

## Comprobaciones documentales

El notebook se genera con Jupytext y el HTML se exporta con nbconvert **sin
`--execute`**. El validador general de la entrega comprueba sincronización con
el `.py`, sintaxis, enlaces, celdas sin ejecutar/sin salidas y ambos interruptores
`RUN_PROCESSING=False`, `RUN_COMPARISON=False` en esta plantilla. Los otros tres
notebooks de análisis conservan su condición de entregas ejecutadas.

## Lo que estas pruebas no demuestran

No verifican los bindings C++/PyROOT, compatibilidad de esquemas ADST, cobertura
real de counters, integridad de verdad UMD ni coincidencia real con el parquet
antiguo. Tampoco miden tiempo/RAM de producción ni una nueva asimetría.

La validación física comienza con el piloto ejecutado por el autor: coincidencia
externa de A, tabla de cobertura y estudio explícito de información UMD ausente.
Un resultado sintético correcto no reemplaza esos controles.
