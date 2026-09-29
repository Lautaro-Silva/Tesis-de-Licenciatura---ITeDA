# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # ADST → parquet: dos rutas comparables, un solo lector
#
# **Preparado para que lo ejecute el autor. No se ha ejecutado sobre ADST.**
# Derivado de `Scripts/Procesamiento_ADST_v8-2.py`, función `readADST_surface_v17`.
# Conserva su estructura: entorno → auxiliares → lector por archivo → wrapper →
# configuración de tandas → procesamiento → controles. Todas las funciones están
# en este cuaderno, no escondidas en un lector externo.
#
# La pregunta es precisa: ¿qué cambia al retirar SOLAMENTE el requisito de
# presencia SD reconstruida, manteniendo el universo UMD del lector original?
#
# | Salida | Universo | HasStation |
# |---|---|---|
# | A_con_HasStation | Counters y módulos UMD del lector original | Exigido |
# | B_sin_HasStation | Los mismos requisitos comunes de counter/módulo/geometría | No exigido |
# | inventario_SD | Todas las estaciones SD simuladas guardadas | Sólo registrado |
#
# **El inventario SD NO es la ruta B.** Permite descubrir si siguen faltando
# estaciones por no tener counter/módulos UMD. B puede resultar igual a A si la
# selección ya ocurrió antes de guardar esos objetos. Ése sería un resultado
# importante, no un motivo para cambiar silenciosamente de universo.
#
# A se obtiene de B con un único filtro, tras extraer una vez los valores comunes.
# Además, A se compara contra tu parquet original. La identidad A=B[HasStation]
# es una garantía de diseño; **no sustituye** esa comprobación externa.
#
# No se modifica el lector original, Offline ni sus configuraciones. Nunca se
# escribe sobre los parquet existentes. `RUN_PROCESSING=False` por defecto.

# %%
# CELDA 1 — Importaciones livianas. Importar este .py NO importa ROOT ni procesa.
import os
import sys
import time
import json
import re
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from IPython.display import display

REPO = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / 'CLAUDE.md').is_file())
HERE = REPO / 'claude_work/revision_asimetrias_sd_umd/02_notebooks/04_reprocesamiento'
SOURCE_ORIGINAL = REPO / 'Scripts/Procesamiento_ADST_v8-2.py'

# No se toca el entorno persistente. Esta función sólo carga la biblioteca que
# el autor eligió para SU proceso, después de habilitar la ejecución.
def cargar_offline(library_path):
    """No inicializar ROOT automáticamente al abrir/importar el cuaderno."""
    import ROOT
    library_path = Path(library_path)
    if not library_path.is_file():
        raise FileNotFoundError(library_path)
    if ROOT.gSystem.Load(str(library_path)) < 0:
        raise RuntimeError('No se pudo cargar libRecEventKG.so. Revisar el entorno ROOT/Offline.')
    print('Python:', sys.executable, '| ROOT:', ROOT.gROOT.GetVersion())
    print('Biblioteca:', library_path)
    # No silenciamos warnings de esquema/checksum: no equivalen a validación.
    return ROOT

# %% [markdown]
# ## 1. Entorno y alcance — antes de correr
#
# Usá un kernel con PyROOT compatible con los ADST, numpy, pandas y pyarrow.
# El venv de análisis por sí solo no certifica compatibilidad con el ROOT de
# Offline. No se instala ningún paquete ni se cambia una configuración aquí.
#
# A diferencia de la extracción diagnóstica anterior, **no hay cortes por theta,
# radio, energía, saturación, señal positiva ni número de muones** en este lector.
# Los límites de archivos/eventos de la prueba inicial son límites de lectura,
# se aplican por igual a ambas rutas y se registran. Para toda una producción se
# ponen en None. No mezclar un piloto con una tanda completa.
#
# Se mantienen las convenciones históricas, incluso las columnas geométricas que
# no se recomiendan para el análisis actual: no se corrigen a la vez que HasStation.
# Para comparar asimetrías Infill usar `r_core_MC` y
# `phi_plane_euler_MC_true_core`, deshaciendo su +pi como en `plots_seccion_6`.
# A1 > 0 significa exceso temprano. Los ángulos phi almacenados están en radianes.

# %%
# CELDA 2 — Auxiliares: mismos módulos y rotaciones que en v17.
def getModuleList(counter, sim=True):
    return [counter.GetModule(i) for i in (range(6) if sim else range(100, 116))
            if counter.HasModule(i)]

def iter_cpp(begin, end):
    """Recorre el mismo iterador C++ que v17, sin convertir objetos ROOT a listas."""
    iterator = begin
    while iterator != end:
        yield iterator.__deref__()
        iterator += 1

def log_energy(energy):
    return float(np.log10(energy)) if energy > 0 else np.nan

def position_with_fallback(geo, detector_id):
    """Mismo intento ID/ID±100000 de v17; registrar un fallo, no inventar posición."""
    alternate = detector_id + 100000 if detector_id < 90000 else detector_id - 100000
    errors = []
    for candidate in (detector_id, alternate):
        try:
            return geo.GetStationPosition(candidate), candidate, ''
        except Exception as exc:
            errors.append(type(exc).__name__)
    return None, None, '/'.join(errors)

def rotate_position(ROOT, position, core, theta, azimuth):
    vector = ROOT.TVector3(position.X()-core.X(), position.Y()-core.Y(), position.Z()-core.Z())
    vector.RotateZ(-azimuth)
    vector.RotateY(-theta)
    return vector

def azimuth(vector, extra_pi=False):
    # Se copia el +2pi de v17 para minimizar diferencias numéricas de redondeo.
    return float((np.arctan2(vector.Y(), vector.X()) + (np.pi if extra_pi else 0) + 2*np.pi) % (2*np.pi))

