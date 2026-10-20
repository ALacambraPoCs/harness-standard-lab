"""Autotest: cada caso de tests/fixtures/cases.yaml produce exactamente los fallos esperados."""
from pathlib import Path

import pytest

from harness_cli.selftest import load_cases, run_case
from harness_cli.standard import load_standard

FIXTURES = Path(__file__).parent / "fixtures"
STANDARD = load_standard()
CASES = load_cases(FIXTURES)["casos"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case):
    outcome = run_case(FIXTURES, case, STANDARD)
    assert outcome.ok, outcome.detail
