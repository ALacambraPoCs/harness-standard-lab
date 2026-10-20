"""Matriz de trazabilidad requisito → regla → fixture (ADR-001, ADR-002)."""
from __future__ import annotations

from pathlib import Path

from .rules import load_all
from .selftest import load_cases, run_all
from .standard import Standard


def build(standard: Standard, fixtures_dir: Path) -> tuple[list[dict], list[str]]:
    registry = load_all()
    cases = load_cases(fixtures_dir)["casos"]
    by_rule: dict[str, list[str]] = {}
    for c in cases:
        for r in c.get("expect_fail", []):
            by_rule.setdefault(r, []).append(c["id"])
    problems: list[str] = []
    rows = []
    for req in standard.requirements.values():
        rules = req["reglas"]
        for r in rules:
            if r not in registry:
                problems.append(f"{req['id']}: la regla `{r}` no existe en la CLI.")
            elif req["id"] not in registry[r].requirements:
                problems.append(f"{req['id']}: la regla `{r}` no declara este requisito.")
        if req["verificacion"] in ("automatica", "semiautomatica") and not rules:
            problems.append(f"{req['id']}: verificación {req['verificacion']} sin reglas.")
        if req["naturaleza"] == "enforcement" and req["ambito"] == "instancia" and req["verificacion"] == "manual":
            problems.append(f"{req['id']}: aviso — enforcement verificado solo manualmente (pendiente de control L4/L5).")
        fx = sorted({c for r in rules for c in by_rule.get(r, [])})
        rows.append({"id": req["id"], "nivel": req["nivel"], "conformidad": ",".join(req["conformidad"]) or "—",
                     "naturaleza": req["naturaleza"], "verificacion": req["verificacion"],
                     "reglas": rules, "fixtures": fx, "titulo": req["titulo"]})
    for rid, rule in registry.items():
        for q in rule.requirements:
            if q not in standard.requirements:
                problems.append(f"Regla `{rid}`: requisito {q} inexistente.")
        if rid not in by_rule:
            problems.append(f"Regla `{rid}`: sin fixture no conforme que la haga fallar.")
    return rows, problems


def to_markdown(rows: list[dict], problems: list[str], outcomes=None) -> str:
    out = ["# Matriz de trazabilidad", "",
           "Generada por `harness matrix`. No editar a mano.", "",
           "| Requisito | Nivel | Niveles | Naturaleza | Verificación | Reglas | Fixtures no conformes |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['id']} | {r['nivel']} | {r['conformidad']} | {r['naturaleza']} | {r['verificacion']} | "
                   f"{'<br>'.join(f'`{x}`' for x in r['reglas']) or '—'} | {'<br>'.join(r['fixtures']) or '—'} |")
    if outcomes is not None:
        out += ["", "## Autotest de fixtures", "", "| Caso | Resultado | Detalle |", "|---|---|---|"]
        out += [f"| {o.id} | {'✅' if o.ok else '❌'} | {o.detail} |" for o in outcomes]
    out += ["", "## Incidencias", ""] + ([f"- {p}" for p in problems] or ["- Ninguna."])
    return "\n".join(out) + "\n"


def blocking(problems: list[str]) -> list[str]:
    return [p for p in problems if "aviso —" not in p]


def run(standard: Standard, fixtures_dir: Path, execute: bool):
    rows, problems = build(standard, fixtures_dir)
    outcomes = run_all(fixtures_dir, standard) if execute else None
    if outcomes:
        problems += [f"Caso `{o.id}`: {o.detail}" for o in outcomes if not o.ok]
    return rows, problems, outcomes
