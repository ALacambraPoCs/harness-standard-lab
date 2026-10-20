from __future__ import annotations

from dataclasses import asdict, dataclass, field

SEVERITY_BY_LEVEL = {
    "DEBE": "error",
    "NO DEBE": "error",
    "DEBERÍA": "warning",
    "NO DEBERÍA": "warning",
    "PUEDE": "info",
}
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    """Un incumplimiento detectado por una regla (formato QUÉ / POR QUÉ / CÓMO ARREGLAR)."""

    rule: str
    requirement: str
    message: str           # QUÉ ha fallado
    remedy: str            # CÓMO arreglarlo
    path: str | None = None
    severity: str | None = None   # None => derivada del nivel del requisito
    status: str = "fail"          # fail | waived
    why: str = ""                 # POR QUÉ (título del requisito), lo rellena el checker
    waiver: dict | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v not in (None, "")}


@dataclass
class Result:
    root: str
    standard_version: str
    cli_version: str
    declared_level: str | None
    effective_level: str | None
    adapters: list[str]
    rules_run: list[str] = field(default_factory=list)
    rules_skipped: dict[str, str] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        c = {"error": 0, "warning": 0, "info": 0, "waived": 0}
        for f in self.findings:
            if f.status == "waived":
                c["waived"] += 1
            else:
                c[f.severity or "error"] += 1
        return c

    def exit_code(self, strict: bool = False) -> int:
        c = self.counts()
        if c["error"] or (strict and c["warning"]):
            return 1
        return 0

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "standard_version": self.standard_version,
            "cli_version": self.cli_version,
            "declared_level": self.declared_level,
            "effective_level": self.effective_level,
            "adapters": self.adapters,
            "counts": self.counts(),
            "rules_run": self.rules_run,
            "rules_skipped": self.rules_skipped,
            "findings": [f.to_dict() for f in self.findings],
        }
