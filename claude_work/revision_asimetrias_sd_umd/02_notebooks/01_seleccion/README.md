# Empezá por el notebook, no por los archivos de resultados

Abrí **[seleccion_sd_paso_a_paso.ipynb](seleccion_sd_paso_a_paso.ipynb)**.

Es un recorrido documentado en español, con explicaciones, tablas de estaciones reales, ajustes calculados paso a paso y figuras. La versión [HTML](seleccion_sd_paso_a_paso.html) permite leerlo con sus salidas sin abrir Jupyter.

## ¿De dónde salieron esos datos?

Los `.root` ADST de simulación guardan una colección de estaciones SD simuladas y otra de estaciones SD reconstruidas. El lector del parquet consulta la primera **sólo si existe la contraparte en la segunda**. El control leyó también los conteos simulados de estaciones sin esa contraparte.

No se reconstruyeron nuevamente las lluvias. No se generaron muones nuevos. No se recuperaron las alturas y momentos individuales de producción que faltaban para el Fast-MC. La pregunta es: **¿cuánto cambia el promedio cuando incluyo o excluyo esas filas ya guardadas?**

## Qué reproduce

1. Muestra rutas, archivos y el filtro exacto del lector original.
2. Abre registros con conteo MC aunque no exista objeto REC.
3. Lee tu parquet, distingue módulos UMD de estaciones SD y elimina sólo la repetición SD.
4. Empareja archivos, eventos y estaciones; comprueba conteos, radios y ángulos.
5. Calcula las doce medias azimutales y ajusta A1, comprobándolo algebraicamente.
6. Dibuja perfiles antes/después, eficiencias y distribuciones de conteos.
7. Recalcula el bootstrap pareado por grupos de lluvias y la evolución radial.
8. Muestra UMD, SD muones, SD EM y SD Total sin equiparar conteos y señal.
9. Repite controles con mezcla común de radio/energía/cenital y bandas más estrechas.
10. Verifica el límite del piloto UMD: información ausente no implica cero muones.
11. Incluye el extractor ROOT completo, una opción segura de relectura y el cotejo de una lectura fresca pequeña.

**No carga A1 ni intervalos desde JSON.** Los calcula desde las filas. Las constantes finales sólo comprueban la reproducción del resultado anterior después de obtenerlo.

El objetivo es hacer comprensible y reproducible el hallazgo de selección y sus controles. No rehace todos los barridos analíticos exploratorios del informe anterior ni los presenta como validación física del trigger.

## Cómo ejecutarlo normalmente

Abrí Jupyter/VS Code dentro del repositorio y elegí el kernel de `venv/bin/python`. Ejecutá las celdas en orden. Los insumos predeterminados son:

- El parquet original, en la ruta configurada al inicio.
- `../../04_soporte/tablas/adst_counts_fast.csv`: **106280 filas de estaciones**, no coeficientes ajustados. Es la extracción previa de veinte ADST, reutilizada para evitar lectura ROOT innecesaria.
- `../../04_soporte/tablas/umd_selection_raw.csv`: resumen por módulo del piloto UMD, utilizado sólo para examinar disponibilidad.

La ejecución principal no importa ROOT ni llama a los scripts comprimidos del informe anterior. El archivo de estaciones pesa aproximadamente 24 MB. Las librerías numéricas se limitan a un hilo y no hay paralelismo de procesamiento.

Las salidas aparecen dentro del notebook y en `exports/`: gráficos PNG/PDF y tablas CSV con nombres descriptivos. Reejecutar puede reemplazar esas salidas generadas; nunca modifica los insumos, la tesis ni los resultados de la auditoría anterior.

## Si querés empezar desde los ADST

El apéndice A incluye el código de [read_original_adst.py](read_original_adst.py) y el comando reproducible. La relectura está desactivada por defecto: `REREAD_ADST = False`.

- Prueba inicial: un archivo, como máximo cincuenta eventos guardados.
- Extracción completa: veinte archivos y todos sus eventos; requiere cambiar deliberadamente la confirmación de costo.
- Es lectura serial de archivos existentes, no simulación ni reconstrucción. La referencia histórica del barrido completo es de varios minutos, dependiente del servidor.
- Se crea una carpeta nueva por ejecución. El extractor rechaza sobrescribir una carpeta existente y sólo permite salidas dentro de este directorio de trabajo.
- Después apuntá `RAW_STATION_TABLE` al nuevo `stations.csv` y repetí el notebook. Una extracción parcial no tiene por qué reproducir el A1 del conjunto completo.

La lectura utiliza el intérprete/diccionario ROOT6 de Offline especificado, en un proceso separado. No se instala ningún kernel ni paquete y no se mezclan bibliotecas ROOT dentro del kernel pandas.

## Prueba fresca incluida

`raw_smoke_test/` contiene la relectura acotada efectuada con el extractor nuevo: cincuenta eventos guardados del primer archivo, de los que nueve están en la banda cenital y producen doscientas filas SD. El notebook coteja cada una con la extracción anterior. Esto verifica una submuestra desde el archivo original; no se presenta como otra lectura completa de veinte archivos.

**Compatibilidad:** ROOT emite avisos de esquema/checksum para un mapa de apuntado FD de `Detector` y para `RdRecStationParameterStorageMap`. No se ocultaron y no se escriben objetos ROOT. Se valida específicamente la coincidencia de conteos, presencia y coordenadas usados aquí; no se certifica compatibilidad de todos los campos ni se autoriza reescribir ADST con ese diccionario.

## Fuentes emparejadas y regeneración

El `.py` percent es la fuente editable; el `.ipynb` se sincroniza mediante jupytext y guarda las salidas ejecutadas. No se edita manualmente el JSON del notebook.

Desde la raíz del repositorio:

```bash
venv/bin/jupytext --sync claude_work/revision_asimetrias_sd_umd/02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.py
venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 claude_work/revision_asimetrias_sd_umd/02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.ipynb
venv/bin/jupyter nbconvert --to html --embed-images claude_work/revision_asimetrias_sd_umd/02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.ipynb
```

El HTML incluye figuras; la representación de ecuaciones puede requerir MathJax en el navegador. Para editar interactivamente, abrí el `.ipynb`. No se tocaron notebooks preexistentes ni se ejecutó `git add`, `commit` o `push`.
