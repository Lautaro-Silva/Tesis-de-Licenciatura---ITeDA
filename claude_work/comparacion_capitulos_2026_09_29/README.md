# Comparación de capítulos y notas GAP

Abrir **ABRIR.html** en un navegador. Funciona localmente, sin servidor ni Overleaf.
Para usarlo en otra computadora, descargar `comparacion_capitulos.zip`, extraerlo
completo y abrir `ABRIR.html` dentro de la carpeta extraída. No basta descargar
sólo el HTML: sus enlaces usan los PDF, fuentes y diferencias de la misma carpeta.
Si el navegador descarga los PDF en vez de mostrarlos dentro del visor, usar «Abrir PDF»
y disponer dos ventanas lado a lado. El resto de las funciones no requiere visor PDF.

## Contenido

- `pdf/`: cuatro compilaciones reducidas de capítulos 3, 5 y 6, y las dos notas GAP copiadas de sus PDF existentes.
- `fuentes/original/`: capítulos actuales de `Tesis - Latex/capitulos`.
- `fuentes/cinematica/`: `kinematic_divergence_explainer_and_thesis_updates`.
- `fuentes/revision/`: `revision_asimetrias_sd_umd/03_borradores_tesis`.
- `fuentes/integrado/`: `borradores_capitulos_3_5_6_integrados_2026_09_24`.
- `fuentes/gap_viejo/` y `fuentes/gap_publicado/`: código, bibliografía y figuras de ambas notas.
- `diferencias/`: las seis combinaciones de versiones por capítulo (18 comparaciones), y GAP vieja frente a publicada. Resaltan código LaTeX, no el PDF. Los números de línea corresponden al fuente; se ocultan bloques idénticos largos. Cambios de saltos de línea también aparecen como diferencias.
- `manifest.json`: procedencia y SHA-256 de las copias. Los capítulos copiados son idénticos byte a byte a sus fuentes al preparar el paquete; se normalizó sólo su nombre de archivo.
- `referencias_externas.json`: etiquetas citadas cuyo destino está fuera de los tres capítulos de cada versión.

## Ejemplo concreto

1. Izquierda: **Revisión SD/UMD**, capítulo 3.
2. Derecha: **Integrado · 24 septiembre**, capítulo 3.
3. Leer los PDF; luego abrir **Ver diferencias**.
4. Cambiar la izquierda a **Borrador de divergencia cinemática** para contrastar el desarrollo anterior.
5. Cambiarla a **GAP · versión vieja** para leer el desarrollo en inglés de §2. Cambiar a **GAP · publicado** para su §2 y discusión en §5. El diff automático entre idiomas no es útil; la guía del visor ubica los pasajes correspondientes.
6. Consultar **Original de la tesis** antes de decidir qué conservar.

Las seis versiones son documentos para revisar, no alternativas físicamente equivalentes.
El orden o la fecha no determina qué afirmaciones se deben aceptar. Este paquete no hace
una nueva revisión científica ni verifica la publicación remota de la nota GAP.

## Redactar la versión unificada

Duplicar **una carpeta completa** de `fuentes/` de tesis en otra carpeta, por ejemplo
`mi_version_unificada/`. Elegir la base deliberadamente: original, cinemática, revisión
o integrado. Las cuatro incluyen figuras, bibliografía y `revision.tex`.

Abrir `revision.tex` de la copia en TeXstudio como documento principal. Editar
`03_fenomenologia.tex`, `05_anillo_denso.tex` y `06_infill.tex`, copiando los pasajes
elegidos desde los otros `.tex`. Los archivos `.tex` son fragmentos de capítulo;
se compila `revision.tex`, no un fragmento suelto. Cambiar también el rótulo de
versión en `revision.tex` para identificar la redacción nueva.

Desde la carpeta de trabajo, compilar con:

```bash
pdflatex -interaction=nonstopmode -halt-on-error revision.tex
biber revision
pdflatex -interaction=nonstopmode -halt-on-error revision.tex
pdflatex -interaction=nonstopmode -halt-on-error revision.tex
```

Al copiar texto del integrado, copiar también las entradas necesarias de
`bibliografia_adicional.bib`, su `\addbibresource` y cualquier figura nueva que se use.
Si cambia una etiqueta o se incorporan secciones, revisar referencias y citas al
compilar. Las referencias a material omitido se muestran como **externa** mediante
etiquetas de apoyo en `revision.tex`; al integrar a la tesis completa, usar los
capítulos y bibliografía, no estas etiquetas de apoyo. No se alteró el texto para
inventar numeración de capítulos ausentes.

Las notas GAP usan BibTeX (`bibtex main`), no Biber. Se preservaron sus PDF existentes,
sin recompilarlos; el paquete conserva también sus fuentes locales, pero no garantiza
que esos PDF históricos procedan exactamente de esos fuentes.

## Regenerar el paquete

Desde la raíz del repositorio:

```bash
python3 claude_work/comparacion_capitulos_2026_09_29/preparar.py --compile
```

Requiere Python, pdfLaTeX y Biber; no instala herramientas. Compila secuencialmente.
Este comando actualiza las copias y resultados de esta carpeta desde sus originales:
**no editar los snapshots de `fuentes/` como versión final; trabajar en una copia aparte.**
El visor contiene una instantánea del código: no refleja cambios hasta regenerarlo.
No se cambian los originales, no se hacen commits y no se ejecutan análisis físicos.

## Validación de esta entrega

Las cuatro compilaciones reducidas finalizaron sin referencias ni citas indefinidas.
Se verificaron 113 copias contra sus fuentes mediante SHA-256, las 19 comparaciones,
la sintaxis JavaScript y los destinos de capítulo en los seis PDF. Detalles en
`VALIDACION.json`. Los originales y el borrador cinemático conservan algunos avisos
de líneas que exceden el margen; no se reescribió su contenido para cambiar el formato.
