#!/usr/bin/env python3
"""Hook Stop de Claude Code: no dejar que el agente dé el trabajo por terminado si `check` falla
o si las tareas no validan. Componente del catálogo `verificar-al-terminar` (ver FICHA.md).

Contrato:
- Entrada: JSON del evento Stop por stdin (session_id, cwd, …; `stop_hook_active` si existe).
- Salida: exit 0 → el agente puede parar. Exit 2 + mensaje en stderr → Claude Code impide parar y
  le muestra el mensaje (documentado: "Prevents Claude from stopping, continues the conversation").
- Es retroalimentación (L3), no autoridad: la autoridad es la CI (ADR-016).
- Falla en abierto (exit 0 con aviso) si no puede leer el manifiesto: un hook roto no debe bloquear
  el trabajo; HS-CMP-006 y la CI cubren ese caso.
- Límite de reintentos por sesión (MAX_BLOQUEOS) para evitar bucles, sin depender de campos no verificados.

Solo usa la biblioteca estándar (la instancia no tiene por qué tener PyYAML).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_BLOQUEOS = int(os.environ.get("HARNESS_STOP_MAX", "3"))
TIMEOUT = int(os.environ.get("HARNESS_STOP_TIMEOUT", "240"))
COLA = 25  # líneas de salida que se muestran al agente


def comando_check(manifest: Path) -> str | None:
    """Lee commands.check del manifiesto sin PyYAML (formato de la plantilla: clave en línea)."""
    en_commands = False
    for linea in manifest.read_text(encoding="utf-8").splitlines():
        if re.match(r"^commands:\s*$", linea):
            en_commands = True
            continue
        if en_commands:
            if linea and not linea.startswith((" ", "\t")):
                break
            m = re.match(r"^\s+check:\s*(.+?)\s*$", linea)
            if m:
                valor = m.group(1)
                if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                    valor = valor[1:-1]
                return valor
    return None


def ejecutar(cmd: list[str] | str, cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=TIMEOUT)
        return p.returncode, "\n".join((p.stdout + p.stderr).strip().splitlines()[-COLA:])
    except subprocess.TimeoutExpired:
        return 124, f"tiempo agotado ({TIMEOUT}s)"


def contador(session_id: str) -> Path:
    d = Path(tempfile.gettempdir()) / "harness-stop-hook"
    d.mkdir(exist_ok=True)
    return d / (re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "sin-sesion") + ".count")


def main() -> int:
    try:
        evento = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        evento = {}
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or evento.get("cwd") or ".").resolve()
    manifest = raiz / ".harness" / "manifest.yaml"
    if not manifest.is_file():
        print("verificar-al-terminar: no hay .harness/manifest.yaml; no se verifica.", file=sys.stderr)
        return 0
    check = comando_check(manifest)
    if not check:
        print("verificar-al-terminar: el manifiesto no declara commands.check; no se verifica.", file=sys.stderr)
        return 0

    fallos = []
    code, out = ejecutar(check, raiz)
    if code != 0:
        fallos.append(f"`check` ({check}) terminó con código {code}:\n{out}")
    if shutil.which("harness") and (raiz / "docs" / "plans").is_dir():
        code, out = ejecutar(["harness", "tasks", "validate", "--path", str(raiz)], raiz)
        if code != 0:
            fallos.append(f"`harness tasks validate` terminó con código {code}:\n{out}")

    cont = contador(str(evento.get("session_id", "")))
    if not fallos:
        cont.unlink(missing_ok=True)
        return 0
    n = int(cont.read_text() or 0) + 1 if cont.exists() else 1
    if n > MAX_BLOQUEOS:
        cont.unlink(missing_ok=True)
        print(f"verificar-al-terminar: siguen fallando las verificaciones tras {MAX_BLOQUEOS} intentos; "
              "se permite parar. Informa a la persona responsable de lo que falla.", file=sys.stderr)
        return 0
    cont.write_text(str(n))
    print("No des el trabajo por terminado: estas verificaciones fallan "
          f"(intento {n} de {MAX_BLOQUEOS}). Corrígelas o explica por qué no puedes.\n\n" + "\n\n".join(fallos),
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