LEGACY_COLUMNS = [
    'event_id', 'logE_MC', 'theta_MC', 'phi_MC', 'primary', 'logE_REC', 'theta_REC', 'phi_REC',
    'counterId', 'moduleId', 'nMuones_REC', 'nMuones_MC', 'module_status', 'is_sd_saturated',
    'x_plane', 'y_plane', 'phi_plane_sp', 'phi_plane_ground', 'phi_plane_ground_mc',
    'phi_plane_euler_MC', 'phi_plane_euler_MC_true_core', 'r_core', 'r_core_err', 'r_core_MC',
    'is_true_umd_pos', 'phi_plane_sp_umd_counter', 'phi_plane_sp_umd_module',
    'phi_plane_darko_rec', 'phi_plane_darko_mc', 'r_umd_rec', 'r_umd_mc',
    'sdId', 'sdSignal_REC', 'sd_nMuons_MC', 'sd_nEM_MC', 'sdSignal_err', 'sdMuonSignal_REC',
]
EXTRA_COLUMNS = [
    'source', 'event_index', 'has_sd_rec', 'has_sd_sim', 'sd_truth_available',
    'has_rec_shower_object', 'is_dense_ring', 'mc_geometry_available',
    'umd_serialized_channels', 'umd_channels_with_truth', 'umd_truth_summary_complete',
    'nMuones_MC_available',
]
MODULE_KEY = ['source', 'event_id', 'sdId', 'counterId', 'moduleId']
STATION_KEY = ['source', 'event_id', 'sdId']

# %% [markdown]
# ## 2. Qué se conserva y qué se protege cuando no hay SD reconstruido
#
# Se usan los mismos accessors para conteos y señales. Cuando falta sdStation,
# sus señales, errores y flags de saturación se guardan como ausentes, no cero.
# La geometría MC Infill sale de DetectorGeometry y del núcleo/eje verdaderos:
# no requiere ese objeto reconstruido. La geometría relativa al núcleo REC puede
# existir aunque una estación particular no esté reconstruida; no se borra.
#
# **Anillo Denso:** v17 usa geometría SP de la estación REC y deja varias phi MC
# en NaN. Se conserva esa convención para A. Sin SD REC no se inventan coordenadas
# de anillo: se conserva la fila B, con geometría ausente y una marca explícita.
# No usar esa fila para inferir una asimetría sin recuperar una geometría válida.
#
# Los getters inesperadamente fallidos producen un error de archivo. Sólo el
# fallback geométrico y la ausencia conocida de un accessor MC se tratan como en
# v17. No convertimos cualquier excepción de ROOT en cero muones.

# %%
def event_context(event):
    """Verdad MC imprescindible; objeto de shower REC opcional, no corte de evento."""
    mc = event.GetGenShower()
    sd = event.GetSDEvent()
    rec = sd.GetSdRecShower()
    has_rec = rec is not None and bool(rec)
    context = {
        'mc_core': mc.GetCoreSiteCS(), 'mc_theta': mc.GetZenith(), 'mc_phi': mc.GetAzimuth(),
        'rec_core': rec.GetCoreSiteCS() if has_rec else None,
        'rec_phi': rec.GetAzimuth() if has_rec else np.nan,
    }
    fields = {
        'event_id': str(event.GetEventId()), 'logE_MC': log_energy(mc.GetEnergy()),
        'theta_MC': float(mc.GetZenith()*180/np.pi), 'phi_MC': float(mc.GetAzimuth()*180/np.pi),
        'primary': str(mc.GetShortPrimaryName()),
        'logE_REC': log_energy(rec.GetEnergy()) if has_rec else np.nan,
        'theta_REC': float(rec.GetZenith()*180/np.pi) if has_rec else np.nan,
        'phi_REC': float(rec.GetAzimuth()*180/np.pi) if has_rec else np.nan,
        # Existencia de objeto NO es certificación de calidad de reconstrucción.
        'has_rec_shower_object': has_rec,
    }
    return sd, context, fields

def sd_counts(sd, sd_id):
    has_sim = bool(sd.HasSimStation(sd_id))
    values = {'sd_nMuons_MC': np.nan, 'sd_nEM_MC': np.nan,
              'has_sd_sim': has_sim, 'sd_truth_available': False}
    if has_sim:
        station = sd.GetSimStationById(sd_id)
        # Como v17: un accessor inexistente deja NaN; errores de ejecución distintos
        # de AttributeError no se silencian.
        try:
            values['sd_nMuons_MC'] = float(station.GetNumberOfMuons())
            values['sd_nEM_MC'] = float(station.GetNumberOfElectrons()) + float(station.GetNumberOfPhotons())
            values['sd_truth_available'] = True
        except AttributeError:
            pass
    return values

