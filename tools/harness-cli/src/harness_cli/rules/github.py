"""Reglas del adaptador de plataforma github (ADR-013, HS-GOV-004)."""
from __future__ import annotations

import yaml

from ..context import Context
from ..matchers import owners_for, parse_codeowners
from ..model import Finding
from . import rule

REUSABLE = "harness-conformance.yml"


@rule("core.codeowners.sensitive-paths", ["HS-SEC-002"], platform="github")
def codeowners_sensitive(ctx: Context):
    """CODEOWNERS (primera ubicación reconocida por GitHub) asigna propietario a cada ruta sensible."""
    spec = ctx.standard.roles["codeowners"]
    present = [p for p in spec["alternativas"] if (ctx.root / p).is_file()]
    if not present:
        yield Finding("core.codeowners.sensitive-paths", "HS-SEC-002", "No existe archivo CODEOWNERS.",
                      "Crea .github/CODEOWNERS (plantilla: template/adapters/github/CODEOWNERS).", spec["ruta"])
        return
    path = present[0]
    if len(present) > 1:
        yield Finding("core.codeowners.sensitive-paths", "HS-SEC-002",
                      f"Hay varios CODEOWNERS ({', '.join(present)}); GitHub solo usa {path}.",
                      "Deja un único archivo para evitar confusiones.", path, severity="warning")
    rules = parse_codeowners(ctx.read(path) or "")
    for sample in ctx.standard.sensitive_paths:
        eff = owners_for(rules, sample)
        if eff is None:
            yield Finding("core.codeowners.sensitive-paths", "HS-SEC-002", f"Ninguna regla de {path} cubre `{sample}`.",
                          "Añade un patrón con propietario de plataforma/seguridad (ADR-013).", path)
        elif not eff.owners:
            yield Finding("core.codeowners.sensitive-paths", "HS-SEC-002",
                          f"`{sample}` queda sin propietario por la regla `{eff.pattern}` (línea {eff.line}); en CODEOWNERS gana el último patrón que coincide.",
                          "Reordena o añade propietarios: las rutas sensibles deben declararse al final del archivo.", path)


@rule("core.ci.conformance-workflow", ["HS-GOV-004"], platform="github")
def conformance_workflow(ctx: Context):
    """Un workflow ejecuta la conformidad (harness check o el reutilizable) en pull_request."""
    wdir = ctx.root / ctx.standard.roles["ci.workflows"]["ruta"]
    found_any = False
    for wf in sorted(list(wdir.glob("*.yml")) + list(wdir.glob("*.yaml"))) if wdir.is_dir() else []:
        text = wf.read_text(encoding="utf-8", errors="replace")
        if REUSABLE not in text and "harness check" not in text:
            continue
        found_any = True
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        on = doc.get("on", doc.get(True))  # PyYAML interpreta la clave `on` como booleano True
        events = set([on] if isinstance(on, str) else (on or []))
        if "pull_request" in events:
            return
    rel = ctx.standard.roles["ci.workflows"]["ruta"]
    msg = ("Ningún workflow de conformidad se dispara en `pull_request`." if found_any
           else "Ningún workflow ejecuta `harness check` ni llama a harness-conformance.yml.")
    yield Finding("core.ci.conformance-workflow", "HS-GOV-004", msg,
                  "Añade .github/workflows/harness.yml que llame al workflow reutilizable en `pull_request` y `merge_group`, y márcalo como check requerido en el ruleset.", rel)
