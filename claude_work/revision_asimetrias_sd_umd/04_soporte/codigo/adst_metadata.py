"""Read only one ADST file header. Never export host/user or full configuration."""
import ROOT,json,xml.etree.ElementTree as ET
from pathlib import Path
from review_paths import TABLES as OUT, PHYSICS, FIGURES, TEMPLATES, CODE, REPO
BASE=Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton')
ROOT.gSystem.Load('/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so');ROOT.gErrorIgnoreLevel=ROOT.kError
v=ROOT.std.vector('string')();v.push_back(str(sorted(BASE.glob('*.root'))[0]));f=ROOT.RecEventFile(v);info=ROOT.FileInfo();f.ReadFileInfo(info)
result={'offline_version':str(info.GetOfflineVersion()),'adst_version':str(info.GetRecEventVersion())}
config=str(info.GetOfflineConfiguration())
allow={'forcedSDTrigger','saveParticles','saveParticleTypes','simulateUMD','useWeightDependentResamplingArea','muonWeightScale','muCapture','maxParticleTrackingTime','signalSeparationMode','clearParticleList','saveSimStations','energyCut','muonCut','maximumRadius','resamplingArea'}
try:
    root=ET.fromstring(config);result['configuration_values']=[{'tag':e.tag,'value':(e.text or '').strip(),'units':e.attrib.get('unit','')} for e in root.iter() if e.tag in allow]
except ET.ParseError:result['xml_parse_failed']=True
def branches(b):
    out=[]
    for x in b:
        name=str(x.GetName())
        if any(s in name for s in ['fMDEvent','fGenStations','fGenShower','fEventId']):out.append(name)
        out.extend(branches(x.GetListOfBranches()))
    return out
result['relevant_branch_names']=branches(f.GetEventTree().GetListOfBranches())
(OUT/'adst_metadata.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
