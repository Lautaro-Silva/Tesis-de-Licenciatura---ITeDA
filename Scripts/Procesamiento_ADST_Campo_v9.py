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

def readADST_surface_data_v18(fname):
    """
    [VERSIÓN DATOS EXPERIMENTALES - ULTRA LIGERA]
    Extrae exclusivamente la información reconstruida del SD y UMD.
    Se eliminaron los cálculos geométricos manuales; 
    se utiliza directamente sdStation.GetAzimuthSP() y sdStation.GetSPDistance().
    """
    if not os.path.exists(fname):
        return pd.DataFrame()

    files = ROOT.std.vector('string')()
    files.push_back(fname)

    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    
    # YA NO NECESITAMOS DetectorGeometry. Acelera drásticamente la lectura.
    file1.SetBuffers(event)

    data = []
    event_count = 0
    start_time = time.time()

    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        event_count += 1
        event_id_lluvia = event.GetEventId()

        # --- RECONSTRUCCIÓN GLOBAL DE LA LLUVIA ---
        sEvent = event.GetSDEvent()
        sShower = sEvent.GetSdRecShower()
        
        rec_energy = sShower.GetEnergy()
        logE_REC = np.log10(rec_energy) if rec_energy > 0 else np.nan
        
        theta_REC_deg = sShower.GetZenith() * 180.0 / np.pi
        phi_REC_deg = sShower.GetAzimuth() * 180.0 / np.pi
        
        # [RESTAURADO] Posición del núcleo reconstruido
        pos_core = sShower.GetCoreSiteCS()
        core_x = pos_core.X()
        core_y = pos_core.Y()

        # --- BUCLE SOBRE LOS COUNTERS (ESTACIONES UMD) ---
        mEvent = event.GetMDEvent()
        counterIterator = mEvent.CountersBegin()
        countersEnd = mEvent.CountersEnd()
        
        while counterIterator != countersEnd:
            counter = counterIterator.__deref__()
            counterId = counter.GetId()            
            sdId = counter.GetSdPartnerId()    

            # Buscamos su pareja SD
            sdStation = sEvent.GetStationById(sdId) if sEvent.HasStation(sdId) else None
            
            # --- Corte de Calidad Básico ---
            if sdStation is None:
                counterIterator += 1
                continue 

            is_sd_saturated = sdStation.IsLowGainSaturated()
            sdSignal = sdStation.GetTotalSignal()
            sdSignal_err = sdStation.GetTotalSignalError()
            sdMuonSignal = sdStation.GetMuonSignal()
            
            # --- GEOMETRÍA DIRECTA DE RECONSTRUCCIÓN ---
            # Extraemos la única verdad disponible en el SDEvent
            phi_plane_sp = sdStation.GetAzimuthSP()
            r_core = sdStation.GetSPDistance()
            r_core_err = sdStation.GetSPDistanceError() 

            # --- BUCLE SOBRE LOS MÓDULOS ---
            # sim=False obliga a buscar los IDs físicos reales de la electrónica (100, 101, etc.)
            modules = getModuleList(counter, sim=False) 
            
            for module in modules:
                nMuones_REC = module.GetNumberOfEstimatedMuons()
                moduleId = module.GetId()

                if module.IsCandidate(): status = "candidate"
                elif module.IsSaturated(): status = "saturated"
                elif module.IsRejected(): status = "rejected"
                elif module.IsSilent(): status = "silent"
                else: status = "undefined"

                # Guardamos solo lo real. 
                # (Nota: Agregué campos en np.nan al final por si tus scripts viejos de pandas 
                # exigen la existencia de columnas MC para no tirar error de KeyError)
                data.append({
                    "event_id": event_id_lluvia,
                    
                    # Info REC Lluvia
                    "logE_REC": logE_REC, 
                    "theta_REC": theta_REC_deg, 
                    "phi_REC": phi_REC_deg,
                    
                    # Info Identidad Estación/Módulo
                    "counterId": counterId,
                    "moduleId": moduleId,
                    "module_status": status,      
                    
                    # Señal UMD
                    "nMuones_REC": nMuones_REC,

                    # Geometría SD
                    "phi_plane_sp": phi_plane_sp,
                    "r_core": r_core,       
                    "r_core_err": r_core_err,  
                    "core_x": core_x,         # <-- RESTAURADO
                    "core_y": core_y,         # <-- RESTAURADO

                    # Señal SD acoplada
                    "sdId": sdId,
                    "is_sd_saturated": is_sd_saturated,
                    "sdSignal_REC": sdSignal,           
                    "sdSignal_err": sdSignal_err,
                    "sdMuonSignal_REC": sdMuonSignal,
                    
                    # --- Rellenos de Seguridad para Scripts Viejos ---
                    "logE_MC": np.nan, "theta_MC": np.nan, "phi_MC": np.nan, "nMuones_MC": np.nan,
                    "phi_plane_euler_MC": np.nan, "phi_plane_ground": np.nan
                })

            counterIterator += 1 
                
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
        df = readADST_surface_data_v18(root_fpath) 
        
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
# # Paralelizacion Datos de Campo - Prueba 1 - 04/21

