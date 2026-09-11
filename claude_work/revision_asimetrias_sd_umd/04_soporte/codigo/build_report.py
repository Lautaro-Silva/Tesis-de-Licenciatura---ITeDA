"""Build matching Markdown/HTML and one data-derived SVG from audited outputs.
No network access. MathJax in the HTML is an optional browser-side CDN dependency.
"""
from pathlib import Path
import re,json,html,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from markdown_it import MarkdownIt
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
fits=pd.read_csv(OUT/'selection_closure_fits.csv')
boots=pd.read_csv(OUT/'selection_paired_bootstrap.csv')
match=json.loads((OUT/'selection_match_summary.json').read_text())
std=json.loads((OUT/'selection_standardized.json').read_text())
umd=json.loads((OUT/'umd_selection_check.json').read_text())
def value(lo,sample):return fits.query('lo==@lo and sample==@sample and variable=="mu"').iloc[0]
def boot(lo,quantity):return boots.query('lo==@lo and quantity==@quantity').iloc[0]
def signed(x,d=4):return f'{x:+.{d}f}'.replace('-','−')
def interval(z):return f'[{signed(z.low)}, {signed(z.high)}]'
allfar=value(1050,'all_sim');kept=value(1050,'parquet');bb=boot(1050,'difference')
delta=kept.A-allfar.A
legacy=pd.read_csv(OUT/'analytic_legacy.csv').query('response=="SDcount" and floor<1').iloc[0]
(OUT/'model_benchmark_residuals.json').write_text(json.dumps(dict(legacy_SD_endpoint=legacy.endpoint,legacy_SD_Fourier=legacy.A1,raw_all_A1=allfar.A,raw_selected_A1=kept.A,selection_shift=delta,endpoint_benchmark_minus_raw_all=legacy.endpoint-allfar.A,Fourier_benchmark_minus_raw_all=legacy.A1-allfar.A,qualification='Nominal analytic point versus finite-bin Monte Carlo; not a unique physical term decomposition.'),indent=2))
headline=(f'**Established result, all {match["files"]} matched production files:** at '
          f'1050–1400 m and 30–40°, the SD truth-count coefficient changes from '
          f'**{signed(allfar.A)} before station-reconstruction selection to {signed(kept.A)} afterward**. '
          f'The paired difference is **{signed(delta)}**, with a parent-shower bootstrap '
          f'95% interval **{interval(bb)}**. Positive means early excess. The selected value '
          'reproduces the parquet exactly; the pre-selection coefficient is positive. '
          'Thus the sign inversion is induced by this selection in the tested production, '
          'without requiring negative pre-selection SD station-count asymmetry.')
table=['| Shower-plane radius [m] | All simulated SD stations: A₁ | Retained/parquet: A₁ | Difference | All / retained stations |',
       '|---|---:|---:|---:|---:|']
for lo,hi in [(300,600),(650,950),(1050,1400),(1400,1800)]:
    x=value(lo,'all_sim');y=value(lo,'parquet')
    table.append(f'| {lo}–{hi} | {signed(x.A)} | {signed(y.A)} | {signed(y.A-x.A)} | {int(x.n):,} / {int(y.n):,} |')
statistics=(f'The raw extraction contains {match["raw_rows"]:,} station occurrences in the audited radius range; '
            f'{match["matched_rows"]:,} match retained parquet stations, with zero muon-count or EM-count mismatches '
            'and numerical agreement of radius/azimuth. In the far bin, the pre-selection '
            f'95% interval is {interval(boot(1050,"all"))}, and the retained interval is '
            f'{interval(boot(1050,"kept"))}. The paired difference has bootstrap standard deviation '
            f'{bb.sd:.4f}, using {int(bb.clusters)} parent-shower groups and {int(bb.draws)} resamples. '
            'The confidence intervals are statistical, conditional on this production and grouping; '
            'they do not include hadronic-model or source-provenance uncertainty. The independently bootstrapped '
            'parquet interval in §3.1 differs slightly because its observed parent set and random resamples differ.')
standard=(f'**Covariate control:** standardizing both raw samples to the same empirical distribution '
          f'over {std["cells"]} radius/energy/zenith cells gives {signed(std["all"]["A"])} before selection '
          f'and {signed(std["selected"]["A"])} afterward. The difference, '
          f'{signed(std["difference"]["A"])}, is not erased by phase-space mixing. '
          'The secondary uncertainty diagnostic uses positive exponential parent-cluster weights to '
          'avoid conditioning a multinomial bootstrap on sparsely populated cells remaining nonempty. '
          'The primary quoted confidence interval remains the unstandardized paired result. '
          '`selection_narrow_bins.csv` also tests separate radial/zenith halves and a bin '
          '1150–1250 m, 34–36°; the central SD sign changes from positive to negative in each. '
          'No separate significance claim is assigned to every narrower-bin fit.')
