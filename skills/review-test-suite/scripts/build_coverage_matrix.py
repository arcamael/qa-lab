#!/usr/bin/env python3
"""Presence/adequacy/risk per taxonomy category. Usage:
python build_coverage_matrix.py <path> [--required type1,type2] [--out FILE].
Adequacy is a coarse static heuristic (missing / weak / adequate); Claude refines it with judgment.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
import _common as C

ALL_TYPES = ["unit", "integration", "component", "contract", "api", "e2e", "smoke", "regression",
             "exploratory", "performance", "security", "compliance", "accessibility", "usability",
             "compatibility", "localization", "reliability", "recoverability", "installability",
             "data-integrity", "visual-regression", "observability", "privacy", "ai-ml"]

RISK = {  # default risk if a category is missing/weak
    "security": "high", "compliance": "high", "privacy": "high", "data-integrity": "high",
    "api": "high", "e2e": "high", "integration": "medium", "unit": "medium",
    "performance": "medium", "accessibility": "medium", "reliability": "medium",
    "ai-ml": "high", "contract": "medium",
}


def adequacy(n: int) -> str:
    if n == 0:
        return "missing"
    if n < 5:
        return "weak"
    return "adequate"


def run(root: str, required: list[str]) -> dict:
    counts = Counter()
    for f in C.discover_test_files(root):
        text = C.read(f)
        fws = C.detect_frameworks(text)
        ttype, _, _ = C.classify_type(f, text, fws, root)
        counts[ttype] += sum(1 for _ in C.iter_tests(text, C.detect_language(f))) or 1
    rows = []
    universe = sorted(set(ALL_TYPES) | set(counts) | set(required))
    for t in universe:
        n = counts.get(t, 0)
        adq = adequacy(n)
        risk = RISK.get(t, "low")
        if t in required and n == 0:
            risk = "high"
        rows.append({"test_type": t, "present": n > 0, "n_tests": n, "adequacy": adq, "risk": risk})
    return {"coverage_matrix": rows}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("path")
    ap.add_argument("--required", default=""); ap.add_argument("--out")
    a = ap.parse_args()
    req = [x.strip() for x in a.required.split(",") if x.strip()]
    payload = json.dumps(run(a.path, req), indent=2)
    open(a.out, "w").write(payload) if a.out else print(payload)


if __name__ == "__main__":
    main()
