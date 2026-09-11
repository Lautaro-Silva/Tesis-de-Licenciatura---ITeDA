# Validación de la entrega organizada

- Archivos originales inventariados: 163.
- Archivos científicos/documentales trasladados y presentes en la entrega: 129.
- Originales comprobados dentro de la copia recuperable local: 163.
- Fuentes Python con sintaxis válida: 26.
- Notebooks sincronizados con su .py, ejecutados y sin errores: 3.
- Enlaces locales de documentos verificados: 80.
- Tablas CSV contrastadas con los originales: 35; columnas numéricas sin cambios a tolerancia 1e-10 absoluta/relativa.
- Archivos Offline con huella comprobada sin modificaciones: 13.

Los CSV de detalle están en regresion_numerica.csv. Los tiempos de ejecución y
rutas en fichas de procedencia pueden cambiar al trasladar y reejecutar; no se
exige identidad binaria de PDF, HTML, notebooks o manifiestos regenerados.

La validación del informe técnico está en ../tablas/validation_results.json;
la del recorrido didáctico, en ../../02_notebooks/01_seleccion/VALIDACION.md;
la de los borradores, en ../../03_borradores_tesis/validation.json.

No se ejecutó ROOT ni una producción Offline. El traslado no cambia estimadores,
bins, semillas ni conclusiones físicas. La copia local original queda excluida
de Git; en un clon nuevo se omite sólo ese control retrospectivo de archivo.
