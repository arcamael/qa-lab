#!/usr/bin/env python3
"""Compute a stable bug fingerprint.

Two uses:
  - ad-hoc:   python fingerprint.py "wrong password rejected" "auth.api.spec.ts" "expected status<200>"
  - re-stamp: cat candidates.json | python fingerprint.py --stdin
              (recomputes `fingerprint` for each candidate from its fp-relevant fields and prints them)

The fingerprint normalizes run-specific noise (timestamps, ids, ports, paths, generated data) so the
same defect hashes identically across runs and machines. See references/deduplication.md.
"""
from __future__ import annotations

import json
import sys

from _common import fingerprint


def _restamp() -> int:
    doc = json.load(sys.stdin)
    cands = doc.get("candidates", doc if isinstance(doc, list) else [])
    for c in cands:
        loc = c.get("location", {})
        parts = [c.get("title", ""), str(loc.get("file", "")).split("/")[-1],
                 str(loc.get("test_id", "")), str(loc.get("rule_id", ""))]
        c["fingerprint"] = fingerprint(*parts)
    json.dump({"candidates": cands}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--stdin":
        return _restamp()
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    print(fingerprint(*argv[1:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
