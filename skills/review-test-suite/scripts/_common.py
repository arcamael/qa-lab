"""Shared, dependency-free helpers for the review-test-suite scripts.

Discovery, language/framework detection, test-type classification, and a heuristic
per-test-body extractor for JS/TS, Python, and Java. Deliberately conservative: a missed
test is better than a false accusation. No third-party imports (NFR: runs anywhere).
"""
from __future__ import annotations

import os
import re
from typing import Iterator

EXCLUDE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "dist", "build", "__pycache__",
    ".pytest_cache", "coverage", ".next", "target", "out", "vendor",
}
EXCLUDE_FILE_HINTS = ("__snapshots__", ".snap", ".min.", ".d.ts")

EXT_LANG = {
    ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript",
    ".mjs": "javascript", ".py": "python", ".java": "java", ".rb": "ruby", ".go": "go",
    ".cs": "csharp", ".feature": "gherkin",
}

TEST_NAME_RE = re.compile(r"(test|spec|_test|\.test|\.spec|it_)", re.IGNORECASE)

FRAMEWORK_SIGNALS = {
    "playwright": (r"@playwright/test", r"playwright"),
    "cypress": (r"\bcy\.", r"cypress"),
    "jest": (r"@jest", r"\bjest\b", r"describe\(", r"\bit\("),
    "vitest": (r"\bvitest\b",),
    "mocha": (r"\bmocha\b",),
    "pytest": (r"\bimport pytest\b", r"def test_", r"@pytest"),
    "unittest": (r"import unittest", r"TestCase"),
    "junit": (r"org\.junit", r"@Test"),
    "selenium": (r"selenium", r"webdriver"),
    "k6": (r"k6/http", r"export default function", r"import http from 'k6'"),
    "jmeter": (r"jmeterTestPlan",),
    "restassured": (r"io\.restassured", r"RestAssured"),
    "cucumber": (r"@cucumber", r"Scenario:", r"Feature:"),
    "pact": (r"@pact", r"pact",),
    "axe": (r"axe-core", r"@axe-core"),
    "supertest": (r"supertest",),
    "newman": (r"newman",),
}

# Directory-name -> taxonomy type (highest-precedence signal).
DIR_TYPE = {
    "unit": "unit", "integration": "integration", "component": "component",
    "contract": "contract", "api": "api", "e2e": "e2e", "system": "e2e",
    "smoke": "smoke", "sanity": "smoke", "regression": "regression",
    "exploratory": "exploratory", "perf": "performance", "performance": "performance",
    "load": "performance", "stress": "performance", "security": "security",
    "sec": "security", "compliance": "compliance", "a11y": "accessibility",
    "accessibility": "accessibility", "usability": "usability",
    "compatibility": "compatibility", "l10n": "localization", "i18n": "localization",
    "reliability": "reliability", "chaos": "reliability", "recovery": "recoverability",
    "visual": "visual-regression", "observability": "observability", "privacy": "privacy",
    "ai": "ai-ml", "ml": "ai-ml", "eval": "ai-ml", "evals": "ai-ml",
}


def discover_test_files(root: str) -> list[str]:
    found: list[str] = []
    if os.path.isfile(root):
        return [root]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in EXT_LANG:
                continue
            if any(h in fn for h in EXCLUDE_FILE_HINTS):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            # A file is a "test" if its name or its path signals it.
            if TEST_NAME_RE.search(fn) or any(seg in DIR_TYPE for seg in rel.lower().split(os.sep)):
                found.append(full)
    return sorted(found)


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def detect_language(path: str) -> str:
    return EXT_LANG.get(os.path.splitext(path)[1].lower(), "unknown")


def detect_frameworks(text: str) -> list[str]:
    hits = []
    for name, patterns in FRAMEWORK_SIGNALS.items():
        if any(re.search(p, text) for p in patterns):
            hits.append(name)
    return hits


