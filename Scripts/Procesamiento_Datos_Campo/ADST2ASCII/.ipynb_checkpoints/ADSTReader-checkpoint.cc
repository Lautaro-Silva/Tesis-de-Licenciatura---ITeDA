#include "ADSTReader.h"

using namespace std;
using namespace utl;
using namespace fwk;

ADSTReader::ADSTReader()
{}

ADSTReader::~ADSTReader()
{}

VModule::ResultFlag ADSTReader::Init()
{
    return eSuccess;
}

VModule::ResultFlag ADSTReader::Run (evt::Event& event)
{

    //Setting the dataset
    Branch topBranch = CentralConfig::GetInstance()->GetTopBranch("ADSTReader");
    topBranch.GetChild("base").GetData(base);
    topBranch.GetChild("year").GetData(year);
    topBranch.GetChild("month").GetData(month);
    topBranch.GetChild("subset").GetData(subset);
    topBranch.GetChild("onlyT5").GetData(onlyT5);
    topBranch.GetChild("minLgE").GetData(minLgE);
    topBranch.GetChild("minLgSref").GetData(minLgSref);
    topBranch.GetChild("onlyFreeBeta").GetData(onlyFreeBeta);

    cout << "Running with XML config:" << endl;
    cout << "onlyT5: " << onlyT5 << " - minLgE: " << minLgE << " - LgSref: " << minLgSref << " - onlyFreeBeta: " << onlyFreeBeta << endl; 

    stringstream ss;
    vector<string> vInput;

    int nDays = 31;

    if (month == 4 || month == 6 || month == 9 || month == 11)
        nDays = 30;
    if (month == 2)
        nDays = 28;
    if (month == 2 && (year == 2020 || year == 2024))
        nDays = 29;

    for (int iday=1; iday<=nDays; ++iday) {
        ss << "/data5/ngonzale/" << base << "/Outputs/";
        ss << year << "/" << setfill('0') << setw(2) << month << "/ADST_" << subset << "_" << year << "_" << setfill('0') << setw(2) << month << "_" << setfill('0') << setw(2) << iday << ".root";
        vInput.push_back(ss.str());
        ss.str("");
    }

    nEvents = 0;

    //vInput.push_back("/data5/ngonzale/MdSd433DataReconstruction/ADST.root");

    //Reading the ADSTs
    for (unsigned int i=0; i<vInput.size(); ++i) {

        //Open ADST file
        RecEventFile adstFile(vInput.at(i).c_str());

        RecEvent event;
        auto eventPtr = &event;
        adstFile.SetBuffers(&eventPtr);
        cout << "Opened " << vInput.at(i) << " with " <<  adstFile.GetNEvents() << " events" << endl;
        cout << "**********" << endl;
    
        DetectorGeometry detGeom;
        adstFile.ReadDetectorGeometry(detGeom);

        //Loop over events
        while (adstFile.ReadNextEvent() == RecEventFile::eSuccess) {

            const auto& sdEvent = event.GetSDEvent();

            if (onlyT5) {

                if (!sdEvent.IsT5())
                    continue;
                else {
                    int nNeighUB = sdEvent.GetT5PriorActiveNeighbors().size();
                    int nNeighUUB = sdEvent.GetT5PriorActiveUUBNeighbors().size();

                    if (nNeighUB < 5 && nNeighUUB < 5)
                        continue;
                }
            }

            if (minLgE > log10(sdEvent.GetSdRecShower().GetEnergy()))
                continue;

            if (minLgSref > log10(sdEvent.GetSdRecShower().GetShowerSize()))
                continue;

            if (onlyFreeBeta && sdEvent.GetSdRecShower().GetBetaError() == 0)
                continue;

            ++nEvents;

            // Event general features
            const auto& sdRecShower = sdEvent.GetSdRecShower();
            auto& mdEvent = event.GetMDEvent();

            string eventId = event.GetEventId();
            int gps = sdEvent.GetGPSSecond();
            int ngps = sdEvent.GetGPSNanoSecond();

            if (sdEvent.IsT5()) {
                if (sdEvent.GetT5PriorActiveUUBNeighbors().size() >= 4)
                    ss << sdEvent.GetT5PriorActiveUUBNeighbors().size() << "T5PriorUUB";
                else if (sdEvent.GetT5PriorActiveNeighbors().size() >= 4)
                    ss << sdEvent.GetT5PriorActiveNeighbors().size() << "T5Prior";

                if (sdEvent.GetT5PostActiveUUBNeighbors().size() >= 4) {
                    ss << "_" << sdEvent.GetT5PostActiveUUBNeighbors().size() << "T5PostUUB";
                    ss << "_" << sdEvent.GetT5PostCoreTriangle() << "PostTriangle";
                }
                else if (sdEvent.GetT5PostActiveNeighbors().size() >= 4) {
                    ss << "_" << sdEvent.GetT5PostActiveNeighbors().size() << "T5Post";
                    ss << "_" << sdEvent.GetT5PostCoreTriangle() << "PostTriangle";
                }
            }
            if (!sdEvent.IsT5Prior() && !sdEvent.IsT5Posterior() && sdEvent.GetT4Trigger()) {
                string name = sdEvent.ReturnT4Name();
                name.erase(remove(name.begin(), name.end(), ' '), name.end());
                ss << name;
            }

            string arrayTrigger = ss.str().substr(0,ss.str().length());
            ss.str("");
            int triggered_SD = sdEvent.GetNumberOfCandidates();
            bool eventSaturation = sdEvent.IsSaturated();

            //Event geometry
            double theta = sdRecShower.GetZenith();
            double dTheta = sdRecShower.GetZenithError();
            double phi = sdRecShower.GetAzimuth();
            double dPhi = sdRecShower.GetAzimuthError();
            double corrThPhi = sdRecShower.GetZenithAzimuthCorrelation();

            const auto& core = sdRecShower.GetCoreUTMCS();
            double easting = core.X();
            double dEasting = sdRecShower.GetCoreEastingError();
            double northing = core.Y();
            double dNorthing = sdRecShower.GetCoreNorthingError();
            double corrXY = sdRecShower.GetCoreNorthingEastingCorrelation();

            double axisX = sdRecShower.GetAxisSiteCS().X();
            double axisY = sdRecShower.GetAxisSiteCS().Y();
            double axisZ = sdRecShower.GetAxisSiteCS().Z();

            double hottestS = 0;
            int hottestId = 0;

            for (const auto& station : sdEvent.GetStationVector()) {

                int sId = station.GetId();

                if (station.IsRejected()) {
                    if (sId != 30) continue;
                    else {
                        string reason = station.GetRemovalReason();
                        replace(begin(reason),end(reason), ' ', '_');
                        if (!(gps < 1417824018 && reason == "off-grid"))
                            continue;
                    }
                }

                double signal = station.GetTotalSignal();

                if (signal > hottestS) {
                    hottestS = station.GetTotalSignal();
                    hottestId = sId;
                }

            }

            double smallestr = 9999;
            int closestId = 0;

            for (const auto& station : detGeom.GetStations()) {

                int sId = station.first;

                if (!IsStationInBase(sId)) continue;

                auto& stationPos = station.second;
                double corex = sdRecShower.GetCoreSiteCS().X();
                double corey = sdRecShower.GetCoreSiteCS().Y();
                double r = sqrt(pow(stationPos.X()-corex,2) + pow(stationPos.Y()-corey,2));

                if (closestId ==  -1 || r < smallestr) {
                    closestId = sId;
                    smallestr = r;
                }

                /*if (r < smallestDistance) {
                    smallestDistance = r;
                    closestId = sId;
                }*/

            }

            //Event energy
            double beta = sdRecShower.GetBeta();
            double dBeta = sdRecShower.GetBetaError();
            double gamma = sdRecShower.GetGamma();
            double dGamma = sdRecShower.GetGammaError();
            double Sopt = sdRecShower.GetShowerSize();
            double dSopt = sdRecShower.GetShowerSizeError();
            double Sref = sdRecShower.GetAttShowerSize();

            double chi2 = sdRecShower.GetLDFChi2();
            double ndf = sdRecShower.GetLDFNdof();
            double likelihood =  sdRecShower.GetLDFLikelihood();

            double E = sdRecShower.GetEnergy()/1.e17;
            double dE = sdRecShower.GetEnergyError()/1.e17;

            // Streaming the event quantities
            if (eventFlags.id) cout << "Event ID = " << eventId << endl;
            if (eventFlags.gps) cout << "GPS = " << gps << endl;
            if (eventFlags.ngps) cout << "nGPS = " << ngps << endl;
            if (eventFlags.arrayTrigger) cout << "Array trigger = " << arrayTrigger << endl;
            if (eventFlags.triggeredSD) cout << "Triggered SD = " << triggered_SD << endl;
            if (eventFlags.saturation) cout << "Event saturation (LowGain) = " << eventSaturation << endl;

            if (eventFlags.theta) cout << "Theta (deg) = " << theta/deg << " +/- " << dTheta/deg << endl;
            if (eventFlags.phi) cout << "Phi (deg) = " << phi/deg << " +/- " << dPhi/deg << endl;
            if (eventFlags.corrThetaPhi) cout << "Correlation Theta-Phi = " << corrThPhi << endl;
            if (eventFlags.easting) cout << "Easting (m) = " << fixed << easting << " +/- " << dEasting << endl;
            if (eventFlags.northing) cout << "Northing (m) = " << fixed << northing << " +/- " << dNorthing << endl;
            if (eventFlags.corrNorthingEasting) cout << "Correlation Northing-Easting = " << defaultfloat << corrXY << endl;
            if (eventFlags.axis) cout << "Axis components = " << axisX << " " << axisY << " " << axisZ << endl;
            if (eventFlags.hottestId) cout << "Hottest ID = " << hottestId << endl;
            if (eventFlags.closestId) cout << "Closest ID = " << closestId << endl;
            
            if (eventFlags.LDFBeta) cout << "LDF beta = " << beta << " +/- " << dBeta << endl;
            if (eventFlags.LDFGamma) cout << "LDF gamma = " << gamma << " +/- " << dGamma << endl;
            if (eventFlags.S300) cout << "Sopt (VEM) = " << Sopt << " +/- " << dSopt << endl;
            if (eventFlags.S30) cout << "Sref (VEM) = " << Sref << endl;
            if (eventFlags.chi2) cout << "Chi2 = " << chi2 << endl;
            if (eventFlags.Ndf) cout << "NDF = " << ndf << endl;
            if (eventFlags.likelihood) cout << "Likelihood = " << likelihood << endl;
            if (eventFlags.E) cout << "E (10^17 eV) = " << E << " +/- " << dE << endl;

            //Triggered stations
            for (const auto& station : sdEvent.GetStationVector()) {

                unsigned int sId = station.GetId();

                if (!IsStationInBase(sId)) continue;

                //Avoiding off-grid and ub or uub stations (depends on the input)
                if (station.IsRejected())
                    continue;

                string trigAlgo = station.GetStationTriggerName();
                trigAlgo.erase(remove(trigAlgo.begin(),trigAlgo.end(),' '),trigAlgo.end());
                int saturationLevel = 0;
                if (station.IsHighGainSaturated())
                    saturationLevel = 1;
                if (station.IsLowGainSaturated())
                    saturationLevel = 2;
                if (station.IsSmallPMTSaturated())
                    saturationLevel = 3;

                double r = station.GetSPDistance()/m;
                double dr = station.GetSPDistanceError()/m;
                double azi = station.GetAzimuthSP()/deg;
                double signal = station.GetTotalSignal();
                double dSignal = station.GetTotalSignalError();
                double recovSignal = -1;
                double dRecovSignal = -1;
                if (!station.IsUUB()) {
                    recovSignal = station.GetRecoveredSignal();
                    dRecovSignal = station.GetRecoveredSignalError();
                }

                //Average of the three LPMTs
                map<int,double> mapLPMTs;
                double LPMTSignal = 0;
                int LPMTs = 0;
                for (int j=1; j<=3; ++j) {
                    if (station.HasPMTTraces(eTotalTrace,j)) {
                        const auto& traces = station.GetPMTTraces(eTotalTrace,j);
                        double pmtSignal = traces.GetVEMSignal();
                        mapLPMTs[j] = pmtSignal;
                        LPMTSignal += pmtSignal;
                        ++LPMTs;
                    }
                    else
                        mapLPMTs[j] = 0;
                }
                LPMTSignal /= LPMTs;

                //SPMT sector
                double SPMTSignal = station.GetPMTTraces(eTotalTrace,4).GetVEMSignal();
                double dSPMTSignal = 0;

                // From GAP2022_018
                // based on analysis of small showers signals
                double SPMTBeta = station.GetPMTTraces(eTotalTrace,4).GetSmallPMTCalibBeta();
                constexpr double a = 0.055;
                constexpr double b = 1.7;
                //const double shFluctuations = b * sqrt(SPMTSignal);
                const double shFluctuations = b * sqrt(SPMTSignal) * SPMTBeta;
                const double detResolution = a * SPMTSignal;
                dSPMTSignal = sqrt(pow(shFluctuations,2) + pow(detResolution,2));

                //UMD sector
                double Nmu = -2;
                double area = 0;

                if (mdEvent.HasCounterBySdPartnerId(sId)) {
                    Nmu = -1;

                    MdRecCounter* counter = mdEvent.GetCounterBySdPartnerId(sId);
                    if (!counter->IsRejected()) {
                        Nmu = counter->GetNumberOfMuons();
                        area = counter->GetActiveArea()/m2 * cos(theta);
                    }
                    else
                        cout << "Counter " << sId << " rejected" << endl;
                }

                //SSD sector
                double MIP = -1;
                double dMIP = 0;

                if (station.HasScintillator()) {
                    const auto& scint = station.GetScintillator();
                    MIP = scint.GetTotalSignal();
                    dMIP = scint.GetTotalSignalError();

                    // If uncertainty is not saved in the ADST, calculate it here
                    if (dMIP == 0) {
                        double a = 1.449;
                        double b = 0.175;
                        double factor = a*(1 + b*(1/cos(theta) - 1.22));
                        double shFluctuations = factor * sqrt(MIP);
                        double baseFluctuations = 0.04;
                        dMIP = sqrt(pow(shFluctuations,2) + pow(baseFluctuations,2));
                    }

                }

                if (stationFlags.id) cout << "Station = " << sId;
                if (stationFlags.trig) cout << " # Trig = " << trigAlgo;
                if (stationFlags.saturation) cout << " # Saturation flag = " << saturationLevel;
                if (stationFlags.r) cout << " # r (m) = " << r << " +/- " << dr;
                if (stationFlags.phi) cout << " # Phi (deg) = " << azi;
                if (stationFlags.S) cout << " # S (VEM) = " << signal << " +/- " << dSignal;
                if (stationFlags.recoveredS) cout << " # S recov. (VEM) = " << recovSignal << " +/- " << dRecovSignal;
                if (stationFlags.LPMT1) cout << " # LPMT1 (VEM) = " << mapLPMTs[1];
                if (stationFlags.LPMT2) cout << " # LPMT2 (VEM) = " << mapLPMTs[2];
                if (stationFlags.LPMT3) cout << " # LPMT3 (VEM) = " << mapLPMTs[3];
                if (stationFlags.SPMTS) cout << " # SPMT S (VEM) = " << SPMTSignal << " +/- " << dSPMTSignal;
                if (stationFlags.SPMTBeta) cout << " # SPMT calib. beta = " << SPMTBeta;
                if (stationFlags.Nmu) cout << " # Nmu = " << Nmu;
                if (stationFlags.area) cout << " # Area (m2) = " << area;
                if (stationFlags.SsdS) cout << " # SSD (MIP) = " << MIP << " +/- " << dMIP;
                cout << endl;

            }//station vector

            // Rejected stations
            for (const auto& station : sdEvent.GetStationVector()) {
        
                unsigned int sId = station.GetId();

                if (!IsStationInBase(sId)) continue;

                if (station.IsRejected()) {
                    string reason = station.GetRemovalReason();
                    replace(begin(reason),end(reason), ' ', '_');
                    cout << "RejStation = " << sId << " # Rejection reasons = " << reason << endl;
                    continue;
                }

            }

            for (const auto& badStation : sdEvent.GetBadStationVector()) {

                int bsId = badStation.GetId();

                if (!IsStationInBase(bsId)) continue;

                bool found = false;

                for (const auto& station : sdEvent.GetStationVector()) {
                    int sId = station.GetId();
                    if (bsId == sId) {
                        found = true;
                        break;
                    }
                }

                if (!found)
                    cout << "RejStation = " << badStation.GetId() << " # Rejection reasons = " << FindRejectionFlags(badStation.GetReason()) << endl;
            }

            cout << "**********" << endl;

        } //loop in events

    } //loop in observer files

    return eSuccess;

}

