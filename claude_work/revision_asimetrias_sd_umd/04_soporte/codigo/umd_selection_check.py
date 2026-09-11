"""Validate selected UMD counts, without imputing absent unselected truth as zero."""
import json
import pandas as pd
from verify import load_data,OUT
u=pd.read_csv(OUT/'umd_selection_raw.csv')
d=load_data();d['source']=d.source.str.replace('.parquet','.root',regex=False)
p=d[d.source.isin(u.source.unique()) & d.r_core_MC.between(150,1800,inclusive='left')].copy()
z=p.merge(u[['source','event_id','sdId','moduleId','mu']],on=['source','event_id','sdId','moduleId'],how='left',validate='one_to_one')
missing=z.mu.isna()
# For retained parquet rows only, the reader's own convention yields zero when no
# corresponding simulation scintillator is present. This does NOT establish zero
# injection for non-reconstructed stations, whose channels may never be made.
assert (z.nMuones_MC==z.mu.fillna(0)).all()
raw=pd.read_csv(OUT/'adst_counts_fast.csv');raw=raw[raw.source.isin(u.source.unique())]
r=dict(files=int(u.source.nunique()),raw_module_records=len(u),non_SDrec_populated_module_records=int((u.has_rec==0).sum()),matched_parquet_module_rows=len(z),missing_retained_sim_module_rows=int(missing.sum()),nonzero_parquet_for_missing_module=int((z.loc[missing,'nMuones_MC']!=0).sum()),mu_count_mismatches=0,all_SD_occurrences=len(raw),non_SDrec_occurrences=int((raw.has_rec==0).sum()),total_retained_muons=float(z.nMuones_MC.sum()),conclusion='Unselected UMD truth is not recoverable from populated scintillator summaries in this pilot. Do not zero-fill absent unselected counters/modules.')
(OUT/'umd_selection_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
