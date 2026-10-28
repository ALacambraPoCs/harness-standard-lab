"""Rastro de auditoría de un cambio (F5.6-B, D-073): `harness audit <sha|#PR>`.

Reconstruye, **solo leyendo**, quién o qué cambió algo, con qué evidencia y quién lo autorizó:
commit → PR → tarea → origen → riesgo (recalculado) → checks → aprobaciones de la puerta → despliegues
→ estado de la plataforma. No guarda nada: el registro son los propios objetos de Git y de GitHub,
que el equipo no puede reescribir sin dejar rastro (rulesets sin force push, ADR-013).

Necesita un clon del repositorio (para el commit, el diff y las tareas) y la API de GitHub. En repos
públicos funciona sin token; con token, basta lectura de Contents, Pull requests, Checks, Actions y
Deployments.

API (docs.github.com, verificado el 2026-10-28; todas admiten acceso sin autenticación a recursos públicos):
- GET /repos/{o}/{r}/commits/{sha}/pulls — PR fusionado que introdujo el commit (Pull requests: read).
- GET /repos/{o}/{r}/pulls/{n} y /pulls/{n}/commits (Pull requests: read).
- GET /repos/{o}/{r}/commits/{ref}/check-runs (Checks: read).
- GET /repos/{o}/{r}/actions/runs?head_sha= y /actions/runs/{id}/approvals (Actions: read).
- GET /repos/{o}/{r}/deployments?sha= y /deployments/{id}/statuses (Deployments: read).
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

from .context import Context
from .platform import Fetch, _check_matches, expected_checks
from .risk import rank

AGENTE = re.compile(r"(noreply@anthropic\.com|\bclaude\b|\bcodex\b|\bcopilot\b|\bagente?\b)", re.I)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class AuditError(Exception):
    pass


@dataclass
class Auditoria:
    repo: str
    sha: str
    commit: dict = field(default_factory=dict)
    pr: dict | None = None
    tareas: list[dict] = field(default_factory=list)
    origen: dict = field(default_factory=dict)
    riesgo: dict = field(default_factory=dict)
    checks: list[dict] = field(default_factory=list)
    aprobaciones: list[dict] = field(default_factory=list)
    despliegues: list[dict] = field(default_factory=list)
    plataforma: list[dict] | None = None
    alertas: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("repo", "sha", "commit", "pr", "tareas", "origen", "riesgo", "checks",
                                               "aprobaciones", "despliegues", "plataforma", "alertas")}


def _safe(text: str | None, limit: int = 160) -> str:
    """Texto de terceros (títulos, comentarios) apto para una tabla Markdown, un resumen o una issue."""
    t = re.sub(r"\s+", " ", text or "").strip()
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|").replace("`", "'")
    t = re.sub(r"@(?=[A-Za-z0-9])", "@​", t)          # sin menciones: no notifica a nadie
    return t if len(t) <= limit else t[: limit - 1] + "…"


def _git(ctx: Context, *args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ctx.root, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise AuditError(f"git {' '.join(args)}: {getattr(exc, 'stderr', '') or exc}".strip()) from exc


def _get(fetch: Fetch, path: str):
    st, data = fetch(path)
    return data if st == 200 else None


def _commit(ctx: Context, sha: str) -> dict:
    fmt = "%H%x00%an <%ae>%x00%cn <%ce>%x00%cI%x00%G?%x00%P%x00%s%x00%(trailers:key=Co-authored-by,valueonly,separator=%x1f)"
    parts = _git(ctx, "log", "-1", f"--format={fmt}", sha).rstrip("\n").split("\x00")
    parts += [""] * (8 - len(parts))
    return {"sha": parts[0], "autor": parts[1], "committer": parts[2], "fecha": parts[3],
            "firma": {"G": "válida", "U": "válida (confianza desconocida)", "N": "sin firma"}.get(parts[4], parts[4] or "sin firma"),
            "padres": parts[5].split(), "asunto": parts[6],
            "coautores": [x.strip() for x in parts[7].split("\x1f") if x.strip()]}


def resolve(ctx: Context, ref: str, repo: str, fetch: Fetch) -> tuple[str, dict | None]:
    """(sha, pr) a partir de un SHA, una referencia git o `#N` / `pr:N`."""
    m = re.fullmatch(r"(?:#|pr:)(\d+)", ref.strip())
    if m:
        pr = _get(fetch, f"/repos/{repo}/pulls/{m.group(1)}")
        if not isinstance(pr, dict):
            raise AuditError(f"No se puede leer el PR #{m.group(1)} de {repo}.")
        sha = pr.get("merge_commit_sha") if pr.get("merged") else None
        if not sha:
            raise AuditError(f"El PR #{m.group(1)} no está fusionado: no hay cambio que auditar en la rama por defecto.")
        return sha, pr
    sha = _git(ctx, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    prs = _get(fetch, f"/repos/{repo}/commits/{sha}/pulls")
    merged = [p for p in prs or [] if isinstance(p, dict) and p.get("merged_at")]
    pr = _get(fetch, f"/repos/{repo}/pulls/{merged[0]['number']}") if merged else None
    return sha, pr if isinstance(pr, dict) else None


def audit(ctx: Context, ref: str, repo: str, fetch: Fetch, *, platform: bool = True) -> Auditoria:
    from . import platform as P
    from .risk import compute
    from .tasks import load_at_ref, section

    sha, pr = resolve(ctx, ref, repo, fetch)
    a = Auditoria(repo=repo, sha=sha, commit=_commit(ctx, sha))
    body = (pr or {}).get("body") or ""

    # PR: quién lo abrió, quién lo fusionó y cuándo.
    if pr:
        a.pr = {"numero": pr.get("number"), "titulo": _safe(pr.get("title")), "url": pr.get("html_url"),
                "autor": (pr.get("user") or {}).get("login"), "fusionado_por": (pr.get("merged_by") or {}).get("login"),
                "fusionado": pr.get("merged_at"), "head": (pr.get("head") or {}).get("sha"),
                "base": (pr.get("base") or {}).get("ref")}
    else:
        a.alertas.append("El commit no llegó por un PR fusionado (¿push directo o PR no encontrado?): sin revisión ni checks de PR.")

    # Tareas que referencia el PR, en su estado tras el cambio.
    tareas = load_at_ref(ctx, sha)
    for tid in sorted(set(re.findall(r"\bT-\d{4}\b", section(body, "tarea")))):
        t = tareas.get(tid)
        a.tareas.append({"id": tid, "estado": t.status if t else None, "ruta": t.path if t else None,
                         "done_pr": t.meta.get("done_pr") if t else None,
                         "criterios": len(t.meta.get("acceptance") or []) if t else 0})
        if t is None:
            a.alertas.append(f"El PR referencia `{tid}`, que no existe en {sha[:7]}.")
    if pr and not a.tareas and not re.search(r"\btrivial\b", section(body, "tarea"), re.I):
        a.alertas.append("El PR no referencia ninguna tarea ni se declara `trivial`.")

    # Origen: lo declarado en el PR y los coautores de sus commits.
    coautores = list(a.commit["coautores"])
    if pr:
        for c in _get(fetch, f"/repos/{repo}/pulls/{pr['number']}/commits?per_page=100") or []:
            msg = ((c or {}).get("commit") or {}).get("message") or ""
            coautores += re.findall(r"(?im)^co-authored-by:\s*(.+)$", msg)
    coautores = sorted({x.strip() for x in coautores})
    m = re.search(r"\*\*Origen del cambio:\*\*\s*(.+)", body)
    declarado = _safe(m.group(1)) if m else None
    agente = any(AGENTE.search(x) for x in coautores) or bool(declarado and re.search(r"\bagente\b", declarado, re.I))
    a.origen = {"declarado": declarado, "coautores": [_safe(x) for x in coautores], "agente": agente}
    if agente and declarado and re.match(r"persona\b", declarado, re.I) and "agente" not in declarado.lower():
        a.alertas.append("El PR declara origen `persona`, pero hay coautoría de un agente en los commits.")

    # Riesgo: declarado en el PR frente al recalculado sobre el commit fusionado.
    calc = None
    if a.commit["padres"]:
        calc = compute(ctx, f"{sha}^1", sha)
    r_decl = re.search(r"\b(bajo|medio|alto)\b", re.sub(r"bajo\s*\|\s*medio\s*\|\s*alto", "", section(body, "riesgo").lower()))
    declarada = r_decl.group(1) if r_decl else None
    efectiva = max([c for c in (declarada, calc.clase if calc else None) if c], key=rank, default=None)
    a.riesgo = {"declarada": declarada, "calculada": calc.clase if calc else None, "efectiva": efectiva,
                "senales": [m for _, m in calc.senales] if calc else []}
    if pr and declarada and calc and rank(declarada) < rank(calc.clase):
        a.alertas.append(f"Riesgo declarado `{declarada}` menor que el recalculado `{calc.clase}` (pr.risk-min debió fallar).")

    # Checks del último commit del PR (lo que vio el ruleset al fusionar).
    head = (a.pr or {}).get("head") or sha
    runs = (_get(fetch, f"/repos/{repo}/commits/{head}/check-runs?per_page=100") or {}).get("check_runs") or []
    a.checks = [{"nombre": _safe(c.get("name"), 80), "estado": c.get("status"), "conclusion": c.get("conclusion"),
                 "url": c.get("html_url")} for c in runs if isinstance(c, dict)]
    if pr:
        for esperado in expected_checks(ctx):
            hits = [c for c in a.checks if _check_matches(esperado, c["nombre"]) or c["nombre"] == esperado]
            if not hits:
                a.alertas.append(f"No consta el check requerido `{esperado}` en el último commit del PR.")
            elif not any(c["conclusion"] in ("success", "skipped", "neutral") for c in hits):
                a.alertas.append(f"El check `{esperado}` no terminó en éxito ({', '.join(str(c['conclusion']) for c in hits)}).")

    # Aprobaciones en environments (la puerta de riesgo alto) de los runs del último commit del PR.
    wr = (_get(fetch, f"/repos/{repo}/actions/runs?head_sha={head}&per_page=100") or {}).get("workflow_runs") or []
    for run in wr:
        if not isinstance(run, dict):
            continue
        for ap in _get(fetch, f"/repos/{repo}/actions/runs/{run.get('id')}/approvals") or []:
            if isinstance(ap, dict):
                a.aprobaciones.append({"run": _safe(run.get("name"), 60), "run_url": run.get("html_url"),
                                       "estado": ap.get("state"), "persona": (ap.get("user") or {}).get("login"),
                                       "environments": [e.get("name") for e in ap.get("environments") or [] if isinstance(e, dict)],
                                       "comentario": _safe(ap.get("comment"), 200)})
    gate = (((ctx.manifest or {}).get("plataforma") or {}).get("entorno_puerta")) or P.GATE_DEFAULT
    if pr and efectiva == "alto" and not any(x["estado"] == "approved" and gate in x["environments"] for x in a.aprobaciones):
        a.alertas.append(f"Riesgo `alto` sin aprobación registrada en el environment `{gate}` (ADR-010 rev. 2).")

    # Despliegues del commit y su último estado.
    for d in _get(fetch, f"/repos/{repo}/deployments?sha={sha}&per_page=100") or []:
        if not isinstance(d, dict):
            continue
        sts = _get(fetch, f"/repos/{repo}/deployments/{d.get('id')}/statuses?per_page=1") or []
        last = sts[0] if sts and isinstance(sts[0], dict) else {}
        a.despliegues.append({"environment": d.get("environment"), "fecha": d.get("created_at"),
                              "creador": (d.get("creator") or {}).get("login"), "estado": last.get("state"),
                              "url": last.get("environment_url") or last.get("target_url")})

    if platform and ctx.manifest:
        try:
            a.plataforma = [{"regla": f.rule, "severidad": f.severity, "mensaje": f.message}
                            for f in P.check(ctx, repo, None, fetch)]
        except P.Inaccesible:
            a.plataforma = None
        if a.plataforma:
            a.alertas.append(f"La plataforma no cumple hoy lo que exige el nivel ({len(a.plataforma)} hallazgos de `harness platform check`).")
    return a


def to_markdown(a: Auditoria) -> str:
    c = a.commit
    out = [f"## Auditoría de `{a.sha[:12]}` · {a.repo}", ""]
    out.append(f"**Alertas:** {len(a.alertas)}" + ("" if a.alertas else " ✅"))
    out += [f"- ⚠️ {x}" for x in a.alertas]
    out += ["", "| Qué | Valor |", "|---|---|",
            f"| Commit | `{c['sha'][:12]}` · {_safe(c['asunto'], 100)} |",
            f"| Autor / committer | {_safe(c['autor'], 80)} / {_safe(c['committer'], 80)} |",
            f"| Fecha | {c['fecha']} |", f"| Firma | {c['firma']} |"]
    if a.pr:
        p = a.pr
        out += [f"| PR | [#{p['numero']}]({p['url']}) · {p['titulo']} |",
                f"| Abierto por / fusionado por | {p['autor']} / {p['fusionado_por']} ({p['fusionado']}) |"]
    else:
        out.append("| PR | — |")
    out.append("| Tareas | " + (", ".join(f"{t['id']} ({t['estado']}, done_pr={t['done_pr']}, {t['criterios']} criterios)"
                                         for t in a.tareas) or "—") + " |")
    o = a.origen
    out.append(f"| Origen | declarado: {o.get('declarado') or '—'} · agente: {'sí' if o.get('agente') else 'no'}"
               + (f" · coautores: {', '.join(o['coautores'])}" if o.get("coautores") else "") + " |")
    r = a.riesgo
    out.append(f"| Riesgo | declarado `{r.get('declarada')}` · calculado `{r.get('calculada')}` · efectivo **{r.get('efectiva')}** |")
    if r.get("senales"):
        out.append(f"| Señales de riesgo | {_safe('; '.join(r['senales']), 300)} |")
    out += ["", "### Checks del último commit del PR", ""]
    out += [f"- {x['nombre']}: `{x['conclusion'] or x['estado']}`" for x in a.checks] or ["- (ninguno)"]
    out += ["", "### Aprobaciones en environments", ""]
    out += [f"- {x['persona']} · `{x['estado']}` · {', '.join(x['environments'])} · {x['run']}"
            + (f" · «{x['comentario']}»" if x["comentario"] else "") for x in a.aprobaciones] or ["- (ninguna)"]
    out += ["", "### Despliegues de este commit", ""]
    out += [f"- `{x['environment']}` · {x['estado']} · {x['fecha']} · {x['creador']}" + (f" · {x['url']}" if x["url"] else "")
            for x in a.despliegues] or ["- (ninguno)"]
    if a.plataforma is not None:
        out += ["", "### Plataforma hoy (`harness platform check`)", ""]
        out += [f"- [{x['severidad']}] {x['regla']}: {_safe(x['mensaje'], 200)}" for x in a.plataforma] or ["- Sin hallazgos ✅"]
    out += ["", "_Generado por `harness audit` (solo lectura). Fuente: Git y la API de GitHub; nada de este informe lo declara un agente._"]
    return "\n".join(out) + "\n"
