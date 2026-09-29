# Auditoría de filas: parquet original vs lector con flag

Diagnóstico serial sobre parquet existentes y el CSV SD ya guardado. No se abrió
ROOT, no se modificó Offline y no se reprocesó la producción. El script que
reproduce este informe es `auditar_perdida_filas.py`, en esta misma carpeta.

## 1. Resultado observado: sí se perdieron filas

Se cotejaron 20 archivos de cada versión, con los mismos nombres.
La clave es archivo/event_id/counterId/moduleId/sdId; no se compara sólo la intersección.

| Cantidad | Filas por módulo |
|---|---:|
| Parquet anterior | 1589487 |
| Nuevo, flag True | 1525740 |
| Nuevo, flag False | 45 |
| Nuevo total | 1525785 |
| Filas anteriores que desaparecieron | 63747 |
| Filas genuinamente añadidas | 45 |

Balance: 1589487 − 63747 + 45 = 1525785.
Eventos representados sólo en el viejo/nuevo: 0/0.
Valores distintos en las columnas antiguas entre filas comunes: ninguno.

Las 63747 filas perdidas tienen 63747 ceros
en nMuones_MC, 62406 ceros y 1341 NaN
en nMuones_REC. Sus estados son {'candidate': 61791, 'rejected': 1956}.
Conservaban SD-MC conocido en 63747 filas, positivo en
52452. Por tanto, perderlas también elimina información SD
válida: no son simplemente filas vacías prescindibles.

## 2. Cambio de código que hay que investigar/corregir

Antes: `if simCounter is None: continue`.
Después: `if simCounter is None or not simCounter: continue`.

Esta segunda condición NO es necesariamente neutra para el número de filas.
MDEvent::GetSimCounter devuelve nullptr si falta la entrada simulada.
El writer guarda counters reconstruidos y simulados con requisitos diferentes.
Un proxy nullptr puede no ser None. Si un módulo no tiene canales enumerados,
el lector antiguo puede guardar su suma inicial cero sin desreferenciarlo; el
nuevo filtro descarta el counter entero, incluido su conteo SD disponible.

Esto es una explicación concreta del fallo, no una demostración fila por fila
del puntero real: los parquet no guardan HasSimCounter ni el número de canales.
La comprobación directa requiere una lectura dirigida del ADST. Los ceros UMD
antiguos tampoco deben reinterpretarse automáticamente como verdad física completa.

Contraejemplo reproducido con las dos funciones reales y objetos artificiales:
un counter con proxy nulo (no None), tres módulos sin canales, y SD simulado
disponible. El lector original guarda 3 filas, el nuevo guarda
0. En las originales nMuones_MC queda en cero inicial y el conteo
SD-MC vale uno. Esto demuestra que el cambio de condición puede eliminar filas
SD válidas, sin invocar un fallo de Offline. No reemplaza la inspección del
puntero real en los eventos perdidos. Las pruebas originales omitieron justamente
la combinación proxy nulo + canales vacíos; que pasaran no certificaba equivalencia.

## 3. El lector mínimo no cubre la muestra SD de la sección 5

En la misma región Infill, 30≤theta<40 grados y 150≤r<1800 m:

- Inventario SD simulado anterior: 106280 estaciones/evento.
- De ellas con HasStation=True: 51031; sin él: 55249.
- Parquet viejo, SD sin duplicados: 51031; coincide con la selección del inventario.
- Parquet nuevo, SD sin duplicados: 46820.
- Filas nuevas por módulo con flag False en esta región: 0.
- Estaciones/evento con HasStation=False recuperadas del inventario: 0.
- Filas viejas por módulo perdidas en esta región: 12633.

La coincidencia de conteos SD del inventario con el parquet viejo se volvió a
comprobar: exacta. Máxima diferencia radial: 4.55e-13 m; azimutal:
1.14e-13 grados. Esto respalda el control anterior de la muestra seleccionada,
no valida automáticamente todas las variables de ROOT ni su población ausente.

El bucle original parte de `MDEvent.CountersBegin()` y de módulos UMD guardados.
La sección 5 parte de `SDEvent.GetSimStationVector()`, sin exigir esos módulos.
Cambiar HasStation no elimina los requisitos UMD. Corregir la pérdida de filas
es necesario pero, por sí solo, no garantiza recuperar todo el inventario SD.

## 4. Comparación numérica con el MISMO ajuste de la sección 5

Se ejecutan sus funciones de ajuste sin importar el notebook: doce bins de phi,
medias/SEM, normalización y curve_fit idénticos. A1>0 = temprano; A1<0 = tardío.
La unidad es estación/evento, NO módulo. Son errores formales, no bootstrap.

| Muestra, una fila SD/evento | A1, 1200–1350 m | Error formal | Filas |
|---|---:|---:|---:|
| SD_sim_vector_all | +0.06886683 | 0.01575591 | 12212 |
| SD_sim_vector_HasStation | -0.12399013 | 0.01713878 | 3694 |
| old_parquet_SD_unique | -0.12399013 | 0.01713878 | 3694 |
| new_flag_true_SD_unique | -0.11006015 | 0.02032858 | 2663 |
| new_all_SD_unique | -0.11006015 | 0.02032858 | 2663 |

El CSV auditoria_filas_ajustes.csv contiene todos los bins y ambos conteos SD.
No se modifica ni sustituye la figura anterior. El nuevo parquet no se certifica
como dataset equivalente al anterior filtrado hasta resolver las filas perdidas.

## 5. Warnings y errores: qué muestra el código, no qué se puede suponer

- El extractor diagnóstico antiguo adst_counts_fast.py sí fija
  `ROOT.gErrorIgnoreLevel=ROOT.kError`: oculta warnings de niveles inferiores.
- El lector mínimo NO fija ese nivel. El nivel efectivo del kernel del usuario
  no está registrado y puede heredarse de celdas previas: no se puede certificar
  desde un log copiado que todas las advertencias se mostraron.
- Conserva excepciones geométricas amplias que pueden terminar en un skip sin
  mensaje, y un AttributeError de getters MC deja valores ausentes.
- El wrapper captura errores de archivo y devuelve un texto; los textos se
  imprimen después de pool.map. Éxito significa que escribió parquet, no igualdad
  con el anterior ni integridad certificada de todos los objetos ROOT.
- La lectura termina cuando ReadNextEvent deja de devolver eSuccess; la versión
  mínima no distingue EOF de fallo ni comprueba GetNEvents.

Sumas reproducidas del log paralelo: [{'version': 'old', 'files_completed': 20, 'rows': 1589487, 'events': 24139, 'warning_lines': 0}, {'version': 'new', 'files_completed': 20, 'rows': 1525785, 'events': 24139, 'warning_lines': 0}].
No hay evidencia aquí que permita atribuir el problema a un bug de Offline.
Sí hay una selección adicional introducida por nuestro lector y una comparación
de universos que no puede presentarse como si fuera el mismo experimento.

## Fuentes de código inspeccionadas (instalación local, sólo lectura)

- ADST/RecEvent/src/MDEventADST.cc, GetSimCounter: retorna nullptr si no encuentra ID.
- Modules/General/RecDataWriterNG/MD2ADST.cc, Convert: AddCounter para counters
  existentes; AddSimCounter sólo cuando HasSimData.
- El mismo archivo, MakeCounter: retorna antes de llenar módulos si falta RecData.

No se corrigió ni rerunó el lector durante esta auditoría. Primero se documenta
el fallo observado; una corrección debe conservar las filas SD aun sin verdad
UMD y distinguir ausencia de información de cero físico.