VModule::ResultFlag ADSTReader::Finish()
{
    stringstream ss;

    if (nEvents > 0) {
        ss << "./Outputs/";

        if (base == "SdInfillDataReconstruction")
            ss << "750/";

        if (base == "SdDataReconstruction")
            ss << "1500/";

        ss << subset << "_" << year << "_" << setfill('0') << setw(2) << month;
        rename("log",ss.str().c_str());
        ss.str("");

        cout << "Event written to log: " << nEvents << endl;
    }

    return eSuccess;
}

//Need this function because it is only implemented for RecStation, not for BadStation
string ADSTReader::FindRejectionFlags (int rejStatus)
{
    stringstream ssRet;

    if (rejStatus & ERejectionStatus::eLightning)
        ssRet << "lightning_";
    if (rejStatus & ERejectionStatus::eBadCompress)
        ssRet << "badCompress_";
    if (rejStatus & ERejectionStatus::eOutOfTime)
        ssRet << "outOfTime_";
    if (rejStatus & ERejectionStatus::eOffGrid)
        ssRet << "offGrid_";
    if (rejStatus & ERejectionStatus::eDenseArray)
        ssRet << "denseArray_";
    if (rejStatus & ERejectionStatus::eRandomRejection)
        ssRet << "random_";
    if (rejStatus & ERejectionStatus::eEngineeringArray)
        ssRet << "engArray_";
    if (rejStatus & ERejectionStatus::eMCInnerRadiusCut)
        ssRet << "innerRadiusCut_";
    if (rejStatus & ERejectionStatus::eNoRecData)
        ssRet << "noRecData_";
    if (rejStatus & ERejectionStatus::eLonely)
        ssRet << "lonely_";
    if (rejStatus & ERejectionStatus::eNoTrigger)
        ssRet << "noTrigger_";
    if (rejStatus & ERejectionStatus::eErrorCode)
        ssRet << "errorCode_";
    if (rejStatus & ERejectionStatus::eNoCalibData)
        ssRet << "noCalibData_";
    if (rejStatus & ERejectionStatus::eNoGPSData)
        ssRet << "noGpsData_";
    if (rejStatus & ERejectionStatus::eBadCalib)
        ssRet << "badCalib_";
    if (rejStatus & ERejectionStatus::eRegularMC)
        ssRet << "regular C_";
    if (rejStatus & ERejectionStatus::eTOTdRejected)
        ssRet << "TOTdRejected_";
    if (rejStatus & ERejectionStatus::eMoPSRejected)
        ssRet << "MoPSRejected_";
    if (rejStatus & ERejectionStatus::eNotAliveT2)
        ssRet << "notAliveT2_";
    if (rejStatus & ERejectionStatus::eNotAliveT120)
        ssRet << "notAliveT120_";
    if (rejStatus & ERejectionStatus::eBadSilent)
        ssRet << "badSilent_";
    if (rejStatus & ERejectionStatus::eAllPMTsBad)
        ssRet << "allPMTsBad_";
    if (rejStatus & ERejectionStatus::eElectronicsType)
        ssRet << "electronics_";

    string str = ssRet.str().substr(0, ssRet.str().length()-1);
    
    return str;

}

