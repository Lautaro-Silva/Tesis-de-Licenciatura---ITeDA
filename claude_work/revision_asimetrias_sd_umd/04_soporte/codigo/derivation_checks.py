"""Exact sign/Jacobian, selection example, and scale checks used in report."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
th=np.deg2rad(35);D=7500.;r=1200.;phi=np.linspace(-np.pi,np.pi,1441)
def h(y):return float(2*simpson(y*np.cos(phi),x=phi)/simpson(y,x=phi))
L=np.hypot(D-r*np.tan(th)*np.cos(phi),r);ci=D*np.cos(th)/L;ap=np.pi*1.8**2*ci+2*1.8*1.2*np.sqrt(1-ci*ci)
L0=np.hypot(D,r);ci0=D*np.cos(th)/L0;si0=np.sqrt(1-ci0**2);eta=D*r*np.tan(th)/L0**2
kappa=(np.pi*1.8**2*ci0-2*1.8*1.2*ci0**2/si0)/(np.pi*1.8**2*ci0+2*1.8*1.2*si0)
# Poisson muon trigger plus independent electromagnetic trigger toy. Not fitted to MC.
mu=.6*(1+.19*np.cos(phi));e=.35*(1+.8*np.cos(phi));eps=1-(1-e)*np.exp(-mu);selected=mu/eps
legacy=pd.read_csv(OUT/'analytic_legacy.csv').query('response=="SDcount" and floor<1').iloc[0]
needed=(-.1-legacy.endpoint)/(1+.1*legacy.endpoint)
scales=dict(eta=eta,kappa_SD=kappa,aperture_SD_A1=h(ap),aperture_plate_A1=h(ci),inverse_square_A1=h(L**-2),required_effective_ADF_slope_no_loss=2+kappa+.1/eta,minimum_pure_cosine_added_fraction=(legacy.endpoint+.1)/(1+legacy.endpoint),missing_factor_endpoint=needed,required_scattering_variance_difference=4*abs(needed)*r*r/9,water_Cherenkov_momentum_GeV=.1056583755/np.sqrt(1.33**2-1),water_Cherenkov_total_energy_GeV=.1056583755/np.sqrt(1-1/1.33**2),early_distance_m=float(L[len(phi)//2]),late_distance_m=float(L[0]),toy_mu_before=h(mu),toy_mu_after=h(selected),toy_selection_A=h(eps),toy_UMD_independent_A=.13,toy_mean_mu_selected=float(simpson(selected,x=phi)/(2*np.pi)))
(OUT/'derivation_numbers.json').write_text(json.dumps(scales,indent=2));print(json.dumps(scales,indent=2))
base=Path('/opt/build/AugerOffline-icrc2025-test7')
names=['Framework/SEvent/StationSimData.cc','Framework/SEvent/StationSimData.h','Framework/SEvent/Station.cc','Framework/SDetector/Station.cc','Modules/General/RecDataWriterNG/SD2ADST.cc','Modules/SdSimulation/CachedShowerRegeneratorOG/CachedShowerRegenerator.cc','Modules/SdSimulation/G4StationSimulator/G4StationSimulator.cc','Modules/General/RecDataWriterNG/MD2ADST.cc','ADST/RecEvent/src/GenStation.h']
names+=['Modules/MdSimulation/MdOptoElectronicSimulator/MdOptoElectronicSimulator.cc','Framework/MEvent/Module.h','ADST/RecEvent/src/MdSimCounter.h','ADST/RecEvent/src/MdSimScintillator.h']
(OUT/'offline_source_manifest.json').write_text(json.dumps([dict(file=n,sha256=hashlib.sha256((base/n).read_bytes()).hexdigest()) for n in names],indent=2))
# Numeric normalization and geometry test, independent of the prior scripts.
alpha=np.linspace(0,np.pi/2,20001)
normalization=[]
for E in [.155,1.,10.]:
    k=E/.2;norm=1-np.exp(-k)*(1+k);f=k*k/(2*np.pi)*np.cos(alpha)*np.exp(-k*np.sin(alpha))/norm
    normalization.append(float(simpson(2*np.pi*np.sin(alpha)*f,x=alpha)))
assert np.max(np.abs(np.array(normalization)-1))<1e-9
assert L[len(phi)//2]<L[0] and ci[len(phi)//2]>ci[0]
# Check the first-order selection expression against exact Fourier integration.
ma=.6;ee=.35;aa=1e-5;bb=2e-5
mm=ma*(1+aa*np.cos(phi));ep=ee*(1+bb*np.cos(phi))
linear=aa-np.exp(-ma)*((1-ee)*ma*aa+ee*bb)/(1-(1-ee)*np.exp(-ma))
exact=h(mm/(1-(1-ep)*np.exp(-mm)))
assert abs(exact-linear)<1e-12
# Independent Cartesian verification of the solid-angle Jacobian dOmega/dr/dphi.
source=np.array([D*np.sin(th),0,D*np.cos(th)]);axis=source/D
def ray(rr,pp):
    x=np.array([rr*np.cos(pp)/np.cos(th),rr*np.sin(pp),0.])-source
    return x/np.linalg.norm(x)
checks=[]
for pp in [0.,.4,1.2,2.3,np.pi]:
    u=ray(r,pp);du_r=(ray(r+.01,pp)-ray(r-.01,pp))/.02
    du_p=(ray(r,pp+1e-5)-ray(r,pp-1e-5))/2e-5
    ll=np.hypot(D-r*np.tan(th)*np.cos(pp),r)
    got=abs(np.dot(u,np.cross(du_r,du_p)));expected=D*r/ll**3
    checks.append(abs(got/expected-1))
    assert abs(-u[2]-D*np.cos(th)/ll)<1e-12
    assert abs(-u@axis-(D-r*np.tan(th)*np.cos(pp))/ll)<1e-12
assert max(checks)<1e-7
def aperture(c):
    ll=np.hypot(D-r*np.tan(th)*c,r);co=D*np.cos(th)/ll
    return np.pi*1.8**2*co+2*1.8*1.2*np.sqrt(1-co*co)
slope=(np.log(aperture(1e-5))-np.log(aperture(-1e-5)))/2e-5
assert abs(slope-eta*kappa)<1e-9
(OUT/'unit_checks.json').write_text(json.dumps(dict(adf_integrals=normalization,early_shorter=True,early_more_vertical=True,selection_linearization_error=abs(exact-linear),solid_angle_jacobian_max_relative_error=max(checks),aperture_slope_numeric=slope,aperture_slope_analytic=eta*kappa),indent=2))
