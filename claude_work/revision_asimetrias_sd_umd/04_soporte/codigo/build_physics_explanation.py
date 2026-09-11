"""Render the conceptual physics note; no data reads or numerical modeling."""
from pathlib import Path
import re,html
from markdown_it import MarkdownIt
from html.parser import HTMLParser
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
text=(PHYSICS/'physics_explanation.md').read_text()
equations=[]
def save(m):
    raw=m.group();display=raw.startswith('\\[')
    equations.append(('<div class="eq">' if display else '<span>')+html.escape(raw)+('</div>' if display else '</span>'))
    return f'PHYSICSMATH{len(equations)-1}END'
body=MarkdownIt('commonmark',{'html':True}).enable('table').render(re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)',save,text,flags=re.S))
for i,e in enumerate(equations):
    token=f'PHYSICSMATH{i}END'
    if e.startswith('<div'):body=body.replace('<p>'+token+'</p>',e)
    body=body.replace(token,e)
body=body.replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
style=re.search(r'<style>(.*?)</style>',(PHYSICS/'report.html').read_text(),re.S).group(1)
document='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>The physical effects behind SD–UMD asymmetry</title><script defer src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script><style>'+style+'</style></head><body><main class="wrap">'+body+'</main></body></html>\n'
assert 'PHYSICSMATH' not in document
assert text.count('\\[')==text.count('\\]') and text.count('\\(')==text.count('\\)')
HTMLParser().feed(document)
(PHYSICS/'physics_explanation.html').write_text(document)
print('Rendered physics_explanation.html; no new numerical calculation. Inline/display equations:',len(equations))
