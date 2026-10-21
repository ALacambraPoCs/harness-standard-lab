"""Reglas introducidas en el estándar 0.2.0 (F2.5): anclas de contenido, segmentos, presupuestos,
rutas portables, ADR, referencias, plantilla de PR y estructura de tareas."""
from __future__ import annotations

import os
import re
import subprocess

import yaml

from ..context import Context
from ..markdown import imports, normalize, prose_lines
from ..matchers import SKIP_DIRS, walk_files
from ..model import Finding
from . import rule

ANCHOR = re.compile(r"<!--\s*harness:([a-z0-9-]+)\s*-->")
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)
ADR_FILE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
BAD_CHARS = re.compile(r'[:<>"|?*\\\x00-\x1f]')
DEFAULT_MAX_CONSTRAINTS = 15
CHAIN_MAX_BYTES = 32 * 1024
MIN_DUP_CHARS = 30


def sections(text: str) -> dict[str, str]:
    """Contenido de cada ancla <!-- harness:x --> hasta la siguiente (sin comentarios HTML)."""
    out, marks = {}, list(ANCHOR.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = re.sub(r"<!--.*?-->", "", text[m.end():end], flags=re.S)
        out[m.group(1)] = body.strip()
    return out


def _require_anchors(ctx: Context, path: str, anchors: list[str], rule_id: str, req: str, what: str):
    text = ctx.read(path)
    if text is None:
        return  # la existencia la verifica otro requisito
    secs = sections(text)
    missing = [a for a in anchors if not secs.get(a)]
    if missing:
        yield Finding(rule_id, req, f"{path}: faltan o están vacías las secciones {', '.join(f'harness:{a}' for a in missing)}.",
                      f"Añade las anclas `<!-- harness:… -->` con su contenido ({what}).", path)


# ─────────────── instrucciones ───────────────
@rule("core.instructions.root-anchors", ["HS-INS-009"])
def root_anchors(ctx: Context):
    """AGENTS.md raíz tiene resumen, comandos, restricciones y mapa con contenido."""
    yield from _require_anchors(ctx, ctx.standard.roles["instructions.root"]["ruta"],
                                ["resumen", "comandos", "restricciones", "mapa"],
                                "core.instructions.root-anchors", "HS-INS-009", "plantilla: template/core/AGENTS.md")


@rule("core.instructions.flow-anchor", ["HS-INS-010"])
def flow_anchor(ctx: Context):
    """AGENTS.md raíz explica el flujo de trabajo (dónde está la tarea y quién marca done)."""
    yield from _require_anchors(ctx, ctx.standard.roles["instructions.root"]["ruta"], ["flujo"],
                                "core.instructions.flow-anchor", "HS-INS-010", "ficha instructions.root")


@rule("core.instructions.constraints-budget", ["HS-CTX-002"])
def constraints_budget(ctx: Context):
    """El n.º de restricciones duras de AGENTS.md raíz no supera el presupuesto."""
    path = ctx.standard.roles["instructions.root"]["ruta"]
    text = ctx.read(path)
    if text is None:
        return
    body = sections(text).get("restricciones", "")
    n = sum(1 for l in body.splitlines() if re.match(r"^\s*([-*+]|\d+\.)\s+\S", l))
    budget = (ctx.manifest.get("budgets") or {}).get("instructions_max_constraints", DEFAULT_MAX_CONSTRAINTS)
    if n > budget:
        yield Finding("core.instructions.constraints-budget", "HS-CTX-002",
                      f"{path} tiene {n} restricciones duras (presupuesto: {budget}).",
                      "Deja solo lo que el agente nunca debe hacer; lo demás va a convenciones, linters o permisos.", path)


def _segment_agents(ctx: Context):
    root = ctx.root / ctx.standard.roles["instructions.root"]["ruta"]
    return [p for p in walk_files(ctx.root, {"AGENTS.md"}) if p != root]


@rule("core.instructions.chain-bytes", ["HS-CTX-003"])
def chain_bytes(ctx: Context):
    """La cadena AGENTS.md raíz → segmento más profundo cabe en 32 KiB."""
    files = {p.parent: p.stat().st_size for p in walk_files(ctx.root, {"AGENTS.md"})}
    for d in files:
        total = sum(size for anc, size in files.items() if anc == d or anc in d.parents)
        if total > CHAIN_MAX_BYTES and not any(other != d and d in other.parents for other in files):
            rel = (d / "AGENTS.md").relative_to(ctx.root).as_posix()
            yield Finding("core.instructions.chain-bytes", "HS-CTX-003",
                          f"La cadena de AGENTS.md hasta {rel} suma {total} bytes (máximo {CHAIN_MAX_BYTES}).",
                          "Reduce las instrucciones o muévelas a documentos enlazados: Codex trunca a partir de 32 KiB.", rel)


@rule("core.instructions.segment-anchors", ["HS-INS-011"])
def segment_anchors(ctx: Context):
    """Cada AGENTS.md de segmento tiene `ambito` y al menos otra sección con contenido."""
    for p in _segment_agents(ctx):
        rel = p.relative_to(ctx.root).as_posix()
        secs = {k: v for k, v in sections(p.read_text(encoding="utf-8", errors="replace")).items() if v}
        if "ambito" not in secs or len(secs) < 2:
            yield Finding("core.instructions.segment-anchors", "HS-INS-011",
                          f"{rel}: necesita `harness:ambito` y al menos otra sección con contenido.",
                          "Ver examples/fragmentos/segmento-AGENTS.md. Si el segmento no tiene reglas propias, borra el archivo.", rel)


@rule("core.instructions.segment-no-duplication", ["HS-INS-012"])
def segment_no_dup(ctx: Context):
    """Un AGENTS.md de segmento no repite líneas sustantivas de la raíz."""
    root = ctx.read(ctx.standard.roles["instructions.root"]["ruta"])
    if root is None:
        return
    base = {normalize(l) for _, l in prose_lines(root) if len(normalize(l)) >= MIN_DUP_CHARS}
    for p in _segment_agents(ctx):
        rel = p.relative_to(ctx.root).as_posix()
        dups = [n for n, l in prose_lines(p.read_text(encoding="utf-8", errors="replace"))
                if len(normalize(l)) >= MIN_DUP_CHARS and normalize(l) in base]
        if dups:
            yield Finding("core.instructions.segment-no-duplication", "HS-INS-012",
                          f"{rel} repite {len(dups)} línea(s) de AGENTS.md raíz (primera en la línea {dups[0]}).",
                          "El agente ya carga la raíz: deja en el segmento solo lo propio.", rel)


# ─────────────── adaptador claude-code ───────────────
@rule("adapter.claude.segment-adapter", ["HS-INS-013"])
def segment_adapter(ctx: Context):
    """Cada AGENTS.md de segmento tiene al lado un CLAUDE.md que importa @AGENTS.md."""
    for p in _segment_agents(ctx):
        c = p.parent / "CLAUDE.md"
        rel = c.relative_to(ctx.root).as_posix()
        text = c.read_text(encoding="utf-8", errors="replace") if c.is_file() else None
        if text is None or not any(t in ("AGENTS.md", "./AGENTS.md") for _, t in imports(text)):
            yield Finding("adapter.claude.segment-adapter", "HS-INS-013",
                          f"{rel} no existe o no importa `@AGENTS.md`: Claude Code no verá las instrucciones del segmento.",
                          "Crea el archivo con la línea `@AGENTS.md` (examples/fragmentos/segmento-CLAUDE.md). R-13.", rel)


@rule("adapter.claude.import-first", ["HS-INS-014"])
def import_first(ctx: Context):
    """`@AGENTS.md` es la primera línea no vacía de cada CLAUDE.md."""
    for c in walk_files(ctx.root, {"CLAUDE.md"}):
        rel = c.relative_to(ctx.root).as_posix()
        if rel.startswith(".claude/"):
            continue
        first = next((l.strip() for l in c.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()), "")
        if first not in ("@AGENTS.md", "@./AGENTS.md"):
            yield Finding("adapter.claude.import-first", "HS-INS-014",
                          f"{rel}: la primera línea no vacía es `{first[:40]}`, no `@AGENTS.md`.",
                          "Pon `@AGENTS.md` como primera línea: deja claro que AGENTS.md es la fuente.", rel)


@rule("adapter.claude.single-location", ["HS-INS-015"])
def single_location(ctx: Context):
    """No existe .claude/CLAUDE.md (una sola ubicación del adaptador)."""
    if (ctx.root / ".claude" / "CLAUDE.md").is_file():
        yield Finding("adapter.claude.single-location", "HS-INS-015", "Existe .claude/CLAUDE.md además del CLAUDE.md raíz.",
                      "Une su contenido en CLAUDE.md raíz (sección harness:claude) y borra .claude/CLAUDE.md.", ".claude/CLAUDE.md")


# ─────────────── gobierno ───────────────
def _tracked_paths(ctx: Context) -> list[str]:
    if (ctx.root / ".git").exists():
        try:
            out = subprocess.run(["git", "ls-files", "-z"], cwd=ctx.root, capture_output=True, check=True).stdout
            return [p for p in out.decode("utf-8", "replace").split("\0") if p]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    out = []
    for dirpath, dirnames, filenames in os.walk(ctx.root):
        dirnames[:] = [d for d in dirnames if d != ".git" and d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, ctx.root)
        out += [os.path.normpath(os.path.join(rel, f)).replace(os.sep, "/") for f in filenames]
    return out


@rule("core.paths.portable", ["HS-GOV-008"], needs_valid_manifest=False)
def portable_paths(ctx: Context):
    """Ninguna ruta versionada contiene caracteres no válidos en Windows ni acaba en espacio o punto."""
    bad = [p for p in _tracked_paths(ctx)
           if any(BAD_CHARS.search(seg) or seg.endswith((" ", ".")) for seg in p.split("/") if seg not in (".", ".."))]
    if bad:
        yield Finding("core.paths.portable", "HS-GOV-008",
                      f"{len(bad)} ruta(s) no portables, p. ej.: {', '.join(bad[:3])}.",
                      "Renómbralas o elimínalas. Si vienen de Windows (`*:Zone.Identifier`), bórralas e ignóralas en .gitignore (R-11).")


@rule("core.manifest.docs-language", ["HS-GOV-007"])
def docs_language(ctx: Context):
    """El manifiesto declara project.docs_language."""
    if not (ctx.manifest.get("project") or {}).get("docs_language"):
        yield Finding("core.manifest.docs-language", "HS-GOV-007", "El manifiesto no declara `project.docs_language`.",
                      "Añade el idioma de los documentos de la instancia (p. ej. `docs_language: es`, D-020).",
                      ctx.standard.roles["manifest"]["ruta"])


# ─────────────── arquitectura y decisiones ───────────────
@rule("core.architecture.anchors", ["HS-ARC-003"])
def architecture_anchors(ctx: Context):
    """El mapa de arquitectura tiene visión, mapa de código, límites e invariantes."""
    yield from _require_anchors(ctx, ctx.role_path("architecture.map"), ["vision", "mapa-codigo", "limites", "invariantes"],
                                "core.architecture.anchors", "HS-ARC-003", "plantilla: template/core/docs/architecture/ARCHITECTURE.md")


def _adrs(ctx: Context):
    d = ctx.root / ctx.role_path("decisions.dir")
    return sorted(p for p in d.glob("*.md") if ADR_FILE.match(p.name)) if d.is_dir() else []


@rule("core.decisions.index", ["HS-ARC-004"])
def decisions_index(ctx: Context):
    """El README de decisiones tiene `indice` y enumera todos los ADR."""
    ddir = ctx.role_path("decisions.dir").rstrip("/")
    path = f"{ddir}/README.md"
    text = ctx.read(path)
    if text is None:
        yield Finding("core.decisions.index", "HS-ARC-004", f"No existe {path}.",
                      "Crea el índice (plantilla: template/core/docs/decisions/README.md).", path)
        return
    idx = sections(text).get("indice")
    if not idx:
        yield Finding("core.decisions.index", "HS-ARC-004", f"{path} no tiene la sección `harness:indice` con contenido.",
                      "Añade el ancla y la tabla número · título · estado.", path)
        return
    missing = [p.name for p in _adrs(ctx) if p.name not in idx]
    if missing:
        yield Finding("core.decisions.index", "HS-ARC-004", f"El índice de {path} no enlaza: {', '.join(missing[:5])}.",
                      "Añade una fila por ADR con enlace a su archivo.", path)


@rule("core.decisions.frontmatter", ["HS-ARC-005"])
def decisions_frontmatter(ctx: Context):
    """Cada ADR NNNN-*.md tiene frontmatter válido (schemas/adr.schema.json) e id igual al número."""
    validator = ctx.standard.validator("adr")
    for p in _adrs(ctx):
        rel = p.relative_to(ctx.root).as_posix()
        m = FRONT.match(p.read_text(encoding="utf-8", errors="replace"))
        try:
            meta = yaml.safe_load(m.group(1)) if m else None
        except yaml.YAMLError:
            meta = None
        if not isinstance(meta, dict):
            yield Finding("core.decisions.frontmatter", "HS-ARC-005", f"{rel}: sin frontmatter YAML válido.",
                          "Usa el formato de docs/decisions/_plantilla.md.", rel)
            continue
        meta = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in meta.items()}
        for err in validator.iter_errors(meta):
            loc = "/".join(map(str, err.absolute_path)) or "(raíz)"
            yield Finding("core.decisions.frontmatter", "HS-ARC-005", f"{rel}: `{loc}`: {err.message}",
                          "Ajusta el frontmatter a schemas/adr.schema.json.", rel)
        num = ADR_FILE.match(p.name).group(1)
        if meta.get("id") != f"ADR-{num}":
            yield Finding("core.decisions.frontmatter", "HS-ARC-005", f"{rel}: `id` debe ser ADR-{num}.",
                          "Usa el mismo número en el nombre del archivo y en `id`.", rel)


