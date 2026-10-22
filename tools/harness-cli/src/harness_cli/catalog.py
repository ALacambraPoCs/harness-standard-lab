"""Validación del catálogo de componentes del repositorio central (standard/05-componentes, F3.3)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

from .model import Finding
from .skills import validate_skill
from .standard import Standard, semver

TIPO_DIR = {"skill": "skill", "subagente": "subagente", "hook": "hook", "mcp": "mcp", "workflow": "workflow", "plugin": "plugin"}
FICHA_SECTIONS = 17
TRANSITIONS = {  # standard/05-componentes/00-modelo.md §5
    "experimental": {"estable", "retirado"},
    "estable": {"deprecado"},
    "deprecado": {"retirado"},
    "retirado": set(),
}
RULE_REQ = {"catalog.entry": "HS-CMP-010", "catalog.ficha": "HS-CMP-011", "catalog.skill": "HS-CMP-012",
            "catalog.transition": "HS-CMP-013", "catalog.version": "HS-CMP-013"}


def _f(std: Standard, rule: str, msg: str, remedy: str, path: str) -> Finding:
    req = RULE_REQ[rule]
    spec = std.requirements.get(req)
    sev = "error" if not spec or spec["nivel"] in ("DEBE", "NO DEBE") else "warning"
    return Finding(rule, req, msg, remedy, path, severity=sev,
                   why=f"{req} ({spec['nivel']}): {spec['titulo']}" if spec else req)


def entries(root: Path, catalog: str = "catalog") -> list[Path]:
    base = root / catalog
    return sorted(base.glob("*/*/componente.yaml")) if base.is_dir() else []


def _load(text: str):
    try:
        data = yaml.load(text, Loader=_Loader)  # noqa: S506 (SafeLoader sin fechas)
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


class _Loader(yaml.SafeLoader):
    pass


_Loader.yaml_implicit_resolvers = {k: [(t, r) for t, r in v if t != "tag:yaml.org,2002:timestamp"]
                                   for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}


def validate(std: Standard, root: Path, catalog: str = "catalog", base: str | None = None) -> tuple[list[Finding], int]:
    out: list[Finding] = []
    validator = std.validator("catalog-entry")
    found = entries(root, catalog)
    for entry in found:
        cdir = entry.parent
        rel = entry.relative_to(root).as_posix()
        data = _load(entry.read_text(encoding="utf-8"))
        if data is None:
            out.append(_f(std, "catalog.entry", f"{rel}: YAML inválido o no es un objeto.", "Corrige la sintaxis.", rel))
            continue
        for err in validator.iter_errors(data):
            loc = "/".join(map(str, err.absolute_path)) or "(raíz)"
            out.append(_f(std, "catalog.entry", f"{rel}: `{loc}`: {err.message}", "Ajusta la entrada a schemas/catalog-entry.schema.json.", rel))
        if data.get("id") != cdir.name:
            out.append(_f(std, "catalog.entry", f"{rel}: `id` ({data.get('id')}) no coincide con el directorio ({cdir.name}).",
                          "Usa el mismo identificador.", rel))
        if TIPO_DIR.get(data.get("tipo")) != cdir.parent.name:
            out.append(_f(std, "catalog.entry", f"{rel}: `tipo` ({data.get('tipo')}) no coincide con el directorio ({cdir.parent.name}).",
                          "Mueve el componente a catalog/<tipo>/<id>/.", rel))
        for a in data.get("archivos") or []:
            if isinstance(a, dict) and isinstance(a.get("origen"), str) and not (cdir / a["origen"]).is_file():
                out.append(_f(std, "catalog.entry", f"{rel}: el archivo de origen `{a['origen']}` no existe.", "Añádelo o corrige la ruta.", rel))
        # ficha de 17 puntos
        ficha = cdir / "FICHA.md"
        frel = ficha.relative_to(root).as_posix()
        if not ficha.is_file():
            out.append(_f(std, "catalog.ficha", f"No existe {frel}.", "Crea la ficha desde standard/05-componentes/_PLANTILLA-FICHA.md.", frel))
        else:
            heads = set(re.findall(r"(?m)^##\s+(\d{1,2})\.\s+\S", ficha.read_text(encoding="utf-8")))
            missing = [str(i) for i in range(1, FICHA_SECTIONS + 1) if str(i) not in heads]
            if missing:
                out.append(_f(std, "catalog.ficha", f"{frel}: faltan los apartados {', '.join(missing)} de 17.",
                              "Completa la ficha; si un apartado no aplica, dilo en una línea.", frel))
        # skill: SKILL.md conforme y coherente con la entrada
        if data.get("tipo") == "skill":
            src = [a for a in data.get("archivos") or [] if isinstance(a, dict) and str(a.get("origen", "")).endswith("SKILL.md")]
            if not src:
                out.append(_f(std, "catalog.skill", f"{rel}: una skill debe instalar un SKILL.md.", "Añade el SKILL.md a `archivos`.", rel))
            for a in src:
                p = cdir / a["origen"]
                if not p.is_file():
                    continue
                prel = p.relative_to(root).as_posix()
                rep = validate_skill(p, prel, expected_name=data.get("id"))
                for e in rep.spec + rep.profile:
                    out.append(_f(std, "catalog.skill", f"{prel}: {e}.", "Ajusta el SKILL.md (ADR-012).", prel))
                perfil = (data.get("compatibilidad") or {}).get("perfil")
                if perfil and rep.meta and rep.perfil != perfil:
                    out.append(_f(std, "catalog.skill", f"{prel}: perfil `{rep.perfil}` distinto del de la entrada (`{perfil}`).",
                                  "Alinea `metadata.harness-perfil` con `compatibilidad.perfil`.", prel))
                if not str(a.get("destino", "")) == f".claude/skills/{data.get('id')}/SKILL.md":
                    out.append(_f(std, "catalog.skill", f"{rel}: el destino debe ser `.claude/skills/{data.get('id')}/SKILL.md` (ADR-012).",
                                  "Corrige `destino`.", rel))
        if base:
            out += _transition(std, root, cdir, rel, data, base)
    return out, len(found)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def _transition(std, root, cdir, rel, data, base) -> list[Finding]:
    out = []
    try:
        old = _load(_git(root, "show", f"{base}:{rel}"))
    except subprocess.CalledProcessError:
        return out  # componente nuevo
    if old is None:
        return out
    a, b = old.get("estado"), data.get("estado")
    if a != b and b not in TRANSITIONS.get(a, set()):
        out.append(_f(std, "catalog.transition", f"{rel}: transición de estado `{a}` → `{b}` no permitida.",
                      f"Desde `{a}`: {', '.join(sorted(TRANSITIONS.get(a, set()))) or 'ninguna'}.", rel))
    crel = cdir.relative_to(root).as_posix()
    changed = [l for l in _git(root, "diff", "--name-only", f"{base}...HEAD", "--", crel).splitlines() if l]
    ov, nv = semver(old.get("version")), semver(data.get("version"))
    if changed and ov and nv and not nv > ov:
        out.append(_f(std, "catalog.version", f"{rel}: el componente cambia ({len(changed)} archivo/s) pero `version` no sube ({old.get('version')} → {data.get('version')}).",
                      "Sube la versión con SemVer (PATCH, MINOR o MAJOR según el cambio).", rel))
    return out
