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
# # Procesamiento ADST v8-2: el mismo lector, con HasStation guardado como flag
#
# **Este cuaderno es para que lo ejecutes vos, celda por celda, en tu entorno Offline.**
# No se ejecutó sobre ROOT reales al prepararlo. No tiene condiciones para agentes,
# RUN_PROCESSING, manifiestos ni un lector alternativo oculto.
#
# Se conserva el código de v8-2: sus importaciones, sus tres funciones y sus
# bucles de eventos → counters → módulos → canales. Las modificaciones del lector
# están señaladas con **CAMBIO** en los comentarios. No hay funciones auxiliares nuevas.
#
# Sale UN parquet por archivo, con las columnas originales y sólo una columna
# adicional: `has_sd_rec`. Después comparás el dataframe completo con
# `df.loc[df["has_sd_rec"]]`. No son dos procesamientos distintos.
#
# Si HasStation es True se conservan los cálculos originales. Si es False se
# omiten únicamente los getters del objeto sdStation que no existe. El shower
# reconstruido es otro objeto: no se borra por la ausencia de esta estación.
#
# **Alcance:** se mantienen los demás requisitos de v8-2 (counter UMD, módulos,
# simCounter y geometría recuperable). Quitar este skip no recupera counters que
# nunca se guardaron en el ADST. Tampoco certifica verdad MC UMD completa: la suma
# histórica de canales se conserva, incluidos sus ceros cuando falta información.
#
# La celda de procesamiento se ejecuta normalmente cuando vos la ejecutás:
# **no usar Run All sin revisar antes rutas, archivos y costo.**
# Sólo hay una tanda de ejemplo para no lanzar varias producciones por accidente.
# Cambiá las rutas para las otras tandas, como hacías antes.

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