def classify_type(path: str, text: str, frameworks: list[str], root: str) -> tuple[str, float, str]:
    """Return (type, confidence, signal)."""
    rel = os.path.relpath(path, root).lower()
    for seg in rel.split(os.sep):
        if seg in DIR_TYPE:
            return DIR_TYPE[seg], 0.9, f"directory:{seg}"
    fw = set(frameworks)
    if "k6" in fw or "jmeter" in fw:
        return "performance", 0.85, "framework"
    if "axe" in fw:
        return "accessibility", 0.85, "framework"
    if "pact" in fw:
        return "contract", 0.85, "framework"
    if fw & {"playwright", "cypress", "selenium"}:
        # browser frameworks: e2e unless content is clearly api-only
        if re.search(r"\brequest\b|fetch\(|http", text) and not re.search(r"page\.|cy\.|click|locator", text):
            return "api", 0.6, "content:api"
        return "e2e", 0.65, "framework:browser"
    if "cucumber" in fw or "Feature:" in text:
        return "e2e", 0.6, "bdd"
    if re.search(r"\b(request|supertest|RestAssured|http)\b", text):
        return "api", 0.6, "content:api"
    if fw & {"pytest", "jest", "vitest", "mocha", "junit", "unittest"}:
        return "unit", 0.5, "framework:xunit"
    return "other", 0.3, "fallback"


# ---- per-test-body extraction --------------------------------------------------

def _match_brace(text: str, open_idx: int) -> int:
    depth = 0
    i = open_idx
    in_str = None
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
        else:
            if c in "'\"`":
                in_str = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return len(text) - 1


_JS_TEST_RE = re.compile(r"(?:^|[^.\w])(it|test)\s*\(\s*(['\"`])(?P<title>.*?)\2", re.DOTALL)


def _iter_js(text: str) -> Iterator[dict]:
    for m in _JS_TEST_RE.finditer(text):
        start = m.start()
        arrow = text.find("=>", m.end())
        base = arrow if (arrow != -1 and arrow - m.end() < 200) else m.end()
        ob = text.find("{", base)
        if ob == -1:
            continue
        cb = _match_brace(text, ob)
        yield {
            "test_id": m.group("title").strip(),
            "line": text.count("\n", 0, start) + 1,
            "body": text[ob:cb + 1],
            "body_offset": ob,
        }


_PY_DEF_RE = re.compile(r"^(?P<indent>[ \t]*)(?:async\s+)?def\s+(?P<name>test\w*)\s*\(", re.MULTILINE)


def _iter_py(text: str) -> Iterator[dict]:
    lines = text.splitlines(keepends=True)
    line_starts = []
    pos = 0
    for ln in lines:
        line_starts.append(pos)
        pos += len(ln)
    for m in _PY_DEF_RE.finditer(text):
        indent = len(m.group("indent").replace("\t", "    "))
        start_line = text.count("\n", 0, m.start())
        body_lines = []
        for j in range(start_line + 1, len(lines)):
            ln = lines[j]
            if ln.strip() == "":
                body_lines.append(ln)
                continue
            cur_indent = len(ln) - len(ln.lstrip())
            if cur_indent <= indent:
                break
            body_lines.append(ln)
        yield {
            "test_id": m.group("name"),
            "line": start_line + 1,
            "body": "".join(body_lines),
            "body_offset": line_starts[min(start_line + 1, len(line_starts) - 1)] if lines else 0,
        }


_JAVA_TEST_RE = re.compile(r"@Test[\s\S]{0,300}?\b(?P<name>\w+)\s*\([^)]*\)\s*(?:throws[^{]+)?\{")


def _iter_java(text: str) -> Iterator[dict]:
    for m in _JAVA_TEST_RE.finditer(text):
        ob = text.rfind("{", m.start(), m.end())
        if ob == -1:
            continue
        cb = _match_brace(text, ob)
        yield {
            "test_id": m.group("name"),
            "line": text.count("\n", 0, m.start()) + 1,
            "body": text[ob:cb + 1],
            "body_offset": ob,
        }


def iter_tests(text: str, language: str) -> Iterator[dict]:
    if language in ("typescript", "javascript"):
        yield from _iter_js(text)
    elif language == "python":
        yield from _iter_py(text)
    elif language == "java":
        yield from _iter_java(text)


# ---- assertion detection (shared, accurate) ------------------------------------
# Counts assertion *entry points* — expect(...), assert(...), assertEquals(...),
# verify(...), should(...), python `assert x`, AND custom assertion methods such as
# expectLoggedIn() that wrap assertions in a page object. Matcher chains (.toBe, .toEqual)
# are NOT counted separately, so one expect(x).toBe(y) counts once, not twice.
ASSERTION_RE = re.compile(r"\b(?:expect\w*|assert\w*|verify|should)\s*\(|\.should\s*\(|\bassert\s+\w")


def count_assertions(body: str) -> int:
    return len(ASSERTION_RE.findall(body))


def has_assertion(body: str) -> bool:
    return ASSERTION_RE.search(body) is not None
