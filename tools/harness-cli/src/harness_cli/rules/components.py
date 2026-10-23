"""Reglas de componentes y del adaptador de Claude Code (estándar 0.3.0, F3.3; 0.5.0, F3.7)."""
from __future__ import annotations

import json
import re

import yaml

from ..context import Context
from ..matchers import compile_pattern
from ..model import Finding
from ..skills import validate_skill
from . import rule
from .n1 import FRONT, sections

SETTINGS = ".claude/settings.json"
MIN_CLAUDE = (2, 1, 277)
SECRET_SAMPLES = [".env", ".env.production", "config/.env"]
CMD_PATH = re.compile(r"(?:\$\{CLAUDE_PROJECT_DIR\}|\$CLAUDE_PROJECT_DIR|\"\$CLAUDE_PROJECT_DIR\")/([^\s\"']+)")


def _skills(ctx: Context):
    base = ctx.root / ".claude" / "skills"
    if not base.is_dir():
        return []
    return sorted(d for d in base.iterdir() if d.is_dir())


def _reports(ctx: Context):
    if "skills" not in ctx._cache:
        out = []
        for d in _skills(ctx):
            md = d / "SKILL.md"
            rel = md.relative_to(ctx.root).as_posix()
            out.append((rel, validate_skill(md, rel) if md.is_file() else None))
        ctx._cache["skills"] = out
    return ctx._cache["skills"]


@rule("adapter.claude.skills-spec", ["HS-CMP-001"])
def skills_spec(ctx: Context):
    """Cada .claude/skills/<name>/ tiene SKILL.md conforme a la especificación de Agent Skills."""
    for rel, rep in _reports(ctx):
        if rep is None:
            yield Finding("adapter.claude.skills-spec", "HS-CMP-001", f"{rel} no existe.",
                          "Cada directorio de .claude/skills/ es una skill y necesita SKILL.md.", rel)
            continue
        for e in rep.spec:
            yield Finding("adapter.claude.skills-spec", "HS-CMP-001", f"{rel}: {e}.",
                          "Ajusta el frontmatter a agentskills.io/specification (ADR-012).", rel)


@rule("adapter.claude.skills-profile", ["HS-CMP-002"])
def skills_profile(ctx: Context):
    """Las skills usan solo los campos de su perfil (portable por defecto)."""
    for rel, rep in _reports(ctx):
        if rep is None or rep.spec:
            continue
        for e in rep.profile:
            yield Finding("adapter.claude.skills-profile", "HS-CMP-002", f"{rel}: {e}.",
                          "Las skills portables solo usan los campos de Agent Skills (ADR-012).", rel)


@rule("core.skills.no-agents-dir", ["HS-CMP-003"], needs_valid_manifest=False)
def no_agents_dir(ctx: Context):
    """No se versiona .agents/skills/ en la v1 (ADR-012)."""
    if (ctx.root / ".agents" / "skills").is_dir():
        yield Finding("core.skills.no-agents-dir", "HS-CMP-003", "Existe .agents/skills/ en la instancia.",
                      "La fuente canónica es .claude/skills/ (ADR-012); .agents/skills/ solo lo generará `harness sync` cuando un adaptador lo necesite.",
                      ".agents/skills")


def _agents(ctx: Context):
    base = ctx.root / ".claude" / "agents"
    out = []
    for p in sorted(base.glob("*.md")) if base.is_dir() else []:
        rel = p.relative_to(ctx.root).as_posix()
        m = FRONT.match(p.read_text(encoding="utf-8", errors="replace"))
        try:
            meta = yaml.safe_load(m.group(1)) if m else None
        except yaml.YAMLError:
            meta = None
        out.append((rel, meta if isinstance(meta, dict) else None))
    return out


