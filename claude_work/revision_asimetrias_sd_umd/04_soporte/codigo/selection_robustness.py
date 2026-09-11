"""Common-covariate raw-ADST selection comparison and small-bin sign checks."""
import json
import numpy as np
import pandas as pd
from verify import OUT,fit
from statistical_checks import harmonic_means
a=pd.read_csv(OUT/'adst_counts_fast.csv');a['bin']=np.floor((a.phi+np.pi)/(2*np.pi)*12).astype(int).clip(0,11)
q=a[a.r.between(1050,1400,inclusive='left')].copy()
q['cell']=pd.cut(q.logE,[17.49,17.75,18.01],labels=False)*100+pd.cut(q.r,np.arange(1050,1401,50),right=False,labels=False)*10+pd.cut(q.theta,[30,35,40],right=False,labels=False)
c=q[q.has_rec==1].groupby(['cell','bin']).size().unstack(fill_value=0)
good=c.index[(c>0).all(axis=1)];q=q[q.cell.isin(good)].copy();cells,ci=np.unique(q.cell,return_inverse=True)
parents,pi=np.unique(q.event_id.str.replace(r':Use_\d+$','',regex=True),return_inverse=True)
b=q.bin.to_numpy();k=q.has_rec.to_numpy();m=q.mu.to_numpy()
arrays=[]
for x in [np.ones(len(q)),m,k,k*m]:
    z=np.zeros((len(parents),len(cells),12));np.add.at(z,(pi,ci,b),x);arrays.append(z.reshape(len(parents),-1))
prior=np.bincount(ci)/len(ci)
def statistic(w):
    n,s,nk,sk=[(w@z).reshape(len(cells),12) for z in arrays]
    if np.any(nk==0):return None
    aa=harmonic_means(prior@(s/n));ak=harmonic_means(prior@(sk/nk))
    return np.array([aa,ak,ak-aa])
point=statistic(np.ones(len(parents)));rng=np.random.default_rng(170926);draw=[]
for _ in range(500):
    # Positive exponential cluster weights avoid conditioning a multinomial
    # bootstrap on rare retained cells staying nonempty. Secondary uncertainty
    # diagnostic only; the unstandardized paired multinomial CI is primary.
    v=statistic(rng.exponential(1.,len(parents)))
    if v is not None:draw.append(v)
draw=np.asarray(draw)
res={'cells':len(cells),'rows':len(q),'parents':len(parents),'valid_bootstraps':len(draw),'method':'Positive exponential parent-cluster multiplier bootstrap; secondary diagnostic.','target':'Fixed empirical all-station covariate distribution; common support in all azimuth bins.'}
for j,name in enumerate(['all','selected','difference']):res[name]=dict(A=float(point[j]),sd=float(draw[:,j].std(ddof=1)),low=float(np.quantile(draw[:,j],.025)),high=float(np.quantile(draw[:,j],.975)))
(OUT/'selection_standardized.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
rows=[]
for lo,hi,tl,tu in [(1050,1200,30,40),(1200,1350,30,40),(1150,1250,34,36),(1050,1400,30,35),(1050,1400,35,40)]:
    z=a[a.r.between(lo,hi,inclusive='left')&a.theta.between(tl,tu,inclusive='left')]
    for label,s in [('all',z),('selected',z[z.has_rec==1])]:rows.append(dict(rlo=lo,rhi=hi,tlo=tl,thi=tu,sample=label,**fit(s,'mu',False)))
pd.DataFrame(rows).to_csv(OUT/'selection_narrow_bins.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
# Diagnostics of retained composition; q=1 toy is not an exact description.
stats=[]
for b,s in a[a.r.between(1050,1400,inclusive='left')].groupby('bin'):
    keep=s[s.has_rec==1]
    stats.append(dict(bin=int(b),eps=len(keep)/len(s),mu_eff=keep.mu.sum()/s.mu.sum(),mu_all=s.mu.mean(),mu_selected=keep.mu.mean(),zero_mu_all=float((s.mu==0).mean()),zero_mu_selected=float((keep.mu==0).mean()),EM_all=s.em.mean(),EM_selected=keep.em.mean()))
pd.DataFrame(stats).to_csv(OUT/'selection_composition.csv',index=False)
