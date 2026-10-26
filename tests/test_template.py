"""La plantilla instanciada supera su propio validador (criterio de aceptación del producto B), en N0 y N1."""
import datetime as dt
import shutil
from pathlib import Path

import pytest

from harness_cli import tasks as T
from harness_cli.checker import run_check
from harness_cli.context import Context
from harness_cli.standard import load_standard

TEMPLATE = Path(__file__).resolve().parents[1] / "template"
VALUES = {
    "{{PROJECT_NAME}}": "demo", "{{PROJECT_SUMMARY}}": "Servicio de demostración.",
    "{{OWNER}}": "@org/demo", "{{KIND}}": "service", "{{DOCS_LANGUAGE}}": "es", "{{DATE}}": "2026-10-21",
    "{{SETUP}}": "python3 -c pass", "{{CHECK}}": "python3 -c pass", "{{TEST}}": "python3 -c pass",
    "{{HARNESS_OWNERS}}": "@org/harness-owners", "{{SECURITY_OWNERS}}": "@org/security",
    "{{PLATFORM_OWNERS}}": "@org/platform", "{{CLI_REF}}": "cli-v0.5.1-rc.1", "{{STANDARD_REPO}}": "org/harness-standard",
}


def render(dst: Path, level: str = "N0") -> None:
    shutil.copytree(TEMPLATE / "core", dst, dirs_exist_ok=True)
    shutil.copytree(TEMPLATE / "adapters" / "claude-code", dst, dirs_exist_ok=True)
    shutil.copytree(TEMPLATE / "adapters" / "github", dst, dirs_exist_ok=True)
    if level == "N1":
        shutil.copytree(TEMPLATE / "niveles" / "n1", dst, dirs_exist_ok=True)
    (dst / "gitignore.fragment").rename(dst / ".gitignore")
    for p in dst.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            for k, v in {**VALUES, "{{LEVEL}}": level}.items():
                text = text.replace(k, v)
            assert "{{" not in text, f"marcador sin sustituir en {p}"
            p.write_text(text, encoding="utf-8")


@pytest.mark.parametrize("level", ["N0", "N1"])
def test_template_passes_own_validator(tmp_path, level):
    render(tmp_path, level)
    std = load_standard()
    if level == "N1":
        ctx = Context.build(tmp_path, std, dt.date(2026, 10, 21))
        assert (tmp_path / "docs/plans/INDEX.md").read_text(encoding="utf-8") == T.render_index(T.validate(ctx)[1])
    res = run_check(tmp_path, standard=std, today=dt.date(2026, 10, 21), run_commands=True)
    failing = [(f.rule, f.message) for f in res.findings if f.status == "fail"]
    assert not failing, failing
    assert res.effective_level == level


# Reglas de settings.json que cubren cada patrón sensible (ficha adapter.claude.settings, F3.2).
SENSITIVE_TO_RULE = {
    "AGENTS.md": "Edit(AGENTS.md)", "**/AGENTS.md": "Edit(AGENTS.md)",
    "CLAUDE.md": "Edit(CLAUDE.md)", "**/CLAUDE.md": "Edit(CLAUDE.md)",
    "/.claude/": "Edit(/.claude/**)", "/.agents/": "Edit(/.agents/**)", "/.mcp.json": "Edit(/.mcp.json)",
    "/.harness/": "Edit(/.harness/**)", "/.github/workflows/": "Edit(/.github/workflows/**)",
    "/.github/CODEOWNERS": "Edit(/.github/CODEOWNERS)",
}


def test_settings_base_cubre_rutas_sensibles():
    import json
    s = json.loads((TEMPLATE / "adapters/claude-code/.claude/settings.json").read_text(encoding="utf-8"))
    perms = s["permissions"]
    guarded = set(perms.get("ask", [])) | set(perms.get("deny", []))
    std = load_standard()
    missing = [p for p in std.sensitive_patterns if SENSITIVE_TO_RULE.get(p) not in guarded]
    assert not missing, f"patrones_sensibles sin regla ask/deny en settings.json: {missing}"
    assert {"Read(.env)", "Read(.env.*)", "Edit(.env)", "Edit(.env.*)"} <= set(perms["deny"])
    assert perms["disableBypassPermissionsMode"] == "disable"
    assert s.get("enableAllProjectMcpServers") is not True
    assert s["$schema"] == "https://json.schemastore.org/claude-code-settings.json"
    assert "defaultMode" not in perms


