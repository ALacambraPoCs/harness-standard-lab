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
    "{{PLATFORM_OWNERS}}": "@org/platform", "{{CLI_REF}}": "cli-v0.3.0-rc.1", "{{STANDARD_REPO}}": "org/harness-standard",
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
