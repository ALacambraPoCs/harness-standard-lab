"""Reglas del núcleo agnóstico (nivel N0)."""
from __future__ import annotations

import datetime as dt
import subprocess

from .. import SUPPORTED_STANDARD
from ..context import Context
from ..markdown import imports, links
from ..matchers import walk_files
from ..model import Finding
from . import rule

DEFAULT_MAX_LINES = 200
WAIVER_MAX_DAYS = 90
WAIVER_WARN_DAYS = 14


@rule("core.manifest.valid", ["HS-GOV-001"], needs_valid_manifest=False)
def manifest_valid(ctx: Context):
    """El manifiesto existe, es YAML válido y valida contra schemas/manifest.schema.json."""
    path = ctx.standard.roles["manifest"]["ruta"]
    if not (ctx.root / path).is_file():
        yield Finding("core.manifest.valid", "HS-GOV-001", f"No existe {path}.",
                      "Crea el manifiesto (plantilla: template/core/.harness/manifest.yaml) o ejecuta `harness init`.", path)
        return
    if ctx.manifest is None:
        yield Finding("core.manifest.valid", "HS-GOV-001", f"{path} no se puede leer: {ctx.manifest_error}.",
                      "Corrige la sintaxis YAML; el documento raíz debe ser un objeto.", path)
        return
    for err in sorted(ctx.standard.validator("manifest").iter_errors(ctx.manifest), key=lambda e: list(e.absolute_path)):
        loc = "/".join(map(str, err.absolute_path)) or "(raíz)"
        yield Finding("core.manifest.valid", "HS-GOV-001", f"Manifiesto inválido en `{loc}`: {err.message}",
                      "Ajusta el campo al esquema schemas/manifest.schema.json.", path)


def _semver(v: str) -> tuple[int, int, int] | None:
    try:
        a, b, c = (int(x) for x in v.split("."))
        return a, b, c
    except (ValueError, AttributeError):
        return None


@rule("core.manifest.standard-version", ["HS-GOV-002"])
def standard_version(ctx: Context):
    """La versión declarada está soportada, no es posterior al estándar cargado y el nivel está definido."""
    declared = ctx.manifest["standard"]["version"]
    sv, cur = _semver(declared), _semver(ctx.standard.version)
    path = ctx.standard.roles["manifest"]["ruta"]
    if f"{sv[0]}.{sv[1]}" not in SUPPORTED_STANDARD:
        yield Finding("core.manifest.standard-version", "HS-GOV-002",
                      f"La versión del estándar {declared} no está soportada por esta CLI (soporta {', '.join(SUPPORTED_STANDARD)}.x).",
                      "Usa una versión de la CLI compatible o migra la instancia a una versión soportada.", path)
    elif cur and sv > cur:
        yield Finding("core.manifest.standard-version", "HS-GOV-002",
                      f"La instancia declara {declared}, posterior al estándar cargado ({ctx.standard.version}).",
                      "Actualiza la CLI a una versión que incluya ese estándar.", path)
    level = ctx.manifest["standard"]["level"]
    if level not in ctx.standard.defined_levels:
        yield Finding("core.manifest.standard-version", "HS-GOV-002",
                      f"El nivel {level} no tiene requisitos definidos en el estándar {ctx.standard.version} "
                      f"(definidos: {', '.join(ctx.standard.defined_levels)}).",
                      f"Declara un nivel definido ({ctx.standard.defined_levels[-1]} como máximo) hasta que el estándar especifique {level}.", path)


@rule("core.waivers.valid", ["HS-GOV-003"])
def waivers_valid(ctx: Context):
    """Cada waiver se refiere a un requisito exentable, dura ≤ 90 días y no ha caducado."""
    path = ctx.standard.roles["manifest"]["ruta"]
    for i, w in enumerate(ctx.manifest.get("waivers") or []):
        rid = w["requirement"]
        req = ctx.standard.requirements.get(rid)
        where = f"waivers[{i}] ({rid})"
        if req is None:
            yield Finding("core.waivers.valid", "HS-GOV-003", f"{where}: el requisito no existe en el estándar {ctx.standard.version}.",
                          "Corrige el ID o elimina el waiver.", path)
            continue
        if not req["exentable"]:
            yield Finding("core.waivers.valid", "HS-GOV-003", f"{where}: el requisito no es exentable.",
                          "Cumple el requisito; solo el grupo de gobierno puede autorizar una excepción mediante ADR.", path)
        approved, expires = dt.date.fromisoformat(w["approved_on"]), dt.date.fromisoformat(w["expires"])
        if (expires - approved).days > WAIVER_MAX_DAYS:
            yield Finding("core.waivers.valid", "HS-GOV-003",
                          f"{where}: dura {(expires - approved).days} días (máximo {WAIVER_MAX_DAYS}).",
                          "Reduce la caducidad; puedes renovarlo con un nuevo `approved_on`.", path)
        if approved > ctx.today:
            yield Finding("core.waivers.valid", "HS-GOV-003", f"{where}: `approved_on` está en el futuro.",
                          "Usa la fecha real de aprobación.", path)
        if expires < ctx.today:
            yield Finding("core.waivers.valid", "HS-GOV-003", f"{where}: caducó el {expires.isoformat()}.",
                          "Cumple el requisito o renueva el waiver con nueva aprobación.", path)
        elif (expires - ctx.today).days <= WAIVER_WARN_DAYS:
            yield Finding("core.waivers.valid", "HS-GOV-003",
                          f"{where}: caduca el {expires.isoformat()} ({(expires - ctx.today).days} días).",
                          "Planifica el cumplimiento o la renovación.", path, severity="warning")


