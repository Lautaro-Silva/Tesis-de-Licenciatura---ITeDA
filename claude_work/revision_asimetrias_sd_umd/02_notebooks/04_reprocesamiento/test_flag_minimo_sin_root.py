"""Pruebas artificiales del cambio mínimo: nunca ejecutar/importar el notebook.

Sólo se extraen definiciones de función con AST. Los objetos falsos ya existentes
en test_dos_rutas_sin_root se reutilizan para no duplicar una biblioteca de pruebas.
Nada de este archivo se necesita para procesar los ADST desde el nuevo cuaderno.
"""
import ast
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import numpy as np
import pandas as pd

from test_dos_rutas_sin_root import (
    fake_api, original_function, Event, Counter, Module, SimCounter,
    SimStation, RecStation, dual,
)

SOURCE = Path(__file__).with_name('Procesamiento_ADST_v8-2_flag.py')


def minimal_reader(api):
    # No se ejecutan import ROOT, carga de librerías, tandas ni celdas de análisis.
    tree = ast.parse(SOURCE.read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert [n.name for n in functions] == [
        'getModuleList', 'readADST_surface_v17_flag', 'process_file_wrapper']
    namespace = {'ROOT': api, 'np': np, 'pd': pd, 'os': os, 'time': time}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['readADST_surface_v17_flag']


class TestMinimalFlag(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='minimal_flag_synthetic_')
        self.path = Path(self.temp.name)/'SIB23e_175_180_proton_SYNTHETIC_Run001.root'
        # Ruta vacía, NO un ROOT: satisface os.path.exists del código original.
        self.path.touch()

    def tearDown(self):
        self.temp.cleanup()

    def assert_selected_unchanged(self, factory=Event):
        api = fake_api(factory)
        old = original_function(api)(str(self.path))
        new = minimal_reader(api)(str(self.path))
        self.assertEqual(set(new.columns), set(old.columns) | {'has_sd_rec'})
        selected = new.loc[new.has_sd_rec, old.columns].reset_index(drop=True)
        pd.testing.assert_frame_equal(selected, old, check_dtype=False, check_exact=True)
        return new

    def test_selected_values_exactly_original(self):
        new = self.assert_selected_unchanged()
        self.assertEqual(len(new), 5)
        self.assertEqual(new.has_sd_rec.sum(), 3)

    def test_missing_station_does_not_remove_global_shower_or_mc(self):
        new = minimal_reader(fake_api())(str(self.path))
        added = new.loc[~new.has_sd_rec]
        self.assertEqual(added.sdId.unique().tolist(), [4002])
        missing = ['sdSignal_REC','sdSignal_err','sdMuonSignal_REC',
                   'r_core_err','phi_plane_sp','is_sd_saturated']
        self.assertTrue(added[missing].isna().all().all())
        retained = ['logE_REC','theta_REC','phi_REC','r_core_MC',
                    'phi_plane_euler_MC_true_core','sd_nMuons_MC','nMuones_REC']
        self.assertTrue(added[retained].notna().all().all())
        self.assertEqual(added.nMuones_MC.tolist(), [4., 0.])  # Suma histórica, sin redefinirla.

    def test_all_has_station_returns_original_dataset(self):
        def factory():
            event = Event(); event.sd.rec[4002] = RecStation(); return event
        new = self.assert_selected_unchanged(factory)
        self.assertTrue(new.has_sd_rec.all())

    def test_dense_selected_original_and_absent_coordinates_missing(self):
        def factory():
            event = Event()
            for sid in [90001, 90002]:
                counter = Counter(sid, [Module(0, [0])])
                event.md.counters.append(counter)
                event.md.sim[counter.GetId()] = SimCounter({(0,0):2})
                event.sd.sim[sid] = SimStation(sid)
            event.sd.rec[90001] = RecStation()
            return event
        new = self.assert_selected_unchanged(factory)
        absent = new.loc[new.sdId.eq(90002)]
        self.assertEqual(len(absent), 1)
        self.assertTrue(absent[['r_core','r_core_MC','x_plane','y_plane','r_umd_mc']].isna().all().all())
        self.assertEqual(absent.nMuones_MC.iloc[0], 2.)

    def test_existing_umd_universe_not_replaced(self):
        new = minimal_reader(fake_api())(str(self.path))
        # 4003 tiene SD simulado pero no counter UMD; NO se inventa una fila.
        # 4004 no tiene simCounter; 4005 no tiene módulos; 4006 no tiene geometría.
        for sid in [4003, 4004, 4005, 4006]:
            self.assertNotIn(sid, new.sdId.tolist())

    def test_null_cpp_pointer_is_safely_skipped(self):
        class NullPointer:
            def __bool__(self): return False
        def factory():
            event = Event(); event.md.sim[104002] = NullPointer(); return event
        new = minimal_reader(fake_api(factory))(str(self.path))
        self.assertNotIn(4002, new.sdId.tolist())

    def test_parquet_roundtrip_preserves_flag_and_missing_values(self):
        new = minimal_reader(fake_api())(str(self.path))
        parquet = self.path.with_suffix('.parquet')
        new.to_parquet(parquet, index=False)
        restored = pd.read_parquet(parquet)
        pd.testing.assert_series_equal(new.has_sd_rec, restored.has_sd_rec)
        self.assertTrue(restored.loc[~restored.has_sd_rec, 'is_sd_saturated'].isna().all())

    def test_only_original_helpers_and_unchanged_wrapper_logic(self):
        old = ast.parse(dual.SOURCE_ORIGINAL.read_text())
        new = ast.parse(SOURCE.read_text())
        old_functions = {n.name:n for n in old.body if isinstance(n, ast.FunctionDef)}
        new_functions = {n.name:n for n in new.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(len(new_functions), 3)
        self.assertEqual(ast.dump(old_functions['getModuleList']), ast.dump(new_functions['getModuleList']))
        wrapper = new_functions['process_file_wrapper']
        # La única edición ejecutable del wrapper es el nombre del lector llamado.
        for node in ast.walk(wrapper):
            if isinstance(node, ast.Name) and node.id == 'readADST_surface_v17_flag':
                node.id = 'readADST_surface_v17'
        self.assertEqual(ast.dump(old_functions['process_file_wrapper']), ast.dump(wrapper))


if __name__ == '__main__':
    assert 'ROOT' not in sys.modules, 'Estas pruebas no deben importar ROOT.'
    unittest.main(verbosity=2)