@rule("adapter.claude.agents-valid", ["HS-CMP-004"])
def agents_valid(ctx: Context):
    """Cada subagente de .claude/agents/ tiene frontmatter con `name` y `description`, y nombres únicos."""
    seen: dict[str, str] = {}
    for rel, meta in _agents(ctx):
        if meta is None:
            yield Finding("adapter.claude.agents-valid", "HS-CMP-004", f"{rel}: sin frontmatter YAML válido.",
                          "Empieza el archivo con --- name/description --- (code.claude.com/docs/en/sub-agents).", rel)
            continue
        for k in ("name", "description"):
            if not isinstance(meta.get(k), str) or not meta[k].strip():
                yield Finding("adapter.claude.agents-valid", "HS-CMP-004", f"{rel}: falta `{k}`.",
                              "`name` y `description` son obligatorios.", rel)
        n = meta.get("name")
        if isinstance(n, str) and n in seen:
            yield Finding("adapter.claude.agents-valid", "HS-CMP-004", f"{rel}: `name` {n} duplicado (también en {seen[n]}).",
                          "Cada subagente necesita un nombre único.", rel)
        elif isinstance(n, str):
            seen[n] = rel


@rule("adapter.claude.agents-tools", ["HS-CMP-005"])
def agents_tools(ctx: Context):
    """Cada subagente declara `tools` (lista explícita: privilegio mínimo)."""
    for rel, meta in _agents(ctx):
        if meta is not None and not meta.get("tools"):
            yield Finding("adapter.claude.agents-tools", "HS-CMP-005",
                          f"{rel}: no declara `tools`, así que hereda todas las herramientas.",
                          "Declara solo las que necesita, p. ej. `tools: Read, Grep, Glob` para un revisor.", rel)


def _settings(ctx: Context):
    if "settings" not in ctx._cache:
        text = ctx.read(SETTINGS)
        try:
            ctx._cache["settings"] = (json.loads(text) if text is not None else None, None)
        except json.JSONDecodeError as exc:
            ctx._cache["settings"] = (None, str(exc))
    return ctx._cache["settings"]


def _hooks(ctx: Context):
    data, _ = _settings(ctx)
    out = []
    hooks = (data or {}).get("hooks") if isinstance(data, dict) else None
    for event, groups in (hooks or {}).items() if isinstance(hooks, dict) else []:
        for g in groups if isinstance(groups, list) else []:
            for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
                if isinstance(h, dict):
                    out.append((event, h))
    return out


@rule("adapter.claude.hooks-scripts", ["HS-CMP-006"])
def hooks_scripts(ctx: Context):
    """Los hooks de comando que referencian scripts del proyecto apuntan a archivos versionados existentes."""
    for event, h in _hooks(ctx):
        if h.get("type") != "command":
            continue
        for target in CMD_PATH.findall(str(h.get("command", ""))):
            p = (ctx.root / target).resolve()
            if ctx.root not in p.parents or not p.is_file():
                yield Finding("adapter.claude.hooks-scripts", "HS-CMP-006",
                              f"Hook {event}: el script `{target}` no existe en el repositorio.",
                              "Versiona el script (p. ej. en .claude/hooks/) o corrige la ruta. Un hook roto falla en silencio.", SETTINGS)


@rule("adapter.claude.hooks-nondeterministic", ["HS-CMP-007"])
def hooks_nondeterministic(ctx: Context):
    """Si hay hooks prompt/agent, la política de seguridad no presenta hooks como control."""
    nd = sorted({f"{e}:{h.get('type')}" for e, h in _hooks(ctx) if h.get("type") in ("prompt", "agent")})
    if not nd:
        return
    text = ctx.read(ctx.role_path("security.policy")) or ""
    if re.search(r"\bhooks?\b", sections(text).get("controles", ""), re.I):
        yield Finding("adapter.claude.hooks-nondeterministic", "HS-CMP-007",
                      f"Hay hooks no deterministas ({', '.join(nd)}) y la tabla harness:controles menciona hooks.",
                      "Comprueba que ningún control de la tabla depende de un hook prompt o agent (ADR-009, C9); solo cuentan los de tipo command.",
                      ctx.role_path("security.policy"))


