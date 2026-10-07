"""
Build a book-class preview of the whole thesis with the revised Chapter 6.

Nothing outside this folder's `compilacion/` subfolder is written. The user's main.tex and
chapter files are only read: the preview works on copies.

What the preview uses:
- Chapters 3 and 5: the author's final versions in `Tesis - Latex/DRAFTS/` (already book style).
- Chapter 6: the new draft `Tesis - Latex/DRAFTS/06_infill.tex`.
- Chapters 1, 2, 4, 7, 8 and the annex: `capitulos/`, still written for the article class; in
  the copy, every sectioning level is promoted by one (\\section -> \\chapter, and so on).

Files that are not tracked in git (DRAFTS/03 and 05, the author's working copy of Chapter 7
and its figures) are taken from the main checkout when this runs inside a worktree.

Usage (from the repository root):
    python claude_work/capitulo6_infill_2026_10_07/construir_vista_previa.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
MAIN_CHECKOUT = Path("/home/lsilva/Github/Tesis-de-Licenciatura---ITeDA")
BUILD_DIR = HERE / "compilacion"
THESIS_COPY = BUILD_DIR / "tesis"

# Chapters still written for the article class: their levels are promoted in the copy.
ARTICLE_STYLE_CHAPTERS = ["01_introduccion.tex", "02_observatorio.tex", "04_metodologia.tex",
                          "07_datos_reales.tex", "08_conclusiones.tex", "09_anexos.tex"]

# Untracked or locally modified files that live only in the main checkout.
FILES_FROM_MAIN_CHECKOUT = [
    "Tesis - Latex/DRAFTS/03_fenomenologia.tex",
    "Tesis - Latex/DRAFTS/05_anillo_denso.tex",
    "Tesis - Latex/capitulos/07_datos_reales.tex",
]
FOLDERS_FROM_MAIN_CHECKOUT = ["Tesis - Latex/capitulos/imagenes_capitulos/cap7"]


# Build-only fixes for problems outside Chapter 6, applied to the copies and reported to the
# author (the original files are not changed): file -> list of (old text, new text).
BUILD_ONLY_FIXES = {
    "DRAFTS/03_fenomenologia.tex": [
        # Only esquema_lluvia.png exists in imagenes_capitulos/cap3/.
        ("cap3/esquema_lluvia.jpeg", "cap3/esquema_lluvia.png"),
    ],
}


def apply_build_only_fixes():
    for relative, fixes in BUILD_ONLY_FIXES.items():
        path = THESIS_COPY / relative
        text = path.read_text()
        for old, new in fixes:
            if old in text:
                text = text.replace(old, new)
                print("Build-only fix in {}: {} -> {}".format(relative, old, new))
        path.write_text(text)


def copy_sources():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    ignore = shutil.ignore_patterns("main.pdf", "*-SAVE-ERROR", "*.aux", "*.log", "*.bbl", "*.bcf")
    shutil.copytree(REPO_ROOT / "Tesis - Latex", THESIS_COPY, ignore=ignore)
    if MAIN_CHECKOUT.resolve() != REPO_ROOT.resolve():
        for relative in FILES_FROM_MAIN_CHECKOUT:
            target = THESIS_COPY / Path(relative).relative_to("Tesis - Latex")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(MAIN_CHECKOUT / relative, target)
        for relative in FOLDERS_FROM_MAIN_CHECKOUT:
            target = THESIS_COPY / Path(relative).relative_to("Tesis - Latex")
            shutil.copytree(MAIN_CHECKOUT / relative, target, dirs_exist_ok=True)


def promote_levels(text):
    """\\section -> \\chapter, \\subsection -> \\section, \\subsubsection -> \\subsection."""
    text = re.sub(r"\\subsubsection(?=[*\[{])", "@@LEVEL3@@", text)
    text = re.sub(r"\\subsection(?=[*\[{])", "@@LEVEL2@@", text)
    text = re.sub(r"\\section(?=[*\[{])", r"\\chapter", text)
    text = text.replace("@@LEVEL2@@", "\\section")
    text = text.replace("@@LEVEL3@@", "\\subsection")
    return text


def add_page_marker(path, after_label, marker):
    """Insert a zref label right after a chapter label, to find the chapter's physical pages."""
    text = path.read_text()
    anchor = "\\label{" + after_label + "}"
    if anchor not in text:
        raise ValueError("Label {} not found in {}".format(after_label, path))
    text = text.replace(anchor, anchor + "\n\\zlabel{" + marker + "}", 1)
    path.write_text(text)


def write_preview_main(chapter6_name):
    text = (THESIS_COPY / "main.tex").read_text()
    text = text.replace("\\documentclass[spanish,a4paper,12pt]{article}",
                        "\\documentclass[spanish,a4paper,12pt,openany]{book}")
    for counter in ["figure", "table", "equation"]:
        text = text.replace("\\counterwithin{" + counter + "}{section}",
                            "\\counterwithin{" + counter + "}{chapter}")
    text = text.replace("\\renewcommand{\\sectionmark}[1]{\\markboth{\\thesection.\\ #1}{}}",
                        "\\renewcommand{\\chaptermark}[1]{\\markboth{\\thechapter.\\ #1}{}}")
    text = text.replace("\\usepackage[pdfencoding=auto, psdextra]{hyperref}",
                        "\\usepackage{zref-abspage,zref-user}\n\\usepackage[pdfencoding=auto, psdextra]{hyperref}")
    text = text.replace("\\input{capitulos/03_fenomenologia.tex}", "\\input{DRAFTS/03_fenomenologia.tex}")
    text = text.replace("\\input{capitulos/05_anillo_denso.tex}", "\\input{DRAFTS/05_anillo_denso.tex}")
    text = text.replace("\\input{capitulos/06_infill.tex}", "\\input{DRAFTS/" + chapter6_name + ".tex}")
    for name in ["03_fenomenologia", "05_anillo_denso", chapter6_name]:
        if "\\input{DRAFTS/" + name + ".tex}" not in text:
            raise ValueError("Could not redirect chapter " + name)
    (THESIS_COPY / "main_vista_previa.tex").write_text(text)


