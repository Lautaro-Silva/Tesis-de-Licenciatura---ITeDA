#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <sstream>
#include <iomanip>
#include <boost/tuple/tuple.hpp>
#include <cstdio>
#include <algorithm>

#include <fwk/CentralConfig.h>
#include <fwk/VModule.h>
#include <fwk/RandomEngineRegistry.h>

#include <utl/ErrorLogger.h>
#include <utl/TimeStamp.h>
#include <utl/UTCDateTime.h>
#include <utl/ErrorLogger.h>
#include <utl/Reader.h>

#include <RecEvent.h>
#include <RecEventFile.h>
#include <DetectorGeometry.h>
#include <StationStatus.h>
#include <MDEventADST.h>

#include <TFile.h>
#include <TProfile.h>
#include <TRandom3.h>

using namespace std;

class ADSTReader : public fwk::VModule
{
    public:
    ADSTReader();
    virtual ~ADSTReader();

    string base;
    int year, month, day0, day1;
    string subset;
    bool onlyT5;
    double minLgE;
    double minLgSref;
    bool onlyFreeBeta;

    int nEvents;

    string FindRejectionFlags (int);

    vector<int> vSd433Stations, vSd750Stations, vSdStationsNotFrom1500;
    bool IsFromSd433 (int);
    bool IsFromSd750 (int);
    bool IsFromSd1500 (int);

    bool IsStationInBase (int);

    fwk::VModule::ResultFlag Init();
    fwk::VModule::ResultFlag Run(evt::Event& event);
    fwk::VModule::ResultFlag Finish();

    private:

    struct EventFlags {
        bool id           = true;
        bool gps          = true;
        bool ngps         = false;
        bool arrayTrigger = true;
        bool triggeredSD  = false;
        bool saturation   = false;

        bool theta               = true;
        bool phi                 = false;
        bool corrThetaPhi        = false;
        bool easting             = false;
        bool northing            = false;
        bool corrNorthingEasting = false;
        bool axis                = false;
        bool hottestId           = false;
        bool closestId           = false;

        bool LDFBeta    = false;
        bool LDFGamma   = false;
        bool S300       = false;
        bool S30        = true;
        bool chi2       = false;
        bool Ndf        = false;
        bool likelihood = false;
        bool E          = true;
    };

    struct StationFlags {
        bool id         = true;
        bool trig       = false;
        bool saturation = false;
        bool r          = true;
        bool phi        = true;
        bool S          = false;
        bool recoveredS = false;
        bool LPMT1      = false;
        bool LPMT2      = false;
        bool LPMT3      = false;
        bool SPMTS      = false;
        bool SPMTBeta   = false;
        bool Nmu        = true;
        bool area       = true;
        bool SsdS       = true;
    };

    EventFlags eventFlags;
    StationFlags stationFlags;

    REGISTER_MODULE ("ADSTReader",ADSTReader);

};



