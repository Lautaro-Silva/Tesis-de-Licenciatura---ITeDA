
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
mpl.use('Agg') # para que pueda guardar imagenes usando byobu!!


## Funciona con python2 !!
import os
import sys

import numpy as np
from scipy.stats import chi2, norm
import ROOT # importa ROOT como una libreria de python2

# Funciones auxiliares
# to get MD counters list for simulations
def getCounterList(sevent, mevent):
    # sevent: SEvent object
    # mevent: MEvent object
    cList = []
    stationVector = sevent.GetStationVector()
    for station in stationVector:
        stationId = station.GetId()
        counterId = int( "10" + str(stationId) ) #  For simulations, counterID = stationID + 100000. e.g. station Id = 4001, then counterId = 104001 
        if mevent.HasCounter(counterId):
            cList.append(mevent.GetCounter(counterId))
    
    return cList

# To get modules list for simulations
def getModuleList(counter):
    # counter must be an MdRecCounter object
    possibleModules = range(100, 116) # for Data
    possibleModules = range(0, 6) # for simulations
    modules = []
    for modId in possibleModules:
        if counter.HasModule(modId):
            modules.append(counter.GetModule(modId))
    return modules



## Defino funcion que lee un ADST

def readADST_sim(fname):
    # fname (str): path al ADST
         

    # your offline enviourment needs to be exported
    AugerOfflineRoot = os.environ["AUGEROFFLINEROOT"]
    ROOT.gSystem.Load(os.path.join(AugerOfflineRoot, "lib/libRecEventKG.so"))
    
    # paths of ADST files
    DataFiles = fname if isinstance(fname, list) else [fname]

    files = ROOT.std.vector('string')()
    for datfile in DataFiles:
        files.push_back(datfile)
    
    
    #print(DataFiles)
    #print(list(files))
    # see https://web.ikp.kit.edu/augeroracle-doc/ADST/html/classes.html
    # for documentation of the ADST file formal and class structure

    # RecEventFile class
    file1 = ROOT.RecEventFile(files)

    # RecEvent class
    event = ROOT.RecEvent()

    # DetectorGeometry class
    geo = ROOT.DetectorGeometry()
    file1.ReadDetectorGeometry(geo)
    
    # loop over all events in ADST file1s
    file1.SetBuffers(event)
    
    
    nMod = 0 # ejemplo, cuento todos los modulos que estuvieron involucrados en el ADST
    
    ## Itero sobre todos los eventos de ese ADST
    
    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        
        
        #########################
        ## Extracting MC parameters
        
        MCShower = event.GetGenShower() # MC parameters

        
        ee = MCShower.GetEnergy()
        logee = np.log10(ee) # logE
        thetaMC = MCShower.GetZenith() * 180.  / np.pi # degrees
        pp = MCShower.GetShortPrimaryName() # primary
        phiMC = MCShower.GetAzimuth() * 180. / np.pi
        
        axisCoreCS = list( MCShower.GetAxisCoreCS() )
        axisSiteCS = list( MCShower.GetAxisSiteCS() )
        coreSiteCSMC = list( MCShower.GetCoreSiteCS() )
        coreUTMCSMC = list( MCShower.GetCoreUTMCS() ) # creo que la posicion importante es esta: la UTM
        
        print("---- MC parameters of %s ----" % fname.split("DST/")[1])
        print("primary = %s\tlogE = %.2f\ttheta = %.2f\tazimuth = %.2f\t" % (pp, logee, thetaMC, phiMC))
        print("axisCoreCS = %s\taxisSiteCS = %s" % (axisCoreCS, axisSiteCS))
        print("coreSiteCS = %s\t coreUTMCS = %s" % (coreSiteCSMC, coreUTMCSMC))
        
        
        #########################
        ## Extracting REC parameters
        
        sEvent = event.GetSDEvent()
        sShower = sEvent.GetSdRecShower()
        
        zenithAngleRad = sShower.GetZenith() # en radianes
        zenithAngle = zenithAngleRad * 180.0 / np.pi # paso a grados
        cosZenithSd = sShower.GetCosZenith()
        energy = sShower.GetEnergy()
        logE = np.log10(energy)
        azimuthAngleRad = sShower.GetAzimuth() # en radianes
        azimuthAngle = azimuthAngleRad * 180. / np.pi # paso a grados
        coreSiteCSRec = list( sShower.GetCoreSiteCS() )
        coreUTMCSRec = list( sShower.GetCoreUTMCS() ) # creo que la posicion importante es esta: la UTM
        
        print("---- REC parameters of %s ----" % fname.split("DST/")[1])
        print("logE = %.2f\ttheta = %.2f\tazimuth = %.2f\t" % (logE, zenithAngle, azimuthAngle))
        #print("axisCoreCS = %s\taxisSiteCS = %s" % (axisCoreCS, axisSiteCS))
        print("coreSiteCS = %s\t coreUTMCS = %s" % (coreSiteCSRec, coreUTMCSRec))
        print("\n")
        
        
        
        
        mEvent = event.GetMDEvent()
        
        counterList = getCounterList(sEvent, mEvent)
        
        # itero sobre contadores MD
        for counter in counterList:
            counterId = counter.GetId()
            #print("*) analyzing counter %i" % counterId)
            if counter.IsRejected() or counter.IsSaturated():
                continue
            
            sdId = counter.GetSdPartnerId()
            sdStation = sEvent.GetStationById(sdId) # en simulaciones, el counterId no es el mismo que la station Id
            sdSignal = sdStation.GetTotalSignal()
            
            ## WCD local trigger information
            triggerName = sdStation.GetStationTriggerName()
            
            ## Loop over modules involved
            for mod in modulesList:
                modId = mod.GetId()
                #print("     module %i" % modId)
                if mod.IsRejected() or mod.IsSaturated():
                    continue
                
                ## aca haces el analisis que quieras con los modulos del md
                nMod += 1
        
        
    return nMod
            
