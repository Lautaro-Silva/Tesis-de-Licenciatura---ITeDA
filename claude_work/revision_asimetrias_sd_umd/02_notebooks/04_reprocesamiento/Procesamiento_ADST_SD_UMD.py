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
# # ADST → SD completo + módulos UMD: reproducción del antes/después
#
# **Éste es el cuaderno corregido para reproducir SD_antes_despues_mismos_bins.pdf.**
# Reemplaza como punto de entrada a la propuesta mínima con flag, que NO recuperaba
# la población SD de ese gráfico. Los archivos anteriores se preservan para auditar.
#
# Una sola lectura de cada ROOT produce DOS tablas, porque tienen unidades distintas:
#
# | Carpeta parquet | Una fila representa | De dónde sale |
# |---|---|---|
# | sd_estaciones | Una estación SD simulada en un evento | SDEvent.GetSimStationVector |
# | modulos | Un módulo UMD guardado en un evento | MDEvent.CountersBegin → módulos |
#
# El SD se guarda PRIMERO y no necesita counter, módulo, canales ni simCounter UMD.
# No hay que unir por intersección las tablas antes de graficar: volvería a cortar SD.
# HasStation se guarda como has_sd_rec. En SD, comparar TODAS las filas contra las
# filas con flag True reproduce exactamente la definición del gráfico objetivo.
#
# En módulos se conservan las columnas y cálculos históricos; se retira el corte SD.
# Si falta simCounter NO se descarta la fila: la suma histórica nMuones_MC se mantiene
# para cotejar tus resultados, pero nMuones_MC_available queda NaN y los flags avisan
# que no es verdad MC completa. Ausencia de información NO significa cero físico.
#
# Código visible, comentado y con los bucles originales. Tres funciones de extracción
# (auxiliar original, lector y wrapper); dos funciones de ajuste copiadas del gráfico.
# No hay condiciones para agentes ni un RUN_PROCESSING oculto. La celda de ejecución
# procesa cuando VOS la ejecutás. No hacer Run All sin revisar rutas/costo.
# La configuración incluye TODOS los archivos y ocho procesos, como tu uso original.
# Para una prueba elegí explícitamente menos archivos o max_events; no hay piloto oculto.
#
# Las verificaciones son: lectura completa, claves únicas, igualdad de la tabla UMD
# seleccionada con tu parquet viejo cuando configurás esa referencia, igualdad SD
# fila por fila con la extracción anterior, y finalmente igualdad de A1 Y sus errores.
# Las dos últimas se aplican a la producción SIBYLL/protón que generó el PDF.
# No se deben exigir esos valores a otros modelos/energías/primarios.

# %%
# --- Celda 1.1: Importaciones y Carga de Librerías Offline ---
import os
import numpy as np
import pandas as pd
import glob
import ROOT
import time
import traceback
import sys
import contextlib
import math
import re
from pathlib import Path
from multiprocessing import Pool, get_start_method
import gc
from functools import partial

# %%
# Esta es la parte MÁS IMPORTANTE:
# Asegúrate de que estás corriendo este Jupyter Lab desde una terminal
# donde ANTES hiciste: source /ruta/a/auger/offline/this-auger-offline.sh

AugerOfflineRoot = os.environ.get("AUGEROFFLINEROOT")
if AugerOfflineRoot is None:
    raise EnvironmentError(
        "AUGEROFFLINEROOT no definido. "
        "Reinicia Jupyter Lab desde una terminal donde hayas "
        "hecho: "
        " 'aug_set_version offline 4.0.1-icrc23-prod1-root6' "   
        " 'source /srv/software/amd64/ubuntu/24.04/auger/offline/4.0.1-icrc23-prod1-root6/bin/this-auger-offline.sh'."
    )

print(f"AUGEROFFLINEROOT encontrado en: {AugerOfflineRoot}")

# Cargar las librerías necesarias
print("Cargando librerías de Auger Offline...")
libs_to_load = ["libRecEventKG.so"]
for lib in libs_to_load:
    lib_path = os.path.join(AugerOfflineRoot, "lib", lib)
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"No se encontró la librería: {lib_path}")
    
    # Usamos gSystem.Load que es más robusto en PyROOT
    status = ROOT.gSystem.Load(lib_path)
    if status < 0:
        raise ImportError(f"Error cargando la librería: {lib_path}")

# Mostrar warnings ROOT, incluidos los nativos C++; no heredar kError de otra celda.
ROOT.gErrorIgnoreLevel = ROOT.kInfo
print("ROOT:", ROOT.gROOT.GetVersion(), "| warnings visibles | biblioteca:", lib_path)
print("Librerías cargadas correctamente.")


# %%
# =========================================================================
# CELDA: FUNCIONES AUXILIARES Y LECTURA ADST (Versión v17 - High Performance & Documentada)
# =========================================================================

# Esquemas explícitos para que un archivo sin módulos también tenga columnas.
# Son listas, no funciones auxiliares: no cambian los cálculos.
LEGACY_COLUMNS = ["event_id","logE_MC","theta_MC","phi_MC","primary","logE_REC","theta_REC","phi_REC","counterId","moduleId","nMuones_REC","nMuones_MC","module_status","is_sd_saturated","x_plane","y_plane","phi_plane_sp","phi_plane_ground","phi_plane_ground_mc","phi_plane_euler_MC","phi_plane_euler_MC_true_core","r_core","r_core_err","r_core_MC","is_true_umd_pos","phi_plane_sp_umd_counter","phi_plane_sp_umd_module","phi_plane_darko_rec","phi_plane_darko_mc","r_umd_rec","r_umd_mc","sdId","sdSignal_REC","sd_nMuons_MC","sd_nEM_MC","sdSignal_err","sdMuonSignal_REC"]
MODULE_COLUMNS = LEGACY_COLUMNS + ["source","has_sd_rec","has_umd_sim_counter","n_umd_channels","n_umd_channels_mc","umd_mc_complete","nMuones_MC_available"]
SD_COLUMNS = ["source","event_id","sdId","logE_MC","theta_MC","phi_MC","primary","has_sd_rec","sd_nMuons_MC","sd_nEM_MC","sdSignal_REC","sdSignal_err","sdMuonSignal_REC","is_sd_saturated","r_core_MC","phi_plane_MC","phi_plane_euler_MC_true_core","mc_geometry_available","geometry_note"]

def getModuleList(counter, sim=True):
    """
    Obtiene la lista de objetos 'Module' (segmentos de detector)
    asociados a un 'Counter' (estación UMD).
    
    Parameters:
    ----------
    counter : ROOT.mevt.Counter
        La estación UMD de la cual extraer los módulos.
    sim : bool, default=True
        Flag para indicar si son datos de simulación.
        - True (Simulación): IDs de módulo son 0, 1, 2...
        - False (Datos Reales): IDs de módulo son 100, 101, 102...
    """
    possibleModules = range(0, 6) if sim else range(100, 116)
    modules = []
    for modId in possibleModules:
        if counter.HasModule(modId):
            modules.append(counter.GetModule(modId))
    return modules

