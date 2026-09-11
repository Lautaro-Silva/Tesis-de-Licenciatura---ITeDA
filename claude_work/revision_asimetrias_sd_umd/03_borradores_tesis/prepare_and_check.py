"""Lightweight draft checks and a separate full-thesis preview; no MC jobs.

Run from anywhere with Python 3. All generated files stay beside this script.
This script never writes to the thesis, bibliography, GAP notes, or prior work.
"""
from pathlib import Path
import csv
import difflib
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'CLAUDE.md').is_file())
THESIS = ROOT / 'Tesis - Latex'
AUDIT = ROOT / 'claude_work/revision_asimetrias_sd_umd/04_soporte/tablas'
STEMS = ['03_fenomenologia', '05_anillo_denso', '06_infill']


def read(path):
    return path.read_text(encoding='utf-8')


def write(name, text):
    target = OUT / name
    assert target.parent == OUT and target.resolve().is_relative_to(OUT)
    target.write_text(text, encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncomment(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


protected = sorted(
    p for folder in [THESIS, ROOT / 'GAP_Notes_Latex']
    for p in folder.rglob('*') if p.suffix in {'.tex', '.bib', '.sty', '.cls'}
)
hashes = {str(p.relative_to(ROOT)): sha(p) for p in protected}
snapshot = OUT / 'protected_sources_sha256.json'
if snapshot.exists():
    assert json.loads(read(snapshot)) == hashes, 'Protected sources changed since snapshot'
else:
    write(snapshot.name, json.dumps(hashes, indent=2) + '\n')

checks = {}
drafts = {}
for stem in STEMS:
    source = THESIS / 'capitulos' / (stem + '.tex')
    draft = OUT / (stem + '_DRAFT.tex')
    old, new = read(source), read(draft)
    drafts[stem] = new
    images = lambda t: re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', t)
    old_images, new_images = images(old), images(new)
    checks[stem] = {
        'original_figures': len(old_images), 'draft_figures': len(new_images),
        'all_original_figures_preserved': sorted(old_images) == sorted(new_images),
        'all_graphics_exist': all((THESIS / p).exists() for p in new_images),
        'source_sha256': sha(source), 'draft_sha256': sha(draft),
    }
    assert checks[stem]['all_original_figures_preserved']
    assert checks[stem]['all_graphics_exist']
    stack = []
    for kind, env in re.findall(r'\\(begin|end)\{([^}]+)\}', uncomment(new)):
        if kind == 'begin':
            stack.append(env)
        else:
            assert stack and stack.pop() == env, (stem, env)
    assert not stack, (stem, stack)
    write('cambios_' + stem[:2] + '.diff', ''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=str(source.relative_to(ROOT)), tofile=draft.name)))

# Resolve labels against the full proposed thesis, including unchanged chapters.
texts = []
for p in sorted((THESIS / 'capitulos').glob('*.tex')):
    texts.append(drafts.get(p.stem, read(p)))
composite = uncomment('\n'.join(texts))
labels = re.findall(r'\\label\{([^}]+)\}', composite)
assert len(labels) == len(set(labels)), 'Duplicate labels in composite thesis'
refs = set(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', composite))
checks['unresolved_labels_in_full_preview'] = sorted(refs - set(labels))
draft_text = uncomment('\n'.join(drafts.values()))
draft_refs = set(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', draft_text))
assert not draft_refs - set(labels), draft_refs - set(labels)
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', read(THESIS / 'bibliografia.bib')))
cites = {k.strip() for group in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}', draft_text)
         for k in group.split(',')}
checks['missing_draft_citation_keys'] = sorted(cites - bibkeys)
assert not checks['missing_draft_citation_keys']

# Check new numbers against FINAL twenty-file outputs, not the older pilot files.
with (AUDIT / 'selection_closure_fits.csv').open() as f:
    fits = list(csv.DictReader(f))
with (AUDIT / 'selection_paired_bootstrap.csv').open() as f:
    bootstrap = list(csv.DictReader(f))
numeric = []
for lo, hi in [(300, 600), (650, 950), (1050, 1400), (1400, 1800)]:
    values = []
    for sample in ['all_sim', 'SDrec']:
        row = next(x for x in fits if int(x['lo']) == lo and int(x['hi']) == hi
                   and x['sample'] == sample and x['variable'] == 'mu')
        val = float(row['A'])
        assert f'{val:+.4f}' in drafts['06_infill'], (lo, sample, val)
        values.append(val)
    numeric.append({'lo': lo, 'hi': hi, 'before': values[0], 'after': values[1],
                    'difference': values[1] - values[0]})
far = next(x for x in numeric if x['lo'] == 1050)
assert f"{far['difference']:.4f}" in drafts['06_infill']
farboot = [x for x in bootstrap if x['lo'] == '1050']
for row in farboot:
    for field in ['low', 'high']:
        assert f"{float(row[field]):.4f}" in drafts['06_infill']
checks['new_numbers_match_final_audit'] = True
checks['numeric_provenance'] = numeric
checks['source_outputs_sha256'] = {
    name: sha(AUDIT / name) for name in ['selection_closure_fits.csv',
                                        'selection_paired_bootstrap.csv']}

# Separate preview, full original context, three substituted drafts only.
main = read(THESIS / 'main.tex')
for stem in STEMS:
    main = main.replace('\\input{capitulos/' + stem + '.tex}',
                        '\\input{' + (OUT / (stem + '_DRAFT.tex')).as_posix() + '}')
main = re.sub(r'\\input\{(capitulos/[^}]+)\}',
              lambda m: '\\input{' + (THESIS / m.group(1)).as_posix() + '}', main)
main = main.replace('\\addbibresource{bibliografia.bib}',
                    '\\addbibresource{' + (THESIS / 'bibliografia.bib').as_posix() + '}')
main = main.replace('\\begin{document}',
    '\\graphicspath{{' + THESIS.as_posix() + '/}}\n'
    '\\setlength{\\headheight}{30pt}\n'
    '\\begin{document}\n'
    '\\begin{center}\\Large Vista previa de borradores de los capítulos 3, 5 y 6\\end{center}\n'
    '\\noindent Documento de trabajo: sólo esos capítulos están revisados. '
    'Los demás textos, figuras y notas pendientes se incluyen sin cambios para dar contexto. '
    'Esta compilación no modifica la tesis original.\\clearpage\n')
write('preview.tex', '% GENERATED by prepare_and_check.py; do not edit.\n' + main)
checks['protected_source_files_checked'] = len(hashes)
write('validation.json', json.dumps(checks, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(checks, indent=2, ensure_ascii=False))