@rule("adapter.claude.min-version", ["HS-CMP-008"])
def min_version(ctx: Context):
    """El manifiesto exige al menos la versión mínima verificada del adaptador."""
    for a in (ctx.manifest.get("adapters") or {}).get("agents") or []:
        if a.get("id") != "claude-code":
            continue
        try:
            v = tuple(int(x) for x in str(a.get("min_version")).split("."))
        except ValueError:
            continue
        if v < MIN_CLAUDE:
            yield Finding("adapter.claude.min-version", "HS-CMP-008",
                          f"`min_version` {a.get('min_version')} es anterior a la mínima del adaptador ({'.'.join(map(str, MIN_CLAUDE))}).",
                          "Sube `adapters.agents[claude-code].min_version` (standard/adaptadores/claude-code.md §1).",
                          ctx.standard.roles["manifest"]["ruta"])


# ─────────────── settings.json ───────────────
def _rules(data, kinds: tuple[str, ...], tool: str) -> list[str]:
    perms = data.get("permissions") if isinstance(data, dict) else None
    out = []
    for k in kinds:
        for r in (perms or {}).get(k) or []:
            m = re.fullmatch(rf"{tool}\((.+)\)", str(r).strip())
            if m and not m.group(1).startswith(("//", "~")):
                out.append(m.group(1).removeprefix("./"))
    return out


def _covered(patterns: list[str], path: str) -> bool:
    return any(compile_pattern(p).match(path) for p in patterns)


@rule("adapter.claude.settings-secrets", ["HS-SEC-007"])
def settings_secrets(ctx: Context):
    """Existe .claude/settings.json válido con deny de lectura y edición de .env y .env.*."""
    data, err = _settings(ctx)
    if data is None:
        msg = f"{SETTINGS} no es JSON válido: {err}." if err else f"No existe {SETTINGS}."
        yield Finding("adapter.claude.settings-secrets", "HS-SEC-007", msg,
                      "Copia template/adapters/claude-code/.claude/settings.json (ficha adapter.claude.settings).", SETTINGS)
        return
    for tool in ("Read", "Edit"):
        pats = _rules(data, ("deny",), tool)
        missing = [s for s in SECRET_SAMPLES if not _covered(pats, s)]
        if missing:
            yield Finding("adapter.claude.settings-secrets", "HS-SEC-007",
                          f"permissions.deny no impide {tool} de {', '.join(missing)}.",
                          f"Añade `{tool}(.env)` y `{tool}(.env.*)` a permissions.deny.", SETTINGS)


@rule("adapter.claude.settings-sensitive", ["HS-SEC-008"])
def settings_sensitive(ctx: Context):
    """Cada ruta sensible de roles.yaml queda cubierta por una regla ask o deny de Edit."""
    data, _ = _settings(ctx)
    if data is None:
        return  # lo informa adapter.claude.settings-secrets
    pats = _rules(data, ("ask", "deny"), "Edit")
    missing = [s for s in ctx.standard.sensitive_paths if not _covered(pats, s)]
    if missing:
        yield Finding("adapter.claude.settings-sensitive", "HS-SEC-008",
                      f"Edición sin confirmación de rutas sensibles: {', '.join(missing[:6])}.",
                      "Añade reglas `Edit(...)` a permissions.ask para cada patrón de patrones_sensibles (ver la plantilla).", SETTINGS)


@rule("adapter.claude.settings-modes", ["HS-SEC-009"])
def settings_modes(ctx: Context):
    """disableBypassPermissionsMode, sin aprobación automática de MCP ni modos no aplicables."""
    data, _ = _settings(ctx)
    if not isinstance(data, dict):
        return
    perms = data.get("permissions") or {}
    if perms.get("disableBypassPermissionsMode") != "disable":
        yield Finding("adapter.claude.settings-modes", "HS-SEC-009", "Falta `permissions.disableBypassPermissionsMode: \"disable\"`.",
                      "Añádelo: impide el modo que omite todas las confirmaciones.", SETTINGS)
    if data.get("enableAllProjectMcpServers") is True:
        yield Finding("adapter.claude.settings-modes", "HS-SEC-009", "`enableAllProjectMcpServers` es true.",
                      "Quítalo: cada servidor MCP se aprueba de forma explícita (S-MCP).", SETTINGS)
    if perms.get("defaultMode") in ("auto", "bypassPermissions"):
        yield Finding("adapter.claude.settings-modes", "HS-SEC-009", f"`defaultMode: {perms['defaultMode']}` en el proyecto.",
                      "No tiene efecto desde el proyecto y confunde; quítalo.", SETTINGS)