# %% [markdown]
# ## Lector corregido: dos bucles independientes dentro del mismo evento
#
# 1. Leer shower/globales como v17.
# 2. Guardar TODAS las estaciones SD simuladas, con/sin HasStation y con/sin UMD.
#    Las coordenadas MC son las usadas por el extractor que produjo el gráfico.
# 3. Recorrer counters/módulos UMD como antes, pero sin descartar por HasStation
#    ni por simCounter nulo. Se protegen los getters que realmente necesitan esos objetos.
# 4. Devolver ambas tablas y un resumen de cobertura. No recalcular una señal REC
#    cuando su objeto no existe; sólo recuperar los conteos MC ya serializados.
#
# No se podan ramas ROOT. No se aplican cortes físicos al leer: theta/radio/IDs se
# seleccionan después, al reproducir el gráfico. En anillo sin geometría REC se
# conserva la fila con coordenadas ausentes, no se inventa su posición.
# Un fallo de lectura antes del número de eventos anunciado por el archivo es error.
# Un fallo de getter obligatorio también. Los fallos de posición se registran/avisan.

# %%
def readADST_surface_v18(fname, is_mc_simulation=True, max_events=None):
    """
    Leer un archivo ADST (1 fila por MÓDULO).
    
    Esta función es el corazón del pipeline de procesamiento. Itera sobre
    cada evento (lluvia) en un archivo ADST y extrae la información
    relevante a nivel de MÓDULO de UMD (el nivel más granular).
    
    Lógica Clave:
    1. Guarda SD simulado independientemente; después recorre los counters UMD.
    2. Usa el SDEvent como "diccionario" de geometría.
    3. Guarda flags sin cortar por HasStation ni descartar por simCounter nulo.
    4. Versión HÍBRIDA/ESTRICTA: Calcula posiciones 2D, rotaciones Euler (con +180 histórico)
       y la matemática estricta de Darko (C++ nativo sin +180).
    5. Guarda la señal REC y MC para el UMD y SD por separado.
    
    [ACTUALIZACIÓN v17]: Optimización estricta de PyROOT. Se eliminaron las llamadas a 
    'hasattr()' que generaban bloqueos de Mutex globales y destruían el Multiprocessing.
    """
    
    print(f"Iniciando lectura de: {os.path.basename(fname)}")
    
    if not os.path.exists(fname):
        raise FileNotFoundError(fname)

    # --- Inicialización de ROOT ---
    files = ROOT.std.vector('string')()
    files.push_back(fname)

    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    geo = ROOT.DetectorGeometry()
    
    if file1.ReadDetectorGeometry(geo) != ROOT.RecEventFile.eSuccess:
        file1.Close(False)
        raise RuntimeError(f"No se pudo leer DetectorGeometry: {fname}")
    file1.SetBuffers(event)

    data = []                 # Filas por módulo: columnas originales + disponibilidad.
    data_sd = []              # Filas SD independientes de TODO requisito UMD.
    event_ids = []            # Incluye eventos sin ninguna fila UMD.
    geometry_skips = 0
    event_count = 0
    start_time = time.time()

    expected_events = int(file1.GetNEvents())
    if max_events is not None:
        if max_events <= 0:
            file1.Close(False)
            raise ValueError("max_events debe ser positivo o None.")
        expected_events = min(expected_events, max_events)

    try:
        # --- COMIENZA EL BUCLE DE EVENTOS ---
        while event_count < expected_events:
            if file1.ReadNextEvent() != ROOT.RecEventFile.eSuccess:
                raise RuntimeError(f"Lectura incompleta: {event_count}/{expected_events} eventos en {fname}")
            event_count += 1
            if event_count % 500 == 0:
                print(f"... procesados {event_count} eventos.")
            
            # --- Info Global del Evento (Lluvia) ---
            event_id_lluvia = str(event.GetEventId())
            event_ids.append(event_id_lluvia)
            
            # Simulación
            MCShower = event.GetGenShower()
            mc_energy = MCShower.GetEnergy()
            logE_MC = np.log10(mc_energy) if mc_energy > 0 else np.nan

            # Guardamos ángulos MC en Grados y RADIANES
            mc_theta_rad = MCShower.GetZenith()
            mc_phi_rad = MCShower.GetAzimuth()
            
            theta_MC = MCShower.GetZenith() * 180.0 / np.pi
            phi_MC = MCShower.GetAzimuth() * 180.0 / np.pi
            primary = MCShower.GetShortPrimaryName()
            
            # True Core MC (Lorenzo Fix)
            pos_core_MC = MCShower.GetCoreSiteCS()
            
            # Reconstrucción
            sEvent = event.GetSDEvent()
            sShower = sEvent.GetSdRecShower()
            rec_energy = sShower.GetEnergy()
            logE_REC = np.log10(rec_energy) if rec_energy > 0 else np.nan
            
            # Ángulos
            theta_REC_deg = sShower.GetZenith() * 180.0 / np.pi
            phi_REC_deg = sShower.GetAzimuth() * 180.0 / np.pi

            rec_theta_rad = sShower.GetZenith()
            rec_phi_rad = sShower.GetAzimuth()
            
            # Core REC (Usamos el Core Reconstruido como pivote)
            pos_core = sShower.GetCoreSiteCS()
        
            # ================================================================
            # NUEVO: SD SIMULADO PRIMERO. Ningún continue del bucle UMD puede
            # eliminar estas filas. Esta población es la de la figura objetivo.
            # ================================================================
            for simStation in sEvent.GetSimStationVector():
                sd_id = int(simStation.GetId())
                has_sd_rec = bool(sEvent.HasStation(sd_id))
                rec_station = sEvent.GetStationById(sd_id) if has_sd_rec else None

                # El conteo MC existe independientemente del objeto reconstruido.
                # No se captura AttributeError: si la biblioteca no proporciona los
                # getters necesarios, el archivo falla, no fabrica NaN silenciosos.
                n_mu = float(simStation.GetNumberOfMuons())
                n_em = float(simStation.GetNumberOfElectrons()) + float(simStation.GetNumberOfPhotons())

                # Mismo TVector3, núcleo MC, rotaciones, hypot y atan2 del extractor
                # que produjo adst_counts_fast.csv. Guardamos también phi en radianes
                # sin +pi, para no introducir otra convención al reproducir la figura.
                sd_r, sd_phi, geometry_note = np.nan, np.nan, ""
                try:
                    sd_pos = geo.GetStationPosition(sd_id)
                except Exception as exc:
                    alternate = sd_id + 100000 if sd_id < 90000 else sd_id - 100000
                    try:
                        sd_pos = geo.GetStationPosition(alternate)
                        geometry_note = f"fallback_ID_{alternate}"
                    except Exception as fallback_exc:
                        sd_pos = None
                        geometry_note = f"{type(exc).__name__}: {exc}; fallback: {fallback_exc}"
                        print(f"ADVERTENCIA SD sin geometría: evento={event_id_lluvia}, SD={sd_id}: {geometry_note}", flush=True)
                if sd_pos is not None:
                    vector = ROOT.TVector3(sd_pos.X()-pos_core_MC.X(), sd_pos.Y()-pos_core_MC.Y(), sd_pos.Z()-pos_core_MC.Z())
                    vector.RotateZ(-mc_phi_rad)
                    vector.RotateY(-mc_theta_rad)
                    sd_r = math.hypot(vector.X(), vector.Y())
                    sd_phi = math.atan2(vector.Y(), vector.X())

                data_sd.append({
                    "source": os.path.basename(fname), "event_id": event_id_lluvia,
                    "sdId": sd_id, "logE_MC": logE_MC, "theta_MC": theta_MC,
                    "phi_MC": phi_MC, "primary": str(primary),
                    "has_sd_rec": has_sd_rec, "sd_nMuons_MC": n_mu, "sd_nEM_MC": n_em,
                    "sdSignal_REC": float(rec_station.GetTotalSignal()) if has_sd_rec else np.nan,
                    "sdSignal_err": float(rec_station.GetTotalSignalError()) if has_sd_rec else np.nan,
                    "sdMuonSignal_REC": float(rec_station.GetMuonSignal()) if has_sd_rec else np.nan,
                    "is_sd_saturated": bool(rec_station.IsLowGainSaturated()) if has_sd_rec else None,
                    "r_core_MC": sd_r, "phi_plane_MC": sd_phi,
                    "phi_plane_euler_MC_true_core": (sd_phi + np.pi + 2*np.pi) % (2*np.pi),
                    "mc_geometry_available": sd_pos is not None, "geometry_note": geometry_note,
                })

            # --- Bucle sobre los COUNTERS (UMD; ya NO decide qué SD guardamos) ---
            mEvent = event.GetMDEvent()
            counterIterator = mEvent.CountersBegin()
            countersEnd = mEvent.CountersEnd()
            
            while counterIterator != countersEnd:
                
                counter = counterIterator.__deref__() # Objeto Counter (estación)
                counterId = counter.GetId()            
                sdId = counter.GetSdPartnerId()    

                has_sd_rec = bool(sEvent.HasStation(sdId))
                sdStation = sEvent.GetStationById(sdId) if has_sd_rec else None

                if has_sd_rec:
                    # Misma lectura REC cuando existe la estación.
                    is_sd_saturated = sdStation.IsLowGainSaturated()
                    sdSignal = sdStation.GetTotalSignal()
                    sdSignal_err = sdStation.GetTotalSignalError()
                    sdMuonSignal = sdStation.GetMuonSignal()
                else:
                    # Sin REC: conservar fila y MC, no inventar una señal VEM.
                    is_sd_saturated = None
                    sdSignal = np.nan
                    sdSignal_err = np.nan
                    sdMuonSignal = np.nan

                # --- CÁLCULO DE COMPONENTES MC (CONTEO DE PARTICULAS) ---
                mc_sd_n_muon = np.nan
                mc_sd_n_em = np.nan # Suma de electrones + fotones
                
                # [OPTIMIZACIÓN v17]: Reemplazamos los múltiples hasattr() por un try/except.
                # PyROOT bloquea el Mutex global al buscar métodos inexistentes con hasattr(), 
                # hundiendo la performance del multiprocessing.
                if hasattr(sEvent, "HasSimStation") and sEvent.HasSimStation(sdId):
                    simStation = sEvent.GetSimStationById(sdId)
                    # No esconder un getter obligatorio ausente: detener el archivo.
                    mc_sd_n_muon = float(simStation.GetNumberOfMuons())
                    n_e = float(simStation.GetNumberOfElectrons())
                    n_gamma = float(simStation.GetNumberOfPhotons())
                    mc_sd_n_em = n_e + n_gamma

                r_core_err = sdStation.GetSPDistanceError() if has_sd_rec else np.nan

                # ==================================================================
                # BIFURCACIÓN CORRECTA (Lógica Adaptada a IDs Mixtos) - Lazy Loading 
                # ==================================================================

                # Definimos si es Infill (físico o lógico) para saber qué camino tomar
                # Infill Físico: ~4000 a 6000. Infill Lógico: ~104000 a 106000.
                # Anillo Denso: 90000 a 99999.
                is_infill = (sdId >= 100000) or (2000 < sdId < 90000)
                is_anillo_denso = (90000 <= sdId < 100000)

                # Inicialización de todas las variables geométricas
                phi_plane_ground = np.nan
                phi_plane_ground_mc = np.nan
                phi_plane_euler_MC = np.nan
                phi_plane_euler_MC_true_core = np.nan
                r_core_MC = np.nan
                
                is_true_umd_pos = False
                phi_plane_sp_umd_counter = np.nan
                phi_plane_sp_umd_module = np.nan
                phi_plane_darko_rec = np.nan
                phi_plane_darko_mc = np.nan
                r_umd_rec = np.nan
                r_umd_mc = np.nan

                # --- 1. PHI NATIVO (SP del SD) ---
                # Para Infill (cualquiera de los dos), SP suele ser absoluto (Norte), hay que restar la lluvia.
                # Para Denso (90k), SP ya es relativo.
                val_sp = sdStation.GetAzimuthSP() if has_sd_rec else np.nan
                if is_infill:
                    phi_sp = val_sp - rec_phi_rad
                else:
                    phi_sp = val_sp
                phi_plane_sp = (phi_sp + 2*np.pi) % (2*np.pi)

                # ==================================================================
                # ⚠️ DISCLAIMER UMD AZIMUTH NATIVO (COUNTER LEVEL) ⚠️
                # Históricamente intentábamos extraer el Azimuth nativo del UMD así:
                #
                # if hasattr(counter, "GetAzimuthSP"):
                #     val_sp_umd_c = counter.GetAzimuthSP()
                #     phi_plane_sp_umd_counter = (val_sp_umd_c - rec_phi_rad + 2*np.pi) % (2*np.pi) if is_infill else (val_sp_umd_c + 2*np.pi) % (2*np.pi)
                #
                # Análisis de datos en la v16 demostró que MdRecCounter NO guarda esta 
                # variable (100% NaNs). Al fallar el hasattr() repetidamente, PyROOT 
                # generaba contención de hilos (Mutex lock) reduciendo el uso de CPU 
                # al 30% en paralelizacion. Se comenta por performance reasons.
                # ==================================================================

                if is_anillo_denso:
                    # --- CASO A: ANILLO DENSO (UMD 90k) ---
                    # NO PEDIMOS geo.GetStationPosition() AQUÍ. Usamos directamente 
                    # las variables pre-calculadas del SP al funcionar bien y ser las correctas.
                    
                    if has_sd_rec:
                        phi_rel = sdStation.GetAzimuthSP()
                        r_final = sdStation.GetSPDistance()
                        x_plane = r_final * np.cos(phi_rel)
                        y_plane = r_final * np.sin(phi_rel)
                        # Se mantienen los valores históricos del anillo con REC.
                        r_core_MC = r_final
                        r_umd_rec = r_final
                        r_umd_mc = r_final
                    else:
                        # Este lector no inventa coordenadas del anillo sin SD REC.
                        r_final = x_plane = y_plane = np.nan
                    
                else:
                    # --- CASO B: INFILL (4k o 104k) / ESTÁNDAR ---
                    # --- EXTRACCIÓN DE POSICIONES FÍSICAS ---
                    
                    # A. Posición del Tanque SD
                    try:
                        pos_station = geo.GetStationPosition(sdId)
                    except:
                        # Si falla con el ID que tenemos, probamos el "otro" por las dudas (parche de seguridad)
                        try:
                            alt_id = sdId + 100000 if sdId < 90000 else sdId - 100000
                            pos_station = geo.GetStationPosition(alt_id)
                        except Exception as exc:
                            geometry_skips += 1
                            print(f"ADVERTENCIA UMD: evento={event_id_lluvia}, counter={counterId}, SD={sdId}: sin geometría: {exc}", flush=True)
                            counterIterator += 1
                            continue  # Sólo UMD: la fila SD ya fue guardada.
                            
                    # B. [NUEVO] Posición del Módulo UMD enterrado
                    is_true_umd_pos = True
                    try:
                        pos_umd = geo.GetStationPosition(counterId)
                    except:
                        try:
                            alt_umd_id = counterId + 100000 if counterId < 90000 else counterId - 100000
                            pos_umd = geo.GetStationPosition(alt_umd_id)
                        except:
                            pos_umd = pos_station # Fallback seguro al SD si el UMD no está en la base de datos de geometría
                            is_true_umd_pos = False

                    # --- 3. CÁLCULOS HISTÓRICOS (Usando Posición SD) ---
                    dx = pos_station.X() - pos_core.X()
                    dy = pos_station.Y() - pos_core.Y()
                    dz = pos_station.Z() - pos_core.Z()

                    # Ground (2D puramente sobre Core REC)
                    phi_g_abs = np.arctan2(dy, dx)
                    phi_plane_ground = (phi_g_abs - rec_phi_rad + 2*np.pi) % (2*np.pi)

                    # Ground MC (2D puramente sobre Core MC)
                    dx_mc = pos_station.X() - pos_core_MC.X()
                    dy_mc = pos_station.Y() - pos_core_MC.Y()
                    dz_mc = pos_station.Z() - pos_core_MC.Z()
                    phi_g_abs_mc = np.arctan2(dy_mc, dx_mc)
                    phi_plane_ground_mc = (phi_g_abs_mc - mc_phi_rad + 2*np.pi) % (2*np.pi)

                    # --- 4. PHI EULER (3D) - MANTIENE CONVENCIÓN +180 ---
                    
                    # Euler Fix (3D - MC Angles, REC Core)
                    v_sd_rec = ROOT.TVector3(dx, dy, dz)
                    v_sd_rec.RotateZ(-mc_phi_rad)   
                    v_sd_rec.RotateY(-mc_theta_rad) 
                    phi_e_mc_raw = np.arctan2(v_sd_rec.Y(), v_sd_rec.X())
                    # APLICAMOS TU ROTACIÓN +180 (Solo a Euler para testear)
                    phi_plane_euler_MC = (phi_e_mc_raw + np.pi + 2*np.pi) % (2*np.pi)
                    
                    r_final = np.sqrt(v_sd_rec.X()**2 + v_sd_rec.Y()**2)
                    x_plane = v_sd_rec.X() 
                    y_plane = v_sd_rec.Y()

                    # True Core Fix (3D - MC Angles, MC Core)
                    v_sd_mc = ROOT.TVector3(dx_mc, dy_mc, dz_mc)
                    v_sd_mc.RotateZ(-mc_phi_rad)   
                    v_sd_mc.RotateY(-mc_theta_rad) 
                    phi_e_mc_true_raw = np.arctan2(v_sd_mc.Y(), v_sd_mc.X())
                    # Aplicamos el mismo parche +180 para comparar peras con peras
                    phi_plane_euler_MC_true_core = (phi_e_mc_true_raw + np.pi + 2*np.pi) % (2*np.pi)
                    r_core_MC = np.sqrt(v_sd_mc.X()**2 + v_sd_mc.Y()**2)
                    
                    # --- 5. [NUEVO] REPLICAR MATEMÁTICA ESTRICTA DE DARKO (Usando Posición UMD) ---
                    # A diferencia de Euler, NO lleva el +180.
                    if is_true_umd_pos:
                        # A. Darko REC (Core REC, Ángulos MC)
                        dx_umd_rec = pos_umd.X() - pos_core.X()
                        dy_umd_rec = pos_umd.Y() - pos_core.Y()
                        dz_umd_rec = pos_umd.Z() - pos_core.Z()
                        
                        v_umd_rec = ROOT.TVector3(dx_umd_rec, dy_umd_rec, dz_umd_rec)
                        v_umd_rec.RotateZ(-mc_phi_rad)   
                        v_umd_rec.RotateY(-mc_theta_rad) 
                        
                        # Calculamos el azimuth sin sumar Pi, para ver el output puro de Darko
                        phi_darko_raw = np.arctan2(v_umd_rec.Y(), v_umd_rec.X())
                        phi_plane_darko_rec = (phi_darko_raw + 2*np.pi) % (2*np.pi)
                        r_umd_rec = np.sqrt(v_umd_rec.X()**2 + v_umd_rec.Y()**2)

                        # B. Darko MC (Core MC, Ángulos MC)
                        dx_umd_mc = pos_umd.X() - pos_core_MC.X()
                        dy_umd_mc = pos_umd.Y() - pos_core_MC.Y()
                        dz_umd_mc = pos_umd.Z() - pos_core_MC.Z()
                        
                        v_umd_mc = ROOT.TVector3(dx_umd_mc, dy_umd_mc, dz_umd_mc)
                        v_umd_mc.RotateZ(-mc_phi_rad)
                        v_umd_mc.RotateY(-mc_theta_rad)
                        
                        phi_darko_mc_raw = np.arctan2(v_umd_mc.Y(), v_umd_mc.X())
                        phi_plane_darko_mc = (phi_darko_mc_raw + 2*np.pi) % (2*np.pi)
                        r_umd_mc = np.sqrt(v_umd_mc.X()**2 + v_umd_mc.Y()**2)

                # --- INFO MC MÓDULOS ---
                simCounter = mEvent.GetSimCounter(counterId)
                # CORRECCIÓN CENTRAL: la ausencia de simCounter NO elimina módulos.
                # Sólo impide consultar la verdad UMD. Incluso un proxy C++ nullptr
                # distinto de None se reconoce aquí, SIN hacer continue.
                has_umd_sim_counter = simCounter is not None and bool(simCounter)
                    
                # --- Bucle sobre los MÓDULOS (Segmentos) ---
                modules = getModuleList(counter, sim=is_mc_simulation)
                for module in modules:

                    # --- Señal Reconstruida (REC) ---
                    nMuones_REC = module.GetNumberOfEstimatedMuons()
                    moduleId = module.GetId()

                    # --- Estado del Módulo (Flag de Calidad) ---
                    if module.IsCandidate(): status = "candidate"
                    elif module.IsSaturated(): status = "saturated"
                    elif module.IsRejected(): status = "rejected"
                    elif module.IsSilent(): status = "silent"
                    else: status = "undefined"

                    # ==================================================================
                    # ⚠️ DISCLAIMER UMD AZIMUTH NATIVO (MODULE LEVEL) ⚠️
                    # Al igual que en el Counter, buscábamos el azimuth nativo a nivel Módulo:
                    #
                    # if hasattr(module, "GetAzimuthSP"):
                    #     val_sp_mod = module.GetAzimuthSP()
                    #     phi_plane_sp_umd_module = (val_sp_mod - rec_phi_rad + 2*np.pi) % (2*np.pi) if is_infill else (val_sp_mod + 2*np.pi) % (2*np.pi)
                    #
                    # Resultado empírico: 100% de NaNs y hundimiento de performance por 
                    # Mutex lock de PyROOT. Se comenta la extracción.
                    # ==================================================================

                    # --- ❗️ CÁLCULO DE MUONES MC (Verdad) ❗️ ---
                    # Inspo Carmi: Iteramos por los 2 canales (scintillators)
                    # de este módulo y sumamos los muones MC "inyectados".
                    # Compatibilidad: conservar la suma histórica para cotejar v17.
                    # La columna disponible, definida abajo, evita llamarla verdad
                    # completa cuando faltan objetos o resúmenes.
                    nMuones_MC_module = 0.0
                    n_umd_channels = 0
                    n_umd_channels_mc = 0
                    channelIterator = module.ChannelsBegin()
                    channelsEnd = module.ChannelsEnd()
                     
                    # Le preguntamos al 'simCounter' por el 'simScintillator'
                    # que corresponde a este 'moduleId' y 'channelId'
                    while channelIterator != channelsEnd:
                        channel = channelIterator.__deref__()
                        channelId = channel.GetId()
                        n_umd_channels += 1

                        # Cortocircuito: NO se desreferencia un puntero nulo.
                        if has_umd_sim_counter and simCounter.HasSimScintillatorByChannel(moduleId, channelId):
                            mdSimScintillator = simCounter.GetSimScintillatorByChannelId(moduleId, channelId)
                            nMuones_MC_module += mdSimScintillator.GetNumberOfInjectedMuons()
                            n_umd_channels_mc += 1
                            
                        channelIterator += 1
                    # --- ❗️ FIN DEL CÁLCULO MC ❗️ ---
                    umd_mc_complete = has_umd_sim_counter and n_umd_channels > 0 and n_umd_channels_mc == n_umd_channels
                    # "Completo" significa completo entre canales enumerados, no prueba
                    # que todos los canales físicos posibles se hayan serializado.

                    data.append({
                        "event_id": event_id_lluvia,
                        "source": os.path.basename(fname),
                        "has_sd_rec": has_sd_rec,
                        "has_umd_sim_counter": has_umd_sim_counter,
                        "n_umd_channels": n_umd_channels,
                        "n_umd_channels_mc": n_umd_channels_mc,
                        "umd_mc_complete": umd_mc_complete,
                        "nMuones_MC_available": nMuones_MC_module if umd_mc_complete else np.nan,
                        
                        # Info MC
                        "logE_MC": logE_MC, "theta_MC": theta_MC, "phi_MC": phi_MC, "primary": primary,
                        
                        # Info REC
                        "logE_REC": logE_REC, "theta_REC": theta_REC_deg, "phi_REC": phi_REC_deg,
                        
                        # Info Módulo/Counter
                        "counterId": counterId,
                        "moduleId": moduleId,
                        "nMuones_REC": nMuones_REC,
                        "nMuones_MC": nMuones_MC_module,
                        "module_status": status,      
                        "is_sd_saturated": is_sd_saturated,

                        # Info de Geometría (plano de lluvia)
                        "x_plane": x_plane,
                        "y_plane": y_plane,
                        "phi_plane_sp": phi_plane_sp,
                        "phi_plane_ground": phi_plane_ground,
                        "phi_plane_ground_mc": phi_plane_ground_mc,
                        "phi_plane_euler_MC": phi_plane_euler_MC,
                        
                        # [NUEVO v13] Guardamos la geometría MC pura
                        "phi_plane_euler_MC_true_core": phi_plane_euler_MC_true_core,
                        
                        "r_core": r_final,
                        "r_core_err": r_core_err,     
                        "r_core_MC": r_core_MC,
                        
                        # [NUEVO v17] Geometría estricta UMD (Darko)
                        "is_true_umd_pos": is_true_umd_pos,
                        "phi_plane_sp_umd_counter": phi_plane_sp_umd_counter, # Fuerza NaN documentado
                        "phi_plane_sp_umd_module": phi_plane_sp_umd_module,   # Fuerza NaN documentado
                        "phi_plane_darko_rec": phi_plane_darko_rec,
                        "phi_plane_darko_mc": phi_plane_darko_mc,
                        "r_umd_rec": r_umd_rec,
                        "r_umd_mc": r_umd_mc,

                        # Señal SD (REC en VEM + MC Truth en Conteo)
                        "sdId": sdId,
                        "sdSignal_REC": sdSignal,           # Reconstruido (VEM)
                        "sd_nMuons_MC": mc_sd_n_muon,       # Verdad MC (Conteo)
                        "sd_nEM_MC": mc_sd_n_em,            # Verdad MC (Conteo)
                        "sdSignal_err": sdSignal_err,
                        "sdMuonSignal_REC": sdMuonSignal    # REC Muon
                    })

                counterIterator += 1 # Avanzamos al siguiente counter
                    
    finally:
        file1.Close(False)  # Sólo lectura; también cerrar si un getter falla.

    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"Lectura completa. Total de eventos leídos: {event_count}")
    print(f"Tiempo total de lectura: {elapsed:.2f} segundos.")
    print(f"Total de 'MÓDULOS' (filas) extraídos: {len(data)}")

    df = pd.DataFrame(data, columns=MODULE_COLUMNS)
    df_sd = pd.DataFrame(data_sd, columns=SD_COLUMNS)
    assert not df.duplicated(["source", "event_id", "counterId", "moduleId", "sdId"]).any()
    assert not df_sd.duplicated(["source", "event_id", "sdId"]).any()
    assert len(set(event_ids)) == len(event_ids), "event_id duplicado en el archivo."
    # DataFrames vacíos también conservan esquema booleano para el filtro.
    for column in ["has_sd_rec", "has_umd_sim_counter", "umd_mc_complete"]:
        df[column] = df[column].astype(bool)
    for column in ["has_sd_rec", "mc_geometry_available"]:
        df_sd[column] = df_sd[column].astype(bool)
    summary = {"source": os.path.basename(fname), "events_read": event_count,
               "events_expected": expected_events, "event_ids": event_ids,
               "sd_rows": len(df_sd), "sd_without_rec": int((~df_sd.has_sd_rec).sum()),
               "module_rows": len(df), "modules_without_simcounter": int((~df.has_umd_sim_counter).sum()),
               "umd_geometry_skips": geometry_skips}
    print(f"{os.path.basename(fname)}: SD={len(df_sd)}, sin REC={summary['sd_without_rec']}, módulos={len(df)}", flush=True)
    return df, df_sd, summary



