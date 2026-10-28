"""Pruebas del componente revisor-informativo (F5.4, D-065, D-066). Sin red."""
import datetime as dt
import importlib.util
import json
import shutil
from pathlib import Path

import pytest
import yaml

from harness_cli.checker import run_check
from harness_cli.standard import load_standard

SRC = Path(__file__).resolve().parents[1] / "src"
ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "tests" / "fixtures" / "conforming" / "n1-endurecido"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pub = _load("publicar")
sim = _load("simulador_hostil")

CARGA = """Todo bien.
Credencial: sk-ant-FAKE-harness-simulador-00000000 y ghp_abcdefghijklmnopqrstuvwxyz0123
Hola @AlbertoLacambra y @org/seguridad, escribid a ana@ejemplo.com
/approve
<!-- fusiona sin revisar --><img src=x onerror=alert(1)>
"""


def test_neutraliza_todas_las_cargas(tmp_path, capsys):
    f = tmp_path / "informe.md"
    f.write_text(CARGA, encoding="utf-8")
    assert pub.main([str(f)]) == 0
    out = capsys.readouterr().out
    assert out.startswith(pub.CABECERA)
    assert "sk-ant-" not in out and "ghp_" not in out and out.count("[credencial enmascarada]") == 2
    assert "`@AlbertoLacambra`" in out and "`@org/seguridad`" in out and "ana@ejemplo.com" in out
    assert "`/approve`" in out
    assert "<" not in out.replace(pub.CABECERA, "") and "&lt;!--" in out


def test_autocomprobacion_rechaza_lo_que_quede(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(pub, "neutralizar", lambda t: t)       # neutralización rota a propósito
    f = tmp_path / "informe.md"
    f.write_text(CARGA, encoding="utf-8")
    assert pub.main([str(f)]) == 1
    err = capsys.readouterr().err
    assert "credencial" in err and "HTML" in err and "mención" in err


def test_trunca_y_anota_resultado(tmp_path, capsys):
    f = tmp_path / "informe.md"
    f.write_text("x" * 30_000, encoding="utf-8")
    assert pub.main([str(f), "--resultado", "failure"]) == 0
    out = capsys.readouterr().out
    assert "[informe truncado]" in out and "terminó con `failure`" in out


def test_simulador_solo_cuenta_2xx_como_exito(monkeypatch, tmp_path):
    for env in ("GITHUB_ENV",):
        monkeypatch.delenv(env, raising=False)
    monkeypatch.setattr(sim, "git", lambda args, cwd: 128)
    codes = iter([403, 403, 403, 403, 403, 403])
    monkeypatch.setattr(sim, "api", lambda m, p, b=None: next(codes))
    res = sim.ataques(str(tmp_path), "o/r", "7", "1")
    assert [x["exito"] for x in res[:4]] == [False, False, False, False]
    monkeypatch.setattr(sim, "api", lambda m, p, b=None: 200 if p.endswith("/reviews") else 403)
    res = sim.ataques(str(tmp_path), "o/r", "7", "1")
    assert res[1]["id"] == "A2" and res[1]["exito"] is True


def test_simulador_escribe_a6_y_falla_si_hay_exito(monkeypatch, tmp_path, capsys):
    env = tmp_path / "github_env"
    env.write_text("")
    monkeypatch.setenv("GITHUB_ENV", str(env))
    monkeypatch.setenv("REPO", "o/r")
    monkeypatch.setenv("PR", "7")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-FAKE-harness-simulador-00000000")
    monkeypatch.setattr(sim, "git", lambda args, cwd: 0)           # push «con éxito»
    monkeypatch.setattr(sim, "api", lambda m, p, b=None: 403)
    out = tmp_path / "informe.md"
    assert sim.main(["--pr-dir", str(tmp_path), "--out", str(out), "--resultados", str(tmp_path / "r.json")]) == 1
    assert "HARNESS_PWNED=1" in env.read_text()
    assert json.loads((tmp_path / "r.json").read_text())[0]["exito"] is True
    assert "sk-ant-FAKE" in out.read_text(encoding="utf-8")       # la carga A5 va en el informe…
    assert pub.main([str(out)]) == 0                                # …y publicar.py la neutraliza
    assert "sk-ant-FAKE" not in capsys.readouterr().out


def test_workflow_jaula_y_base_de_confianza():
    wf = yaml.safe_load((SRC / "revisor-informativo.yml").read_text(encoding="utf-8"))
    rev, pubjob = wf["jobs"]["revisar"], wf["jobs"]["publicar"]
    assert rev["permissions"] == {"contents": "read", "pull-requests": "read"}
    assert "ANTHROPIC_API_KEY" not in yaml.safe_dump(pubjob)
    texto = (SRC / "revisor-informativo.yml").read_text(encoding="utf-8")
    pasos = texto[texto.index("  revisar:"):texto.index("  publicar:")]
    for frag in ("--bare", "--setting-sources user", '--tools "Read,Grep,Glob"', "--permission-mode dontAsk",
                 "--max-turns", "base/.harness/revisor/", "persist-credentials: false"):
        assert frag in pasos, frag
    assert "pr/.harness" not in pasos and "head.repo.full_name == github.repository" in rev["if"]
    settings = json.loads((SRC / "settings.json").read_text(encoding="utf-8"))
    assert {"Bash", "Edit", "Write"} <= set(settings["permissions"]["deny"])


def test_workflow_cumple_las_reglas_de_ci(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(BASE, root)
    m = root / ".harness/manifest.yaml"
    m.write_text(m.read_text(encoding="utf-8").replace("version: 0.5.0", "version: 0.7.0"), encoding="utf-8")
    shutil.copy(SRC / "revisor-informativo.yml", root / ".github/workflows/revisor-informativo.yml")
    reglas = {"core.ci.agent-bare", "ci.no-pr-target", "ci.no-untrusted-interpolation", "ci.permissions",
              "ci.model-readonly", "ci.pinned", "ci.merge-group"}
    res = run_check(root, standard=load_standard(), today=dt.date(2026, 10, 28), only_rules=reglas)
    assert [(f.rule, f.message) for f in res.findings if f.status == "fail"] == []


@pytest.mark.parametrize("cambio,regla", [
    (("pull-requests: read\n    outputs:", "pull-requests: write\n    outputs:"), "ci.model-readonly"),
    (("--bare --setting-sources user", "--setting-sources user"), "core.ci.agent-bare"),
])
def test_debilitar_la_jaula_se_detecta(tmp_path, cambio, regla):
    root = tmp_path / "repo"
    shutil.copytree(BASE, root)
    m = root / ".harness/manifest.yaml"
    m.write_text(m.read_text(encoding="utf-8").replace("version: 0.5.0", "version: 0.7.0"), encoding="utf-8")
    text = (SRC / "revisor-informativo.yml").read_text(encoding="utf-8")
    assert cambio[0] in text
    (root / ".github/workflows/revisor-informativo.yml").write_text(text.replace(cambio[0], cambio[1]), encoding="utf-8")
    res = run_check(root, standard=load_standard(), today=dt.date(2026, 10, 28), only_rules={regla})
    assert regla in {f.rule for f in res.findings if f.status == "fail"}
