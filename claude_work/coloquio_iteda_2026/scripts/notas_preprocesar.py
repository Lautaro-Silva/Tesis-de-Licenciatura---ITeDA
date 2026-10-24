"""Prepare notas_expositor.md for pandoc's PDF output.

Pandoc only starts a list after a blank line. The notes often put a list right
after a bold label line ("**Oral:** ...\n- item"), which GitHub renders fine
but pandoc merges into one paragraph. This inserts the missing blank lines and
writes the result to build/notas_para_pdf.md.
"""
import re
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

list_item = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")
lines = source.read_text().splitlines()
output_lines = []
for line in lines:
    previous = output_lines[-1] if output_lines else ""
    starts_list = list_item.match(line) is not None
    previous_is_list_or_blank = previous.strip() == "" or list_item.match(previous) is not None
    previous_is_indented_continuation = previous.startswith("   ")
    if starts_list and not previous_is_list_or_blank and not previous_is_indented_continuation:
        output_lines.append("")
    output_lines.append(line)

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(output_lines) + "\n")