def station_geometry(ROOT, geo, sd_id, counter_id, rec_station, ctx):
    """Convenciones de v17; devuelve también disponibilidad y fallo geométrico."""
    fields = {name: np.nan for name in [
        'x_plane', 'y_plane', 'phi_plane_sp', 'phi_plane_ground', 'phi_plane_ground_mc',
        'phi_plane_euler_MC', 'phi_plane_euler_MC_true_core', 'r_core', 'r_core_MC',
        'phi_plane_sp_umd_counter', 'phi_plane_sp_umd_module',
        'phi_plane_darko_rec', 'phi_plane_darko_mc', 'r_umd_rec', 'r_umd_mc',
    ]}
    dense = 90000 <= sd_id < 100000
    infill = sd_id >= 100000 or 2000 < sd_id < 90000
    fields.update(is_dense_ring=dense, is_true_umd_pos=False, mc_geometry_available=False)
    if rec_station is not None:
        value = rec_station.GetAzimuthSP()
        fields['phi_plane_sp'] = float((value - ctx['rec_phi'] + 2*np.pi) % (2*np.pi)) if infill else float((value+2*np.pi) % (2*np.pi))
    if dense:
        if rec_station is not None:
            radius, phi = rec_station.GetSPDistance(), rec_station.GetAzimuthSP()
            fields.update(r_core=radius, r_core_MC=radius, r_umd_rec=radius, r_umd_mc=radius,
                          x_plane=radius*np.cos(phi), y_plane=radius*np.sin(phi))
        # V17 no proporciona phi_euler_MC_true_core para el anillo. No confundir
        # su radio SP almacenado con un conjunto completo de coordenadas MC.
        return fields, True, 'dense_missing_sd_rec' if rec_station is None else ''

    pos, used_id, error = position_with_fallback(geo, sd_id)
    if pos is None:
        return fields, False, 'sd_geometry_unavailable:'+error
    mc = rotate_position(ROOT, pos, ctx['mc_core'], ctx['mc_theta'], ctx['mc_phi'])
    fields['r_core_MC'] = float(np.sqrt(mc.X()**2 + mc.Y()**2))
    fields['phi_plane_euler_MC_true_core'] = azimuth(mc, extra_pi=True)
    fields['phi_plane_ground_mc'] = float((np.arctan2(pos.Y()-ctx['mc_core'].Y(), pos.X()-ctx['mc_core'].X())-ctx['mc_phi']+2*np.pi) % (2*np.pi))
    fields['mc_geometry_available'] = True
    if ctx['rec_core'] is not None:
        rec = rotate_position(ROOT, pos, ctx['rec_core'], ctx['mc_theta'], ctx['mc_phi'])
        fields.update(r_core=float(np.sqrt(rec.X()**2+rec.Y()**2)), x_plane=rec.X(), y_plane=rec.Y(),
                      phi_plane_euler_MC=azimuth(rec, extra_pi=True))
        fields['phi_plane_ground'] = float((np.arctan2(pos.Y()-ctx['rec_core'].Y(), pos.X()-ctx['rec_core'].X())-ctx['rec_phi']+2*np.pi) % (2*np.pi))
    umd, _, _ = position_with_fallback(geo, counter_id)
    fields['is_true_umd_pos'] = umd is not None
    # Igual que v17: si sólo hay fallback a SD, las columnas Darko quedan NaN.
    if umd is not None:
        mc_umd = rotate_position(ROOT, umd, ctx['mc_core'], ctx['mc_theta'], ctx['mc_phi'])
        fields.update(phi_plane_darko_mc=azimuth(mc_umd), r_umd_mc=float(np.hypot(mc_umd.X(), mc_umd.Y())))
        if ctx['rec_core'] is not None:
            rec_umd = rotate_position(ROOT, umd, ctx['rec_core'], ctx['mc_theta'], ctx['mc_phi'])
            fields.update(phi_plane_darko_rec=azimuth(rec_umd), r_umd_rec=float(np.hypot(rec_umd.X(), rec_umd.Y())))
    return fields, True, ''

# %% [markdown]
# ## 3. UMD: compatibilidad histórica no equivale a verdad completa
#
# `nMuones_MC` conserva el cálculo de v17: suma sobre los canales del módulo que
# tienen resumen MC, empezando en cero. Esto permite cotejar A con tu parquet.
# **Ese cero histórico no certifica cero muones físicos si faltan resúmenes.**
#
# Se añaden cantidad de canales serializados, cantidad con resumen MC y
# `umd_truth_summary_complete`. `nMuones_MC_available` sólo contiene la suma
# cuando todos los canales enumerados tienen resumen y hay al menos un canal;
# en los demás casos es NaN. Incluso esa marca se refiere a canales enumerados:
# no prueba que el ADST haya serializado todos los centelladores físicos.
# No dibujar un UMD “sin selección” rellenando NaN con cero o descartándolos sin
# estudiar si su ausencia depende del azimut.

# %%
def module_values(module, sim_counter):
    if module.IsCandidate():
        status = 'candidate'
    elif module.IsSaturated():
        status = 'saturated'
    elif module.IsRejected():
        status = 'rejected'
    elif module.IsSilent():
        status = 'silent'
    else:
        status = 'undefined'
    module_id = int(module.GetId())
    count, channels, populated = 0., 0, 0
    for channel in iter_cpp(module.ChannelsBegin(), module.ChannelsEnd()):
        channels += 1
        channel_id = channel.GetId()
        if sim_counter.HasSimScintillatorByChannel(module_id, channel_id):
            scintillator = sim_counter.GetSimScintillatorByChannelId(module_id, channel_id)
            count += float(scintillator.GetNumberOfInjectedMuons())
            populated += 1
    complete = channels > 0 and populated == channels
    return {'moduleId': module_id, 'module_status': status,
            'nMuones_REC': float(module.GetNumberOfEstimatedMuons()), 'nMuones_MC': count,
            'umd_serialized_channels': channels, 'umd_channels_with_truth': populated,
            'umd_truth_summary_complete': complete,
            'nMuones_MC_available': count if complete else np.nan}

def module_frame(rows):
    """Esquema estable incluso si un archivo/ruta no produce ninguna fila."""
    frame = pd.DataFrame(rows, columns=LEGACY_COLUMNS+EXTRA_COLUMNS)
    strings = {'event_id', 'source', 'primary', 'module_status'}
    integers = {'counterId', 'moduleId', 'sdId', 'event_index', 'umd_serialized_channels', 'umd_channels_with_truth'}
    booleans = {'is_sd_saturated', 'is_true_umd_pos', 'has_sd_rec', 'has_sd_sim',
                'sd_truth_available', 'has_rec_shower_object', 'is_dense_ring',
                'mc_geometry_available', 'umd_truth_summary_complete'}
    for col in frame:
        dtype = 'string' if col in strings else 'Int64' if col in integers else 'boolean' if col in booleans else 'float64'
        frame[col] = frame[col].astype(dtype)
    return frame

def split_routes(base):
    """ÉSTE es el único filtro que distingue las rutas comparadas."""
    route_b = base.reset_index(drop=True).copy()
    route_a = route_b.loc[route_b.has_sd_rec].reset_index(drop=True).copy()
    return route_a, route_b