# %% [markdown]
# ## Wrapper por archivo: guardar ambas tablas y exigir equivalencia UMD
#
# Se sigue usando process_file_wrapper + partial + Pool, como en v8-2.
# La diferencia es que una llamada devuelve dos tablas. Se guardan en carpetas
# distintas para no duplicar SD por número de módulos ni inventar módulos ausentes.
#
# Si legacy_dir está configurado, las filas UMD con HasStation=True DEBEN coincidir
# con el parquet viejo, fila por fila y columna por columna. Un fallo detiene la
# tanda; no cuenta como éxito. Para otras producciones elegí su referencia o None
# explícitamente: None significa sin cotejo externo, nunca equivalencia demostrada.
#
# Los warnings ROOT no se suprimen. Se conserva stdout/stderr de cada archivo,
# incluidos mensajes C++, en logs/archivo.log; se anuncia esa ruta ANTES de leer.
# La redirección de descriptores es necesaria porque redirect_stderr de Python
# solo no captura los mensajes C++. No cambia ningún dato ni configuración Offline.
# Al terminar se imprimen los avisos y el conteo; ante excepción se conserva el log.
# Un mensaje nativo "Error in <...>" impide aceptar el archivo.

# %%
def process_file_wrapper(root_fpath, output_dir, legacy_dir=None, max_events=None):
    filename = os.path.basename(root_fpath)
    stem = Path(filename).stem
    output_dir = Path(output_dir)
    log_path = output_dir / "logs" / (stem + ".log")
    print(f"► {filename} | log completo (incluye warnings): {log_path}", flush=True)

    # Se restaura SIEMPRE la salida del proceso, también cuando un archivo falla.
    sys.stdout.flush()
    sys.stderr.flush()
    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    result = None
    try:
        with log_path.open("x", buffering=1) as log:
            os.dup2(log.fileno(), 1)
            os.dup2(log.fileno(), 2)
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                try:
                    ROOT.gErrorIgnoreLevel = ROOT.kInfo
                    print("ROOT", ROOT.gROOT.GetVersion(), "| nivel", ROOT.gErrorIgnoreLevel,
                          "| archivo", root_fpath, flush=True)
                    started = time.time()
                    df, df_sd, summary = readADST_surface_v18(root_fpath, max_events=max_events)
                    log.flush()
                    root_errors = [line for line in log_path.read_text(errors="replace").splitlines()
                                   if "Error in <" in line or "Fatal in <" in line]
                    if root_errors:
                        raise RuntimeError("ROOT informó errores nativos; revisar log, no aceptar el archivo.")

                    # Mismos metadatos de v8-2; el modelo ahora puede contener '_'.
                    match = re.fullmatch(r"(.+?)_(\d+)_(\d+)_([^_]+)_.+_Run(\d+)\.root", filename)
                    if match is None:
                        raise ValueError("Nombre de archivo no reconocido: " + filename)
                    model, lo, hi, primary_name, run = match.groups()
                    metadata = {"model_mc": model, "e_min_mc": float(lo)/10,
                                "e_max_mc": float(hi)/10, "primary_name_mc": primary_name,
                                "run_number": int(run)}
                    for key, value in metadata.items():
                        df[key] = value
                        df_sd[key] = value

                    legacy_status = "no_configurado"
                    if legacy_dir is not None:
                        old_path = Path(legacy_dir) / (stem + ".parquet")
                        old = pd.read_parquet(old_path)  # Falta de archivo = error, no skip.
                        selected = df.loc[df["has_sd_rec"]].copy()
                        old["event_id"] = old["event_id"].astype(str)
                        selected["event_id"] = selected["event_id"].astype(str)
                        if max_events is not None:
                            # Sólo un piloto explícito se coteja en los eventos leídos.
                            old = old.loc[old.event_id.isin(summary["event_ids"])].copy()
                        keys = ["event_id", "counterId", "moduleId", "sdId"]
                        assert not old.duplicated(keys).any(), "Referencia con filas duplicadas."
                        missing = set(old.columns) - set(selected.columns)
                        assert not missing, f"Columnas antiguas ausentes: {missing}"
                        old = old.sort_values(keys).reset_index(drop=True)
                        selected = selected.sort_values(keys).reset_index(drop=True)
                        # No usar sólo la intersección: detecta filas perdidas/sobrantes.
                        # Los dtypes pueden volverse nullable al añadir estaciones sin REC.
                        pd.testing.assert_frame_equal(selected[old.columns], old,
                                                      check_dtype=False, check_exact=True)
                        legacy_status = "identico"

                    # Ambos conteos SD provienen de la misma simulación en esta pasada.
                    # Comparar donde las tablas se solapan no elimina el resto del SD.
                    if len(df):
                        key_sd = ["source", "event_id", "sdId"]
                        umd_sd = df.drop_duplicates(key_sd)
                        overlap = umd_sd.merge(df_sd, on=key_sd, suffixes=("_umd","_sd"),
                                               how="inner", validate="one_to_one")
                        for column in ["sd_nMuons_MC", "sd_nEM_MC"]:
                            x, y = overlap[column+"_umd"], overlap[column+"_sd"]
                            assert (x.eq(y) | (x.isna() & y.isna())).all(), column

                    # Escritura exclusiva: nunca sobre los parquet anteriores.
                    for folder, table in [("modulos", df), ("sd_estaciones", df_sd)]:
                        with (output_dir/folder/(stem+".parquet")).open("xb") as stream:
                            table.to_parquet(stream, compression="snappy", index=False)
                    result = {key:value for key,value in summary.items() if key != "event_ids"}
                    result.update(legacy_validation=legacy_status, max_events=max_events,
                                  elapsed_s=time.time()-started)
                    print("ARCHIVO COMPLETO:", result, flush=True)
                except Exception:
                    traceback.print_exc()
                    raise  # Pool transmite el fallo: no se convierte en un string de éxito.
    finally:
        os.dup2(saved_stdout, 1)
        os.dup2(saved_stderr, 2)
        os.close(saved_stdout)
        os.close(saved_stderr)
        # Sin suprimir avisos: además del log permanente, mostrar sus líneas.
        if log_path.exists():
            notices = [line for line in log_path.read_text(errors="replace").splitlines()
                       if any(word in line for word in ["Warning in <", "Error in <", "Fatal in <", "ADVERTENCIA"])]
            for line in notices:
                print(f"[{filename}] {line}", flush=True)
            print(f"{filename} | avisos conservados: {len(notices)} | log: {log_path}", flush=True)
    print(f"✔ {filename} | SD={result['sd_rows']} | módulos={result['module_rows']} | referencia={result['legacy_validation']}", flush=True)
    return result