# ─────────────── seguridad y contexto ───────────────
@rule("core.security.anchors", ["HS-SEC-005"])
def security_anchors(ctx: Context):
    """La política de seguridad tiene secretos, entradas no confiables, aprobaciones y controles."""
    yield from _require_anchors(ctx, ctx.role_path("security.policy"),
                                ["secretos", "entradas-no-confiables", "aprobaciones", "controles"],
                                "core.security.anchors", "HS-SEC-005", "plantilla: template/core/docs/security/SECURITY.md")


@rule("core.references.provenance", ["HS-CTX-004"])
def references_provenance(ctx: Context):
    """Si hay referencias externas: índice con `indice` y cada archivo con `Fuente:` y fecha."""
    d = ctx.root / ctx.role_path("references.dir")
    if not d.is_dir():
        return
    rel_dir = ctx.role_path("references.dir").rstrip("/")
    readme = ctx.read(f"{rel_dir}/README.md")
    idx = sections(readme).get("indice", "") if readme else ""
    if not idx:
        yield Finding("core.references.provenance", "HS-CTX-004", f"{rel_dir}/README.md no existe o no tiene `harness:indice`.",
                      "Crea el índice (examples/fragmentos/references-README.md).", f"{rel_dir}/README.md")
    for p in sorted(x for x in d.iterdir() if x.is_file() and x.name != "README.md" and not x.name.startswith(".")):
        head = "\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[:5])
        rel = p.relative_to(ctx.root).as_posix()
        if not re.search(r"Fuente:\s*\S+.*\d{4}-\d{2}-\d{2}", head):
            yield Finding("core.references.provenance", "HS-CTX-004", f"{rel}: no indica `Fuente: <url> · Capturado: AAAA-MM-DD`.",
                          "Añade la procedencia en las primeras líneas.", rel)
        elif idx and p.name not in idx:
            yield Finding("core.references.provenance", "HS-CTX-004", f"{rel} no figura en el índice.", "Añádelo al índice.", rel)