def assert_routes(route_a, route_b):
    assert not route_b.duplicated(MODULE_KEY).any(), 'Clave de módulo duplicada.'
    pd.testing.assert_frame_equal(route_a, route_b.loc[route_b.has_sd_rec].reset_index(drop=True))
    # SD se repite por módulo como en v17, pero no puede cambiar dentro de la estación.
    for col in ['sd_nMuons_MC', 'sd_nEM_MC', 'r_core_MC', 'phi_plane_euler_MC_true_core', 'has_sd_rec']:
        assert route_b.groupby(STATION_KEY, dropna=False)[col].nunique(dropna=False).le(1).all(), col
    absent = route_b.loc[~route_b.has_sd_rec]
    assert absent[['sdSignal_REC', 'sdSignal_err', 'sdMuonSignal_REC', 'r_core_err', 'is_sd_saturated']].isna().all().all()
    incomplete = ~route_b.umd_truth_summary_complete
    assert route_b.loc[incomplete, 'nMuones_MC_available'].isna().all()

# %% [markdown]
# ## 4. Lector por archivo: una pasada compartida
#
# El bucle principal sigue siendo MDEvent.CountersBegin → módulos 0–5 → canales.
# No se exige `IsCandidate`, no se corta saturación ni se elimina Nmu=0.
# Se conserva la necesidad de un simCounter y de geometría SD Infill recuperable.
# Se registra por counter qué impide emitir una fila B, aun cuando tampoco había
# SD REC. El control de nullptr se hace con bool: GetSimCounter devuelve un puntero
# C++ nulo si falta; `is None` por sí solo no es suficiente en todos los PyROOT.
#
# El inventario adicional usa GetSimStationVector, pero NO añade sus estaciones
# al dataframe de módulos. Sirve para medir la diferencia entre universos.
# Tampoco carga listas de partículas ni cinemáticas de producción.
# No se deshabilitan ramas ROOT: se evita añadir el cambio de I/O del lector
# diagnóstico anterior al experimento sobre el pipeline original.

# %%
def readADST_surface_dual(fname, ROOT, max_events=None):
    """Devuelve A, B, auditoría de counters, inventario SD y lista de eventos leídos."""
    if max_events is not None and max_events <= 0:
        raise ValueError('max_events debe ser positivo o None (todos).')
    files = ROOT.std.vector('string')()
    files.push_back(str(fname))
    reader, event, geo = ROOT.RecEventFile(files), ROOT.RecEvent(), ROOT.DetectorGeometry()
    if reader.ReadDetectorGeometry(geo) != ROOT.RecEventFile.eSuccess:
        raise RuntimeError('No se pudo leer DetectorGeometry; no se marca el archivo completo.')
    reader.SetBuffers(event)
    expected_events = int(reader.GetNEvents())
    if max_events is not None:
        expected_events = min(expected_events, max_events)
    modules, counters, inventory, events = [], [], [], []
    event_index = 0
    while event_index < expected_events:
        # El API devuelve eFailure tanto al terminar como si no puede continuar.
        # A diferencia de detenerse silenciosamente, exigimos leer las entradas
        # declaradas (o el límite del piloto) antes de certificar el archivo.
        if reader.ReadNextEvent() != ROOT.RecEventFile.eSuccess:
            raise RuntimeError('Fin de lectura anterior al número esperado de eventos.')
        event_index += 1
        sd, ctx, common = event_context(event)
        common.update(source=Path(fname).name, event_index=event_index)
        md = event.GetMDEvent()
        event_counter_audit = []
        for counter in iter_cpp(md.CountersBegin(), md.CountersEnd()):
            counter_id, sd_id = int(counter.GetId()), int(counter.GetSdPartnerId())
            has_rec = bool(sd.HasStation(sd_id))
            rec_station = sd.GetStationById(sd_id) if has_rec else None
            geometry, geometry_ok, geometry_note = station_geometry(ROOT, geo, sd_id, counter_id, rec_station, ctx)
            sim_counter = md.GetSimCounter(counter_id)
            has_sim_counter = sim_counter is not None and bool(sim_counter)
            available_modules = getModuleList(counter, sim=True)
            eligible = geometry_ok and has_sim_counter
            n_b = len(available_modules) if eligible else 0
            reason = ('geometry_unavailable' if not geometry_ok else
                      'sim_counter_unavailable' if not has_sim_counter else
                      'no_modules_0_to_5' if not available_modules else 'emitted')
            audit = {key: common[key] for key in ['source', 'event_id', 'event_index']}
            audit.update(counterId=counter_id, sdId=sd_id, has_sd_rec=has_rec,
                         has_sim_counter=has_sim_counter, geometry_available=geometry_ok,
                         geometry_note=geometry_note, modules_present=len(available_modules),
                         rows_B=n_b, rows_A=n_b if has_rec else 0, reason_B=reason)
            counters.append(audit)
            event_counter_audit.append(audit)
            if not eligible:
                continue
            station_values = {
                **common, **geometry, **sd_counts(sd, sd_id), 'sdId': sd_id, 'counterId': counter_id,
                'has_sd_rec': has_rec,
                'is_sd_saturated': bool(rec_station.IsLowGainSaturated()) if has_rec else pd.NA,
                'sdSignal_REC': float(rec_station.GetTotalSignal()) if has_rec else np.nan,
                'sdSignal_err': float(rec_station.GetTotalSignalError()) if has_rec else np.nan,
                'sdMuonSignal_REC': float(rec_station.GetMuonSignal()) if has_rec else np.nan,
                'r_core_err': float(rec_station.GetSPDistanceError()) if has_rec else np.nan,
            }
            for module in available_modules:
                modules.append({**station_values, **module_values(module, sim_counter)})

        # Complemento separado: estaciones SD que el universo UMD puede no cubrir.
        for station in sd.GetSimStationVector():
            sid = int(station.GetId())
            item = {key: common[key] for key in ['source', 'event_id', 'event_index', 'theta_MC', 'phi_MC', 'logE_MC']}
            related = [c for c in event_counter_audit if c['sdId'] == sid]
            pos, _, note = position_with_fallback(geo, sid) if not 90000 <= sid < 100000 else (None, None, 'dense_geometry_not_inferred')
            vector = rotate_position(ROOT, pos, ctx['mc_core'], ctx['mc_theta'], ctx['mc_phi']) if pos is not None else None
            item.update(sdId=sid, has_sd_rec=bool(sd.HasStation(sid)),
                        sd_nMuons_MC=float(station.GetNumberOfMuons()),
                        sd_nEM_MC=float(station.GetNumberOfElectrons())+float(station.GetNumberOfPhotons()),
                        r_core_MC=float(np.hypot(vector.X(), vector.Y())) if vector is not None else np.nan,
                        phi_plane_euler_MC_true_core=azimuth(vector, extra_pi=True) if vector is not None else np.nan,
                        mc_geometry_available=vector is not None, geometry_note=note,
                        n_umd_counters=len(related), rows_B=sum(c['rows_B'] for c in related),
                        rows_A=sum(c['rows_A'] for c in related))
            inventory.append(item)
        events.append({key: common[key] for key in ['source', 'event_id', 'event_index', 'theta_MC', 'logE_MC']})
        if event_index % 500 == 0:
            print(Path(fname).name, '| eventos:', event_index, '| módulos B:', len(modules), flush=True)

    reader.Close(False)  # Sólo cerrar lectura; no escribir EventInfo.
    route_a, route_b = split_routes(module_frame(modules))
    assert_routes(route_a, route_b)
    # Esquemas también para producciones sin counters o estaciones.
    counter_cols = ['source','event_id','event_index','counterId','sdId','has_sd_rec','has_sim_counter',
                    'geometry_available','geometry_note','modules_present','rows_B','rows_A','reason_B']
    inventory_cols = ['source','event_id','event_index','theta_MC','phi_MC','logE_MC','sdId','has_sd_rec',
                      'sd_nMuons_MC','sd_nEM_MC','r_core_MC','phi_plane_euler_MC_true_core',
                      'mc_geometry_available','geometry_note','n_umd_counters','rows_B','rows_A']
    event_cols = ['source','event_id','event_index','theta_MC','logE_MC']
    tables = {'A_con_HasStation': route_a, 'B_sin_HasStation': route_b,
              'auditoria_counters': pd.DataFrame(counters, columns=counter_cols),
              'inventario_SD': pd.DataFrame(inventory, columns=inventory_cols),
              'eventos_leidos': pd.DataFrame(events, columns=event_cols)}
    assert not tables['eventos_leidos'].duplicated(['source', 'event_id']).any()
    assert not tables['inventario_SD'].duplicated(STATION_KEY).any()
    # Cotejo interno de conteos entre las dos colecciones, sin añadir filas.
    once = route_b.drop_duplicates(STATION_KEY)
    joined = once.merge(tables['inventario_SD'], on=STATION_KEY, suffixes=('_B','_SD'), how='left', validate='one_to_one', indicator=True)
    assert joined.loc[joined.has_sd_sim.fillna(False), '_merge'].eq('both').all()
    for col in ['sd_nMuons_MC','sd_nEM_MC']:
        present = joined.sd_truth_available.fillna(False)
        assert np.array_equal(joined.loc[present, col+'_B'].to_numpy(float), joined.loc[present, col+'_SD'].to_numpy(float))
    return tables

