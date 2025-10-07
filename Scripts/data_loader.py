import os
import ROOT
import numpy as np

offline_lib = os.path.join(os.environ["AUGEROFFLINEROOT"], "lib")
ROOT.gSystem.Load(os.path.join(offline_lib, "libRecEventKG.so"))

fname = "ADST_SUPERAMIGA_230cm_Proton_e1850_t15_v2.root"
file1 = ROOT.RecEventFile([fname])
event = ROOT.RecEvent()
geo = ROOT.DetectorGeometry()
file1.ReadDetectorGeometry(geo)
file1.SetBuffers(event)

data = []

while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
    sEvent = event.GetSDEvent()
    sShower = sEvent.GetSdRecShower()
    zenith = sShower.GetZenith()
    energy = sShower.GetEnergy()
    data.append([zenith, energy])

np.save("adst_data.npy", np.array(data))
print("Datos guardados en adst_data.npy")
