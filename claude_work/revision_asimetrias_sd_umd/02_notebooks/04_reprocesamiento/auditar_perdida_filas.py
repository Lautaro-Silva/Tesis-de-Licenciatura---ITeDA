"""Auditoría de parquet existentes: NO importa ROOT ni ejecuta el procesamiento.

Una pareja de archivos a la vez; sin multiprocessing. Escribe sólo informes
pequeños en esta carpeta, nunca modifica los parquet ni el notebook del autor.
Usa las funciones de ajuste de la sección 5 mediante AST, sin ejecutar sus celdas.
"""
import ast
from collections import Counter
import hashlib
import contextlib
import io
from pathlib import Path
import re

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
OLD = Path('/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17')
NEW = Path('/home/lsilva/Github/ADST_Alexey_module_v12_flag/parquet_sib_proton_17')
KEY = ['event_id', 'counterId', 'moduleId', 'sdId']
STATION_KEY = ['source', 'event_id', 'sdId']


def window(frame, name):
    # Mismo universo Infill y banda angular/radial de la sección 5.
    cut = frame.loc[(frame.counterId >= 100000) & frame.theta_MC.ge(30) & frame.theta_MC.lt(40)
                    & frame.r_core_MC.ge(150) & frame.r_core_MC.lt(1800)].copy()
    cut['source'] = name.replace('.parquet', '.root')
    cut['phi_MC_Truth'] = (np.rad2deg(cut.phi_plane_euler_MC_true_core) % 360) - 180
    return cut


