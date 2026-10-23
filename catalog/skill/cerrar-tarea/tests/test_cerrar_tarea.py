"""Pruebas de la skill cerrar-tarea: especificación, perfil y coherencia con la CLI real."""
import re
import shlex
from pathlib import Path

import pytest

from harness_cli import cli
from harness_cli.skills import validate_skill

SRC = Path(__file__).resolve().parents[1] / "src" / "SKILL.md"
TEXT = SRC.read_text(encoding="utf-8")


def test_especificacion_y_perfil():
    rep = validate_skill(SRC, "SKILL.md", expected_name="cerrar-tarea")
    assert rep.spec == [] and rep.profile == [] and rep.perfil == "portable"
    assert len(TEXT.splitlines()) < 500


COMANDOS = sorted(set(re.findall(r"`(harness [^`]+)`", TEXT)))


@pytest.mark.parametrize("cmd", COMANDOS)
def test_los_comandos_harness_existen(cmd, monkeypatch):
    """Cada `harness …` citado debe aceptarlo el parser actual, opciones incluidas (deriva skill ↔ CLI).
    Se sustituyen las acciones por funciones vacías: solo se comprueba el análisis de argumentos."""
    llamadas = []
    for name in [n for n in dir(cli) if n.startswith("_cmd_")]:
        monkeypatch.setattr(cli, name, lambda args, _n=name: llamadas.append(_n) or 0)
    args = shlex.split(re.sub(r"<[^>]+>", "1", cmd))[1:]
    assert cli.main(args) == 0, cmd
    assert llamadas, cmd


def test_detecta_opcion_inventada(monkeypatch):
    for name in [n for n in dir(cli) if n.startswith("_cmd_")]:
        monkeypatch.setattr(cli, name, lambda args: 0)
    with pytest.raises(SystemExit) as exc:
        cli.main(["tasks", "validate", "--opcion-inventada"])
    assert exc.value.code == 2


def test_cubre_los_errores_de_la_ci():
    for regla in ("tasks.done-pr", "tasks.transition", "tasks.acceptance", "pr.issue", "tasks.index"):
        assert regla in TEXT
    assert "No cambies los criterios de aceptación" in TEXT


def test_usa_tasks_close_y_no_edicion_manual():
    """P-4 (D-044): el cierre lo hace la CLI; la skill no describe la edición a mano."""
    assert "harness tasks close T-NNNN --pr <número>" in TEXT
    assert "git mv docs/plans/active" not in TEXT
    assert TEXT.index("Abre el PR") < TEXT.index("harness tasks close T-NNNN")


def test_evidencia_literal_y_sin_confirmaciones_extra():
    """P-6 (D-046): bloque literal del verificador, sin confirmación propia antes del push y sin depender de gh."""
    for frase in ("<!-- verificador:inicio -->", "<!-- verificador:fin -->", "harness:evidencia", "copiado literal",
                  "no pidas otra confirmación tú", "Sin `gh`", "No uses `gh api`"):
        assert frase in TEXT, frase