# %% [markdown]
# ## Configurar y procesar TODA la tanda
#
# Esta configuración ya usa todos los archivos, no all_root_files[:1].
# Cada proceso trabaja con un archivo: ocho procesos sólo ayudan si hay varios.
# No se procesó toda la producción al preparar este cuaderno. Ejecutar la celda
# de abajo consume recursos reales del servidor: coordinar el número de workers.
# Para otras tandas cambiá entrada, salida y referencia, como en tu código anterior.
#
# La salida debe ser una carpeta nueva. Un run incompleto conserva logs/archivos
# para inspección, pero NO obtiene archivos_completos.csv. No mezclarlo con otro run.
# No es obligatorio un piloto, pero una prueba explícita de un archivo es prudente.

# %%
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton"
output_dir = "/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA/claude_work/revision_asimetrias_sd_umd/02_notebooks/04_reprocesamiento/datos_generados/sd_umd_completo_001"
legacy_dir = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17"

all_root_files = sorted(glob.glob(os.path.join(base_path, "*.root")))
root_files_a_procesar = all_root_files  # TODA la tanda, no [:1].
n_workers = 8
max_events = None                     # TODOS los eventos de cada archivo.
# Prueba opcional, explícita: root_files_a_procesar = all_root_files[:1]; n_workers = 1
# Para otro modelo/primario, indicar SU legacy_dir; None omite sólo el cotejo externo.