# ─────────────── reglas Bash (estándar 0.5.0, F3.7) ───────────────
def bash_rule_matches(rule: str, cmd: str) -> bool:
    """Aproxima la coincidencia de una regla `Bash(...)` de Claude Code con un comando simple.

    Documentado (permissions, «Wildcard patterns»): `*` equivale a cualquier secuencia; `:*` final
    equivale a ` *`; un ` *` final como único comodín también coincide con el comando sin argumentos.
    `Bash` sin paréntesis coincide con todo.
    """
    rule = str(rule).strip()
    if rule in ("Bash", "Bash(*)"):
        return True
    m = re.fullmatch(r"Bash\((.+)\)", rule)
    if not m:
        return False
    pat = m.group(1)
    if pat.endswith(":*"):
        pat = pat[:-2] + " *"
    rx = ".*".join(re.escape(part) for part in pat.split("*"))
    if re.fullmatch(rx, cmd, re.S):
        return True
    return pat.endswith(" *") and pat.count("*") == 1 and cmd == pat[:-2]


def bash_decision(data, cmd: str) -> str | None:
    """Decisión efectiva de la configuración para un comando: deny → ask → allow (o None)."""
    perms = data.get("permissions") if isinstance(data, dict) else None
    for kind in ("deny", "ask", "allow"):
        if any(bash_rule_matches(r, cmd) for r in (perms or {}).get(kind) or []):
            return kind
    return None


@rule("adapter.claude.settings-automode", ["HS-SEC-010"])
def settings_automode(ctx: Context):
    """settings.json fija permissions.disableAutoMode: "disable" (D-041)."""
    data, _ = _settings(ctx)
    if not isinstance(data, dict):
        return
    if (data.get("permissions") or {}).get("disableAutoMode") != "disable":
        yield Finding("adapter.claude.settings-automode", "HS-SEC-010", "Falta `permissions.disableAutoMode: \"disable\"`.",
                      "Añádelo: en modo automático las confirmaciones las decide un modelo, no una regla (ADR-009).", SETTINGS)


GH_ASK = ["gh api repos/o/r", "gh api -X DELETE repos/o/r/git/refs/heads/main"]
GH_DENY = ["gh repo delete o/r --yes", "gh secret set TOKEN", "gh secret list", "gh ruleset list", "gh auth token", "gh auth login"]


@rule("adapter.claude.settings-gh", ["HS-SEC-011"])
def settings_gh(ctx: Context):
    """settings.json pide confirmación para `gh api` y rechaza las operaciones de gh sobre repo, secretos, rulesets y sesión (D-042)."""
    data, _ = _settings(ctx)
    if not isinstance(data, dict):
        return
    sin_ask = [c for c in GH_ASK if bash_decision(data, c) not in ("ask", "deny")]
    sin_deny = [c for c in GH_DENY if bash_decision(data, c) != "deny"]
    if sin_ask:
        yield Finding("adapter.claude.settings-gh", "HS-SEC-011", f"`{sin_ask[0]}` se ejecutaría sin confirmación.",
                      "Añade `Bash(gh api *)` a permissions.ask (adaptador §3).", SETTINGS)
    if sin_deny:
        yield Finding("adapter.claude.settings-gh", "HS-SEC-011", f"No se rechazan: {', '.join(f'`{c}`' for c in sin_deny)}.",
                      "Añade a permissions.deny `Bash(gh repo delete *)`, `Bash(gh secret *)`, `Bash(gh ruleset *)` y `Bash(gh auth *)`.", SETTINGS)