@rule("core.roles.relocation", ["HS-GOV-006"])
def roles_relocation(ctx: Context):
    """Solo se reubican roles reubicables y hacia rutas existentes del tipo correcto."""
    path = ctx.standard.roles["manifest"]["ruta"]
    for role, target in (ctx.manifest.get("roles") or {}).items():
        spec = ctx.standard.roles.get(role)
        if spec is None:
            yield Finding("core.roles.relocation", "HS-GOV-006", f"Rol desconocido `{role}`.",
                          "Usa un rol de standard/roles.yaml.", path)
            continue
        if not spec["reubicable"]:
            yield Finding("core.roles.relocation", "HS-GOV-006", f"El rol `{role}` no es reubicable (ruta fija: {spec['ruta']}).",
                          f"Elimina `roles.{role}` del manifiesto y usa {spec['ruta']}.", path)
            continue
        p = ctx.root / target
        ok = p.is_file() if spec["tipo"] == "archivo" else p.is_dir()
        if not ok:
            yield Finding("core.roles.relocation", "HS-GOV-006",
                          f"`roles.{role}` apunta a `{target}`, que no existe como {spec['tipo']}.",
                          "Corrige la ruta o crea el archivo/directorio.", path)


@rule("core.instructions.root-exists", ["HS-INS-001"], needs_valid_manifest=False)
def root_instructions(ctx: Context):
    """Existe AGENTS.md en la raíz."""
    path = ctx.standard.roles["instructions.root"]["ruta"]
    if not (ctx.root / path).is_file():
        yield Finding("core.instructions.root-exists", "HS-INS-001", f"No existe {path} en la raíz.",
                      "Crea AGENTS.md como índice (plantilla: template/core/AGENTS.md).", path)


@rule("core.instructions.commands-match", ["HS-INS-002"])
def commands_match(ctx: Context):
    """AGENTS.md cita literalmente setup, check y test del manifiesto."""
    path = ctx.standard.roles["instructions.root"]["ruta"]
    text = ctx.read(path)
    if text is None:
        return
    for role in ("setup", "check", "test"):
        cmd = ctx.commands.get(role)
        if cmd and cmd not in text:
            yield Finding("core.instructions.commands-match", "HS-INS-002",
                          f"{path} no cita el comando `{role}` del manifiesto: `{cmd}`.",
                          f"Añade `{cmd}` literalmente a la sección de comandos de {path}.", path)


def _instruction_files(ctx: Context):
    return walk_files(ctx.root, {"AGENTS.md", "CLAUDE.md"})


@rule("core.instructions.references-resolve", ["HS-INS-005"])
def references_resolve(ctx: Context):
    """Todos los @imports y enlaces relativos de AGENTS.md/CLAUDE.md apuntan a rutas existentes."""
    for f in _instruction_files(ctx):
        rel = f.relative_to(ctx.root).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        for kind, items in (("import", imports(text)), ("enlace", links(text))):
            for line, target in items:
                if target.startswith("~"):
                    yield Finding("core.instructions.references-resolve", "HS-INS-005",
                                  f"{rel}:{line}: {kind} a ruta personal `{target}`.",
                                  "No referencies rutas del directorio personal en archivos versionados.", rel)
                    continue
                base = ctx.root if target.startswith("/") else f.parent
                resolved = (base / target.lstrip("/")).resolve()
                inside = ctx.root == resolved or ctx.root in resolved.parents
                if not inside or not resolved.exists():
                    yield Finding("core.instructions.references-resolve", "HS-INS-005",
                                  f"{rel}:{line}: el {kind} `{target}` no se resuelve.",
                                  "Corrige la ruta (relativa al archivo) o crea el destino. Claude Code ignora en silencio los imports rotos.", rel)


@rule("core.instructions.links-core-docs", ["HS-INS-008"])
def links_core_docs(ctx: Context):
    """AGENTS.md enlaza al mapa de arquitectura, a las decisiones y a la política de seguridad."""
    path = ctx.standard.roles["instructions.root"]["ruta"]
    text = ctx.read(path)
    if text is None:
        return
    targets = set()
    for _, t in links(text):
        targets.add((ctx.root / t).resolve())
    for role in ("architecture.map", "decisions.dir", "security.policy"):
        want = (ctx.root / ctx.role_path(role)).resolve()
        if not any(t == want or want in t.parents for t in targets):
            yield Finding("core.instructions.links-core-docs", "HS-INS-008",
                          f"{path} no enlaza al rol `{role}` ({ctx.role_path(role)}).",
                          f"Añade un enlace Markdown relativo, p. ej. [{role}]({ctx.role_path(role)}).", path)


