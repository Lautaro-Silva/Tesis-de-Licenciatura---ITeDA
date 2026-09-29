"""Synthetic tests ONLY. Never import ROOT or open a production ADST.

The original reader's two function definitions are extracted with ast, not its
top-level imports/environment/batch cells. They run against an artificial API.
The new reader runs against the SAME artificial events. This tests implementation
logic and an original-code baseline, not compatibility with actual C++/ROOT data.
"""
import ast
import importlib.util
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dual_notebook', HERE/'Procesamiento_ADST_dos_rutas.py')
dual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dual)
assert 'ROOT' not in sys.modules, 'Synthetic tests must never import ROOT.'


class Vector:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    def X(self): return self.x
    def Y(self): return self.y
    def Z(self): return self.z
    def RotateZ(self, a):
        self.x, self.y = math.cos(a)*self.x-math.sin(a)*self.y, math.sin(a)*self.x+math.cos(a)*self.y
    def RotateY(self, a):
        self.x, self.z = math.cos(a)*self.x+math.sin(a)*self.z, -math.sin(a)*self.x+math.cos(a)*self.z


class Iterator:
    def __init__(self, items, index=0): self.items, self.index = items, index
    def __eq__(self, other): return self.items is other.items and self.index == other.index
    def __deref__(self): return self.items[self.index]
    def __iadd__(self, n): self.index += n; return self


class Channel:
    def __init__(self, channel_id): self.channel_id = channel_id
    def GetId(self): return self.channel_id


class Module:
    def __init__(self, module_id, channels):
        self.module_id = module_id
        self.channels = [Channel(i) for i in channels]
    def GetId(self): return self.module_id
    def IsCandidate(self): return True
    def IsSaturated(self): return False
    def IsRejected(self): return False
    def IsSilent(self): return False
    def GetNumberOfEstimatedMuons(self): return 2.
    def ChannelsBegin(self): return Iterator(self.channels)
    def ChannelsEnd(self): return Iterator(self.channels, len(self.channels))


class Counter:
    def __init__(self, sd_id, modules): self.sd_id, self.modules = sd_id, {m.GetId(): m for m in modules}
    def GetId(self): return self.sd_id+100000
    def GetSdPartnerId(self): return self.sd_id
    def HasModule(self, i): return i in self.modules
    def GetModule(self, i): return self.modules[i]


class SimCounter:
    def __init__(self, counts): self.counts = counts
    def HasSimScintillatorByChannel(self, m, c): return (m, c) in self.counts
    def GetSimScintillatorByChannelId(self, m, c):
        return types.SimpleNamespace(GetNumberOfInjectedMuons=lambda: self.counts[m, c])


class RecStation:
    def IsLowGainSaturated(self): return False
    def GetTotalSignal(self): return 8.
    def GetTotalSignalError(self): return .8
    def GetMuonSignal(self): return 0.
    def GetSPDistanceError(self): return 3.
    def GetAzimuthSP(self): return .7
    def GetSPDistance(self): return 450.


class SimStation:
    def __init__(self, sd_id): self.sd_id = sd_id
    def GetId(self): return self.sd_id
    def GetNumberOfMuons(self): return self.sd_id % 5
    def GetNumberOfElectrons(self): return 30
    def GetNumberOfPhotons(self): return 70


class Geometry:
    def GetStationPosition(self, station_id):
        physical = station_id-100000 if station_id >= 100000 else station_id
        if physical == 4006: raise KeyError('Deliberately missing geometry')
        if physical == 4002 and station_id >= 100000: raise KeyError('UMD geometry absent, SD fallback')
        return Vector(100.*(physical-4000), 300., -2.3 if station_id >= 100000 else 0.)


class MD:
    def __init__(self):
        self.counters = [Counter(4001, [Module(0, [0,1]), Module(1, [0,1])]),
                         Counter(4002, [Module(0, [0,1]), Module(1, [])]),
                         Counter(4004, [Module(0, [0])]), Counter(4005, []),
                         Counter(4006, [Module(0, [0])]), Counter(4007, [Module(0, [0])])]
        self.sim = {104001: SimCounter({(0,0):2, (0,1):1, (1,0):0, (1,1):0}),
                    104002: SimCounter({(0,0):4}), 104005: SimCounter({}),
                    104006: SimCounter({(0,0):1}), 104007: SimCounter({(0,0):1})}
    def CountersBegin(self): return Iterator(self.counters)
    def CountersEnd(self): return Iterator(self.counters, len(self.counters))
    def GetSimCounter(self, i): return self.sim.get(i)