# Comandos que nunca deberían quedar permitidos sin confirmación en la base (P-3, D-043).
BROAD_SAMPLES = [
    "python3 -c x", "python -c x", "bash -c x", "sh -c x", "node -e x", "npx paquete", "uv run x",
    "curl https://ejemplo.invalid", "wget https://ejemplo.invalid", "rm -rf build",
    "git reset --hard HEAD~1", "git push origin main", "gh pr merge 1", "gh api repos/o/r",
    "harness check --run-commands", "harness tasks validate --base origin/main --run-acceptance",
]


@rule("adapter.claude.settings-allow-broad", ["HS-SEC-012"])
def settings_allow_broad(ctx: Context):
    """Ninguna regla allow deja ejecutar sin confirmación intérpretes, red, borrado ni comandos que ejecutan el contrato (D-043)."""
    data, _ = _settings(ctx)
    if not isinstance(data, dict):
        return
    abiertos = [c for c in BROAD_SAMPLES if bash_decision(data, c) == "allow"]
    if abiertos:
        yield Finding("adapter.claude.settings-allow-broad", "HS-SEC-012",
                      f"permissions.allow deja ejecutar sin confirmación: {', '.join(f'`{c}`' for c in abiertos[:5])}.",
                      "Acota las reglas allow a comandos sin efectos (adaptador §3) o añade un ask más específico.", SETTINGS)


# ─────────────── agente en CI ───────────────
CLAUDE_P = re.compile(r"(?m)^\s*(?:[\w./-]*/)?claude\b[^\n]*?(?:\s-p\b|\s--print\b)[^\n]*$")


@rule("core.ci.agent-bare", ["HS-CI-004"], platform="github")
def agent_bare(ctx: Context):
    """Los pasos que ejecutan `claude -p` usan --bare y --setting-sources user (R-14)."""
    wdir = ctx.root / ctx.standard.roles["ci.workflows"]["ruta"]
    for wf in sorted(list(wdir.glob("*.yml")) + list(wdir.glob("*.yaml"))) if wdir.is_dir() else []:
        rel = wf.relative_to(ctx.root).as_posix()
        try:
            doc = yaml.safe_load(wf.read_text(encoding="utf-8", errors="replace")) or {}
        except yaml.YAMLError:
            continue
        for job in (doc.get("jobs") or {}).values() if isinstance(doc, dict) else []:
            for step in (job.get("steps") or []) if isinstance(job, dict) else []:
                run = step.get("run") if isinstance(step, dict) else None
                for line in CLAUDE_P.findall(run or ""):
                    if "--bare" not in line or not re.search(r"--setting-sources[ =]user\b", line):
                        yield Finding("core.ci.agent-bare", "HS-CI-004",
                                      f"{rel}: `{line.strip()[:80]}` sin `--bare --setting-sources user`.",
                                      "En CI el agente no debe cargar hooks, MCP ni env del repositorio (adaptador §5, R-14).", rel)


# ─────────────── distribución (ADR-017) ───────────────
@rule("core.components.drift", ["HS-CMP-009"])
def components_drift(ctx: Context):
    """Los componentes de .harness/components.lock están instalados sin cambios locales."""
    from ..distribucion import LOCK, DistribucionError, deriva, leer_lock
    if not (ctx.root / LOCK).is_file():
        return
    try:
        lock = leer_lock(ctx.root)
    except (DistribucionError, ValueError) as exc:
        yield Finding("core.components.drift", "HS-CMP-009", f"{LOCK} no es válido: {exc}",
                      "Regenera el lock con `harness components add/sync` en lugar de editarlo a mano.", LOCK)
        return
    for cid, entrada in lock["componentes"].items():
        for problema in deriva(ctx.root, entrada):
            yield Finding("core.components.drift", "HS-CMP-009", f"Componente `{cid}` {entrada.get('version')}: {problema}.",
                          "Restaura con `harness components remove` + `add`, o conviértelo en un componente propio (otro id y su ficha). ADR-017.",
                          LOCK)
