"""Readable, serial extraction of SD simulation counts from EXISTING ADST files.

This is NOT CORSIKA, Geant4, or reconstruction. It reads saved objects using the
Offline/ROOT6 dictionaries. It deliberately does NOT require HasStation before
reading a simulated station's count. See the companion notebook for the analysis.

Safety: writes only into a NEW subdirectory of this walkthrough folder. It never
overwrites the forensic-review cache, the parquet, a ROOT input, or the thesis.
The full extraction is opt-in; default is one file and fifty saved events.
"""
import argparse
import csv
import math
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = Path(
    '/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/'
    'MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton'
)
DEFAULT_LIBRARY = Path('/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so')


def shower_plane_coordinates(position, core, zenith, azimuth):
    """Return r [m] and early/late phi [rad] from SITE-coordinate positions.

    This explicitly implements RotateZ(-azimuth), then RotateY(-zenith), as in
    the original audited reader. No reconstructed core enters this calculation.
    The resulting phi=0 points early. We check it against the parquet separately.
    """
    dx = position.X() - core.X()
    dy = position.Y() - core.Y()
    dz = position.Z() - core.Z()
    x_after_z = math.cos(azimuth) * dx + math.sin(azimuth) * dy
    y_after_z = -math.sin(azimuth) * dx + math.cos(azimuth) * dy
    x_plane = math.cos(zenith) * x_after_z - math.sin(zenith) * dz
    y_plane = y_after_z
    return math.hypot(x_plane, y_plane), math.atan2(y_plane, x_plane)


