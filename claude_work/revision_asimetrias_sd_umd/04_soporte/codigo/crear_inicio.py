"""Render the package entry page from README; no duplicate scientific content."""
from markdown_it import MarkdownIt
from review_paths import PACKAGE

body = MarkdownIt('commonmark', {'html': True}).enable('table').render((PACKAGE / 'README.md').read_text())
style = '''body{margin:0;background:#f5f7fa;color:#172738;font:17px/1.65 system-ui,sans-serif}
main{max-width:1100px;margin:36px auto;padding:36px;background:white;border-radius:12px}
h1,h2{color:#194e70;line-height:1.25}h2{margin-top:2em}a{color:#126ba3}
table{border-collapse:collapse;width:100%;font-size:.93em}td,th{border-bottom:1px solid #d8e2e9;padding:10px;text-align:left}
pre{overflow:auto;background:#edf2f6;padding:18px}code{font-size:.9em}strong{color:#163e5b}
@media(max-width:700px){main{padding:18px;margin:0}table{display:block;overflow:auto}}
'''
(PACKAGE / 'INICIO.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Revisión de asimetrías SD–UMD — inicio</title><style>'+style+'</style>'
    '<main>'+body+'</main></html>\n')
print('Created INICIO.html from README.md.')
