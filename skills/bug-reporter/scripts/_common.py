"""Shared, dependency-free helpers for the bug-reporter scripts.

Candidate construction, noise normalization (for stable fingerprints), and severity mapping.
No third-party imports — runs anywhere Python 3.10+ does.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from typing import Any

# ---- noise normalization (so the same bug fingerprints the same across runs) ----
# Order matters: structural tokens (timestamps, uuids, emails, hosts, paths) are normalized
# BEFORE generic numbers, so digits inside an email/uuid don't leak into the number bucket.
_NORMALIZERS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?"), "<ts>"),     # timestamps
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<uuid>"),
    (re.compile(r"[\w.+-]+@[\w.-]+\.\w+"), "<email>"),                                # emails (incl. generated)
    (re.compile(r"\b[0-9a-fA-F]{16,}\b"), "<hex>"),                                   # long hex ids
    (re.compile(r"https?://[^/\s:]+(?::\d+)?"), "<host>"),                            # scheme://host:port
    (re.compile(r"/(?:tmp|var|private|Users|home)/[^\s:'\"]+"), "<path>"),            # absolute paths
    (re.compile(r":\d{2,5}\b"), ":<port>"),                                           # bare ports
    (re.compile(r"\b\d{3,}\b"), "<n>"),                                               # long numbers (ids, ms, status)
]


def normalize(text: str) -> str:
    """Strip run-specific noise so equivalent failures collapse to one signature.

    HTTP status codes are normalized to <n> like any other number — title + location already
    separate distinct bugs, so preserving them added fragility (digits leak into emails/ids)
    for negligible dedup value.
    """
    if not text:
        return ""
    t = text
    for pat, repl in _NORMALIZERS:
        t = pat.sub(repl, t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def fingerprint(*parts: str) -> str:
    """Stable short signature over normalized parts."""
    joined = "␟".join(normalize(p) for p in parts if p)
    return "bf_" + hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]


# ---- severity ------------------------------------------------------------------
SEVERITIES = ["blocker", "critical", "major", "minor", "info"]
SEV_TO_PRIORITY = {"blocker": "P0", "critical": "P1", "major": "P2", "minor": "P3", "info": "P4"}


def _idx(sev: str) -> int:
    return SEVERITIES.index(sev) if sev in SEVERITIES else len(SEVERITIES) - 1


def more_severe(sev: str, steps: int = 1) -> str:
    """Raise severity toward `blocker` (lower index)."""
    return SEVERITIES[max(0, _idx(sev) - steps)]


def less_severe(sev: str, steps: int = 1) -> str:
    """Lower severity toward `info` (higher index)."""
    return SEVERITIES[min(len(SEVERITIES) - 1, _idx(sev) + steps)]


def make_candidate(
    *,
    source: str,
    title: str,
    severity: str = "major",
    location: dict[str, Any] | None = None,
    evidence: list[str] | None = None,
    fp_parts: list[str] | None = None,
) -> dict[str, Any]:
    """Build a normalized candidate dict (matches contracts/bug-report.schema.json $defs/candidate)."""
    loc = location or {}
    parts = fp_parts or [title, loc.get("file", ""), loc.get("test_id", ""), loc.get("rule_id", "")]
    fp = fingerprint(*[str(p) for p in parts])
    return {
        "id": fp,                       # provisional id == fingerprint; stable per candidate
        "source": source,
        "fingerprint": fp,
        "classification": "product-bug",  # provisional; Step 2 (judgment) sets the real class
        "severity": severity if severity in SEVERITIES else "major",
        "priority": SEV_TO_PRIORITY.get(severity, "P2"),
        "title": title.strip()[:120],
        "location": loc,
        "evidence": evidence or [],
        "labels": [],
    }


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return json.load(fh)


def emit(candidates: list[dict[str, Any]]) -> None:
    """Print candidates as JSON to stdout (the seam between scripts and the skill)."""
    json.dump({"candidates": candidates}, sys.stdout, indent=2)
    sys.stdout.write("\n")
