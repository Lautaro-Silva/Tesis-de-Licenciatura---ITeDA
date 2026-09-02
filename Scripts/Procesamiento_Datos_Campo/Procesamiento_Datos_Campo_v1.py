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
# # Procesamiento Paralelo — Datos Experimentales Auger SD-750 + UMD
#
# Procesa todos los archivos ADST de datos reales y los guarda como `.parquet`.  
# Adaptado del pipeline de simulaciones `v17/v8` con los cambios necesarios  
# para datos experimentales (sin MC truth, cortes de calidad estrictos).
#
# **Workflow:**
# 1. Setup del entorno Auger Offline
# 2. Configuración central (paths, años, cortes)
# 3. Funciones de lectura (v19) — documentadas exhaustivamente
# 4. Función trabajadora (`process_file_wrapper_data`)
# 5. Búsqueda de archivos + resume automático
# 6. Ejecución con `Pool(N_WORKERS)`

# %%
import os
import time
import glob
import traceback
import gc
import numpy as np
import pandas as pd
from multiprocessing import Pool
from functools import partial
import ROOT

# kError silencia los TStreamerInfo warnings que aparecen al leer
# archivos .root generados con versiones distintas de Offline.
# En el notebook de prueba usábamos kWarning; acá subimos el umbral
# para no saturar la salida cuando corren 8 workers en paralelo.
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kError

print('Imports OK')

# %%
AugerOfflineRoot = os.environ.get('AUGEROFFLINEROOT')
if AugerOfflineRoot is None:
    raise EnvironmentError(
        'AUGEROFFLINEROOT no definido.\n'
        'Correr Jupyter desde una terminal donde se haya hecho:\n'
        '  aug_set_version offline 4.0.1-icrc23-prod1-root6\n'
        '  source .../bin/this-auger-offline.sh'
    )
print(f'AUGEROFFLINEROOT: {AugerOfflineRoot}')

for lib in ['libRecEventKG.so']:
    lib_path = os.path.join(AugerOfflineRoot, 'lib', lib)
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f'No se encontro: {lib_path}')
    status = ROOT.gSystem.Load(lib_path)
    if status < 0:
        raise ImportError(f'Error cargando: {lib_path}')

print('Librerias cargadas. Listo!')

# %% [markdown]
# ## ⚙️ Configuración central
#
# **Editá solo esta celda** para cambiar qué datos procesar y con qué cortes.

# %%
# ================================================================
# CONFIGURACIÓN CENTRAL — Editá solo esta celda
# ================================================================

# Directorio raíz donde están los ADST, organizados como:
#   BASE_PATH / year / month / ADST_SUBSET_year_month_day.root
BASE_PATH  = '/srv/workspace_favalli/ngonzalez/ADSTs/v4r2'

# Años y meses a procesar
YEARS  = [2021, 2022, 2023, 2024, 2025, 2026]
MONTHS = ['01','02','03','04','05','06','07','08','09','10','11','12']

# Subset (PhaseI, PhaseII, PhaseIISPMT, etc.)
# Determina qué archivos buscar: ADST_PhaseI_YEAR_MONTH_DAY.root
SUBSET = ['PhaseI', 'PhaseIISPMTPhaseIIBeta']

# Directorio de salida para los .parquet resultantes
OUTPUT_DIR = '/home/lsilva/Github/parquet_datos_campo/'

# Número de workers en el Pool paralelo.
# Regla práctica: empezar con 4, subir a 8-10 si el servidor aguanta.
# Cada worker ocupa ~1-2 GB de RAM y un núcleo completo de CPU.
# Con más de 10 workers la ganancia es marginal por limitaciones de I/O.
N_WORKERS = 12

# ── Cortes de calidad ────────────────────────────────────────────────
# Se pasan a readADST_surface_data_v19 vía partial() en la celda de ejecución.
# Podés modificarlos sin tocar la función de lectura.
ONLY_6T5           = True   # Corte fiducial (recomendado: siempre True)
MIN_LOG_E          = 17.0   # log10(E / eV) mínimo
MAX_THETA_DEG      = 65.0   # Ángulo cenital máximo [grados]
SKIP_REJECTED_STAS = True   # Saltear estaciones SD rechazadas

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f'Output dir:  {OUTPUT_DIR}')
print(f'Cortes:      6T5={ONLY_6T5}, logE>={MIN_LOG_E}, theta<={MAX_THETA_DEG} deg')