def enable_needed_branches(reader):
    """Read counts/positions/status, not PMT traces or per-particle lists.

    This only reduces file I/O. Branches below describe the existing ROOT schema;
    they are not physics cuts. Both reconstructed and simulated station vectors
    are enabled, including their IDs so that HasStation can answer correctly.
    """
    branches = [
        'event.fEventId',
        'event.fGenShower.fEnergy',
        'event.fGenShower.fCoreSiteCS*',
        'event.fGenShower.fAxisCoreCS*',
        'event.fSDEvent.fStations',
        'event.fSDEvent.fGenStations',
    ]
    branches += [
        'event.fSDEvent.fStations.' + name
        for name in ['fId', 'fStatus', 'fTriggerBits', 'fTotalSignal']
    ]
    branches += [
        'event.fSDEvent.fGenStations.' + name
        for name in ['fId', 'fNumberOfMuons', 'fNumberOfElectrons',
                     'fNumberOfPhotons', 'fThinning', 'fUsedWeight',
                     'fInsideMinRadius']
    ]
    reader.SetBranchStatus('*', False)
    for branch in branches:
        reader.SetBranchStatus(branch, True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--library', type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument('--max-files', type=int, default=1)
    parser.add_argument('--max-events', type=int, default=50,
                        help='Saved events per file; 0 means all. Default: 50.')
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='NEW directory inside this walkthrough folder.')
    args = parser.parse_args()
    if not 1 <= args.max_files <= 20 or args.max_events < 0:
        parser.error('Use 1..20 files and max-events >= 0; extraction is serial.')
    output = args.output_dir.resolve()
    if output == HERE or not output.is_relative_to(HERE):
        parser.error('Output must be a NEW subdirectory inside ' + str(HERE))
    if output.exists():
        parser.error('Output already exists. Choose another name; nothing overwritten.')
    files = sorted(args.input_dir.glob('*.root'))[:args.max_files]
    if len(files) != args.max_files:
        parser.error('Not enough input ROOT files in the selected directory.')

    # Delayed import makes --help usable without ROOT. The notebook launches this
    # script with the matching ROOT6 interpreter, separate from its pandas kernel.
    import ROOT
    if not args.library.is_file():
        raise FileNotFoundError(args.library)
    status = ROOT.gSystem.Load(str(args.library))
    if status < 0:
        raise RuntimeError('Cannot load the ADST dictionaries. Check ROOT6/Offline.')
    print('ROOT version:', ROOT.gROOT.GetVersion(), flush=True)
    print('ADST dictionary:', args.library, flush=True)
    print('Only reading existing files; no reconstruction is run.', flush=True)

    output.mkdir(parents=True, exist_ok=False)
    fields = ['source', 'event_id', 'sdId', 'r', 'phi', 'theta', 'logE',
              'mu', 'em', 'has_rec', 'has_md', 'signal', 'candidate', 'silent',
              'thinning', 'weight', 'inside_rmin']
    records = []
    total_rows = 0
    started = time.monotonic()
    with (output / 'stations.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for filename in files:
            print('Reading:', filename.name, flush=True)
            file_started = time.monotonic()
            names = ROOT.std.vector('string')()
            names.push_back(str(filename))
            reader = ROOT.RecEventFile(names)
            event = ROOT.RecEvent()
            geometry = ROOT.DetectorGeometry()
            reader.ReadDetectorGeometry(geometry)
            enable_needed_branches(reader)
            reader.SetBuffers(event)
            events_read = events_selected = rows_written = 0

            # We count SAVED ADST events. Events that never entered the ADST are
            # outside this comparison and cannot be reconstructed from this file.
            while args.max_events == 0 or events_read < args.max_events:
                if reader.ReadNextEvent() != ROOT.RecEventFile.eSuccess:
                    break
                events_read += 1
                shower = event.GetGenShower()
                theta = shower.GetZenith()       # ROOT API returns radians.
                azimuth = shower.GetAzimuth()    # Primary azimuth, not station phi.
                if not 30 <= math.degrees(theta) < 40:
                    continue
                events_selected += 1
                core = shower.GetCoreSiteCS()    # TRUE core, not reconstructed core.
                sd_event = event.GetSDEvent()

                # KEY DIFFERENCE from the parquet reader: iterate SIM stations.
                # A GenStation may exist even when HasStation(sd_id) is false.
                for simulated_station in sd_event.GetSimStationVector():
                    sd_id = simulated_station.GetId()
                    if not 2000 < sd_id < 90000:
                        continue  # Same physical-SD ID gate as the audited reader.
                    position = geometry.GetStationPosition(sd_id)
                    radius, phi = shower_plane_coordinates(position, core, theta, azimuth)
                    if not 150 <= radius < 1800:
                        continue

                    has_rec = bool(sd_event.HasStation(sd_id))
                    reconstructed_station = sd_event.GetStationById(sd_id) if has_rec else None
                    # No `continue` if has_rec is false! The count is available
                    # from simulated_station independently of that condition.
                    row = {
                        'source': filename.name, 'event_id': str(event.GetEventId()),
                        'sdId': sd_id, 'r': radius, 'phi': phi,
                        'theta': math.degrees(theta),
                        'logE': math.log10(shower.GetEnergy()),
                        'mu': simulated_station.GetNumberOfMuons(),
                        'em': simulated_station.GetNumberOfElectrons()
                              + simulated_station.GetNumberOfPhotons(),
                        'has_rec': int(has_rec),
                        'has_md': -1,  # NOT READ. This is not a physical zero.
                        'signal': reconstructed_station.GetTotalSignal() if has_rec else '',
                        'candidate': int(reconstructed_station.IsCandidate()) if has_rec else 0,
                        'silent': int(reconstructed_station.IsSilent()) if has_rec else 0,
                        'thinning': simulated_station.GetThinning(),
                        'weight': simulated_station.GetUsedWeight(),
                        'inside_rmin': int(simulated_station.IsInsideRMin()),
                    }
                    writer.writerow(row)
                    rows_written += 1
                if events_read % 200 == 0:
                    print('  saved events read:', events_read, flush=True)
            total_rows += rows_written
            records.append({
                'source': filename.name, 'input_path': str(filename),
                'input_bytes': filename.stat().st_size,
                'events_read': events_read, 'events_in_zenith_band': events_selected,
                'station_rows': rows_written,
                'elapsed_seconds': time.monotonic() - file_started,
            })
            print('  saved events:', events_read, '| selected events:', events_selected,
                  '| station rows:', rows_written, flush=True)

    with (output / 'provenance.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print('Finished:', total_rows, 'station rows in', time.monotonic() - started, 's', flush=True)
    print('Tables:', output / 'stations.csv', 'and', output / 'provenance.csv', flush=True)


if __name__ == '__main__':
    main()
