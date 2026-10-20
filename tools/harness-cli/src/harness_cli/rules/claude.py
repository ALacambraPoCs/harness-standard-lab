"""Reglas del adaptador claude-code (ADR-003, ADR-013)."""
from __future__ import annotations

from ..context import Context
from ..markdown import headings, imports, normalize, prose_lines
from ..matchers import gitignore_matches
from ..model import Finding
from . import rule

MIN_DUP_CHARS = 30


@rule("adapter.claude.imports-agents", ["HS-INS-006"])
def imports_agents(ctx: Context):
    """CLAUDE.md raíz existe e importa @AGENTS.md fuera de bloques de código."""
    path = ctx.standard.roles["adapter.claude.instructions"]["ruta"]
    text = ctx.read(path)
    if text is None:
        yield Finding("adapter.claude.imports-agents", "HS-INS-006", f"No existe {path} (adaptador claude-code declarado).",
                      "Crea CLAUDE.md con la línea `@AGENTS.md` (plantilla: template/adapters/claude-code/CLAUDE.md).", path)
        return
    if not any(t in ("AGENTS.md", "./AGENTS.md") for _, t in imports(text)):
        yield Finding("adapter.claude.imports-agents", "HS-INS-006", f"{path} no importa `@AGENTS.md`.",
                      "Añade una línea `@AGENTS.md` fuera de bloques de código. Sin ella, Claude Code no lee AGENTS.md si existe un CLAUDE.md.", path)


@rule("adapter.claude.no-duplication", ["HS-INS-007"])
def no_duplication(ctx: Context):
    """CLAUDE.md no repite encabezados ni líneas sustantivas de AGENTS.md."""
    cpath = ctx.standard.roles["adapter.claude.instructions"]["ruta"]
    apath = ctx.standard.roles["instructions.root"]["ruta"]
    ctext, atext = ctx.read(cpath), ctx.read(apath)
    if ctext is None or atext is None:
        return
    a_heads = set(headings(atext))
    dup_heads = [h for h in headings(ctext) if h in a_heads]
    a_lines = {normalize(l) for _, l in prose_lines(atext) if len(normalize(l)) >= MIN_DUP_CHARS}
    dup_lines = [(n, l) for n, l in prose_lines(ctext) if len(normalize(l)) >= MIN_DUP_CHARS and normalize(l) in a_lines]
    if dup_heads:
        yield Finding("adapter.claude.no-duplication", "HS-INS-007",
                      f"{cpath} repite encabezados de {apath}: {', '.join(dup_heads[:5])}.",
                      "Deja en CLAUDE.md solo `@AGENTS.md` y contenido exclusivo de Claude Code.", cpath)
    if dup_lines:
        yield Finding("adapter.claude.no-duplication", "HS-INS-007",
                      f"{cpath} repite {len(dup_lines)} línea(s) de {apath} (primera en la línea {dup_lines[0][0]}).",
                      "Elimina el contenido duplicado: AGENTS.md es la fuente única (ADR-003).", cpath)


@rule("adapter.claude.local-files-ignored", ["HS-SEC-003"])
def local_files_ignored(ctx: Context):
    """.gitignore ignora CLAUDE.local.md y .claude/settings.local.json."""
    text = ctx.read(".gitignore") or ""
    for p in ("CLAUDE.local.md", ".claude/settings.local.json"):
        if not gitignore_matches(text, p):
            yield Finding("adapter.claude.local-files-ignored", "HS-SEC-003", f".gitignore no ignora `{p}`.",
                          f"Añade `{p}` a .gitignore: es configuración personal y no debe versionarse.", ".gitignore")
