#!/usr/bin/env python3
"""Hook PreToolUse de Claude Code: un `git push` se ejecuta suelto (componente `push-suelto`; H-28, H-34).

Con el sandbox, `excludedCommands` solo saca del sandbox un `git push …` que coincide tal cual. Un push
encadenado (`;`, `&&`, `|`…), dentro de `$(…)` o con opciones antes del subcomando (`git -C dir push`) se
ejecuta dentro del sandbox, sin credenciales, y falla. La skill lo pide (L1) y el agente lo incumplió (H-34):
este hook lo rechaza antes de ejecutarlo y le dice al agente la forma correcta.

Contrato: JSON por stdin (`tool_name`, `tool_input.command`). Exit 0 → sigue el flujo normal de permisos
(no aprueba nada). Exit 2 + stderr → Claude Code bloquea la llamada y muestra el motivo al agente.
Solo biblioteca estándar.
"""
from __future__ import annotations

import json
import re
import sys

PUSH = re.compile(r"\bgit\b(?P<pre>[^;&|\n`]*?)\bpush\b")
COMPUESTO = re.compile(r"(;|&&|\|\||\||\n|`|\$\()")
MENSAJE = ("push-suelto: ejecuta `git push` como un comando suelto, desde la raíz del repositorio y sin "
           "`;`, `&&`, `|`, `$(…)` ni opciones antes de `push` (como `-C <ruta>`). Solo así sale del sandbox "
           "con las credenciales de git (H-28). Ejemplo: `git push -u origin <rama>`.")


def motivo(cmd: str) -> str | None:
    """Devuelve el motivo del rechazo, o None si el comando no contiene un push problemático."""
    m = PUSH.search(cmd)
    if not m:
        return None
    if COMPUESTO.search(cmd.strip()):
        return "compuesto"
    if m.group("pre").strip():                      # git -C x push, git -c k=v push, git --git-dir … push
        return "opciones antes de push"
    if not cmd.lstrip().startswith("git"):           # env X=1 git push, sudo git push…
        return "prefijo"
    return None


def main() -> int:
    try:
        evento = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0                                    # entrada inesperada: no bloquea (falla en abierto, L3)
    if evento.get("tool_name") != "Bash":
        return 0
    cmd = (evento.get("tool_input") or {}).get("command") or ""
    m = motivo(cmd)
    if m:
        print(f"{MENSAJE} (detectado: {m})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
