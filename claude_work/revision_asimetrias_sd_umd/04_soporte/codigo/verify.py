"""Read-only, single-process forensic checks; outputs only in this directory.
Run from repository root: OPENBLAS_NUM_THREADS=1 venv/bin/python .../verify.py
"""
from pathlib import Path
import json, hashlib, time
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.integrate import simpson

from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
DATA=Path('/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17')
VARS=['nMuones_MC','sd_nMuons_MC','sd_nEM_MC','sdSignal_REC']

def fit(d,v,weighted=True):
    g=d.groupby('bin',observed=True)[v].agg(['mean','sem','size'])
    if len(g)!=12 or not np.isfinite(g['mean']).all(): return dict(A=None,error=None,n=len(d))
    y=g['mean'].to_numpy(); norm=y.mean(); x=-np.pi+(g.index.to_numpy()+.5)*2*np.pi/12
    sig=g['sem'].to_numpy()/norm
    if norm<=0 or (weighted and np.any(sig<=0)): return dict(A=None,error=None,n=len(d))
    p,c=curve_fit(lambda x,a:1+a*np.cos(x),x,y/norm,p0=[0],sigma=sig if weighted else None,absolute_sigma=weighted)
    return dict(A=float(p[0]),error=float(np.sqrt(c[0,0])),n=len(d))

def load_data():
    cols=['event_id','run_number','logE_MC','theta_MC','phi_MC','counterId','sdId','moduleId','module_status','is_sd_saturated','r_core_MC','r_umd_mc','phi_plane_euler_MC_true_core','phi_plane_darko_mc']+VARS
    frames=[]; manifest=[]
    for f in sorted(DATA.glob('*.parquet')):
        d=pd.read_parquet(f,columns=cols)
        manifest.append(dict(file=f.name,bytes=f.stat().st_size,rows=len(d)))
        d=d[(d.counterId>=100000)&d.theta_MC.between(30,40,inclusive='left')].copy()
        d['source']=f.name
        frames.append(d)
    d=pd.concat(frames,ignore_index=True)
    # Stored Euler has an extra +pi; undo it (same convention as plots_seccion_6).
    d['phi']=(d.phi_plane_euler_MC_true_core+2*np.pi)%(2*np.pi)-np.pi
    d['bin']=np.floor((d.phi+np.pi)/(2*np.pi)*12).astype(int).clip(0,11)
    d['event_key']=d.source+'|'+d.event_id.astype(str)
    (OUT/'data_manifest.json').write_text(json.dumps(manifest,indent=2))
    return d

def mc():
    d=load_data(); rows=[]
    for lo,hi in [(300,600),(650,950),(1050,1400),(1400,1800),(1050,1200),(1200,1350)]:
        z=d[d.r_core_MC.between(lo,hi,inclusive='left')]
        for name,q in [('modules',z),('station_once',z.drop_duplicates(['event_key','sdId'])),('silent',z[z.module_status=='silent']),('candidate',z[z.module_status=='candidate']),('SDsignal_zero',z[z.sdSignal_REC<=0]),('SDsignal_positive',z[z.sdSignal_REC>0])]:
            for v in VARS:
                for weighted in [True,False]:
                    rows.append(dict(lo=lo,hi=hi,sample=name,variable=v,weighted=weighted,**fit(q,v,weighted)))
    pd.DataFrame(rows).to_csv(OUT/'mc_fits.csv',index=False)
    z=d[d.r_core_MC.between(1050,1400,inclusive='left')].copy()
    agg=z.groupby('bin',observed=True).agg(n=('event_key','size'),events=('event_key','nunique'),r=('r_core_MC','mean'),logE=('logE_MC','mean'),theta=('theta_MC','mean'),SDmu=('sd_nMuons_MC','mean'),UMD=('nMuones_MC','mean'),EM=('sd_nEM_MC','mean'),signal=('sdSignal_REC','mean'),zero_signal=('sdSignal_REC',lambda s:np.mean(s<=0)),zero_sdmu=('sd_nMuons_MC',lambda s:np.mean(s==0)))
    agg.to_csv(OUT/'far_bin_diagnostics.csv')
    print('Rows',len(d),'events',d.event_key.nunique(),'far',len(z));print(agg.to_string())
    print(pd.crosstab(z.module_status,z.sdSignal_REC<=0).to_string())
    # Stratify primary energy, radius, theta: retain bins with all azimuths represented.
    strat=[]
    for e in sorted(d.logE_MC.round(2).unique()):
        q=z[np.isclose(z.logE_MC,e,atol=.006)]
        if len(q)<100: continue
        for v in VARS:strat.append(dict(energy=e,**fit(q,v),variable=v))
    pd.DataFrame(strat).to_csv(OUT/'energy_strata.csv',index=False)
    summary=dict(rows=len(d),events=d.event_key.nunique(),far_rows=len(z),status=z.module_status.value_counts().to_dict(),energies=d.logE_MC.describe().to_dict(),nan={v:int(z[v].isna().sum()) for v in VARS},duplicate_station_fraction=float(z.duplicated(['event_key','sdId']).mean()))
    (OUT/'mc_summary.json').write_text(json.dumps(summary,indent=2))
    return d

def analytical():
    theta=np.deg2rad(35); D=7500.;r=1200.;Q=.2;gamma=2.6
    phi=np.linspace(-np.pi,np.pi,721);delta=r*np.tan(theta)*np.cos(phi)
    L=np.hypot(D-delta,r); sa=r/L;ca=(D-delta)/L
    ci=D*np.cos(theta)/L;si=np.sqrt(1-ci**2)
    apertures={'perpendicular':np.ones_like(L),'SDcount':np.pi*1.8**2*ci+2*1.8*1.2*si,'UMDcount':ci}
    def harmonic(y):return float(2*simpson(y*np.cos(phi),x=phi)/simpson(y,x=phi))
    def endpoint(y):return float((y[360]-y[0])/(y[360]+y[0]))
    rows=[]
    for floor in [.155,1/np.cos(theta)]:
        E=np.geomspace(floor,2000,6001);k=E/Q;norm=-np.expm1(-k)-k*np.exp(-k)
        f=k[:,None]**2/(2*np.pi)*ca*np.exp(-k[:,None]*sa)/norm[:,None]
        y=simpson(E[:,None]**(-gamma)*f,x=E,axis=0)/L**2
        for name,a in apertures.items():rows.append(dict(model='legacy_no_transport',floor=floor,response=name,A1=harmonic(y*a),endpoint=endpoint(y*a)))
        # Median and low-energy fraction in the arriving integral of this untransported model.
        w=E**(-gamma)*f[:,180];cum=np.r_[0,np.cumsum((w[1:]+w[:-1])/2*np.diff(E))];cum/=cum[-1]
        rows[-1].update(median_production_E=float(np.interp(.5,cum,E)),fraction_below_1GeV=float(np.interp(1,E,cum)))
    # Exact monochromatic angular slope needed to reach SD -0.10, and transport diagnostics follow separately.
    result=dict(epsilon=float(r/D*np.tan(theta)),required_missing_additive=-.10-rows[1]['endpoint'],required_multiplicative_residual=float((-.10-rows[1]['endpoint'])/(1+.10*rows[1]['endpoint'])))
    pd.DataFrame(rows).to_csv(OUT/'analytic_legacy.csv',index=False)
    (OUT/'analytic_summary.json').write_text(json.dumps(result,indent=2));print(pd.DataFrame(rows).to_string(index=False));print(result)

if __name__=='__main__':
    t=time.monotonic(); analytical(); mc();print('Elapsed seconds',time.monotonic()-t)