# %%
# -----------------------------------------------------------------
# SCRIPT PRINCIPAL
# -----------------------------------------------------------------

n_workers = 8  # Ajustar como sea necesario

print(f"--- INICIANDO PROCESO PARALELO ({n_workers} Workers) ---")
start_total_time = time.time()

# --- 1. Configuración de Rutas ---
base_path = "/srv/data/Malargue/Raid/data/Prod/v4r2/XAuger/2021/04"
output_dir = "/home/lsilva/Github/ADST_campo_v1/04.21/"

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

# %%

# %%
import ROOT
import os

fname = "/srv/data/Malargue/Raid/data/Prod/v4r2/XAuger/2026/01/xad_2026_01_01_12h00.root"
output_txt = "diagnostico_adst.txt"

print(f"Iniciando escaneo... Guardando los resultados en '{output_txt}'")

with open(output_txt, "w") as f_out:
    f_out.write(f"--- RADIOGRAFÍA DEL ARCHIVO ADST ---\n")
    f_out.write(f"Archivo: {os.path.basename(fname)}\n\n")

    # Abrimos en modo estricto lectura
    f = ROOT.TFile.Open(fname, "READ")

    if not f or f.IsZombie():
        f_out.write("❌ Error fatal: El archivo está corrupto o ROOT no puede leerlo.\n")
        print("Error. Revisa el archivo txt.")
    else:
        f_out.write("✅ Archivo abierto exitosamente.\n\n")
        
        # Extraemos las "llaves" del archivo usando listas de Python
        keys = f.GetListOfKeys()
        
        f_out.write("--- 1. MACRO-OBJETOS EN EL ARCHIVO ---\n")
        for key in keys:
            nombre = key.GetName()
            clase = key.GetClassName()
            f_out.write(f" -> Nombre: '{nombre}' | Clase: '{clase}'\n")
        
        # Buscamos los posibles árboles estándar de ADST
        # Agregué "Events" que es clásico de CDAS
        nombres_comunes = ["ADST", "Events", "Tree", "EventTree"]
        
        for nombre_arbol in nombres_comunes:
            arbol = f.Get(nombre_arbol)
            if arbol and hasattr(arbol, "GetEntries"):
                f_out.write(f"\n🌟 ¡ENCONTRADO! El árbol de datos se llama: '{nombre_arbol}'\n")
                f_out.write(f" -> Eventos totales en el archivo: {arbol.GetEntries()}\n\n")
                
                # Imprimimos las primeras 50 ramas para ver si está el UMD/MD
                ramas = arbol.GetListOfBranches()
                f_out.write("--- 2. ESTRUCTURA DE RAMAS (Primeras 50) ---\n")
                for i in range(min(50, ramas.GetEntries())):
                    f_out.write(f"      - {ramas.At(i).GetName()}\n")
                break
        else:
            f_out.write("\n⚠️ No se encontró ningún árbol de eventos estándar.\n")

        f.Close()
        f_out.write("\nFin del escaneo.\n")

print(f"✅ ¡Listo! Abrí el archivo '{output_txt}' y pasame lo que dice.")

# %%
import ROOT

file_mdm = "/srv/data/Malargue/Raid/data/Prod/v4r2/Mdm/2021/04/mdm_2021_04_05_12h00.root"
file_ad = "/srv/data/Malargue/Raid/data/Prod/v4r2/Auger/2021/04/ad_2021_04_05_12h00.root"

