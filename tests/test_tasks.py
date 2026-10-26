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
    assert "pr.risk-sensitive" in rules(f, "warning")


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


def test_pr_riesgo_invalido(repo):
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/architecture/ARCHITECTURE.md", "# cambio\n")
    commit(repo)
    assert "pr.risk" in rules(T.check_pr(ctx(repo), pr(tarea="trivial — doc", riesgo="enorme"), base))


# ─────────────── ADR aceptado inmutable (HS-ARC-006) ───────────────
ADR = "---\nid: ADR-0002\ntitulo: Usar céntimos\nestado: {estado}\nfecha: 2026-10-01\ndecisores: [\"@ana\"]\n{extra}---\n\n## Decisión\n{decision}\n"


def test_adr_aceptado_reescrito_avisa(repo):
    write(repo, "docs/decisions/0002-centimos.md", ADR.format(estado="aceptada", extra="", decision="Enteros."))
    commit(repo)
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/decisions/0002-centimos.md", ADR.format(estado="aceptada", extra="", decision="Decimal."))
    commit(repo)
    f = T.check_pr(ctx(repo), pr(tarea="trivial — doc"), base)
    assert "pr.adr-immutable" in rules(f, "warning")


def test_adr_aceptado_solo_cambia_estado(repo):
    write(repo, "docs/decisions/0002-centimos.md", ADR.format(estado="aceptada", extra="", decision="Enteros."))
    commit(repo)
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/decisions/0002-centimos.md",
          ADR.format(estado="reemplazada", extra="reemplazada_por: ADR-0003\n", decision="Enteros."))
    commit(repo)
    f = T.check_pr(ctx(repo), pr(tarea="trivial — doc"), base)
    assert "pr.adr-immutable" not in rules(f, "warning")


# ─────────────── harness tasks close (P-4, D-044) ───────────────
ACTIVE = "docs/plans/active/T-0001-x.md"
DONE = "docs/plans/completed/T-0001-x.md"


def test_close_lleva_a_done_y_pasa_la_validacion_del_pr(repo):
    write(repo, ACTIVE, task_text(status="in_progress"))
    commit(repo)
    c = ctx(repo)
    changed = T.close(c, "T-0001", 7, resultado="Logrado: x.", autor="@ana", today=dt.date(2026, 10, 23))
    assert changed == [ACTIVE, DONE, "docs/plans/INDEX.md"]
    assert not (repo / ACTIVE).exists()
    text = (repo / DONE).read_text(encoding="utf-8")
    assert "status: done\ndone_pr: 7\n" in text
    assert "- 2026-10-23 — cerrada en el PR #7 — @ana" in text
    assert T.section(T.parse_task(text, DONE).body, "resultado") == "## Resultado\nLogrado: x."
    findings, _ = T.validate(ctx(repo), base="HEAD", pr_number=7, run_acceptance=True)
    assert rules(findings) == []
    assert "| T-0001 |" in (repo / "docs/plans/INDEX.md").read_text(encoding="utf-8")


def test_close_es_idempotente_con_el_mismo_pr_y_rechaza_otro(repo):
    write(repo, ACTIVE, task_text(status="in_progress", resultado="Hecho."))
    c = ctx(repo)
    T.close(c, "T-0001", 7)
    antes = (repo / DONE).read_text(encoding="utf-8")
    assert T.close(ctx(repo), "T-0001", 7) == []
    assert (repo / DONE).read_text(encoding="utf-8") == antes
    with pytest.raises(T.CloseError, match="done_pr=7"):
        T.close(ctx(repo), "T-0001", 8)


@pytest.mark.parametrize("status,kwargs,match", [
    ("ready", {"resultado": "x"}, "solo se cierra desde"),
    ("in_progress", {}, "Resultado está vacía"),
    ("in_progress", {"resultado": "x", "pr": 0}, "entero positivo"),
])
def test_close_precondiciones_sin_efectos(repo, status, kwargs, match):
    write(repo, ACTIVE, task_text(status=status))
    antes = (repo / ACTIVE).read_text(encoding="utf-8")
    pr = kwargs.pop("pr", 7)
    with pytest.raises(T.CloseError, match=match):
        T.close(ctx(repo), "T-0001", pr, **kwargs)
    assert (repo / ACTIVE).read_text(encoding="utf-8") == antes
    assert not (repo / DONE).exists() and not (repo / "docs/plans/INDEX.md").exists()


def test_close_tarea_inexistente(repo):
    with pytest.raises(T.CloseError, match="no existe"):
        T.close(ctx(repo), "T-0009", 7)


def test_close_criterio_manual_exige_verified_by(repo):
    write(repo, ACTIVE, task_text(status="in_review", check="manual", resultado="Hecho."))
    with pytest.raises(T.CloseError, match="verified-by"):
        T.close(ctx(repo), "T-0001", 7)
    T.close(ctx(repo), "T-0001", 7, verified_by="luis")
    meta = T.parse_task((repo / DONE).read_text(encoding="utf-8"), DONE).meta
    assert meta["acceptance"][0]["verified_by"] == "@luis"
    findings, _ = T.validate(ctx(repo))
    assert rules(findings) == []


