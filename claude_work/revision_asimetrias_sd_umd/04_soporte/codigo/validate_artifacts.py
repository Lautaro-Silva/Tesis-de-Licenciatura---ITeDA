"""Final assertions for the full twenty-file result and generated documents."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import ast,json,re,hashlib
import numpy as np
import pandas as pd
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
checks={}
for f in CODE.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
checks['python_syntax']=True
a=pd.read_csv(OUT/'adst_counts_fast.csv')
match=json.loads((OUT/'selection_match_summary.json').read_text())
assert match['files']==20==a.source.nunique()
assert (a.has_rec==1).sum()==match['matched_rows']==51031
assert len(a)==match['raw_rows']==106280
assert match['mu_count_mismatches']==match['em_count_mismatches']==0
assert not a.duplicated(['source','event_id','sdId']).any()
checks['full_raw_sample_and_matching']=True
fits=pd.read_csv(OUT/'selection_closure_fits.csv')
for lo in [300,650,1050,1400]:
    for v in ['mu','em']:
        q=fits.query('lo==@lo and variable==@v').set_index('sample')
        assert q.loc['SDrec','n']==q.loc['parquet','n']
        assert abs(q.loc['SDrec','A']-q.loc['parquet','A'])<1e-12
q=fits.query('lo==1050 and variable=="mu"').set_index('sample')
assert q.loc['all_sim','A']>0 and q.loc['parquet','A']<0
checks['selection_sign_and_parquet_equality']=True
b=pd.read_csv(OUT/'selection_closure_bins.csv')
assert np.max(np.abs(b.kept_mu-b.closure))<1e-12
checks['exact_selection_identity']=True
boot=pd.read_csv(OUT/'selection_paired_bootstrap.csv')
assert boot.query('lo==1050 and quantity=="difference"').iloc[0].high<0
assert (boot.draws==800).all()
checks['paired_bootstrap']=True
std=json.loads((OUT/'selection_standardized.json').read_text())
assert std['cells']==28 and std['valid_bootstraps']==500
assert std['all']['A']>0>std['selected']['A']
checks['covariate_standardization']=True
u=json.loads((OUT/'umd_selection_check.json').read_text())
assert u['mu_count_mismatches']==0 and u['non_SDrec_populated_module_records']==0
assert u['non_SDrec_occurrences']>0
checks['umd_missing_truth_not_zero']=True
unit=json.loads((OUT/'unit_checks.json').read_text())
assert unit['solid_angle_jacobian_max_relative_error']<1e-7
assert max(abs(np.array(unit['adf_integrals'])-1))<1e-9
checks['geometry_and_adf']=True
txt=(PHYSICS/'report.md').read_text();ht=(PHYSICS/'report.html').read_text()
assert not any(t in txt+ht for t in ['{{selection','{{raw_','{{standardization','{{umd_audit','MATHTOKEN','PROTECTEDTOKEN'])
assert not any(ord(c)<32 and c not in '\n\r\t' for c in txt+ht)
assert '@import' not in ht and '9..144,500;' not in ht
assert txt.count('\\[')==txt.count('\\]') and txt.count('\\(')==txt.count('\\)')
checks['report_placeholders_and_math_delimiters']=True
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        for key in ['href','src']:
            if key in d:self.links.append(d[key])
parser=Links();parser.feed(ht);assert len(parser.ids)==len(set(parser.ids))
for link in parser.links:
    parts=urlsplit(link)
    if parts.scheme:continue
    if parts.path:assert (PHYSICS/unquote(parts.path)).exists(),link
    elif parts.fragment:assert parts.fragment in parser.ids,link
checks['html_local_links_and_anchors']=True
for f,sha in json.loads((OUT/'report_manifest.json').read_text()).items():
    assert hashlib.sha256((OUT/f).read_bytes()).hexdigest()==sha,f
checks['report_manifest']=True
(OUT/'validation_results.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
