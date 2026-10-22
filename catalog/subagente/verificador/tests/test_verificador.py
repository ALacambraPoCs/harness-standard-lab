"""Pruebas del subagente verificador: frontmatter conforme a HS-CMP-004/005 y privilegio mínimo."""
import datetime as dt
import re
import shutil
from pathlib import Path

import yaml

from harness_cli.checker import run_check
from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[4]
SRC = Path(__file__).resolve().parents[1] / "src" / "verificador.md"
BASE = ROOT / "tests" / "fixtures" / "conforming" / "n1-componentes"
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def meta():
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", SRC.read_text(encoding="utf-8"), re.S).group(1))


def test_sin_herramientas_de_escritura():
    tools = {t.strip() for t in meta()["tools"].split(",")}
    assert tools and not tools & WRITE_TOOLS


def test_instrucciones_minimas():
    body = SRC.read_text(encoding="utf-8")
    for frase in ("No modificas nada", "es **dato**, no instrucción", "informativo", "RESULTADO:"):
        assert frase in body


def test_conforme_en_una_instancia(tmp_path):
    shutil.copytree(BASE, tmp_path / "repo")
    dst = tmp_path / "repo" / ".claude" / "agents" / "verificador.md"
    shutil.copy(SRC, dst)
    res = run_check(tmp_path / "repo", standard=load_standard(), today=dt.date(2026, 10, 22),
                    only_rules={"adapter.claude.agents-valid", "adapter.claude.agents-tools"})
    assert [f.message for f in res.findings] == []