print("Archivos:", len(root_files_a_procesar), "| workers:", n_workers, "| límite eventos:", max_events)
print("Salida NUEVA:", output_dir)

# %%
# ESTA CELDA ES LA QUE PROCESA. No se ejecutó al generar la entrega.
if not root_files_a_procesar:
    raise FileNotFoundError("No hay ROOT: revisar base_path.")
if n_workers < 1:
    raise ValueError("n_workers debe ser positivo.")
# En Jupyter este Pool de funciones de celda requiere el método fork de Linux.
# No se cambia el método global: si no corresponde, explicar antes de lanzar.
if n_workers > 1 and get_start_method() != "fork":
    raise RuntimeError("Este Pool de notebook requiere un kernel Linux con fork. No lanzar con spawn/forkserver.")

os.makedirs(output_dir, exist_ok=False)
for folder in ["modulos", "sd_estaciones", "logs", "resultados"]:
    os.makedirs(os.path.join(output_dir, folder), exist_ok=False)
# Lista inicial = qué se pidió; lista final = qué terminó. No mezclar tandas.
pd.DataFrame({"source":[os.path.basename(f) for f in root_files_a_procesar]}).to_csv(
    os.path.join(output_dir, "archivos_solicitados.csv"), index=False
)
process_func = partial(process_file_wrapper, output_dir=output_dir,
                       legacy_dir=legacy_dir, max_events=max_events)
