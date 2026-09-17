"""
lector_adst_v17_completo.py
===========================

ADST -> pandas reader for the MdSdInfill Monte Carlo productions.

This is YOUR reader `readADST_surface_v17` from `Scripts/Procesamiento_ADST_v8-2.py`,
carried over as literally as possible, with a small number of changes that are
each marked in the code with a comment of the form

    # CHANGE N: <what> -- <why>

so you can grep for "CHANGE" and see every deviation from v17 in one go.
Your original Spanish comments are kept verbatim where the code is unchanged.

---------------------------------------------------------------------------
WHY THIS FILE EXISTS (short version, the long version is in CAMBIOS.md)
---------------------------------------------------------------------------

v17 loops over UMD *counters* and, for each counter, looks up its SD partner
station. If that SD station has no reconstructed object (`HasStation` false),
the counter is skipped. So the parquet only ever contained SD stations that
were reconstructed.

To study the SD-muon asymmetry BEFORE that requirement we need SD stations that
were NOT reconstructed. Those cannot be recovered from the counter loop,
because Offline does not write UMD modules/channels for an SD station that did
not trigger. They simply are not in `MDEvent`. They ARE, however, in the list of
*simulated* SD stations, `SDEvent.GetSimStationVector()`.

So this reader produces TWO tables from ONE pass over the events:

  Table A  "modulos"        one row per UMD module (exactly your v17 table,
                            plus one boolean column `has_sd_rec`).
  Table B  "estaciones_sd"  one row per SIMULATED SD station per event,
                            reconstructed or not (NEW).

`modulos[modulos.has_sd_rec]` must reproduce your old parquet row for row.
That is how we check nothing was lost or changed.

---------------------------------------------------------------------------
HOW TO USE
---------------------------------------------------------------------------

    import lector_adst_v17_completo as lector
    lector.cargar_offline()                       # once, before any reading
    df_mod, df_sd, resumen = lector.readADST_surface_v17_completo(path)

or, for batch processing with multiprocessing, `lector.process_file_wrapper`
(see the notebook Procesamiento_ADST_v17_completo.ipynb).

The ROOT import happens when this module is imported, exactly like v8-2 imported
ROOT in its first cell. The Offline dictionary library is loaded explicitly by
`cargar_offline()`.
"""

import os
import re
import json
import time
import traceback

import numpy as np
import pandas as pd
import ROOT


# =========================================================================
# 0. LOADING THE OFFLINE LIBRARY  (your "Celda 1.1", moved into a function)
# =========================================================================

def cargar_offline():
    """
    Load the Auger Offline ADST dictionaries (libRecEventKG.so).

    Same logic as the first cell of Procesamiento_ADST_v8-2: read the
    AUGEROFFLINEROOT environment variable and load `lib/libRecEventKG.so`.

    CHANGE 0: it is a function (instead of top-level cell code) so that the
    notebook AND the pilot script call the same code. It also RETURNS the
    library path it loaded, so every run can print/record which Offline
    version read the files -- that turned out to matter (see CAMBIOS.md,
    "Offline library mismatch").
    """
    AugerOfflineRoot = os.environ.get("AUGEROFFLINEROOT")
    if AugerOfflineRoot is None:
        raise EnvironmentError(
            "AUGEROFFLINEROOT no definido. "
            "Reinicia Jupyter Lab desde una terminal donde hayas "
            "hecho 'source .../this-auger-offline.sh' de la versión de Offline elegida."
        )

    lib_path = os.path.join(AugerOfflineRoot, "lib", "libRecEventKG.so")
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"No se encontró la librería: {lib_path}")

    # Usamos gSystem.Load que es más robusto en PyROOT
    status = ROOT.gSystem.Load(lib_path)
    if status < 0:
        raise ImportError(f"Error cargando la librería: {lib_path}")

    print(f"AUGEROFFLINEROOT: {AugerOfflineRoot}")
    print(f"ROOT {ROOT.gROOT.GetVersion()} | librería cargada: {lib_path}")
    return lib_path


