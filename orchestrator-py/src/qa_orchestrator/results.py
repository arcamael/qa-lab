"""Read and summarize a Playwright JSON report (the seam between the TS suite and the brain).

The TS suite writes results.json via Playwright's `json` reporter. This module turns that
into a small, stable Summary the rest of the orchestrator can reason over without knowing
anything about TypeScript or Playwright internals.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class Summary:
    passed: int = 0
    failed: int = 0
    flaky: int = 0
    skipped: int = 0
    failed_titles: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.flaky + self.skipped

    @property
    def ok(self) -> bool:
        return self.failed == 0


def load_report(path: str | Path) -> dict:
    """Load a Playwright JSON report from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _walk_specs(suites: list | None) -> Iterator[dict]:
    """Yield every spec, recursing through nested suites."""
    for suite in suites or []:
        yield from suite.get("specs", [])
        yield from _walk_specs(suite.get("suites"))


def summarize(report: dict) -> Summary:
    """Reduce a Playwright report to pass/fail/flaky/skipped counts and failed test titles."""
    summary = Summary()
    stats = report.get("stats") or {}

    if stats:
        # Playwright's own tallies are authoritative when present.
        summary.passed = stats.get("expected", 0)
        summary.failed = stats.get("unexpected", 0)
        summary.flaky = stats.get("flaky", 0)
        summary.skipped = stats.get("skipped", 0)

    failed_from_walk = 0
    for spec in _walk_specs(report.get("suites")):
        if not spec.get("ok", True):
            failed_from_walk += 1
            summary.failed_titles.append(spec.get("title", "<unknown>"))

    # If the report had no stats block, derive counts from the tree walk.
    if not stats:
        total = sum(1 for _ in _walk_specs(report.get("suites")))
        summary.failed = failed_from_walk
        summary.passed = total - failed_from_walk

    return summary
