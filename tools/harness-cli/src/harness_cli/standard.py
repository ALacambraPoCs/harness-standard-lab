"""Carga de los datos normativos (producto A): requisitos, roles y esquemas.

Orden de búsqueda de la raíz del estándar:
1. Variable de entorno HARNESS_STANDARD_ROOT.
2. Repositorio central (desarrollo): directorio ascendente que contenga standard/requirements.yaml.
3. Copia empaquetada en harness_cli/_standard (instalación con pip).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

LEVELS = ("N0", "N1", "N2", "N3")


def find_standard_root() -> Path:
    env = os.environ.get("HARNESS_STANDARD_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "standard" / "requirements.yaml").is_file() and (parent / "schemas").is_dir():
            return parent
    bundled = here.parent / "_standard"
    if (bundled / "standard" / "requirements.yaml").is_file():
        return bundled
    raise FileNotFoundError("No se encuentra la raíz del estándar (standard/requirements.yaml).")


@dataclass
class Standard:
    root: Path
    version: str
    requirements: dict[str, dict[str, Any]]
    roles: dict[str, dict[str, Any]]
    sensitive_paths: list[str]
    sensitive_patterns: list[str] = field(default_factory=list)
    trivial_patterns: list[str] = field(default_factory=list)
    critical_patterns: list[str] = field(default_factory=list)
    test_patterns: list[str] = field(default_factory=list)
    defined_levels: tuple[str, ...] = ("N0",)
    levels_since: dict[str, str] = field(default_factory=dict)
    schemas: dict[str, dict[str, Any]] = field(default_factory=dict)

    def level_defined(self, level: str, version: str | None) -> bool:
        """El nivel existe en la versión declarada (niveles_desde; por defecto, desde 0.1.0)."""
        if level not in self.defined_levels:
            return False
        since = semver(self.levels_since.get(level, "0.1.0"))
        declared = semver(version) if version else None
        return declared is None or since is None or declared >= since

    def validator(self, name: str) -> Draft202012Validator:
        return Draft202012Validator(self.schemas[name], format_checker=FormatChecker())

    def applicable(self, level: str, adapters: set[str], version: str | None = None) -> list[dict[str, Any]]:
        """Requisitos de ámbito instancia que aplican al nivel, adaptadores y versión declarados.

        Con `version`, un requisito solo aplica si `desde` ≤ versión declarada: una instancia que
        declara 0.1.0 no queda obligada por requisitos introducidos en 0.2.0 hasta que migra (D-029).
        """
        out = []
        declared = semver(version) if version else None
        for req in self.requirements.values():
            if req["ambito"] != "instancia" or req["estado"] in ("retirado",):
                continue
            if level not in req["conformidad"]:
                continue
            if declared and (semver(req["desde"]) or (0, 0, 0)) > declared:
                continue
            if req.get("adaptador") and req["adaptador"] not in adapters:
                continue
            out.append(req)
        return out


def semver(v: Any) -> tuple[int, int, int] | None:
    try:
        a, b, c = (int(x) for x in str(v).split("."))
        return a, b, c
    except (ValueError, AttributeError):
        return None


def _load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_standard(root: Path | None = None) -> Standard:
    root = root or find_standard_root()
    schemas = {}
    for name in ("manifest", "requirement", "roles", "task", "adr", "catalog-entry"):
        with (root / "schemas" / f"{name}.schema.json").open(encoding="utf-8") as fh:
            schemas[name] = json.load(fh)
    reqs_doc = _load_yaml(root / "standard" / "requirements.yaml")
    roles_doc = _load_yaml(root / "standard" / "roles.yaml")
    std = Standard(
        root=root,
        version=(root / "standard" / "VERSION").read_text(encoding="utf-8").strip(),
        requirements={r["id"]: r for r in reqs_doc["requisitos"]},
        roles=roles_doc["roles"],
        sensitive_paths=roles_doc["rutas_sensibles"],
        defined_levels=tuple(reqs_doc["niveles_definidos"]),
        levels_since=reqs_doc.get("niveles_desde") or {},
        sensitive_patterns=roles_doc["patrones_sensibles"],
        trivial_patterns=roles_doc["patrones_triviales"],
        critical_patterns=roles_doc.get("rutas_criticas") or [],
        test_patterns=roles_doc.get("patrones_pruebas") or [],
        schemas=schemas,
    )
    # El propio estándar debe ser válido: si no, es un defecto del producto A.
    errs = list(std.validator("requirement").iter_errors(reqs_doc)) + list(
        std.validator("roles").iter_errors(roles_doc)
    )
    if errs:
        msgs = "; ".join(f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errs[:5])
        raise ValueError(f"Datos del estándar inválidos: {msgs}")
    return std
