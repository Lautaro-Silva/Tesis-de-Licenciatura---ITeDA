# Reprocesamiento ADST — abrir la versión simple

**Versión recomendada según tu última indicación:**
[Procesamiento_ADST_v8-2_flag.ipynb](Procesamiento_ADST_v8-2_flag.ipynb)
· [HTML](Procesamiento_ADST_v8-2_flag.html).

Es una copia del lector v8-2 con cambios marcados inline: se retira el skip de
`HasStation`, se guarda `has_sd_rec` y se protegen los getters de la estación REC
ausente. Conserva las tres funciones originales, sin auxiliares nuevos, ni
manifiestos, ni interruptores para agentes. Produce **un solo dataset**, con las
columnas anteriores y únicamente ese flag adicional. Para comparar:

```python
df_sin_corte = df.copy()                       # Todas las filas: True y False.
df_con_corte = df.loc[df["has_sd_rec"]].copy() # Requisito original.
```

La lectura del shower global y la geometría Infill quedan iguales; señal/error/
saturación/azimut nativo de la estación ausente quedan vacíos. En anillo también
faltan las coordenadas obtenidas de esa estación. Se mantiene el requisito de
counter/módulos UMD, simCounter y geometría recuperable. La suma UMD histórica no
se redefine: sus ceros con resúmenes ausentes no se certifican como ceros físicos.

**No se ejecutó sobre ROOT.** Abrilo en tu entorno Offline; revisá entrada y salida
nueva y ejecutá un archivo primero. La celda de procesamiento se ejecuta normalmente
cuando vos la corrés: no hacer Run All sin revisar el costo. Para toda la tanda,
cambiá `root_files_a_procesar = all_root_files[:1]` por `all_root_files`.
Las otras producciones se seleccionan cambiando las rutas, como antes.
Incluye celdas de lectura, selección por flag y un cotejo directo con el parquet viejo.

Ver [validación de la versión simple](VALIDACION_FLAG_MINIMO.md).
El lector original y la versión anterior se preservan sin sobrescribirlos.

---

## Versión anterior: dos rutas y auditoría ampliada (conservada, no recomendada como punto de partida)

Abrí [Procesamiento_ADST_dos_rutas.ipynb](Procesamiento_ADST_dos_rutas.ipynb).
Para leerlo sin Jupyter: [HTML](Procesamiento_ADST_dos_rutas.html).
Es un cuaderno completo, muy comentado en español, derivado de
`Scripts/Procesamiento_ADST_v8-2.py` y su función `readADST_surface_v17`.
**Está preparado para que lo ejecutes vos: no se reprocesó ningún ROOT.**

## Qué comparación permite

| Producto | De dónde salen las filas | Requisito SD reconstruido |
|---|---|---|
| A_con_HasStation | Counters y módulos UMD que recorre v17 | Exige `HasStation` |
| B_sin_HasStation | Mismo universo inicial y mismos requisitos comunes que A | No exige `HasStation` |
| inventario_SD | Estaciones SD simuladas guardadas, tengan o no counter UMD | Se registra, no se corta |

Las dos rutas se extraen en una sola pasada: **A es exactamente B filtrado por
`has_sd_rec`**. Además se compara A, fila por fila, con tu parquet original.
La primera igualdad es una garantía de diseño; la segunda es una prueba externa
que tiene que pasar con tus archivos reales.

Esto **no es simplemente renombrar la extracción diagnóstica anterior**: aquella
partía del vector de estaciones SD simuladas. Aquí se parte de los mismos counters
UMD del lector original. El inventario SD queda separado precisamente para detectar
la diferencia entre esos universos, no para ocultarla.

## Qué permanece y qué cambia respecto de v8-2

| Se conserva | Se cambia explícitamente |
|---|---|
| Recorrido de counters UMD → módulos 0–5 → canales | Extracción común seguida de dos rutas, en lugar de descartar pronto con `HasStation` |
| Necesidad de simCounter y geometría Infill recuperable | Se registran los counters perdidos y el motivo; comprobación robusta del puntero nulo |
| Getters de conteos, señales y estados; columnas históricas | Si no hay SD REC, señales/errores REC ausentes, no cero; columnas adicionales de disponibilidad |
| Rotaciones, fallback de IDs y convenciones geométricas históricas | Se marca geometría verdadera no disponible; no se inventa para anillo sin SD REC |
| Suma histórica de `nMuones_MC`, para reproducir el parquet | Se añade `nMuones_MC_available`: NaN si el resumen de canales enumerados está incompleto |
| Metadatos de modelo, energía, primario y run | Parser compatible con nombres de modelo que contienen guion bajo |
| Un parquet por archivo y ruta | Escritura exclusiva, manifiestos y comprobaciones; ejecución serial, sin Pool |

Por eso no afirmo que sea un archivo literalmente idéntico con una línea borrada.
Hay adaptaciones necesarias para acceder a MC sin desreferenciar una estación REC
ausente, y controles adicionales. La coincidencia externa con tu parquet es la
forma de verificar que A conserva el resultado del procesamiento previo.

No se imponen cortes físicos por ángulo, radio, energía, saturación o señal.
No se cambian las convenciones geométricas a la vez que la selección.
Las marcas de disponibilidad no eliminan filas automáticamente.

## Cómo correrlo vos

