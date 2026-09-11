"""Bounded read-only ADST audit. No reconstruction or simulation is launched.
Uses ROOT6, stdlib CSV; unnecessary detector trace branches are disabled.
"""
import ROOT
import argparse,csv,math,time,json
from pathlib import Path
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
BASE=Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton')
ap=argparse.ArgumentParser();ap.add_argument('--files',type=int,default=1);ap.add_argument('--max-events',type=int,default=2000);args=ap.parse_args()
ROOT.gSystem.Load('/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so');ROOT.gErrorIgnoreLevel=ROOT.kError
rows=[];audit=[];start=time.monotonic()
for fname in sorted(BASE.glob('*.root'))[:args.files]:
    fv=ROOT.std.vector('string')();fv.push_back(str(fname));f=ROOT.RecEventFile(fv)
    ev=ROOT.RecEvent();geo=ROOT.DetectorGeometry();f.ReadDetectorGeometry(geo)
    for branch in ['event.fMDEvent*','event.fSDEvent.fStations.fTraces*','event.fSDEvent.fGenStations.fPETimeDistr*']:
        f.SetBranchStatus(branch,False)
    f.SetBuffers(ev);i=0;accepted=0;particles=0;simstations=0
    while i<args.max_events and f.ReadNextEvent()==ROOT.RecEventFile.eSuccess:
        i+=1;sh=ev.GetGenShower();th=sh.GetZenith();az=sh.GetAzimuth()
        if i%200==0:print('events read',i,flush=True)
        if not 30<=math.degrees(th)<40:continue
        accepted+=1;core=sh.GetCoreSiteCS();sd=ev.GetSDEvent()
        for st in sd.GetSimStationVector():
            sid=st.GetId()
            # Physical SD IDs; UMD counterparts carry the additional 100000.
            if not 2000<sid<90000:continue
            simstations+=1;particles+=bool(st.HasParticles())
            try:pos=geo.GetStationPosition(sid)
            except Exception:continue
            v=ROOT.TVector3(pos.X()-core.X(),pos.Y()-core.Y(),pos.Z()-core.Z());v.RotateZ(-az);v.RotateY(-th)
            r=math.hypot(v.X(),v.Y());phi=math.atan2(v.Y(),v.X())
            if not 150<=r<1800:continue
            has=bool(sd.HasStation(sid));rec=sd.GetStationById(sid) if has else None
            rows.append(dict(source=fname.name,event_id=str(ev.GetEventId()),sdId=sid,r=r,phi=phi,theta=math.degrees(th),logE=math.log10(sh.GetEnergy()),mu=st.GetNumberOfMuons(),em=st.GetNumberOfElectrons()+st.GetNumberOfPhotons(),has_rec=int(has),has_md=-1,signal=rec.GetTotalSignal() if has else '',candidate=int(rec.IsCandidate()) if has else 0,silent=int(rec.IsSilent()) if has else 0,has_particles=int(st.HasParticles()),thinning=st.GetThinning(),weight=st.GetUsedWeight(),inside_rmin=int(st.IsInsideRMin())))
    audit.append(dict(source=fname.name,events_read=i,zenith_selected=accepted,infill_simstations=simstations,stations_with_particles=particles));print(audit[-1],flush=True)
with (OUT/'adst_station_audit.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
(OUT/'adst_audit_summary.json').write_text(json.dumps(dict(files=audit,rows=len(rows),elapsed_s=time.monotonic()-start),indent=2));print('rows',len(rows),'seconds',time.monotonic()-start,flush=True)