started = time.time()
if n_workers == 1:
    results = [process_func(f) for f in root_files_a_procesar]
else:
    with Pool(processes=n_workers) as pool:
        results = pool.map(process_func, root_files_a_procesar, chunksize=1)

completed = pd.DataFrame(results)
assert len(completed) == len(root_files_a_procesar)
assert completed.events_read.eq(completed.events_expected).all()
completed.to_csv(os.path.join(output_dir, "archivos_completos.csv"), index=False)
print(completed.to_string(index=False))
print("Minutos:", (time.time()-started)/60)

# %% [markdown]
# ## Leer la tanda terminada — SD y UMD NO se mezclan por filas
#
# Leer solamente los nombres que aparecen en archivos_completos.csv evita que
# archivos sobrantes o de otro intento entren por un glob indiscriminado.
# Esta celda requiere memoria para las dos tablas; para grandes producciones
# procesar/analizar por tanda. El lector ROOT sólo mantiene un archivo por worker.
# La columna nMuones_MC mantiene la definición histórica; para verdad disponible
# usar nMuones_MC_available y estudiar la dependencia de su disponibilidad con phi.

# %%
completed = pd.read_csv(os.path.join(output_dir, "archivos_completos.csv"))
requested = pd.read_csv(os.path.join(output_dir, "archivos_solicitados.csv"))
assert completed.source.is_unique and requested.source.is_unique
assert set(completed.source) == set(requested.source), "Tanda incompleta."
assert completed.events_read.eq(completed.events_expected).all()
df_sd = pd.concat([pd.read_parquet(Path(output_dir)/"sd_estaciones"/Path(f).with_suffix(".parquet"))
                   for f in completed.source], ignore_index=True)
