"""Ciclo de vida de tareas (ADR-005, ADR-016) y comprobación de PR (D-023) sobre repos git temporales."""
import datetime as dt
import shutil
import subprocess
from pathlib import Path

import pytest

from harness_cli import tasks as T
from harness_cli.context import Context
from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[1]
BASE_FIXTURE = ROOT / "tests" / "fixtures" / "conforming" / "n0-basico"
STD = load_standard()

BODY = """
<!-- harness:objetivo -->
Objetivo.
<!-- harness:alcance -->
Dentro: x.
<!-- harness:plan -->
1. Hacer x.
<!-- harness:progreso -->
- [x] 2026-10-21 10:00 — hecho
<!-- harness:decisiones -->
- ninguna
<!-- harness:resultado -->
{resultado}
"""


def task_text(tid="T-0001", status="ready", check="true", extra="", resultado=""):
    return (f"---\nid: {tid}\ntitle: Tarea de prueba {tid}\nowner: \"@ana\"\nstatus: {status}\nrisk: bajo\n"
            f"created: 2026-10-21\n{extra}acceptance:\n  - id: AC1\n    description: El check pasa\n    check: \"{check}\"\n---\n"
            + BODY.format(resultado=resultado))


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(BASE_FIXTURE, root)
    (root / "docs/plans/active").mkdir(parents=True)
    (root / "docs/plans/completed").mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    return root


def commit(root, msg="cambio"):
    git(root, "add", "-A")
    git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", msg)


def ctx(root):
    return Context.build(root, STD, dt.date(2026, 10, 21))


def rules(findings, severity="error"):
    return sorted({f.rule for f in findings if f.severity == severity})


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ─────────────── validación estática ───────────────
def test_tarea_valida(repo):
    write(repo, "docs/plans/active/T-0001-ejemplo.md", task_text())
    f, ts = T.validate(ctx(repo))
    assert rules(f) == [] and len(ts) == 1


@pytest.mark.parametrize("name,text,rule", [
    ("T-0001-ejemplo.md", "sin frontmatter", "tasks.schema"),
    ("T-0001-ejemplo.md", task_text(status="volando"), "tasks.schema"),
    ("t1.md", task_text(), "tasks.naming"),
    ("T-0002-otro.md", task_text(tid="T-0001"), "tasks.naming"),
    ("T-0001-ejemplo.md", task_text(status="done", extra="done_pr: 3\n", resultado="ok"), "tasks.location"),
    ("T-0001-ejemplo.md", task_text(status="done", resultado="ok"), "tasks.schema"),       # falta done_pr
    ("T-0001-ejemplo.md", task_text(status="blocked"), "tasks.schema"),                     # falta blocked_reason
    ("T-0001-ejemplo.md", task_text(extra="depends_on: [T-0099]\n"), "tasks.depends"),
    ("T-0001-ejemplo.md", task_text().replace("<!-- harness:plan -->", ""), "tasks.body"),
])
def test_tarea_invalida(repo, name, text, rule):
    write(repo, f"docs/plans/active/{name}", text)
    f, _ = T.validate(ctx(repo))
    assert rule in rules(f)


def test_done_sin_resultado(repo):
    write(repo, "docs/plans/completed/T-0001-ejemplo.md", task_text(status="done", extra="done_pr: 3\n", resultado=""))
    assert "tasks.body" in rules(T.validate(ctx(repo))[0])


def test_ids_duplicados(repo):
    write(repo, "docs/plans/active/T-0001-a.md", task_text())
    write(repo, "docs/plans/active/T-0001-b.md", task_text())
    assert "tasks.unique" in rules(T.validate(ctx(repo))[0])


# ─────────────── transiciones y aceptación (ADR-016) ───────────────
def _start(repo, status="in_progress", check="true"):
    write(repo, "docs/plans/active/T-0001-ejemplo.md", task_text(status=status, check=check))
    commit(repo, "tarea en curso")
    return git(repo, "rev-parse", "HEAD")


def _to_done(repo, check="true", pr=7):
    (repo / "docs/plans/active/T-0001-ejemplo.md").unlink()
    write(repo, "docs/plans/completed/T-0001-ejemplo.md",
          task_text(status="done", check=check, extra=f"done_pr: {pr}\n", resultado="Hecho."))
    commit(repo, "done")


def test_done_con_aceptacion_que_pasa(repo):
    base = _start(repo)
    _to_done(repo)
    f, _ = T.validate(ctx(repo), base=base, pr_number=7, run_acceptance=True)
    assert rules(f) == []


def test_done_con_aceptacion_que_falla_bloquea(repo):
    base = _start(repo)
    _to_done(repo, check="false")
    f, _ = T.validate(ctx(repo), base=base, pr_number=7, run_acceptance=True)
    assert "tasks.acceptance" in rules(f)


def test_done_pr_distinto(repo):
    base = _start(repo)
    _to_done(repo, pr=99)
    assert "tasks.done-pr" in rules(T.validate(ctx(repo), base=base, pr_number=7)[0])


def test_transicion_ilegal(repo):
    base = _start(repo, status="proposed")
    _to_done(repo)
    assert "tasks.transition" in rules(T.validate(ctx(repo), base=base, pr_number=7, run_acceptance=True)[0])


def test_borrar_tarea_prohibido(repo):
    base = _start(repo)
    (repo / "docs/plans/active/T-0001-ejemplo.md").unlink()
    commit(repo)
    assert "tasks.deleted" in rules(T.validate(ctx(repo), base=base)[0])


