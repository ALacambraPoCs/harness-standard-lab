"""Pruebas del hook verificar-al-terminar (componente del catálogo)."""
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "src" / "verificar_al_terminar.py"


def run(root: Path, session: str, env_extra=None):
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root), "PATH": "/usr/bin:/bin", **(env_extra or {})}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"session_id": session, "hook_event_name": "Stop"}),
                       capture_output=True, text=True, env=env, timeout=60)
    return p.returncode, p.stderr


def instancia(tmp_path: Path, check: str) -> Path:
    (tmp_path / ".harness").mkdir()
    (tmp_path / ".harness/manifest.yaml").write_text(
        f"standard:\n  version: 0.3.0\n  level: N1\ncommands:\n  setup: true\n  check: {check}\n  test: true\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def sesion():
    return f"test-{uuid.uuid4().hex}"


def test_check_pasa_permite_parar(tmp_path, sesion):
    assert run(instancia(tmp_path, "python3 -c pass"), sesion)[0] == 0


def test_check_falla_bloquea_con_mensaje(tmp_path, sesion):
    code, err = run(instancia(tmp_path, "python3 -c \"import sys; print('rojo'); sys.exit(3)\""), sesion)
    assert code == 2 and "código 3" in err and "rojo" in err and "intento 1 de 3" in err


def test_limite_de_reintentos(tmp_path, sesion):
    root = instancia(tmp_path, "false")
    codes = [run(root, sesion)[0] for _ in range(4)]
    assert codes == [2, 2, 2, 0]


def test_contador_se_reinicia_al_pasar(tmp_path, sesion):
    root = instancia(tmp_path, "test -f ok")
    assert run(root, sesion)[0] == 2
    (root / "ok").write_text("x")
    assert run(root, sesion)[0] == 0
    (root / "ok").unlink()
    _, err = run(root, sesion)
    assert "intento 1 de 3" in err


def test_sin_manifiesto_falla_en_abierto(tmp_path, sesion):
    code, err = run(tmp_path, sesion)
    assert code == 0 and "no hay .harness/manifest.yaml" in err


def test_check_entre_comillas(tmp_path, sesion):
    assert run(instancia(tmp_path, "\"python3 -c pass\""), sesion)[0] == 0


def test_tareas_invalidas_bloquean(tmp_path, sesion):
    root = instancia(tmp_path / "repo", "true") if (tmp_path / "repo").mkdir() is None else None
    (root / "docs/plans").mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "harness"
    fake.write_text("#!/bin/sh\necho 'tasks.schema: T-0001 inválida'\nexit 1\n")
    fake.chmod(0o755)
    code, err = run(root, sesion, {"PATH": f"{bin_dir}:/usr/bin:/bin"})
    assert code == 2 and "harness tasks validate" in err and "T-0001 inválida" in err
