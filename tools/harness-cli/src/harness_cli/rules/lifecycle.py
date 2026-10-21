"""Reglas del ciclo de vida de tareas y del PR (N1, ADR-005, ADR-016, D-023).

La lógica está en `harness_cli.tasks`. Aquí se registran las reglas para la trazabilidad
(requisito ↔ regla ↔ prueba) y para que `harness check` ejecute la parte estática.
- context="check": las ejecuta `harness check` (validación sin base).
- context="pr": necesitan la base o el cuerpo del PR; las ejecutan `harness tasks validate --base`
  y `harness pr check` en el workflow harness-tasks-lifecycle.yml. Se prueban en tests/test_tasks.py.
"""
from __future__ import annotations

from ..context import Context
from ..model import Finding
from . import rule

STATIC = ["tasks.schema", "tasks.naming", "tasks.unique", "tasks.body", "tasks.depends",
          "tasks.location", "tasks.acceptance"]


def _static(ctx: Context) -> list[Finding]:
    if "tasks.static" not in ctx._cache:
        from .. import tasks as T
        ctx._cache["tasks.static"] = T.validate(ctx)
    return ctx._cache["tasks.static"][0]


def _register_static(rule_id: str) -> None:
    from ..tasks import RULE_REQ

    def func(ctx: Context):
        for f in _static(ctx):
            if f.rule == rule_id:
                f.severity = None  # la deriva el checker (y aplica waivers)
                yield f
    func.__doc__ = f"Parte estática de {rule_id} (ver harness_cli.tasks)."
    rule(rule_id, [RULE_REQ[rule_id]])(func)


for _r in STATIC:
    _register_static(_r)


@rule("tasks.index", ["HS-STA-006"])
def tasks_index(ctx: Context):
    """plans.index coincide con la salida de `harness tasks index`."""
    from .. import tasks as T
    if not (ctx.root / ctx.role_path("plans.dir")).is_dir():
        return
    path = ctx.role_path("plans.index")
    expected = T.render_index(T.validate(ctx)[1] if "tasks.static" not in ctx._cache else ctx._cache["tasks.static"][1])
    if ctx.read(path) != expected:
        yield Finding("tasks.index", "HS-STA-006", f"{path} no coincide con las tareas actuales.",
                      "Ejecuta `harness tasks index --write` y añade el resultado al PR.", path)


def _pr_rule(rule_id: str, doc: str) -> None:
    from ..tasks import RULE_REQ

    def func(ctx: Context):
        return iter(())
    func.__doc__ = doc
    rule(rule_id, [RULE_REQ[rule_id]], context="pr")(func)


for _id, _doc in [
    ("tasks.deleted", "Ninguna tarea de la base desaparece (se cancela, no se borra)."),
    ("tasks.transition", "Solo transiciones de estado permitidas respecto a la base del PR."),
    ("tasks.done-pr", "`done_pr` es el número del PR que hace la transición a done."),
    ("pr.anchors", "El cuerpo del PR contiene las secciones tarea, riesgo y sensible."),
    ("pr.task", "El PR referencia una tarea existente (o es trivial o un revert)."),
    ("pr.trivial", "Un PR trivial solo toca rutas triviales y ninguna sensible (D-023)."),
    ("pr.risk", "La clase de riesgo del PR es bajo, medio o alto."),
    ("pr.sensitive", "`sensible: no` no se declara si el diff toca rutas sensibles."),
    ("pr.risk-sensitive", "Un PR que toca rutas sensibles no se declara de riesgo bajo."),
    ("pr.adr-immutable", "Un ADR aceptado solo cambia estado/reemplazada_por."),
]:
    _pr_rule(_id, _doc)