# %% [markdown]
# ## Qué cambió en esta versión y dónde se leen los muones sin HasStation
#
# **Sí se extraen los conteos MC cuando `has_sd_rec=False`, si existen los objetos
# simulados correspondientes.** Lo que queda en NaN es la señal RECONSTRUIDA de
# una estación que no tiene objeto SD REC, no automáticamente su conteo MC.
# El lector no vuelve a simular partículas ni calcula una nueva respuesta del
# tanque: lee los resultados MC ya guardados en el ADST.
#
# ### Dos preguntas distintas al SDEvent
#
# - `HasStation(sdId)`: ¿está guardada la estación SD reconstruida? Permite usar
#   `GetStationById(sdId)` para leer señal REC, error, saturación y azimut SP.
# - `HasSimStation(sdId)`: ¿está guardada la estación SD simulada? Permite usar
#   `GetSimStationById(sdId)` para leer los conteos de partículas MC.
#
# La segunda pregunta se hace **fuera del bloque `if has_sd_rec ... else ...`**,
# a la misma indentación que ese bloque. Por eso se ejecuta en ambos casos.
# Recorrido de una estación con `has_sd_rec=False`:
#
# 1. El `else` deja `sdSignal`, su error y `sdMuonSignal` en NaN. No hace `continue`.
# 2. A continuación se consulta `HasSimStation`. Si existe, `GetNumberOfMuons()`
#    llena `mc_sd_n_muon`, y electrones + fotones llenan `mc_sd_n_em`.
# 3. Se calculan las coordenadas Infill con geometría y shower, como antes.
# 4. Si se cumplen los requisitos UMD que ya existían, se recorren sus módulos y
#    canales. `GetNumberOfInjectedMuons()` alimenta la suma `nMuones_MC_module`.
# 5. `data.append` guarda esos valores como `sd_nMuons_MC`, `sd_nEM_MC` y
#    `nMuones_MC`, junto con `has_sd_rec=False`. Así llegan al parquet.
#
# | Columna del parquet | Fuente | Si HasStation es False |
# |---|---|---|
# | `sd_nMuons_MC` | `simStation.GetNumberOfMuons()` | Se lee si existe SD simulado y el getter está disponible |
# | `sd_nEM_MC` | Electrones + fotones de `simStation` | Se lee bajo la misma condición; es conteo, no señal en VEM |
# | `nMuones_MC` | Suma de `GetNumberOfInjectedMuons()` en canales UMD | Se conserva la suma original cuando hay counter/módulos; resúmenes ausentes pueden dejarla incompleta |
# | `nMuones_REC` | `module.GetNumberOfEstimatedMuons()` | Se lee del módulo UMD existente; no es el getter de señal del tanque |
# | `sdSignal_REC`, `sdMuonSignal_REC` | Señales de `sdStation` reconstruida | NaN: este lector no recupera una señal REC inexistente |
#
# ### Cambios respecto de v8-2
#
# - Se reemplaza el skip por ausencia de SD REC por la columna `has_sd_rec`.
# - Se protegen los getters propios de `sdStation` para no llamarlos sobre None.
#   Con HasStation=True, sus cálculos se conservan.
# - En anillo sin SD REC, las coordenadas que dependían de ese objeto quedan en
#   NaN. Las rotaciones y convenciones Infill no se modifican.
# - Se reconoce también el puntero C++ nulo de simCounter mediante `bool`, además
#   del chequeo original contra None. No se inventa un counter cuando falta.
# - Se cambia el nombre de la función y su llamada desde el wrapper. No se añaden
#   funciones auxiliares; getters MC y suma de muones UMD siguen siendo los originales.
# - La tanda de ejemplo usa una salida nueva y empieza con un archivo/un trabajador;
#   esto no introduce cortes físicos dentro del lector.
#
# ### Qué puede cambiar en la asimetría, y qué no está demostrado aún
#
# El cambio posible no viene de asignar ceros ni de modificar los conteos: antes
# se promediaba el conteo MC sólo para filas que cumplían HasStation; ahora puede
# promediarse también el de las filas antes descartadas. Si los conteos de las
# estaciones descartadas difieren de los retenidos de forma dependiente del azimut,
# cambia la curva de medias y puede cambiar el signo de A1.
# **A1 positivo = exceso temprano; negativo = exceso tardío.**
#
# No se garantiza que esta copia mínima elimine la inversión antes de correrla y
# ajustar los datos. El estudio anterior partía del vector de estaciones SD simuladas;
# este lector conserva el universo de counters/módulos UMD de v8-2. Puede seguir
# faltando población por esos otros requisitos, aunque retiremos HasStation.
# Si no existe SD simulado, sus conteos quedan ausentes, no cero. La suma histórica
# UMD tampoco certifica verdad completa si faltan resúmenes de canales.
#
# La comparación pertinente para la inversión de **SD-Muon(MC)** usa
# `sd_nMuons_MC`, no `sdSignal_REC`. No hay aquí una nueva señal total SD en VEM
# para las estaciones sin reconstrucción. Tampoco se deben eliminar esas filas
# mediante un `dropna()` global: volvería a imponer indirectamente el corte.
#
# **Estado:** no se procesó ROOT real con esta versión. La explicación distingue
# lo que hace el código de un resultado de asimetría todavía por verificar.