# %% [markdown]
# ## 5. Comparación externa con tu parquet: condición necesaria, no adorno
#
# Por archivo se coteja A contra el parquet existente en los mismos eventos leídos.
# Un piloto de cincuenta eventos no se compara contra todas las filas del archivo.
# En una lectura completa sí se compara la referencia entera: un evento adicional
# en el parquet antiguo debe detectarse, no desaparecer al tomar la intersección.
# Se usa unión externa por evento/counter/módulo/SD: también se detectan filas
# perdidas o añadidas, no sólo valores coincidentes en la intersección.
#
# Se comprueban todas las columnas v17 disponibles. Las ausentes se informan;
# las columnas centrales de conteo/geometría son obligatorias. Conteos e IDs deben
# coincidir exactamente; sólo las coordenadas y cantidades continuas admiten
# tolerancia numérica. Un fallo NO se declara éxito ni se oculta en el promedio A1.
# Si tu parquet fue generado con otra versión, hay que explicar esas diferencias
# antes de interpretar B−A. Este código no certifica por sí solo cuál versión lo creó.

# %%
def compare_to_legacy(route_a, event_table, parquet_file, restrict_to_read_events=False):
    original = pd.read_parquet(parquet_file)
    original['source'] = Path(parquet_file).with_suffix('.root').name
    original['event_id'] = original.event_id.astype(str)
    if restrict_to_read_events:
        original = original.loc[original.event_id.isin(event_table.event_id.astype(str))].copy()
    current = route_a.copy()
    current['event_id'] = current.event_id.astype(str)
    required = MODULE_KEY + ['nMuones_MC','sd_nMuons_MC','sd_nEM_MC','r_core_MC','phi_plane_euler_MC_true_core']
    missing_required = sorted(set(required)-set(original.columns))
    if missing_required:
        raise ValueError('Faltan columnas obligatorias en el parquet de referencia: '+str(missing_required))
    assert not original.duplicated(MODULE_KEY).any(), 'Referencia con claves duplicadas.'
    columns = [c for c in LEGACY_COLUMNS if c in original and c not in MODULE_KEY]
    joined = current[MODULE_KEY+columns].merge(original[MODULE_KEY+columns], on=MODULE_KEY,
            how='outer', suffixes=('_new','_old'), indicator=True, validate='one_to_one')
    records = [{'column': '__rows_new_only__', 'mismatches': int(joined._merge.eq('left_only').sum())},
               {'column': '__rows_old_only__', 'mismatches': int(joined._merge.eq('right_only').sum())}]
    both = joined.loc[joined._merge.eq('both')]
    exact = {'nMuones_MC','sd_nMuons_MC','sd_nEM_MC','primary','module_status','is_sd_saturated','is_true_umd_pos'}
    for col in columns:
        x, y = both[col+'_new'], both[col+'_old']
        if col in exact or pd.api.types.is_string_dtype(current[col].dtype):
            equal = (x.eq(y).fillna(False) | (x.isna() & y.isna())).to_numpy(bool)
        else:
            equal = np.isclose(x.to_numpy(float, na_value=np.nan), y.to_numpy(float, na_value=np.nan), rtol=1e-10, atol=1e-8, equal_nan=True)
        records.append({'column': col, 'mismatches': int((~equal).sum())})
    report = pd.DataFrame(records)
    missing_optional = sorted(set(LEGACY_COLUMNS)-set(original.columns))
    return report, missing_optional

