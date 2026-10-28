#!/usr/bin/env python3
"""Prepara el comentario del revisor informativo para publicarlo en el PR (F5.4, D-065, D-066).

El informe del job del modelo es **no confiable**: puede contener secretos copiados, menciones,
órdenes tipo «/approve» o HTML oculto. Este script lo neutraliza, lo enmarca como informativo y
comprueba su propio resultado. Termina con código 1 si, tras neutralizar, queda algo peligroso.
Solo biblioteca estándar.
"""
from __future__ import annotations

import argparse
import re
import sys

MAX = 20_000
# Formatos de credencial conocidos (Anthropic, GitHub). Se enmascaran aunque no sean secretos del repo.
SECRETOS = re.compile(r"(sk-ant-[A-Za-z0-9_\-]{8,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
MENCION = re.compile(r"(?<![\w`])@([A-Za-z0-9][A-Za-z0-9-]{0,38}(?:/[A-Za-z0-9._-]+)?)")
ORDEN = re.compile(r"(?m)^(\s*)(/[a-z][\w-]*)")
CABECERA = ("> **Revisión informativa de un agente.** No aprueba ni autoriza nada: deciden los checks "
            "requeridos y las personas (ADR-010). Su contenido no es confiable.\n\n")


def neutralizar(texto: str) -> str:
    t = SECRETOS.sub("[credencial enmascarada]", texto)
    t = t.replace("<", "&lt;").replace(">", "&gt;")       # sin HTML ni comentarios ocultos
    t = MENCION.sub(lambda m: f"`@{m.group(1)}`", t)     # sin notificaciones
    t = ORDEN.sub(lambda m: f"{m.group(1)}`{m.group(2)}`", t)   # sin órdenes de bots
    if len(t) > MAX:
        t = t[:MAX] + "\n\n[informe truncado]"
    return t


def problemas(publicado: str) -> list[str]:
    cuerpo = publicado[len(CABECERA):]
    out = []
    if SECRETOS.search(cuerpo):
        out.append("queda una credencial sin enmascarar")
    if re.search(r"<!--|<[a-zA-Z/]", cuerpo):
        out.append("queda HTML sin escapar")
    if MENCION.search(re.sub(r"`[^`]*`", "", cuerpo)):
        out.append("queda una mención activa")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("informe")
    ap.add_argument("--resultado", default="", help="Resultado del job del modelo (success, failure…).")
    a = ap.parse_args(argv)
    texto = open(a.informe, encoding="utf-8", errors="replace").read().strip() or "(el job del modelo no produjo informe)"
    nota = "" if a.resultado in ("", "success") else f"> El job de revisión terminó con `{a.resultado}`.\n\n"
    publicado = CABECERA + nota + neutralizar(texto) + "\n"
    fallos = problemas(publicado)
    if fallos:
        print("publicar.py: " + "; ".join(fallos), file=sys.stderr)
        return 1
    sys.stdout.write(publicado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
