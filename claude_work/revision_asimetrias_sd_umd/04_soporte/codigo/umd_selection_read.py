"""Bounded raw UMD counter-summary audit, including non-SD-reconstructed stations.
Uses existing ADST only; unsplit scintillator branch can be expensive.
"""
import ROOT,argparse,csv,math,json,time
from pathlib import Path
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
BASE=Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton')
ap=argparse.ArgumentParser();ap.add_argument('--files',type=int,default=1);args=ap.parse_args()
ROOT.gSystem.Load('/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so');ROOT.gErrorIgnoreLevel=ROOT.kError
keep=['event.fEventId','event.fGenShower.fEnergy','event.fGenShower.fCoreSiteCS*','event.fGenShower.fAxisCoreCS*','event.fSDEvent.fStations','event.fSDEvent.fStations.fId','event.fSDEvent.fGenStations','event.fSDEvent.fGenStations.fId','event.fMDEvent.fSimCounters','event.fMDEvent.fSimCounters.fId','event.fMDEvent.fSimCounters.fSdPartnerId','event.fMDEvent.fSimCounters.fScintillators','event.fMDEvent.fSimCounters.fAreaByModule']
rows=[];meta=[];start=time.monotonic()
for fname in sorted(BASE.glob('*.root'))[:args.files]:
    fv=ROOT.std.vector('string')();fv.push_back(str(fname));f=ROOT.RecEventFile(fv)
    ev=ROOT.RecEvent();geo=ROOT.DetectorGeometry();f.ReadDetectorGeometry(geo);f.SetBranchStatus('*',False)
    for b in keep:f.SetBranchStatus(b,True)
    f.SetBuffers(ev);i=0;sel=0;missing=0;nsd=0
    while f.ReadNextEvent()==ROOT.RecEventFile.eSuccess:
        i+=1;sh=ev.GetGenShower();th=sh.GetZenith();az=sh.GetAzimuth()
        if not 30<=math.degrees(th)<40:continue
        sel+=1;core=sh.GetCoreSiteCS();sd=ev.GetSDEvent();md=ev.GetMDEvent()
        for st in sd.GetSimStationVector():
            sid=st.GetId()
            if not 2000<sid<90000:continue
            pos=geo.GetStationPosition(sid);v=ROOT.TVector3(pos.X()-core.X(),pos.Y()-core.Y(),pos.Z()-core.Z());v.RotateZ(-az);v.RotateY(-th)
            r=math.hypot(v.X(),v.Y())
            if not 150<=r<1800:continue
            nsd+=1
            if not md.HasSimCounterBySdPartnerId(sid):missing+=1;continue
            co=md.GetSimCounterBySdPartnerId(sid);mods={}
            for sc in co.GetSimScintillatorVector():
                mid=sc.GetModuleId();ch=sc.GetChannelId()
                mm=mods.setdefault(mid,dict(mu=0,nsc=0,channels=set()))
                mm['mu']+=sc.GetNumberOfInjectedMuons();mm['nsc']+=1;mm['channels'].add(ch)
            for mid,mm in mods.items():
                rows.append(dict(source=fname.name,event_id=str(ev.GetEventId()),sdId=sid,counterId=co.GetId(),moduleId=mid,r=r,phi=math.atan2(v.Y(),v.X()),theta=math.degrees(th),logE=math.log10(sh.GetEnergy()),mu=mm['mu'],area=co.GetAreaByModule(mid),nsc=mm['nsc'],nchannels=len(mm['channels']),has_rec=int(sd.HasStation(sid))))
        if sel%25==0:print('selected',sel,'rows',len(rows),'elapsed',time.monotonic()-start,flush=True)
    meta.append(dict(file=fname.name,events=i,selected=sel,sd_occurrences=nsd,missing_sim_counter=missing));print(meta[-1],flush=True)
with (OUT/'umd_selection_raw.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'umd_selection_raw_summary.json').write_text(json.dumps(dict(files=meta,rows=len(rows),elapsed_s=time.monotonic()-start),indent=2));print('rows',len(rows),'seconds',time.monotonic()-start,flush=True)