def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def filename_metadata(path):
    # Son metadatos, no cortes. Se admite un nombre de modelo con '_' (EPOSLHC_R);
    # split('_') con posiciones fijas fallaría en esa producción.
    match = re.fullmatch(r'(.+?)_(\d+)_(\d+)_([^_]+)_.+_Run(\d+)', Path(path).stem)
    if match is None:
        raise ValueError('No se reconoce el nombre de producción: '+Path(path).name)
    model, lo, hi, primary, run = match.groups()
    return {'model_mc': model, 'e_min_mc': float(lo)/10,
            'e_max_mc': float(hi)/10, 'primary_name_mc': primary, 'run_number': int(run)}

def write_new_json(path, contents):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(contents, stream, indent=2, ensure_ascii=False)

def process_file_wrapper(fname, dataset_output, ROOT, max_events, legacy_directory=None):
    """Un archivo, ambas rutas; sin sobreescritura ni éxito si falla la validación."""
    started = time.monotonic()
    fname, dataset_output = Path(fname), Path(dataset_output)
    initial = fname.stat()
    tables = readADST_surface_dual(fname, ROOT, max_events=max_events)
    metadata = filename_metadata(fname)
    for name in ['A_con_HasStation','B_sin_HasStation']:
        for key, value in metadata.items():
            tables[name][key] = value
    assert_routes(tables['A_con_HasStation'], tables['B_sin_HasStation'])
    expected = None if legacy_directory is None else Path(legacy_directory)/fname.with_suffix('.parquet').name
    report, optional = None, []
    reference_state = 'not_configured'
    if expected is not None:
        if not expected.is_file():
            raise FileNotFoundError('Referencia configurada pero ausente: '+str(expected))
        report, optional = compare_to_legacy(tables['A_con_HasStation'], tables['eventos_leidos'], expected,
                                             restrict_to_read_events=max_events is not None)
        reference_state = 'pass' if report.mismatches.eq(0).all() else 'FAIL'
    # La escritura exclusiva evita el "si existe, saltear" ambiguo del wrapper viejo.
    # Un directorio de tanda es nuevo. Archivos parciales nunca se llaman completos.
    outputs = {}
    for name, table in tables.items():
        directory = dataset_output/name
        directory.mkdir(parents=True, exist_ok=True)
        output = directory/fname.with_suffix('.parquet').name
        with output.open('xb') as stream:
            table.to_parquet(stream, index=False, compression='snappy')
        outputs[name] = {'rows': len(table), 'relative_path': str(output.relative_to(dataset_output)),
                         'sha256': sha256_file(output)}
    if report is not None:
        directory = dataset_output/'comparacion_legacy'
        directory.mkdir(exist_ok=True)
        with (directory/(fname.stem+'.csv')).open('x') as stream:
            report.to_csv(stream, index=False)
    now = fname.stat()
    if (initial.st_size, initial.st_mtime_ns) != (now.st_size, now.st_mtime_ns):
        raise RuntimeError('El ROOT de entrada cambió durante la lectura.')
    complete = reference_state != 'FAIL'
    result = {'source': fname.name, 'input_bytes': initial.st_size, 'input_mtime_ns': initial.st_mtime_ns,
              'event_limit': max_events, 'events_read': len(tables['eventos_leidos']),
              'legacy_validation': reference_state, 'legacy_missing_optional_columns': optional,
              'outputs': outputs, 'elapsed_seconds': time.monotonic()-started, 'complete': complete}
    marker = dataset_output/'manifiestos'
    marker.mkdir(exist_ok=True)
    write_new_json(marker/(fname.stem+'.json'), result)
    if not complete:
        raise AssertionError('Ruta A no coincide con el parquet. Ver comparacion_legacy; no interpretar B−A todavía.')
    print(fname.name, '| A:', len(tables['A_con_HasStation']), '| B:', len(tables['B_sin_HasStation']),
          '| referencia:', reference_state, '| segundos:', round(result['elapsed_seconds'],1), flush=True)
    return result

# %% [markdown]
# ## 6. Configurar tandas, igual que al final de v8-2
#
# Una entrada por modelo/energía/primario. Se incluyen ejemplos de las tandas de
# v8-2; sólo protones SIBYLL está activo inicialmente. Podés agregar cualquier
# otra carpeta. Para procesar **todos los archivos** de las tandas elegidas, poner
# MAX_FILES=None y MAX_EVENTS=None después del piloto.
#
# No hay Pool automático: N_WORKERS=1 es intencional para el servidor compartido.
# Las dos rutas salen de una pasada, no duplican la lectura ROOT. Se mantiene en
# memoria un archivo a la vez, como v17. Medí tiempo/RAM en un archivo completo
# antes de escalar; el piloto limitado a pocos eventos no predice bien su costo.
#
# Si querés todos los modelos/energías/primarios disponibles, podés usar la función
# de descubrimiento de directorios de abajo y revisar la tabla antes de habilitar.
# Ese modo no adivina la ruta de tus parquet antiguos: asignala explícitamente
# para disponer de la validación externa en cada producción.

