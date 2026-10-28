"""Ciclo de vida de tareas (ADR-005, ADR-016) y comprobación de PR (D-023, pr.template).

Funciones puras sobre el árbol de trabajo y, opcionalmente, una referencia git base para
validar transiciones. Solo escribe en el repositorio `close` (P-4); el índice lo escribe la CLI.
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .context import Context, _StrDateLoader
from .matchers import compile_pattern
from .model import SEVERITY_BY_LEVEL, Finding

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)
TASK_FILE = re.compile(r"^(T-\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
TERMINAL = {"done", "cancelled"}
ALLOWED = {
    None: {"proposed", "ready", "in_progress"},           # creación
    "proposed": {"ready", "cancelled"},
    "ready": {"in_progress", "cancelled"},
    "in_progress": {"blocked", "in_review", "done", "cancelled"},
    "blocked": {"in_progress", "cancelled"},
    "in_review": {"in_progress", "done"},
    "done": {"regressed"},
    "regressed": {"in_progress"},
    "cancelled": set(),
}
BODY_ANCHORS = ["objetivo", "alcance", "plan", "progreso", "decisiones"]
DONE_ANCHORS = ["resultado"]
INDEX_HEADER = "<!-- generado por harness tasks index; no editar -->"

# Regla → requisito (F2.5). pr.issue pertenece al experimento X-01: no es requisito normativo.
RULE_REQ = {
    "tasks.schema": "HS-STA-002", "tasks.naming": "HS-STA-002", "tasks.unique": "HS-STA-002",
    "tasks.body": "HS-STA-002", "tasks.depends": "HS-STA-002",
    "tasks.location": "HS-STA-003", "tasks.deleted": "HS-STA-003",
    "tasks.transition": "HS-STA-004",
    "tasks.acceptance": "HS-STA-005", "tasks.done-pr": "HS-STA-005",
    "pr.anchors": "HS-CI-002", "pr.task": "HS-CI-002", "pr.trivial": "HS-CI-002", "pr.risk": "HS-CI-002",
    "pr.sensitive": "HS-SEC-006", "pr.risk-sensitive": "HS-SEC-006",
    "pr.adr-immutable": "HS-ARC-006",
    "pr.risk-min": "HS-CI-005",
    "pr.issue": "X-01",
}


def _finding(ctx: Context, rule: str, msg: str, remedy: str, path: str | None, severity: str | None = None) -> Finding:
    req = RULE_REQ[rule]
    spec = ctx.standard.requirements.get(req)
    sev = severity or (SEVERITY_BY_LEVEL[spec["nivel"]] if spec else "error")
    why = f"{req} ({spec['nivel']}): {spec['titulo']}" if spec else req
    return Finding(rule, req, msg, remedy, path, severity=sev, why=why)


@dataclass
class Task:
    path: str                    # relativo a la raíz
    meta: dict[str, Any]
    body: str
    errors: list[str] = field(default_factory=list)

    @property
    def id(self) -> str | None:
        return self.meta.get("id") if isinstance(self.meta, dict) else None

    @property
    def status(self) -> str | None:
        return self.meta.get("status") if isinstance(self.meta, dict) else None


def parse_task(text: str, path: str) -> Task:
    m = FRONT.match(text)
    if not m:
        return Task(path, {}, text, ["sin frontmatter YAML (--- … ---)"])
    try:
        meta = yaml.load(m.group(1), Loader=_StrDateLoader) or {}  # noqa: S506 (SafeLoader)
    except yaml.YAMLError as exc:
        return Task(path, {}, text[m.end():], [f"frontmatter YAML inválido: {exc}"])
    if not isinstance(meta, dict):
        return Task(path, {}, text[m.end():], ["el frontmatter no es un objeto"])
    return Task(path, meta, text[m.end():])


def anchors_in(body: str) -> set[str]:
    return set(re.findall(r"<!--\s*harness:([a-z0-9-]+)\s*-->", body))


def section(body: str, anchor: str) -> str:
    """Texto entre <!-- harness:anchor --> y la siguiente ancla (o el final)."""
    m = re.search(rf"<!--\s*harness:{re.escape(anchor)}\s*-->(.*?)(?=<!--\s*harness:[a-z0-9-]+\s*-->|\Z)", body, re.S)
    return m.group(1).strip() if m else ""


# ─────────────────────────── carga ───────────────────────────
def _dirs(ctx: Context) -> tuple[str, str]:
    return ctx.role_path("plans.active").rstrip("/"), ctx.role_path("plans.completed").rstrip("/")


def load_worktree(ctx: Context) -> list[Task]:
    out = []
    for d in _dirs(ctx):
        base = ctx.root / d
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*.md")):
            if p.name.startswith("_") or p.name == "README.md":
                continue
            out.append(parse_task(p.read_text(encoding="utf-8"), f"{d}/{p.name}"))
    return out


def _git(ctx: Context, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=ctx.root, capture_output=True, text=True, check=True).stdout


def load_at_ref(ctx: Context, ref: str) -> dict[str, Task]:
    """Tareas en la referencia base, indexadas por id."""
    out: dict[str, Task] = {}
    for d in _dirs(ctx):
        try:
            names = _git(ctx, "ls-tree", "--name-only", f"{ref}:{d}").split()
        except subprocess.CalledProcessError:
            continue
        for n in names:
            if not n.endswith(".md") or n.startswith("_") or n == "README.md":
                continue
            t = parse_task(_git(ctx, "show", f"{ref}:{d}/{n}"), f"{d}/{n}")
            if t.id:
                out[t.id] = t
    return out


def changed_paths(ctx: Context, base: str) -> list[str]:
    return [l for l in _git(ctx, "diff", "--name-only", f"{base}...HEAD").splitlines() if l]


# ─────────────────────────── validación ───────────────────────────
def validate(ctx: Context, *, base: str | None = None, pr_number: int | None = None,
             run_acceptance: bool = False, approvers: set[str] | None = None,
             timeout: int | None = None) -> tuple[list[Finding], list[Task]]:
    """Valida esquema, ubicación, cuerpo, dependencias y (con base) transiciones y aceptación."""
    findings: list[Finding] = []
    tasks = load_worktree(ctx)
    active_dir, completed_dir = _dirs(ctx)
    validator = ctx.standard.validator("task")
    timeout = timeout or ((ctx.manifest or {}).get("tasks") or {}).get("acceptance_timeout", 600)

    def f(rule, msg, remedy, path):
        findings.append(_finding(ctx, rule, msg, remedy, path))

    ids: dict[str, str] = {}
    for t in tasks:
        for e in t.errors:
            f("tasks.schema", f"{t.path}: {e}.", "Empieza el archivo con un frontmatter YAML válido (ver _plantilla-tarea.md).", t.path)
        if t.errors:
            continue
        for err in validator.iter_errors(t.meta):
            loc = "/".join(map(str, err.absolute_path)) or "(raíz)"
            f("tasks.schema", f"{t.path}: `{loc}`: {err.message}", "Ajusta el frontmatter a schemas/task.schema.json.", t.path)
        name = Path(t.path).name
        m = TASK_FILE.match(name)
        if not m:
            f("tasks.naming", f"{t.path}: el nombre no sigue `T-NNNN-<slug>.md`.", "Renombra el archivo (slug en minúsculas con guiones).", t.path)
        elif t.id and m.group(1) != t.id:
            f("tasks.naming", f"{t.path}: el id `{t.id}` no coincide con el nombre del archivo.", "Usa el mismo T-NNNN en el nombre y en `id`.", t.path)
        if t.id in ids:
            f("tasks.unique", f"{t.path}: id `{t.id}` duplicado (también en {ids[t.id]}).", "Asigna el siguiente número libre.", t.path)
        elif t.id:
            ids[t.id] = t.path
        folder = str(Path(t.path).parent)
        want = completed_dir if t.status in TERMINAL else active_dir
        if t.status and folder != want:
            f("tasks.location", f"{t.path}: estado `{t.status}` debe estar en `{want}/`.", f"Mueve el archivo a `{want}/`.", t.path)
        present = anchors_in(t.body)
        missing = [a for a in BODY_ANCHORS if a not in present]
        if t.status == "done":
            missing += [a for a in DONE_ANCHORS if not section(t.body, a)]
        if missing:
            f("tasks.body", f"{t.path}: faltan (o están vacías) las secciones {', '.join(missing)}.",
              "Añade las anclas <!-- harness:… --> de la plantilla de tarea y su contenido.", t.path)
        for ac in t.meta.get("acceptance") or []:
            if ac.get("check") == "manual" and t.status == "done" and not ac.get("verified_by"):
                f("tasks.acceptance", f"{t.path}: criterio {ac.get('id')} es manual y no tiene `verified_by`.",
                  "Indica la persona que lo verificó; debe haber aprobado el PR.", t.path)
    for t in tasks:
        for dep in t.meta.get("depends_on") or []:
            if dep not in ids:
                f("tasks.depends", f"{t.path}: depende de `{dep}`, que no existe.", "Corrige la dependencia o crea la tarea.", t.path)

    if base is not None:
        before = load_at_ref(ctx, base)
        for t in tasks:
            if not t.id or t.errors:
                continue
            old = before.get(t.id)
            old_status = old.status if old else None
            if t.status != old_status and t.status not in ALLOWED.get(old_status, set()):
                f("tasks.transition", f"{t.path}: transición `{old_status or '(nueva)'}` → `{t.status}` no permitida.",
                  f"Transiciones válidas desde `{old_status or '(nueva)'}`: {', '.join(sorted(ALLOWED.get(old_status, set()))) or 'ninguna'}.", t.path)
            if t.status == "done" and old_status != "done":
                if pr_number is not None and t.meta.get("done_pr") != pr_number:
                    f("tasks.done-pr", f"{t.path}: `done_pr` = {t.meta.get('done_pr')} pero este PR es #{pr_number}.",
                      f"Pon `done_pr: {pr_number}`.", t.path)
                for ac in t.meta.get("acceptance") or []:
                    if ac.get("check") == "manual":
                        who = (ac.get("verified_by") or "").lstrip("@").lower()
                        if approvers is not None and who and who not in approvers:
                            f("tasks.acceptance", f"{t.path}: {ac['id']} verificado por @{who}, que no ha aprobado este PR.",
                              "La persona en `verified_by` debe aprobar el PR.", t.path)
                    elif run_acceptance:
                        code, tail = _run(ctx, ac["check"], timeout)
                        if code != 0:
                            f("tasks.acceptance", f"{t.path}: {ac['id']} (`{ac['check']}`) terminó con código {code}. {tail}",
                              "La tarea no puede marcarse done hasta que todos sus criterios pasen en CI (ADR-016).", t.path)
        for tid, old in before.items():
            if tid not in ids:
                f("tasks.deleted", f"La tarea `{tid}` ({old.path}) se ha borrado.",
                  "Las tareas no se borran: usa `status: cancelled` y muévela a completed/.", old.path)
    return findings, tasks


def _run(ctx: Context, cmd: str, timeout: int) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, shell=True, cwd=ctx.root, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=timeout)
        return p.returncode, " | ".join((p.stdout + p.stderr).strip().splitlines()[-5:])
    except subprocess.TimeoutExpired:
        return 124, f"tiempo agotado ({timeout}s)"


# ─────────────────────────── índice ───────────────────────────
def render_index(tasks: list[Task]) -> str:
    rows = [INDEX_HEADER, "", "# Índice de tareas", "",
            "| Id | Título | Estado | Riesgo | Responsable | Segmentos | Issue | Archivo |",
            "|---|---|---|---|---|---|---|---|"]
    for t in sorted((t for t in tasks if t.id), key=lambda t: t.id):
        m = t.meta
        issue = f"#{m['issue']}" if m.get("issue") else "—"
        rel = "/".join(Path(t.path).parts[-2:])
        rows.append(f"| {t.id} | {m.get('title', '')} | {m.get('status', '')} | {m.get('risk', '')} | {m.get('owner', '')} | "
                    f"{', '.join(m.get('segments') or []) or '—'} | {issue} | [{Path(t.path).name}]({rel}) |")
    return "\n".join(rows) + "\n"


# ─────────────────────────── cierre (P-4, D-044) ───────────────────────────
class CloseError(Exception):
    """Precondición de `harness tasks close` no cumplida: no se ha modificado nada."""


def _section_re(anchor: str) -> re.Pattern:
    return re.compile(rf"(<!--\s*harness:{re.escape(anchor)}\s*-->)(.*?)(?=<!--\s*harness:[a-z0-9-]+\s*-->|\Z)", re.S)


def _replace_section(body: str, anchor: str, heading: str, text: str) -> str:
    m = _section_re(anchor).search(body)
    new = f"\n## {heading}\n{text.strip()}\n"
    if not m:
        return body.rstrip("\n") + f"\n\n<!-- harness:{anchor} -->{new}"
    tail = "\n" if m.end() < len(body) else ""
    return body[:m.start(2)] + new + tail + body[m.end():]


def _append_to_section(body: str, anchor: str, line: str) -> str:
    m = _section_re(anchor).search(body)
    if not m:
        raise CloseError(f"la tarea no tiene la sección `{anchor}`")
    rest = body[m.end():]
    sep = "\n\n" if rest else "\n"
    return body[:m.start(2)] + m.group(2).rstrip("\n") + "\n" + line + sep + rest


def _set_front(front: str, key: str, value: str, after: str) -> str:
    line = re.compile(rf"(?m)^{key}:.*$")
    if line.search(front):
        return line.sub(f"{key}: {value}", front, count=1)
    return re.sub(rf"(?m)^({after}:.*)$", lambda mm: f"{mm.group(1)}\n{key}: {value}", front, count=1)


def close(ctx: Context, task_id: str, pr: int, *, resultado: str | None = None,
          verified_by: str | None = None, autor: str | None = None,
          today: dt.date | None = None) -> list[str]:
    """Lleva una tarea a `done` de forma determinista (ADR-016). Devuelve las rutas modificadas.

    No ejecuta criterios de aceptación, ni crea el PR, ni hace commit. Si una precondición
    falla, lanza CloseError sin escribir nada. Es idempotente con el mismo PR.
    """
    if not isinstance(pr, int) or pr <= 0:
        raise CloseError("--pr debe ser un entero positivo")
    tasks = [t for t in load_worktree(ctx) if t.id == task_id]
    if not tasks:
        raise CloseError(f"no existe la tarea {task_id}")
    if len(tasks) > 1:
        raise CloseError(f"{task_id} aparece en varios archivos: {', '.join(t.path for t in tasks)}")
    t = tasks[0]
    if t.errors:
        raise CloseError(f"{t.path}: {t.errors[0]}")
    _, completed_dir = _dirs(ctx)
    if t.status == "done":
        if t.meta.get("done_pr") == pr and str(Path(t.path).parent) == completed_dir:
            return []
        raise CloseError(f"{task_id} ya está en done con done_pr={t.meta.get('done_pr')}")
    if "done" not in ALLOWED.get(t.status, set()):
        origen = ", ".join(sorted(k for k, v in ALLOWED.items() if k and "done" in v))
        raise CloseError(f"{task_id} está en `{t.status}`; solo se cierra desde {origen}")
    manual = [ac for ac in t.meta.get("acceptance") or [] if ac.get("check") == "manual"]
    if any(not ac.get("verified_by") for ac in manual) and not verified_by:
        raise CloseError("hay criterios manuales sin `verified_by`: indica --verified-by @persona (debe aprobar el PR)")
    if not resultado and not section(t.body, "resultado"):
        raise CloseError('la sección Resultado está vacía: indica --resultado "…"')

    text = (ctx.root / t.path).read_text(encoding="utf-8")
    m = FRONT.match(text)
    front, body = m.group(1), text[m.end():]
    front = _set_front(front, "status", "done", "status")
    front = _set_front(front, "done_pr", str(pr), "status")
    if verified_by:
        who = verified_by if verified_by.startswith("@") else f"@{verified_by}"
        front = re.sub(r"(?m)^(\s+)check:\s*[\"']?manual[\"']?\s*$(?!\n\s+verified_by:)",
                       lambda mm: f'{mm.group(0)}\n{mm.group(1)}verified_by: "{who}"', front)
    day = (today or dt.date.today()).isoformat()
    quien = autor or t.meta.get("owner") or "—"
    body = _append_to_section(body, "progreso", f"- {day} — cerrada en el PR #{pr} — {quien}")
    if resultado:
        body = _replace_section(body, "resultado", "Resultado", resultado)
    new_text = f"---\n{front}\n---\n{body}"

    nt = parse_task(new_text, t.path)
    errs = nt.errors + [e.message for e in ctx.standard.validator("task").iter_errors(nt.meta)]
    if errs:
        raise CloseError(f"el resultado no valida contra task.schema.json: {errs[0]}")

    dest = f"{completed_dir}/{Path(t.path).name}"
    (ctx.root / dest).parent.mkdir(parents=True, exist_ok=True)
    (ctx.root / dest).write_text(new_text, encoding="utf-8")
    changed = [dest]
    if dest != t.path:
        (ctx.root / t.path).unlink()
        changed.insert(0, t.path)
    idx = ctx.role_path("plans.index")
    _, found = validate(ctx)
    (ctx.root / idx).parent.mkdir(parents=True, exist_ok=True)
    (ctx.root / idx).write_text(render_index(found), encoding="utf-8")
    return changed + [idx]


# ─────────────────────────── PR ───────────────────────────
def _matches_any(patterns: list[str], path: str) -> bool:
    return any(compile_pattern(p, codeowners=True).match(path) for p in patterns)


def _requirement_applies(ctx: Context, req_id: str) -> bool:
    """El requisito existe y su `desde` ≤ la versión declarada en el manifiesto (D-029)."""
    from .standard import semver
    req = ctx.standard.requirements.get(req_id)
    declared = semver(ctx.declared_version) if ctx.declared_version else None
    return bool(req) and declared is not None and (semver(req["desde"]) or (0, 0, 0)) <= declared


def check_pr(ctx: Context, body: str, base: str, *, title: str = "") -> list[Finding]:
    """Comprueba el cuerpo del PR contra el diff y las tareas (pr.template, D-023)."""
    findings: list[Finding] = []

    def f(rule, msg, remedy, severity=None):
        findings.append(_finding(ctx, rule, msg, remedy, None, severity))

    paths = changed_paths(ctx, base)
    sensitive = [p for p in paths if _matches_any(ctx.standard.sensitive_patterns, p)]
    tarea = section(body, "tarea")
    riesgo = section(body, "riesgo").lower()
    sens = section(body, "sensible").lower()
    for anchor, val in (("tarea", tarea), ("riesgo", riesgo), ("sensible", sens)):
        if not val:
            f("pr.anchors", f"El cuerpo del PR no tiene la sección `harness:{anchor}` (o está vacía).",
              "Usa la plantilla de PR sin borrar las anclas <!-- harness:… -->.")
    m_r = re.search(r"\b(bajo|medio|alto)\b", re.sub(r"bajo\s*\|\s*medio\s*\|\s*alto", "", riesgo))
    if riesgo and not m_r:
        f("pr.risk", "La clase de riesgo no es `bajo`, `medio` ni `alto` (deja solo una).", "Escribe una única clase de riesgo.")
    declared_sensitive = None
    if sens:
        clean = re.sub(r"no\s*\|\s*sí", "", sens)
        if re.search(r"\bs[ií]\b", clean):
            declared_sensitive = True
        elif re.search(r"\bno\b", clean):
            declared_sensitive = False
        else:
            f("pr.sensitive", "La sección `sensible` debe decir `sí` o `no` (deja solo una).", "Elige `sí` o `no`.")
    if sensitive and declared_sensitive is False:
        f("pr.sensitive", f"El PR declara `sensible: no` pero toca rutas sensibles: {', '.join(sensitive[:5])}.",
          "Declara `sí` y describe el cambio; requiere revisión de plataforma/seguridad (ADR-013).")
    if sensitive and m_r and m_r.group(1) == "bajo" and not _requirement_applies(ctx, "HS-CI-005"):
        f("pr.risk-sensitive", "Un PR que toca rutas sensibles no debería declararse de riesgo `bajo`.",
          "Usa al menos `medio`.", severity="warning")

    if m_r and _requirement_applies(ctx, "HS-CI-005"):
        from .risk import compute, rank
        calc = compute(ctx, base)
        if rank(m_r.group(1)) < rank(calc.clase):
            motivos = "; ".join(m for c, m in calc.senales if c == calc.clase)[:300]
            f("pr.risk-min", f"Riesgo declarado `{m_r.group(1)}` menor que el calculado `{calc.clase}` ({motivos}).",
              f"Declara al menos `{calc.clase}`. Puedes subir la clase, no bajarla (D-058). Detalle: `harness pr risk --base <ref>`.")

    is_revert = bool(re.search(r"^\s*Reverts\s+#\d+", body, re.M)) or title.startswith("Revert")
    task_ids = re.findall(r"\bT-\d{4}\b", tarea)
    is_trivial = bool(re.search(r"\btrivial\b", tarea.lower())) and not task_ids
    if is_trivial:
        allowed = ((ctx.manifest or {}).get("tasks") or {}).get("trivial_paths") or ctx.standard.trivial_patterns
        bad = [p for p in paths if p in sensitive or not _matches_any(allowed, p)]
        if bad and not is_revert:
            f("pr.trivial", f"PR `trivial` que toca rutas no permitidas para trivial: {', '.join(bad[:5])}.",
              "Crea un archivo de tarea y referéncialo (`T-NNNN`), o limita el PR a documentación o lockfiles (D-023).")
    elif tarea and not task_ids and not is_revert:
        f("pr.task", "La sección `tarea` no contiene un `T-NNNN` ni `trivial`.", "Referencia la tarea o declara `trivial` con su motivo.")
    else:
        tasks = {t.id: t for t in load_worktree(ctx) if t.id}
        for tid in task_ids:
            t = tasks.get(tid)
            if t is None:
                f("pr.task", f"La tarea `{tid}` no existe en el repositorio.", "Crea el archivo de tarea en plans.active o corrige el id.")
                continue
            if t.path not in paths:
                f("pr.task", f"El PR no actualiza `{t.path}` (progreso/decisiones de la tarea).",
                  "Registra el progreso en el archivo de tarea en el mismo PR.", severity="warning")
            issue = t.meta.get("issue")
            if issue and t.status == "done" and not re.search(rf"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s*:?\s*#{issue}\b", body, re.I):
                f("pr.issue", f"La tarea `{tid}` pasa a done y tiene `issue: {issue}`, pero el PR no incluye `Closes #{issue}`.",
                  f"Añade `Closes #{issue}` al cuerpo del PR (X-01).")
    findings += adr_immutable(ctx, base, paths)
    return findings


ADR_FILE = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ADR_MUTABLE_KEYS = {"estado", "reemplazada_por"}


def adr_immutable(ctx: Context, base: str, paths: list[str]) -> list[Finding]:
    """Un ADR `aceptada` en la base solo cambia `estado`/`reemplazada_por` (C-15, HS-ARC-006)."""
    out = []
    ddir = ctx.role_path("decisions.dir").rstrip("/")
    for p in paths:
        if Path(p).parent.as_posix() != ddir or not ADR_FILE.match(Path(p).name):
            continue
        try:
            old = parse_task(_git(ctx, "show", f"{base}:{p}"), p)
        except subprocess.CalledProcessError:
            continue  # ADR nuevo
        if old.errors or old.meta.get("estado") != "aceptada":
            continue
        cur = ctx.root / p
        if not cur.is_file():
            out.append(_finding(ctx, "pr.adr-immutable", f"Se ha borrado el ADR aceptado {p}.",
                                "Un ADR aceptado no se borra: márcalo `reemplazada` o `deprecada` y crea uno nuevo.", p))
            continue
        new = parse_task(cur.read_text(encoding="utf-8"), p)
        strip = lambda m: {k: v for k, v in m.items() if k not in ADR_MUTABLE_KEYS}
        norm = lambda s: re.sub(r"\s+", " ", s).strip()
        if new.errors or strip(new.meta) != strip(old.meta) or norm(new.body) != norm(old.body):
            out.append(_finding(ctx, "pr.adr-immutable", f"{p} estaba `aceptada` y su contenido ha cambiado.",
                                "No reescribas un ADR aceptado: crea uno nuevo que lo reemplace (`reemplaza`) y cambia aquí solo `estado` y `reemplazada_por`.", p))
    return out


# ─────────────────────────── espejo en issues (X-01) ───────────────────────────
STATUS_LABEL = "status:"


def plan_issue_sync(ctx: Context, base: str | None, run_url: str = "") -> list[dict]:
    """Operaciones para reflejar en las issues las tareas cambiadas desde `base` (dirección única archivo → issue)."""
    tasks = {t.id: t for t in load_worktree(ctx) if t.id and not t.errors}
    before = load_at_ref(ctx, base) if base else {}
    ops: list[dict] = []
    for tid, t in sorted(tasks.items()):
        issue = t.meta.get("issue")
        if not isinstance(issue, int):
            continue
        old = before.get(tid)
        if old is not None and old.meta == t.meta:
            continue  # sin cambios en el frontmatter
        owner = str(t.meta.get("owner", ""))
        ops.append({"op": "set-status", "issue": issue, "task": tid, "status": t.status,
                    "assignee": owner.lstrip("@") if owner.startswith("@") and "/" not in owner else None})
        if t.status == "done" and (old is None or old.status != "done"):
            ops.append({"op": "comment", "issue": issue, "task": tid,
                        "body": (f"✅ `{tid}` pasa a **done** (verificado por `harness tasks` en el PR #{t.meta.get('done_pr')}, ADR-016)."
                                 + (f" Ejecución: {run_url}" if run_url else ""))})
    return ops


def apply_issue_ops(ops: list[dict], repo: str, token: str, api: str = "https://api.github.com") -> list[str]:
    """Aplica las operaciones con la API REST de GitHub. Devuelve un registro legible."""
    import json
    import urllib.error
    import urllib.request

    def call(method: str, path: str, payload: dict | None = None):
        req = urllib.request.Request(f"{api}/repos/{repo}{path}", method=method,
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                              "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (URL fija de la API)
                body = r.read()
                return r.status, json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            return e.code, None

    log = []
    for op in ops:
        n = op["issue"]
        if op["op"] == "set-status":
            label = f"{STATUS_LABEL}{op['status']}"
            call("POST", "/labels", {"name": label, "color": "ededed"})  # 422 si ya existe
            code, issue = call("GET", f"/issues/{n}")
            if code != 200 or issue is None:
                log.append(f"#{n}: no accesible (HTTP {code}); se omite")
                continue
            keep = [l["name"] for l in issue.get("labels", []) if not l["name"].startswith(STATUS_LABEL)]
            call("PUT", f"/issues/{n}/labels", {"labels": keep + [label]})
            if op.get("assignee"):
                call("POST", f"/issues/{n}/assignees", {"assignees": [op["assignee"]]})
            log.append(f"#{n}: {op['task']} → {label}" + (f", asignada a @{op['assignee']}" if op.get("assignee") else ""))
        elif op["op"] == "comment":
            call("POST", f"/issues/{n}/comments", {"body": op["body"]})
            log.append(f"#{n}: comentario de evidencia")
    return log
