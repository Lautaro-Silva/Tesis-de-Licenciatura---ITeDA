# Capítulo 3: revisión según las indicaciones del autor

Entrega del 30 de septiembre de 2026. La carpeta conserva la fecha del 29, cuando comenzó la revisión.

1. **`capitulo_3.pdf`**: texto propuesto para leer como capítulo de tesis.
2. **`RESPUESTAS_Y_CRITERIOS.pdf`**: explicación de los puntos consultados, decisiones editoriales y referencias verificadas. También disponible en Markdown.
3. **`03_fenomenologia_DRAFT.tex`**: fuente editable del capítulo. La ecuación 3.4 conserva el número que tenía en CINEMÁTICA.
4. **`diferencias_con_CINEMATICA.html`**: comparación del código anterior con el nuevo borrador. No compara los PDF ni evalúa la física.

Para compilar en TeXstudio, abrir **`vista_previa.tex` como documento principal**. El archivo de capítulo es un fragmento, no el documento principal. Se incluyen las dos figuras y las bibliografías, por lo que esta carpeta se puede copiar o subir a Overleaf de manera independiente de los demás capítulos.

Desde una terminal con pdfLaTeX, Biber y Pandoc:

```bash
bash compilar.sh
```

Pandoc se utiliza sólo para el PDF de respuestas. Para compilar únicamente el capítulo en TeXstudio: pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX, sobre `vista_previa.tex`.

## Alcance

Se conserva la exposición de CINEMÁTICA/GAP vieja, con precisiones de física y redacción. Se reemplaza el desarrollo posterior a la ecuación 3.4 por una explicación gradual de las ponderaciones. La respuesta del tanque y la conexión con Armbruster se reescriben desde sus argumentos físicos. La selección de estaciones queda como una introducción conceptual breve.

No se introducen resultados de toy models ni una afirmación de imposibilidad de inversión. Su eventual estudio cuantitativo requiere una subsección independiente con supuestos, gráficos y comparación de observables. Las respuestas explican qué calculan los modelos existentes y por qué no se adoptan aquí como una validación.

Los originales de la tesis, los borradores anteriores, las notas GAP y los capítulos 5 y 6 no se modificaron. No hay una integración automática, ni cambios en notebooks, ni nuevos ajustes de datos o simulaciones. Las dos claves complementarias propuestas son `Armbruster2018` y `GAP2002_074`.

Si el autor acepta el texto, la integración posterior deberá llevar el capítulo, las figuras y las nuevas entradas bibliográficas a sus ubicaciones definitivas, y armonizar las referencias desde otros capítulos. Esta entrega es un borrador para revisión, no una incorporación aprobada.

`manifest_fuentes.json` documenta las fuentes utilizadas y sus hashes; `VALIDACION.json` registra las verificaciones de la entrega. Los archivos de `soporte/` son extracciones y páginas renderizadas de las referencias locales para el cotejo, no material nuevo de tesis.

Para descargar la entrega, usar `capitulo3_para_revisar.zip` y extraer la carpeta completa. El capítulo puede compilarse fuera del repositorio. La verificación de hashes con `verificar_entrega.py` requiere, en cambio, el checkout original y el entorno Python del proyecto.