@rule("core.instructions.size-budget", ["HS-CTX-001"])
def size_budget(ctx: Context):
    """Cada AGENTS.md/CLAUDE.md respeta el presupuesto de líneas."""
    budget = (ctx.manifest.get("budgets") or {}).get("instructions_max_lines", DEFAULT_MAX_LINES)
    for f in _instruction_files(ctx):
        n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        if n > budget:
            rel = f.relative_to(ctx.root).as_posix()
            yield Finding("core.instructions.size-budget", "HS-CTX-001",
                          f"{rel} tiene {n} líneas (presupuesto: {budget}).",
                          "Mueve el detalle a documentos enlazados, instrucciones locales de segmento o skills (divulgación progresiva).", rel)


def _exists_role(ctx: Context, role: str, rule_id: str, req: str, remedy: str):
    spec = ctx.standard.roles[role]
    path = ctx.role_path(role)
    p = ctx.root / path
    if spec["tipo"] == "archivo" and not p.is_file():
        yield Finding(rule_id, req, f"No existe {path} (rol `{role}`).", remedy, path)
    elif spec["tipo"] == "directorio":
        if not p.is_dir() or not any(p.glob("*.md")):
            yield Finding(rule_id, req, f"No existe {path}/ con al menos un archivo .md (rol `{role}`).", remedy, path)


@rule("core.architecture.map-exists", ["HS-ARC-001"])
def architecture_map(ctx: Context):
    """Existe el mapa de arquitectura."""
    yield from _exists_role(ctx, "architecture.map", "core.architecture.map-exists", "HS-ARC-001",
                            "Crea el mapa (plantilla: template/core/docs/architecture/ARCHITECTURE.md) o declara su ruta en `roles.architecture.map`.")


@rule("core.decisions.exists", ["HS-ARC-002"])
def decisions_dir(ctx: Context):
    """Existe el directorio de decisiones con al menos un .md."""
    yield from _exists_role(ctx, "decisions.dir", "core.decisions.exists", "HS-ARC-002",
                            "Crea docs/decisions/ con un README.md índice y tu primer ADR, o declara `roles.decisions.dir`.")


@rule("core.security.doc-exists", ["HS-SEC-001"])
def security_doc(ctx: Context):
    """Existe la política de seguridad."""
    yield from _exists_role(ctx, "security.policy", "core.security.doc-exists", "HS-SEC-001",
                            "Crea la política (plantilla: template/core/docs/security/SECURITY.md) o declara `roles.security.policy`.")


@rule("core.commands.declared", ["HS-VER-001"], needs_valid_manifest=False)
def commands_declared(ctx: Context):
    """El manifiesto declara setup, check y test."""
    if not isinstance(ctx.manifest, dict):
        return  # lo informa core.manifest.valid
    path = ctx.standard.roles["manifest"]["ruta"]
    for role in ("setup", "check", "test"):
        if not ctx.commands.get(role):
            yield Finding("core.commands.declared", "HS-VER-001", f"El manifiesto no declara el comando `{role}`.",
                          f"Añade `commands.{role}` con la invocación real (p. ej. `make {role}`).", path)


def _run(ctx: Context, cmd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, shell=True, cwd=ctx.root, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=ctx.command_timeout)
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-5:]
        return proc.returncode, " | ".join(tail)
    except subprocess.TimeoutExpired:
        return 124, f"tiempo agotado ({ctx.command_timeout}s)"


@rule("core.commands.execute", ["HS-VER-002"], needs_commands=True)
def commands_execute(ctx: Context):
    """setup y check terminan con código 0 sin entrada estándar."""
    for role in ("setup", "check"):
        cmd = ctx.commands.get(role)
        if not cmd:
            continue
        code, tail = _run(ctx, cmd)
        if code != 0:
            yield Finding("core.commands.execute", "HS-VER-002",
                          f"`{role}` (`{cmd}`) terminó con código {code}. Últimas líneas: {tail or '(sin salida)'}",
                          "Corrige el comando para que sea no interactivo y termine con 0 en un entorno limpio.")
            return  # si setup falla, check no es significativo


@rule("core.commands.idempotent", ["HS-VER-003"], needs_commands=True)
def commands_idempotent(ctx: Context):
    """Ejecutar setup dos veces termina con 0 ambas veces."""
    cmd = ctx.commands.get("setup")
    if not cmd:
        return
    for attempt in (1, 2):
        code, tail = _run(ctx, cmd)
        if code != 0:
            yield Finding("core.commands.idempotent", "HS-VER-003",
                          f"`setup` falló en la ejecución {attempt} de 2 (código {code}). {tail}",
                          "Haz que setup compruebe el estado antes de actuar (crear solo si no existe, instalar con lockfile).")
            return
