"""Deterministic sensitivity tests, NOT a calibrated air-shower generator.
Production spectrum and fixed source distances are explicitly assumed.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
M=.1056583755;CTA=658.65

def calculate(D=7500,Q=.2,turnover=0.,r=1200,threshold='angle',nE=1801,nphi=73,transport=True):
    th=np.deg2rad(35);phi=np.linspace(-np.pi,np.pi,nphi)
    L=np.hypot(D-r*np.tan(th)*np.cos(phi),r);sa=r/L;ca=np.sqrt(1-sa**2);ci=D*np.cos(th)/L
    A=np.pi*1.8**2*ci+2*1.8*1.2*np.sqrt(1-ci**2)
    # Exponential atmosphere: vertical overburden 860 g/cm2, scale height 7400 m.
    h=D*np.cos(th);X=860*(1-np.exp(-h/7400))/ci
    loss=.002*X if transport else 0*X
    out={}
    for det in ['SD','UMD']:
        groundmin=np.full_like(L,.155) if det=='SD' else np.ones_like(L)*(M+.002*540/(ci if threshold=='angle' else np.cos(th)))
        # Integrate in Ef, so the threshold is exact and Ei includes path-dependent losses.
        t=np.linspace(0,1,nE);Ef=groundmin[None,:]*(2000/groundmin[None,:])**t[:,None];Ei=Ef+loss
        momentum=np.sqrt(Ei**2-M**2);k=momentum/Q;norm=-np.expm1(-k)-k*np.exp(-k)
        f=k*k/(2*np.pi)*ca*np.exp(-k*sa)/norm
        if transport:
            # Exact numerical decay integral along straight path, with exponential air density.
            u=np.linspace(0,1,65);depth=860/ci[None,:]*(np.exp(-h*(1-u[:,None])/7400)-np.exp(-h/7400))
            integral=np.zeros_like(Ei)
            for j in range(len(u)-1):
                e1=Ei-.002*depth[j];e2=Ei-.002*depth[j+1]
                integral+=(u[j+1]-u[j])/2*(1/np.sqrt(e1*e1-M*M)+1/np.sqrt(e2*e2-M*M))
            survival=np.exp(-M/CTA*L*integral)
        else:survival=1
        w=(Ei+turnover)**(-2.6)*f*survival
        y=simpson(w*Ef*np.log(2000/groundmin),x=t,axis=0)/L**2*(A if det=='SD' else ci)
        out[det]=float(2*simpson(y*np.cos(phi),x=phi)/simpson(y,x=phi))
    return out

rows=[]
for D in [4000,7500,12000]:
    for Q in [.12,.2,.3]:
        for turnover in [0,.5,2.]:
            for threshold in ['fixed','angle']:
                rows.append(dict(D=D,Q=Q,turnover=turnover,threshold=threshold,**calculate(D,Q,turnover,threshold=threshold)))
pd.DataFrame(rows).to_csv(OUT/'transport_sensitivity.csv',index=False)
print(pd.DataFrame(rows).query('D==7500').to_string(index=False))
check=[]
for n in [901,1801,3601]:check.append(dict(nE=n,**calculate(nE=n)))
pd.DataFrame(check).to_csv(OUT/'transport_convergence.csv',index=False)
print('convergence',check)
