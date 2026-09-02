# Notebooks activos: formato `.py` (jupytext, percent)

Los notebooks de análisis activos de este repositorio se editan como ficheros `.py`
en formato *percent* de [jupytext](https://jupytext.readthedocs.io/), no como `.ipynb`.
Un `.ipynb` con las mismas celdas sigue existiendo en disco para poder ejecutarlas
interactivamente, pero **no está trackeado en git** — es un artefacto local.

## Por qué

Un `.ipynb` es JSON, y cada celda ejecutada guarda su salida (figuras en base64,
tablas, texto) dentro del mismo archivo. Varios notebooks de este repo llegaron a
pesar varios MB casi enteramente por esas salidas — `plots_seccion_6.ipynb` llegó a
tener 12.4 MB de 12.5 MB en salidas guardadas. Eso hace que:

- cualquier herramienta que edite el archivo como texto tenga que procesar ese JSON
  completo, incluidas las imágenes codificadas;
- los diffs de git sean ilegibles (una imagen en base64 no se puede revisar);
- el repositorio crezca de forma acumulativa con cada commit que reejecuta el notebook.

El `.py` en formato percent contiene solo el código, marcado con `# %%` por celda —
texto plano, diffeable, sin salidas.

## Cómo trabajar con ellos

**Abrir un `.py` como notebook:** en JupyterLab (con la extensión de jupytext, ya
instalada en `venv/`) o en VS Code, abrir el `.py` directamente — se muestra con la
interfaz de celdas de un notebook normal, y se ejecuta celda por celda igual que
siempre.

**El `.py` y el `.ipynb` están emparejados (*paired*).** La cabecera YAML al inicio
del `.py` (`# jupytext: formats: ipynb,py:percent`) le dice a jupytext que ambos
representan el mismo notebook. Guardar desde cualquiera de los dos regenera el otro
automáticamente si se abrió el `.py` en Jupyter/VS Code con la extensión activa. Para
sincronizar manualmente desde la terminal:

```bash
venv/bin/jupytext --sync Scripts/nombre_del_notebook.py
```

**El `.ipynb` es local, no se commitea.** Está en `.gitignore` explícitamente (por
ruta, no con un patrón `*.ipynb` global — los notebooks históricos en `Codigo Viejo/`,
`Test Iniciales/`, etc. siguen trackeados tal cual). Si el `.ipynb` de un notebook
activo se borra o no existe (por ejemplo, en un clon nuevo del repo), abrir el `.py`
en Jupyter lo regenera vacío de salidas; hay que volver a ejecutarlo para tener las
figuras.

**Las figuras que importan para la tesis se guardan a disco**, no solo como salida
de celda — buscar las llamadas a `plt.savefig(...)` dentro de cada notebook. Nota:
esas llamadas usan nombres de archivo relativos (sin carpeta), así que escriben en el
directorio desde donde se lanzó Jupyter — no directamente en
`Tesis - Latex/imagenes/`. Eso es preexistente a esta conversión y no se tocó.

## Notebooks convertidos en esta migración

- `Scripts/plots_seccion_6.py`
- `Scripts/validacion_rec_muones.py`
- `Scripts/analisis_infill_sims.py`
- `Scripts/validacion_asimetria_infill_sd_mu_v2.py`
- `Scripts/Presentacion_Foundations/presentacion_feb_2026_v2.py`
- `Scripts/Procesamiento_ADST_v8-2.py` (requiere entorno Auger Offline, no el venv)
- `Scripts/Procesamiento_ADST_Campo_v9.py` (requiere entorno Auger Offline)
- `Scripts/Procesamiento_Datos_Campo/Procesamiento_Datos_Campo_v1.py` (requiere Auger Offline)
- `Scripts/Procesamiento_Datos_Campo/Analisis_Preliminar_DatosCampo_Phase1.py`
- `Scripts/Procesamiento_Datos_Campo/Analisis_Preliminar_DatosCampo_Phase2.py`

El resto de los notebooks del repo (`Codigo Viejo V1/`, `Codigo Viejo V2/`,
`Cosas Random Mayo 2026/`, `Test Iniciales/`, `Pruebas Infill/`, `Carmina_y_Marina/`,
`Intento Toy Model para Inversion Fallido/`, `calculador_puntaje_conicet.ipynb`) se
dejaron como `.ipynb` — son código histórico/deprecado, no se construye sobre ellos
(ver `CLAUDE.md` §8).

La conversión se verificó como puramente de formato: el contenido de cada celda de
código y markdown es idéntico, carácter por carácter, entre el `.ipynb` original y el
`.py` convertido, para los 10 notebooks — ver
`claude_work/notebooks_a_py/verificar_roundtrip.py` y el informe en la misma carpeta.
