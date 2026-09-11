# Soporte técnico — no hace falta empezar por aquí

Esta sección preserva la evidencia y la reproducibilidad de la auditoría original.
La lectura recomendada empieza en [la guía principal](../README.md).

- `codigo/`: scripts antiguos de extracción, cálculo y verificación; no ejecutarlos
  todos a ciegas. Algunos lectores ROOT antiguos reemplazan sus tablas de salida.
  Para releer ADST, preferir el lector acotado y documentado del notebook 1.
- `tablas/`: una única copia de las extracciones y los resultados previos. No son
  archivos que el autor deba interpretar sin el notebook o el informe.
- `figuras/`: exportaciones de la figura del informe técnico.
- `plantillas/`: fuente del informe y estilo local, sin dependencia del directorio
  no versionado de una revisión anterior.
- `referencias/`: copia inalterada del PDF entregado por el autor para probar la
  reproducción. Es un **insumo de validación**, no otra figura recomendada.
- `organizacion/`: inventario completo del traslado y validación de la entrega.

## Tablas importantes y tablas históricas

| Archivos | Alcance |
|---|---|
| `adst_counts_fast.csv` y su resumen | Extracción SD principal de veinte archivos; insumo común de los tres notebooks |
| `selection_closure_*`, `selection_paired_bootstrap.csv`, `selection_match_summary.json` | Control principal inicial, bandas anchas y emparejamiento con parquet |
| `umd_selection_raw*`, `umd_selection_check.json` | Piloto UMD y límite de disponibilidad de verdad MC |
| `offline_source_manifest.json` | Huellas de los archivos Offline inspeccionados; no contiene una copia del código institucional |
| `adst_station_audit.csv`, `adst_selection_*`, `adst_cluster_bootstrap.json` | Pilotos anteriores de un archivo; **no** sustituir el resultado principal con ellos |
| `analytic_*`, `transport_*`, `unit_checks.json`, `derivation_numbers.json` | Verificaciones analíticas y sensibilidad de modelos, no ajustes a la curva UMD |
| Otras tablas y JSON | Diagnósticos, procedencia y comprobaciones del informe inicial |

La [guía detallada de la auditoría](README_auditoria.md) conserva el mapa de
productores y resultados. Sus notas sobre no haber hecho commits describen la
fase original de investigación; la presente entrega organizada sí se prepara
para el commit y push solicitados por el autor.

Los resultados más recientes no están duplicados aquí: viven junto a su notebook
en `../02_notebooks/03_sd_vs_umd/resultados/`.
