import csv, re

with open('claude_work/REVIEW_ASTRA/checks/_all_files.txt') as f:
    files = [l.strip() for l in f if l.strip()]

def classify(p):
    if p.startswith('GAP_Notes_Latex/GAP2026_041/'):
        if p.endswith('main.tex'):
            return 'Subagent A', 'Current GAP-041 note, full read'
        if p.endswith('.pdf'):
            return 'not read', 'figure PDF; numbers already quoted in main.tex text, not opened'
        if p.endswith('.bib'):
            return 'not read', 'bibliography file, not prose'
        return 'not read', 'auxiliary asset'
    if p.startswith("GAP_Notes_Latex/[Version_Vieja]GAP_41/"):
        if p.endswith('main.tex'):
            return 'Subagent B', 'Old/superseded GAP-041 draft, full read'
        return 'not read', 'duplicate figure/bib asset shared with current version'
    if p.startswith("GAP_Notes_Latex/[UNFINISHED]GAP_Core_REC/"):
        if p.endswith('main.tex'):
            return 'Subagent A', 'Unfinished core-reconstruction-bias note, full read (added to scope)'
        return 'not read', 'auxiliary asset'
    if p.startswith('claude_work/gap_notes_asimetrias_review_v4/'):
        return 'Subagent C', 'v4 (latest pre-Astra Claude review pass), full read'
    if re.match(r'claude_work/gap_notes_asimetrias_review(_v2|_v3)?/', p):
        tag = 'v1 (unversioned)' if 'review/' in p else ('v2' if 'v2/' in p else 'v3')
        return 'Subagent C', f'{tag} predecessor, diffed against v4 counterpart'
    if p.startswith('claude_work/kinematic_divergence_explainer_and_thesis_updates/'):
        if p.endswith('.ipynb'):
            return 'not read', 'paired jupytext notebook, redundant with the .py per repo convention'
        return 'Subagent D', 'full read'
    if p.startswith('claude_work/unified_asymmetry_model_v1/'):
        if p.endswith('.html'):
            return 'not read', 'rendered duplicate of report.md'
        return 'Subagent G', 'full read; key numbers cross-checked against run_output.txt'
    if p.startswith('claude_work/revision_asimetrias_sd_umd/'):
        rel = p[len('claude_work/revision_asimetrias_sd_umd/'):]
        if rel.startswith('99_archivo_local/'):
            return 'SKIPPED', 'untracked in git (absent from review worktree); extracted-text bibliography cache, not opened this pass'
        if rel.startswith('01_fisica/'):
            if rel.endswith('.html'):
                return 'not read', 'rendered duplicate of the .md twin'
            return 'Subagent F + me', 'full read (report.md and physics_explanation.md also read directly by me in Phase 3)'
        if '02_notebooks/04_reprocesamiento/Procesamiento_ADST_dos_rutas.py' in rel:
            return 'me (Phase 3)', 'untracked -> absent from Subagent F worktree; read directly by me from the main checkout; NOT YET EXECUTED per its own header (prepared/validated code, no ADST run yet)'
        if rel.startswith('02_notebooks/01_seleccion/exports/') or rel.startswith('02_notebooks/01_seleccion/raw_smoke_test/'):
            return 'Subagent F', 'CSV data table, contents reported'
        if rel.startswith('02_notebooks/01_seleccion/') and rel.endswith('.html'):
            return 'not read', 'rendered duplicate of the .py (repo convention: edit/read the .py)'
        if rel.startswith('02_notebooks/01_seleccion/'):
            return 'Subagent F', 'full read'
        if rel.startswith('02_notebooks/02_reproduccion/resultados/') and (rel.endswith('.pdf') or rel.endswith('.png')):
            return 'not read', 'figure image; underlying CSV numbers reported instead'
        if rel.startswith('02_notebooks/02_reproduccion/') and rel.endswith('.html'):
            return 'not read', 'rendered duplicate of the .py'
        if rel.startswith('02_notebooks/02_reproduccion/'):
            return 'Subagent F', 'full read'
        if rel.startswith('02_notebooks/03_sd_vs_umd/resultados/') and (rel.endswith('.pdf') or rel.endswith('.png')):
            return 'not read', 'figure image; underlying CSV numbers reported instead'
        if rel.startswith('02_notebooks/03_sd_vs_umd/') and rel.endswith('.html'):
            return 'not read', 'rendered duplicate of the .py'
        if 'replicas_pareadas.csv' in rel:
            return 'Subagent F', 'shape/columns inspected (581KB bootstrap-replica dump), not row-by-row'
        if rel.startswith('02_notebooks/03_sd_vs_umd/'):
            return 'Subagent F', 'full read'
        if rel.startswith('03_borradores_tesis/'):
            if rel.endswith('.diff'):
                if '06' in rel:
                    return 'Subagent F', 'diff read in full'
                return 'Subagent F', 'diff inspected (representative portion, first ~80 lines)'
            if rel in ('03_borradores_tesis/preview.pdf',):
                return 'not read', 'compiled PDF preview of the draft tex, not opened as image'
            return 'Subagent F', 'full read'
        if rel.startswith('04_soporte/codigo/'):
            base = rel.split('/')[-1]
            if base in ('selection_closure.py','umd_selection_check.py','adst_counts_fast.py'):
                return 'Subagent F', 'full read (decision-critical script)'
            return 'Subagent F', 'inspected by name/docstring, described in report.md sec.10'
        if rel.startswith('04_soporte/tablas/'):
            if rel.endswith('adst_station_audit.csv') or rel.endswith('umd_selection_raw.csv') or rel.endswith('adst_counts_fast.csv'):
                return 'Subagent F + me', 'schema/shape inspected via pandas; adst_counts_fast.csv independently reprocessed by me (see checks/zenith_energy_dependence.py)'
            return 'Subagent F', 'contents reported'
        if rel.startswith('04_soporte/figuras/'):
            return 'not read', 'figure image, referenced by filename only'
        if rel.startswith('04_soporte/plantillas/'):
            return 'not read', 'HTML/MD template scaffolding, not analysis content'
        if rel.startswith('04_soporte/referencias/'):
            return 'not read', 'copy of the original thesis figure PDF, used only for provenance, not re-derived'
        if rel.startswith('04_soporte/organizacion/'):
            return 'Subagent F', 'contents reported'
        if rel in ('04_soporte/README.md','04_soporte/README_auditoria.md'):
            return 'Subagent F', 'full read'
        if rel in ('README.md','RESUMEN_PARA_DIRECCION.md'):
            return 'Subagent F + me', 'full read'
        if rel.endswith('.html') or rel.endswith('.pdf'):
            return 'not read', 'rendered duplicate of a .md twin, or a compiled artifact'
        return 'Subagent F', 'read'
    return 'UNCLASSIFIED', ''

rows = []
for p in files:
    who, note = classify(p)
    status = 'skipped' if who == 'SKIPPED' else ('not read' if who == 'not read' else 'read')
    rows.append((p, who, status, note))

with open('claude_work/REVIEW_ASTRA/coverage_manifest.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['path','read_by','status','note'])
    w.writerows(rows)

print(f'{len(rows)} rows written')
from collections import Counter
print(Counter(r[2] for r in rows))
unclassified = [r for r in rows if r[1]=='UNCLASSIFIED']
for r in unclassified: print('UNCLASSIFIED:', r[0])
