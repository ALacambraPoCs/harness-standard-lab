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
    base = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_STOP_")}
    env = {**base, "CLAUDE_PROJECT_DIR": str(root), "PATH": "/usr/bin:/bin", **(env_extra or {})}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"session_id": session, "hook_event_name": "Stop"}),
                       capture_output=True, text=True, env=env, timeout=60)
    return p.returncode, p.stderr


def run_full(root: Path, session: str, env_extra=None):
    base = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_STOP_")}
    env = {**base, "CLAUDE_PROJECT_DIR": str(root), "PATH": "/usr/bin:/bin", **(env_extra or {})}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"session_id": session, "hook_event_name": "Stop"}),
                       capture_output=True, text=True, env=env, timeout=60)
    return p.returncode, p.stdout, p.stderr


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
    assert code == 2 and "código 3" in err and "rojo" in err and "intento 1 de 2" in err and "HARNESS_STOP_MAX=0" in err


def test_limite_de_reintentos(tmp_path, sesion):
    root = instancia(tmp_path, "false")
    codes = [run(root, sesion)[0] for _ in range(3)]
    assert codes == [2, 2, 0]


def test_contador_se_reinicia_al_pasar(tmp_path, sesion):
    root = instancia(tmp_path, "test -f ok")
    assert run(root, sesion)[0] == 2
    (root / "ok").write_text("x")
    assert run(root, sesion)[0] == 0
    (root / "ok").unlink()
    _, err = run(root, sesion)
    assert "intento 1 de 2" in err


def test_limite_configurable(tmp_path, sesion):
    root = instancia(tmp_path, "false")
    codes = [run(root, sesion, {"HARNESS_STOP_MAX": "3"})[0] for _ in range(4)]
    assert codes == [2, 2, 2, 0]


def test_suspendido_no_bloquea_pero_informa(tmp_path, sesion):
    root = instancia(tmp_path, "python3 -c \"import sys; print('rojo'); sys.exit(1)\"")
    for _ in range(2):
        code, err = run(root, sesion, {"HARNESS_STOP_MAX": "0"})
        assert code == 0 and "suspendido" in err and "rojo" in err


def test_suspendido_avisa_con_systemmessage(tmp_path, sesion):
    """P-11 (D-051): con exit 0 stderr no se muestra; el aviso va en systemMessage (JSON en stdout)."""
    root = instancia(tmp_path, "python3 -c \"import sys; print('rojo'); sys.exit(1)\"")
    code, out, _ = run_full(root, sesion, {"HARNESS_STOP_MAX": "0"})
    assert code == 0
    msg = json.loads(out)["systemMessage"]
    assert "suspendido" in msg and "código 1" in msg


def test_agotar_reintentos_avisa_con_systemmessage(tmp_path, sesion):
    root = instancia(tmp_path, "false")
    run_full(root, sesion)
    run_full(root, sesion)
    code, out, _ = run_full(root, sesion)
    assert code == 0 and "tras 2 intentos" in json.loads(out)["systemMessage"]


def test_al_bloquear_stdout_vacio(tmp_path, sesion):
    """Exit 2: el mensaje va en stderr (Claude lo ve); sin JSON en stdout."""
    code, out, err = run_full(instancia(tmp_path, "false"), sesion)
    assert code == 2 and out == "" and "intento 1 de 2" in err


def test_valor_invalido_usa_el_defecto(tmp_path, sesion):
    code, err = run(instancia(tmp_path, "false"), sesion, {"HARNESS_STOP_MAX": "dos"})
    assert code == 2 and "intento 1 de 2" in err


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