def main():
    old_files = {p.name:p for p in OLD.glob('*.parquet')}
    new_files = {p.name:p for p in NEW.glob('*.parquet')}
    assert old_files.keys() == new_files.keys(), 'Primero resolver archivos faltantes/sobrantes.'
    totals, unequal, lost_status = Counter(), Counter(), Counter()
    file_rows, old_parts, new_parts, lost_parts = [], [], [], []
    for name in sorted(old_files):
        a = pd.read_parquet(old_files[name]); b = pd.read_parquet(new_files[name])
        assert set(b.columns) == set(a.columns) | {'has_sd_rec'}
        assert not a.duplicated(KEY).any() and not b.duplicated(KEY).any()
        ai, bi = a.set_index(KEY), b.set_index(KEY)
        lost = ai.loc[~ai.index.isin(bi.index)].reset_index()
        added = bi.loc[~bi.index.isin(ai.index)].reset_index()
        common = ai.loc[ai.index.isin(bi.index)]
        paired = bi.reindex(common.index)
        for col in ai.columns:
            same = common[col].eq(paired[col]) | (common[col].isna() & paired[col].isna())
            unequal[col] += int((~same).sum())
        lost_status.update(lost.module_status.value_counts().to_dict())
        ea, eb = set(a.event_id), set(b.event_id)
        row = dict(file=name, old=len(a), new=len(b), new_true=int(b.has_sd_rec.sum()),
                   new_false=int((~b.has_sd_rec).sum()), old_only=len(lost), new_only=len(added),
                   common=len(common), lost_umd_mc_zero=int(lost.nMuones_MC.eq(0).sum()),
                   lost_umd_rec_zero=int(lost.nMuones_REC.eq(0).sum()),
                   lost_umd_rec_nan=int(lost.nMuones_REC.isna().sum()),
                   lost_sd_mc_known=int(lost.sd_nMuons_MC.notna().sum()),
                   lost_sd_mc_positive=int(lost.sd_nMuons_MC.gt(0).sum()),
                   old_events=len(ea), new_events=len(eb), old_only_events=len(ea-eb), new_only_events=len(eb-ea))
        assert len(b) == len(a)-len(lost)+len(added)
        assert len(added) == int((~b.has_sd_rec).sum())
        assert not added.has_sd_rec.any()
        totals.update({k:v for k,v in row.items() if k != 'file'})
        file_rows.append(row)
        old_parts.append(window(a, name)); new_parts.append(window(b, name)); lost_parts.append(window(lost, name))
        print(name, '| old:',len(a),'new:',len(b),'lost:',len(lost),'added:',len(added),flush=True)
    old_window = pd.concat(old_parts, ignore_index=True)
    new_window = pd.concat(new_parts, ignore_index=True)
    lost_window = pd.concat(lost_parts, ignore_index=True)
    old_sd = old_window.drop_duplicates(STATION_KEY)
    new_sd = new_window.drop_duplicates(STATION_KEY)
    raw = pd.read_csv(PACKAGE/'04_soporte/tablas/adst_counts_fast.csv', dtype={'event_id':str})
    raw['r_core_MC'] = raw.r
    raw['phi_MC_Truth'] = np.rad2deg(raw.phi)
    raw['sd_nMuons_MC'], raw['sd_nEM_MC'] = raw.mu, raw.em
    old_sd['event_id'] = old_sd.event_id.astype(str)
    new_sd['event_id'] = new_sd.event_id.astype(str)
    # Verificar respaldo del resultado anterior, no sólo volver a citarlo.
    join = raw.merge(old_sd, on=STATION_KEY, how='outer', suffixes=('_raw','_old'), indicator=True, validate='one_to_one')
    assert not join._merge.eq('right_only').any()
    assert join._merge.eq('both').equals(join.has_rec.eq(1))
    match = join.loc[join._merge.eq('both')]
    for c in ['sd_nMuons_MC','sd_nEM_MC']:
        assert np.array_equal(match[c+'_raw'], match[c+'_old'])
    max_radius_delta = float(abs(match.r_core_MC_raw-match.r_core_MC_old).max())
    max_phi_delta = float(abs((match.phi_MC_Truth_raw-match.phi_MC_Truth_old+180)%360-180).max())
    assert max_radius_delta < 1e-6 and max_phi_delta < 1e-6
    nidx = pd.MultiIndex.from_frame(new_sd[STATION_KEY])
    ridx = pd.MultiIndex.from_frame(raw[STATION_KEY])
    recovered = ridx.isin(nidx) & raw.has_rec.eq(0)

    # Cargar únicamente las dos funciones del estimador existente, sin sus tandas.
    path = PACKAGE/'02_notebooks/02_reproduccion/reproducir_desglose_sd.py'
    tree = ast.parse(path.read_text())
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'harmonic_model','fit_one_band'}]
    assert len(defs) == 2
    edges = np.linspace(-180,180,13)
    ns = {'np':np,'pd':pd,'curve_fit':curve_fit,'phi_bin_edges':edges,'phi_centers':(edges[1:]+edges[:-1])/2}
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(path),'exec'), ns)
    fit = ns['fit_one_band']
    samples = {'SD_sim_vector_all':raw, 'SD_sim_vector_HasStation':raw.loc[raw.has_rec.eq(1)],
               'old_parquet_SD_unique':old_sd, 'new_flag_true_SD_unique':new_sd.loc[new_sd.has_sd_rec],
               'new_all_SD_unique':new_sd}
    fit_rows = []
    for sample, table in samples.items():
        for col in ['sd_nMuons_MC','sd_nEM_MC']:
            for lo in range(150,1201,150):
                band = table.loc[table.r_core_MC.ge(lo) & table.r_core_MC.lt(lo+150)]
                fit_rows.append(dict(sample=sample,column=col,r_min=lo,r_max=lo+150,**fit(band,col)))
    fits = pd.DataFrame(fit_rows)

    # El log paralelo permite sumar filas/eventos, pero no asignar una línea de
    # terminación a un archivo sólo por su proximidad: los prints se intercalan.
    log = (HERE/'outputs.txt').read_text()
    log_parts = log.split('OUTPUT NUEVO:')
    log_totals = []
    for label, text in zip(['old','new'], log_parts):
        rows = [int(x) for x in re.findall(r"Total de 'MÓDULOS' \(filas\) extraídos: (\d+)",text)]
        events = [int(x) for x in re.findall(r'Total de eventos leídos: (\d+)',text)]
        log_totals.append(dict(version=label,files_completed=len(rows),rows=sum(rows),events=sum(events),
                               warning_lines=len(re.findall(r'Warning|warning|TStreamer',text))))
    perfile = pd.DataFrame(file_rows)
    perfile.to_csv(HERE/'auditoria_filas_por_archivo.csv',index=False)
    fits.to_csv(HERE/'auditoria_filas_ajustes.csv',index=False)
    far = fits.loc[fits.column.eq('sd_nMuons_MC') & fits.r_min.eq(1200)]
    table_lines = ['| Muestra, una fila SD/evento | A1, 1200–1350 m | Error formal | Filas |',
                   '|---|---:|---:|---:|']
    for row in far.itertuples():
        table_lines.append(f'| {row.sample} | {row.A1:+.8f} | {row.error:.8f} | {row.n_rows} |')
    table = '\n'.join(table_lines)
    mismatches = {k:v for k,v in unequal.items() if v}
    # Contraejemplo de lógica que las pruebas originales omitieron. Sólo objetos
    # Python: un proxy nulo NO None y módulos con lista de canales vacía.
    # La API falsa no abre el pathname; éste sólo satisface os.path.exists.
    with contextlib.redirect_stdout(io.StringIO()):
        from test_flag_minimo_sin_root import minimal_reader
        from test_dos_rutas_sin_root import fake_api, original_function, Event, Counter as FakeCounter, Module
        class NullPointer:
            def __bool__(self): return False
        def empty_channels_event():
            event = Event()
            event.md.counters = [FakeCounter(4001, [Module(i, []) for i in [1,2,3]])]
            event.md.sim = {104001: NullPointer()}
            return event
        api = fake_api(empty_channels_event)
        before = original_function(api)(str(HERE/'outputs.txt'))
        after = minimal_reader(api)(str(HERE/'outputs.txt'))
    assert len(before) == 3 and len(after) == 0
    assert before.nMuones_MC.eq(0).all() and before.sd_nMuons_MC.eq(1).all()
    text = f'''# Auditoría de filas: parquet original vs lector con flag

Diagnóstico serial sobre parquet existentes y el CSV SD ya guardado. No se abrió
ROOT, no se modificó Offline y no se reprocesó la producción. El script que
reproduce este informe es `auditar_perdida_filas.py`, en esta misma carpeta.

## 1. Resultado observado: sí se perdieron filas

Se cotejaron {len(file_rows)} archivos de cada versión, con los mismos nombres.
La clave es archivo/event_id/counterId/moduleId/sdId; no se compara sólo la intersección.

| Cantidad | Filas por módulo |
|---|---:|
| Parquet anterior | {totals['old']} |
| Nuevo, flag True | {totals['new_true']} |
| Nuevo, flag False | {totals['new_false']} |
| Nuevo total | {totals['new']} |
| Filas anteriores que desaparecieron | {totals['old_only']} |
| Filas genuinamente añadidas | {totals['new_only']} |

Balance: {totals['old']} − {totals['old_only']} + {totals['new_only']} = {totals['new']}.
Eventos representados sólo en el viejo/nuevo: {totals['old_only_events']}/{totals['new_only_events']}.
Valores distintos en las columnas antiguas entre filas comunes: {mismatches or 'ninguno'}.

Las {totals['old_only']} filas perdidas tienen {totals['lost_umd_mc_zero']} ceros
en nMuones_MC, {totals['lost_umd_rec_zero']} ceros y {totals['lost_umd_rec_nan']} NaN
en nMuones_REC. Sus estados son {dict(lost_status)}.
Conservaban SD-MC conocido en {totals['lost_sd_mc_known']} filas, positivo en
{totals['lost_sd_mc_positive']}. Por tanto, perderlas también elimina información SD
válida: no son simplemente filas vacías prescindibles.

## 2. Cambio de código que hay que investigar/corregir

Antes: `if simCounter is None: continue`.
Después: `if simCounter is None or not simCounter: continue`.

Esta segunda condición NO es necesariamente neutra para el número de filas.
MDEvent::GetSimCounter devuelve nullptr si falta la entrada simulada.
El writer guarda counters reconstruidos y simulados con requisitos diferentes.
Un proxy nullptr puede no ser None. Si un módulo no tiene canales enumerados,
el lector antiguo puede guardar su suma inicial cero sin desreferenciarlo; el
nuevo filtro descarta el counter entero, incluido su conteo SD disponible.

Esto es una explicación concreta del fallo, no una demostración fila por fila
del puntero real: los parquet no guardan HasSimCounter ni el número de canales.
La comprobación directa requiere una lectura dirigida del ADST. Los ceros UMD
antiguos tampoco deben reinterpretarse automáticamente como verdad física completa.

Contraejemplo reproducido con las dos funciones reales y objetos artificiales:
un counter con proxy nulo (no None), tres módulos sin canales, y SD simulado
disponible. El lector original guarda {len(before)} filas, el nuevo guarda
{len(after)}. En las originales nMuones_MC queda en cero inicial y el conteo
SD-MC vale uno. Esto demuestra que el cambio de condición puede eliminar filas
SD válidas, sin invocar un fallo de Offline. No reemplaza la inspección del
puntero real en los eventos perdidos. Las pruebas originales omitieron justamente
la combinación proxy nulo + canales vacíos; que pasaran no certificaba equivalencia.

## 3. El lector mínimo no cubre la muestra SD de la sección 5

En la misma región Infill, 30≤theta<40 grados y 150≤r<1800 m:

- Inventario SD simulado anterior: {len(raw)} estaciones/evento.
- De ellas con HasStation=True: {int(raw.has_rec.eq(1).sum())}; sin él: {int(raw.has_rec.eq(0).sum())}.
- Parquet viejo, SD sin duplicados: {len(old_sd)}; coincide con la selección del inventario.
- Parquet nuevo, SD sin duplicados: {len(new_sd)}.
- Filas nuevas por módulo con flag False en esta región: {int((~new_window.has_sd_rec).sum())}.
- Estaciones/evento con HasStation=False recuperadas del inventario: {int(recovered.sum())}.
- Filas viejas por módulo perdidas en esta región: {len(lost_window)}.

La coincidencia de conteos SD del inventario con el parquet viejo se volvió a
comprobar: exacta. Máxima diferencia radial: {max_radius_delta:.3g} m; azimutal:
{max_phi_delta:.3g} grados. Esto respalda el control anterior de la muestra seleccionada,
no valida automáticamente todas las variables de ROOT ni su población ausente.

El bucle original parte de `MDEvent.CountersBegin()` y de módulos UMD guardados.
La sección 5 parte de `SDEvent.GetSimStationVector()`, sin exigir esos módulos.
Cambiar HasStation no elimina los requisitos UMD. Corregir la pérdida de filas
es necesario pero, por sí solo, no garantiza recuperar todo el inventario SD.

## 4. Comparación numérica con el MISMO ajuste de la sección 5

Se ejecutan sus funciones de ajuste sin importar el notebook: doce bins de phi,
medias/SEM, normalización y curve_fit idénticos. A1>0 = temprano; A1<0 = tardío.
La unidad es estación/evento, NO módulo. Son errores formales, no bootstrap.

{table}

El CSV auditoria_filas_ajustes.csv contiene todos los bins y ambos conteos SD.
No se modifica ni sustituye la figura anterior. El nuevo parquet no se certifica
como dataset equivalente al anterior filtrado hasta resolver las filas perdidas.

## 5. Warnings y errores: qué muestra el código, no qué se puede suponer

- El extractor diagnóstico antiguo adst_counts_fast.py sí fija
  `ROOT.gErrorIgnoreLevel=ROOT.kError`: oculta warnings de niveles inferiores.
- El lector mínimo NO fija ese nivel. El nivel efectivo del kernel del usuario
  no está registrado y puede heredarse de celdas previas: no se puede certificar
  desde un log copiado que todas las advertencias se mostraron.
- Conserva excepciones geométricas amplias que pueden terminar en un skip sin
  mensaje, y un AttributeError de getters MC deja valores ausentes.
- El wrapper captura errores de archivo y devuelve un texto; los textos se
  imprimen después de pool.map. Éxito significa que escribió parquet, no igualdad
  con el anterior ni integridad certificada de todos los objetos ROOT.
- La lectura termina cuando ReadNextEvent deja de devolver eSuccess; la versión
  mínima no distingue EOF de fallo ni comprueba GetNEvents.

Sumas reproducidas del log paralelo: {log_totals}.
No hay evidencia aquí que permita atribuir el problema a un bug de Offline.
Sí hay una selección adicional introducida por nuestro lector y una comparación
de universos que no puede presentarse como si fuera el mismo experimento.

## Fuentes de código inspeccionadas (instalación local, sólo lectura)

- ADST/RecEvent/src/MDEventADST.cc, GetSimCounter: retorna nullptr si no encuentra ID.
- Modules/General/RecDataWriterNG/MD2ADST.cc, Convert: AddCounter para counters
  existentes; AddSimCounter sólo cuando HasSimData.
- El mismo archivo, MakeCounter: retorna antes de llenar módulos si falta RecData.

No se corrigió ni rerunó el lector durante esta auditoría. Primero se documenta
el fallo observado; una corrección debe conservar las filas SD aun sin verdad
UMD y distinguir ausencia de información de cero físico.
'''
    (HERE/'AUDITORIA_FILAS.md').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
