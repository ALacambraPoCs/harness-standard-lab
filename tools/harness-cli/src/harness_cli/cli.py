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
    if not (fixtures / "cases.yaml").is_file():
        print(f"No existe {fixtures / 'cases.yaml'}. En el repo central usa: harness --standard-root . matrix", file=sys.stderr)
        return 2
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


def _cmd_roles(args) -> int:
    from .roles_table import render_into, table
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    if not args.write:
        print(table(std))
        return 0
    doc = std.root / "standard" / "03-estructura-canonica.md"
    if not doc.is_file():
        print(f"No existe {doc}. En el repo central usa: harness --standard-root . roles --write", file=sys.stderr)
        return 2
    old = doc.read_text(encoding="utf-8")
    new = render_into(old, std)
    if args.check:
        if new != old:
            print(f"{doc} está desactualizado: ejecuta `harness roles --write`.", file=sys.stderr)
            return 1
        return 0
    doc.write_text(new, encoding="utf-8")
    print(f"Tabla de roles actualizada en {doc}")
    return 0


def _print_findings(findings, title: str, fmt: str) -> int:
    import json
    errors = [f for f in findings if f.severity == "error"]
    if fmt == "json":
        print(json.dumps({"title": title, "errors": len(errors), "warnings": len(findings) - len(errors),
                          "findings": [f.to_dict() for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(title)
        for f in findings:
            print(f"{'✗' if f.severity == 'error' else '!'} [{f.severity.upper()}] {f.rule}" + (f"  ({f.path})" if f.path else ""))
            print(f"    QUÉ:   {f.message}")
            print(f"    CÓMO:  {f.remedy}")
        print(f"Resultado: {len(errors)} error(es), {len(findings) - len(errors)} aviso(s).")
    return 1 if errors else 0


def _ctx(args):
    from .context import Context
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    return Context.build(Path(args.path), std, dt.date.today())


def _cmd_tasks(args) -> int:
    from . import tasks as T
    ctx = _ctx(args)
    if args.tasks_cmd == "validate":
        approvers = {a.strip().lstrip("@").lower() for a in args.approvers.split(",") if a.strip()} if args.approvers is not None else None
        findings, found = T.validate(ctx, base=args.base, pr_number=args.pr_number, run_acceptance=args.run_acceptance,
                                     approvers=approvers)
        return _print_findings(findings, f"harness tasks validate · {len(found)} tarea(s)", args.format)
    if args.tasks_cmd == "issue-sync":
        import json
        import os
        base = None if (args.base or "").strip("0") == "" else args.base
        ops = T.plan_issue_sync(ctx, base, run_url=args.run_url or "")
        if args.dry_run:
            print(json.dumps(ops, ensure_ascii=False, indent=2))
            return 0
        token, repo = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", "")
        if not token or not repo:
            print("Faltan GITHUB_TOKEN o GITHUB_REPOSITORY.", file=sys.stderr)
            return 2
        for line in T.apply_issue_ops(ops, repo, token) or ["Sin cambios que reflejar."]:
            print(line)
        return 0
    if args.tasks_cmd == "close":
        try:
            changed = T.close(ctx, args.task_id, args.pr, resultado=args.resultado,
                              verified_by=args.verified_by, autor=args.autor)
        except T.CloseError as exc:
            print(f"harness tasks close: {exc}. No se ha modificado nada.", file=sys.stderr)
            return 2
        if not changed:
            print(f"{args.task_id} ya estaba cerrada con el PR #{args.pr}. Sin cambios.")
            return 0
        print(f"{args.task_id} → done (PR #{args.pr}). Archivos modificados (inclúyelos en el commit):")
        for c in changed:
            print(f"  {c}")
        return 0
    # index
    findings, found = T.validate(ctx)
    path = ctx.root / ctx.role_path("plans.index")
    new = T.render_index(found)
    if args.check:
        old = path.read_text(encoding="utf-8") if path.is_file() else ""
        if old != new:
            print(f"{path.relative_to(ctx.root)} está desactualizado: ejecuta `harness tasks index --write`.", file=sys.stderr)
            return 1
        print("Índice de tareas al día.")
        return 0
    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
        print(f"Índice escrito en {path.relative_to(ctx.root)} ({len(found)} tarea(s)).")
        return 0
    print(new)
    return 0


def _cmd_pr(args) -> int:
    import os
    from . import tasks as T
    ctx = _ctx(args)
    if args.pr_cmd == "risk":
        import json
        from .risk import compute
        r = compute(ctx, args.base)
        if args.format == "json":
            print(json.dumps(r.as_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Riesgo calculado: {r.clase}")
            for c, m in r.senales:
                print(f"  [{c}] {m}")
        if args.github_output and os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
                fh.write(f"clase={r.clase}\n")
        return 0
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    else:
        body = os.environ.get(args.body_env, "")
    title = os.environ.get(args.title_env, "") if args.title_env else ""
    return _print_findings(T.check_pr(ctx, body, args.base, title=title), "harness pr check", args.format)


def _cmd_platform(args) -> int:
    import os
    from . import platform as P
    ctx = _ctx(args)
    repo = args.repo or os.environ.get("GITHUB_REPOSITORY") or P.repo_from_git(ctx)
    if not repo:
        print("No se pudo deducir el repositorio: usa --repo dueño/repo.", file=sys.stderr)
        return 2
    try:
        findings = P.check(ctx, repo, args.branch, P.http_fetch(P.resolve_token()))
    except P.Inaccesible as exc:
        print(f"No se puede contactar con la API de GitHub: {exc}", file=sys.stderr)
        return 2
    return _print_findings(findings, f"harness platform check · {repo} · {ctx.level}", args.format)


def _cmd_catalog(args) -> int:
    from .catalog import render_index, update_readme, validate
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    if args.catalog_cmd == "index":
        readme = Path(args.path) / args.catalog / "README.md"
        old = readme.read_text(encoding="utf-8")
        new = update_readme(old, render_index(Path(args.path), args.catalog))
        if args.check:
            if new != old:
                print(f"{readme} está desactualizado: ejecuta `harness catalog index --write`.", file=sys.stderr)
                return 1
            print("Índice del catálogo al día.")
            return 0
        if args.write:
            readme.write_text(new, encoding="utf-8")
            print(f"Índice escrito en {readme}.")
            return 0
        print(render_index(Path(args.path), args.catalog))
        return 0
    findings, n = validate(std, Path(args.path), args.catalog, base=args.base)
    return _print_findings(findings, f"harness catalog validate · {n} componente(s)", args.format)


def _cmd_components(args) -> int:
    from . import distribucion as D
    std = load_standard(Path(args.standard_root) if args.standard_root else None)
    root = Path(args.path)
    try:
        if args.components_cmd == "add":
            log = D.add(root, std, args.ids)
        elif args.components_cmd == "sync":
            log = D.sync(root, std)
        elif args.components_cmd == "remove":
            log = D.remove(root, std, args.ids)
        else:
            log = D.listado(root, std)
    except D.DistribucionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("\n".join(log) or "Nada que hacer.")
    if args.components_cmd in ("add", "sync", "remove"):
        print(f"Revisa el diff ({D.LOCK}, archivos y {D.SETTINGS}) y súbelo en un PR: son rutas sensibles (ADR-013).")
    return 0


def build_parser() -> argparse.ArgumentParser:
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

    r = sub.add_parser("roles", help="Tabla de roles (estructura canónica) desde standard/roles.yaml.")
    r.add_argument("--write", action="store_true", help="Actualiza la tabla generada en standard/03-estructura-canonica.md.")
    r.add_argument("--check", action="store_true", help="Con --write: no escribe; falla si la tabla está desactualizada.")
    r.set_defaults(func=_cmd_roles)

    t = sub.add_parser("tasks", help="Ciclo de vida de tareas (ADR-005, ADR-016).")
    tsub = t.add_subparsers(dest="tasks_cmd", required=True)
    tv = tsub.add_parser("validate", help="Valida archivos de tarea y, con --base, sus transiciones.")
    tv.add_argument("--path", default=".")
    tv.add_argument("--base", help="Referencia git base (p. ej. origin/main) para validar transiciones.")
    tv.add_argument("--pr-number", type=int, help="Número del PR (exige done_pr igual).")
    tv.add_argument("--run-acceptance", action="store_true", help="Ejecuta los criterios de aceptación de las tareas que pasan a done.")
    tv.add_argument("--approvers", help="Logins (separados por comas) que han aprobado el PR, para criterios manuales.")
    tv.add_argument("--format", choices=["text", "json"], default="text")
    tv.set_defaults(func=_cmd_tasks)
    ts = tsub.add_parser("issue-sync", help="X-01: refleja estado y responsable de las tareas cambiadas en sus issues.")
    ts.add_argument("--path", default=".")
    ts.add_argument("--base", help="Commit anterior (p. ej. github.event.before). Vacío o ceros = todas.")
    ts.add_argument("--run-url", help="URL de la ejecución de CI para el comentario de evidencia.")
    ts.add_argument("--dry-run", action="store_true", help="Solo muestra las operaciones.")
    ts.set_defaults(func=_cmd_tasks)
    tc = tsub.add_parser("close", help="Lleva una tarea a done tras abrir su PR (ADR-016): mueve, done_pr, progreso e índice.")
    tc.add_argument("task_id", metavar="T-NNNN")
    tc.add_argument("--pr", type=int, required=True, help="Número del PR que cierra la tarea.")
    tc.add_argument("--resultado", help="Texto de la sección Resultado (obligatorio si está vacía).")
    tc.add_argument("--verified-by", help="Persona que verificó los criterios manuales (debe aprobar el PR).")
    tc.add_argument("--autor", help="Autor de la línea de progreso (por defecto, el owner de la tarea).")
    tc.add_argument("--path", default=".")
    tc.set_defaults(func=_cmd_tasks)
    ti = tsub.add_parser("index", help="Genera o comprueba el índice de tareas (plans.index).")
    ti.add_argument("--path", default=".")
    ti.add_argument("--write", action="store_true")
    ti.add_argument("--check", action="store_true")
    ti.set_defaults(func=_cmd_tasks)

    pr = sub.add_parser("pr", help="Comprobaciones de pull request.")
    prsub = pr.add_subparsers(dest="pr_cmd", required=True)
    pc = prsub.add_parser("check", help="Valida el cuerpo del PR contra el diff y las tareas (pr.template, D-023).")
    pc.add_argument("--path", default=".")
    pc.add_argument("--base", required=True, help="Referencia git base del PR (p. ej. origin/main).")
    g = pc.add_mutually_exclusive_group(required=True)
    g.add_argument("--body-file")
    g.add_argument("--body-env", help="Variable de entorno con el cuerpo del PR (evita inyección en el shell).")
    pc.add_argument("--title-env", help="Variable de entorno con el título del PR.")
    pc.add_argument("--format", choices=["text", "json"], default="text")
    pc.set_defaults(func=_cmd_pr)
    prr = prsub.add_parser("risk", help="Calcula la clase de riesgo mínima del PR a partir del diff y las tareas (D-058).")
    prr.add_argument("--path", default=".")
    prr.add_argument("--base", required=True, help="Referencia git base del PR (p. ej. origin/main).")
    prr.add_argument("--format", choices=["text", "json"], default="text")
    prr.add_argument("--github-output", action="store_true", help="Escribe `clase=<clase>` en $GITHUB_OUTPUT.")
    prr.set_defaults(func=_cmd_pr)

    pl = sub.add_parser("platform", help="Autoridad comprobable: ruleset y environments reales en GitHub (F5.3-A).")
    plsub = pl.add_subparsers(dest="platform_cmd", required=True)
    plc = plsub.add_parser("check", help="Compara el ruleset y los environments con lo que exige el nivel. Solo lee.")
    plc.add_argument("--path", default=".")
    plc.add_argument("--repo", help="dueño/repo (por defecto, GITHUB_REPOSITORY o el remoto origin).")
    plc.add_argument("--branch", help="Rama a comprobar (por defecto, la rama por defecto del repositorio).")
    plc.add_argument("--format", choices=["text", "json"], default="text")
    plc.set_defaults(func=_cmd_platform)

    cg = sub.add_parser("catalog", help="Catálogo de componentes del repositorio central (F3).")
    cgsub = cg.add_subparsers(dest="catalog_cmd", required=True)
    cv = cgsub.add_parser("validate", help="Valida entradas, fichas, skills y (con --base) transiciones y versiones.")
    cv.add_argument("--path", default=".", help="Raíz del repositorio central (por defecto: .)")
    cv.add_argument("--catalog", default="catalog", help="Directorio del catálogo (por defecto: catalog)")
    cv.add_argument("--base", help="Referencia git base para validar transiciones de estado y subidas de versión.")
    cv.add_argument("--format", choices=["text", "json"], default="text")
    cv.set_defaults(func=_cmd_catalog)
    ci = cgsub.add_parser("index", help="Genera o comprueba el índice de catalog/README.md.")
    ci.add_argument("--path", default=".")
    ci.add_argument("--catalog", default="catalog")
    ci.add_argument("--write", action="store_true")
    ci.add_argument("--check", action="store_true")
    ci.set_defaults(func=_cmd_catalog)

    co = sub.add_parser("components", help="Instala y actualiza componentes del catálogo en una instancia (ADR-017).")
    cosub = co.add_subparsers(dest="components_cmd", required=True)
    for name, hlp, ids in (("add", "Instala componentes (y sus dependencias) desde el catálogo de esta CLI.", True),
                           ("remove", "Retira componentes instalados sin cambios locales.", True),
                           ("sync", "Actualiza los componentes instalados a la versión del catálogo de esta CLI.", False),
                           ("list", "Lista el catálogo y el estado de lo instalado.", False)):
        sp = cosub.add_parser(name, help=hlp)
        if ids:
            sp.add_argument("ids", nargs="+")
        sp.add_argument("--path", default=".")
        sp.set_defaults(func=_cmd_components)

    e = sub.add_parser("explain", help="Muestra un requisito o una regla.")
    e.add_argument("id")
    e.set_defaults(func=_cmd_explain)

    return p


def main(argv: list[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
