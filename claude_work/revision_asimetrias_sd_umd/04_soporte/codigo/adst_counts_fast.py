"""Column-pruned raw ADST audit; validates against the full-branch pilot.
One process. No physics processing. --files selects the first N production files.
"""
import ROOT,argparse,csv,math,json,time
from pathlib import Path
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
BASE=Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton')
ap=argparse.ArgumentParser();ap.add_argument('--files',type=int,default=1);args=ap.parse_args()
ROOT.gSystem.Load('/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so');ROOT.gErrorIgnoreLevel=ROOT.kError
keep=['event.fEventId','event.fGenShower.fEnergy','event.fGenShower.fCoreSiteCS*','event.fGenShower.fAxisCoreCS*','event.fSDEvent.fStations','event.fSDEvent.fGenStations']
keep+=['event.fSDEvent.fStations.'+x for x in ['fId','fStatus','fTriggerBits','fTotalSignal']]
keep+=['event.fSDEvent.fGenStations.'+x for x in ['fId','fNumberOfMuons','fNumberOfElectrons','fNumberOfPhotons','fThinning','fUsedWeight','fInsideMinRadius']]
rows=[];meta=[];start=time.monotonic()
for fname in sorted(BASE.glob('*.root'))[:args.files]:
    fv=ROOT.std.vector('string')();fv.push_back(str(fname));f=ROOT.RecEventFile(fv)
    ev=ROOT.RecEvent();geo=ROOT.DetectorGeometry();f.ReadDetectorGeometry(geo);f.SetBranchStatus('*',False)
    for b in keep:f.SetBranchStatus(b,True)
    f.SetBuffers(ev);i=0;sel=0
    while f.ReadNextEvent()==ROOT.RecEventFile.eSuccess:
        i+=1;sh=ev.GetGenShower();th=sh.GetZenith();az=sh.GetAzimuth()
        if not 30<=math.degrees(th)<40:continue
        sel+=1;core=sh.GetCoreSiteCS();sd=ev.GetSDEvent()
        for st in sd.GetSimStationVector():
            sid=st.GetId()
            if not 2000<sid<90000:continue
            pos=geo.GetStationPosition(sid);v=ROOT.TVector3(pos.X()-core.X(),pos.Y()-core.Y(),pos.Z()-core.Z());v.RotateZ(-az);v.RotateY(-th)
            r=math.hypot(v.X(),v.Y())
            if not 150<=r<1800:continue
            has=bool(sd.HasStation(sid));rec=sd.GetStationById(sid) if has else None
            rows.append(dict(source=fname.name,event_id=str(ev.GetEventId()),sdId=sid,r=r,phi=math.atan2(v.Y(),v.X()),theta=math.degrees(th),logE=math.log10(sh.GetEnergy()),mu=st.GetNumberOfMuons(),em=st.GetNumberOfElectrons()+st.GetNumberOfPhotons(),has_rec=int(has),has_md=-1,signal=rec.GetTotalSignal() if has else '',candidate=int(rec.IsCandidate()) if has else 0,silent=int(rec.IsSilent()) if has else 0,thinning=st.GetThinning(),weight=st.GetUsedWeight(),inside_rmin=int(st.IsInsideRMin())))
    meta.append(dict(file=fname.name,events=i,selected=sel));print(meta[-1],flush=True)
with (OUT/'adst_counts_fast.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'adst_counts_fast_summary.json').write_text(json.dumps(dict(files=meta,rows=len(rows),elapsed_s=time.monotonic()-start),indent=2));print('rows',len(rows),'seconds',time.monotonic()-start,flush=True)