# %% [markdown]
# ## 📦 Funciones de lectura — v19
#
# La función `readADST_surface_data_v19` está comentada exhaustivamente,  
# explicando cada diferencia con la versión de simulaciones (`v17`)  
# y el origen de cada corte de calidad (C++ del director, `ADSTReader.cc`).

# %%
# ===========================================================================
# CELDA: FUNCIONES DE LECTURA — versión v19 (Datos Experimentales)
# ===========================================================================

def getModuleList(counter, sim=False):
    """
    Devuelve los Módulos (segmentos de scintillador) de un Counter UMD.

    DIFERENCIA CLAVE entre simulaciones y datos reales:
    ─────────────────────────────────────────────────────
    sim=True  (simulaciones, v17): IDs 0, 1, 2, 3, 4, 5
      Los IDs en simulación son asignados secuencialmente por
      el framework de Offline al crear el evento simulado.

    sim=False (datos reales, v19): IDs 100, 101, ..., 115
      Los IDs en datos reales corresponden al número físico
      del segmento de hardware instalado en el campo (cada
      counter UMD del SD-750 puede tener hasta 3 módulos).

    Usamos HasModule() antes de GetModule() para no fallar si
    un módulo está físicamente ausente o sin datos en ese evento.
    """
    ids = range(0, 6) if sim else range(100, 116)
    return [counter.GetModule(mid) for mid in ids if counter.HasModule(mid)]


