#!/usr/bin/env python3
"""Deterministic suite metrics: pyramid distribution, redundancy, assertion stats,
skipped count, and a flakiness-risk index. Usage: python compute_metrics.py <path> [--out FILE].
"""
from __future__ import annotations
import argparse, json, re
from collections import Counter
import _common as C

ASSERT_HINTS = ("expect(", ".should(", "assert ", "assert(", "self.assert", "assertEquals",
                "assertThat", "assertTrue", "assertFalse", "verify(", ".toBe", ".toEqual",
                ".toContain", ".toMatch", ".toThrow")
SLEEP_RE = re.compile(r"waitForTimeout\s*\(|time\.sleep\s*\(|Thread\.sleep\s*\(|cy\.wait\s*\(\s*\d")
SKIP_RE = re.compile(r"\.skip\b|xit\s*\(|@Ignore\b|@Disabled\b|@pytest\.mark\.skip")

PYRAMID_KEYS = {"unit": "unit", "component": "unit", "integration": "integration",
                "api": "integration", "contract": "integration", "e2e": "e2e", "smoke": "e2e"}


def run(root: str) -> dict:
    titles = Counter()
    total_tests = 0
    total_assertions = 0
    sleeps = 0
    skipped = 0
    type_counts = Counter()
    for f in C.discover_test_files(root):
        text = C.read(f)
        lang = C.detect_language(f)
        fws = C.detect_frameworks(text)
        ttype, _, _ = C.classify_type(f, text, fws, root)
        skipped += len(SKIP_RE.findall(text))
        for t in C.iter_tests(text, lang):
            total_tests += 1
            type_counts[ttype] += 1
            titles[(ttype, t["test_id"])] += 1
            total_assertions += C.count_assertions(t["body"])
            if SLEEP_RE.search(t["body"]):
                sleeps += 1
    dupes = sum(c - 1 for c in titles.values() if c > 1)
    pyramid = Counter()
    for ttype, n in type_counts.items():
        pyramid[PYRAMID_KEYS.get(ttype, "other")] += n
    pj = sum(pyramid.values()) or 1
    return {
        "metrics": {
            "flakiness_risk_index": round(sleeps / total_tests, 3) if total_tests else 0.0,
            "redundancy_pct": round(100 * dupes / total_tests, 1) if total_tests else 0.0,
            "avg_assertions_per_test": round(total_assertions / total_tests, 2) if total_tests else 0.0,
            "pyramid_distribution": {k: round(100 * v / pj, 1) for k, v in pyramid.items()},
            "skipped_test_count": skipped,
            "tests_with_fixed_sleep": sleeps,
            "total_tests": total_tests,
        }
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("path"); ap.add_argument("--out")
    a = ap.parse_args()
    payload = json.dumps(run(a.path), indent=2)
    open(a.out, "w").write(payload) if a.out else print(payload)


if __name__ == "__main__":
    main()
