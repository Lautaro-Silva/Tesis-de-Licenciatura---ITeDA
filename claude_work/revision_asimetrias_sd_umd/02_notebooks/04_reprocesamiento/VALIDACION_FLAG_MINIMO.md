# Validación de la copia mínima de v8-2

**Ocho pruebas artificiales pasadas; ningún ADST real procesado.**
El notebook está sin ejecutar. Las pruebas extraen únicamente las funciones
mediante AST y les proporcionan objetos Python artificiales: no importan ROOT,
no cargan Offline y no ejecutan las celdas de tandas.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python claude_work/revision_asimetrias_sd_umd/02_notebooks/04_reprocesamiento/test_flag_minimo_sin_root.py
```

Comprobaciones:

1. Filtrar `has_sd_rec=True` reproduce exactamente los valores de todas las
   columnas originales sobre los mismos eventos artificiales. Sólo se permite
   diferencia de dtype por la introducción de valores ausentes; no tolerancia numérica.
2. Sin estación SD REC se conservan el shower global, geometría Infill y conteos
   disponibles; los getters propios de esa estación quedan ausentes.
3. Si todas las estaciones elegibles tienen HasStation, se recupera todo el
   dataset original sin filas añadidas.
4. Anillo con REC reproduce los valores originales; sin REC conserva conteos
   pero no inventa coordenadas de anillo.
5. No se amplía el universo a estaciones SD sin counter UMD; los demás requisitos
   de disponibilidad del lector original permanecen.
6. Un puntero simCounter C++ falso distinto de None se descarta sin desreferenciarlo.
7. La ida/vuelta parquet sintética conserva el flag booleano y los valores ausentes.
8. Hay exactamente tres funciones: las originales. `getModuleList` es idéntica
   en AST; el wrapper también, salvo el nombre del lector que llama.

Los archivos artificiales se crean temporalmente bajo `/tmp`. La ruta ficticia
con extensión `.root` está vacía; sirve sólo para el `os.path.exists` original.

La versión simple conserva deliberadamente limitaciones históricas: la suma de
canales UMD no certifica información completa; el parser de metadatos puede fallar
con modelos que contienen `_`; el wrapper informa errores por archivo sin un
manifiesto global. No se ocultan esas limitaciones ni se modifica su física.

**Pendiente para el autor:** correr un archivo real y cotejar el subconjunto True
con su parquet anterior, usando la celda de comparación incluida. Las pruebas
artificiales no prueban compatibilidad PyROOT ni igualdad sobre la producción real.

La revisión deja intactos el lector original, la primera propuesta auditada,
Offline y los datos de producción. No se crearon nuevos parquet de producción.
