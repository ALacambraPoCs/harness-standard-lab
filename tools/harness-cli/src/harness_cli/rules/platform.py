"""Reglas de `harness platform check` (F5.3-A, HS-CI-006). Se ejecutan contra la API, no en `harness check`."""
from __future__ import annotations

from ..context import Context
from . import rule

_DOCS = {
    "platform.manifest": "Hay un manifiesto válido que indica qué nivel comprobar.",
    "platform.reachable": "La API de GitHub devuelve el repositorio y las reglas de su rama por defecto.",
    "platform.pull-request": "La rama por defecto exige PR para cambiar (N1+).",
    "platform.required-checks": "Los checks del nivel son requeridos en la rama por defecto.",
    "platform.no-force-push": "La rama por defecto bloquea el force push.",
    "platform.no-deletion": "La rama por defecto no se puede borrar.",
    "platform.approvals": "N2+: ≥ 1 aprobación, Code Owners y aprobación del último push por otra persona.",
    "platform.gate-environment": "El environment de la puerta de riesgo alto existe y tiene revisores (0.6.0+).",
    "platform.deploy-environment": "El environment de despliegue declarado existe y está limitado a ramas concretas.",
}


def _make(rule_id: str, doc: str) -> None:
    def func(ctx: Context):
        return iter(())
    func.__doc__ = doc
    rule(rule_id, ["HS-CI-006"], context="platform")(func)


for _id, _doc in _DOCS.items():
    _make(_id, _doc)
