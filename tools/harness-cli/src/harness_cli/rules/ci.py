"""Seguridad de los workflows de la instancia (estándar 0.7.0, F5.3-B, D-063; HS-CI-007 y HS-CI-008).

Reglas estáticas y deterministas sobre `.github/workflows/*.yml`. Reducen el riesgo de los vectores
V2, V3 y V12 del modelo de amenazas (docs/fase-5/02-modelo-amenazas.md); no son una prueba formal.
Fuentes: docs.github.com «Secure use reference» y «Reusing workflow configurations» (F5-01, G8–G10).
"""
from __future__ import annotations

import re

import yaml

from ..context import Context
from ..model import Finding
from . import rule

UNTRUSTED = re.compile(
    r"\$\{\{[^}]*\b(github\.head_ref|github\.event\.("
    r"pull_request\.(title|body|head\.ref|head\.label)|issue\.(title|body)|comment\.body|review\.body|"
    r"review_comment\.body|head_commit\.(message|author)|commits|discussion\.(title|body)|pages))")
MODEL_CREDS = re.compile(r"\b(ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH_TOKEN|anthropic_api_key|claude_code_oauth_token)\b")
SHA = re.compile(r"^[0-9a-f]{40}$")
# Workflows reutilizables del propio estándar: se fijan a un tag de release `cli-v…` (ADR-008, D-063).
STANDARD_WORKFLOW = re.compile(r"/\.github/workflows/harness-[a-z-]+\.ya?ml@cli-v[0-9][0-9A-Za-z.\-]*$")


def _workflows(ctx: Context):
    wdir = ctx.root / ctx.standard.roles["ci.workflows"]["ruta"]
    if not wdir.is_dir():
        return []
    out = []
    for wf in sorted(list(wdir.glob("*.yml")) + list(wdir.glob("*.yaml"))):
        rel = wf.relative_to(ctx.root).as_posix()
        text = wf.read_text(encoding="utf-8", errors="replace")
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict):
            out.append((rel, doc, text))
    return out


def _triggers(doc: dict) -> set[str]:
    on = doc.get("on", doc.get(True))           # PyYAML lee la clave `on:` como True
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return {str(x) for x in on}
    if isinstance(on, dict):
        return {str(k) for k in on}
    return set()


def _jobs(doc: dict):
    jobs = doc.get("jobs")
    return [(n, j) for n, j in jobs.items() if isinstance(j, dict)] if isinstance(jobs, dict) else []


def _writes(perms) -> list[str]:
    if perms == "write-all":
        return ["write-all"]
    if isinstance(perms, dict):
        return [f"{k}: {v}" for k, v in perms.items() if str(v) == "write"]
    return []


@rule("ci.no-pr-target", ["HS-CI-007"], platform="github")
def no_pr_target(ctx: Context):
    """Ningún workflow se dispara con `pull_request_target` (salvo waiver con ADR)."""
    for rel, doc, _ in _workflows(ctx):
        if "pull_request_target" in _triggers(doc):
            yield Finding("ci.no-pr-target", "HS-CI-007", f"{rel} se dispara con `pull_request_target`.",
                          "Usa `pull_request`: los forks reciben token de solo lectura y sin secretos. Si es imprescindible, "
                          "registra un ADR y un waiver, y no hagas checkout del código del PR (F5-01, G9).", rel)


@rule("ci.no-untrusted-interpolation", ["HS-CI-007"], platform="github")
def no_untrusted_interpolation(ctx: Context):
    """Los datos del evento controlados por terceros no se interpolan en `run:` ni en `script:`."""
    for rel, doc, _ in _workflows(ctx):
        for jname, job in _jobs(doc):
            for step in job.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                for campo, valor in (("run", step.get("run")), ("script", (step.get("with") or {}).get("script"))):
                    m = UNTRUSTED.search(valor or "") if isinstance(valor, str) else None
                    if m:
                        yield Finding("ci.no-untrusted-interpolation", "HS-CI-007",
                                      f"{rel} (job `{jname}`): `{m.group(1)}` interpolado en `{campo}:` (inyección de script).",
                                      "Pásalo por `env:` (p. ej. `TITLE: ${{ github.event.pull_request.title }}`) y usa `\"$TITLE\"` en el script (G10).",
                                      rel)


@rule("ci.permissions", ["HS-CI-007"], platform="github")
def permissions(ctx: Context):
    """Cada workflow declara `permissions:` de nivel superior y sin escritura global."""
    for rel, doc, _ in _workflows(ctx):
        if "permissions" not in doc:
            yield Finding("ci.permissions", "HS-CI-007", f"{rel} no declara `permissions:` de nivel superior.",
                          "Añade `permissions: {contents: read}` y amplía solo en el job que lo necesite (G8).", rel)
            continue
        w = _writes(doc["permissions"])
        if w:
            yield Finding("ci.permissions", "HS-CI-007", f"{rel} concede escritura a todos los jobs: {', '.join(w)}.",
                          "Deja el nivel superior en lectura y declara la escritura en el job que la usa.", rel)


@rule("ci.model-readonly", ["HS-CI-007"], platform="github")
def model_readonly(ctx: Context):
    """Un job con credenciales del modelo no tiene permisos de escritura (salvo id-token, para OIDC)."""
    for rel, doc, _ in _workflows(ctx):
        for jname, job in _jobs(doc):
            if not MODEL_CREDS.search(yaml.safe_dump(job, allow_unicode=True)):
                continue
            perms = job.get("permissions", doc.get("permissions"))
            if perms is None:
                w = ["sin `permissions:` (hereda los permisos por defecto del repositorio)"]
            else:
                w = [x for x in _writes(perms) if not x.startswith("id-token")]
            if w:
                yield Finding("ci.model-readonly", "HS-CI-007",
                              f"{rel} (job `{jname}`) usa credenciales del modelo con escritura: {', '.join(w)}.",
                              "El job del modelo solo lee; publica el resultado en otro job sin credenciales del modelo (ADR-013).",
                              rel)


def _uses(doc: dict):
    for jname, job in _jobs(doc):
        if isinstance(job.get("uses"), str):
            yield jname, job["uses"]
        for step in job.get("steps") or []:
            if isinstance(step, dict) and isinstance(step.get("uses"), str):
                yield jname, step["uses"]


@rule("ci.pinned", ["HS-CI-008"], platform="github")
def pinned(ctx: Context):
    """Las actions y workflows reutilizables de terceros se fijan a un SHA completo."""
    for rel, doc, _ in _workflows(ctx):
        for jname, ref in _uses(doc):
            if ref.startswith(("./", "docker://")) or STANDARD_WORKFLOW.search(ref):
                continue
            version = ref.rsplit("@", 1)[1] if "@" in ref else ""
            if not SHA.match(version):
                yield Finding("ci.pinned", "HS-CI-008", f"{rel} (job `{jname}`): `{ref}` no está fijado a un SHA.",
                              "Usa el SHA completo del commit y deja la versión en un comentario (`@<sha> # v4.2.0`) (G10).", rel)


@rule("ci.merge-group", ["HS-CI-008"], platform="github")
def merge_group(ctx: Context):
    """Los workflows que se ejecutan en PR también se ejecutan en `merge_group`."""
    for rel, doc, _ in _workflows(ctx):
        t = _triggers(doc)
        if "pull_request" in t and "merge_group" not in t:
            yield Finding("ci.merge-group", "HS-CI-008", f"{rel} se dispara con `pull_request` pero no con `merge_group`.",
                          "Añade `merge_group:`: con merge queue, sin él no se ejecutan sus checks (G5).", rel)