umdtext=(f'The bounded one-file extraction contains {umd["raw_module_records"]:,} populated simulation-module '
         f'records, **all associated with reconstructed SD stations**. Its truth totals reproduce all '
         f'{umd["matched_parquet_module_rows"]:,} corresponding parquet module rows after using the reader’s '
         f'zero convention for the {umd["missing_retained_sim_module_rows"]:,} absent retained-module summaries; '
         'every such retained parquet count is zero. In contrast, '
         f'{umd["non_SDrec_occurrences"]:,} SD simulation-station occurrences without reconstructed partners '
         'have no populated UMD module records. That is not evidence that their true underground injection is zero.\n\n'
         'The source explains a concrete information-loss path. '
         '`MdOptoElectronicSimulator.cc:572–584` skips the module/channel path if the associated WCD '
         'has no accepted trigger and `forcedSDTrigger` is false. The inspected production header has '
         '`forcedSDTrigger = 0`. `G4StationSimulator::AddInjectedParticle` makes simulation scintillators, '
         'not electronic channels. Crucially, `MD2ADST::MakeSimCounter`, lines 610–618, serializes '
         'scintillator truth by iterating **event channels**, not all simulation scintillators. '
         'An existing simulated counter with no channels can therefore become an ADST object with an '
         'empty scintillator vector even after particles entered its soil/scintillator simulation.\n\n'
         '**Established:** this pilot cannot support a pre-selection UMD harmonic by reading these '
         'summaries and zero-filling missing objects. **Source-based inference:** the trigger/channel '
         'serialization path can discard the required truth. It is not a proof that every missing '
         'counter contained an injected muon. A pre-electronics count summary, or serialization '
         'independent of channel creation, is the minimal remedy. The pilot and exact retained-count '
         'validation are reproducible with `umd_selection_read.py` and `umd_selection_check.py`.')

# One compact visualization: measured radial change and its binwise composition.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14,4.1),layout='constrained')
radii=[450,800,1225,1600]
for sample,label,color in [('all_sim','Before station selection','#a54334'),('parquet','Retained / parquet','#285d9b')]:
    ys=[value(lo,sample).A for lo in [300,650,1050,1400]]
    errs=[boot(lo,'all' if sample=='all_sim' else 'kept').sd for lo in [300,650,1050,1400]]
    axes[0].errorbar(radii,ys,yerr=errs,marker='o',capsize=3,color=color,label=label)
axes[0].axhline(0,color='#777',lw=.8);axes[0].set(xlabel='Shower-plane radius [m]',ylabel='SD muon A₁',title='Sign change under station selection')
axes[0].legend(fontsize=8)
c=pd.read_csv(OUT/'selection_composition.csv');xx=-180+(c.bin+.5)*30
axes[1].plot(xx,c.mu_all/c.mu_all.mean(),'o-',color='#a54334',label='All simulated')
axes[1].plot(xx,c.mu_selected/c.mu_selected.mean(),'o-',color='#285d9b',label='Retained')
axes[1].set(xlabel='Azimuth φ [degrees]; 0 = early',ylabel='Mean count / azimuthal mean',title='1050–1400 m; 30–40°')
axes[1].legend(fontsize=8)
axes[2].plot(xx,c.eps,'o-',color='#285d9b',label='Station retention ε')
axes[2].plot(xx,c.mu_eff,'s-',color='#5b4686',label='Muon-weighted retention εN')
axes[2].set(xlabel='Azimuth φ [degrees]; 0 = early',ylabel='Retention fraction',title='The two efficiencies are different',ylim=(0,1))
axes[2].legend(fontsize=8)
for ax in axes:ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
fig.savefig(FIGURES/'selection_audit.svg',metadata={'Date':None});fig.savefig(FIGURES/'selection_audit.png',dpi=140);plt.close(fig)

text=(TEMPLATES/'report.template.md').read_text().replace(chr(1),'')
thesisnumbers=('> En los veinte archivos de protones SIBYLL 2.3e de esta verificación, para '
               r'\(1050\le r<1400\,\mathrm m\), \(30\le\theta<40^\circ\) y '
               r'\(17.5\le\log_{10}(E_0/\mathrm{eV})<18.0\), '
               f'el coeficiente SD pasa de {signed(allfar.A)} antes de exigir una estación reconstruida '
               f'a {signed(kept.A)} después de esa condición. La diferencia es {signed(delta)}, '
               f'con intervalo bootstrap del 95% {interval(bb)}, remuestreando lluvias progenitoras '
               'y manteniendo juntas sus reutilizaciones. El valor posterior coincide exactamente '
               'con el obtenido del parquet. La comparación se limita a los eventos escritos en '
               'esta producción y no elimina sus posibles selecciones a nivel de evento ni los '
               'efectos de regeneración de partículas.')