class SD:
    def __init__(self):
        self.sim = {i: SimStation(i) for i in range(4001, 4007)}
        self.rec = {i: RecStation() for i in [4001,4004,4005,4006,4007]}
    def HasStation(self, i): return i in self.rec
    def GetStationById(self, i): return self.rec[i]
    def HasSimStation(self, i): return i in self.sim
    def GetSimStationById(self, i): return self.sim[i]
    def GetSimStationVector(self): return list(self.sim.values())
    def GetSdRecShower(self): return Shower(reconstructed=True)


class Shower:
    def __init__(self, reconstructed=False): self.rec = reconstructed
    def GetEnergy(self): return 10**17.7
    def GetZenith(self): return .61 if self.rec else .6
    def GetAzimuth(self): return .32 if self.rec else .3
    def GetCoreSiteCS(self): return Vector(10., -20., 0.) if self.rec else Vector(0.,0.,0.)
    def GetShortPrimaryName(self): return 'proton'


class Event:
    def __init__(self): self.md, self.sd, self.identifier = MD(), SD(), 'synthetic:Run_1:Shower_1:Use_1'
    def GetEventId(self): return self.identifier
    def GetMDEvent(self): return self.md
    def GetSDEvent(self): return self.sd
    def GetGenShower(self): return Shower()


class StringVector(list):
    def push_back(self, x): self.append(x)


def fake_api(event_factory=Event, number_events=1, fail_after=None):
    class Reader:
        eSuccess, eFailure = 0, 1
        def __init__(self, files): self.index = 0
        def ReadDetectorGeometry(self, geo): return self.eSuccess
        def SetBuffers(self, target): self.target = target
        def GetNEvents(self): return number_events
        def ReadNextEvent(self):
            if self.index >= number_events or (fail_after is not None and self.index >= fail_after): return self.eFailure
            self.target.__dict__.update(event_factory().__dict__)
            self.target.identifier += f':entry{self.index}'
            self.index += 1
            return self.eSuccess
        def Close(self, write_event_info): assert write_event_info is False
    return types.SimpleNamespace(RecEventFile=Reader, RecEvent=Event, DetectorGeometry=Geometry,
        TVector3=Vector, std=types.SimpleNamespace(vector=lambda _: StringVector),
        gROOT=types.SimpleNamespace(GetVersion=lambda: 'SYNTHETIC-NO-ROOT'))


def original_function(ROOT):
    tree = ast.parse(dual.SOURCE_ORIGINAL.read_text())
    wanted = [node for node in tree.body if isinstance(node, ast.FunctionDef)
              and node.name in {'getModuleList','readADST_surface_v17'}]
    assert len(wanted) == 2
    namespace = {'ROOT': ROOT, 'np': np, 'pd': pd, 'os': os, 'time': time}
    exec(compile(ast.Module(body=wanted, type_ignores=[]), str(dual.SOURCE_ORIGINAL), 'exec'), namespace)
    return namespace['readADST_surface_v17']


