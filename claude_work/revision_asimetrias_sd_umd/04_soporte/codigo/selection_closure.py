"""Paired counterfactual sample-selection test, matched to parquet by exact IDs."""
import json
import numpy as np
import pandas as pd
from verify import load_data,OUT,fit
from statistical_checks import harmonic_means
RNG=np.random.default_rng(110926)
d=load_data();p=d.drop_duplicates(['source','event_id','sdId']).copy();p['source']=p.source.str.replace('.parquet','.root',regex=False)
f=OUT/'adst_counts_fast.csv';a=pd.read_csv(f if f.exists() else OUT/'adst_station_audit.csv')
a=a.merge(p[['source','event_id','sdId','sd_nMuons_MC','sd_nEM_MC','r_core_MC','phi','nMuones_MC']].rename(columns={'phi':'phi_parquet'}),on=['source','event_id','sdId'],how='left',indicator=True)
a['kept_parquet']=(a['_merge']=='both').astype(int);a['bin']=np.floor((a.phi+np.pi)/(2*np.pi)*12).astype(int).clip(0,11)
# Raw reads should exactly reproduce every stored SD truth count in overlapping rows.
matched=a[a.kept_parquet==1]
assert (matched.mu==matched.sd_nMuons_MC).all() and (matched.em==matched.sd_nEM_MC).all()
assert np.max(np.abs(matched.r-matched.r_core_MC))<1e-6
assert np.max(np.abs(np.angle(np.exp(1j*(matched.phi-matched.phi_parquet)))))<1e-8
summary={'matched_rows':len(matched),'mu_count_mismatches':0,'em_count_mismatches':0,'raw_rows':len(a),'files':a.source.nunique()}
fits=[];bins=[];paired=[]
for lo,hi in [(300,600),(650,950),(1050,1400),(1400,1800)]:
    q=a[a.r.between(lo,hi,inclusive='left')].copy()
    q['parent']=q.event_id.str.replace(r':Use_\d+$','',regex=True)
    for name,s in [('all_sim',q),('SDrec',q[q.has_rec==1]),('parquet',q[q.kept_parquet==1])]:
        for v in ['mu','em']:fits.append(dict(lo=lo,hi=hi,sample=name,variable=v,**fit(s,v,False)))
    for b,s in q.groupby('bin'):
        k=s[s.kept_parquet==1];eff=len(k)/len(s);mueff=k.mu.sum()/s.mu.sum() if s.mu.sum() else np.nan
        bins.append(dict(lo=lo,hi=hi,bin=b,n_all=len(s),n_kept=len(k),eff=eff,mu_eff=mueff,all_mu=s.mu.mean(),kept_mu=k.mu.mean(),closure=s.mu.mean()*mueff/eff if eff else np.nan))
    # Paired bootstrap: same resampled parent showers for all vs retained means.
    keys,ids=np.unique(q.parent.to_numpy(),return_inverse=True);b=q.bin.to_numpy();k=q.kept_parquet.to_numpy()
    arrays=[]
    for x in [np.ones(len(q)),q.mu.to_numpy(),k,k*q.mu.to_numpy()]:
        ar=np.zeros((len(keys),12));np.add.at(ar,(ids,b),x);arrays.append(ar)
    draws=[]
    for _ in range(800):
        w=RNG.multinomial(len(keys),np.full(len(keys),1/len(keys)));n,s,nk,sk=[w@ar for ar in arrays]
        if np.any(nk==0):continue
        aa=harmonic_means(s/n);ak=harmonic_means(sk/nk);draws.append([aa,ak,ak-aa])
    dr=np.array(draws)
    for j,name in enumerate(['all','kept','difference']):
        paired.append(dict(lo=lo,hi=hi,quantity=name,sd=float(dr[:,j].std(ddof=1)),low=float(np.quantile(dr[:,j],.025)),high=float(np.quantile(dr[:,j],.975)),clusters=len(keys),draws=len(dr)))
pd.DataFrame(fits).to_csv(OUT/'selection_closure_fits.csv',index=False);pd.DataFrame(bins).to_csv(OUT/'selection_closure_bins.csv',index=False);pd.DataFrame(paired).to_csv(OUT/'selection_paired_bootstrap.csv',index=False)
(OUT/'selection_match_summary.json').write_text(json.dumps(summary,indent=2));print(summary);print(pd.DataFrame(fits).to_string(index=False));print(pd.DataFrame(paired).to_string(index=False))