def readADST_surface_data_v19(
    fname,
    only_6T5=True,
    min_logE=17.0,
    max_theta_deg=65.0,
    skip_rejected_stations=True,
    verbose=False,
):
    """
    Lee un archivo ADST de DATOS EXPERIMENTALES del Observatorio Auger
    y retorna un DataFrame con una fila por módulo UMD en eventos
    que pasan todos los cortes de calidad.

    ================================================================
    HISTORIAL Y DIFERENCIAS RESPECTO A readADST_surface_v17
    (la versión para simulaciones)
    ================================================================

    La v17 procesaba simulaciones CORSIKA/FLUKA donde la 'verdad'
    completa (energía exacta, ángulos exactos, core exacto, muones
    inyectados) estaba disponible vía MCShower y SimCounter.

    La v19 procesa datos reales del Observatorio Auger (SD-750 + UMD)
    donde NADA de eso existe. Todos los cambios se describen abajo,
    con referencia al código C++ (ADSTReader.cc) que proporcionó
    el director como referencia de los cortes estándar.

    ----------------------------------------------------------------
    CAMBIO 1 — Sin MCShower (la diferencia más fundamental)
    ----------------------------------------------------------------
    En v17 (simulaciones), al inicio de cada evento hacíamos:

        MCShower = event.GetGenShower()
        logE_MC  = np.log10(MCShower.GetEnergy())
        theta_MC = MCShower.GetZenith() * 180.0 / np.pi
        phi_MC   = MCShower.GetAzimuth() * 180.0 / np.pi
        core_MC  = MCShower.GetCoreSiteCS()  # posición exacta del core
        primary  = MCShower.GetShortPrimaryName()

    En v19 (datos reales):
      → GetGenShower() existe pero devuelve un objeto vacío/inválido.
      → Llamarlo produce valores sin sentido o crashes silenciosos.
      → Se ELIMINÓ toda mención a MCShower/GetGenShower.
      → La energía, ángulos y core solo existen como RECONSTRUCCIÓN:

        sShower  = sEvent.GetSdRecShower()
        logE_REC = np.log10(sShower.GetEnergy())
        theta    = sShower.GetZenith() * 180.0 / np.pi
        phi      = sShower.GetAzimuth() * 180.0 / np.pi
        core_REC = sShower.GetCoreSiteCS()

    Esto también implica que variables como logE_MC, theta_MC,
    phi_MC, primary, phi_plane_euler_MC, phi_plane_ground_mc, y
    r_core_MC desaparecen completamente del DataFrame de salida.

    ----------------------------------------------------------------
    CAMBIO 2 — Sin SimCounter ni muones inyectados
    ----------------------------------------------------------------
    En v17 (simulaciones), la 'verdad' de muones del UMD se obtenía
    con una estructura anidada compleja:

        simCounter = mEvent.GetSimCounter(counterId)
        # Bucle sobre canales del módulo:
        while channelIterator != channelsEnd:
            channel   = channelIterator.__deref__()
            channelId = channel.GetId()
            if simCounter.HasSimScintillatorByChannel(moduleId, channelId):
                simScint = simCounter.GetSimScintillatorByChannelId(...)
                nMuones_MC += simScint.GetNumberOfInjectedMuons()
            channelIterator += 1

    En v19 (datos reales):
      → mEvent.GetSimCounter() retorna None siempre.
      → No existen 'muones inyectados': la lluvia fue real, no simulada.
      → Se eliminó GetSimCounter() y todo el bucle de canales.
      → La ÚNICA señal de muones disponible es la reconstruida:

        nMuones_REC = module.GetNumberOfEstimatedMuons()

      Este número es el resultado del algoritmo de reconstrucción
      del UMD que ajusta la forma del waveform para estimar cuántos
      muones cruzaron el scintillador. No es una verdad, es una medida.

    ----------------------------------------------------------------
    CAMBIO 3 — Cortes de calidad (del C++ del director)
    ----------------------------------------------------------------
    El director proporcionó ADSTReader.cc + ADSTReader.h como
    referencia de los cortes estándar del observatorio. Aquí se
    replica cada corte en Python, con su equivalente C++ comentado.

    [A] CORTE 6T5 — fiducial del arreglo (nivel de EVENTO)

        Código C++ original (ADSTReader.cc, Run()):

            if (!sdEvent.IsT5()) continue;
            int nNeighUB  = sdEvent.GetT5PriorActiveNeighbors().size();
            int nNeighUUB = sdEvent.GetT5PriorActiveUUBNeighbors().size();
            if (nNeighUB < 5 && nNeighUUB < 5) continue;

        Traducción Python (esta función):

            if not sEvent.IsT5(): continue
            n_ub  = sEvent.GetT5PriorActiveNeighbors().size()
            n_uub = sEvent.GetT5PriorActiveUUBNeighbors().size()
            if n_ub < 5 and n_uub < 5: continue

        ¿Qué significa T5 y por qué es el corte más importante?

        IsT5() verifica que la estación más activa de la lluvia
        ('hottest station') tenía sus 6 vecinos inmediatos activos
        en el momento del trigger. Garantiza que el core de la
        lluvia cayó DENTRO del arreglo activo.

        Sin T5, el core puede haber caído fuera del arreglo y la
        reconstrucción de energía, ángulo y core pueden ser muy
        malas. En simulaciones, el arreglo es ideal y este corte
        no es tan crítico. En datos reales, hay sectores del arreglo
        offline por mantenimiento o fallas, haciendo este corte
        imprescindible.

        UB  = Upgrade Board (electrónica vieja, Phase I)
        UUB = Upgraded Upgrade Board (electrónica nueva, Phase II)
        El OR entre ambos (nNeighUB>=5 OR nNeighUUB>=5) cubre el
        período de transición 2021-presente donde ambas coexisten.

        NOTA: en los datos de v4r2, muchos archivos ya vienen con
        pre-selección T5 aplicada en la producción, por eso el corte
        no tira eventos adicionales. Pero conviene dejarlo activo
        como seguro para datasets donde esto no sea el caso.

    [B] CORTE DE ENERGÍA (nivel de EVENTO)

        C++: if (logE < minLgE) continue;  (ADSTReader.cc, Run())
        Python: if logE < min_logE: continue

        Por defecto min_logE=17.0 (10^17 eV).
        El SD-750 alcanza 100% de eficiencia de trigger alrededor
        de ese umbral. Bajo ese valor hay sesgos de trigger que
        complican cualquier análisis estadístico.

    [C] CORTE DE ÁNGULO CENITAL (nivel de EVENTO)

        No está en el C++ del director pero es estándar en Auger.
        Por defecto max_theta_deg=65.0 grados.

        ¿Por qué 65°?
        Para theta > 65°, la lluvia es muy inclinada. El muón llega
        al UMD con una trayectoria más oblicua, recorriendo más
        camino en el scintillador. La respuesta del detector cambia
        y la reconstrucción de nMuones es menos confiable.
        La mayoría de análisis de composición usan 0-65°. Ademas
        son los angulos con los que trabaje en las simulaciones.

    [D] ESTACIONES SD RECHAZADAS (nivel de ESTACIÓN)

        C++: en ADSTReader.h (struct StationFlags) y Run()
        Python: if sdStation.IsRejected(): continue

        Causas frecuentes de rechazo en datos reales:
          lightning  : el tank fue golpeado por un rayo (señal espuria)
          noCalib    : sin constante de calibración VEM válida
          badSilent  : no respondió al trigger pero no hay razón conocida
          offGrid    : antena GPS/comunicaciones caída
          notAliveT2 : no respondió al trigger local T2
          lowGainSat : saturación del canal de baja ganancia

        En simulaciones este rechazo es raro (<1%).
        En datos reales es normal ver 5-15% de estaciones rechazadas.

        Al final lo guardamos como flag

    [E] COUNTERS UMD RECHAZADOS (nivel de COUNTER)

        Python: if counter.IsRejected(): continue

        El UMD tiene su propio sistema de calidad independiente del SD.
        Un counter puede ser rechazado por problemas en la electrónica
        del UMD (EASIER board) sin que el WCD asociado tenga problemas.

        Al final lo guardamos como flag

    ----------------------------------------------------------------
    CAMBIO 4 — Geometría simplificada (sin DetectorGeometry)
    ----------------------------------------------------------------
    En v17 (simulaciones), cargábamos la geometría del detector y
    calculábamos manualmente la posición en el plano de lluvia:

        geo = ROOT.DetectorGeometry()               # objeto costoso
        file1.ReadDetectorGeometry(geo)             # lectura lenta
        pos_station = geo.GetStationPosition(sdId)  # por estación
        dx = pos_station.X() - core_MC.X()
        dy = pos_station.Y() - core_MC.Y()
        # ... rotaciones 3D con TVector3 para phi_euler ...

    En v19 (datos reales):
      → NO se usa DetectorGeometry. Mejora la velocidad ~2x.
      → El framework de Offline ya calculó estas distancias al
        reconstruir el evento. Se acceden directamente:

        r_core      = sdStation.GetSPDistance()    # distancia al core [m]
        phi_plane   = sdStation.GetAzimuthSP()     # azimuth relativo [rad]

      → SP = Shower Plane (plano de lluvia). Las coordenadas ya están
        en el sistema de referencia del eje de la lluvia.

      → ATENCIÓN: phi_plane_sp devuelve valores en [-pi, pi],
        NO en [0, 2pi]. Para normalizar en el análisis posterior:
            phi_normalizado = phi_plane_sp % (2 * np.pi)

    ----------------------------------------------------------------
    CAMBIO 5 — verbose=False para no saturar Jupyter en paralelo
    ----------------------------------------------------------------
    La v17 imprimía progreso cada 500 eventos:
        print(f'... procesados {event_count} eventos.')

    Con 8 workers corriendo simultáneamente, esto genera cientos de
    líneas mezcladas por segundo y puede disparar el error:
        'IOPub data rate exceeded'
    (el mismo que aparece en los outputs del notebook de simulaciones).

    Con verbose=False (default), la función no imprime nada.
    El wrapper process_file_wrapper_data maneja el log de progreso
    a nivel de archivo (un mensaje por archivo, no por evento).

    ----------------------------------------------------------------
    Parameters
    ----------------------------------------------------------------
    fname : str
        Ruta al archivo .root. Ej: ADST_PhaseI_2021_04_03.root
    only_6T5 : bool
        Aplicar el corte fiducial 6T5. Siempre True en producción.
    min_logE : float
        log10(E/eV) mínimo aceptado. Default 17.0.
    max_theta_deg : float
        Ángulo cenital máximo [grados]. Default 60.0.
    skip_rejected_stations : bool
        Saltear estaciones SD marcadas como rechazadas. Default True.
    verbose : bool
        Imprimir resumen al final. Default False (para Pool paralelo).

    Returns
    -------
    pd.DataFrame
        Una fila por módulo UMD que pasó todos los cortes.
        Columnas: event_id, logE_REC, theta_REC, phi_REC, core_x, core_y,
        counterId, sdId, moduleId, nMuones_REC, module_status,
        r_core, r_core_err, phi_plane_sp,
        is_sd_saturated, sdSignal_REC, sdSignal_err, sdMuonSignal_REC.
        (El wrapper agrega: subset, year, month, day.)
    """
    if not os.path.exists(fname):
        return pd.DataFrame()

    # ── Inicialización de ROOT ─────────────────────────────────────────
    # DIFERENCIA con v17: en v17 también creábamos DetectorGeometry aquí.
    # En v19 no lo necesitamos: el SDEvent ya tiene la geometría calculada.
    # Esto elimina la llamada a ReadDetectorGeometry() que era costosa.
    files = ROOT.std.vector('string')()
    files.push_back(fname)
    file1 = ROOT.RecEventFile(files)
    event = ROOT.RecEvent()
    file1.SetBuffers(event)

    data = []
    n_read = n_no_energy = n_no_t5 = n_theta_cut = n_passed = 0
    t0 = time.time()

    # ── BUCLE PRINCIPAL DE EVENTOS ─────────────────────────────────────
    while file1.ReadNextEvent() == ROOT.RecEventFile.eSuccess:
        n_read += 1

        # SDEvent: contiene la reconstrucción del detector de superficie.
        # DIFERENCIA v17: en v17 también accedíamos a event.GetGenShower()
        # para la verdad MC. En v19 NO lo hacemos: devuelve datos inválidos.
        sEvent  = event.GetSDEvent()
        sShower = sEvent.GetSdRecShower()

        # ── CORTE A: ENERGÍA ───────────────────────────────────────────
        # C++: if (logE < minLgE) continue;
        rec_energy = sShower.GetEnergy()
        if rec_energy <= 0:
            n_no_energy += 1
            continue
        logE = np.log10(rec_energy)
        if logE < min_logE:
            n_no_energy += 1
            continue

        # ── CORTE B: 6T5 FIDUCIAL ──────────────────────────────────────
        # Traducción exacta del C++ del director (ADSTReader.cc):
        #   if (!sdEvent.IsT5()) continue;
        #   if (nNeighUB < 5 && nNeighUUB < 5) continue;
        if only_6T5:
            if not sEvent.IsT5():
                n_no_t5 += 1
                continue
            n_ub  = sEvent.GetT5PriorActiveNeighbors().size()
            n_uub = sEvent.GetT5PriorActiveUUBNeighbors().size()
            if n_ub < 5 and n_uub < 5:
                n_no_t5 += 1
                continue

        # ── CORTE C: ÁNGULO CENITAL ────────────────────────────────────
        theta = sShower.GetZenith() * 180.0 / np.pi
        if theta > max_theta_deg:
            n_theta_cut += 1
            continue

        n_passed += 1

        # ── Variables del evento que pasó los cortes ───────────────────
        # DIFERENCIA v17: en v17 aquí también extraíamos logE_MC,
        # theta_MC, phi_MC, core_MC, primary de MCShower.
        # En v19 solo existe la reconstrucción.
        ev_id          = event.GetEventId()
        phi            = sShower.GetAzimuth() * 180.0 / np.pi
        pos_core       = sShower.GetCoreSiteCS()
        core_x, core_y = pos_core.X(), pos_core.Y()

        # ── BUCLE SOBRE COUNTERS (estaciones UMD) ─────────────────────
        mEvent   = event.GetMDEvent()
        it, end  = mEvent.CountersBegin(), mEvent.CountersEnd()

        while it != end:
            c    = it.__deref__()
            cid  = c.GetId()
            # sdPartnerId: ID de la estación WCD (SD) asociada a este UMD.
            # Con esto 'linkeamos' el MDEvent con el SDEvent.
            sdId = c.GetSdPartnerId()

            # Si la estación SD no participó en la reconstrucción de
            # este evento, no tiene sentido incluirla.
            if not sEvent.HasStation(sdId):
                it += 1
                continue
            st = sEvent.GetStationById(sdId)

            # ── CORTE D: ESTACIÓN SD RECHAZADA ─────────────────────────
            # C++: struct StationFlags en ADSTReader.h
            # Causas: lightning, noCalib, badSilent, offGrid, ...

            # ── CORTE E: COUNTER UMD RECHAZADO ─────────────────────────


            # Guardamos los flags de rechazo como columnas en el DataFrame.
            # NO hacemos skip: es el análisis quien decide qué filtrar.
            # Esto permite estudiar la fracción de rechazo y sus causas,
            # y comparar señal de módulos "buenos" vs "rechazados".
            # Para análisis limpio: df[~df['is_sd_rejected'] & ~df['is_counter_rejected']]
            is_sd_rejected      = st.IsRejected()
            is_counter_rejected = c.IsRejected()

            # ── Geometría en el plano de lluvia ─────────────────────────
            # DIFERENCIA v17: en v17 calculábamos r y phi manualmente
            # con geo.GetStationPosition() y rotaciones TVector3.
            # En v19 usamos directamente los valores del SDEvent.
            # RECORDAR: phi_plane_sp está en [-pi, pi], no en [0, 2pi].
            r_core       = st.GetSPDistance()
            r_core_err   = st.GetSPDistanceError()
            phi_plane_sp = st.GetAzimuthSP()

            # ── Señales del WCD (SD) ─────────────────────────────────────
            is_sat        = st.IsLowGainSaturated()
            sd_signal     = st.GetTotalSignal()       # [VEM]
            sd_signal_err = st.GetTotalSignalError()  # [VEM]
            sd_muon_sig   = st.GetMuonSignal()        # [VEM] suele ser 0

            # ── BUCLE SOBRE MÓDULOS UMD ──────────────────────────────────
            # DIFERENCIA v17: sim=True usaba IDs 0-5 (simulación).
            # En v19: sim=False usa IDs 100-115 (hardware real).
            for m in getModuleList(c, sim=False):

                # Señal reconstruida del módulo.
                # DIFERENCIA v17: en v17 también teníamos nMuones_MC
                # (verdad de la simulación via GetNumberOfInjectedMuons).
                # En v19 nMuones_REC es la ÚNICA medida de muones disponible.
                nMuones_REC = m.GetNumberOfEstimatedMuons()
                moduleId    = m.GetId()

                # Estado del módulo (flag de calidad de la reconstrucción UMD)
                # candidate: módulo usado activamente en la reconstrucción
                # saturated: señal alta, reconstrucción con incerteza mayor
                # rejected:  excluido por el control de calidad del UMD
                # silent:    sin señal (puede ser normal a grandes distancias)
                # undefined: estado no reconocido (no debería ocurrir)
                if   m.IsCandidate(): s = 'candidate'
                elif m.IsSaturated(): s = 'saturated'
                elif m.IsRejected():  s = 'rejected'
                elif m.IsSilent():    s = 'silent'
                else:                 s = 'undefined'

                data.append({
                    'event_id':         ev_id,
                    # Lluvia (solo reconstrucción; no hay verdad MC)
                    'logE_REC':         logE,
                    'theta_REC':        theta,
                    'phi_REC':          phi,
                    'core_x':           core_x,
                    'core_y':           core_y,
                    
                    # Identidad del módulo
                    'counterId':        cid,
                    'sdId':             sdId,
                    'moduleId':         moduleId,
                    
                    # Señal UMD
                    'nMuones_REC':      nMuones_REC,
                    'module_status':    s,
                    
                    # Geometría (plano de lluvia, calculada por Offline)
                    'r_core':           r_core,
                    'r_core_err':       r_core_err,
                    'phi_plane_sp':     phi_plane_sp,  # en [-pi, pi]
                    
                    # Señal del WCD (SD) asociado
                    'is_sd_saturated':  is_sat,
                    'is_sd_rejected':     is_sd_rejected,      # flag: lightning, noCalib, etc.
                    'is_counter_rejected': is_counter_rejected, # flag: falla del UMD
                    'sdSignal_REC':     sd_signal,
                    'sdSignal_err':     sd_signal_err,
                    'sdMuonSignal_REC': sd_muon_sig,
                })

            it += 1

    # ── Resumen opcional ──────────────────────────────────────────────
    if verbose:
        elapsed = time.time() - t0
        fn = os.path.basename(fname)
        print(f'  [{fn}]')
        print(f'    Leidos={n_read} | Pasaron={n_passed} | Filas={len(data)}')
        print(f'    Tirados: E={n_no_energy} T5={n_no_t5} theta={n_theta_cut}')
        print(f'    Tiempo: {elapsed:.1f}s')

    return pd.DataFrame(data)