# %%
def readADST_surface_v17_flag(fname, is_mc_simulation=True):
    """
    Leer un archivo ADST (1 fila por MÓDULO).
    
    Esta función es el corazón del pipeline de procesamiento. Itera sobre
    cada evento (lluvia) en un archivo ADST y extrae la información
    relevante a nivel de MÓDULO de UMD (el nivel más granular).
    
    Lógica Clave:
    1. Itera sobre el MDEvent para encontrar TODOS los counters UMD.
    2. Usa el SDEvent como "diccionario" de geometría.
    3. NO filtra por 'IsLowGainSaturated' ni por HasStation: guarda ambos flags.
       HasStation sólo decide si podemos acceder al objeto sdStation.
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
        
        # Reconstrucción DEL SHOWER (no de una estación particular).
        # CAMBIO: aclaración, no cambio de cálculo. Que una estación no esté en
        # SDEvent no elimina este objeto global. Conservamos tu lectura original.
        # Su existencia tampoco garantiza calidad del ajuste: no añadimos cortes.
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

            # CAMBIO 1: guardamos el requisito como dato, en lugar de hacer skip.
            # HasStation pregunta por la estación SD RECONSTRUIDA, no por el shower
            # ni por su estación SIMULADA. Esos objetos se consultan por separado.
            has_sd_rec = bool(sEvent.HasStation(sdId))
            sdStation = sEvent.GetStationById(sdId) if has_sd_rec else None

            if has_sd_rec:
                # CON estación REC: exactamente tus getters y valores anteriores.
                is_sd_saturated = sdStation.IsLowGainSaturated()
                sdSignal = sdStation.GetTotalSignal()
                sdSignal_err = sdStation.GetTotalSignalError()
                sdMuonSignal = sdStation.GetMuonSignal()
            else:
                # SIN estación REC: no podemos llamar métodos sobre None.
                # Ausencia de señal reconstruida NO significa señal física cero.
                is_sd_saturated = None  # Flag desconocido, no "no saturada".
                sdSignal = np.nan
                sdSignal_err = np.nan
                sdMuonSignal = np.nan
                # No hay continue aquí: seguimos con MC, geometría y módulos UMD.

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

            # CAMBIO 2: éste también es un getter de la estación, no del shower.
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
            # CAMBIO 3: sin estación REC no hay azimut SP nativo guardado.
            # NaN se propaga en este cálculo; las rotaciones MC de abajo siguen.
            # No cambiamos la convención histórica cuando HasStation es True.
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
                
                # CAMBIO 4: este caso, a diferencia de Infill, usa sdStation
                # para SUS COORDENADAS. Con REC dejamos tu bloque igual.
                if has_sd_rec:
                    phi_rel = sdStation.GetAzimuthSP()
                    r_final = sdStation.GetSPDistance()
                    x_plane = r_final * np.cos(phi_rel)
                    y_plane = r_final * np.sin(phi_rel)

                    # Valores históricos: se conservan, no se reinterpretan como
                    # nuevas coordenadas MC independientes de reconstrucción.
                    r_core_MC = r_final
                    r_umd_rec = r_final
                    r_umd_mc = r_final
                else:
                    # Sin el objeto no conocemos aquí la posición del anillo.
                    # Conservamos la fila y sus conteos, no inventamos un radio.
                    r_final = np.nan
                    x_plane = np.nan
                    y_plane = np.nan
                    # r_core_MC, r_umd_rec y r_umd_mc ya se inicializaron en NaN.
                
            else:
                # --- CASO B: INFILL (4k o 104k) / ESTÁNDAR ---
                # --- EXTRACCIÓN DE POSICIONES FÍSICAS ---
                
                # INFILL: todo este bloque de geometría queda como en v8-2.
                # geo, pos_core y pos_core_MC no son sdStation. Por eso podemos
                # calcular las coordenadas aun si esta estación no tiene SD REC.
                # Si falta la posición en geo, se conserva tu skip original.

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
            # CAMBIO 5: el requisito simCounter ya existía. PyROOT puede devolver
            # un puntero C++ nulo que NO es None; bool lo detecta antes de acceder.
            # No reconstruimos ni inventamos un counter simulado cuando falta.
            if simCounter is None or not simCounter:
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
                # SIN CAMBIO: se conserva tu suma para poder cotejar el parquet.
                # Si faltan resúmenes de canales, este cero inicial NO prueba
                # ausencia física de muones. No se redefine el observable aquí.
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
                    # CAMBIO 6: única columna nueva. True recupera el corte viejo;
                    # usar TODAS las filas retira sólo ese requisito explícito.
                    "has_sd_rec": has_sd_rec,

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
        df = readADST_surface_v17_flag(root_fpath) 
        
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
# ## Configurar una tanda — igual que antes, salida NUEVA
#
# Revisá la ruta de entrada y elegí otra carpeta de salida para cada tanda.
# No uses los parquet antiguos como salida: el wrapper original salta archivos
# existentes, por lo que mezclar lecturas viejas/nuevas invalidaría la comparación.
#
# Se conserva también tu parser de metadatos. Su limitación histórica con modelos
# cuyo nombre contiene '_' no se corrige en esta prueba: revisar sus advertencias.
# No se añaden cortes por theta, radio, energía, señal o número de muones.

# %%
# Entrada de ejemplo: misma producción que usás para la comparación SD/UMD.
base_path = "/srv/data/Malargue/icrc2025/test7/IdealMC_CORSIKA/MdSdInfill_CORSIKA78010_FLUKA/SIB23e/17.5_18.0/proton"

# Salida distinta de tus parquet originales, dentro de la carpeta de esta entrega.
# Cambiá el nombre final para otra tanda/prueba. No se sobrescribe la original.
output_dir = "/home/lsilva/Github/ADST_Alexey_module_v12_flag/parquet_sib_proton_17/"

# La búsqueda lista nombres; aún no lee eventos ni ejecuta el lector.
all_root_files = sorted(glob.glob(os.path.join(base_path, "*.root")))
print(f"Archivos encontrados: {len(all_root_files)}")

# Prueba inicial: UN ARCHIVO COMPLETO, sin cambiar el bucle de eventos de v17.
#root_files_a_procesar = all_root_files[:1]
# Para TODA la tanda, reemplazá la línea anterior por:
root_files_a_procesar = all_root_files

# Un trabajador inicialmente: no se dispara el Pool de ocho de tu ejemplo viejo.
# Elegí más sólo después de medir costo y coordinar el uso del servidor compartido.
n_workers = 8

# %% [markdown]
# ## Procesar — ejecutar esta celda inicia la lectura ROOT
#
# No hay una condición que decida quién puede ejecutar: ésta es tu celda normal.
# No se ejecutó durante la preparación del cuaderno. Medí primero un archivo.
# Se conserva el wrapper original (incluido su reporte de errores por archivo).
# Una lista de resultados con errores NO es una tanda completa.
# La carpeta nueva se exige una sola vez para evitar mezclar tandas por accidente.

# %%
if not root_files_a_procesar:
    raise FileNotFoundError("No hay archivos para procesar: revisar base_path.")

# Esta protección sólo evita mezclar/sobrescribir resultados; no corta eventos.
# Para volver a correr una prueba, elegí otra output_dir en la celda anterior.
os.makedirs(output_dir, exist_ok=False)

start_total_time = time.time()
process_func = partial(process_file_wrapper, output_dir=output_dir)

# El modo inicial es serial y legible. El modo paralelo es el mismo Pool de v8-2.
if n_workers == 1:
    results = []
    for root_fpath in root_files_a_procesar:
        results.append(process_func(root_fpath))
else:
    with Pool(processes=n_workers) as pool:
        results = pool.map(process_func, root_files_a_procesar)

for res in results:
    print(res)
print(f"Tiempo total: {(time.time() - start_total_time) / 60:.2f} minutos")

# %% [markdown]
# ## Leer el MISMO parquet y comparar con/sin el flag
#
# Esta celda no extrae datos otra vez. Lee sólo la tanda recién creada.
# Para grandes producciones, cargar todos los parquet a la vez puede requerir
# mucha memoria: empezá por la prueba de un archivo.
#
# Para reproducir tu análisis anterior no cambiamos aquí la ponderación por módulo.
# Si decidís deduplicar SD por estación/evento, hacelo en AMBAS muestras y no
# confundas ese cambio de ponderación con el efecto de HasStation.
# El esquema de abajo es idéntico para los dos subconjuntos: cambiás sólo el flag.

# %%
parquet_files = sorted(glob.glob(os.path.join(output_dir, "*.parquet")))
if not parquet_files:
    raise FileNotFoundError("No se escribieron parquet: revisar los mensajes del procesamiento.")

# source_file identifica el archivo al juntar eventos; NO añade una columna al
# parquet guardado. No cambia ningún conteo ni requiere una función auxiliar.
df = pd.concat(
    [pd.read_parquet(f).assign(source_file=os.path.basename(f)) for f in parquet_files],
    ignore_index=True
)

df_sin_corte = df.copy()                          # True Y False: todas las filas.
df_con_corte = df.loc[df["has_sd_rec"]].copy()    # Sólo True: requisito anterior.
df_solo_agregadas = df.loc[~df["has_sd_rec"]].copy()  # Diagnóstico: NO es "sin corte".

print("Filas con el requisito anterior:", len(df_con_corte))
print("Filas sin ese requisito:", len(df_sin_corte))
print("Filas añadidas:", len(df_solo_agregadas))

# Ejemplo de MISMA selección física en ambas; después aplicás tu ajuste de A1:
df_infill = df.loc[
    (df["counterId"] >= 100000) &
    (df["theta_MC"] >= 30) & (df["theta_MC"] < 40)
].copy()
df_infill_con_corte = df_infill.loc[df_infill["has_sd_rec"]].copy()
df_infill_sin_corte = df_infill.copy()

# IMPORTANTE: NO usar df.dropna() global. Las filas sin SD REC tienen NaN
# precisamente en esas columnas; borrarlas reintroduciría el corte sin avisarte.
# sdSignal_REC sólo existe para True. Para esa señal no hay comparación "sin
# corte" recuperable con este lector; para SD-MC sí, cuando existe simStation.
# UMD mantiene tu definición histórica nMuones_MC, sin garantizar completitud.
# Usá r_core_MC y phi_plane_euler_MC_true_core en el análisis Infill MC.
# Se conserva el +pi histórico: deshacelo como en plots_seccion_6.
# A1 positivo = exceso temprano; negativo = exceso tardío.

# %% [markdown]
# ## Comprobar una referencia original, sin nuevas funciones
#
# Antes de interpretar A1, cotejá por archivo `df_con_corte` contra tu parquet
# viejo. Este bloque está comentado para que elijas explícitamente ambos archivos;
# no abre una referencia ni procesa automáticamente. No usa sólo la intersección:
# assert_frame_equal detecta filas faltantes/sobrantes, además de valores distintos.
#
# No se promete coincidencia real sin ese cotejo. Las pruebas de desarrollo fueron
# con objetos artificiales; no verifican bindings PyROOT ni el contenido del ADST.

# %%
# archivo_nuevo = os.path.join(output_dir, os.path.basename(root_files_a_procesar[0]).replace(".root", ".parquet"))
# archivo_viejo = os.path.join("/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17", os.path.basename(archivo_nuevo))
# nuevo = pd.read_parquet(archivo_nuevo)
# viejo = pd.read_parquet(archivo_viejo)
# nuevo = nuevo.loc[nuevo["has_sd_rec"]].copy()
#
# claves = ["event_id", "counterId", "moduleId", "sdId"]
# assert not nuevo.duplicated(claves).any()
# assert not viejo.duplicated(claves).any()
# # No agregamos ni quitamos columnas históricas: sólo excluimos el nuevo flag.
# assert set(nuevo.columns) - {"has_sd_rec"} == set(viejo.columns)
# # Normalizamos el tipo de event_id, no su valor.
# nuevo["event_id"] = nuevo["event_id"].astype(str)
# viejo["event_id"] = viejo["event_id"].astype(str)
# nuevo = nuevo.sort_values(claves).reset_index(drop=True)
# viejo = viejo.sort_values(claves).reset_index(drop=True)
# pd.testing.assert_frame_equal(
#     nuevo[viejo.columns], viejo, check_dtype=False, check_exact=True
# )
# print("Coinciden las filas y todos los valores originales del archivo.")
#
# Si falla, revisar la diferencia antes de atribuirla a física.
# Si con/sin flag tienen igual tamaño, los counters/módulos guardados podrían ya
# restringir la población. No añadir estaciones SD de otro universo para forzar
# que cambie: éste es deliberadamente tu pipeline original con el skip retirado.
