"""Integridad del producto A y trazabilidad con B."""
from pathlib import Path

from harness_cli.matrix import blocking, build
from harness_cli.rules import load_all
from harness_cli.standard import load_standard

FIXTURES = Path(__file__).parent / "fixtures"


def test_standard_data_is_valid():
    std = load_standard()  # valida requirements.yaml y roles.yaml contra sus esquemas
    assert std.version.count(".") == 2
    assert std.defined_levels


def test_traceability_has_no_gaps():
    _, problems = build(load_standard(), FIXTURES)
    assert not blocking(problems), problems


def test_every_rule_documents_itself():
    for rule in load_all().values():
        assert rule.doc, f"{rule.id} sin docstring"


def test_tabla_de_roles_al_dia():
    from harness_cli.roles_table import render_into
    std = load_standard()
    doc = std.root / "standard" / "03-estructura-canonica.md"
    text = doc.read_text(encoding="utf-8")
    assert render_into(text, std) == text, "Ejecuta `harness roles --write`"
