"""Verificación del cuaderno corregido, sin ejecutar sus celdas de producción.

--mode synthetic: pruebas artificiales y casos nulos/errores.
--mode cached: cálculo y figura sobre el CSV real ya disponible, sin ROOT.
--mode root: máximo DIEZ eventos del primer ADST, un proceso; no producción completa.
--output: directorio NUEVO dentro de esta carpeta, para conservar evidencia.

Las definiciones se extraen mediante AST para evitar importar ROOT/lanzar tandas
cuando sólo se prueba código. El cuaderno no depende de este verificador.
"""
import argparse
import ast
import contextlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import traceback

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
SOURCE = HERE/'Procesamiento_ADST_SD_UMD.py'


def functions_namespace(root=None):
    tree = ast.parse(SOURCE.read_text())
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) or
                   (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in {'LEGACY_COLUMNS','MODULE_COLUMNS','SD_COLUMNS'})]
    ns = dict(ROOT=root, np=np, pd=pd, os=os, math=math, time=time, re=re,
              Path=Path, sys=sys, contextlib=contextlib, traceback=traceback)
    exec(compile(ast.Module(body=definitions,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns


def synthetic():
    from test_dos_rutas_sin_root import fake_api, Event, Module, Counter, SimCounter, RecStation, original_function
    def baseline():
        e = Event()
        # La colección original artificial usa None, no el proxy C++ real; separar
        # ese caso de la comparación exacta y probarlo explícitamente abajo.
        e.md.counters = [c for c in e.md.counters if c.sd_id != 4004]
        return e
    passed = []
    api = fake_api(baseline)
    ns = functions_namespace(api)
    reader = ns['readADST_surface_v18']
    # Ruta existente sólo para el os.path.exists original; la API falsa NO la abre.
    old = original_function(api)(str(SOURCE))
    modules, sd, summary = reader(str(SOURCE))
    pd.testing.assert_frame_equal(modules.loc[modules.has_sd_rec,old.columns].reset_index(drop=True),
                                  old,check_dtype=False,check_exact=True)
    passed.append('original_selected_columns_exact')
    assert 4003 in sd.sdId.to_list() and 4003 not in modules.sdId.to_list()
    assert len(sd) == 6 and len(sd.loc[~sd.has_sd_rec]) == 2
    passed.append('SD_without_UMD_or_REC_retained')
    assert not sd.loc[sd.sdId.eq(4006),'mc_geometry_available'].iloc[0]
    passed.append('SD_geometry_failure_retains_count_and_marks_missing')

    class NullPointer:
        def __bool__(self): return False
    def null_empty():
        e=Event(); e.md.counters=[Counter(4001,[Module(i,[]) for i in (1,2,3)])]
        e.md.sim={104001:NullPointer()}; return e
    api=fake_api(null_empty); read=functions_namespace(api)['readADST_surface_v18']
    old=original_function(api)(str(SOURCE)); modules,sd,_=read(str(SOURCE))
    assert len(modules)==len(old)==3 and modules.nMuones_MC.eq(0).all()
    assert modules.nMuones_MC_available.isna().all() and not modules.has_umd_sim_counter.any()
    pd.testing.assert_frame_equal(modules[old.columns],old,check_dtype=False,check_exact=True)
    passed.append('regression_null_proxy_empty_channels_NO_row_loss')
    def null_with_channels():
        e=null_empty(); e.md.counters=[Counter(4001,[Module(1,[0])])]; return e
    modules,sd,_=functions_namespace(fake_api(null_with_channels))['readADST_surface_v18'](str(SOURCE))
    assert len(modules)==1 and modules.nMuones_MC_available.isna().all()
    passed.append('null_proxy_with_channels_not_dereferenced')
    def no_counters():
        e=Event(); e.md.counters=[]; return e
    modules,sd,_=functions_namespace(fake_api(no_counters))['readADST_surface_v18'](str(SOURCE))
    assert modules.empty and len(sd)==6
    passed.append('no_counters_does_not_remove_SD')
    modules,sd,summary=functions_namespace(fake_api(number_events=0))['readADST_surface_v18'](str(SOURCE))
    assert modules.empty and sd.empty and 'has_sd_rec' in sd
    passed.append('empty_schema')
    try:
        functions_namespace(fake_api(number_events=3,fail_after=1))['readADST_surface_v18'](str(SOURCE))
    except RuntimeError:
        passed.append('premature_EOF_fails')
    else:
        raise AssertionError('Premature EOF accepted')
    modules,sd,summary=functions_namespace(fake_api(number_events=3))['readADST_surface_v18'](str(SOURCE),max_events=1)
    assert summary['events_read']==1
    passed.append('explicit_event_limit')
    return {'mode':'synthetic','checks':passed}


def cached(output):
    import matplotlib
    matplotlib.use('Agg')
    import jupytext
    raw=pd.read_csv(PACKAGE/'04_soporte/tablas/adst_counts_fast.csv',dtype={'event_id':str})
    # Esto es una prueba del cálculo/plot sobre DATOS REALES GUARDADOS, no una
    # extracción ROOT nueva. No se presenta como resultado del lector v18.
    sd=raw.rename(columns={'r':'r_core_MC','phi':'phi_plane_MC','theta':'theta_MC',
                          'mu':'sd_nMuons_MC','em':'sd_nEM_MC','has_rec':'has_sd_rec'}).copy()
    sd['has_sd_rec']=sd.has_sd_rec.astype(bool)
    sd['mc_geometry_available']=True
    completed=pd.DataFrame({'source':sorted(raw.source.unique()),'max_events':np.nan})
    ns=functions_namespace()
    ns.update(df_sd=sd,completed=completed,output_dir=str(output))
    nb=jupytext.read(SOURCE)
    run=False
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        if cell.source.startswith('from scipy.optimize import curve_fit'):
            run=True
        if run:
            exec(compile(cell.source,str(SOURCE),'exec'),ns)
    assert ns['full_pdf_verified'] is True
    assert len(ns['selection_fits'])==32
    ref=ast.parse((PACKAGE/'02_notebooks/02_reproduccion/reproducir_desglose_sd.py').read_text())
    new=ast.parse(SOURCE.read_text())
    for name in ['harmonic_model','fit_one_band']:
        a=next(n for n in ref.body if isinstance(n,ast.FunctionDef) and n.name==name)
        b=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(a)==ast.dump(b),name
    return {'mode':'cached_real_data','points':32,'reference_fit_functions_identical':True,
            'full_pdf_numeric_check':True,'note':'No ROOT reread in cached mode.'}


def root_probe(output):
    import ROOT
    ROOT.gErrorIgnoreLevel=ROOT.kInfo
    library='/opt/auger/offline/icrc2025-test7-root6/lib/libRecEventKG.so'
    assert ROOT.gSystem.Load(library)>=0
    ns=functions_namespace(ROOT)
    fname=Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton/SIB23e_175_180_proton_MdSdInfill_CORSIKA78010_FLUKA_Run010.root')
    old=Path('/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17')
    # Esta llamada valida las filas seleccionadas con el parquet REAL viejo.
    result=ns['process_file_wrapper'](str(fname),str(output),str(old),max_events=10)
    sd=pd.read_parquet(output/'sd_estaciones'/fname.with_suffix('.parquet').name)
    modules=pd.read_parquet(output/'modulos'/fname.with_suffix('.parquet').name)
    raw=pd.read_csv(PACKAGE/'04_soporte/tablas/adst_counts_fast.csv',dtype={'event_id':str})
    raw=raw.loc[raw.source.eq(fname.name) & raw.event_id.isin(sd.event_id)]
    selected=sd.loc[sd.sdId.gt(2000)&sd.sdId.lt(90000)&sd.theta_MC.ge(30)&sd.theta_MC.lt(40)
                    &sd.r_core_MC.ge(150)&sd.r_core_MC.lt(1800)]
    merged=selected.merge(raw,on=['source','event_id','sdId'],how='outer',validate='one_to_one',indicator=True)
    assert merged._merge.eq('both').all()
    assert merged.sd_nMuons_MC.eq(merged.mu).all() and merged.sd_nEM_MC.eq(merged.em).all()
    assert merged.has_sd_rec.eq(merged.has_rec.astype(bool)).all()
    assert np.allclose(merged.r_core_MC,merged.r,atol=1e-6,rtol=0)
    assert np.allclose(merged.phi_plane_MC,merged.phi,atol=1e-12,rtol=0)
    # Caso que se perdía por bool(simCounter): se conserva, con verdad no disponible.
    absent=modules.loc[~modules.has_umd_sim_counter]
    assert len(absent)>0 and absent.nMuones_MC_available.isna().all()
    assert result['legacy_validation']=='identico'
    return {'mode':'real_ROOT_bounded','events':10,'summary':result,
            'reference_SD_rows_matched':len(merged),'SD_without_REC_in_reference_window':int((~merged.has_sd_rec).sum()),
            'preserved_modules_without_simcounter':len(absent),'ROOT':ROOT.gROOT.GetVersion(),
            'library':library,'note':'Only first ten events; full production not run.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['synthetic','cached','root'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    if not output.is_relative_to(HERE/'datos_generados'):
        raise ValueError('Use a NEW subdirectory inside datos_generados for validation.')
    output.mkdir(parents=True,exist_ok=False)
    for folder in ['modulos','sd_estaciones','logs','resultados']:
        (output/folder).mkdir()
    result=synthetic() if args.mode=='synthetic' else cached(output) if args.mode=='cached' else root_probe(output)
    (output/'VALIDACION.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
