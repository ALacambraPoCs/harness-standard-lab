"""harness platform check (F5.3-A, HS-CI-006) con respuestas de la API simuladas (sin red)."""
import datetime as dt
import shutil
from pathlib import Path

import pytest

from harness_cli import platform as P
from harness_cli.context import Context
from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tests" / "fixtures" / "conforming" / "n1-endurecido"
STD = load_standard()

RULES_OK = [
    {"type": "pull_request", "parameters": {"required_approving_review_count": 0}},
    {"type": "required_status_checks", "parameters": {"required_status_checks": [
        {"context": "conformance / harness check"}, {"context": "tasks / harness tasks"},
        {"context": "tasks / puerta riesgo alto"}]}},
    {"type": "non_fast_forward"}, {"type": "deletion"},
]
GATE_OK = {"name": "aprobacion-riesgo-alto", "protection_rules": [
    {"type": "required_reviewers", "prevent_self_review": False,
     "reviewers": [{"type": "User", "reviewer": {"login": "persona"}}]}]}


def instancia(tmp_path, version="0.7.0", level="N1", extra=""):
    root = tmp_path / "repo"
    shutil.copytree(BASE, root)
    m = root / ".harness/manifest.yaml"
    text = m.read_text(encoding="utf-8").replace("version: 0.5.0", f"version: {version}").replace("level: N1", f"level: {level}")
    m.write_text(text + extra, encoding="utf-8")
    return Context.build(root, STD, dt.date(2026, 10, 28))


def fake(rules=RULES_OK, gate=GATE_OK, gate_status=200, extra=None):
    def fetch(path):
        if path == "/repos/o/r":
            return 200, {"default_branch": "main"}
        if path == "/repos/o/r/rules/branches/main":
            return (200, rules) if rules is not None else (404, None)
        if path == "/repos/o/r/environments/aprobacion-riesgo-alto":
            return gate_status, gate
        if extra and path in extra:
            return extra[path]
        return 404, None
    return fetch


def ids(findings):
    return sorted({f.rule for f in findings})


def test_conforme_n1(tmp_path):
    assert P.check(instancia(tmp_path), "o/r", None, fake()) == []


def test_sin_reglas_ni_acceso(tmp_path):
    assert ids(P.check(instancia(tmp_path), "o/r", None, fake(rules=None))) == ["platform.reachable"]


@pytest.mark.parametrize("quitar,regla", [
    ("pull_request", "platform.pull-request"),
    ("required_status_checks", "platform.required-checks"),
    ("non_fast_forward", "platform.no-force-push"),
    ("deletion", "platform.no-deletion"),
])
def test_falta_una_regla(tmp_path, quitar, regla):
    rules = [r for r in RULES_OK if r["type"] != quitar]
    assert ids(P.check(instancia(tmp_path), "o/r", "main", fake(rules=rules))) == [regla]


def test_falta_un_check_requerido(tmp_path):
    rules = [dict(r) for r in RULES_OK]
    rules[1] = {"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "conformance / harness check"}]}}
    f = P.check(instancia(tmp_path), "o/r", "main", fake(rules=rules))
    assert ids(f) == ["platform.required-checks"] and "harness tasks" in f[0].message and "puerta riesgo alto" in f[0].message


def test_puerta_inexistente_o_sin_revisores(tmp_path):
    f = P.check(instancia(tmp_path), "o/r", "main", fake(gate=None, gate_status=404))
    assert ids(f) == ["platform.gate-environment"] and "SIN protección" in f[0].message
    sin = {"name": "aprobacion-riesgo-alto", "protection_rules": []}
    assert ids(P.check(instancia(tmp_path / "b"), "o/r", "main", fake(gate=sin))) == ["platform.gate-environment"]


def test_version_0_5_no_exige_puerta(tmp_path):
    rules = [dict(r) for r in RULES_OK]
    rules[1] = {"type": "required_status_checks", "parameters": {"required_status_checks": [
        {"context": "conformance / harness check"}, {"context": "tasks / harness tasks"}]}}
    assert P.check(instancia(tmp_path, version="0.5.0"), "o/r", "main", fake(rules=rules, gate=None, gate_status=404)) == []


def test_n2_exige_aprobaciones_y_prevent_self_review(tmp_path):
    f = P.check(instancia(tmp_path, level="N2"), "o/r", "main", fake())
    assert ids(f) == ["platform.approvals", "platform.gate-environment"]
    assert "Code Owners" in f[0].message or "Code Owners" in f[1].message
    rules = [dict(r) for r in RULES_OK]
    rules[0] = {"type": "pull_request", "parameters": {"required_approving_review_count": 1, "require_code_owner_review": True,
                                                       "require_last_push_approval": True}}
    gate = {"protection_rules": [dict(GATE_OK["protection_rules"][0], prevent_self_review=True)]}
    assert P.check(instancia(tmp_path / "b", level="N2"), "o/r", "main", fake(rules=rules, gate=gate)) == []


def test_entorno_de_despliegue_declarado(tmp_path):
    ctx = instancia(tmp_path, extra="plataforma:\n  entorno_despliegue: github-pages\n")
    f = P.check(ctx, "o/r", "main", fake())
    assert ids(f) == ["platform.deploy-environment"]
    ok = {"/repos/o/r/environments/github-pages": (200, {"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}})}
    assert P.check(instancia(tmp_path / "b", extra="plataforma:\n  entorno_despliegue: github-pages\n"), "o/r", "main", fake(extra=ok)) == []


def test_cli_sin_repo(tmp_path, monkeypatch, capsys):
    from harness_cli.cli import main
    instancia(tmp_path)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert main(["platform", "check", "--path", str(tmp_path / "repo")]) == 2
    assert "--repo" in capsys.readouterr().err