def test_criterio_manual_requiere_aprobador(repo):
    base = _start(repo)
    (repo / "docs/plans/active/T-0001-ejemplo.md").unlink()
    text = task_text(status="done", check="manual", extra="done_pr: 7\n", resultado="Hecho.").replace(
        'check: "manual"', 'check: "manual"\n    verified_by: "@luis"')
    write(repo, "docs/plans/completed/T-0001-ejemplo.md", text)
    commit(repo)
    assert "tasks.acceptance" in rules(T.validate(ctx(repo), base=base, pr_number=7, approvers={"ana"})[0])
    assert rules(T.validate(ctx(repo), base=base, pr_number=7, approvers={"luis"})[0]) == []


# ─────────────── índice ───────────────
def test_indice(repo):
    write(repo, "docs/plans/active/T-0002-b.md", task_text(tid="T-0002", extra="issue: 5\n"))
    write(repo, "docs/plans/active/T-0001-a.md", task_text())
    _, ts = T.validate(ctx(repo))
    idx = T.render_index(ts)
    assert idx.startswith(T.INDEX_HEADER)
    assert idx.index("T-0001") < idx.index("T-0002") and "#5" in idx


# ─────────────── PR (pr.template, D-023) ───────────────
PR_OK = """<!-- harness:tarea -->
**Tarea:** {tarea}
<!-- harness:riesgo -->
**Riesgo:** {riesgo} — porque sí
<!-- harness:evidencia -->
- check en verde
<!-- harness:sensible -->
**¿Toca configuración de agentes, CI o seguridad?** {sensible}
"""


def pr(tarea="T-0001", riesgo="bajo", sensible="no"):
    return PR_OK.format(tarea=tarea, riesgo=riesgo, sensible=sensible)


def test_pr_con_tarea(repo):
    base = _start(repo)
    write(repo, "docs/plans/active/T-0001-ejemplo.md", task_text(status="in_review"))
    write(repo, "src/app.py", (repo / "src/app.py").read_text() + "\n")
    commit(repo)
    assert rules(T.check_pr(ctx(repo), pr(), base)) == []


def test_pr_tarea_inexistente(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "src/app.py", (repo / "src/app.py").read_text() + "\n")
    commit(repo)
    assert "pr.task" in rules(T.check_pr(ctx(repo), pr(tarea="T-0042"), base))


def test_pr_trivial_solo_docs(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/architecture/ARCHITECTURE.md", "# cambio\n")
    commit(repo)
    assert rules(T.check_pr(ctx(repo), pr(tarea="trivial — errata"), base)) == []


def test_pr_trivial_que_toca_codigo(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "src/app.py", "x = 1\n")
    commit(repo)
    assert "pr.trivial" in rules(T.check_pr(ctx(repo), pr(tarea="trivial — mini"), base))


def test_pr_revert_exento_de_trivial(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "src/app.py", "x = 1\n")
    commit(repo)
    body = pr(tarea="trivial — revert") + "\nReverts #3\n"
    assert "pr.trivial" not in rules(T.check_pr(ctx(repo), body, base))


def test_pr_sensible_no_declarado(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "AGENTS.md", (repo / "AGENTS.md").read_text() + "\n")
    commit(repo)
    f = T.check_pr(ctx(repo), pr(tarea="trivial — doc", sensible="no"), base)
    assert "pr.sensitive" in rules(f)
    assert "pr.trivial" in rules(f)  # una ruta sensible nunca es trivial


def test_pr_sensible_riesgo_bajo_avisa(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, ".github/workflows/x.yml", "on: push\n")
    commit(repo)
    f = T.check_pr(ctx(repo), pr(tarea="trivial — ci", sensible="sí"), base)
    assert "pr.risk" in rules(f, "warning")


def test_pr_sin_anclas(repo):
    base = git(repo, "rev-parse", "HEAD")
    assert "pr.anchors" in rules(T.check_pr(ctx(repo), "Sin plantilla", base))


def test_pr_done_con_issue_sin_closes(repo):
    base = _start(repo)
    (repo / "docs/plans/active/T-0001-ejemplo.md").unlink()
    write(repo, "docs/plans/completed/T-0001-ejemplo.md",
          task_text(status="done", extra="done_pr: 7\nissue: 12\n", resultado="Hecho."))
    commit(repo)
    assert "pr.issue" in rules(T.check_pr(ctx(repo), pr(), base))
    assert "pr.issue" not in rules(T.check_pr(ctx(repo), pr(tarea="T-0001\nCloses #12"), base))


# ─────────────── X-01 ───────────────
def test_plan_issue_sync(repo):
    write(repo, "docs/plans/active/T-0001-ejemplo.md", task_text(status="in_progress", extra="issue: 12\n"))
    commit(repo)
    base = git(repo, "rev-parse", "HEAD")
    (repo / "docs/plans/active/T-0001-ejemplo.md").unlink()
    write(repo, "docs/plans/completed/T-0001-ejemplo.md",
          task_text(status="done", extra="done_pr: 7\nissue: 12\n", resultado="Hecho."))
    commit(repo)
    ops = T.plan_issue_sync(ctx(repo), base, run_url="https://run")
    assert {o["op"] for o in ops} == {"set-status", "comment"}
    assert ops[0]["status"] == "done" and ops[0]["assignee"] == "ana"
    assert "https://run" in ops[1]["body"]
    assert T.plan_issue_sync(ctx(repo), git(repo, "rev-parse", "HEAD")) == []   # sin cambios
