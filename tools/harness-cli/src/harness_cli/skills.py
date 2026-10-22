"""Validación de skills según la especificación de Agent Skills (agentskills.io/specification) y los
perfiles de ADR-012. Implementación propia: `skills-ref` es solo una demostración (H4, F3)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Extensiones de Claude Code verificadas el 2026-10-22 (code.claude.com/docs/en/skills).
CLAUDE_FIELDS = {"when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
                 "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell"}
NAME_RE = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
FRONT = re.compile(r"^---\n(.*?)\n---\n?", re.S)
PROFILE_KEY = "harness-perfil"
MAX_LINES = 500


@dataclass
class SkillReport:
    path: str
    meta: dict = field(default_factory=dict)
    spec: list[str] = field(default_factory=list)      # incumplimientos de la especificación
    profile: list[str] = field(default_factory=list)   # campos fuera del perfil declarado (ADR-012)
    warnings: list[str] = field(default_factory=list)

    @property
    def perfil(self) -> str:
        md = self.meta.get("metadata") if isinstance(self.meta.get("metadata"), dict) else {}
        return str(md.get(PROFILE_KEY, "portable"))


def validate_skill(skill_md: Path, rel: str, expected_name: str | None = None) -> SkillReport:
    """Valida un SKILL.md. `expected_name` por defecto es el nombre del directorio padre."""
    rep = SkillReport(rel)
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = FRONT.match(text)
    if not m:
        rep.spec.append("no empieza con frontmatter YAML (--- … ---)")
        return rep
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        rep.spec.append(f"frontmatter YAML inválido: {exc}")
        return rep
    if not isinstance(meta, dict):
        rep.spec.append("el frontmatter no es un objeto")
        return rep
    rep.meta = meta
    expected = expected_name or skill_md.parent.name
    name, desc = meta.get("name"), meta.get("description")
    if not isinstance(name, str) or not NAME_RE.match(name):
        rep.spec.append("`name` obligatorio: 1–64 caracteres a-z0-9 y guiones, sin `--` ni guion inicial/final")
    elif name != expected:
        rep.spec.append(f"`name` ({name}) debe coincidir con el directorio ({expected})")
    if not isinstance(desc, str) or not 1 <= len(desc.strip()) <= 1024:
        rep.spec.append("`description` obligatoria, 1–1024 caracteres")
    comp = meta.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        rep.spec.append("`compatibility` debe ser texto de 1–500 caracteres")
    md = meta.get("metadata")
    if md is not None and (not isinstance(md, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in md.items())):
        rep.spec.append("`metadata` debe ser un mapa de texto a texto")
    at = meta.get("allowed-tools")
    if at is not None and not isinstance(at, str):
        rep.spec.append("`allowed-tools` debe ser texto separado por espacios")
    if "license" in meta and not isinstance(meta["license"], str):
        rep.spec.append("`license` debe ser texto")
    perfil = rep.perfil
    if perfil not in ("portable", "claude-code"):
        rep.spec.append(f"`metadata.{PROFILE_KEY}` debe ser `portable` o `claude-code`")
    extra = sorted(set(meta) - SPEC_FIELDS)
    unknown = [f for f in extra if f not in CLAUDE_FIELDS]
    if unknown:
        rep.profile.append(f"campos desconocidos: {', '.join(unknown)}")
    if perfil == "portable" and [f for f in extra if f in CLAUDE_FIELDS]:
        rep.profile.append(f"perfil portable con extensiones de Claude Code: {', '.join(f for f in extra if f in CLAUDE_FIELDS)} "
                           f"(declara `metadata.{PROFILE_KEY}: claude-code` y justifícalo, o quítalas)")
    n = len(text.splitlines())
    if n > MAX_LINES:
        rep.warnings.append(f"{n} líneas (la especificación recomienda < {MAX_LINES}; mueve detalle a references/)")
    return rep
