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
    "{{PLATFORM_OWNERS}}": "@org/platform", "{{CLI_REF}}": "cli-v0.2.0-rc.2", "{{STANDARD_REPO}}": "org/harness-standard",
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
