"""Coincidencia de patrones estilo gitignore, usada para CODEOWNERS y .gitignore.

Semántica soportada (subconjunto documentado de gitignore/CODEOWNERS de GitHub):
- Un patrón con '/' inicial o intermedio se ancla a la raíz; sin '/' coincide en cualquier nivel.
- Barra final: solo directorios (y por tanto su contenido).
- '*' no cruza '/'; '**' sí; '?' es un carácter que no es '/'.
- Un patrón que coincide con un directorio coincide con todo su contenido, salvo en CODEOWNERS
  cuando el último segmento lleva '*' (p. ej. `docs/*` no cubre `docs/sub/x`, según la documentación de GitHub).
No soportado (GitHub tampoco lo admite en CODEOWNERS): negación '!', clases '[ ]'.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


def compile_pattern(pattern: str, codeowners: bool = False) -> re.Pattern[str]:
    pat = pattern.strip()
    dir_only = pat.endswith("/")
    body = pat.rstrip("/")
    anchored = body.startswith("/") or "/" in body
    body = body.lstrip("/")
    rx = []
    i = 0
    while i < len(body):
        if body.startswith("**/", i):
            rx.append("(?:.*/)?")
            i += 3
        elif body.startswith("/**", i) and i + 3 == len(body):
            rx.append("/.*")
            i += 3
        elif body.startswith("**", i):
            rx.append(".*")
            i += 2
        elif body[i] == "*":
            rx.append("[^/]*")
            i += 1
        elif body[i] == "?":
            rx.append("[^/]")
            i += 1
        else:
            rx.append(re.escape(body[i]))
            i += 1
    prefix = "" if anchored else "(?:.*/)?"
    last = body.rsplit("/", 1)[-1]
    if dir_only:
        suffix = "/.+"
    elif codeowners and "*" in last and "**" not in last:
        # GitHub: `docs/*` cubre los archivos de docs/ pero no los anidados (difiere de gitignore).
        suffix = ""
    else:
        suffix = "(?:/.*)?"
    return re.compile("^" + prefix + "".join(rx) + suffix + "$")


@dataclass
class OwnerRule:
    pattern: str
    owners: list[str]
    line: int
    regex: re.Pattern[str]


def parse_codeowners(text: str) -> list[OwnerRule]:
    rules = []
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.split(" #", 1)[0].strip() if not raw.lstrip().startswith("#") else ""
        if not line:
            continue
        parts = line.split()
        rules.append(OwnerRule(parts[0], parts[1:], n, compile_pattern(parts[0], codeowners=True)))
    return rules


def owners_for(rules: list[OwnerRule], path: str) -> OwnerRule | None:
    """Devuelve la regla efectiva (gana el último patrón que coincide)."""
    match = None
    for r in rules:
        if r.regex.match(path):
            match = r
    return match


def gitignore_matches(text: str, path: str) -> bool:
    """True si algún patrón no negado de .gitignore coincide y ninguno posterior lo niega."""
    ignored = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        neg = line.startswith("!")
        if neg:
            line = line[1:]
        if compile_pattern(line).match(path):
            ignored = not neg
    return ignored


SKIP_DIRS = {".git", ".harness-standard", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__", ".tox"}


def walk_files(root: Path, names: set[str]) -> list[Path]:
    """Busca archivos con nombre en `names`, ignorando directorios de dependencias y worktrees."""
    out = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts[:2] == (".claude", "worktrees"):
            continue
        if p.is_file() and p.name in names:
            out.append(p)
    return sorted(out)
