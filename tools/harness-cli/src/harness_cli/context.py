from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .standard import Standard


class _StrDateLoader(yaml.SafeLoader):
    """SafeLoader que conserva las fechas como texto (el esquema las valida con format: date)."""


_StrDateLoader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


@dataclass
class Context:
    root: Path
    standard: Standard
    today: dt.date
    run_commands: bool = False
    command_timeout: int = 900
    manifest: dict[str, Any] | None = None
    manifest_error: str | None = None
    manifest_valid: bool = False
    _cache: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build(cls, root: Path, standard: Standard, today: dt.date, **kw) -> "Context":
        ctx = cls(root=root.resolve(), standard=standard, today=today, **kw)
        mpath = ctx.root / standard.roles["manifest"]["ruta"]
        if mpath.is_file():
            try:
                data = yaml.load(mpath.read_text(encoding="utf-8"), Loader=_StrDateLoader)  # noqa: S506
                ctx.manifest = data if isinstance(data, dict) else None
                if ctx.manifest is None:
                    ctx.manifest_error = "el manifiesto no es un objeto YAML"
            except yaml.YAMLError as exc:
                ctx.manifest_error = f"YAML inválido: {exc}"
        if ctx.manifest is not None:
            ctx.manifest_valid = not any(True for _ in standard.validator("manifest").iter_errors(ctx.manifest))
        return ctx

    # ── vistas del manifiesto (tolerantes a manifiestos inválidos) ──
    @property
    def level(self) -> str:
        try:
            lvl = self.manifest["standard"]["level"]
            return lvl if lvl in ("N0", "N1", "N2", "N3") else "N0"
        except (TypeError, KeyError):
            return "N0"

    @property
    def adapters(self) -> set[str]:
        try:
            return {a["id"] for a in self.manifest["adapters"]["agents"] if isinstance(a, dict) and "id" in a}
        except (TypeError, KeyError):
            return set()

    @property
    def platform(self) -> str | None:
        try:
            return self.manifest["adapters"]["platform"]["id"]
        except (TypeError, KeyError):
            return None

    @property
    def commands(self) -> dict[str, str]:
        try:
            cmds = self.manifest["commands"]
            return {k: v for k, v in cmds.items() if isinstance(v, str)} if isinstance(cmds, dict) else {}
        except (TypeError, KeyError):
            return {}

    def role_path(self, role: str) -> str:
        """Ruta efectiva de un rol: reubicación válida del manifiesto o ruta por defecto."""
        spec = self.standard.roles[role]
        if spec.get("relativa_a"):
            return f"{self.role_path(spec['relativa_a']).rstrip('/')}/{spec['ruta']}"
        if spec.get("alternativas"):
            for alt in spec["alternativas"]:
                if (self.root / alt).exists():
                    return alt
            return spec["ruta"]
        if spec.get("reubicable") and isinstance(self.manifest, dict):
            roles = self.manifest.get("roles") or {}
            if isinstance(roles, dict) and isinstance(roles.get(role), str):
                return roles[role]
        return spec["ruta"]

    def read(self, rel: str) -> str | None:
        p = self.root / rel
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
        return None
