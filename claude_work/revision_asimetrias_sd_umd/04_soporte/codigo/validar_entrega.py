"""Read-only checks of relocated sources, links, notebook outputs and regression.

Writes only the validation report/CSV in 04_soporte/organizacion. With the local
pre-move archive available, also checks all original files and numerical CSVs.
A fresh clone does not need that ignored backup to validate its notebooks/links.
"""
import ast
import csv
import hashlib
import io
import json
import tarfile
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import jupytext
import nbformat
import numpy as np
import pandas as pd
from markdown_it import MarkdownIt
from review_paths import PACKAGE, REPO

REPORTS = PACKAGE / '04_soporte/organizacion'
inventory = list(csv.DictReader((REPORTS / 'inventario_traslado.csv').open()))
delivered = [row for row in inventory if row['entrega_git'] == 'True']
for row in delivered:
    assert (REPO / row['destino']).is_file(), row['destino']
sources = list(PACKAGE.rglob('*.py'))
sources = [p for p in sources if '99_archivo_local' not in p.parts and '.ipynb_checkpoints' not in p.parts]
for source in sources:
    ast.parse(source.read_text(), filename=str(source))

notebooks = list((PACKAGE / '02_notebooks').rglob('*.ipynb'))
notebooks = [p for p in notebooks if '.ipynb_checkpoints' not in p.parts]
assert len(notebooks) == 3
for filename in notebooks:
    nb = nbformat.read(filename, as_version=4)
    paired = jupytext.read(filename.with_suffix('.py'))
    assert [(c.cell_type, c.source) for c in nb.cells] == [(c.cell_type, c.source) for c in paired.cells], filename
    for cell in nb.cells:
        if cell.cell_type == 'code' and cell.source.strip():
            assert cell.execution_count is not None, filename
            assert not any(o.output_type == 'error' for o in cell.get('outputs', [])), filename
    assert filename.with_suffix('.html').exists()

# Validate navigational links (not names inside fenced code or prose).
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                self.links.append(value)

checked_links = 0
def check_link(target, document):
    global checked_links
    pieces = urlsplit(target)
    if pieces.scheme or not pieces.path or pieces.path.startswith('//'):
        return
    path = document.parent / unquote(pieces.path)
    assert path.exists(), f'{document.relative_to(PACKAGE)} -> {target}'
    checked_links += 1

markdown = MarkdownIt('commonmark').enable('table')
for document in PACKAGE.rglob('*'):
    if ('99_archivo_local' in document.parts or '.ipynb_checkpoints' in document.parts
        or document.suffix not in {'.html', '.md'}):
        continue
    # Template links are relative to its rendered physics report.
    location = PACKAGE / '01_fisica/report.md' if document.name == 'report.template.md' else document
    if document.name == 'resumen_direccion.template.md':
        location = PACKAGE / 'RESUMEN_PARA_DIRECCION.md'
    parser = LinkParser()
    parser.feed(markdown.render(document.read_text()) if document.suffix == '.md' else document.read_text())
    for target in parser.links:
        check_link(target, location)

# Numerical regression against the untouched files archived before migration.
archive_path = PACKAGE / '99_archivo_local/originales_antes_de_organizar.tar.gz'
regressions = []
archive_checked = 0
if archive_path.exists():
    with tarfile.open(archive_path, 'r:gz') as archive:
        for row in inventory:
            content = archive.extractfile(row['origen']).read()
            assert hashlib.sha256(content).hexdigest() == row['sha256_original']
            archive_checked += 1
            destination = REPO / row['destino']
            assert destination.exists(), destination
            if destination.suffix != '.csv' or row['entrega_git'] != 'True':
                continue
            before, after = pd.read_csv(io.BytesIO(content)), pd.read_csv(destination)
            assert list(before.columns) == list(after.columns), destination
            assert before.shape == after.shape, destination
            numeric = before.select_dtypes(include='number').columns
            max_difference = 0.
            for column in numeric:
                x, y = before[column].to_numpy(float), after[column].to_numpy(float)
                assert np.allclose(x, y, atol=1e-10, rtol=1e-10, equal_nan=True), (destination, column)
                finite = np.isfinite(x) & np.isfinite(y)
                if finite.any():
                    max_difference = max(max_difference, float(np.max(abs(x[finite] - y[finite]))))
            regressions.append({'tabla': str(destination.relative_to(PACKAGE)),
                                'filas': len(after), 'columnas_numericas': len(numeric),
                                'max_diferencia_absoluta': max_difference})
    pd.DataFrame(regressions).to_csv(REPORTS / 'regresion_numerica.csv', index=False)

# Offline fingerprints remain those of the original audit; this script only reads.
base = REPO / 'claude_work/revision_asimetrias_sd_umd/04_soporte/tablas'
manifest = json.loads((base / 'offline_source_manifest.json').read_text())
from pathlib import Path
offline = Path('/opt/build/AugerOffline-icrc2025-test7')
offline_checked = 0
if offline.is_dir():
    for item in manifest:
        assert hashlib.sha256((offline / item['file']).read_bytes()).hexdigest() == item['sha256']
        offline_checked += 1

text = f'''# Validación de la entrega organizada

- Archivos originales inventariados: {len(inventory)}.
- Archivos científicos/documentales trasladados y presentes en la entrega: {len(delivered)}.
- Originales comprobados dentro de la copia recuperable local: {archive_checked}.
- Fuentes Python con sintaxis válida: {len(sources)}.
- Notebooks sincronizados con su .py, ejecutados y sin errores: {len(notebooks)}.
- Enlaces locales de documentos verificados: {checked_links}.
- Tablas CSV contrastadas con los originales: {len(regressions)}; columnas numéricas sin cambios a tolerancia 1e-10 absoluta/relativa.
- Archivos Offline con huella comprobada sin modificaciones: {offline_checked}.

Los CSV de detalle están en regresion_numerica.csv. Los tiempos de ejecución y
rutas en fichas de procedencia pueden cambiar al trasladar y reejecutar; no se
exige identidad binaria de PDF, HTML, notebooks o manifiestos regenerados.

La validación del informe técnico está en ../tablas/validation_results.json;
la del recorrido didáctico, en ../../02_notebooks/01_seleccion/VALIDACION.md;
la de los borradores, en ../../03_borradores_tesis/validation.json.

No se ejecutó ROOT ni una producción Offline. El traslado no cambia estimadores,
bins, semillas ni conclusiones físicas. La copia local original queda excluida
de Git; en un clon nuevo se omite sólo ese control retrospectivo de archivo.
'''
(REPORTS / 'VALIDACION.md').write_text(text)
print(text)