# =========================================================================
# 1. SMALL HELPERS
# =========================================================================

def getModuleList(counter, sim=True):
    """
    [UNCHANGED from v17 -- copied verbatim]

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


def _posicion_con_fallback(geo, detector_id):
    """
    Position of a detector in site coordinates, or None if it is not found.

    This is EXACTLY the try/except pattern v17 used twice (once for the SD
    tank, once for the UMD counter), written once so both tables use the same
    rule:
        1. try the ID as given;
        2. if that fails, try the "other" ID (ID +/- 100000);
        3. if that also fails, give up (return None).

    CHANGE (cosmetic): v17 used a bare `except:`. Here it is `except Exception:`.
    The only difference is that Ctrl-C (KeyboardInterrupt) now stops the run
    instead of being swallowed as "station not found". PyROOT turns C++
    exceptions (e.g. std::out_of_range) into Python exceptions that ARE
    subclasses of Exception, so they are still caught exactly as before.

    Note: when a lookup fails, Offline itself prints a line like
        ERROR DetectorGeometry::GetStationPosition(104218) nonexisting station
    to the C++ stdout of the process. That message also happened in your v17
    runs; you did not see it because Jupyter shows Python output in the
    notebook, not the C++ output of forked workers (that goes to the terminal
    that launched Jupyter). It is harmless: it is the fallback working.
    """
    try:
        return geo.GetStationPosition(detector_id)
    except Exception:
        try:
            alt_id = detector_id + 100000 if detector_id < 90000 else detector_id - 100000
            return geo.GetStationPosition(alt_id)
        except Exception:
            return None


def _proyectar_al_plano_mc(pos, pos_core_MC, mc_theta_rad, mc_phi_rad):
    """
    Project a site-coordinate position onto the TRUE (MC) shower plane.

    These are LITERALLY the v17 lines of the "True Core Fix (3D - MC Angles,
    MC Core)" block, moved into a function so that the module table (A) and the
    new SD-station table (B) are guaranteed to use the same arithmetic.
    Same operations in the same order -> bit-identical floats.

    Returns
    -------
    phi_plane_euler_MC_true_core : float, radians in [0, 2*pi)
        Includes the historical +pi ("MANTIENE CONVENCIÓN +180"). Your analysis
        undoes it with ((deg - 180) % 360), as in plots_seccion_6.py.
    r_core_MC : float, meters
        Distance to the shower axis in the shower plane.
    """
    dx_mc = pos.X() - pos_core_MC.X()
    dy_mc = pos.Y() - pos_core_MC.Y()
    dz_mc = pos.Z() - pos_core_MC.Z()

    # True Core Fix (3D - MC Angles, MC Core)
    v_sd_mc = ROOT.TVector3(dx_mc, dy_mc, dz_mc)
    v_sd_mc.RotateZ(-mc_phi_rad)
    v_sd_mc.RotateY(-mc_theta_rad)
    phi_e_mc_true_raw = np.arctan2(v_sd_mc.Y(), v_sd_mc.X())
    # Aplicamos el mismo parche +180 para comparar peras con peras
    phi_plane_euler_MC_true_core = (phi_e_mc_true_raw + np.pi + 2*np.pi) % (2*np.pi)
    r_core_MC = np.sqrt(v_sd_mc.X()**2 + v_sd_mc.Y()**2)
    return phi_plane_euler_MC_true_core, r_core_MC


# Column order of table B, fixed here so that even a file with zero SD
# stations produces a parquet with the right schema (pd.concat later needs it).
COLUMNAS_ESTACIONES_SD = [
    "event_id", "logE_MC", "theta_MC", "phi_MC", "primary",
    "sdId", "es_anillo_denso", "geometria_disponible",
    "r_core_MC", "phi_plane_euler_MC_true_core",
    "sd_nMuons_MC", "sd_nEM_MC",
    "has_sd_rec", "sdSignal_REC", "sd_is_candidate", "sd_is_silent",
    "tiene_counter_umd",
]


# =========================================================================
# 2. THE READER
# =========================================================================

def readADST_surface_v17_completo(fname, is_mc_simulation=True, max_events=None):
    """
    Leer un archivo ADST y devolver DOS tablas + un resumen.

    Returns
    -------
    df_modulos : DataFrame, 1 row per UMD MODULE
        Same columns as v17, plus `has_sd_rec` (bool).
        `df_modulos[df_modulos.has_sd_rec]` == your old v17 parquet.
    df_estaciones_sd : DataFrame, 1 row per SIMULATED SD station per event
        Columns in COLUMNAS_ESTACIONES_SD. Contains reconstructed AND
        non-reconstructed stations. No theta / radius / signal cuts.
    resumen : dict
        Counts of events, rows, and of every counter that was skipped, by reason.

    Parameters
    ----------
    fname : str
        Path to the ADST .root file.
    is_mc_simulation : bool
        Passed to getModuleList (module IDs 0-5 in simulation).
    max_events : int or None
        CHANGE 7: stop after this many events. None (the default) reads the
        whole file, i.e. exactly what v17 did. Only used for quick pilots.

    Lógica Clave (v17, still true):
    1. Itera sobre el MDEvent para encontrar TODOS los counters UMD.
    2. Usa el SDEvent como "diccionario" de geometría.
    3. NO filtra por 'IsLowGainSaturated', guarda un flag.
    4. Versión HÍBRIDA/ESTRICTA: Calcula posiciones 2D, rotaciones Euler (con +180 histórico)
       y la matemática estricta de Darko (C++ nativo sin +180).
    5. Guarda la señal REC y MC para el UMD y SD por separado.
    NEW in v17_completo:
    6. NO descarta counters por HasStation: lo guarda como flag `has_sd_rec`.
    7. Recorre además TODAS las estaciones SD simuladas (tabla B).
    """

    print(f"Iniciando lectura de: {os.path.basename(fname)}")

    if not os.path.exists(fname):
        print(f"Advertencia: Archivo no encontrado {fname}")
        return pd.DataFrame(), pd.DataFrame(columns=COLUMNAS_ESTACIONES_SD), {}

    # --- Inicialización de ROOT ---  [UNCHANGED]
    files = ROOT.std.vector('string')()
    files.push_back(fname)

    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    geo = ROOT.DetectorGeometry()

    file1.ReadDetectorGeometry(geo) # Ignoramos fallos (Warnings de TStreamerInfo)
    file1.SetBuffers(event)

    data = []            # rows of table A (modules), as in v17
    data_sd = []         # CHANGE 4: rows of table B (SD stations)
    event_count = 0
    start_time = time.time()

    # CHANGE 3: count every counter that does NOT produce module rows, and why.
    # In v17 these were silent `continue`s. Nothing is removed by counting them;
    # it only makes the losses visible in the printed summary.
    descartes = {
        "counter_sin_posicion_sd_en_geometria": 0,   # v17 skip, kept
        "counter_con_simCounter_None": 0,            # v17 skip, kept
    }
    counters_sin_sd_rec = 0   # counters that v17 would have skipped, now kept

    # --- COMIENZA EL BUCLE DE EVENTOS ---
    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        event_count += 1
        if event_count % 500 == 0:
            print(f"... procesados {event_count} eventos.")

        # --- Info Global del Evento (Lluvia) ---  [UNCHANGED]
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
        # (This is the reconstructed SHOWER, not a particular station. It exists
        #  whether or not a given station was reconstructed.)
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

        # CHANGE 4 (bookkeeping for table B): remember which SD IDs have a UMD
        # counter written in THIS event. See the column `tiene_counter_umd`.
        sd_ids_con_counter = set()

        # =================================================================
        # TABLE A -- Bucle sobre los COUNTERS  (your v17 loop)
        # =================================================================
        mEvent = event.GetMDEvent()
        counterIterator = mEvent.CountersBegin()
        countersEnd = mEvent.CountersEnd()

        while counterIterator != countersEnd:

            counter = counterIterator.__deref__() # Objeto Counter (estación)
            counterId = counter.GetId()
            sdId = counter.GetSdPartnerId()
            sd_ids_con_counter.add(int(sdId))

            # -----------------------------------------------------------------
            # CHANGE 1: HasStation is stored as a flag instead of being a skip.
            #
            # v17 did:
            #     sdStation = sEvent.GetStationById(sdId) if sEvent.HasStation(sdId) else None
            #     if sdStation is None:
            #         counterIterator += 1
            #         continue
            #
            # `HasStation(sdId)` answers ONE question: "is there a RECONSTRUCTED
            # SD station object with this ID?". It says nothing about the
            # simulated station (MC truth) or the UMD. So we keep the counter
            # and only avoid calling methods on a station object that does not
            # exist (CHANGE 2).
            #
            # To get back EXACTLY the old dataset:  df[df.has_sd_rec]
            # -----------------------------------------------------------------
            has_sd_rec = bool(sEvent.HasStation(sdId))
            sdStation = sEvent.GetStationById(sdId) if has_sd_rec else None
            if not has_sd_rec:
                counters_sin_sd_rec += 1

            # -----------------------------------------------------------------
            # CHANGE 2: getters of the RECONSTRUCTED station are guarded.
            # With a REC station: exactly the v17 calls and values.
            # Without one: NaN (unknown), NOT zero. "No reconstructed signal"
            # is not "zero signal".
            # -----------------------------------------------------------------
            if has_sd_rec:
                # --- Corte de Calidad 2: Saturación (Corte Diferido) ---
                is_sd_saturated = sdStation.IsLowGainSaturated()

                # Datos básicos de la reconstruccion
                sdSignal = sdStation.GetTotalSignal()
                sdSignal_err = sdStation.GetTotalSignalError()
                sdMuonSignal = sdStation.GetMuonSignal() # Suele ser 0 en Reco estándar
                r_core_err = sdStation.GetSPDistanceError()
            else:
                is_sd_saturated = pd.NA   # unknown (not "not saturated")
                sdSignal = np.nan
                sdSignal_err = np.nan
                sdMuonSignal = np.nan
                r_core_err = np.nan

            # --- CÁLCULO DE COMPONENTES MC (CONTEO DE PARTICULAS) ---  [UNCHANGED]
            # This block never needed the reconstructed station: it asks for the
            # SIMULATED station. So it now also runs when has_sd_rec is False.
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

            # ==================================================================
            # BIFURCACIÓN CORRECTA (Lógica Adaptada a IDs Mixtos) - Lazy Loading  [UNCHANGED]
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
            # CHANGE 2 (cont.): GetAzimuthSP is a method of the REC station.
            # Without it val_sp is NaN, so phi_plane_sp is NaN. Nothing else uses it.
            val_sp = sdStation.GetAzimuthSP() if has_sd_rec else np.nan
            if is_infill:
                phi_sp = val_sp - rec_phi_rad
            else:
                phi_sp = val_sp
            phi_plane_sp = (phi_sp + 2*np.pi) % (2*np.pi)

            # ==================================================================
            # ⚠️ DISCLAIMER UMD AZIMUTH NATIVO (COUNTER LEVEL) ⚠️  [kept from v17]
            # Análisis de datos en la v16 demostró que MdRecCounter NO guarda esta
            # variable (100% NaNs). Se comenta por performance reasons.
            # ==================================================================

            if is_anillo_denso:
                # --- CASO A: ANILLO DENSO (UMD 90k) ---
                # NO PEDIMOS geo.GetStationPosition() AQUÍ. Usamos directamente
                # las variables pre-calculadas del SP al funcionar bien y ser las correctas.
                #
                # CHANGE 2 (cont.): for the Dense Ring the coordinates themselves
                # come from the REC station. Without it we do not invent a position:
                # the row is kept (its MC counts are valid) with NaN coordinates.
                if has_sd_rec:
                    phi_rel = sdStation.GetAzimuthSP()
                    r_final = sdStation.GetSPDistance()
                    x_plane = r_final * np.cos(phi_rel)
                    y_plane = r_final * np.sin(phi_rel)

                    # Valores ficticios para que no quede en NaN
                    r_core_MC = r_final
                    r_umd_rec = r_final
                    r_umd_mc = r_final
                else:
                    r_final = np.nan
                    x_plane = np.nan
                    y_plane = np.nan

            else:
                # --- CASO B: INFILL (4k o 104k) / ESTÁNDAR ---  [UNCHANGED logic]
                # Nothing in this branch uses the reconstructed station: positions
                # come from `geo`, cores from the (MC or REC) shower, angles from MC.
                # --- EXTRACCIÓN DE POSICIONES FÍSICAS ---

                # A. Posición del Tanque SD
                pos_station = _posicion_con_fallback(geo, sdId)
                if pos_station is None:
                    # v17: `continue` ("Basura: ID no encontrado en Geometría").
                    # Kept, but counted (CHANGE 3).
                    descartes["counter_sin_posicion_sd_en_geometria"] += 1
                    counterIterator += 1
                    continue

                # B. [NUEVO] Posición del Módulo UMD enterrado
                is_true_umd_pos = True
                pos_umd = _posicion_con_fallback(geo, counterId)
                if pos_umd is None:
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
                # (same lines as v17, now in _proyectar_al_plano_mc so that
                #  table B uses identical arithmetic)
                phi_plane_euler_MC_true_core, r_core_MC = _proyectar_al_plano_mc(
                    pos_station, pos_core_MC, mc_theta_rad, mc_phi_rad)

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
            # -----------------------------------------------------------------
            # DELIBERATELY UNCHANGED:  `if simCounter is None:`
            #
            # Astra's "flag" version changed this to
            #     if simCounter is None or not simCounter:
            # which looks like a harmless safety check but is NOT: PyROOT returns
            # a *null proxy* (not None) when there is no simulated counter. v17
            # kept those counters -- their modules have no channels, so the
            # channel loop below never touches simCounter and nMuones_MC stays 0,
            # while the SD columns of the row are perfectly valid. The extra
            # `not simCounter` threw 63,747 such rows away in the 20 SIB proton
            # files (AUDITORIA_FILAS.md). Keeping v17's condition keeps those rows.
            # -----------------------------------------------------------------
            if simCounter is None:
                descartes["counter_con_simCounter_None"] += 1   # CHANGE 3: counted
                counterIterator += 1
                continue

            # --- Bucle sobre los MÓDULOS (Segmentos) ---  [UNCHANGED]
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

                # ⚠️ DISCLAIMER UMD AZIMUTH NATIVO (MODULE LEVEL) ⚠️  [kept from v17]
                # Resultado empírico: 100% de NaNs y hundimiento de performance por
                # Mutex lock de PyROOT. Se comenta la extracción.

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
                    "sdMuonSignal_REC": sdMuonSignal,   # REC Muon

                    # CHANGE 1: the only new column of table A.
                    "has_sd_rec": has_sd_rec,
                })

            counterIterator += 1 # Avanzamos al siguiente counter

        # =================================================================
        # TABLE B -- CHANGE 4: bucle sobre TODAS las estaciones SD SIMULADAS
        # =================================================================
        # Why a second loop: the counter loop above only sees SD stations that
        # have a UMD counter written in the ADST, and Offline does not write
        # UMD modules for SD stations that did not trigger. So the stations the
        # HasStation cut removed are NOT reachable from the counters. They are
        # reachable here, from the list of simulated SD stations.
        #
        # One row per simulated station, reconstructed or not. No cuts on
        # theta, radius, energy or signal: selection belongs to the analysis.
        for simStationB in sEvent.GetSimStationVector():
            sdIdB = int(simStationB.GetId())

            # Same ID convention as table A.
            es_anillo_denso = (90000 <= sdIdB < 100000)

            # Is there a RECONSTRUCTED station for this simulated one?
            has_sd_recB = bool(sEvent.HasStation(sdIdB))
            recStationB = sEvent.GetStationById(sdIdB) if has_sd_recB else None

            # --- Geometry in the TRUE shower plane (same arithmetic as table A) ---
            phi_true_B = np.nan
            r_true_B = np.nan
            geometria_disponible = False
            if not es_anillo_denso:
                # Dense Ring stations are virtual: they are not in DetectorGeometry.
                # Asking for their position only prints Offline errors (that is what
                # flooded Astra's log). v17 takes their coordinates from the REC
                # station, so for them use the module table, not this one.
                pos_B = _posicion_con_fallback(geo, sdIdB)
                if pos_B is not None:
                    phi_true_B, r_true_B = _proyectar_al_plano_mc(
                        pos_B, pos_core_MC, mc_theta_rad, mc_phi_rad)
                    geometria_disponible = True
                # If the position is missing the row is still KEPT, with NaN
                # geometry and geometria_disponible=False: nothing disappears.

            data_sd.append({
                # Event info (same values as in table A)
                "event_id": event_id_lluvia,
                "logE_MC": logE_MC,
                "theta_MC": theta_MC,
                "phi_MC": phi_MC,
                "primary": primary,

                # Station identity and geometry
                "sdId": sdIdB,
                "es_anillo_denso": es_anillo_denso,
                "geometria_disponible": geometria_disponible,
                "r_core_MC": r_true_B,                          # same definition as table A
                "phi_plane_euler_MC_true_core": phi_true_B,     # same definition, incl. +pi

                # MC truth counts: same getters as table A (simulated station).
                # Stored as float, like table A.
                "sd_nMuons_MC": float(simStationB.GetNumberOfMuons()),
                "sd_nEM_MC": float(simStationB.GetNumberOfElectrons())
                             + float(simStationB.GetNumberOfPhotons()),

                # The selection flag this whole study is about, plus a little
                # context about the reconstructed station when it exists.
                "has_sd_rec": has_sd_recB,
                "sdSignal_REC": recStationB.GetTotalSignal() if has_sd_recB else np.nan,
                "sd_is_candidate": bool(recStationB.IsCandidate()) if has_sd_recB else pd.NA,
                "sd_is_silent": bool(recStationB.IsSilent()) if has_sd_recB else pd.NA,

                # True if the ADST wrote a UMD *counter object* paired with this SD
                # station in this event. CAREFUL, two traps:
                #  - False does NOT mean "no UMD exists here" (the station may simply
                #    have no counter written);
                #  - True does NOT mean "UMD data exist": for SD stations that did not
                #    trigger, Offline often writes the counter but no modules/channels.
                #    In the pilot (Run010, 50 events) 4647 of 10398 non-reconstructed
                #    station occurrences had a counter, yet only 6 module rows came out.
                #    That is exactly why the counter loop cannot recover these stations.
                "tiene_counter_umd": sdIdB in sd_ids_con_counter,
            })

        # CHANGE 7: optional early stop for pilots (None = read everything).
        if max_events is not None and event_count >= max_events:
            break

    end_time = time.time()
    elapsed = end_time - start_time

    df = pd.DataFrame(data)
    df_sd = pd.DataFrame(data_sd, columns=COLUMNAS_ESTACIONES_SD)

    # Nullable dtypes, so that "unknown" (pd.NA) survives the parquet round trip
    # instead of turning a boolean column into generic Python objects.
    if not df.empty:
        df["is_sd_saturated"] = df["is_sd_saturated"].astype("boolean")
        df["has_sd_rec"] = df["has_sd_rec"].astype(bool)
    for col in ["sd_is_candidate", "sd_is_silent"]:
        df_sd[col] = df_sd[col].astype("boolean")

    resumen = {
        "archivo": os.path.basename(fname),
        "eventos_leidos": event_count,
        "segundos": round(elapsed, 2),
        "filas_modulos": len(df),
        "filas_modulos_con_sd_rec": int(df["has_sd_rec"].sum()) if not df.empty else 0,
        "counters_sin_sd_rec_conservados": counters_sin_sd_rec,
        "filas_estaciones_sd": len(df_sd),
        "estaciones_sd_con_rec": int(df_sd["has_sd_rec"].sum()),
        "descartes_counters": descartes,
    }

    print(f"Lectura completa. Total de eventos leídos: {event_count}")
    print(f"Tiempo total de lectura: {elapsed:.2f} segundos.")
    print(f"Total de 'MÓDULOS' (filas) extraídos: {len(df)} "
          f"(con SD REC: {resumen['filas_modulos_con_sd_rec']})")
    print(f"Total de ESTACIONES SD simuladas extraídas: {len(df_sd)} "
          f"(con SD REC: {resumen['estaciones_sd_con_rec']})")
    print(f"Counters descartados (mismas reglas que v17): {descartes}")

    return df, df_sd, resumen


# =========================================================================
# 3. FILENAME METADATA
# =========================================================================

# CHANGE 6: a regular expression instead of `filename.split('_')`.
#
# v17 did parts = filename.split('_') and took parts[0] as the model, parts[1]
# and parts[2] as energies, parts[3] as primary. That breaks when the MODEL name
# itself contains "_" -- e.g. "EPOSLHC_R_180_185_helium_...": parts[1] is "R",
# float("R") raises, the except prints a warning and the whole metadata block
# is silently missing from that production's parquet.
#
# The pattern reads:   <model>_<emin>_<emax>_<primary>_<anything>_Run<number>.root
# "<model>" is matched lazily (.+?) so it stops at the first "_<digits>_<digits>_".
#   SIB23e_175_180_proton_MdSdInfill_CORSIKA78010_FLUKA_Run010.root
#       -> model SIB23e,    e 17.5-18.0, proton, run 10   (same values as v17)
#   EPOSLHC_R_180_185_helium_MdSdInfill_CORSIKA78010_FLUKA_Run003.root
#       -> model EPOSLHC_R, e 18.0-18.5, helium, run 3    (v17 lost these)
_PATRON_NOMBRE = re.compile(
    r"^(?P<model>.+?)_(?P<emin>\d+)_(?P<emax>\d+)_(?P<primary>[^_]+)_.*_Run(?P<run>\d+)\.root$"
)


def metadatos_desde_nombre(filename):
    """Return the v17 metadata columns parsed from an ADST filename."""
    m = _PATRON_NOMBRE.match(filename)
    if m is None:
        raise ValueError(f"Nombre de archivo no reconocido: {filename}")
    return {
        "model_mc": m.group("model"),
        "e_min_mc": float(m.group("emin")) / 10.0,
        "e_max_mc": float(m.group("emax")) / 10.0,
        "primary_name_mc": m.group("primary"),
        "run_number": int(m.group("run")),
    }


# =========================================================================
# 4. WRITING SAFELY
# =========================================================================

def _guardar_parquet_atomico(df, output_path):
    """
    CHANGE 5: write to "<file>.tmp" first, then rename.

    `os.replace` is atomic on the same filesystem: the final name either does
    not exist or holds a COMPLETE file. v17 wrote directly to the final name,
    so a worker killed mid-write (out of memory, Ctrl-C, server reboot) left a
    truncated parquet, and the next run's "si ya existe, saltear" check would
    silently skip that file forever.
    """
    tmp_path = output_path + ".tmp"
    df.to_parquet(tmp_path, compression="snappy", index=False)
    os.replace(tmp_path, output_path)


# =========================================================================
# 5. FUNCIÓN "TRABAJADORA"  (one ROOT file -> two parquet files)
# =========================================================================

def process_file_wrapper(root_fpath, output_dir, max_events=None):
    """
    Your v8-2 worker, for use with multiprocessing.Pool.

    Output layout (CHANGE 5):
        <output_dir>/modulos/<run>.parquet         table A
        <output_dir>/estaciones_sd/<run>.parquet   table B
        <output_dir>/resumen/<run>.json            counts printed by the reader

    Returns a one-line string, exactly like v8-2: "✔ [Éxito]", "INFO", or
    "❌ [ERROR]" with the traceback. Errors do not stop the other workers.
    """
    # 1. Definir rutas
    filename = os.path.basename(root_fpath)
    stem = filename.replace(".root", "")
    dir_modulos = os.path.join(output_dir, "modulos")
    dir_estaciones = os.path.join(output_dir, "estaciones_sd")
    dir_resumen = os.path.join(output_dir, "resumen")
    for d in (dir_modulos, dir_estaciones, dir_resumen):
        os.makedirs(d, exist_ok=True)
    path_modulos = os.path.join(dir_modulos, stem + ".parquet")
    path_estaciones = os.path.join(dir_estaciones, stem + ".parquet")
    path_resumen = os.path.join(dir_resumen, stem + ".json")

    # 2. Evitar reprocesar
    # CHANGE 5: skip only if BOTH tables already exist. If one is missing the
    # file is read again and both are rewritten.
    if os.path.exists(path_modulos) and os.path.exists(path_estaciones):
        return f"INFO: El archivo ya existe, saltando: {stem}"

    # 3. Imprimir estado
    print(f"► [Iniciando]: {filename}")

    try:
        # ----- INICIO DEL TRABAJO -----
        start_file_time = time.time()

        df, df_sd, resumen = readADST_surface_v17_completo(root_fpath, max_events=max_events)

        if df.empty and df_sd.empty:
            return f"INFO: Archivo vacío o sin datos. Saltando: {filename}"

        # Extraer metadatos del nombre de archivo (CHANGE 6: regex parser).
        # Added to BOTH tables so each can be used on its own.
        try:
            meta = metadatos_desde_nombre(filename)
            for key, value in meta.items():
                if not df.empty:
                    df[key] = value
                df_sd[key] = value
        except Exception as e_parse:
            print(f"  Advertencia: No se pudo parsear metadata en {filename}: {e_parse}")

        # Guardar en Parquet (CHANGE 5: atomic writes, two tables + summary)
        _guardar_parquet_atomico(df, path_modulos)
        _guardar_parquet_atomico(df_sd, path_estaciones)
        with open(path_resumen + ".tmp", "w") as f:
            json.dump(resumen, f, indent=2)
        os.replace(path_resumen + ".tmp", path_resumen)

        # Liberar memoria
        del df, df_sd

        elapsed = time.time() - start_file_time
        return (f"✔ [Éxito]: {filename} -> modulos + estaciones_sd ({elapsed:.2f}s) | "
                f"módulos {resumen['filas_modulos']} "
                f"(sin SD REC: {resumen['filas_modulos'] - resumen['filas_modulos_con_sd_rec']}) | "
                f"estaciones SD {resumen['filas_estaciones_sd']} "
                f"(sin SD REC: {resumen['filas_estaciones_sd'] - resumen['estaciones_sd_con_rec']})")
        # ----- FIN DEL TRABAJO -----

    except Exception as e:
        # Si algo falla, retornamos el string de error
        return f"❌ [ERROR] en {filename}: {e}\n{traceback.format_exc()}"
