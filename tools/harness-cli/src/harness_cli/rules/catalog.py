"""Reglas del catálogo central (ámbito estándar). Las ejecuta `harness catalog validate`; se registran aquí
para la trazabilidad requisito ↔ regla ↔ prueba (tests/test_catalog.py)."""
from __future__ import annotations

from ..catalog import RULE_REQ
from . import rule

DOCS = {
    "catalog.entry": "Cada componente tiene componente.yaml válido, coherente con su directorio y con sus archivos de origen.",
    "catalog.ficha": "Cada componente tiene FICHA.md con los 17 apartados.",
    "catalog.skill": "Las skills del catálogo cumplen Agent Skills, su perfil y el destino .claude/skills/<id>/ (ADR-012).",
    "catalog.transition": "Solo transiciones de estado permitidas respecto a la base.",
    "catalog.version": "Un componente que cambia sube su versión SemVer.",
}


def _register(rid: str) -> None:
    def func(ctx):
        return iter(())
    func.__doc__ = DOCS[rid]
    rule(rid, [RULE_REQ[rid]], context="catalog")(func)


for _r in DOCS:
    _register(_r)