def run(command):
    print("$", " ".join(command))
    result = subprocess.run(command, cwd=THESIS_COPY, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        print(result.stdout[-4000:])
        print(result.stderr[-2000:])
        raise SystemExit("Command failed: " + " ".join(command))


def compile_preview():
    pdflatex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main_vista_previa.tex"]
    run(pdflatex)
    run(["biber", "main_vista_previa"])
    run(pdflatex)
    run(pdflatex)


def report_problems():
    log = (THESIS_COPY / "main_vista_previa.log").read_text(errors="replace")
    undefined_references = sorted(set(re.findall(r"Reference `([^']+)' on page", log)))
    undefined_citations = sorted(set(re.findall(r"Citation `([^']+)'", log)))
    biber_log = (THESIS_COPY / "main_vista_previa.blg").read_text(errors="replace")
    missing_entries = sorted(set(re.findall(r"I didn't find a database entry for '([^']+)'", biber_log)))
    print("Undefined references:", undefined_references or "none")
    print("Undefined citations:", undefined_citations or "none")
    print("Missing bibliography entries:", missing_entries or "none")
    return undefined_references, undefined_citations + missing_entries


def chapter_page_range():
    aux = (THESIS_COPY / "main_vista_previa.aux").read_text(errors="replace")
    pages = {}
    for marker in ["vp:inicio_cap6", "vp:inicio_cap7"]:
        match = re.search(r"\\zref@newlabel\{" + re.escape(marker) + r"\}\{.*?\\abspage\{(\d+)\}", aux)
        pages[marker] = int(match.group(1))
    return pages["vp:inicio_cap6"], pages["vp:inicio_cap7"] - 1


def extract_chapter(first_page, last_page, output_pdf):
    pattern = str(BUILD_DIR / "pagina_%d.pdf")
    subprocess.run(["pdfseparate", "-f", str(first_page), "-l", str(last_page),
                    str(THESIS_COPY / "main_vista_previa.pdf"), pattern], check=True)
    pages = [str(BUILD_DIR / "pagina_{}.pdf".format(n)) for n in range(first_page, last_page + 1)]
    subprocess.run(["pdfunite"] + pages + [str(output_pdf)], check=True)
    for page in pages:
        Path(page).unlink()


def main():
    # --marcado: compile DRAFTS/06_infill_marcado.tex (made by marcar_cambios.py), where Claude's
    # changes are in blue, and write 06_infill_MARCADO.pdf instead of the clean chapter PDF.
    marked = "--marcado" in sys.argv
    chapter6_name = "06_infill"
    chapter6_pdf = "06_infill_BORRADOR.pdf"
    if marked:
        chapter6_name = "06_infill_marcado"
        chapter6_pdf = "06_infill_MARCADO.pdf"

    copy_sources()
    apply_build_only_fixes()
    for name in ARTICLE_STYLE_CHAPTERS:
        path = THESIS_COPY / "capitulos" / name
        path.write_text(promote_levels(path.read_text()))
    add_page_marker(THESIS_COPY / "DRAFTS" / (chapter6_name + ".tex"), "cap:infill", "vp:inicio_cap6")
    add_page_marker(THESIS_COPY / "capitulos" / "07_datos_reales.tex", "sec:datos_reales", "vp:inicio_cap7")
    write_preview_main(chapter6_name)
    compile_preview()
    undefined_references, undefined_citations = report_problems()

    first_page, last_page = chapter_page_range()
    print("Chapter 6: physical pages {}-{}".format(first_page, last_page))
    if not marked:
        shutil.copy2(THESIS_COPY / "main_vista_previa.pdf", HERE / "vista_previa_tesis.pdf")
    extract_chapter(first_page, last_page, HERE / chapter6_pdf)
    # Re-write the chapter PDF with Ghostscript: it shrinks it from ~17 MB to ~0.4 MB, and
    # poppler-based viewers (Evince, Okular) otherwise drop the blue colour of the marked version
    # on some pages with [H] floats.
    raw_pdf = HERE / "capitulo6_sin_normalizar.pdf"
    (HERE / chapter6_pdf).rename(raw_pdf)
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
                    "-o", str(HERE / chapter6_pdf), str(raw_pdf)], check=True)
    raw_pdf.unlink()

    chapter6_text = (REPO_ROOT / "Tesis - Latex" / "DRAFTS" / "06_infill.tex").read_text()
    chapter6_problems = []
    for label in undefined_references:
        if label in chapter6_text:
            chapter6_problems.append(label)
    print("Undefined references used in Chapter 6:", chapter6_problems or "none")
    if chapter6_problems or undefined_citations:
        sys.exit(1)


if __name__ == "__main__":
    main()