for key,v in dict(selection_headline=headline,raw_table='\n'.join(table),raw_statistics=statistics,standardization=standard,umd_audit=umdtext,thesis_numbers=thesisnumbers).items():text=text.replace('{{'+key+'}}',v)
assert '{{' not in text
# Normalize intentionally parenthesized inline TeX to explicit math delimiters.
# Protect existing math, code and Markdown links before balanced-parenthesis scan.
protected=[]
def protect(m):
    protected.append(m.group(0));return f'PROTECTEDTOKEN{len(protected)-1}END'
work=re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)|`[^`\n]+`|!?\[[^\]\n]*\]\([^\n]*?\)',protect,text,flags=re.S)
parts=[];i=0
while i<len(work):
    if work[i]!='(':parts.append(work[i]);i+=1;continue
    j=i+1;level=1
    while j<len(work) and level:
        if work[j]=='(':level+=1
        if work[j]==')':level-=1
        j+=1
    if level:parts.append(work[i:]);break
    body=work[i+1:j-1]
    ismath=('\\' in body or '_' in body or '=' in body or '^' in body or re.fullmatch('[A-Za-z]',body) or re.match('[+−-][0-9]',body))
    parts.append('\\('+body+'\\)' if ismath and '\n' not in body else work[i:j]);i=j
text=''.join(parts)
for i,v in enumerate(protected):text=text.replace(f'PROTECTEDTOKEN{i}END',v)
(PHYSICS/'report.md').write_text(text)

# Protect TeX from Markdown backslash/underscore interpretation, then restore it.
math=[]
def save_math(m):
    raw=m.group(0);display=raw.startswith('\\[')
    math.append(('<div class="eq">' if display else '<span class="math">')+html.escape(raw)+('</div>' if display else '</span>'))
    return f'MATHTOKEN{len(math)-1}END'
render=re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)',save_math,text,flags=re.S)
body=MarkdownIt('commonmark',{'html':True}).enable('table').render(render)
for i,v in enumerate(math):
    token=f'MATHTOKEN{i}END'
    if v.startswith('<div'):body=body.replace('<p>'+token+'</p>',v)
    body=body.replace(token,v)
toc=[]
def heading(m):
    level,title=m.group(1),m.group(2);plain=re.sub('<[^>]+>','',title)
    slug=re.sub('[^a-z0-9]+','-',html.unescape(plain).lower()).strip('-')
    if level=='2':toc.append(f'<li><a href="#{slug}">{plain}</a></li>')
    return f'<h{level} id="{slug}">{title}</h{level}>'
body=re.sub(r'<h([23])>(.*?)</h\1>',heading,body)
body=body.replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
prior=(TEMPLATES/'estilo_informe.html').read_text()
css=re.search(r'<style>(.*?)</style>',prior,re.S).group(1)
# Retain the prior report's typography/palette without requiring hosted fonts.
css=re.sub(r'@import[^\n]*\n','',css)
css+='\n.wrap{max-width:1080px} img{max-width:100%;height:auto} blockquote{border-left:3px solid var(--accent);margin-left:0;padding:14px 22px;background:var(--surface)} .eq{font-size:.95em} .toc{font-size:.9em} @media print{body{background:white;color:black}.wrap{padding:0;max-width:none} h2{break-after:avoid}table,.eq{break-inside:avoid}}'
nav='<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>'+''.join(toc)+'</ol></nav>'
body=body.replace('<h2 id="verdict">',nav+'<h2 id="verdict">',1)
document='''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SD–UMD asymmetry: forensic physics and selection audit</title>
<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},svg:{fontCache:"global"}};</script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script>
<style>'''+css+'</style></head><body><main class="wrap">'+body+'<p class="footnote">Generated from the same Markdown and audited numerical tables. Equations use MathJax from a CDN; the Markdown retains the original TeX.</p></main></body></html>\n'
(PHYSICS/'report.html').write_text(document)
artifacts=['../plantillas/report.template.md','../../01_fisica/report.md','../../01_fisica/report.html','../figuras/selection_audit.svg','selection_closure_fits.csv','selection_paired_bootstrap.csv','selection_standardized.json','umd_selection_check.json']
(OUT/'report_manifest.json').write_text(json.dumps({f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in artifacts},indent=2))
assert not any(ord(c)<32 and c not in '\n\t\r' for c in text)
assert 'MATHTOKEN' not in document and 'PROTECTEDTOKEN' not in text
print('Built report.md, report.html, selection_audit.svg; words',len(text.split()),'math blocks',len(math))
