# Validación de la entrega organizada

- Archivos originales inventariados: 163.
- Archivos científicos/documentales trasladados y presentes en la entrega: 129.
- Originales comprobados dentro de la copia recuperable local: 163.
- Fuentes Python con sintaxis válida: 31.
- Notebooks sincronizados con su .py: 5.
- Notebooks de análisis ejecutados y sin errores: 3.
- Cuadernos de reprocesamiento sin ejecutar: 2; la versión simple corre al ejecutar su celda, la auditada anterior mantiene sus interruptores deshabilitados.
- Enlaces locales de documentos verificados: 107.
- Tablas CSV contrastadas con los originales: 35; columnas numéricas sin cambios a tolerancia 1e-10 absoluta/relativa.
- Archivos Offline con huella comprobada sin modificaciones: 13.

Los CSV de detalle están en regresion_numerica.csv. Los tiempos de ejecución y
rutas en fichas de procedencia pueden cambiar al trasladar y reejecutar; no se
exige identidad binaria de PDF, HTML, notebooks o manifiestos regenerados.

La validación del informe técnico está en ../tablas/validation_results.json;
la del recorrido didáctico, en ../../02_notebooks/01_seleccion/VALIDACION.md;
la de los borradores, en ../../03_borradores_tesis/validation.json;
las pruebas sintéticas del nuevo lector, en ../../02_notebooks/04_reprocesamiento/VALIDACION.md
(carpeta eliminada el 2026-09-29; recuperable desde el commit `0a5dd5e`).

No se ejecutó ROOT ni una producción Offline. El traslado no cambia estimadores,
bins, semillas ni conclusiones físicas. La copia local original queda excluida
de Git; en un clon nuevo se omite sólo ese control retrospectivo de archivo.
