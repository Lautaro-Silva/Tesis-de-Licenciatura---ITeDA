"""One-time, lossless organization of the five review folders.

Not a physics analysis. Refuses to run again after its inventory exists. Records
every original file and hash, preserves an ignored local tar backup, moves rather
than deletes, and mechanically updates paths in text sources. Notebook JSON is
never edited here: sync the moved .py sources with jupytext and execute afterward.
"""
from pathlib import Path
import csv
import hashlib
import os
import re
import tarfile
from urllib.parse import quote, unquote, urlsplit

REPO = next(p for p in Path(__file__).resolve().parents if (p / 'CLAUDE.md').is_file())
ROOT = REPO / 'claude_work/revision_asimetrias_sd_umd'
WORK = REPO / 'claude_work'
SIMPLE = {
    'sd_selection_walkthrough': ROOT / '02_notebooks/01_seleccion',
    'sd_component_plot_reproduction': ROOT / '02_notebooks/02_reproduccion',
    'sd_uncut_vs_umd': ROOT / '02_notebooks/03_sd_vs_umd',
    'physics_selection_thesis_drafts': ROOT / '03_borradores_tesis',
}
FORENSIC = WORK / 'sd_muon_asymmetry_forensic_review'
TABLES = ROOT / '04_soporte/tablas'
CODE = ROOT / '04_soporte/codigo'
PHYSICS = ROOT / '01_fisica'
LOCAL = ROOT / '99_archivo_local'
INVENTORY = ROOT / '04_soporte/organizacion/inventario_traslado.csv'

def destination(path):
    folder = path.relative_to(WORK).parts[0]
    rel = path.relative_to(WORK / folder)
    # Caches and LaTeX intermediate files are recoverable locally, not delivered.
    if ('__pycache__' in rel.parts or '.ipynb_checkpoints' in rel.parts
        or path.suffix in {'.aux', '.bbl', '.bcf', '.blg', '.log', '.out', '.toc'}
        or path.name.endswith(('.run.xml', '.synctex.gz'))):
        return LOCAL / 'intermedios' / folder / rel
    if folder != FORENSIC.name:
        target = SIMPLE[folder]
        if folder in {'sd_component_plot_reproduction', 'sd_uncut_vs_umd'} and path.suffix in {'.csv', '.pdf', '.png'}:
            return target / 'resultados' / rel
        return target / rel
    if path.suffix == '.txt':
        return LOCAL / 'textos_extraidos_PDF' / rel
    if path.suffix == '.py':
        return CODE / rel
    if path.suffix in {'.json', '.csv'}:
        return TABLES / rel
    if path.name == 'report.template.md':
        return ROOT / '04_soporte/plantillas' / rel
    if path.suffix in {'.svg', '.png'}:
        return ROOT / '04_soporte/figuras' / rel
    if path.name == 'README.md':
        return ROOT / '04_soporte/README_auditoria.md'
    return PHYSICS / rel