def test_close_cli(repo, capsys):
    from harness_cli.cli import main
    write(repo, ACTIVE, task_text(status="in_progress"))
    assert main(["tasks", "close", "T-0001", "--pr", "7", "--path", str(repo)]) == 2
    assert "No se ha modificado nada" in capsys.readouterr().err
    assert main(["tasks", "close", "T-0001", "--pr", "7", "--resultado", "Hecho.", "--path", str(repo)]) == 0
    assert DONE in capsys.readouterr().out


# ─────────────── Riesgo calculado (D-058, HS-CI-005) ───────────────
from harness_cli import risk as R  # noqa: E402

PR_BODY = """<!-- harness:tarea -->
**Tarea:** {tarea}
<!-- harness:riesgo -->
**Riesgo:** {riesgo} — prueba
<!-- harness:sensible -->
**¿Toca configuración de agentes, CI o seguridad?** {sens}
"""


def _v06(root):
    p = root / ".harness/manifest.yaml"
    p.write_text(p.read_text(encoding="utf-8").replace("version: 0.1.0", "version: 0.6.0"), encoding="utf-8")


@pytest.mark.parametrize("cambios,esperado,motivo", [
    ({"docs/guia.md": "x"}, "bajo", "sin señales"),
    ({"src/app.py": "print(1)\n"}, "bajo", "sin señales"),
    ({"CLAUDE.md": "@AGENTS.md\nmás\n"}, "medio", "configuración de agentes"),
    ({".github/workflows/x.yml": "name: x\n"}, "alto", "ruta crítica"),
    ({".harness/manifest.yaml": None}, "alto", "ruta crítica"),
])
def test_riesgo_por_rutas(repo, cambios, esperado, motivo):
    for rel, text in cambios.items():
        if text is None:
            p = repo / rel
            p.write_text(p.read_text(encoding="utf-8") + "# cambio\n", encoding="utf-8")
        else:
            write(repo, rel, text)
    commit(repo)
    r = R.compute(ctx(repo), "HEAD~1")
    assert r.clase == esperado and any(motivo in m for _, m in r.senales), r.senales


def test_riesgo_prueba_borrada_y_rutas_criticas_del_manifiesto(repo):
    write(repo, "tests/test_x.py", "def test_x(): pass\n")
    write(repo, "deploy/main.tf", "x\n")
    commit(repo, "base2")
    (repo / "tests/test_x.py").unlink()
    commit(repo)
    assert R.compute(ctx(repo), "HEAD~1").clase == "medio"
    p = repo / ".harness/manifest.yaml"
    p.write_text(p.read_text(encoding="utf-8") + "riesgo:\n  rutas_criticas: [/deploy/]\n", encoding="utf-8")
    commit(repo, "manifest")
    write(repo, "deploy/main.tf", "y\n")
    commit(repo)
    r = R.compute(ctx(repo), "HEAD~1")
    assert r.clase == "alto" and any("deploy/main.tf" in m for _, m in r.senales)


def test_riesgo_tarea_que_se_cierra(repo):
    write(repo, ACTIVE, task_text(status="in_progress", extra=""))
    commit(repo, "tarea")
    T.close(ctx(repo), "T-0001", 7, resultado="Hecho.")
    text = (repo / DONE).read_text(encoding="utf-8").replace('check: "true"', 'check: "true # debilitado"').replace("risk: bajo", "risk: alto")
    (repo / DONE).write_text(text, encoding="utf-8")
    commit(repo)
    r = R.compute(ctx(repo), "HEAD~1")
    motivos = " ".join(m for _, m in r.senales)
    assert r.clase == "alto" and "K-14" in motivos and "risk: alto" in motivos


def test_pr_risk_min_solo_desde_0_6(repo):
    write(repo, ".github/workflows/x.yml", "name: x\n")
    write(repo, ACTIVE, task_text(status="in_progress"))
    commit(repo)
    body = PR_BODY.format(tarea="T-0001", riesgo="bajo", sens="sí")
    assert "pr.risk-min" not in rules(T.check_pr(ctx(repo), body, "HEAD~1"))   # 0.1.0: no aplica (D-029)
    _v06(repo)
    commit(repo, "v06")
    assert "pr.risk-min" in rules(T.check_pr(ctx(repo), body, "HEAD~2"))
    ok = PR_BODY.format(tarea="T-0001", riesgo="alto", sens="sí")
    assert "pr.risk-min" not in rules(T.check_pr(ctx(repo), ok, "HEAD~2"))


def test_pr_risk_cli(repo, capsys, monkeypatch, tmp_path):
    from harness_cli.cli import main
    write(repo, ".github/CODEOWNERS", "* @x\n")
    commit(repo)
    out = tmp_path / "gh_out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    assert main(["pr", "risk", "--base", "HEAD~1", "--path", str(repo), "--github-output"]) == 0
    assert "Riesgo calculado: alto" in capsys.readouterr().out
    assert out.read_text() == "clase=alto\n"