# ─────────────── P-1…P-3 (D-041…D-043): modos, gh y allow de la base ───────────────
def _settings_base():
    import json
    return json.loads((TEMPLATE / "adapters/claude-code/.claude/settings.json").read_text(encoding="utf-8"))


def test_settings_base_modo_automatico_y_gh():
    from harness_cli.rules.components import GH_ASK, GH_DENY, bash_decision
    s = _settings_base()
    assert s["permissions"]["disableAutoMode"] == "disable"
    assert all(bash_decision(s, c) == "ask" for c in GH_ASK)
    assert all(bash_decision(s, c) == "deny" for c in GH_DENY)


# Opciones revisadas de los subcomandos que la base permite sin confirmación (P-3).
# Si se añade una opción nueva a estos subcomandos, este test falla: hay que revisar si tiene
# efectos y, en ese caso, cubrirla con una regla ask en la base y en EFECTOS.
REVISADAS = {
    ("check",): {"--path", "--format", "--json-out", "--strict", "--run-commands", "--timeout", "--today", "--rule", "--verbose"},
    ("tasks", "validate"): {"--path", "--base", "--pr-number", "--run-acceptance", "--approvers", "--format"},
    ("tasks", "close"): {"--pr", "--resultado", "--verified-by", "--autor", "--path"},
    ("tasks", "index"): {"--path", "--write", "--check"},
    ("pr", "check"): {"--path", "--base", "--body-file", "--body-env", "--title-env", "--format"},
    ("components", "list"): None,  # se compara abajo con lo que exista
}
EFECTOS = {
    "harness check --run-commands": "ask",                      # ejecuta setup/check del manifiesto
    "harness check --json-out .claude/settings.json": "ask",    # escribe un archivo arbitrario
    "harness tasks validate --base origin/main --run-acceptance": "ask",  # ejecuta criterios de las tareas
    "harness tasks index --write": None,                        # escribe: no está en allow
    "harness components add verificador": None,                 # instala: no está en allow
    "harness check --strict": "allow",
    "harness tasks close T-0001 --pr 7": "allow",
    "harness components list": "allow",
    # F3.8 (D-052)
    "git add src/app.py": "allow",
    "git commit -m \"T-0001: cerrar la tarea\"": "allow",
    "git add -f .env": "ask",
    "git add docs --force": "ask",
    "git commit -m x --no-verify": "ask",
    "git commit -n -m x": "ask",
    "git commit -m x -n": "ask",
    "git add --force .env": "ask",
    "git push -u origin rama": "ask",
    "gh pr view 7": "allow",
    "gh pr create --draft --title x --body-file cuerpo.md": "allow",
    "gh pr ready 7": "allow",
    "gh pr merge 7": "ask",
    "gh pr edit 7 --body-file cuerpo.md": "ask",
}


def _sub(parser, path):
    import argparse
    for name in path:
        action = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
        parser = action.choices[name]
    return parser


def test_opciones_de_comandos_permitidos_revisadas():
    from harness_cli.cli import build_parser
    p = build_parser()
    for path, esperado in REVISADAS.items():
        opts = {o for a in _sub(p, path)._actions for o in a.option_strings if o.startswith("--") and o != "--help"}
        if esperado is not None:
            assert opts == esperado, f"harness {' '.join(path)}: opciones sin revisar {sorted(opts ^ esperado)}"
        else:
            assert opts <= {"--path"}, f"harness {' '.join(path)}: opciones nuevas {sorted(opts)}"


def test_efectos_de_la_base():
    from harness_cli.rules.components import bash_decision
    s = _settings_base()
    for cmd, want in EFECTOS.items():
        assert bash_decision(s, cmd) == want, cmd
