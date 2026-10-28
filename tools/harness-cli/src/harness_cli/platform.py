"""Autoridad comprobable (F5.3-A, D-062, HS-CI-006): compara el estado real de GitHub con lo que exige
el nivel declarado. Solo lee. En repositorios públicos no necesita token.

API (docs.github.com, verificado el 2026-10-28):
- GET /repos/{o}/{r}/rules/branches/{rama}: reglas activas de la rama (sin autenticación si es público).
- GET /repos/{o}/{r}/environments/{nombre}: environment y `protection_rules` (ídem).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from typing import Callable

from .context import Context
from .model import SEVERITY_BY_LEVEL, Finding
from .standard import semver

API = "https://api.github.com"
GATE_DEFAULT = "aprobacion-riesgo-alto"

# Regla → requisito (las comprobaciones de plataforma cuelgan de HS-CI-006).
RULE_REQ = {
    "platform.reachable": "HS-CI-006",
    "platform.pull-request": "HS-CI-006",
    "platform.required-checks": "HS-CI-006",
    "platform.no-force-push": "HS-CI-006",
    "platform.no-deletion": "HS-CI-006",
    "platform.approvals": "HS-CI-006",
    "platform.gate-environment": "HS-CI-006",
    "platform.deploy-environment": "HS-CI-006",
}

Fetch = Callable[[str], tuple[int, object]]


class Inaccesible(Exception):
    pass


def http_fetch(token: str | None = None) -> Fetch:
    def fetch(path: str) -> tuple[int, object]:
        req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json",
                                                         "X-GitHub-Api-Version": "2022-11-28",
                                                         "User-Agent": "harness-cli"})
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (URL fija de la API)
                return r.status, json.loads(r.read().decode("utf-8") or "null")
        except urllib.error.HTTPError as e:
            return e.code, None
        except urllib.error.URLError as e:
            raise Inaccesible(str(e.reason)) from e
    return fetch


def repo_from_git(ctx: Context) -> str | None:
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ctx.root, capture_output=True,
                             text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def expected_checks(ctx: Context) -> list[str]:
    """Nombres de job de los checks requeridos (se comparan por sufijo con el `context` del ruleset)."""
    plat = (ctx.manifest or {}).get("plataforma") or {}
    if plat.get("checks_requeridos"):
        return list(plat["checks_requeridos"])
    out = ["harness check"]
    if ctx.level in ("N1", "N2", "N3"):
        out.append("harness tasks")
        if _since(ctx, "0.6.0"):
            out.append("puerta riesgo alto")
    return out


def _since(ctx: Context, version: str) -> bool:
    d = semver(ctx.declared_version) if ctx.declared_version else None
    return bool(d) and d >= semver(version)


def _check_matches(expected: str, actual: str) -> bool:
    return actual == expected or actual.endswith(" / " + expected) or actual.endswith("/" + expected)


def check(ctx: Context, repo: str, branch: str | None, fetch: Fetch) -> list[Finding]:
    findings: list[Finding] = []

    def f(rule_id: str, msg: str, remedy: str, severity: str | None = None):
        req = RULE_REQ[rule_id]
        spec = ctx.standard.requirements.get(req)
        sev = severity or (SEVERITY_BY_LEVEL[spec["nivel"]] if spec else "error")
        findings.append(Finding(rule_id, req, msg, remedy, None, severity=sev,
                                why=f"{req} ({spec['nivel']}): {spec['titulo']}" if spec else req))

    level = ctx.level
    plat = (ctx.manifest or {}).get("plataforma") or {}
    if branch is None:
        st, data = fetch(f"/repos/{repo}")
        if st != 200 or not isinstance(data, dict):
            f("platform.reachable", f"No se puede leer el repositorio {repo} (HTTP {st}).",
              "Comprueba el nombre (`--repo dueño/repo`). Con HTTP 403 o 429 puede ser el límite de peticiones sin "
              "token o un proxy: define GITHUB_TOKEN (en Actions, el del job). Si es privado, el token necesita lectura.")
            return findings
        branch = data.get("default_branch") or "main"

    st, rules = fetch(f"/repos/{repo}/rules/branches/{branch}")
    if st != 200 or not isinstance(rules, list):
        f("platform.reachable", f"No se pueden leer las reglas de `{branch}` en {repo} (HTTP {st}).",
          "En repos privados hace falta un token con permiso Metadata: read.")
        return findings
    by_type: dict[str, list[dict]] = {}
    for r in rules:
        if isinstance(r, dict):
            by_type.setdefault(r.get("type", ""), []).append(r.get("parameters") or {})

    if level in ("N1", "N2", "N3") and "pull_request" not in by_type:
        f("platform.pull-request", f"La rama `{branch}` no exige PR para cambiar.",
          "Añade al ruleset la regla «Require a pull request before merging» (plantilla standard/plataforma/).")
    contexts = [c.get("context", "") for p in by_type.get("required_status_checks", [])
                for c in (p.get("required_status_checks") or []) if isinstance(c, dict)]
    faltan = [e for e in expected_checks(ctx) if not any(_check_matches(e, a) for a in contexts)]
    if faltan:
        f("platform.required-checks", f"Checks no requeridos en `{branch}`: {', '.join(faltan)} (requeridos hoy: {', '.join(contexts) or 'ninguno'}).",
          "Añádelos en «Require status checks to pass» del ruleset con el nombre exacto que muestra el PR.")
    if "non_fast_forward" not in by_type:
        f("platform.no-force-push", f"La rama `{branch}` admite force push.", "Activa «Block force pushes» en el ruleset.")
    if "deletion" not in by_type:
        f("platform.no-deletion", f"La rama `{branch}` se puede borrar.", "Activa «Restrict deletions» en el ruleset.")
    if level in ("N2", "N3"):
        prs = by_type.get("pull_request") or [{}]
        p = max(prs, key=lambda x: int(x.get("required_approving_review_count") or 0))
        falta = []
        if int(p.get("required_approving_review_count") or 0) < 1:
            falta.append("≥ 1 aprobación")
        if not p.get("require_code_owner_review"):
            falta.append("revisión de Code Owners")
        if not p.get("require_last_push_approval"):
            falta.append("aprobación del último push por otra persona")
        if falta:
            f("platform.approvals", f"El ruleset de `{branch}` no exige: {', '.join(falta)} (N2+, ADR-010 rev. 2).",
              "Actívalo en la regla de PR del ruleset.")

    if level in ("N1", "N2", "N3") and _since(ctx, "0.6.0"):
        gate = plat.get("entorno_puerta") or GATE_DEFAULT
        st, env = fetch(f"/repos/{repo}/environments/{gate}")
        reviewers = []
        prevent = None
        if st == 200 and isinstance(env, dict):
            for pr in env.get("protection_rules") or []:
                if isinstance(pr, dict) and pr.get("type") == "required_reviewers":
                    reviewers = pr.get("reviewers") or []
                    prevent = pr.get("prevent_self_review")
        if st != 200:
            f("platform.gate-environment", f"El environment `{gate}` no existe (HTTP {st}). Si un workflow lo usa, GitHub lo crea SIN protección.",
              "Créalo en Settings → Environments con «Required reviewers» antes de usar el estándar 0.6.0+.")
        elif not reviewers:
            f("platform.gate-environment", f"El environment `{gate}` no tiene revisores obligatorios: la puerta de riesgo alto no para nada.",
              "Añade al menos un revisor en «Required reviewers».")
        elif level in ("N2", "N3") and not prevent:
            f("platform.gate-environment", f"El environment `{gate}` permite que quien lanza el job lo apruebe (N2+).",
              "Activa «Prevent self-review».")

    deploy = plat.get("entorno_despliegue")
    if deploy:
        st, env = fetch(f"/repos/{repo}/environments/{deploy}")
        if st != 200 or not isinstance(env, dict):
            f("platform.deploy-environment", f"El environment de despliegue `{deploy}` no existe (HTTP {st}).",
              "Créalo y limita sus ramas a la rama por defecto (F5.6).")
        elif not env.get("deployment_branch_policy"):
            f("platform.deploy-environment", f"El environment `{deploy}` admite despliegues desde cualquier rama.",
              "En «Deployment branches and tags», limítalo a la rama por defecto.")
    return findings


def resolve_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None