def main():
    if INVENTORY.exists():
        raise SystemExit('Already organized: refusing to move or overwrite anything.')
    originals = [WORK / name for name in SIMPLE] + [FORENSIC]
    assert all(p.is_dir() for p in originals)
    files = sorted(p for directory in originals for p in directory.rglob('*') if p.is_file())
    mapping = {p: destination(p) for p in files}
    assert len(set(mapping.values())) == len(mapping)
    assert not any(p.exists() for p in mapping.values())
    LOCAL.mkdir(parents=True, exist_ok=True)
    with tarfile.open(LOCAL / 'originales_antes_de_organizar.tar.gz', 'x:gz') as archive:
        for directory in originals:
            archive.add(directory, arcname=str(directory.relative_to(REPO)))
    rows = []
    for old, new in mapping.items():
        digest = hashlib.sha256(old.read_bytes()).hexdigest()
        rows.append({'origen': str(old.relative_to(REPO)), 'destino': str(new.relative_to(REPO)),
                     'bytes_originales': old.stat().st_size, 'sha256_original': digest,
                     'entrega_git': not new.is_relative_to(LOCAL)})
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)
        assert hashlib.sha256(new.read_bytes()).hexdigest() == digest
    # Remove only now-empty directory shells; all original files have been moved.
    for directory in originals:
        for child in sorted((p for p in directory.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
            child.rmdir()
        directory.rmdir()
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)

    # Map a relative documentation target using its original document location.
    def link_target(link, old_document, new_document):
        parts = urlsplit(link)
        if parts.scheme or not parts.path or parts.path.startswith('/'):
            return link
        old_target = (old_document.parent / unquote(parts.path)).resolve()
        new_target = mapping.get(old_target, old_target)
        # report.template.md is rendered into 01_fisica, not read as a report itself.
        base = PHYSICS if old_document.name == 'report.template.md' else new_document.parent
        path = os.path.relpath(new_target, base)
        return quote(path, safe='/._-') + ('#' + parts.fragment if parts.fragment else '')

    for old, new in mapping.items():
        if new.is_relative_to(LOCAL) or new.suffix not in {'.py', '.md', '.html', '.tex'}:
            continue
        text = new.read_text()
        # Fix actual Markdown and HTML relative links before replacing full paths.
        if new.suffix in {'.py', '.md', '.html'}:
            text = re.sub(r'(!?\[[^\]\n]*\]\()([^\s)]+)(\))',
                          lambda m: m[1]+link_target(m[2], old, new)+m[3], text)
            text = re.sub(r'((?:href|src)=["\'])([^"\']+)(["\'])',
                          lambda m: m[1]+link_target(m[2], old, new)+m[3], text)
        # Exact full paths in code, commands, draft wrappers and comments.
        for source, target in sorted(mapping.items(), key=lambda item: -len(str(item[0]))):
            text = text.replace(str(source.relative_to(REPO)), str(target.relative_to(REPO)))
        for name, target in SIMPLE.items():
            text = text.replace('claude_work/' + name, str(target.relative_to(REPO)))
        text = text.replace('claude_work/sd_muon_asymmetry_forensic_review', str(TABLES.relative_to(REPO)))
        if old.parent == FORENSIC and new.suffix == '.py':
            # Legacy numerical scripts now keep their tables outside the code directory.
            text = text.replace('OUT=Path(__file__).resolve().parent',
                                'from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO')
            for name in ['report.md', 'report.html', 'physics_explanation.md', 'physics_explanation.html']:
                text = text.replace("OUT/'"+name+"'", "PHYSICS/'"+name+"'")
            for name in ['selection_audit.svg', 'selection_audit.png']:
                text = text.replace("OUT/'"+name+"'", "FIGURES/'"+name+"'")
            text = text.replace("OUT/'report.template.md'", "TEMPLATES/'report.template.md'")
            text = text.replace("OUT.parent/'unified_asymmetry_model_v1'/'report.html'",
                                "TEMPLATES/'estilo_informe.html'")
            text = text.replace("OUT.glob('*.py')", "CODE.glob('*.py')")
            text = text.replace("(OUT/unquote(parts.path))", "(PHYSICS/unquote(parts.path))")
        if old.name == 'prepare_and_check.py':
            text = text.replace('ROOT = OUT.parent.parent',
                                "ROOT = next(p for p in OUT.parents if (p / 'CLAUDE.md').is_file())")
        if old.name == 'validate_notebook.py':
            text = text.replace("HERE.parent / 'sd_muon_asymmetry_forensic_review'",
                                "HERE.parents[1] / '04_soporte/tablas'")
        if old.name in {'comparar_sd_umd.py', 'reproducir_desglose_sd.py'}:
            # Outputs are one level below their notebook, not mixed with explanations.
            text = text.replace('pd.set_option(', 'pd.set_option(', 1)
            marker = "HERE = REPO / "
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith(marker):
                    lines.insert(i+1, "RESULTS = HERE / 'resultados'\nRESULTS.mkdir(exist_ok=True)")
                    break
            text = '\n'.join(lines)+'\n'
            text = re.sub(r'HERE / (["\'])([^"\']+\.(?:csv|png|pdf))\1',
                          lambda m: 'RESULTS / '+m[1]+m[2]+m[1], text)
            # Comparison inputs produced by the reproduction live in its resultados.
            text = re.sub(r'PREVIOUS / (["\'])([^"\']+\.csv)\1',
                          lambda m: "PREVIOUS / 'resultados' / "+m[1]+m[2]+m[1], text)
        new.write_text(text)
    print(f'Moved and inventoried {len(files)} files. Originals recoverable in {LOCAL.name}.')
    print('Next: update report manifests, sync/execute notebooks, validate, then commit only ROOT.')

if __name__ == '__main__':
    main()
