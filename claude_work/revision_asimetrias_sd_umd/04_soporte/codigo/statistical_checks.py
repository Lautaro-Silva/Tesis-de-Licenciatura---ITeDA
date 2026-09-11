"""Single-process parquet robustness and raw-ADST selection closure."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from verify import load_data,fit,VARS
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
RNG=np.random.default_rng(914261)

def harmonic_means(means):
    x=-np.pi+(np.arange(12)+.5)*2*np.pi/12
    return float(np.sum((means/np.mean(means)-1)*np.cos(x))/np.sum(np.cos(x)**2))

def bootstrap(d,variables,key='event_key',B=400):
    # Resample complete reconstructed events (not independent modules/stations).
    keys,idx=np.unique(d[key].to_numpy(),return_inverse=True);b=d.bin.to_numpy()
    n=np.zeros((len(keys),12));np.add.at(n,(idx,b),1)
    sums=[]
    for v in variables:
        s=np.zeros_like(n);np.add.at(s,(idx,b),d[v].to_numpy());sums.append(s)
    vals=[]
    for _ in range(B):
        weight=RNG.multinomial(len(keys),np.ones(len(keys))/len(keys));den=weight@n
        vals.append([harmonic_means(weight@s/den) for s in sums])
    a=np.array(vals)
    return {v:dict(A=harmonic_means(s.sum(axis=0)/n.sum(axis=0)),sd=float(a[:,j].std(ddof=1)),low=float(np.quantile(a[:,j],.025)),high=float(np.quantile(a[:,j],.975)),clusters=len(keys)) for j,(v,s) in enumerate(zip(variables,sums))}

def parquet():
    d=load_data();z=d[d.r_core_MC.between(1050,1400,inclusive='left')].copy()
    res=bootstrap(z,VARS)
    z['cell']=(pd.cut(z.logE_MC,[17.49,17.75,18.01],labels=False)*100+pd.cut(z.r_core_MC,np.arange(1050,1401,50),right=False,labels=False)*10+pd.cut(z.theta_MC,[30,35,40],right=False,labels=False))
    counts=z.groupby(['cell','bin']).size().unstack(fill_value=0);good=counts.index[(counts>0).all(axis=1)];q=z[z.cell.isin(good)]
    prior=q.groupby('cell').size();prior=prior/prior.sum()
    std=[]
    for v in VARS:
        m=q.groupby(['cell','bin'])[v].mean().unstack();standard=prior@m
        std.append(dict(variable=v,A=harmonic_means(standard),rows=len(q),cells=len(prior)))
    pd.DataFrame(std).to_csv(OUT/'standardized_fits.csv',index=False)
    az=[]
    for j in range(4):
        q=z[(z.phi_MC%360>=90*j)&(z.phi_MC%360<90*(j+1))]
        for v in VARS:az.append(dict(quadrant=j,variable=v,**fit(q,v,False)))
    pd.DataFrame(az).to_csv(OUT/'primary_azimuth_fits.csv',index=False)
    (OUT/'cluster_bootstrap.json').write_text(json.dumps(res,indent=2));print(res);print(std)
    print('event examples',d.event_id.head().tolist())

def raw():
    path=OUT/'adst_station_audit.csv'
    if not path.exists():return
    d=pd.read_csv(path);d['bin']=np.floor((d.phi+np.pi)/(2*np.pi)*12).astype(int).clip(0,11);d['event_key']=d.source+'|'+d.event_id.astype(str)
    fits=[];details=[];boot={}
    for lo,hi in [(300,600),(650,950),(1050,1400),(1400,1800)]:
        q=d[d.r.between(lo,hi,inclusive='left')]
        for name,s in [('all_sim',q),('has_SDrec',q[q.has_rec==1]),('has_SDrec_MD',q[(q.has_rec==1)&(q.has_md==1)]),('no_SDrec',q[q.has_rec==0])]:
            for v in ['mu','em']:
                fits.append(dict(lo=lo,hi=hi,sample=name,variable=v,**fit(s,v,False)))
            if lo==1050 and len(s):boot[name]=bootstrap(s,['mu','em'])
        for b,s in q.groupby('bin'):
            kept=s[s.has_rec==1];p=len(kept)/len(s);pm=kept.mu.sum()/s.mu.sum() if s.mu.sum() else np.nan
            details.append(dict(lo=lo,hi=hi,bin=b,n_all=len(s),n_kept=len(kept),eff=p,mu_eff=pm,mu_all=s.mu.mean(),mu_kept=kept.mu.mean(),closure=s.mu.mean()*pm/p if p else np.nan,EM_all=s.em.mean(),EM_kept=kept.em.mean()))
    pd.DataFrame(fits).to_csv(OUT/'adst_selection_fits.csv',index=False);pd.DataFrame(details).to_csv(OUT/'adst_selection_bins.csv',index=False)
    (OUT/'adst_cluster_bootstrap.json').write_text(json.dumps(boot,indent=2))
    print(pd.DataFrame(fits).to_string(index=False));print(boot)

if __name__=='__main__':
    import sys
    if '--raw-only' not in sys.argv:parquet()
    raw()
