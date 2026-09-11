"""Check the executed notebook and write a short HUMAN-READABLE validation note.

This does not execute ROOT, launch a kernel, or recompute a simulation.
It verifies execution, source pairing, embedded figures and numerical agreement.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat
import jupytext

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parents[1] / '04_soporte/tablas'
SOURCE = HERE / 'seleccion_sd_paso_a_paso.py'
NOTEBOOK = HERE / 'seleccion_sd_paso_a_paso.ipynb'
EXPORT = HERE / 'exports'

source = jupytext.read(SOURCE)
executed = nbformat.read(NOTEBOOK, as_version=4)
nbformat.validate(executed)
assert len(source.cells) == len(executed.cells)
for original, final in zip(source.cells, executed.cells):
    assert original.cell_type == final.cell_type
    assert original.source.strip() == final.source.strip(), 'Python/notebook source mismatch'

code_cells = [c for c in executed.cells if c.cell_type == 'code']
markdown_cells = [c for c in executed.cells if c.cell_type == 'markdown']
assert all(c.execution_count is not None for c in code_cells)
errors = [o for c in code_cells for o in c.outputs if o.output_type == 'error']
assert not errors, errors
images = sum('image/png' in o.get('data', {}) for c in code_cells for o in c.outputs)
assert images == 7
assert len(list(EXPORT.glob('*.png'))) == 7
assert len(list(EXPORT.glob('*.pdf'))) == 7

# Independent comparison to previous saved outputs, AFTER notebook recalculation.
old_fits = pd.read_csv(AUDIT / 'selection_closure_fits.csv')
new_fits = pd.read_csv(EXPORT / 'A1_recalculado_con_bootstrap.csv')
old_ci = pd.read_csv(AUDIT / 'selection_paired_bootstrap.csv')
for row in new_fits.itertuples():
    if row.quantity != 'difference':
        sample = 'all_sim' if row.quantity == 'all' else 'SDrec'
        reference = old_fits.loc[
            old_fits['lo'].eq(row.r_min) & old_fits['hi'].eq(row.r_max)
            & old_fits['sample'].eq(sample) & old_fits['variable'].eq('mu'), 'A'
        ].item()
        assert np.isclose(row.A1, reference, atol=1e-8, rtol=0)
    reference_ci = old_ci.loc[
        old_ci['lo'].eq(row.r_min) & old_ci['hi'].eq(row.r_max)
        & old_ci['quantity'].eq(row.quantity)
    ].iloc[0]
    for new_value, old_value in [
        (row.std_bootstrap, reference_ci['sd']),
        (row.low95, reference_ci['low']),
        (row.high95, reference_ci['high']),
    ]:
        assert np.isclose(new_value, old_value, atol=1e-10, rtol=0)

key = ['source', 'event_id', 'sdId']
fresh = pd.read_csv(HERE / 'raw_smoke_test/stations.csv')
cache = pd.read_csv(AUDIT / 'adst_counts_fast.csv')
match = fresh.merge(cache, on=key, how='left', validate='one_to_one',
                    indicator=True, suffixes=('_fresh', '_cache'))
assert match['_merge'].eq('both').all()
for field in ['mu', 'em', 'has_rec']:
    assert np.array_equal(match[field + '_fresh'], match[field + '_cache'])
assert np.max(np.abs(match['r_fresh'] - match['r_cache'])) < 1e-6
assert np.max(np.abs(np.angle(np.exp(1j * (match['phi_fresh'] - match['phi_cache']))))) < 1e-8
assert fresh['has_rec'].eq(0).any()

card = pd.read_csv(EXPORT / 'ficha_de_ejecucion.csv').set_index('campo')['valor']
assert str(card['Relectura opcional de ROOT activada en este Run All']) == 'False'
text = f'''# Verificación de la entrega

- Notebook ejecutado de principio a fin: **{len(code_cells)} celdas de código**, sin errores.
- **{len(markdown_cells)} celdas explicativas** intercaladas; fuente .py y .ipynb coinciden.
- **{images} figuras** visibles dentro del notebook, además de sus PNG y PDF en exports/.
- Coeficientes de las cuatro bandas e intervalos bootstrap recalculados desde filas:
  coinciden con el control anterior de veinte archivos.
- No se cargaron coeficientes desde JSON para construir los gráficos del notebook.
- Tiempo registrado del recorrido principal: {card['Segundos del recorrido del notebook']} segundos;
  no es una garantía de tiempo en otras máquinas o cargas del servidor.
- Run All con relectura ROOT desactivada; utiliza pandas y un hilo numérico.
- Prueba ROOT separada: {len(fresh)} filas recuperadas de nuevo, incluyendo
  **{int(fresh['has_rec'].eq(0).sum())} sin entrada SD reconstruida**. Sus conteos,
  condición de presencia y coordenadas coinciden con la caché.
- El piloto ROOT es parcial. Las advertencias reales de esquema del diccionario
  están explicadas en el notebook y README; no se certifica todo el contenido ADST.

La coincidencia valida esta reproducción y la disponibilidad de esos registros;
no demuestra por sí sola un fallo del algoritmo de reconstrucción ni aísla la
causa electromagnética del efecto de selección.
'''
(HERE / 'VALIDACION.md').write_text(text, encoding='utf-8')
print(text)