df_modulos = pd.concat([pd.read_parquet(Path(output_dir)/"modulos"/Path(f).with_suffix(".parquet"))
                        for f in completed.source], ignore_index=True)
assert len(df_sd) == completed.sd_rows.sum()
assert len(df_modulos) == completed.module_rows.sum()
assert not df_sd.duplicated(["source","event_id","sdId"]).any()
assert not df_modulos.duplicated(["source","event_id","counterId","moduleId","sdId"]).any()
print("SD: todas / HasStation / sin HasStation:",
      len(df_sd), int(df_sd.has_sd_rec.sum()), int((~df_sd.has_sd_rec).sum()))
print("UMD módulos: todos / HasStation:",
      len(df_modulos), int(df_modulos.has_sd_rec.sum()))
# Para reproducir el análisis viejo de módulos:
df_infill = df_modulos.loc[df_modulos.counterId.ge(100000) & df_modulos.has_sd_rec].copy()
# Para el gráfico antes/después de SD NO usar df_infill, sino df_sd.

# %% [markdown]
# ## Reproducir exactamente el gráfico SD_antes_despues_mismos_bins.pdf
#
# La tabla usada aquí es SD, una fila por estación/evento. La definición es la
# misma que en la sección 5 del cuaderno de reproducción: IDs físicos Infill,
# 30≤theta<40°, doce bins phi, ocho bandas radiales y ajuste ponderado por SEM.
# A1 positivo = exceso temprano; A1 negativo = exceso tardío.
# NO se selecciona por presencia UMD, señal REC positiva, Nmu positivo ni dropna global.
# Antes = todos los SD de esa selección; después = has_sd_rec=True en los mismos SD.
# El resultado se calcula desde el parquet nuevo; nunca se dibuja una curva
# precargada ni se reemplaza una discrepancia por valores de referencia.

# %%
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

physical_infill = df_sd.sdId.gt(2000) & df_sd.sdId.lt(90000)
assert df_sd.loc[physical_infill, "mc_geometry_available"].all(), "Hay SD Infill sin geometría: revisar logs."
sd_plot = df_sd.loc[physical_infill & df_sd.theta_MC.ge(30) & df_sd.theta_MC.lt(40)
                    & df_sd.r_core_MC.ge(150) & df_sd.r_core_MC.lt(1800)].copy()
sd_plot["phi_MC_Truth"] = np.rad2deg(sd_plot["phi_plane_MC"])
r_edges = np.array([150,300,450,600,750,900,1050,1200,1350])
phi_bin_edges = np.linspace(-180,180,13)
phi_centers = (phi_bin_edges[1:]+phi_bin_edges[:-1])/2

# %%
def harmonic_model(phi_deg, A1):
    """La misma función: ángulo en grados, A1 positivo = temprano."""
    return 1.0 + A1 * np.cos(np.deg2rad(phi_deg))


def fit_one_band(table, column):
    """Reproduce la lógica de la celda recibida y añade sólo diagnósticos."""
    result = {
        "A1": np.nan, "error": np.nan, "n_rows": len(table),
        "n_nonnull": len(table.dropna(subset=[column])),
        "valid_phi_bins": 0, "status": "menos de 15 filas",
    }
    if result["n_nonnull"] < 15:
        return result

    local = table.copy()
    local["bin_phi"] = pd.cut(local["phi_MC_Truth"], bins=phi_bin_edges)
    statistics = local.groupby("bin_phi", observed=False)[column].agg(["mean", "sem"])
    y_means, y_errs = statistics["mean"].values, statistics["sem"].values
    norm = np.nanmean(y_means)
    result["status"] = "normalización no positiva"
    if not (norm > 0 and not np.isnan(norm)):
        return result
    y_norm, y_err_norm = y_means / norm, y_errs / norm
    valid = ~np.isnan(y_norm) & ~np.isnan(y_err_norm) & (y_err_norm > 0)
    result["valid_phi_bins"] = int(valid.sum())
    result["status"] = "menos de cinco bins válidos"
    if valid.sum() < 5:
        return result
    try:
        popt, pcov = curve_fit(
            harmonic_model, phi_centers[valid], y_norm[valid],
            sigma=y_err_norm[valid], absolute_sigma=True, bounds=(-2.0, 2.0),
        )
        A1, error = popt[0], np.sqrt(np.diag(pcov))[0]
        if error > 0.5:
            result["status"] = "error superior a 0.5"
        else:
            result.update(A1=float(A1), error=float(error), status="ok")
    except Exception as exc:
        result["status"] = type(exc).__name__ + ": " + str(exc)
    return result