# %% [markdown]
# ## 🔧 Función trabajadora
#
# Misma arquitectura que `process_file_wrapper` de simulaciones:  
# recibe un path, llama a la función de lectura, guarda el `.parquet`,  
# retorna un string de resultado (`✔`, `❌`, o `INFO`).

# %%
def process_file_wrapper_data(
    root_fpath,
    output_dir,  # Este ahora actúa como el OUTPUT_DIR base
    only_6T5=True,
    min_logE=17.0,
    max_theta_deg=65.0,
    skip_rejected_stations=True,
):
    """
    Función trabajadora para el Pool paralelo.
    Modificada para guardar los archivos organizados en subcarpetas Año/Mes.
    """
    filename       = os.path.basename(root_fpath)
    output_fname   = filename.replace('.root', '.parquet')
    
    # ── Parsear año y mes al inicio para definir la subcarpeta de salida ──
    try:
        parts = filename.replace('.root', '').split('_')
        year  = parts[2]   # Mantiene el formato string (ej: '2021')
        month = parts[3]   # Mantiene el formato string (ej: '04')
        specific_output_dir = os.path.join(output_dir, year, month)
    except Exception as e_parse:
        # Fallback por si algún archivo no cumple con el formato esperado
        specific_output_dir = output_dir
        print(f'  Advertencia: No se pudo determinar subcarpeta para {filename}: {e_parse}')
        year, month = "raiz", ""

    output_path = os.path.join(specific_output_dir, output_fname)

    # ── Resume automático (ahora busca en la subcarpeta correcta) ───────
    if os.path.exists(output_path):
        return f'INFO: Ya existe, saltando: {year}/{month}/{output_fname}'

    print(f'► [Iniciando]: {filename}')

    try:
        t0 = time.time()

        # verbose=False: sin prints por evento.
        df = readADST_surface_data_v19(
            root_fpath,
            only_6T5=only_6T5,
            min_logE=min_logE,
            max_theta_deg=max_theta_deg,
            skip_rejected_stations=skip_rejected_stations,
            verbose=False,
        )

        if df.empty:
            return f'INFO: Sin datos tras los cortes: {filename}'

        # ── Parsear metadatos para el DataFrame ───────────────────────────
        try:
            parts        = filename.replace('.root', '').split('_')
            df['subset'] = parts[1]       # 'PhaseI', 'PhaseII', etc.
            df['year']   = int(parts[2])  # 2021
            df['month']  = int(parts[3])  # 4
            df['day']    = int(parts[4])  # 3
        except Exception as e_parse:
            print(f'  Advertencia: no se pudo parsear metadata en DataFrame para {filename}: {e_parse}')

        # ── Crear la subcarpeta dinámicamente si no existe ──────────────
        # 'exist_ok=True' es vital para entornos paralelos (evita colisiones entre workers)
        os.makedirs(specific_output_dir, exist_ok=True)

        # ── Guardar en Parquet ─────────────────────────────────────────
        df.to_parquet(output_path, compression='snappy', index=False)

        # ── Liberar memoria explícitamente ─────────────────────────────
        del df
        gc.collect()

        elapsed = time.time() - t0
        return f' [Exito]: {filename} → {year}/{month}/{output_fname} ({elapsed:.1f}s)'

    except Exception:
        return f' [ERROR] en {filename}:\n{traceback.format_exc()}'


