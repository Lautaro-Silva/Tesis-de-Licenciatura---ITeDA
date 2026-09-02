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

# %%
# --- Celda 1.1: Importaciones y Carga de Librerías Offline ---
import os
import numpy as np
import pandas as pd
import glob
import ROOT
import time
import traceback
from multiprocessing import Pool, cpu_count
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

print("Librerías cargadas correctamente. ¡Listo para trabajar! 🚀")


# %%
# =========================================================================
# CELDA: FUNCIONES AUXILIARES Y LECTURA ADST (Versión v17 - High Performance & Documentada)
# =========================================================================

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

def readADST_surface_v17(fname, is_mc_simulation=True):
    """
    Leer un archivo ADST (1 fila por MÓDULO).
    
    Esta función es el corazón del pipeline de procesamiento. Itera sobre
    cada evento (lluvia) en un archivo ADST y extrae la información
    relevante a nivel de MÓDULO de UMD (el nivel más granular).
    
    Lógica Clave:
    1. Itera sobre el MDEvent para encontrar TODOS los counters UMD.
    2. Usa el SDEvent como "diccionario" de geometría.
    3. NO filtra por 'IsLowGainSaturated', guarda un flag.
    4. Versión HÍBRIDA/ESTRICTA: Calcula posiciones 2D, rotaciones Euler (con +180 histórico)
       y la matemática estricta de Darko (C++ nativo sin +180).
    5. Guarda la señal REC y MC para el UMD y SD por separado.
    
    [ACTUALIZACIÓN v17]: Optimización estricta de PyROOT. Se eliminaron las llamadas a 
    'hasattr()' que generaban bloqueos de Mutex globales y destruían el Multiprocessing.
    """
    
    print(f"Iniciando lectura de: {os.path.basename(fname)}")
    
    if not os.path.exists(fname):
        print(f"Advertencia: Archivo no encontrado {fname}")
        return pd.DataFrame() # Retorna DF vacío 

    # --- Inicialización de ROOT ---
    files = ROOT.std.vector('string')()
    files.push_back(fname)

    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    geo = ROOT.DetectorGeometry()
    
    file1.ReadDetectorGeometry(geo) # Ignoramos fallos (Warnings de TStreamerInfo)
    file1.SetBuffers(event)

    data = []
    event_count = 0
    start_time = time.time()

    # --- COMIENZA EL BUCLE DE EVENTOS ---
    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        event_count += 1
        if event_count % 500 == 0:
            print(f"... procesados {event_count} eventos.")
        
        # --- Info Global del Evento (Lluvia) ---
        event_id_lluvia = event.GetEventId()
        
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
    
        # --- Bucle sobre los COUNTERS ---
        mEvent = event.GetMDEvent()
        counterIterator = mEvent.CountersBegin()
        countersEnd = mEvent.CountersEnd()
        
        while counterIterator != countersEnd:
            
            counter = counterIterator.__deref__() # Objeto Counter (estación)
            counterId = counter.GetId()            
            sdId = counter.GetSdPartnerId()    

            # Buscamos la estación de superficie (SD) asociada
            sdStation = sEvent.GetStationById(sdId) if sEvent.HasStation(sdId) else None
            
            # --- Corte de Calidad 1: Geometría ---
            if sdStation is None:
                counterIterator += 1 # Avanzamos al siguiente counter
                continue 

            # --- Corte de Calidad 2: Saturación (Corte Diferido) ---
            is_sd_saturated = sdStation.IsLowGainSaturated()
            
            # Datos básicos de la reconstruccion
            sdSignal = sdStation.GetTotalSignal()
            sdSignal_err = sdStation.GetTotalSignalError()
            sdMuonSignal = sdStation.GetMuonSignal() # Suele ser 0 en Reco estándar

            # --- CÁLCULO DE COMPONENTES MC (CONTEO DE PARTICULAS) ---
            mc_sd_n_muon = np.nan
            mc_sd_n_em = np.nan # Suma de electrones + fotones
            
            # [OPTIMIZACIÓN v17]: Reemplazamos los múltiples hasattr() por un try/except.
            # PyROOT bloquea el Mutex global al buscar métodos inexistentes con hasattr(), 
            # hundiendo la performance del multiprocessing.
            if hasattr(sEvent, "HasSimStation") and sEvent.HasSimStation(sdId):
                simStation = sEvent.GetSimStationById(sdId)
                try:
                    # Usamos los métodos que el Hunter encontró como NO NULOS
                    mc_sd_n_muon = float(simStation.GetNumberOfMuons())
                    n_e = float(simStation.GetNumberOfElectrons())
                    n_gamma = float(simStation.GetNumberOfPhotons())
                    mc_sd_n_em = n_e + n_gamma
                except AttributeError:
                    # Si la estación simulada no tiene estos métodos, quedan en NaN
                    pass

            r_core_err = sdStation.GetSPDistanceError() 

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
            val_sp = sdStation.GetAzimuthSP()
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
                
                phi_rel = sdStation.GetAzimuthSP()
                r_final = sdStation.GetSPDistance()
                x_plane = r_final * np.cos(phi_rel)
                y_plane = r_final * np.sin(phi_rel)
                
                # Valores ficticios para que no quede en NaN
                r_core_MC = r_final
                r_umd_rec = r_final
                r_umd_mc = r_final
                
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
                    except:
                        counterIterator += 1
                        # print(f'Basura: ID {sdId} no encontrado en Geometría')
                        continue
                        
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
            if simCounter is None:
                counterIterator += 1
                continue
                
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
                nMuones_MC_module = 0.0
                channelIterator = module.ChannelsBegin()
                channelsEnd = module.ChannelsEnd()
                 
                # Le preguntamos al 'simCounter' por el 'simScintillator'
                # que corresponde a este 'moduleId' y 'channelId'
                while channelIterator != channelsEnd:
                    channel = channelIterator.__deref__()
                    channelId = channel.GetId()
                    
                    if simCounter.HasSimScintillatorByChannel(moduleId, channelId):
                        mdSimScintillator = simCounter.GetSimScintillatorByChannelId(moduleId, channelId)
                        nMuones_MC_module += mdSimScintillator.GetNumberOfInjectedMuons()
                        
                    channelIterator += 1
                # --- ❗️ FIN DEL CÁLCULO MC ❗️ ---

                data.append({
                    "event_id": event_id_lluvia,
                    
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
                
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"Lectura completa. Total de eventos leídos: {event_count}")
    print(f"Tiempo total de lectura: {elapsed:.2f} segundos.")
    print(f"Total de 'MÓDULOS' (filas) extraídos: {len(data)}")

    df = pd.DataFrame(data)
    return df


# %%
# -----------------------------------------------------------------
# FUNCIÓN "TRABAJADORA"
# ❗️ 2. AHORA ACEPTA 'output_dir' COMO ARGUMENTO
# -----------------------------------------------------------------
def process_file_wrapper(root_fpath, output_dir):
    # 1. Definir rutas
    filename = os.path.basename(root_fpath)
    output_filename = filename.replace(".root", ".parquet")
    output_path = os.path.join(output_dir, output_filename)
    
    # 2. Evitar reprocesar
    if os.path.exists(output_path):
        return f"INFO: El archivo ya existe, saltando: {output_filename}"

    # 3. Imprimir estado
    print(f"► [Iniciando]: {filename}")
    
    try:
        # ----- INICIO DEL TRABAJO -----
        start_file_time = time.time()

        # IMPORTANTE CAMBIAR EL NOMBRE EN FUNCION DE LA VERSION DE LA FUNCION
        df = readADST_surface_v17(root_fpath) 
        
        if df.empty:
            return f"INFO: Archivo vacío o sin datos UMD. Saltando: {filename}"

        # 2. Extraer metadatos del nombre de archivo
        try:
            parts = filename.split('_')
            df["model_mc"] = parts[0]
            df["e_min_mc"] = float(parts[1]) / 10.0
            df["e_max_mc"] = float(parts[2]) / 10.0
            df["primary_name_mc"] = parts[3]
            run_part = parts[-1].replace('.root', '')
            df["run_number"] = int(run_part.replace('Run', ''))
        except Exception as e_parse:
            print(f"  Advertencia: No se pudo parsear metadata en {filename}: {e_parse}")

        # 3. Guardar en Parquet
        df.to_parquet(
            output_path,
            compression="snappy",
            index=False
        )
        
        # 4. Liberar memoria
        del df
        
        end_file_time = time.time()
        elapsed = end_file_time - start_file_time
        return f"✔ [Éxito]: {filename} -> {output_filename} ({elapsed:.2f}s)"

        # ----- FIN DEL TRABAJO -----

    except Exception as e:
        # Si algo falla, retornamos el string de error
        return f"❌ [ERROR] en {filename}: {e}\n{traceback.format_exc()}"


# %% [markdown]
# # Paralelizacion -> QGS-Helio-17.5-18eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario



print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/QGSIII01/17.5_18.0/helium"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_qgs_helio_17/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")
    
    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")

    # CREAMOS LA FUNCIÓN "PARCIAL" 
    # "Congelamos" el argumento 'output_dir' de nuestra función wrapper
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # pool.map() distribuye la lista 'all_root_files'
        # entre los 4 trabajadores y aplica la función 'process_file_wrapper'
        # results' será una lista con los strings de "Éxito" o "ERROR"
        results = pool.map(process_func, all_root_files)
    
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %% [markdown]
# # Paralelizacion -> Sibyl-Helio-17.5-18eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario



print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/helium"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_helio_17/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")

    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")
    
    # CREAMOS LA FUNCIÓN "PARCIAL" 
    # "Congelamos" el argumento 'output_dir' de nuestra función wrapper
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # pool.map() distribuye la lista 'all_root_files'
        # entre los 4 trabajadores y aplica la función 'process_file_wrapper'
        # results' será una lista con los strings de "Éxito" o "ERROR"
        results = pool.map(process_func, all_root_files)
        
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %% [markdown]
# # Paralelizacion -> Sibyl-Hierro-17.5-18eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario

print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/iron"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_hierro_17/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")

    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")

    # CREAMOS LA FUNCIÓN "PARCIAL" 
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # ❗️ 3. CAMBIO CRÍTICO: imap_unordered + chunksize=1 ❗️
        # 'imap_unordered' devuelve los resultados a medida que se completan.
        # 'chunksize=1' fuerza a los workers a pedir los archivos de a uno,
        # balanceando la carga perfectamente para que ninguno quede ocioso.
        results = list(pool.imap_unordered(process_func, all_root_files, chunksize=1))
    
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %% [markdown] jp-MarkdownHeadingCollapsed=true
# # Paralelizacion -> Sibyl-Oxigeno-17.5-18eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario



print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/oxygen"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v10/parquet_sib_oxigeno_17/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")

    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")

    # CREAMOS LA FUNCIÓN "PARCIAL" 
    # "Congelamos" el argumento 'output_dir' de nuestra función wrapper
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # pool.map() distribuye la lista 'all_root_files'
        # entre los 4 trabajadores y aplica la función 'process_file_wrapper'
        # results' será una lista con los strings de "Éxito" o "ERROR"
        results = pool.map(process_func, all_root_files)
    
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %% [markdown]
# # Paralelizacion -> Sibyl-Proton-17.5-18eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario



print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")

    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")

    # CREAMOS LA FUNCIÓN "PARCIAL" 
    # "Congelamos" el argumento 'output_dir' de nuestra función wrapper
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # pool.map() distribuye la lista 'all_root_files'
        # entre los 4 trabajadores y aplica la función 'process_file_wrapper'
        # results' será una lista con los strings de "Éxito" o "ERROR"
        results = pool.map(process_func, all_root_files)
    
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %% [markdown] jp-MarkdownHeadingCollapsed=true
# # Paralelizacion -> EPOS-Helio-18-18.5eV

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario



print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/EPOSLHC_R/18.0_18.5/helium"
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v10/parquet_epos_helio_18/"

os.makedirs(output_dir, exist_ok=True)
print(f"Buscando archivos en: {base_path}")
print(f"Los archivos .parquet se guardarán en: {output_dir}")

# --- 2. Encontrar todos los archivos ---
all_root_files = glob.glob(os.path.join(base_path, "*.root"))
all_root_files.sort()

if not all_root_files:
    print(f"¡Error! No se encontraron archivos .root en: {base_path}")
else:
    print(f"Encontrados {len(all_root_files)} archivos .root para procesar.")

    # --- 3. Bucle de Procesamiento Paralelo ---
    print(f"Iniciando Pool con {n_workers} trabajadores...")

    # CREAMOS LA FUNCIÓN "PARCIAL" 
    # "Congelamos" el argumento 'output_dir' de nuestra función wrapper
    process_func = partial(process_file_wrapper, output_dir=output_dir)

    with Pool(processes=n_workers) as pool:
        
        # pool.map() distribuye la lista 'all_root_files'
        # entre los 4 trabajadores y aplica la función 'process_file_wrapper'
        # results' será una lista con los strings de "Éxito" o "ERROR"
        results = pool.map(process_func, all_root_files)
    
    print("\n\n--- Proceso Paralelo Completado ---")

    # --- 4. Resumen Final ---
    exitos = 0
    errores = 0
    
    # Imprimimos todos los mensajes de resultado
    for res in results:
        print(res)
        if "✔ [Éxito]" in res:
            exitos += 1
        elif "❌ [ERROR]" in res:
            errores += 1

    end_total_time = time.time()
    print("\n--- Resumen de la Tanda ---")
    print(f"Tiempo total: {(end_total_time - start_total_time) / 60:.2f} minutos")
    print(f"Total de archivos: {len(all_root_files)}")
    print(f"Éxitos: {exitos}")
    print(f"Errores: {errores}")
    print(f"¡Listo! Tus archivos .parquet están en: {output_dir}")

# %%
