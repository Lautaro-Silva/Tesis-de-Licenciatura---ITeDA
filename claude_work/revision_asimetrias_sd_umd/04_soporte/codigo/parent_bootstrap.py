"""Conservative bootstrap grouping repeated library shower IDs across files."""
import json
from verify import load_data,OUT,VARS
from statistical_checks import bootstrap
d=load_data();z=d[d.r_core_MC.between(1050,1400,inclusive='left')].copy()
z['parent']=z.event_id.str.replace(r':Use_\d+$','',regex=True)
res=bootstrap(z,VARS,key='parent',B=600)
(OUT/'parent_cluster_bootstrap.json').write_text(json.dumps(res,indent=2));print(res)