bool ADSTReader::IsFromSd433 (int id)
{

    if (vSd433Stations.size() == 0)
        vSd433Stations = {1764, 11, 12, 13, 47, 97, 98, 1874, 30, 99, 28, 1769, 54, 1765, 50, 734, 42, 1773, 27, 1622, 29, 688};

    for (unsigned int i=0; i<vSd433Stations.size(); ++i) {
        if (vSd433Stations.at(i) == id)
            return true;
    }

    return false;

}

bool ADSTReader::IsFromSd750 (int id)
{
    if (vSd750Stations.size() == 0)
        vSd750Stations = {607, 608, 609, 615, 635, 639, 643, 651, 659, 660, 663, 669, 688, 695, 698, 701, 702, 707, 710, 734, 736, 819, 1570, 1574, 1622, 1625, 1627, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1788, 1790, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1823, 1825, 1826, 1827, 1829, 1830, 1831, 1832, 1833, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845};

    for (unsigned int i=0; i<vSd750Stations.size(); ++i) {
        if (vSd750Stations.at(i) == id)
            return true;
    }

    return false;

}

bool ADSTReader::IsFromSd1500 (int id)
{
    if (vSdStationsNotFrom1500.size() == 0)
        vSdStationsNotFrom1500 = {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 120, 136, 185, 186, 335, 685, 854, 858, 1241, 1242, 1243, 1249, 1252, 1253, 1255, 1256, 1257, 1258, 1259, 1265, 1266, 1267, 1268, 1299, 1300, 1311, 1325, 1328, 1329, 1331, 1333, 1341, 1342, 1343, 1344, 1351, 1570, 1574, 1575, 1618, 1622, 1625, 1627, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776, 1777, 1788, 1790, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1823, 1825, 1826, 1827, 1829, 1830, 1831, 1832, 1833, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1847, 1874, 1891};
    
    for (unsigned int i=0; i<vSdStationsNotFrom1500.size(); ++i) {
        if (vSdStationsNotFrom1500.at(i) == id)
            return false;
    }

    return true;

}

bool ADSTReader::IsStationInBase (int sId) {
    if (base == "MdSd433DataReconstruction") return IsFromSd433(sId);
    if (base == "SdInfillDataReconstruction") return IsFromSd750(sId);
    if (base == "SdDataReconstruction") return IsFromSd1500(sId);
    return false;
}

