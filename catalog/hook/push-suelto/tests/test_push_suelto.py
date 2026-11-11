"""Pruebas del hook push-suelto (H-34)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "src" / "push_suelto.py"


def run(evento):
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(evento), capture_output=True, text=True, timeout=30)
    return p.returncode, p.stderr


def bash(cmd):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}}


@pytest.mark.parametrize("cmd", [
    "git push", "git push -u origin t-0011", "git push origin HEAD:refs/heads/x", "  git push --force-with-lease",
    "git status --short", "python3 -m unittest", "echo 'git pushover'", "gh pr create --draft",
])
def test_permitidos(cmd):
    assert run(bash(cmd)) == (0, "")


@pytest.mark.parametrize("cmd,detalle", [
    ("git status --short | grep -v '^??' ; git push", "compuesto"),       # caso real de la F5 (sesión D)
    ("git add -A && git commit -m x && git push", "compuesto"),
    ("git push 2>&1 | tail -3", "compuesto"),
    ("git push\necho ok", "compuesto"),
    ("echo $(git push)", "compuesto"),
    ("git -C /home/x/repo push -u origin rama", "opciones antes de push"),  # caso real de la F5.7 (sesión C)
    ("git -c credential.helper= push", "opciones antes de push"),
    ("env GIT_TRACE=1 git push", "prefijo"),
])
def test_rechazados(cmd, detalle):
    code, err = run(bash(cmd))
    assert code == 2 and "comando suelto" in err and detalle in err


def test_otras_herramientas_y_entrada_rota():
    assert run({"tool_name": "Edit", "tool_input": {"file_path": "x"}})[0] == 0
    p = subprocess.run([sys.executable, str(HOOK)], input="no es json", capture_output=True, text=True, timeout=30)
    assert p.returncode == 0
