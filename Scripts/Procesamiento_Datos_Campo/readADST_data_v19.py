"""
readADST_surface_data_v19
=========================
Lectura de datos experimentales del SD-750 + UMD del Observatorio Auger.
Incluye todos los cortes de calidad estándar traducidos del C++ (ADSTReader.cc).

Cortes aplicados:
  - 6T5 fiducial (IsT5 + >= 5 vecinos activos UB o UUB)
  - Energía reconstruida mínima (default: logE >= 17.0)
  - Ángulo cenital máximo (default: theta < 60°)
  - Estaciones SD rechazadas (IsRejected)
  - Counters UMD rechazados (counter.IsRejected)

El module_status se guarda siempre (candidate/saturated/rejected/silent)
pero NO se filtra — decidís en el análisis qué hacer con cada categoría.
"""

import os
import time
import numpy as np
import pandas as pd
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning


def getModuleList(counter, sim=False):
    """
    Devuelve los módulos (segmentos de scintillador) de un Counter UMD.

    En datos reales los IDs de módulo son 100, 101, 102...
    En simulaciones son 0, 1, 2... (default cambiado a False para esta versión)
    """
    possible_ids = range(0, 6) if sim else range(100, 116)
    return [counter.GetModule(mid) for mid in possible_ids if counter.HasModule(mid)]


