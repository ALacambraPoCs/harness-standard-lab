"""Utilidades mínimas para analizar archivos de instrucciones Markdown."""
from __future__ import annotations

import re

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
# Import estilo Claude Code: '@ruta' al inicio de línea o tras espacio, con extensión de archivo.
IMPORT = re.compile(r"(?:^|(?<=\s))@((?:\.{0,2}/)?[\w./-]*[\w-]\.[A-Za-z0-9]+)(?=\s|$)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Líneas fuera de bloques de código, con el código en línea eliminado."""
    out, in_fence = [], False
    for n, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((n, INLINE_CODE.sub("", line)))
    return out


def imports(text: str) -> list[tuple[int, str]]:
    found = []
    for n, line in prose_lines(text):
        for m in IMPORT.finditer(line):
            found.append((n, m.group(1)))
    return found


def links(text: str) -> list[tuple[int, str]]:
    found = []
    for n, line in prose_lines(text):
        for m in LINK.finditer(line):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue  # URL absoluta, mailto: o ancla interna
            found.append((n, target.split("#", 1)[0]))
    return [(n, t) for n, t in found if t]


def headings(text: str) -> list[str]:
    return [m.group(1).strip().lower() for _, l in prose_lines(text) if (m := HEADING.match(l))]


def normalize(line: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"^[\s>*+\-\d.]+", "", line)).strip().lower()
