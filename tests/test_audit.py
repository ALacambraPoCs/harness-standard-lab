"""harness audit (F5.6-B, D-073): rastro de auditoría con git real y API simulada (sin red)."""
import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from harness_cli import audit as A
from harness_cli import cli
from harness_cli.context import Context
from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[1]
BASE_FIXTURE = ROOT / "tests" / "fixtures" / "conforming" / "n0-basico"
STD = load_standard()

TASK = ("---\nid: T-0001\ntitle: Tarea de prueba\nowner: \"@ana\"\nstatus: {status}\nrisk: bajo\ncreated: 2026-10-21\n"
        "{extra}acceptance:\n  - id: AC1\n    description: El check pasa\n    check: \"true\"\n---\n"
        "<!-- harness:objetivo -->\nx\n<!-- harness:alcance -->\nx\n<!-- harness:plan -->\nx\n"
        "<!-- harness:progreso -->\nx\n<!-- harness:decisiones -->\nx\n<!-- harness:resultado -->\n{res}\n")

BODY = ("<!-- harness:tarea -->\n**Tarea:** T-0001\n<!-- harness:riesgo -->\n**Riesgo:** {riesgo} — prueba\n"
        "<!-- harness:sensible -->\n**¿Toca configuración?** sí\n\n**Origen del cambio:** {origen}\n")


def git(root, *args):
    return subprocess.run(["git", "-c", "user.email=ana@x", "-c", "user.name=Ana", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """main ← merge --no-ff de una rama que toca un workflow (ruta crítica) y cierra T-0001."""
    root = tmp_path / "repo"
    shutil.copytree(BASE_FIXTURE, root)
    (root / "docs/plans/active").mkdir(parents=True)
    (root / "docs/plans/completed").mkdir(parents=True)
    (root / "docs/plans/active/T-0001-prueba.md").write_text(TASK.format(status="in_progress", extra="", res=""), encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    git(root, "switch", "-qc", "rama")
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows/nuevo.yml").write_text("name: x\non: push\npermissions: {}\njobs: {}\n", encoding="utf-8")
    (root / "docs/plans/active/T-0001-prueba.md").unlink()
    (root / "docs/plans/completed/T-0001-prueba.md").write_text(
        TASK.format(status="done", extra="done_pr: 7\n", res="hecho"), encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "T-0001: cambio\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    git(root, "switch", "-q", "main")
    git(root, "merge", "-q", "--no-ff", "rama", "-m", "Merge pull request #7")
    return root


def ctx(root):
    return Context.build(root, STD, dt.date(2026, 10, 28))


def fake(sha, *, riesgo="alto", origen="agente (Claude Code 2.1) a nombre de @ana", aprobado=True,
         conclusion="success", pr=True, deploy=True):
    pull = {"number": 7, "title": "T-0001 <b>@equipo</b>", "html_url": "https://x/pull/7", "merged": True,
            "merged_at": "2026-10-28T10:00:00Z", "merge_commit_sha": sha, "user": {"login": "ana"},
            "merged_by": {"login": "ana"}, "head": {"sha": "h" * 40}, "base": {"ref": "main"},
            "body": BODY.format(riesgo=riesgo, origen=origen)}
    api = {
        f"/repos/o/r/commits/{sha}/pulls": [pull] if pr else [],
        "/repos/o/r/pulls/7": pull,
        "/repos/o/r/pulls/7/commits?per_page=100": [{"commit": {"message": "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"}}],
        f"/repos/o/r/commits/{'h' * 40}/check-runs?per_page=100": {"check_runs": [
            {"name": "conformance / harness check", "status": "completed", "conclusion": conclusion, "html_url": "u"}]},
        f"/repos/o/r/actions/runs?head_sha={'h' * 40}&per_page=100": {"workflow_runs": [
            {"id": 11, "name": "harness-tasks", "html_url": "https://x/runs/11"}]},
        "/repos/o/r/actions/runs/11/approvals": [
            {"state": "approved" if aprobado else "rejected", "comment": "ok @jefe", "user": {"login": "ana"},
             "environments": [{"name": "aprobacion-riesgo-alto"}]}],
        f"/repos/o/r/deployments?sha={sha}&per_page=100": [
            {"id": 5, "environment": "github-pages", "created_at": "2026-10-28T10:05:00Z", "creator": {"login": "github-actions[bot]"}}] if deploy else [],
        "/repos/o/r/deployments/5/statuses?per_page=1": [{"state": "success", "environment_url": "https://o.github.io/r/"}],
    }

    def fetch(path):
        return (200, api[path]) if path in api else (404, None)
    return fetch


def test_rastro_completo_sin_alertas(repo):
    sha = git(repo, "rev-parse", "HEAD")
    a = A.audit(ctx(repo), "HEAD", "o/r", fake(sha), platform=False)
    assert a.sha == sha and a.pr["numero"] == 7 and a.pr["fusionado_por"] == "ana"
    assert a.tareas == [{"id": "T-0001", "estado": "done", "ruta": "docs/plans/completed/T-0001-prueba.md",
                         "done_pr": 7, "criterios": 1}]
    assert a.riesgo["calculada"] == "alto" and a.riesgo["efectiva"] == "alto"
    assert any("ruta crítica: .github/workflows/nuevo.yml" in s for s in a.riesgo["senales"])
    assert a.origen["agente"] is True
    assert a.aprobaciones[0]["estado"] == "approved" and a.despliegues[0]["estado"] == "success"
    assert a.alertas == []
    md = A.to_markdown(a)
    assert "**Alertas:** 0 ✅" in md and "<b>" not in md and "@equipo" not in md and "@​equipo" in md


def test_por_numero_de_pr(repo):
    sha = git(repo, "rev-parse", "HEAD")
    assert A.audit(ctx(repo), "#7", "o/r", fake(sha), platform=False).sha == sha


@pytest.mark.parametrize("kw,alerta", [
    ({"riesgo": "bajo"}, "menor que el recalculado"),
    ({"aprobado": False}, "sin aprobación registrada"),
    ({"conclusion": "failure"}, "no terminó en éxito"),
    ({"origen": "persona"}, "declara origen `persona`"),
    ({"pr": False}, "no llegó por un PR"),
])
def test_alertas(repo, kw, alerta):
    sha = git(repo, "rev-parse", "HEAD")
    a = A.audit(ctx(repo), sha, "o/r", fake(sha, **kw), platform=False)
    assert any(alerta in x for x in a.alertas), a.alertas


def test_pr_no_fusionado(repo):
    def fetch(path):
        return (200, {"number": 8, "merged": False}) if path == "/repos/o/r/pulls/8" else (404, None)
    with pytest.raises(A.AuditError, match="no está fusionado"):
        A.audit(ctx(repo), "#8", "o/r", fetch)


def test_cli_json_y_strict(repo, monkeypatch, capsys):
    sha = git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr("harness_cli.platform.http_fetch", lambda token=None: fake(sha, aprobado=False))
    assert cli.main(["audit", "HEAD", "--path", str(repo), "--repo", "o/r", "--no-platform", "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["riesgo"]["efectiva"] == "alto" and data["alertas"]
    assert cli.main(["audit", "HEAD", "--path", str(repo), "--repo", "o/r", "--no-platform", "--strict"]) == 1


def test_ref_inexistente(repo, capsys):
    assert cli.main(["audit", "noexiste", "--path", str(repo), "--repo", "o/r", "--no-platform"]) == 2