# %%
RUN_PROCESSING = False             # Cambiar SOLAMENTE cuando vayas a correrlo vos.
RUN_COMPARISON = False             # Lectura/análisis posterior, también opt-in.
RUN_LABEL = 'piloto_dos_rutas_001'  # Nombre nuevo: se rechaza si ya existe.
MAX_FILES = 1                      # None = todos los archivos por tanda.
MAX_EVENTS = 50                    # None = todos los eventos guardados por archivo.
N_WORKERS = 1                      # Este cuaderno es serial, no lanza multiprocessing.

PRODUCTION_ROOT = Path('/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA')
OLD_PARQUET_ROOT = Path('/home/lsilva/Github/ADST_Alexey_module_v11')
DATASETS = [
    {'name': 'sib_proton_17', 'input': PRODUCTION_ROOT/'SIB23e/17.5_18.0/proton',
     'legacy': OLD_PARQUET_ROOT/'parquet_sib_proton_17'},
    # {'name': 'sib_helio_17', 'input': PRODUCTION_ROOT/'SIB23e/17.5_18.0/helium',
    #  'legacy': OLD_PARQUET_ROOT/'parquet_sib_helio_17'},
    # {'name': 'sib_hierro_17', 'input': PRODUCTION_ROOT/'SIB23e/17.5_18.0/iron',
    #  'legacy': OLD_PARQUET_ROOT/'parquet_sib_hierro_17'},
    # {'name': 'qgs_helio_17', 'input': PRODUCTION_ROOT/'QGSIII01/17.5_18.0/helium',
    #  'legacy': OLD_PARQUET_ROOT/'parquet_qgs_helio_17'},
]
library_base = Path(os.environ.get('AUGEROFFLINEROOT', '/opt/auger/offline/icrc2025-test7-root6'))
OFFLINE_LIBRARY = library_base/'lib/libRecEventKG.so'
# Regla del repositorio: las salidas nuevas viven dentro del repo, no en la
# producción original ni sobre los parquet del autor. Esta carpeta está ignorada.
OUTPUT_PARENT = HERE/'datos_generados'

def discover_datasets(production_root):
    """Sólo lista directorios; no abre archivos ROOT ni inicia procesamiento."""
    return [{'name': '_'.join(p.relative_to(production_root).parts).replace('.','p'),
             'input': p, 'legacy': None}
            for p in sorted(Path(production_root).glob('*/*/*'))
            if p.is_dir() and next(p.glob('*.root'), None) is not None]

# OPCIONAL, ejecutarlo vos para seleccionar todas las producciones:
# DATASETS = discover_datasets(PRODUCTION_ROOT)
# display(pd.DataFrame(DATASETS))
# Después completar las referencias legacy disponibles. legacy=None significa
# "sin cotejo externo", NO "reproduce automáticamente el lector original".

def plan_files(datasets, max_files):
    if max_files is not None and max_files <= 0:
        raise ValueError('MAX_FILES debe ser positivo o None.')
    plans = []
    names = [d['name'] for d in datasets]
    if not names or len(set(names)) != len(names):
        raise ValueError('Elegir tandas con nombres únicos.')
    for dataset in datasets:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', dataset['name']):
            raise ValueError('Nombre de tanda inválido.')
        files = sorted(Path(dataset['input']).glob('*.root'))
        if max_files is not None:
            files = files[:max_files]
        if not files:
            raise FileNotFoundError('No hay ROOT en '+str(dataset['input']))
        plans.append((dataset, files))
    return plans

# %% [markdown]
# ## 7. Ejecutar — bloque deshabilitado en la entrega
#
# Orden sugerido para el autor:
#
# 1. Revisar las rutas y el entorno; dejar una tanda, un archivo y cincuenta eventos.
#    Guardar el notebook y sincronizar su .py antes de ejecutar: el manifiesto
#    registra el hash de ese archivo, no cambios de celdas aún sin guardar.
# 2. Habilitar RUN_PROCESSING y ejecutar; exigir coincidencia de A con el parquet.
# 3. Revisar auditoria_counters/inventario_SD. ¿B realmente incorporó módulos?
# 4. Elegir un RUN_LABEL nuevo; MAX_EVENTS=None para medir un archivo completo.
# 5. Con costo y validación conocidos, usar MAX_FILES=None y MAX_EVENTS=None.
#
# Nunca cambiar el nombre de un piloto para hacerlo pasar por producción completa.
# Ante un error, los archivos escritos quedan preservados para inspección y la
# tanda NO tiene RUN_COMPLETE.json. No hay reanudación/reescritura automática:
# usar otra etiqueta y seleccionar explícitamente lo que se quiera repetir.
# Los archivos de todas las rutas tienen los mismos basenames y metadatos.

# %%
def run_processing(datasets, run_directory, ROOT, max_files, max_events):
    run_directory = Path(run_directory).resolve()
    allowed = OUTPUT_PARENT.resolve()
    if run_directory == allowed or not run_directory.is_relative_to(allowed):
        raise ValueError('La tanda debe ser un subdirectorio nuevo de datos_generados.')
    if run_directory.exists():
        raise FileExistsError('La tanda ya existe. No se sobrescribe: '+str(run_directory))
    plans = plan_files(datasets, max_files)
    run_directory.mkdir(parents=True, exist_ok=False)
    configuration = {
        'max_files': max_files, 'max_events': max_events, 'workers': 1,
        'original_reader_sha256': sha256_file(SOURCE_ORIGINAL),
        'dual_reader_sha256': sha256_file(HERE/'Procesamiento_ADST_dos_rutas.py'),
        'root_version': str(ROOT.gROOT.GetVersion()), 'library': str(OFFLINE_LIBRARY),
        'library_sha256': sha256_file(OFFLINE_LIBRARY),
        'datasets': [{'name': d['name'], 'input': str(d['input']),
                      'legacy': str(d['legacy']) if d.get('legacy') is not None else None,
                      'files': [f.name for f in files]} for d, files in plans],
    }
    write_new_json(run_directory/'CONFIG.json', configuration)
    records = []
    try:
        for dataset, files in plans:
            for filename in files:
                result = process_file_wrapper(filename, run_directory/dataset['name'], ROOT,
                                               max_events, dataset.get('legacy'))
                records.append({'dataset': dataset['name'], **result})
        write_new_json(run_directory/'RUN_COMPLETE.json', {'files': records, 'complete': True})
    except Exception as exc:
        write_new_json(run_directory/'RUN_FAILED.json', {'error': type(exc).__name__+': '+str(exc),
                                                        'completed_files': len(records)})
        raise
    return records