1. Abrirlo en un kernel con PyROOT/Offline compatible con tus ADST y con pandas,
   numpy y pyarrow. El cuaderno no instala nada ni modifica configuraciones.
2. Revisar la celda **Configurar tandas**: entrada ROOT, biblioteca y parquet de
   referencia. Inicialmente sólo está activo SIBYLL/protón de la tanda indicada.
3. Mantener `MAX_FILES=1`, `MAX_EVENTS=50` y elegir un `RUN_LABEL` nuevo.
   Guardar/sincronizar el `.py` antes de ejecutar, para que la huella de código
   corresponda a la versión guardada. Habilitar `RUN_PROCESSING=True`.
4. Exigir `referencia: pass` y revisar la cobertura con `RUN_COMPARISON=True`.
   Si A difiere del parquet, el procesamiento falla de forma explícita: no
   interpretar todavía una diferencia física entre A y B.
5. Con otra etiqueta, usar `MAX_EVENTS=None` para probar un archivo completo y
   medir tiempo/memoria. El lector mantiene un archivo a la vez en memoria.
6. Recién después poner **`MAX_FILES=None` y `MAX_EVENTS=None`** para leer todos
   los archivos/eventos de las tandas seleccionadas. Agregar las otras tandas en
   `DATASETS`, o usar `discover_datasets` y completar sus referencias antiguas.

`legacy=None` permite una tanda sin parquet de referencia, pero queda registrada
como **sin cotejo externo**, no como reproducción verificada de v17.
El límite del piloto se aplica por igual a A y B. En el piloto se cotejan sólo
los eventos leídos; en una lectura completa se coteja toda la referencia.

El procesamiento es serial (`N_WORKERS=1`). No hay estimación de horas de servidor:
no ejecuté la producción para medirla. No hay reanudación ni sobrescritura automática;
si falla una tanda, se preserva para inspección y se usa otra etiqueta para repetir.

## Dónde quedan tus datos nuevos

Todo se escribe bajo `datos_generados/<RUN_LABEL>/<producción>/`, dentro de esta
carpeta e ignorado por Git. Los ROOT y parquet anteriores son sólo de lectura.

```text
datos_generados/<RUN_LABEL>/
├── CONFIG.json                    Procedencia, biblioteca, límites y archivos
├── RUN_COMPLETE.json              Sólo si termina la tanda seleccionada
├── RUN_FAILED.json                Si falla durante el procesamiento
└── <producción>/
    ├── A_con_HasStation/           Parquet por archivo, filas por módulo
    ├── B_sin_HasStation/           Parquet por archivo, filas por módulo
    ├── auditoria_counters/        Counters considerados y motivos de pérdida
    ├── inventario_SD/             Inventario SD separado, filas por estación
    ├── eventos_leidos/            Incluso eventos que no emiten filas UMD
    ├── comparacion_legacy/        Diferencias de A contra el parquet anterior
    └── manifiestos/               Conteos, disponibilidad de referencia y hashes
```

**Completo significa que terminó la selección de archivos/eventos configurada:**
un piloto completo sigue siendo un piloto. Si falla un cotejo, no se crea el
marcador global de éxito. Los JSON documentan procedencia; no hace falta leerlos
a mano para el flujo normal: el cuaderno ofrece un cargador y tabla de cobertura.

## Antes de graficar

Usá la última sección para cargar una tanda concreta. No leas recursivamente toda
`datos_generados/`, porque mezclarías rutas, inventarios y pilotos.

- `df_A`, `df_B`: filas por módulo, compatibles con el universo del lector viejo.
- `sd_A`, `sd_B`: esas mismas rutas reducidas a una fila por estación/evento.
- `coverage_summary(tables)`: revela cuánto amplía B y qué parte del inventario SD
  no tiene ninguna fila UMD. El inventario no entra automáticamente al ajuste A/B.

Para SD, deduplicar en ambas rutas evita ponderar una estación por su número de
módulos. Para reproducir literalmente el gráfico viejo por módulo, mantener esa
ponderación en ambas rutas y explicitarla; son estimandos diferentes.

No aplicar a B un `dropna()` global o un corte en señal REC: recuperaría parte
de la selección retirada. Para asimetrías Infill se mantienen `r_core_MC` y
`phi_plane_euler_MC_true_core` en radianes, deshaciendo el +π histórico como en tu
script. **A₁ positivo = exceso temprano; negativo = exceso tardío.**

Si B=A, no significa que HasStation nunca sesgue la muestra SD: puede indicar que
los objetos UMD ya restringen ese universo. Si B incorpora filas sin resúmenes
UMD completos, tampoco significa que hayas recuperado el conteo UMD físico sin
selección. Ausencia de información no equivale a cero muones.

## Qué está validado en esta entrega

Las pruebas artificiales comparan también las funciones originales de tu lector
con el nuevo lector sobre los mismos objetos simulados en Python. Ver
[VALIDACION.md](VALIDACION.md). **No prueban el enlace C++/PyROOT ni la coincidencia
real con tus parquet**: eso queda deliberadamente para tu piloto.
No hay aquí un nuevo A₁ medido ni una conclusión forzada sobre la inversión.

Para editar: modificar el `.py` y sincronizar con Jupytext, como en los otros
cuadernos del repositorio. No editar el JSON del `.ipynb` manualmente.
