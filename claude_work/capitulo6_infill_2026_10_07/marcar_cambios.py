r"""
Build a copy of the Chapter 6 draft with Claude's new or modified text in blue.

Input:  Tesis - Latex/DRAFTS/06_infill.tex   (the draft, unchanged)
Output: Tesis - Latex/DRAFTS/06_infill_marcado.tex

Each entry of CHANGES is a (start, end) pair of literal strings: the text from `start` up to and
including the first `end` after it is wrapped in {\color{blue} ...}. Deleted text is not shown in
the PDF; it is kept in the draft as `% ORIGINAL:` comments. Changed figure captions are listed in
CAPTIONS_CHANGED and marked with a blue "[caption modificado]" tag instead of colouring them.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DRAFT = REPO_ROOT / "Tesis - Latex" / "DRAFTS" / "06_infill.tex"
MARKED = REPO_ROOT / "Tesis - Latex" / "DRAFTS" / "06_infill_marcado.tex"

CHANGES = [
    ("de la degradación geométrica asociada", "modulan la asimetría."),
    ("el fuerte gradiente de la Función de Distribución Lateral (LDF) dentro de cada bin", "fluctuaciones severas en la densidad."),
    ("Que este estadístico resulte compatible", "un $10\\%$ mayores."),
    ("El comportamiento observado es consistente", "viabilidad estadística del arreglo:"),
    ("La modulación azimutal es pequeña y compatible con cero", "$\\tan\\theta \\lesssim 0.2$."),
    ("Sin embargo, a distancias del orden de $\\sim 1100$~m la asimetría presenta", "siguiente bin radial."),
    ("En consecuencia, crece la diferencia de atmósfera", "regiones temprana y tardía."),
    ("En estas condiciones, la gran diferencia", "($1350 - 1500$~m)."),
    ("Estos resultados muestran que", "\\ref{anexo:ajustes_infill_mc}."),
    ("igual que sucedía en la Sección~", "(Sección~\\ref{subsec:bias_direccional})."),
    ("de modo que las diferencias observadas se deban", "(Sección~\\ref{subsec:seleccion_estaciones})."),
    ("Además, ambas asimetrías calculadas", "\\ref{sec:cap_anillo_denso}."),
    ("Esta inversión aparece aun con la geometría Monte Carlo", "en sus componentes."),
    ("se observa una competencia radial", "se observa una competencia radial"),
    ("Otra posibilidad es la selección de estaciones", "reducir la asimetría medida."),
    ("Es aquí donde se encuentra la diferencia principal con el UMD", "diferencia principal con el UMD"),
    ("Este comportamiento arrastra a la señal total del SD", "observada aquí."),
    ("El Capítulo~\\ref{sec:fenomenologia} mostró que esta inversión", "lo que se analiza en la Sección~\\ref{subsec:seleccion_estaciones}."),
    ("\\subsection{Selección de estaciones y la inversión del SD}", "requiere que esa selección sea la misma."),
    ("Con la geometría reconstruida la asimetría resulta positiva pero pequeña", "(Sección~\\ref{subsec:lavado_nucleo})."),
    ("(ver Sección~\\ref{subsec:lavado_nucleo})", "(ver Sección~\\ref{subsec:lavado_nucleo})"),
    ("\\subsection{Origen de la degradación: el corrimiento del núcleo}", "borra la modulación en el \\textit{Infill}."),
    ("A pesar de que el corrimiento del núcleo", "A pesar de que el corrimiento del núcleo"),
    ("Esta resiliencia no implica", "frente a un corrimiento sistemático."),
    ("\\subsection{La inversión del SD con la geometría reconstruida}", "\\label{subsec:inversion_sd_rec}"),
    ("Como la selección de estaciones no depende de la geometría asignada", "se seleccionan de la misma manera."),
    ("La diferencia entre $A_1^{\\mathrm{REC}}$ y $A_1^{\\mathrm{MC}}$", "la propia respuesta del detector."),
    ("\\section{Dependencia con el primario y la energía}", "variaciones de ese orden."),
]

CAPTIONS_CHANGED = [
    "\\caption{Comparación de la evolución radial de la amplitud de asimetría $A_1$ entre el número",
    "\\caption{Desglose de la asimetría azimutal para las componentes inyectadas a nivel del suelo frente al número",
]


def wrap_span(text, start, end):
    begin = text.find(start)
    if begin < 0 or text.count(start) != 1:
        raise ValueError("start must appear exactly once: " + start[:60])
    finish = text.find(end, begin)
    if finish < 0:
        raise ValueError("end not found after start: " + end[:60])
    finish = finish + len(end)
    span = text[begin:finish]
    if "\n\n" not in span:
        return text[:begin] + "{\\color{blue}" + span + "}" + text[finish:]

    # Multi-paragraph span: one colour group per paragraph, because a group that contains an [H]
    # float loses its colour after the float. Floats, headings and comment-only blocks are left as
    # they are (new headings and figures are listed in the README instead).
    blocks = span.split("\n\n")
    marked_blocks = []
    for block in blocks:
        stripped = block.strip()
        lines_without_comments = [line for line in stripped.split("\n") if not line.strip().startswith("%")]
        first_line = ""
        if lines_without_comments:
            first_line = lines_without_comments[0].strip()
        is_structure = first_line.startswith(("\\begin{figure", "\\begin{table", "\\subsection", "\\section", "\\label"))
        if stripped == "" or not lines_without_comments or is_structure:
            marked_blocks.append(block)
        else:
            # Open the group on the first text line (after any comment lines) and start the
            # paragraph before the colour change, so the colour is set in horizontal mode.
            lines = block.split("\n")
            for index, line in enumerate(lines):
                if line.strip() and not line.strip().startswith("%"):
                    lines[index] = "{\\leavevmode\\color{blue}" + line
                    break
            marked_blocks.append("\n".join(lines) + "}")
    return text[:begin] + "\n\n".join(marked_blocks) + text[finish:]


def main():
    text = DRAFT.read_text()
    for start, end in CHANGES:
        text = wrap_span(text, start, end)
    for caption_start in CAPTIONS_CHANGED:
        if text.count(caption_start) != 1:
            raise ValueError("caption not found: " + caption_start[:60])
        tagged = caption_start.replace("\\caption{", "\\caption{\\textcolor{blue}{[caption modificado]} ")
        text = text.replace(caption_start, tagged)
    header = ("% COPIA MARCADA, generada por claude_work/capitulo6_infill_2026_10_07/marcar_cambios.py.\n"
              "% En azul: texto nuevo o modificado por Claude. No editar este archivo; editar 06_infill.tex.\n")
    MARKED.write_text(header + text)
    print("Wrote", MARKED.relative_to(REPO_ROOT), "with", len(CHANGES), "marked spans")


if __name__ == "__main__":
    main()