if RUN_PROCESSING:
    if N_WORKERS != 1:
        raise ValueError('No se habilitó multiprocessing en esta versión; ejecutar serialmente.')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', RUN_LABEL):
        raise ValueError('RUN_LABEL debe ser un nombre simple y nuevo.')
    plans = plan_files(DATASETS, MAX_FILES)
    print('Archivos a leer:', sum(len(files) for _, files in plans))
    print('Límite de eventos por archivo:', MAX_EVENTS, '| sin cortes físicos adicionales.')
    print('Salida nueva:', OUTPUT_PARENT/RUN_LABEL)
    ROOT = cargar_offline(OFFLINE_LIBRARY)
    processing_results = run_processing(DATASETS, OUTPUT_PARENT/RUN_LABEL, ROOT, MAX_FILES, MAX_EVENTS)
else:
    print('Procesamiento DESHABILITADO. No se importó ROOT ni se abrió ningún ADST.')

# %% [markdown]
# ## 8. Leer solamente tandas completas y preparar una comparación honesta
#
# La lectura posterior verifica los hashes de los archivos terminados. No usar
# `pd.read_parquet(datos_generados/)`: mezclaría tandas, rutas, inventarios y pilotos.
# Primero elegir UNA tanda y UNA producción, después UNA tabla.
#
# Para SD, ambas rutas se reducen a una fila por estación/evento. Para UMD se
# conservan los módulos. No aplicar a B un corte de señal REC, candidato SD o
# `dropna()` global: eso podría reintroducir la selección que se acaba de retirar.
# Si se necesita disponibilidad MC, se exige la MISMA condición explícita a ambas
# rutas y se informa cuántas filas se pierden. No rellenar verdad ausente con cero.

# %%
def load_completed_dataset(run_directory, dataset_name):
    run_directory = Path(run_directory)
    complete = json.loads((run_directory/'RUN_COMPLETE.json').read_text())
    if complete.get('complete') is not True:
        raise ValueError('Tanda no completa.')
    files = [r for r in complete['files'] if r['dataset'] == dataset_name]
    if not files:
        raise ValueError('La tanda no contiene esa producción.')
    parts = {name: [] for name in files[0]['outputs']}
    dataset_root = (run_directory/dataset_name).resolve()
    for record in files:
        if not record['complete']:
            raise ValueError('Archivo no validado como completo.')
        for name, item in record['outputs'].items():
            path = (dataset_root/item['relative_path']).resolve()
            if not path.is_relative_to(dataset_root):
                raise ValueError('Ruta de manifiesto fuera de la producción.')
            assert sha256_file(path) == item['sha256'], path
            parts[name].append(pd.read_parquet(path))
    result = {name: pd.concat(items, ignore_index=True) for name, items in parts.items()}
    assert_routes(result['A_con_HasStation'], result['B_sin_HasStation'])
    return result

def coverage_summary(tables):
    """Esta tabla decide si se comparan poblaciones realmente ampliadas."""
    a, b, inv = tables['A_con_HasStation'], tables['B_sin_HasStation'], tables['inventario_SD']
    records = []
    for has_rec in [True, False]:
        subset = b.loc[b.has_sd_rec.eq(has_rec)]
        sd_subset = inv.loc[inv.has_sd_rec.eq(has_rec)]
        records.append({'has_sd_rec': has_rec, 'SD_sim_guardadas': len(sd_subset),
                        'SD_sin_counter_UMD': int(sd_subset.n_umd_counters.eq(0).sum()),
                        'SD_sin_filas_en_B': int(sd_subset.rows_B.eq(0).sum()),
                        'modulos_B': len(subset), 'modulos_con_resumen_incompleto': int((~subset.umd_truth_summary_complete).sum())})
    return pd.DataFrame(records)

if RUN_COMPARISON:
    dataset_name = DATASETS[0]['name']
    tables = load_completed_dataset(OUTPUT_PARENT/RUN_LABEL, dataset_name)
    display(coverage_summary(tables))
    df_A = tables['A_con_HasStation']
    df_B = tables['B_sin_HasStation']
    sd_A = df_A.drop_duplicates(STATION_KEY)
    sd_B = df_B.drop_duplicates(STATION_KEY)
    print('Usar sd_A/sd_B para SD; df_A/df_B para UMD, examinando antes sus marcas de disponibilidad.')
else:
    print('Comparación DESHABILITADA. No se cargaron datasets de una tanda nueva.')

# %% [markdown]
# ## 9. Qué demostraría cada resultado
#
# - **A reproduce el parquet; B añade filas; cambia A1:** el cambio se obtiene
#   retirando HasStation dentro del mismo universo de counters/módulos de v17.
# - **A reproduce el parquet; B=A; inventario muestra SD fuera de B:** quitar
#   HasStation no basta en el pipeline UMD. El requisito de counter/módulo también
#   restringe la muestra; el inventario SD anterior no era la misma población B.
# - **A no reproduce el parquet:** detener la interpretación. Revisar versión,
#   eventos, getters y geometría con la tabla de diferencias, no retocar A1.
# - **B añade módulos pero faltan resúmenes UMD:** se puede estudiar el conteo SD
#   disponible; no se ha recuperado automáticamente el UMD sin selección.
#
# No se incluye un resultado esperado ni un ajuste que fuerce la inversión.
# El notebook anterior de comparación SD–UMD sigue siendo otro estudio hasta
# que esta reproducción hecha por el autor pase sus controles.
#
# **Estado de esta entrega:** código y pruebas de lógica con objetos artificiales;
# no validación ROOT/ADST real, no producción ejecutada, no nuevo A1 medido.