# %% [markdown]
# ## 📂 Búsqueda de archivos
#
# Construye la lista de todos los `.root` a procesar  
# e indica cuántos ya tienen su `.parquet` (resume automático).

# %%
# ── Construir la lista de todos los archivos a procesar ────────────────
# Asumiendo que ahora tienes una lista llamada SUBSET
# Ejemplo: SUBSETS = ['subsetA', 'subsetB', 'subsetC']

print(f'Buscando archivos para los subsets: {SUBSET}')
print(f'Directorio base:   {BASE_PATH}')
print()

all_files = []

# Iteramos primero sobre cada subset
for subset in SUBSET:
    print(f'--- Buscando archivos para: {subset} ---')
    subset_files = []
    
    for year in YEARS:
        for month in MONTHS:
            pattern = os.path.join(
                BASE_PATH, str(year), month,
                f'ADST_{subset}_{year}_{month}_*.root'
            )
            day_files = sorted(glob.glob(pattern))
            subset_files.extend(day_files)
            
            if day_files:
                print(f'  {year}/{month}: {len(day_files):>2} dias')
                
    all_files.extend(subset_files)
    print(f'Archivos encontrados para {subset}: {len(subset_files)}\n')

print(f'Total de archivos encontrados (todos los subsets): {len(all_files)}')