# ─────────────── CI y PR (github) ───────────────
@rule("core.pr.template", ["HS-CI-001"], platform="github")
def pr_template(ctx: Context):
    """Existe la plantilla de PR con tarea, riesgo, evidencia y sensible."""
    path = ctx.role_path("pr.template")
    if ctx.read(path) is None:
        yield Finding("core.pr.template", "HS-CI-001", f"No existe {path}.",
                      "Copia template/adapters/github/.github/pull_request_template.md.", path)
        return
    yield from _require_anchors(ctx, path, ["tarea", "riesgo", "evidencia", "sensible"], "core.pr.template", "HS-CI-001",
                                "plantilla: template/adapters/github/.github/pull_request_template.md")


TASKS_REUSABLE = "harness-tasks-lifecycle.yml"


@rule("core.ci.tasks-workflow", ["HS-CI-003"], platform="github")
def tasks_workflow(ctx: Context):
    """Un workflow llama a harness-tasks-lifecycle.yml (o ejecuta `harness tasks validate`) en pull_request."""
    wdir = ctx.root / ctx.standard.roles["ci.workflows"]["ruta"]
    for wf in sorted(list(wdir.glob("*.yml")) + list(wdir.glob("*.yaml"))) if wdir.is_dir() else []:
        text = wf.read_text(encoding="utf-8", errors="replace")
        if TASKS_REUSABLE not in text and "harness tasks validate" not in text:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        on = doc.get("on", doc.get(True))
        if "pull_request" in ([on] if isinstance(on, str) else (on or [])):
            return
    yield Finding("core.ci.tasks-workflow", "HS-CI-003", "Ningún workflow ejecuta el ciclo de vida de tareas en `pull_request`.",
                  "Copia template/niveles/n1/.github/workflows/harness-tasks.yml y marca `harness tasks` como check requerido.",
                  ctx.standard.roles["ci.workflows"]["ruta"])


# ─────────────── estado ───────────────
@rule("core.plans.structure", ["HS-STA-001"])
def plans_structure(ctx: Context):
    """Existen plans.dir, plans.active y plans.completed."""
    for role in ("plans.dir", "plans.active", "plans.completed"):
        path = ctx.role_path(role)
        if not (ctx.root / path).is_dir():
            yield Finding("core.plans.structure", "HS-STA-001", f"No existe el directorio {path}/ (rol `{role}`).",
                          "Copia template/niveles/n1/docs/plans/ (con .gitkeep en active/ y completed/).", path)
