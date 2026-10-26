"""Clase de riesgo calculada a partir del diff y de las tareas (D-058, HS-CI-005).

La clase efectiva de un PR es la mayor entre la calculada aquí, la declarada en el cuerpo del PR y la
de las tareas que el PR cierra. Declarar puede subir la clase, nunca bajarla. La clase `alto` activa
la puerta explícita del workflow de tareas (ADR-010 rev. 2).
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field

from .context import Context
from .matchers import compile_pattern

CLASES = ("bajo", "medio", "alto")


def rank(clase: str | None) -> int:
    return CLASES.index(clase) if clase in CLASES else -1


@dataclass
class Riesgo:
    clase: str = "bajo"
    senales: list[tuple[str, str]] = field(default_factory=list)   # (clase, motivo)

    def subir(self, clase: str, motivo: str) -> None:
        self.senales.append((clase, motivo))
        if rank(clase) > rank(self.clase):
            self.clase = clase

    def as_dict(self) -> dict:
        return {"clase": self.clase, "senales": [{"clase": c, "motivo": m} for c, m in self.senales]}


def _matches(patterns: list[str], path: str) -> bool:
    return any(compile_pattern(p, codeowners=True).match(path) for p in patterns)


def _name_status(ctx: Context, base: str) -> list[tuple[str, str, str | None]]:
    """(estado, ruta, ruta_anterior) de `git diff --name-status -M base...HEAD`."""
    out = subprocess.run(["git", "diff", "--name-status", "-M", f"{base}...HEAD"], cwd=ctx.root,
                         capture_output=True, text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        st = parts[0][0]
        if st == "R" and len(parts) >= 3:
            rows.append(("R", parts[2], parts[1]))
        elif len(parts) >= 2:
            rows.append((st, parts[1], None))
    return rows


def critical_patterns(ctx: Context) -> list[str]:
    extra = (((ctx.manifest or {}).get("riesgo") or {}).get("rutas_criticas")) or []
    return list(ctx.standard.critical_patterns) + [p for p in extra if isinstance(p, str)]


def compute(ctx: Context, base: str) -> Riesgo:
    """Clase mínima del PR (base...HEAD) según rutas, pruebas borradas y tareas que se cierran."""
    from .tasks import load_at_ref, load_worktree

    r = Riesgo()
    crit = critical_patterns(ctx)
    for st, path, old in _name_status(ctx, base):
        if _matches(crit, path) or (old and _matches(crit, old)):
            r.subir("alto", f"ruta crítica: {path}")
        elif _matches(ctx.standard.sensitive_patterns, path) or (old and _matches(ctx.standard.sensitive_patterns, old)):
            r.subir("medio", f"configuración de agentes: {path}")
        if st == "D" and _matches(ctx.standard.test_patterns, path):
            r.subir("medio", f"prueba borrada: {path}")
        elif st == "R" and old and _matches(ctx.standard.test_patterns, old):
            r.subir("medio", f"prueba renombrada: {old} → {path}")

    before = load_at_ref(ctx, base)
    for t in load_worktree(ctx):
        if not t.id or t.errors or t.status != "done":
            continue
        old = before.get(t.id)
        if old is not None and old.status == "done":
            continue                                   # no la cierra este PR
        if t.meta.get("risk") in CLASES:
            r.subir(t.meta["risk"], f"{t.id} declara risk: {t.meta['risk']}")
        if old is not None and (old.meta.get("acceptance") or []) != (t.meta.get("acceptance") or []):
            r.subir("medio", f"{t.id}: cambian los criterios de aceptación en el PR que la cierra (K-14)")
    if not r.senales:
        r.senales.append(("bajo", "sin señales de riesgo en el diff"))
    return r
