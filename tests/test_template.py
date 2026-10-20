"""La plantilla instanciada supera su propio validador (criterio de aceptación del producto B)."""
import datetime as dt
import shutil
from pathlib import Path

from harness_cli.checker import run_check
from harness_cli.standard import load_standard

TEMPLATE = Path(__file__).resolve().parents[1] / "template"
VALUES = {
    "{{PROJECT_NAME}}": "demo", "{{PROJECT_SUMMARY}}": "Servicio de demostración.",
    "{{OWNER}}": "@org/demo", "{{KIND}}": "service",
    "{{SETUP}}": "python3 -c pass", "{{CHECK}}": "python3 -c pass", "{{TEST}}": "python3 -c pass",
    "{{HARNESS_OWNERS}}": "@org/harness-owners", "{{SECURITY_OWNERS}}": "@org/security",
    "{{PLATFORM_OWNERS}}": "@org/platform", "{{CLI_REF}}": "cli-v0.1.0", "{{STANDARD_REPO}}": "org/harness-standard",
}


def render(dst: Path) -> None:
    shutil.copytree(TEMPLATE / "core", dst, dirs_exist_ok=True)
    shutil.copytree(TEMPLATE / "adapters" / "claude-code", dst, dirs_exist_ok=True)
    shutil.copytree(TEMPLATE / "adapters" / "github", dst, dirs_exist_ok=True)
    (dst / "gitignore.fragment").rename(dst / ".gitignore")
    for p in dst.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            for k, v in VALUES.items():
                text = text.replace(k, v)
            assert "{{" not in text, f"marcador sin sustituir en {p}"
            p.write_text(text, encoding="utf-8")


def test_template_passes_own_validator(tmp_path):
    render(tmp_path)
    res = run_check(tmp_path, standard=load_standard(), today=dt.date(2026, 10, 19), run_commands=True)
    failing = [(f.rule, f.message) for f in res.findings if f.status == "fail"]
    assert not failing, failing
    assert res.effective_level == "N0"
