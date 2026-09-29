#!/usr/bin/env python3
"""Build an offline review pack; originals are read only. Run with --compile for PDFs."""
from pathlib import Path
import argparse
import difflib
import hashlib
import html
import itertools
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
VERSIONS = {
    'original': ('Original de la tesis', ROOT / 'Tesis - Latex/capitulos'),
    'cinematica': ('Borrador de divergencia cinemática', ROOT / 'claude_work/kinematic_divergence_explainer_and_thesis_updates'),
    'revision': ('Revisión SD/UMD', ROOT / 'claude_work/revision_asimetrias_sd_umd/03_borradores_tesis'),
    'integrado': ('Integrado · 24 septiembre', ROOT / 'claude_work/borradores_capitulos_3_5_6_integrados_2026_09_24'),
}
CHAPTERS = {'03': 'fenomenologia', '05': 'anillo_denso', '06': 'infill'}
GAPS = {
    'gap_viejo': ('GAP · versión vieja', ROOT / 'GAP_Notes_Latex/[Version_Vieja]GAP_41', '_VERSION_VIEJA__GAP__A_Phenomenological_Study_of_Early__Late_Azimuthal_Asymmetries_of_the_Muon_Density.pdf'),
    'gap_publicado': ('GAP · publicado (copia local)', ROOT / 'GAP_Notes_Latex/GAP2026_041', 'GAP__Azimuthal_Asymmetries_in_Extensive_Air_Showers__UMD_SD_Comparison_and_Insights_into_the_Surface_Detector_Sign_Inversion.pdf'),
}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')


