"""Registro de reglas de conformidad.

Cada regla declara los requisitos que verifica. El checker solo ejecuta una regla si al menos
uno de sus requisitos aplica a la instancia (nivel declarado + adaptadores).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from ..context import Context
from ..model import Finding


@dataclass
class Rule:
    id: str
    requirements: tuple[str, ...]
    func: Callable[[Context], Iterable[Finding]]
    needs_valid_manifest: bool = True
    needs_commands: bool = False
    platform: str | None = None
    doc: str = ""
    context: str = "check"   # check: harness check · pr: solo con base del PR (tasks validate --base, pr check)


REGISTRY: dict[str, Rule] = {}


def rule(rule_id: str, requirements: Iterable[str], *, needs_valid_manifest: bool = True,
         needs_commands: bool = False, platform: str | None = None, context: str = "check"):
    def deco(func):
        if rule_id in REGISTRY:
            raise ValueError(f"Regla duplicada: {rule_id}")
        REGISTRY[rule_id] = Rule(rule_id, tuple(requirements), func, needs_valid_manifest,
                                 needs_commands, platform, (func.__doc__ or "").strip(), context)
        return func
    return deco


def load_all() -> dict[str, Rule]:
    from . import catalog, claude, components, core, github, lifecycle, n1  # noqa: F401  (registran sus reglas al importarse)
    return REGISTRY