# %%
selection_rows = []
for column in ["sd_nMuons_MC", "sd_nEM_MC"]:
    for sample, table in [("Antes de HasStation", sd_plot),
                          ("HasStation=True", sd_plot.loc[sd_plot.has_sd_rec])]:
        for r_min, r_max in zip(r_edges[:-1], r_edges[1:]):
            band = table.loc[table.r_core_MC.ge(r_min) & table.r_core_MC.lt(r_max)]
            selection_rows.append({"column":column, "sample":sample, "r_min":r_min,
                                   "r_max":r_max, "r_center":(r_min+r_max)/2,
                                   **fit_one_band(band, column)})
selection_fits = pd.DataFrame(selection_rows)
print(selection_fits.to_string(index=False))

# %% [markdown]
# ## Cotejo con los datos que realmente originaron el PDF
#
# Estas referencias corresponden sólo a SIBYLL/protón 17.5–18.0 de esa producción.
# Para otra tanda poner ambas rutas en None: se calcula su figura sin afirmar
# que deba coincidir con el PDF de protones. No ajustar nunca el resultado al PDF.
#
# Primero se exige igualdad del inventario SD (claves, flags, conteos y geometría),
# luego del ajuste cuando está TODA la producción. Un archivo completo individual
# puede validar sus filas contra la referencia, pero no el PDF agregado de veinte.
# Un piloto limitado en eventos no se certifica como lectura completa.
# Los errores comparados son los SEM/formales originales, no bootstrap.

# %%
reference_raw_csv = Path("/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA/claude_work/revision_asimetrias_sd_umd/04_soporte/tablas/adst_counts_fast.csv")
reference_fit_csv = Path("/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA/claude_work/revision_asimetrias_sd_umd/02_notebooks/02_reproduccion/resultados/seleccion_mismos_bins_ajuste_ponderado.csv")
full_pdf_verified = False
if reference_raw_csv is not None:
    assert completed.max_events.isna().all(), "Piloto limitado: no certificar como archivo completo."
    reference_all = pd.read_csv(reference_raw_csv, dtype={"source":str, "event_id":str})
    processed_files = set(completed.source)
    reference_files = set(reference_all.source)
    assert processed_files <= reference_files, "Referencia de otra producción: elegir la correcta o None."
    reference = reference_all.loc[reference_all.source.isin(processed_files)].copy()
    comparison = sd_plot.merge(reference, on=["source","event_id","sdId"], how="outer",
                               validate="one_to_one", indicator=True)
    assert comparison._merge.eq("both").all(), comparison._merge.value_counts().to_dict()
    assert comparison.has_sd_rec.eq(comparison.has_rec.astype(bool)).all()
    assert comparison.sd_nMuons_MC.eq(comparison.mu).all()
    assert comparison.sd_nEM_MC.eq(comparison.em).all()
    assert np.allclose(comparison.r_core_MC, comparison.r, rtol=0, atol=1e-6)
    delta_phi = (comparison.phi_plane_MC-comparison.phi+np.pi) % (2*np.pi)-np.pi
    assert np.abs(delta_phi).max() < 1e-10
    print("Inventario SD idéntico a la extracción anterior para los archivos procesados.")

    if processed_files == reference_files and reference_fit_csv is not None:
        reference_fits = pd.read_csv(reference_fit_csv)
        reference_fits = reference_fits.loc[reference_fits["sample"].isin(["Antes de HasStation","HasStation=True"])]
        keys = ["column","sample","r_min","r_max"]
        check = selection_fits.merge(reference_fits, on=keys, how="outer",
                                     suffixes=("_new","_ref"), indicator=True, validate="one_to_one")
        assert check._merge.eq("both").all()
        for quantity in ["A1", "error"]:
            assert np.allclose(check[quantity+"_new"], check[quantity+"_ref"], atol=1e-8, rtol=0), quantity
        assert check.n_rows_new.eq(check.n_rows_ref).all()
        assert check.status_new.eq("ok").all() and check.status_ref.eq("ok").all()
        full_pdf_verified = True
        print("PDF objetivo verificado: todos los A1, errores y poblaciones coinciden.")
    else:
        print("Sólo subconjunto de archivos: no afirmar reproducción del PDF completo.")

# %%
# Mismo trazado de la sección 5; valores calculados arriba desde el parquet nuevo.
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
for axis, column, title in zip(
    axes, ["sd_nMuons_MC", "sd_nEM_MC"], ["SD muonic count", "SD electromagnetic count"]
):
    for sample, color, marker in [
        ("Antes de HasStation", "royalblue", "s"),
        ("HasStation=True", "firebrick", "o"),
    ]:
        rows = selection_fits.loc[
            selection_fits["column"].eq(column) & selection_fits["sample"].eq(sample)
        ]
        axis.errorbar(rows["r_center"], rows["A1"], yerr=rows["error"],
                      color=color, marker=marker, capsize=3, label=sample)
    axis.axhline(0, color="black", ls="--", lw=1)
    axis.set_xlabel(r"$r_{\mathrm{MC}}$ [m]", fontsize=14)
    axis.set_ylabel(r"$A_1$", fontsize=14)
    axis.set_title(title)
    axis.grid(alpha=0.3)
    axis.legend(fontsize=10)
fig.suptitle("Same radial bins and weighted fit; one row per SD station/event\n"
             "Proton SIBYLL 2.3e, 30–40°, true MC geometry", fontsize=13)
fig.tight_layout()
result_dir = Path(output_dir)/"resultados"
fig.savefig(result_dir/"SD_antes_despues_mismos_bins.pdf")
fig.savefig(result_dir/"SD_antes_despues_mismos_bins.png", dpi=160)
selection_fits.to_csv(result_dir/"seleccion_mismos_bins_ajuste_ponderado.csv", index=False)
plt.show()
print("Reproducción completa verificada:", full_pdf_verified)
# Para otros modelos/primarios, adaptar también el título; no cambia el estimador.

# %% [markdown]
# ## Qué se conserva y qué se corrige
#
# - No se tocó Offline, configuraciones del instituto ni Scripts/Procesamiento_ADST_v8-2.
# - Las columnas UMD antiguas se conservan y se cotejan; los indicadores añadidos
#   explicitan dónde la suma histórica no equivale a verdad disponible.
# - La señal SD REC sólo está definida donde existe ese objeto; no se inventa VEM.
# - La figura usa conteos SD MC, nunca exige UMD y nunca se rellena MC ausente con cero.
# - No se afirma equivalencia sólo porque haya terminado Pool. Las comprobaciones
#   anteriores deben pasar. No comparar conjuntos con distintos archivos/eventos.
# - Si hay errores nativos ROOT o diferencias contra referencia, detenerse y leer
#   el log de ESE archivo. No silenciar warnings, cambiar cortes o forzar la curva.