def snapshot(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {'original': str(src.relative_to(ROOT)), 'copy': str(dst.relative_to(HERE)),
            'sha256': hashlib.sha256(src.read_bytes()).hexdigest()}


def active(tex):
    return re.sub(r'(?<!\\)%[^\n]*', '', tex)


def run(cmd, cwd, output):
    with output.open('w') as f:
        result = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{cmd[0]} failed: {output}\n{output.read_text()[-4000:]}')


def diff_document(a, b, left, right):
    # escape descriptions: HtmlDiff assumes these are trusted HTML.
    page = difflib.HtmlDiff(wrapcolumn=90).make_file(
        a.splitlines(), b.splitlines(), html.escape(left), html.escape(right),
        context=True, numlines=4, charset='utf-8')
    return page.replace('</head>', '<style>body{font:15px system-ui;margin:20px}table.diff{width:100%;font-size:12px}td{vertical-align:top}.diff_header{background:#e9edf2}.diff_add{background:#c9f2d5}.diff_sub{background:#ffd2d2}.diff_chg{background:#fff1a8}</style></head>').replace('<body>', '<body><p>Comparación del código LaTeX. Verde: agregado a la derecha; rojo: retirado de la izquierda; amarillo: modificación. Se ocultan bloques idénticos largos. Los números son líneas de los .tex originales. Esto no evalúa la validez física.</p>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true')
    args = parser.parse_args()
    manifest = []
    data = {'versions': {}, 'diffs': {}, 'external': {}}
    raw = {}
    preamble = (ROOT / 'Tesis - Latex/main.tex').read_text().split(r'\begin{document}')[0]
    preamble = preamble.replace(r'\addbibresource{bibliografia.bib}', r'\addbibresource{bibliografia.bib}')
    for key, (name, folder) in VERSIONS.items():
        target = HERE / 'fuentes' / key
        docs = {}
        for chapter, stem in CHAPTERS.items():
            src = folder / (f'{chapter}_{stem}' + ('' if key == 'original' else '_DRAFT') + '.tex')
            dst = target / f'{chapter}_{stem}.tex'
            manifest.append(snapshot(src, dst))
            tex = dst.read_text()
            raw[key, chapter] = tex
            headings = [m.group(0) for m in re.finditer(r'\\(?:sub)*section\*?\{[^\n]+', active(tex))]
            docs[chapter] = {'tex': str(dst.relative_to(HERE)), 'text': tex, 'headings': headings, 'page': 1}
        manifest.append(snapshot(ROOT / 'Tesis - Latex/bibliografia.bib', target / 'bibliografia.bib'))
        extra = ''
        if key == 'integrado':
            manifest.append(snapshot(folder / 'bibliografia_adicional.bib', target / 'bibliografia_adicional.bib'))
            extra = '\\addbibresource{bibliografia_adicional.bib}\n'
        combined = active('\n'.join(raw[key, ch] for ch in CHAPTERS))
        labels = set(re.findall(r'\\label\{([^}]+)\}', combined))
        refs = set(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', combined))
        external = sorted(refs - labels)
        data['external'][key] = external
        ext = '\\makeatletter\n' + '\n'.join('\\newlabel{' + label + '}{{externa}{1}{}{}{}}' for label in external) + '\n\\makeatother\n'
        # Include only figure dependencies; preserve their original relative paths.
        for figure in set(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', combined)):
            candidates = [ROOT / 'Tesis - Latex' / figure, ROOT / figure, folder / figure]
            src = next((p for p in candidates if p.is_file()), None)
            if src is None:
                raise FileNotFoundError(figure)
            manifest.append(snapshot(src, target / figure))
        body = preamble + extra + '\n' + ext + r'''
\setlength{\headheight}{30pt}
\begin{document}
\begin{center}\Large ''' + name + r'''\end{center}
\noindent Copia para comparación, 29 de septiembre de 2026. Sólo capítulos 3, 5 y 6.
Los textos se reproducen sin edición. Las referencias a material omitido se indican
como «externa»; consultar la tesis completa. La paginación cambia en esta vista.
\tableofcontents
'''
        for chapter, stem in CHAPTERS.items():
            body += '\n\\clearpage\n\\setcounter{section}{' + str(int(chapter)-1) + '}\n\\phantomsection\\label{review:' + chapter + '}\n\\input{' + f'{chapter}_{stem}.tex' + '}\n'
        body += '\n\\clearpage\n\\printbibliography\n\\end{document}\n'
        save(target / 'revision.tex', body)
        build = target / 'compilacion'
        build.mkdir(exist_ok=True)
        if args.compile:
            print(f'Compiling {key}', flush=True)
            latex = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape', '-output-directory=compilacion', 'revision.tex']
            run(latex, target, build / 'paso1.txt')
            run(['biber', '--input-directory=compilacion', '--output-directory=compilacion', 'revision'], target, build / 'biber.txt')
            run(latex, target, build / 'paso2.txt')
            run(latex, target, build / 'paso3.txt')
        pdf = HERE / 'pdf' / f'{key}.pdf'
        pdf.parent.mkdir(exist_ok=True)
        if (build / 'revision.pdf').exists():
            shutil.copy2(build / 'revision.pdf', pdf)
            aux = (build / 'revision.aux').read_text()
            for chapter in CHAPTERS:
                match = re.search(r'\\newlabel\{review:' + chapter + r'\}\{\{[^}]*\}\{(\d+)\}', aux)
                if match:
                    docs[chapter]['page'] = int(match[1])
        data['versions'][key] = {'name': name, 'pdf': str(pdf.relative_to(HERE)), 'docs': docs}
    for key, (name, folder, pdfname) in GAPS.items():
        target = HERE / 'fuentes' / key
        for filename in ['main.tex', 'bibliografia.bib']:
            manifest.append(snapshot(folder / filename, target / filename))
        tex = (target / 'main.tex').read_text()
        for figure in set(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', active(tex))):
            manifest.append(snapshot(folder / figure, target / figure))
        pdf = HERE / 'pdf' / f'{key}.pdf'
        manifest.append(snapshot(folder / pdfname, pdf))
        raw[key, 'gap'] = tex
        data['versions'][key] = {'name': name, 'pdf': str(pdf.relative_to(HERE)), 'docs': {'gap': {
            'tex': str((target / 'main.tex').relative_to(HERE)), 'text': tex,
            'headings': [m.group(0) for m in re.finditer(r'\\(?:sub)*section\*?\{[^\n]+', active(tex))], 'page': 1}}}
    for chapter in CHAPTERS:
        for left, right in itertools.combinations(VERSIONS, 2):
            target = HERE / 'diferencias' / f'{chapter}_{left}_{right}.html'
            print(f'Diff {target.name}', flush=True)
            save(target, diff_document(raw[left, chapter], raw[right, chapter], VERSIONS[left][0], VERSIONS[right][0]))
            data['diffs'][f'{chapter}:{left}:{right}'] = str(target.relative_to(HERE))
    target = HERE / 'diferencias/gap_viejo_publicado.html'
    save(target, diff_document(raw['gap_viejo', 'gap'], raw['gap_publicado', 'gap'], GAPS['gap_viejo'][0], GAPS['gap_publicado'][0]))
    data['diffs']['gap:gap_viejo:gap_publicado'] = str(target.relative_to(HERE))
    template = (HERE / 'visor.html').read_text()
    save(HERE / 'ABRIR.html', template.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')))
    save(HERE / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    save(HERE / 'referencias_externas.json', json.dumps(data['external'], ensure_ascii=False, indent=2))
    print('Ready: ' + str(HERE / 'ABRIR.html'), flush=True)


if __name__ == '__main__':
    main()