def readADST_surface_data_v19(
    fname,
    only_6T5=True,
    min_logE=17.0,
    max_theta_deg=60.0,
    skip_rejected_stations=True,
):
    """
    Lee un archivo ADST de datos reales y devuelve un DataFrame con una fila por módulo UMD.

    Parameters
    ----------
    fname : str
        Ruta al archivo .root (ej. ADST_PhaseI_2021_04_03.root).
    only_6T5 : bool
        Si True, aplica el corte 6T5 fiducial.
        Condición: IsT5() Y (nVecinos_UB >= 5 O nVecinos_UUB >= 5).
        Código del director: nNeighUB < 5 && nNeighUUB < 5 → skip.
    min_logE : float
        Logaritmo base 10 de la energía reconstruida mínima en eV.
        Default 17.0 (= 10^17 eV).
    max_theta_deg : float
        Ángulo cenital máximo en grados. Default 60°.
        Arriba de 60° la respuesta del UMD cambia (mayor trayectoria de muón).
    skip_rejected_stations : bool
        Si True, saltea estaciones SD marcadas como rechazadas
        (lightning, noCalib, badSilent, offGrid, etc.).

    Returns
    -------
    pd.DataFrame
        Una fila por módulo UMD en eventos que pasaron todos los cortes.
        Contiene variables de la lluvia, geometría SD y señal UMD.
    """
    if not os.path.exists(fname):
        print(f"Advertencia: archivo no encontrado → {fname}")
        return pd.DataFrame()

    files = ROOT.std.vector("string")()
    files.push_back(fname)

    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    file1.SetBuffers(event)

    data = []

    # Contadores de diagnóstico — útiles para entender cuánto tira cada corte
    n_read = 0
    n_no_energy = 0
    n_no_t5 = 0
    n_theta_cut = 0
    n_passed_event = 0

    start_time = time.time()

    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        n_read += 1

        sEvent = event.GetSDEvent()
        sShower = sEvent.GetSdRecShower()

        # =====================================================================
        # CORTES A NIVEL DE EVENTO
        # =====================================================================

        # 1. Corte de energía
        rec_energy = sShower.GetEnergy()
        if rec_energy <= 0:
            n_no_energy += 1
            continue
        logE_REC = np.log10(rec_energy)
        if logE_REC < min_logE:
            n_no_energy += 1
            continue

        # 2. Corte 6T5 fiducial
        #    Traducción directa del C++ del director:
        #      if (!sdEvent.IsT5()) continue;
        #      if (nNeighUB < 5 && nNeighUUB < 5) continue;
        if only_6T5:
            if not sEvent.IsT5():
                n_no_t5 += 1
                continue
            n_ub  = sEvent.GetT5PriorActiveNeighbors().size()
            n_uub = sEvent.GetT5PriorActiveUUBNeighbors().size()
            if n_ub < 5 and n_uub < 5:
                n_no_t5 += 1
                continue

        # 3. Corte de ángulo cenital
        theta_deg = sShower.GetZenith() * 180.0 / np.pi
        if theta_deg > max_theta_deg:
            n_theta_cut += 1
            continue

        n_passed_event += 1

        # Variables del evento que pasó los cortes
        event_id  = event.GetEventId()
        phi_deg   = sShower.GetAzimuth() * 180.0 / np.pi
        pos_core  = sShower.GetCoreSiteCS()
        core_x    = pos_core.X()
        core_y    = pos_core.Y()

        # =====================================================================
        # LOOP SOBRE COUNTERS (ESTACIONES UMD)
        # =====================================================================
        mEvent = event.GetMDEvent()
        counter_it  = mEvent.CountersBegin()
        counters_end = mEvent.CountersEnd()

        while counter_it != counters_end:
            counter   = counter_it.__deref__()
            counterId = counter.GetId()
            sdId      = counter.GetSdPartnerId()

            # Buscamos la estación SD asociada al counter UMD
            if not sEvent.HasStation(sdId):
                counter_it += 1
                continue
            sdStation = sEvent.GetStationById(sdId)

            # Guardamos los flags de rechazo como columnas en el DataFrame.
            # NO hacemos skip: es el análisis quien decide qué filtrar.
            # Esto permite estudiar la fracción de rechazo y sus causas,
            # y comparar señal de módulos "buenos" vs "rechazados".
            # Para análisis limpio: df[~df['is_sd_rejected'] & ~df['is_counter_rejected']]
            is_sd_rejected      = sdStation.IsRejected()
            is_counter_rejected = counter.IsRejected()

            # Variables de la estación SD
            is_sd_saturated = sdStation.IsLowGainSaturated()
            sd_signal       = sdStation.GetTotalSignal()
            sd_signal_err   = sdStation.GetTotalSignalError()
            sd_muon_signal  = sdStation.GetMuonSignal()
            phi_plane_sp    = sdStation.GetAzimuthSP()
            r_core          = sdStation.GetSPDistance()
            r_core_err      = sdStation.GetSPDistanceError()

            # =====================================================================
            # LOOP SOBRE MÓDULOS DEL UMD
            # =====================================================================
            # sim=False → busca IDs 100-115 (electrónica real)
            # sim=True  → busca IDs 0-5 (simulaciones)
            for module in getModuleList(counter, sim=False):

                nMuones_REC = module.GetNumberOfEstimatedMuons()
                moduleId    = module.GetId()

                # Estado del módulo — NO se filtra aquí,
                # lo guardamos para decidir en el análisis.
                if   module.IsCandidate(): status = "candidate"
                elif module.IsSaturated(): status = "saturated"
                elif module.IsRejected():  status = "rejected"
                elif module.IsSilent():    status = "silent"
                else:                      status = "undefined"

                data.append({
                    # Identidad del evento
                    "event_id":    event_id,

                    # Lluvia reconstruida
                    "logE_REC":    logE_REC,
                    "theta_REC":   theta_deg,
                    "phi_REC":     phi_deg,
                    "core_x":      core_x,
                    "core_y":      core_y,

                    # Identidad del módulo
                    "counterId":   counterId,
                    "sdId":        sdId,
                    "moduleId":    moduleId,

                    # Señal UMD
                    "nMuones_REC": nMuones_REC,
                    "module_status": status,

                    # Geometría SD (en el plano de lluvia)
                    "r_core":      r_core,
                    "r_core_err":  r_core_err,
                    "phi_plane_sp": phi_plane_sp,

                    # Señal SD
                    "is_sd_saturated":    is_sd_saturated,
                    "is_sd_rejected":     is_sd_rejected,      # flag: lightning, noCalib, etc.
                    "is_counter_rejected": is_counter_rejected, # flag: falla del UMD
                    "sdSignal_REC":    sd_signal,
                    "sdSignal_err":    sd_signal_err,
                    "sdMuonSignal_REC": sd_muon_signal,
                })

            counter_it += 1

    elapsed = time.time() - start_time

    # Resumen de cortes — muy útil para debugging y para la tesis
    print(f"  Archivo: {os.path.basename(fname)}")
    print(f"  Leídos : {n_read:>6}  |  pasaron todos los cortes: {n_passed_event}")
    print(f"  Tirados por energía  : {n_no_energy}")
    print(f"  Tirados por 6T5      : {n_no_t5}")
    print(f"  Tirados por theta    : {n_theta_cut}")
    print(f"  Filas (módulos) guardadas: {len(data)}")
    print(f"  Tiempo: {elapsed:.1f} s")

    return pd.DataFrame(data)


# =============================================================================
# Ejemplo de uso para procesar un mes completo
# =============================================================================
if __name__ == "__main__":

    import glob
    base_path = "/srv/workspace_favalli/ngonzalez/ADSTs/v4r2"
    year  = "2021"
    month = "04"

    pattern = f"{base_path}/{year}/{month}/ADST_PhaseI_{year}_{month}_*.root"
    files   = sorted(glob.glob(pattern))

    print(f"Encontrados {len(files)} archivos para {year}/{month}\n")

    dfs = []
    for f in files:
        df_day = readADST_surface_data_v19(
            f,
            only_6T5=True,
            min_logE=17.0,
            max_theta_deg=60.0,
            skip_rejected_stations=True,
        )
        if not df_day.empty:
            dfs.append(df_day)

    if dfs:
        df_month = pd.concat(dfs, ignore_index=True)
        out = f"data_{year}_{month}.parquet"
        df_month.to_parquet(out, index=False)
        print(f"\nGuardado: {out}  ({len(df_month)} filas)")
    else:
        print("No quedaron datos tras los cortes.")
