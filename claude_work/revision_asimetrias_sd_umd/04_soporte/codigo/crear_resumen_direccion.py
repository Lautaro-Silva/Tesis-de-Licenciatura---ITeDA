"""Render a short advisor summary from verified tables; no new MC processing.

Edit plantillas/resumen_direccion.template.md, then run this script from the
repository venv. All quoted fitted numbers come from the direct-comparison CSV.
Produces matching Markdown, printable HTML and a single-page PDF at package root.
"""
import html
import re
from pathlib import Path

import pandas as pd
from fpdf import FPDF
from markdown_it import MarkdownIt
from review_paths import PACKAGE, TABLES, TEMPLATES

results = PACKAGE / '02_notebooks/03_sd_vs_umd/resultados'
row = pd.read_csv(results / 'comparacion_directa.csv').query('r_min == 1200 and r_max == 1350').iloc[0]
# Verify the production scope used in the abstract from the existing raw table.
scope = pd.read_csv(TABLES / 'adst_counts_fast.csv', usecols=['source', 'theta'])
assert scope.theta.between(30, 40, inclusive='left').all()
assert row.A_SD_antes > 0 > row.A_SD_despues
assert row.delta_antes_low95 < 0 < row.delta_antes_high95
assert abs(row.delta_antes_menos_UMD - (row.A_SD_antes - row.A_UMD_original)) < 1e-12
values = {
    'files': str(scope.source.nunique()),
    'sd_before': f'{row.A_SD_antes:+.3f}', 'sd_after': f'{row.A_SD_despues:+.3f}',
    'umd': f'{row.A_UMD_original:+.3f}', 'delta': f'{row.delta_antes_menos_UMD:+.3f}',
    'low': f'{row.delta_antes_low95:+.3f}', 'high': f'{row.delta_antes_high95:+.3f}',
}
text = (TEMPLATES / 'resumen_direccion.template.md').read_text()
for key, value in values.items():
    text = text.replace('{{'+key+'}}', value)
assert '{{' not in text
assert len(text.split()) < 460, 'Keep the advisor deliverable short.'
for link in re.findall(r'\]\(([^)]+)\)', text):
    assert (PACKAGE / link).is_file(), link
stem = PACKAGE / 'RESUMEN_PARA_DIRECCION'
stem.with_suffix('.md').write_text(text)

body = MarkdownIt('commonmark').render(text)
css = '''body{margin:0;color:#182b3a;background:#edf2f5;font:16px/1.55 system-ui,sans-serif}
main{max-width:830px;margin:30px auto;padding:32px 40px;background:white}
h1{font-size:25px;line-height:1.2;color:#174f70}strong{color:#163e55}a{color:#176d98}
@page{size:A4;margin:16mm}@media print{body{background:white;font-size:10.5pt;line-height:1.4}
main{margin:0;padding:0;max-width:none}h1{font-size:18pt}p{break-inside:avoid}}
@media(max-width:700px){main{margin:0;padding:22px}}
'''
stem.with_suffix('.html').write_text('<!doctype html><html lang="es"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Resumen para dirección — asimetría SD–UMD</title><style>'+css+'</style></head>'
    '<body><main>'+body+'</main></body></html>\n')

# Native vector PDF with embedded Unicode fonts; no browser/install needed.
fonts = Path('/usr/share/fonts/truetype/dejavu')
pdf = FPDF(format='A4')
pdf.set_margins(17, 15, 17)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_font('Review', '', str(fonts / 'DejaVuSans.ttf'))
pdf.add_font('Review', 'B', str(fonts / 'DejaVuSans-Bold.ttf'))
pdf.add_page()
pdf.set_title('Resumen para dirección: inversión de la asimetría muónica SD')
paragraphs = text.strip().split('\n\n')
for index, paragraph in enumerate(paragraphs):
    if index == 0:
        pdf.set_font('Review', 'B', 15)
        pdf.set_text_color(23, 79, 112)
        pdf.multi_cell(0, 7, paragraph.removeprefix('# '), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)
        continue
    plain = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', paragraph)
    pdf.set_text_color(24, 43, 58)
    pdf.set_font('Review', '', 9 if index in {1, len(paragraphs)-1} else 10)
    pdf.multi_cell(0, 4.7, plain, markdown=True, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2.3)
assert pdf.page_no() == 1, 'The summary must fit on a single page.'
pdf.output(str(stem.with_suffix('.pdf')))
print('Summary generated: matching MD/HTML and one-page PDF.')
print('Words:', len(text.split()), '| Numerical values:', values)
