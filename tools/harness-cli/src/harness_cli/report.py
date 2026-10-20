from __future__ import annotations

import json

from .model import Result

ICON = {"error": "✗", "warning": "!", "info": "i"}


def to_text(res: Result, verbose: bool = False) -> str:
    out = [f"harness check · estándar {res.standard_version} · CLI {res.cli_version}",
           f"raíz: {res.root}",
           f"nivel declarado: {res.declared_level or '—'} · nivel efectivo: {res.effective_level or 'ninguno'} · "
           f"adaptadores: {', '.join(res.adapters) or '—'}", ""]
    for f in res.findings:
        tag = "WAIVED" if f.status == "waived" else f.severity.upper()
        icon = "~" if f.status == "waived" else ICON.get(f.severity, "?")
        out.append(f"{icon} [{tag}] {f.rule}" + (f"  ({f.path})" if f.path else ""))
        out.append(f"    QUÉ:        {f.message}")
        out.append(f"    POR QUÉ:    {f.why}")
        out.append(f"    CÓMO:       {f.remedy}")
        if f.waiver:
            out.append(f"    WAIVER:     {f.waiver['reason']} (aprobado por {f.waiver['approved_by']}, caduca {f.waiver['expires']})")
        out.append("")
    if verbose and res.rules_skipped:
        out.append("Reglas omitidas:")
        out += [f"  - {r}: {why}" for r, why in sorted(res.rules_skipped.items())]
        out.append("")
    c = res.counts()
    out.append(f"Resultado: {c['error']} error(es), {c['warning']} aviso(s), {c['info']} info, {c['waived']} con waiver · "
               f"{len(res.rules_run)} regla(s) ejecutada(s), {len(res.rules_skipped)} omitida(s).")
    return "\n".join(out)


def to_json(res: Result) -> str:
    return json.dumps(res.to_dict(), ensure_ascii=False, indent=2)
