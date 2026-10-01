"""Controles de la entrega y de identidades analíticas; no ejecuta simulaciones.

Desde la raíz del repositorio:
venv/bin/python claude_work/capitulo3_revision_autor_2026_09_29/verificar_entrega.py
"""
from pathlib import Path
import hashlib
import json
import math
import re

import pdfplumber
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    report = {'alcance': 'Control documental y algebraico; no es una validación de simulaciones.'}
    manifest = json.loads((HERE / 'manifest_fuentes.json').read_text())
    for item in manifest:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    report['fuentes_sin_modificar'] = len(manifest)
    tex = (HERE / '03_fenomenologia_DRAFT.tex').read_text()
    labels = re.findall(r'\\label\{([^}]+)\}', tex)
    assert len(labels) == len(set(labels))
    references = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', tex))
    assert references <= set(labels), references - set(labels)
    bib = (HERE / 'bibliografia.bib').read_text() + (HERE / 'bibliografia_adicional.bib').read_text()
    keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib))
    citations = set()
    for group in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}', tex):
        citations.update(group.split(','))
    assert citations <= keys, citations - keys
    for figure in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', tex):
        assert (HERE / figure).is_file(), figure
    log = (HERE / 'compilacion/vista_previa.log').read_text(errors='replace')
    problems = [line for line in log.splitlines() if re.search(r'undefined|multiply defined|LaTeX Error|Overfull', line)]
    assert not problems, problems
    aux = (HERE / 'compilacion/vista_previa.aux').read_text()
    assert r'\newlabel{eq:asym_kinematic_ratio}{{3.4}' in aux
    report['ecuacion_conservada'] = '3.4'
    report['citas_resueltas'] = len(citations)
    report['referencias_internas_resueltas'] = len(references)
    report['avisos_criticos_compilacion'] = problems
    report['paginas'] = {}
    for name in ('capitulo_3.pdf', 'RESPUESTAS_Y_CRITERIOS.pdf'):
        with pdfplumber.open(HERE / name) as document:
            assert all(page.extract_text() for page in document.pages)
            report['paginas'][name] = len(document.pages)

    # Integración independiente del cambio de variables p_t -> ángulo sólido.
    def f(alpha, k):
        z = 1 - (1 + k) * math.exp(-k)
        return k * k * math.cos(alpha) * math.exp(-k * math.sin(alpha)) / (2 * math.pi * z)

    normalization = {}
    for k in (0.2, 1, 5, 40):
        integral = quad(lambda a: 2 * math.pi * math.sin(a) * f(a, k), 0, math.pi / 2,
                        epsabs=1e-11, epsrel=1e-11)[0]
        assert abs(integral - 1) < 1e-9
        normalization[str(k)] = integral
    report['normalizacion_distribucion_angular'] = normalization

    # Comprobar la Ec. 3.4 contra cocientes de densidades normalizadas.
    # Los valores son parámetros ilustrativos para comprobar la identidad.
    d_axis, radius, theta = 7500.0, 1200.0, math.radians(35)
    delta = radius * math.tan(theta)
    early, late = math.hypot(d_axis - delta, radius), math.hypot(d_axis + delta, radius)
    ae, al = math.asin(radius / early), math.asin(radius / late)
    ratios = {}
    for k in (1, 50):
        direct = (f(al, k) / late**2) / (f(ae, k) / early**2)
        factored = (early / late)**2 * math.cos(al) / math.cos(ae) * math.exp(k * (math.sin(ae) - math.sin(al)))
        assert math.isclose(direct, factored, rel_tol=1e-12)
        ratios[str(k)] = direct
    assert ratios['1'] < 1 < ratios['50']
    report['cociente_a_parametros_ilustrativos'] = ratios

    # Coeficiente de Fourier del producto completo frente a la expansión de
    # Armbruster: el error decrece al reducir r/D. No se ajustan datos.
    gamma_adf, attenuation_length = 1.4, 30000.0
    expansion = []
    for r in (100.0, 50.0, 25.0):
        def signal(phi):
            d = math.hypot(d_axis - r * math.tan(theta) * math.cos(phi), r)
            alpha = math.asin(r / d)
            return (d_axis / d)**2 * (alpha / (r / d_axis))**(-gamma_adf) * math.exp(-(d - d_axis) / attenuation_length)
        norm = quad(signal, 0, 2 * math.pi, epsabs=1e-11)[0]
        exact = 2 * quad(lambda phi: signal(phi) * math.cos(phi), 0, 2 * math.pi, epsabs=1e-11)[0] / norm
        first = (2 - gamma_adf + d_axis / attenuation_length) * r / d_axis * math.tan(theta)
        expansion.append({'r_m': r, 'fourier_producto': exact, 'primer_orden': first,
                          'error_absoluto': abs(exact - first)})
    assert expansion[2]['error_absoluto'] < expansion[1]['error_absoluto'] < expansion[0]['error_absoluto']
    assert expansion[2]['error_absoluto'] / abs(expansion[2]['primer_orden']) < 1e-4
    report['limite_armbruster'] = expansion
    report['ejemplos_aritmeticos_no_son_datos'] = {
        'cociente_de_sumas': 84 / 101,
        'promedio_sin_pesos_correctos': (0.8 + 4) / 2,
        'media_tardia_seleccionada': 1.5 * (5 / 6) / (1 / 4),
    }
    (HERE / 'VALIDACION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
