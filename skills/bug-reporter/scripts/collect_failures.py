#!/usr/bin/env python3
"""Collect bug candidates from a Playwright JSON report (results.json).

Walks the suite tree, finds specs that did not pass, and emits one normalized candidate per
failing test — with its title, spec file, error message, and a retry-pass flag (a strong flaky
signal). Static only: reads the report, runs nothing.

Usage: python collect_failures.py results.json
"""
from __future__ import annotations

import sys
from typing import Any, Iterator

from _common import emit, make_candidate


def _walk(suites: list | None, file_hint: str = "") -> Iterator[tuple[dict, str]]:
    for suite in suites or []:
        f = suite.get("file") or file_hint
        for spec in suite.get("specs", []):
            yield spec, spec.get("file") or f
        yield from _walk(suite.get("suites"), f)


def _error_text(spec: dict[str, Any]) -> tuple[str, bool, str]:
    """Return (error_message, saw_retry_pass, project)."""
    msg, saw_pass, saw_fail, project = "", False, False, ""
    for test in spec.get("tests", []):
        project = test.get("projectName") or project
        for res in test.get("results", []):
            status = res.get("status")
            if status == "passed":
                saw_pass = True
            elif status in ("failed", "timedOut", "interrupted"):
                saw_fail = True
                err = res.get("error") or {}
                if not msg:
                    msg = (err.get("message") or "").strip()
                for e in res.get("errors", []):
                    if not msg:
                        msg = (e.get("message") or "").strip()
    # retry-pass = failed at least once AND eventually passed → flaky signal
    return msg, (saw_pass and saw_fail), project


def collect(report: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for spec, spec_file in _walk(report.get("suites")):
        if spec.get("ok", True):
            continue
        title = spec.get("title", "<unknown test>")
        line = spec.get("line", 0)
        msg, retry_pass, project = _error_text(spec)
        first_line = (msg.splitlines() or [""])[0][:200]

        cand = make_candidate(
            source="test-failure",
            title=f"{title}",
            severity="major",
            location={"file": spec_file, "line": line, "test_id": title, "project": project},
            evidence=[f"error: {first_line}" if first_line else "test failed (no error message captured)"],
            # fingerprint on the STABLE signal: title + spec basename + normalized error
            fp_parts=[title, spec_file.split("/")[-1], first_line],
        )
        # Surface the flaky signal for Step 2; the skill makes the final classification call.
        if retry_pass:
            cand["evidence"].append("signal: passed on retry within the same run (flaky)")
            cand["classification"] = "flaky-test"
            cand["severity"] = "minor"  # flaky default; the skill re-rates by CI-trust blast radius
            cand["priority"] = "P3"
        candidates.append(cand)
    return candidates


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: collect_failures.py results.json", file=sys.stderr)
        return 2
    import json
    with open(argv[1], "r", encoding="utf-8", errors="replace") as fh:
        report = json.load(fh)
    emit(collect(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
