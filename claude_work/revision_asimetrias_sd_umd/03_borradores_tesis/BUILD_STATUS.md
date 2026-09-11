# Verificación de esta entrega

- Compilación completada: `pdflatex`, `biber`, `pdflatex`, `pdflatex`.
- `preview.pdf`: 80 páginas, con los tres borradores insertados en el contexto completo de la tesis.
- Sin referencias ni citas indefinidas en la última pasada; sin errores fatales.
- Permanecen avisos de marcadores PDF por matemáticas en títulos y una caja demasiado ancha en la carátula administrativa original. No se modificó esa carátula para resolver un aviso ajeno a los borradores.
- Comprobación estática: 19 imágenes originales conservadas y existentes; sin etiquetas duplicadas ni claves bibliográficas faltantes.
- Los coeficientes e intervalos nuevos del control SD se cotejaron contra los CSV finales de veinte archivos; ver `validation.json`.
- Fuentes protegidos: hashes sin cambios entre las verificaciones y sin diferencias Git en `Tesis - Latex/` ni `GAP_Notes_Latex/`.
- Esta verificación de compilación y consistencia no sustituye una nueva validación de todos los análisis heredados del capítulo 5, ni convierte las hipótesis de transporte o disparo en resultados demostrados.

No se ejecutaron trabajos de producción, procesamiento de MC, cambios de notebooks, staging, commits ni pushes.
