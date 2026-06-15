#!/usr/bin/env python3
"""Static test-smell detection. Conservative heuristics; see references/smell-catalog.md.
Usage: python detect_smells.py <path> [--out FILE]
Emits JSON: {findings:[{smell,dimension,severity,location,description,evidence,recommendation,effort}]}.
Secret values are NEVER echoed — evidence reports location + category only.
"""
from __future__ import annotations
import argparse, json, re
import _common as C

SLEEP_RE = re.compile(r"waitForTimeout\s*\(|(?<![.\w])time\.sleep\s*\(|Thread\.sleep\s*\(|cy\.wait\s*\(\s*\d")
ASSERT_HINTS = ("expect(", ".should(", "assert ", "assert(", "self.assert", "assertEquals",
                "assertThat", "assertTrue", "assertFalse", "verify(", "pytest.raises",
                ".toBe", ".toEqual", ".toContain", ".toMatch", ".toThrow", ".toHaveTitle",
                ".toBeVisible", ".toHaveCount", "should.")
SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token|authorization)\b\s*[:=]\s*['\"][^'\"]{6,}['\"]")
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]{12,}")
COND_RE = re.compile(r"^\s*(if|for|while|switch)\b", re.MULTILINE)
TAUTOLOGY_RE = re.compile(r"assertTrue\(\s*true\s*\)|expect\(\s*true\s*\)\s*\.toBe\(\s*true\s*\)|assert\s+True\b")
SKIP_RE = re.compile(r"\.skip\b|(?<![\w.])xit\s*\(|@Ignore\b|@Disabled\b|@pytest\.mark\.skip")
ONLY_RE = re.compile(r"(?:it|test|describe)\.only\s*\(")


def _abs_line(text_body_line: int, match_offset_in_body: int, body: str) -> int:
    return text_body_line + body.count("\n", 0, match_offset_in_body)


def run(root: str) -> dict:
    findings = []
    counter = [0]

    def add(**kw):
        counter[0] += 1
        kw["id"] = f"F-{counter[0]:04d}"
        findings.append(kw)

    for f in C.discover_test_files(root):
        text = C.read(f)
        lang = C.detect_language(f)
        # file-level: .only is a critical smell anywhere
        for m in ONLY_RE.finditer(text):
            add(smell="only-focused", dimension="D9", severity="critical",
                location={"file": f, "test_id": None, "line": text.count("\n", 0, m.start()) + 1},
                description="Focused test (.only) will silently skip the rest of the suite in CI.",
                evidence=".only(", recommendation="Remove .only before committing.", effort="trivial")
        for t in C.iter_tests(text, lang):
            body, base_line = t["body"], t["line"]
            tid = t["test_id"]
            loc = {"file": f, "test_id": tid, "line": base_line}
            if SLEEP_RE.search(body):
                add(smell="fixed-sleep", dimension="D4", severity="critical", location=loc,
                    description="Fixed time wait instead of waiting on a condition; high flakiness risk.",
                    evidence="fixed-delay call in test body",
                    recommendation="Replace with an explicit wait/poll on a locator or condition.",
                    effort="small")
            if not C.has_assertion(body):
                add(smell="missing-assertion", dimension="D3", severity="blocker", location=loc,
                    description="No assertion detected; test can pass without verifying anything.",
                    evidence="no recognized assertion API in body",
                    recommendation="Add an assertion that verifies the behavior the test claims to check.",
                    effort="small")
            if TAUTOLOGY_RE.search(body):
                add(smell="tautological-assert", dimension="D3", severity="critical", location=loc,
                    description="Assertion is tautological (asserts a constant); verifies nothing.",
                    evidence="constant assertion",
                    recommendation="Assert the real contract (status/field/decoded value).",
                    effort="small")
            if BEARER_RE.search(body):
                add(smell="hardcoded-secret", dimension="D6", severity="blocker", location=loc,
                    description="Bearer token literal in test.",
                    evidence="bearer-token literal (value redacted)",  # SAFETY: never echo the value
                    recommendation="Move to env/secret store; never commit tokens.",
                    effort="small")
            elif SECRET_RE.search(body):
                add(smell="credential-like-literal", dimension="D6", severity="major", location=loc,
                    description="Credential-like literal assignment; confirm it is test data, not a real secret.",
                    evidence="password/key literal (value redacted)",  # SAFETY: never echo the value
                    recommendation="If a real secret, move to env/secret store; if test data, use a factory/fixture.",
                    effort="small")
            if COND_RE.search(body):
                add(smell="conditional-logic", dimension="D2", severity="major", location=loc,
                    description="Control flow (if/for/while/switch) inside a test; tests should be straight-line.",
                    evidence="control-flow statement in body",
                    recommendation="Split into separate or parameterized tests.", effort="medium")
            if SKIP_RE.search(body):
                add(smell="skipped-debt", dimension="D9", severity="major", location=loc,
                    description="Skipped/ignored test represents silent coverage debt.",
                    evidence="skip/ignore annotation",
                    recommendation="Re-enable or delete with rationale.", effort="small")
            n_assert = C.count_assertions(body)
            if n_assert > 6:
                add(smell="assertion-roulette", dimension="D3", severity="minor", location=loc,
                    description=f"{n_assert} assertions in one test; on failure it's unclear which broke.",
                    evidence="many assertions, likely without messages",
                    recommendation="Split, or add failure messages.", effort="small")
    return {"findings": findings}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--out")
    a = ap.parse_args()
    payload = json.dumps(run(a.path), indent=2)
    open(a.out, "w").write(payload) if a.out else print(payload)


if __name__ == "__main__":
    main()
