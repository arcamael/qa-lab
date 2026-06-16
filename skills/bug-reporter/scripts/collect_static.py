#!/usr/bin/env python3
"""Collect bug candidates from static-analysis output.

Auto-detects and parses: SARIF (Semgrep/CodeQL/gitleaks/ESLint-sarif), `npm audit --json`, and
Trivy/OSV JSON. Emits normalized candidates. Tool severity is a starting point — the skill re-rates
by real blast radius (see references/static-sources.md). Reads files; runs no scanners.

Usage: python collect_static.py <file> [<file> ...]
"""
from __future__ import annotations

import sys
from typing import Any

from _common import emit, load_json, make_candidate, more_severe

# SARIF level -> our severity; a security/cwe-tagged rule bumps one level harsher.
_SARIF_LEVEL = {"error": "major", "warning": "minor", "note": "info", "none": "info"}
_NPM_SEV = {"critical": "critical", "high": "major", "moderate": "minor", "low": "info", "info": "info"}


def _from_sarif(doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for run in doc.get("runs", []):
        tool = (run.get("tool", {}).get("driver", {}) or {}).get("name", "sast")
        # index rule metadata (tags) for security bumping
        rules = {r.get("id"): r for r in (run.get("tool", {}).get("driver", {}).get("rules", []) or [])}
        for res in run.get("results", []):
            rule_id = res.get("ruleId") or res.get("rule", {}).get("id") or "rule"
            level = res.get("level") or rules.get(rule_id, {}).get("defaultConfiguration", {}).get("level", "warning")
            sev = _SARIF_LEVEL.get(level, "minor")
            tags = " ".join(rules.get(rule_id, {}).get("properties", {}).get("tags", []) or []).lower()
            is_security = any(t in tags for t in ("security", "cwe", "owasp")) or "secret" in tool.lower()
            if is_security:
                sev = more_severe(sev)
            msg = (res.get("message", {}) or {}).get("text", "") or rule_id
            loc = (res.get("locations") or [{}])[0].get("physicalLocation", {})
            artifact = (loc.get("artifactLocation", {}) or {}).get("uri", "")
            line = (loc.get("region", {}) or {}).get("startLine", 0)
            source = "secret" if "secret" in tool.lower() or "gitleaks" in tool.lower() else "sast"
            out.append(make_candidate(
                source=source,
                title=f"[{tool}] {msg}",
                severity=sev,
                location={"file": artifact, "line": line, "rule_id": rule_id},
                evidence=[f"tool: {tool}", f"rule: {rule_id}", f"level: {level}"],
                fp_parts=[tool, rule_id, artifact.split("/")[-1]],  # NOT line: robust to drift
            ))
    return out


def _from_npm_audit(doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    vulns = doc.get("vulnerabilities", {})
    if isinstance(vulns, dict):  # npm v7+ shape
        for pkg, v in vulns.items():
            sev = _NPM_SEV.get(str(v.get("severity", "moderate")), "minor")
            via = v.get("via", [])
            title = next((x.get("title") for x in via if isinstance(x, dict) and x.get("title")), f"vulnerable dependency {pkg}")
            out.append(make_candidate(
                source="sca",
                title=f"{pkg}: {title}",
                severity=sev,
                location={"file": "package.json", "rule_id": pkg},
                evidence=[f"package: {pkg}", f"severity(tool): {v.get('severity')}", "remediation: see `npm audit fix`"],
                fp_parts=["npm-audit", pkg],  # one issue per package
            ))
    return out


def _from_trivy_osv(doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    results = doc.get("Results") or doc.get("results") or []
    for r in results:
        for v in (r.get("Vulnerabilities") or r.get("vulnerabilities") or []):
            vid = v.get("VulnerabilityID") or v.get("id") or "CVE"
            pkg = v.get("PkgName") or v.get("package", {}).get("name", "dependency")
            sev = _NPM_SEV.get(str(v.get("Severity", "MEDIUM")).lower(), "minor")
            fixed = v.get("FixedVersion") or "see advisory"
            out.append(make_candidate(
                source="sca",
                title=f"{pkg}: {vid}",
                severity=sev,
                location={"file": r.get("Target", "dependencies"), "rule_id": vid},
                evidence=[f"package: {pkg}", f"id: {vid}", f"fixed in: {fixed}"],
                fp_parts=["trivy", vid, pkg],
            ))
    return out


def parse(path: str) -> list[dict[str, Any]]:
    try:
        doc = load_json(path)
    except (ValueError, OSError) as e:
        print(f"skip {path}: {e}", file=sys.stderr)
        return []
    if not isinstance(doc, dict):
        return []
    if "runs" in doc and "$schema" in str(doc.get("$schema", "")) or "runs" in doc and "version" in doc:
        return _from_sarif(doc)
    if "vulnerabilities" in doc and "metadata" in doc:
        return _from_npm_audit(doc)
    if "Results" in doc or "results" in doc:
        return _from_trivy_osv(doc)
    if "runs" in doc:
        return _from_sarif(doc)
    print(f"skip {path}: unrecognized format", file=sys.stderr)
    return []


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: collect_static.py <file> [<file> ...]", file=sys.stderr)
        return 2
    candidates: list[dict[str, Any]] = []
    for path in argv[1:]:
        candidates.extend(parse(path))
    emit(candidates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
