from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from . import SUPPORTED_STANDARD, __version__
from .checker import run_check
from .report import to_json, to_text
from .rules import load_all
from .standard import load_standard


def _cmd_check(args) -> int:
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    res = run_check(Path(args.path), standard=std,
                    today=dt.date.fromisoformat(args.today) if args.today else None,
                    run_commands=args.run_commands, command_timeout=args.timeout,
                    only_rules=set(args.rule) if args.rule else None)
    print(to_json(res) if args.format == "json" else to_text(res, verbose=args.verbose))
    if args.json_out:
        Path(args.json_out).write_text(to_json(res), encoding="utf-8")
    return res.exit_code(strict=args.strict)


def _cmd_matrix(args) -> int:
    from .matrix import blocking, run, to_markdown
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    fixtures = Path(args.fixtures) if args.fixtures else std.root / "tests" / "fixtures"
    rows, problems, outcomes = run(std, fixtures, execute=args.strict)
    md = to_markdown(rows, problems, outcomes)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Matriz escrita en {args.output}")
    else:
        print(md)
    if args.strict and blocking(problems):
        print("\n".join(["", "Incidencias bloqueantes:"] + [f"  - {p}" for p in blocking(problems)]), file=sys.stderr)
        return 1
    return 0


def _cmd_explain(args) -> int:
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    reg = load_all()
    key = args.id
    if key in std.requirements:
        r = std.requirements[key]
        print(f"{r['id']} · {r['nivel']} · {r['titulo']}\n\n{r['texto']}\n")
        for k in ("conformidad", "naturaleza", "verificacion", "exentable", "reglas", "fuentes", "estado", "retirada"):
            print(f"  {k}: {r.get(k)}")
        if r.get("verificacion_manual"):
            print(f"  verificacion_manual: {r['verificacion_manual']}")
        return 0
    if key in reg:
        rule = reg[key]
        print(f"{rule.id}\n  requisitos: {', '.join(rule.requirements)}\n  {rule.doc}")
        return 0
    print(f"No existe requisito ni regla `{key}`.", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness", description="CLI de conformidad del Estándar de Harness.")
    p.add_argument("--version", action="version",
                   version=f"harness {__version__} (estándar soportado: {', '.join(s + '.x' for s in SUPPORTED_STANDARD)})")
    p.add_argument("--standard-root", help="Raíz alternativa del estándar (desarrollo).")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="Valida la conformidad de una instancia.")
    c.add_argument("--path", default=".", help="Raíz del repositorio a validar (por defecto: .)")
    c.add_argument("--format", choices=["text", "json"], default="text")
    c.add_argument("--json-out", help="Además de la salida elegida, escribe el informe JSON en este archivo.")
    c.add_argument("--strict", action="store_true", help="Los avisos (DEBERÍA) también hacen fallar.")
    c.add_argument("--run-commands", action="store_true", help="Ejecuta setup/check del contrato (HS-VER-002/003).")
    c.add_argument("--timeout", type=int, default=900, help="Tiempo máximo por comando (s).")
    c.add_argument("--today", help="Fecha de referencia AAAA-MM-DD (para waivers; útil en tests).")
    c.add_argument("--rule", action="append", help="Ejecuta solo esta regla (repetible).")
    c.add_argument("-v", "--verbose", action="store_true")
    c.set_defaults(func=_cmd_check)

    m = sub.add_parser("matrix", help="Genera la matriz requisito → regla → fixture (repo central).")
    m.add_argument("--fixtures", help="Directorio de fixtures (por defecto: <raíz estándar>/tests/fixtures).")
    m.add_argument("--output", help="Archivo Markdown de salida.")
    m.add_argument("--strict", action="store_true", help="Ejecuta los fixtures y falla si hay huecos de trazabilidad.")
    m.set_defaults(func=_cmd_matrix)

    e = sub.add_parser("explain", help="Muestra un requisito o una regla.")
    e.add_argument("id")
    e.set_defaults(func=_cmd_explain)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