for fname, name in zip([file_mdm, file_ad], ["MDM", "AD"]):
    f = ROOT.TFile.Open(fname, "READ")
    if not f or f.IsZombie():
        print(f"❌ {name}: No se pudo abrir.")
        continue
        
    keys = [k.GetName() for k in f.GetListOfKeys()]
    
    # Chequeamos si tiene el arbol de Offline
    if "eventInfo" in keys and "recData" in keys:
        print(f"✅ {name}: ¡FORMATO OFFLINE DETECTADO! ('eventInfo' y 'recData' presentes). Usa estos.")
    # Chequeamos si es CDAS
    elif any("Sd-only" in k or "Xd-only" in k for k in keys):
        print(f"❌ {name}: Formato CDAS detectado (AugerEvent). No compatible con librerías Offline.")
    else:
        print(f"⚠️ {name}: Formato desconocido. Llaves principales: {keys[:5]}")
    
    f.Close()

# %%
import ROOT
import os

# Usamos uno de los archivos xad_ que sabemos que pudiste abrir
fname = "/srv/data/Malargue/Raid/data/Prod/v4r2/XAuger/2021/04/xad_2021_04_05_12h00.root"

print(f"Probando lectura directa de objetos en: {os.path.basename(fname)}")

f = ROOT.TFile.Open(fname, "READ")

if not f or f.IsZombie():
    print("Error al abrir el archivo.")
else:
    keys = f.GetListOfKeys()
    
    eventos_totales = 0
    eventos_con_umd = 0
    
    print("Buscando datos del UMD en los primeros 100 eventos...")
    
    for i, key in enumerate(keys):
        if i >= 100: # Límite rápido para la prueba
            break
            
        if key.GetClassName() != "AugerEvent":
            continue
            
        eventos_totales += 1
        
        augerEvent = key.ReadObj()
        if not augerEvent:
            continue
            
        # Extraemos el corazón del Offline
        event = augerEvent.GetRecEvent()
        if not event:
            continue
            
        # Buscamos el detector de muones
        mEvent = event.GetMDEvent()
        if mEvent and mEvent.GetNumberOfCounters() > 0:
            eventos_con_umd += 1
            print(f"✅ ¡ÉXITO! Evento {event.GetEventId()} tiene {mEvent.GetNumberOfCounters()} estaciones UMD.")
            
            # Verificamos si hay módulos adentro (físicos o simulados)
            counter = mEvent.CountersBegin().__deref__()
            if counter.HasModule(100) or counter.HasModule(101) or counter.HasModule(0):
                print("   -> ¡Y tiene módulos con datos adentro!")
    
    f.Close()
    
    print(f"\n--- Resumen de la prueba ---")
    print(f"Eventos revisados: {eventos_totales}")
    print(f"Eventos con UMD: {eventos_con_umd}")
    
    if eventos_con_umd == 0:
        print("⚠️ Conclusión: Estos archivos CDAS están pelados. Necesitamos sí o sí los ADSTs del ITeDA.")

# %%
import ROOT

fname = "/srv/data/Malargue/Raid/data/Prod/v4r2/XAuger/2021/04/xad_2021_04_05_12h00.root"
print("Analizando la anatomía de AugerEvent de CDAS...")

f = ROOT.TFile.Open(fname, "READ")

if not f or f.IsZombie():
    print("Error al abrir el archivo.")
else:
    for key in f.GetListOfKeys():
        if key.GetClassName() == "AugerEvent":
            augerEvent = key.ReadObj()
            
            # Extraemos todos los métodos y atributos del objeto usando dir() nativo de Python
            todos_los_metodos = dir(augerEvent)
            
            # Filtramos los que parezcan ser del Muon Detector
            metodos_md = [m for m in todos_los_metodos if "Md" in m or "MD" in m or "Muon" in m or "Umd" in m or "UMD" in m]
            
            print("\n✅ ¡Objeto AugerEvent analizado!")
            print("Métodos disponibles para extraer datos del UMD:")
            for m in metodos_md:
                print(f" -> {m}()")
            
            # Busquemos también cómo sacar el SD para asegurarnos
            metodos_sd = [m for m in todos_los_metodos if "Sd" in m or "SD" in m]
            print(f"\nMétodos disponibles para el SD (primeros 5): {metodos_sd[:5]}")
            
            break
            
    f.Close()

# %%