# ── Chequear cuáles ya están procesados (resume) ──────────────────────
# Esta parte del código se mantiene prácticamente igual, ya que `all_files` 
# ahora contiene las rutas absolutas de todos los subsets combinados.

ya_listos = [
    f for f in all_files
    if os.path.exists(
        os.path.join(OUTPUT_DIR, os.path.basename(f).replace('.root', '.parquet'))
    )
]

pendientes = len(all_files) - len(ya_listos)
print(f'Ya procesados (se saltearán): {len(ya_listos)}')
print(f'Pendientes de procesar:       {pendientes}')

# %% [markdown]
# ## 🚀 Ejecución paralela
#
# Mismo patrón que en simulaciones: `partial()` + `Pool.map()`.  
# Si un archivo ya tiene su `.parquet`, se saltea automáticamente.  
# Podés interrumpir y retomar sin perder trabajo.

# %%
if not all_files:
    print('ERROR: No se encontraron archivos. Revisá BASE_PATH y SUBSETS.')

elif pendientes == 0:
    print('Todos los archivos ya están procesados. Nada que hacer.')

else:
    print(f'--- INICIANDO PROCESO PARALELO ({N_WORKERS} workers) ---')
    print(f'Archivos pendientes: {pendientes}')
    print(f'Cortes: 6T5={ONLY_6T5}, logE>={MIN_LOG_E}, theta<={MAX_THETA_DEG}')
    print()

    t_total = time.time()

    # ── Función parcial con parámetros congelados ─────────────────────
    # partial() 'congela' los argumentos fijos (output_dir, cortes),
    # dejando solo root_fpath variable. Así pool.map() puede distribuir
    # la lista de archivos sin necesidad de tuplas ni estructuras extra.
    # Mismo patrón que en la versión de simulaciones (v17/v8).
    # OUTPUT_DIR funciona ahora como el directorio "base" a partir del cual
    # la función creará las carpetas de Año/Mes.
    process_func = partial(
        process_file_wrapper_data,
        output_dir             = OUTPUT_DIR,
        only_6T5               = ONLY_6T5,
        min_logE               = MIN_LOG_E,
        max_theta_deg          = MAX_THETA_DEG,
        skip_rejected_stations = SKIP_REJECTED_STAS,
    )

    # ── Ejecución paralela ────────────────────────────────────────────
    # Pool crea N_WORKERS procesos Python independientes.
    # pool.map() distribuye all_files entre ellos y espera a que
    # todos terminen antes de retornar la lista de resultados.
    # Cada worker carga sus propias librerías de ROOT y Offline:
    # por eso es IMPRESCINDIBLE que el entorno Auger esté cargado
    # antes de abrir Jupyter (la celda de setup lo verifica).
    with Pool(processes=N_WORKERS) as pool:
        results = pool.map(process_func, all_files)

    print('\n--- Proceso Paralelo Completado ---\n')

    # ── Resultados ────────────────────────────────────────────────────
    exitos = 0
    errores = 0
    skipped_exist = 0
    skipped_nodata = 0

    # Creamos un nombre de archivo único para el log usando la fecha/hora
    log_filename = f"log_procesamiento_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    log_filepath = os.path.join(OUTPUT_DIR, log_filename)

    # Abrimos el archivo de texto en modo escritura ('w')
    with open(log_filepath, 'w', encoding='utf-8') as f_log:
        f_log.write(f"=== Log de Procesamiento: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f_log.write(f"Cortes: 6T5={ONLY_6T5}, logE>={MIN_LOG_E}, theta<={MAX_THETA_DEG}\n")
        f_log.write("-" * 60 + "\n\n")

        for res in results:
            print(res)
            
            # Guardamos la misma línea en el log
            f_log.write(res + "\n")

            if ' [Exito]' in res: exitos += 1
            elif ' [ERROR]' in res: errores += 1
            elif 'Ya existe' in res: skipped_exist += 1
            elif 'Sin datos' in res: skipped_nodata += 1

        elapsed_min = (time.time() - t_total) / 60
        
        # Armamos el texto del resumen final
        resumen_txt = (
            f"\n--- Resumen ---\n"
            f"Tiempo total:          {elapsed_min:.2f} minutos\n"
            f"Archivos procesados:   {exitos}\n"
            f"Ya existían:           {skipped_exist}\n"
            f"Sin datos post-cortes: {skipped_nodata}\n"
            f"Con errores:           {errores}\n"
            f"Parquets en:           {OUTPUT_DIR} (organizados por Año/Mes)\n"
        )
        
        f_log.write("\n" + "-" * 60)
        f_log.write(resumen_txt)

    print(resumen_txt)
    print(f"Log detallado guardado en: {log_filepath}")

# %%
