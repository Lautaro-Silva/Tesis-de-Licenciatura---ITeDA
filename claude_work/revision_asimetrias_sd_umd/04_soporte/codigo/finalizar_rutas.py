"""One-time mechanical follow-up to consolidation; no scientific calculations."""
from pathlib import Path
import csv
import os
import re
import shutil
from review_paths import PACKAGE, REPO, PHYSICS, TEMPLATES, CODE

inventory = list(csv.DictReader((PACKAGE / '04_soporte/organizacion/inventario_traslado.csv').open()))
mapping = {REPO / row['origen']: REPO / row['destino'] for row in inventory}
for original, target in mapping.items():
    if not target.exists() or '99_archivo_local' in target.parts or target.suffix not in {'.py', '.md', '.tex', '.html'}:
        continue
    text = target.read_text()
    # Plain-code references and prose paths not expressed as Markdown links.
    for old, new in mapping.items():
        old_rel = os.path.relpath(old, original.parent)
        if old_rel.startswith('../'):
            text = text.replace(old_rel, os.path.relpath(new, target.parent))
    target.write_text(text)

builder = CODE / 'build_report.py'
text = builder.read_text().replace(
    "artifacts=['report.template.md','report.md','report.html','selection_audit.svg',",
    "artifacts=['../plantillas/report.template.md','../../01_fisica/report.md','../../01_fisica/report.html','../figuras/selection_audit.svg',")
builder.write_text(text)

# Preserve only the reusable stylesheet, not a duplicate of the prior report.
style_target = TEMPLATES / 'estilo_informe.html'
if not style_target.exists():
    old_html = (REPO / 'claude_work/unified_asymmetry_model_v1/report.html').read_text()
    style = re.search(r'<style>(.*?)</style>', old_html, re.S).group(1)
    style_target.write_text('<!-- Local style extracted from the previous review; no report content. -->\n<style>'+style+'</style>\n')

# Original reference PDF was an untracked user file outside the five folders.
# Keep a read-only copy in the package so a fresh clone has the test fixture.
reference = PACKAGE / '04_soporte/referencias/SD_Desglose_Componentes_vs_UMD_original.pdf'
if not reference.exists():
    reference.parent.mkdir(exist_ok=True)
    shutil.copy2(REPO / 'Scripts/SD_Desglose_Componentes_vs_UMD.pdf', reference)
notebook = PACKAGE / '02_notebooks/02_reproduccion/reproducir_desglose_sd.py'
text = notebook.read_text().replace(
    'REFERENCE = REPO / "Scripts/SD_Desglose_Componentes_vs_UMD.pdf"',
    'REFERENCE = REPO / "claude_work/revision_asimetrias_sd_umd/04_soporte/referencias/SD_Desglose_Componentes_vs_UMD_original.pdf"')
text = text.replace('# ## 4. Comparar contra el PDF que proporcionaste',
                    '# ## 4. Comparar contra el PDF que proporcionaste\n#\n'
                    '# Se usa una copia inalterada en 04_soporte/referencias para que el\n'
                    '# cotejo también funcione en un clon nuevo. El original de Scripts no se modifica.')
notebook.write_text(text)
print('Updated remaining relative references, manifests and standalone report style.')