class TestDualRoutes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dual_reader_synthetic_')
        self.root = Path(self.temp.name)
        # Empty fixture, not a ROOT file: only the fake API ever receives this path.
        self.input = self.root/'SIB23e_175_180_proton_SYNTHETIC_Run001.root'
        self.input.touch()
        self.api = fake_api()
    def tearDown(self): self.temp.cleanup()

    def test_original_function_and_new_A_agree(self):
        old = original_function(self.api)(str(self.input))
        tables = dual.readADST_surface_dual(self.input, self.api)
        new = tables['A_con_HasStation']
        self.assertEqual(set(dual.LEGACY_COLUMNS), set(old.columns))
        old_path = self.root/self.input.with_suffix('.parquet').name
        old.to_parquet(old_path, index=False)
        report, missing = dual.compare_to_legacy(new, tables['eventos_leidos'], old_path)
        self.assertEqual(missing, [])
        self.assertTrue(report.mismatches.eq(0).all(), report.to_string())
        self.assertEqual(len(new), 3)
        self.assertEqual(len(tables['B_sin_HasStation']), 5)

    def test_availability_and_inventories_are_not_merged(self):
        tables = dual.readADST_surface_dual(self.input, self.api)
        b = tables['B_sin_HasStation']
        self.assertNotIn(4003, b.sdId.tolist())
        inv = tables['inventario_SD'].set_index('sdId')
        self.assertEqual(inv.loc[4003,'n_umd_counters'], 0)
        self.assertEqual(inv.loc[4004,'rows_B'], 0)
        self.assertEqual(inv.loc[4005,'rows_B'], 0)
        self.assertFalse(inv.loc[4006,'mc_geometry_available'])
        unknown = b.loc[b.sdId.eq(4002)]
        self.assertTrue(unknown.nMuones_MC_available.isna().all())
        self.assertEqual(unknown.nMuones_MC.tolist(), [4.,0.])
        zero = b.loc[b.sdId.eq(4001) & b.moduleId.eq(1)].iloc[0]
        self.assertTrue(zero.umd_truth_summary_complete)
        self.assertEqual(zero.nMuones_MC_available, 0.)

    def test_missing_and_partial_reference_detected(self):
        tables = dual.readADST_surface_dual(self.input, self.api)
        a = tables['A_con_HasStation']
        old = a[dual.LEGACY_COLUMNS].copy()
        old.loc[0,'sd_nMuons_MC'] += 1
        file = self.root/self.input.with_suffix('.parquet').name
        old.iloc[:-1].to_parquet(file, index=False)
        report, _ = dual.compare_to_legacy(a, tables['eventos_leidos'], file)
        bad = report.set_index('column').mismatches
        self.assertEqual(bad['__rows_new_only__'], 1)
        self.assertEqual(bad['sd_nMuons_MC'], 1)

    def test_pilot_and_premature_read_failure(self):
        limited = dual.readADST_surface_dual(self.input, fake_api(number_events=3), max_events=1)
        self.assertEqual(len(limited['eventos_leidos']), 1)
        with self.assertRaises(RuntimeError):
            dual.readADST_surface_dual(self.input, fake_api(number_events=3, fail_after=1))

    def test_full_reference_checks_events_outside_pilot(self):
        full = dual.readADST_surface_dual(self.input, fake_api(number_events=2))
        pilot = dual.readADST_surface_dual(self.input, fake_api(number_events=2), max_events=1)
        file = self.root/self.input.with_suffix('.parquet').name
        full['A_con_HasStation'][dual.LEGACY_COLUMNS].to_parquet(file, index=False)
        report, _ = dual.compare_to_legacy(pilot['A_con_HasStation'], pilot['eventos_leidos'], file,
                                           restrict_to_read_events=True)
        self.assertTrue(report.mismatches.eq(0).all())
        report, _ = dual.compare_to_legacy(pilot['A_con_HasStation'], pilot['eventos_leidos'], file)
        self.assertEqual(report.set_index('column').loc['__rows_old_only__', 'mismatches'], 3)

    def test_cpp_null_pointer_is_not_none(self):
        class NullPointer:
            def __bool__(self): return False
        def event_with_null():
            event = Event(); event.md.sim[104004] = NullPointer(); return event
        tables = dual.readADST_surface_dual(self.input, fake_api(event_with_null))
        audit = tables['auditoria_counters'].set_index('sdId')
        self.assertEqual(audit.loc[4004, 'reason_B'], 'sim_counter_unavailable')

    def test_failed_reference_never_marks_run_complete(self):
        old_parent, old_library = dual.OUTPUT_PARENT, dual.OFFLINE_LIBRARY
        try:
            dual.OUTPUT_PARENT = self.root/'failed_run_outputs'
            dual.OFFLINE_LIBRARY = self.root/'fake_library.fixture'
            dual.OFFLINE_LIBRARY.touch()
            legacy = self.root/'old'; legacy.mkdir()
            tables = dual.readADST_surface_dual(self.input, self.api)
            reference = tables['A_con_HasStation'][dual.LEGACY_COLUMNS].copy()
            reference.loc[0, 'nMuones_MC'] += 1
            reference.to_parquet(legacy/self.input.with_suffix('.parquet').name, index=False)
            run = dual.OUTPUT_PARENT/'synthetic_failure'
            with self.assertRaises(AssertionError):
                dual.run_processing([{'name':'test', 'input':self.root, 'legacy':legacy}],
                                    run, self.api, 1, None)
            self.assertFalse((run/'RUN_COMPLETE.json').exists())
            self.assertTrue((run/'RUN_FAILED.json').exists())
            self.assertTrue((run/'test/comparacion_legacy'/self.input.with_suffix('.csv').name).exists())
        finally:
            dual.OUTPUT_PARENT, dual.OFFLINE_LIBRARY = old_parent, old_library

    def test_no_UMD_is_not_synthetic_zero_modules(self):
        def event_without_counters():
            event = Event(); event.md.counters = []; return event
        tables = dual.readADST_surface_dual(self.input, fake_api(event_without_counters))
        self.assertTrue(tables['A_con_HasStation'].empty)
        self.assertTrue(tables['B_sin_HasStation'].empty)
        self.assertFalse(tables['inventario_SD'].empty)

    def test_no_events_still_has_schema(self):
        tables = dual.readADST_surface_dual(self.input, fake_api(number_events=0))
        self.assertEqual(list(tables['A_con_HasStation']), dual.LEGACY_COLUMNS+dual.EXTRA_COLUMNS)

    def test_both_routes_identical_if_all_have_rec(self):
        def selected_event():
            event = Event(); event.sd.rec[4002] = RecStation(); return event
        tables = dual.readADST_surface_dual(self.input, fake_api(selected_event))
        pd.testing.assert_frame_equal(tables['A_con_HasStation'], tables['B_sin_HasStation'])

    def test_dense_without_rec_not_fabricated_geometry(self):
        ctx = {'mc_core':Vector(0,0,0), 'rec_core':Vector(0,0,0), 'mc_theta':.6, 'mc_phi':.3, 'rec_phi':.32}
        result, eligible, _ = dual.station_geometry(self.api, Geometry(), 90001, 90001, None, ctx)
        self.assertTrue(eligible)
        self.assertTrue(result['is_dense_ring'])
        self.assertFalse(result['mc_geometry_available'])
        self.assertTrue(np.isnan(result['r_core_MC']))

    def test_metadata_model_with_underscore(self):
        result = dual.filename_metadata('EPOSLHC_R_180_185_helium_example_Run004.root')
        self.assertEqual(result['model_mc'], 'EPOSLHC_R')
        self.assertEqual(result['e_min_mc'], 18.)

    def test_exclusive_outputs_and_hash_check(self):
        old_parent, old_library = dual.OUTPUT_PARENT, dual.OFFLINE_LIBRARY
        try:
            dual.OUTPUT_PARENT = self.root/'out'
            dual.OFFLINE_LIBRARY = self.root/'fake_library.fixture'
            dual.OFFLINE_LIBRARY.touch()
            legacy = self.root/'old'; legacy.mkdir()
            original_function(self.api)(str(self.input)).to_parquet(legacy/self.input.with_suffix('.parquet').name, index=False)
            run = dual.OUTPUT_PARENT/'synthetic'
            datasets = [{'name':'test', 'input':self.root, 'legacy':legacy}]
            dual.run_processing(datasets, run, self.api, max_files=1, max_events=None)
            tables = dual.load_completed_dataset(run, 'test')
            self.assertEqual(len(tables['B_sin_HasStation']), 5)
            with self.assertRaises(FileExistsError):
                dual.run_processing(datasets, run, self.api, 1, None)
            path = run/'test/B_sin_HasStation'/self.input.with_suffix('.parquet').name
            with path.open('ab') as stream: stream.write(b'test tampering')
            with self.assertRaises(AssertionError): dual.load_completed_dataset(run, 'test')
        finally:
            dual.OUTPUT_PARENT, dual.OFFLINE_LIBRARY = old_parent, old_library


if __name__ == '__main__':
    unittest.main(verbosity=2)
