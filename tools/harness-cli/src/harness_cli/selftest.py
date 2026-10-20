"""Autotest del producto B: ejecuta los casos de tests/fixtures/cases.yaml.

Cada caso parte de una instancia base, aplica mutaciones y comprueba qué reglas fallan.
Lo usan pytest y `harness matrix --strict`.
"""
from __future__ import annotations

import datetime as dt
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from .checker import run_check
from .standard import Standard


@dataclass
class CaseOutcome:
    id: str
    ok: bool
    detail: str
    failing_rules: set[str]


def load_cases(fixtures_dir: Path) -> dict:
    return yaml.safe_load((fixtures_dir / "cases.yaml").read_text(encoding="utf-8"))


def _mutate(root: Path, mutations: list[dict]) -> None:
    for m in mutations or []:
        if "delete" in m:
            p = root / m["delete"]
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        elif "write" in m:
            p = root / m["write"]["path"]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(m["write"]["content"], encoding="utf-8")
        elif "append" in m:
            p = root / m["append"]["path"]
            with p.open("a", encoding="utf-8") as fh:
                fh.write(m["append"]["content"])
        elif "replace" in m:
            p = root / m["replace"]["path"]
            text = p.read_text(encoding="utf-8")
            if m["replace"]["old"] not in text:
                raise ValueError(f"Mutación replace sin coincidencia en {p}: {m['replace']['old']!r}")
            p.write_text(text.replace(m["replace"]["old"], m["replace"]["new"]), encoding="utf-8")
        else:
            raise ValueError(f"Mutación desconocida: {m}")


def run_case(fixtures_dir: Path, case: dict, standard: Standard) -> CaseOutcome:
    today = dt.date.fromisoformat(str(case.get("today", "2026-10-19")))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        shutil.copytree(fixtures_dir / case["base"], root)
        _mutate(root, case.get("mutations", []))
        res = run_check(root, standard=standard, today=today, run_commands=case.get("run_commands", False),
                        command_timeout=60)
    failing = {f.rule for f in res.findings if f.status == "fail" and f.severity in ("error", "warning")}
    expect = set(case.get("expect_fail", []))
    if case.get("conforming"):
        ok = not failing
        detail = "conforme" if ok else f"esperaba 0 fallos, fallan: {sorted(failing)}"
    else:
        missing, extra = expect - failing, failing - expect - set(case.get("allow_also", []))
        ok = not missing and not extra
        detail = "ok" if ok else f"faltan {sorted(missing)}; sobran {sorted(extra)}"
    exp_level = case.get("expect_effective_level", "__any__")
    if exp_level != "__any__" and res.effective_level != exp_level:
        ok, detail = False, f"{detail}; nivel efectivo {res.effective_level} ≠ {exp_level}"
    return CaseOutcome(case["id"], ok, detail, failing)


def run_all(fixtures_dir: Path, standard: Standard) -> list[CaseOutcome]:
    doc = load_cases(fixtures_dir)
    return [run_case(fixtures_dir, c, standard) for c in doc["casos"]]
