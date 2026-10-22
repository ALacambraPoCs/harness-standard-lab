from __future__ import annotations

import datetime as dt
from pathlib import Path

from . import __version__
from .context import Context
from .model import SEVERITY_BY_LEVEL, SEVERITY_ORDER, Result
from .rules import load_all
from .standard import LEVELS, Standard, load_standard


def run_check(root: Path, *, standard: Standard | None = None, today: dt.date | None = None,
              run_commands: bool = False, command_timeout: int = 900,
              only_rules: set[str] | None = None) -> Result:
    std = standard or load_standard()
    ctx = Context.build(root, std, today or dt.date.today(), run_commands=run_commands,
                        command_timeout=command_timeout)
    registry = load_all()
    applicable = {r["id"]: r for r in std.applicable(ctx.level, ctx.adapters, ctx.declared_version)}

    result = Result(root=str(ctx.root), standard_version=std.version, cli_version=__version__,
                    declared_level=(ctx.manifest or {}).get("standard", {}).get("level") if isinstance(ctx.manifest, dict) else None,
                    effective_level=None, adapters=sorted(ctx.adapters))

    for rule in registry.values():
        if only_rules and rule.id not in only_rules:
            continue
        reqs = [r for r in rule.requirements if r in applicable]
        if not reqs:
            result.rules_skipped[rule.id] = "requisitos no aplicables al nivel/adaptadores declarados"
            continue
        if rule.context != "check":
            result.rules_skipped[rule.id] = ("se verifica en el PR (harness tasks validate --base / harness pr check)"
                                             if rule.context == "pr" else "se verifica en el repositorio central (harness catalog validate)")
            continue
        if rule.needs_valid_manifest and not ctx.manifest_valid:
            result.rules_skipped[rule.id] = "manifiesto ausente o inválido (ver core.manifest.valid)"
            continue
        if rule.platform and ctx.platform != rule.platform:
            result.rules_skipped[rule.id] = f"plataforma distinta de {rule.platform}"
            continue
        if rule.needs_commands and not run_commands:
            result.rules_skipped[rule.id] = "requiere --run-commands"
            continue
        result.rules_run.append(rule.id)
        for f in rule.func(ctx):
            req = std.requirements[f.requirement]
            f.why = f"{req['id']} ({req['nivel']}): {req['titulo']}"
            f.severity = f.severity or SEVERITY_BY_LEVEL[req["nivel"]]
            result.findings.append(f)

    _apply_waivers(ctx, result)
    result.findings.sort(key=lambda f: (f.status != "fail", SEVERITY_ORDER.get(f.severity, 9), f.requirement, f.rule))
    result.effective_level = _effective_level(std, ctx, result)
    return result


def _apply_waivers(ctx: Context, result: Result) -> None:
    if not ctx.manifest_valid:
        return
    active = {}
    for w in ctx.manifest.get("waivers") or []:
        req = ctx.standard.requirements.get(w["requirement"])
        if not req or not req["exentable"]:
            continue
        if dt.date.fromisoformat(w["approved_on"]) <= ctx.today <= dt.date.fromisoformat(w["expires"]):
            active[w["requirement"]] = w
    for f in result.findings:
        if f.requirement in active and f.rule != "core.waivers.valid":
            f.status, f.waiver = "waived", active[f.requirement]


def _effective_level(std: Standard, ctx: Context, result: Result) -> str | None:
    """Nivel más alto ≤ declarado en el que no hay errores DEBE/NO DEBE sin waiver.

    Solo se evalúan los niveles definidos en la versión declarada del estándar.
    """
    if not ctx.manifest_valid:
        return None
    failing = {f.requirement for f in result.findings if f.status == "fail" and f.severity == "error"}
    effective = None
    for lvl in LEVELS[: LEVELS.index(ctx.level) + 1]:
        if not std.level_defined(lvl, ctx.declared_version):
            break
        reqs = [r for r in std.applicable(lvl, ctx.adapters, ctx.declared_version) if r["nivel"] in ("DEBE", "NO DEBE")]
        if not reqs or any(r["id"] in failing for r in reqs):
            break
        effective = lvl
    return effective
