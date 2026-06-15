#!/usr/bin/env python3
"""Render review-report.md FROM review-report.json (single source of truth).
Usage: python render_report.py review-report.json [--template PATH] > review-report.md
The human report is NEVER hand-written; it is always produced here so the two views agree.
"""
from __future__ import annotations
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "..", "assets", "report-template.md")

SEV_ORDER = {"blocker": 0, "critical": 1, "major": 2, "minor": 3, "info": 4}


def _table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def render(report: dict) -> str:
    sc = report.get("scorecard", {})
    ss = report.get("suite_summary", {})
    findings = sorted(report.get("findings", []),
                      key=lambda f: (f.get("dimension", ""), SEV_ORDER.get(f.get("severity"), 9),
                                     f.get("location", {}).get("file", "")))
    gaps = report.get("coverage_gaps", [])
    actions = report.get("architect_actions", [])

    # top risks: highest-severity findings + high-risk gaps
    top = [f"- **[{f['severity']}]** {f.get('description','')} ({f.get('location',{}).get('file','')})"
           for f in findings[:3]]
    top += [f"- **[gap/{g['risk']}]** {g['area']}: missing {', '.join(g['missing_scenarios'][:2])}"
            for g in gaps if g.get("risk") == "high"][:2]
    top_risks = "\n".join(top) if top else "- None at or above the gate threshold."

    dim_rows = [[d["id"], d["name"], f"{d['score']}/100", d["confidence"]] for d in sc.get("dimensions", [])]
    dim_table = _table(["Dim", "Name", "Score", "Confidence"], dim_rows) if dim_rows else "_no dimensions scored_"

    cov_rows = [[c["test_type"], "yes" if c["present"] else "**no**", c["adequacy"], c["risk"]]
                for c in sc.get("coverage_matrix", []) if c.get("risk") != "low" or c.get("present")]
    cov_table = _table(["Type", "Present", "Adequacy", "Risk"], cov_rows) if cov_rows else "_n/a_"

    recs = "\n".join(
        f"- **{a['priority']} · {a['action_type']}** — {a['rationale']} "
        f"(`{a.get('target',{}).get('suggested_path') or a.get('target',{}).get('file','')}`) "
        f"[{a['id']} ← {', '.join(a.get('linked_findings', []))}]"
        for a in sorted(actions, key=lambda a: a.get("priority", "P9"))
    ) or "- No actions proposed."

    fbd = []
    cur = None
    for f in findings:
        if f.get("dimension") != cur:
            cur = f.get("dimension")
            fbd.append(f"\n**{cur}**")
        loc = f.get("location", {})
        fbd.append(f"- `{f['id']}` **[{f['severity']}]** {f.get('smell','')}: {f.get('description','')} "
                   f"— {loc.get('file','')}:{loc.get('line','')} ({loc.get('test_id') or '-'}). "
                   f"_Fix:_ {f.get('recommendation','')}")
    findings_md = "\n".join(fbd) if fbd else "_No findings._"

    gaps_md = "\n".join(
        f"- `{g['id']}` **[{g['risk']}]** {g['area']} ({g['test_type']}): "
        f"missing {', '.join(g['missing_scenarios'])}. {g.get('rationale','')}"
        for g in gaps) or "_No coverage gaps recorded._"

    act_counts = {}
    for a in actions:
        act_counts[a["action_type"]] = act_counts.get(a["action_type"], 0) + 1
    action_summary = ", ".join(f"{k}: {v}" for k, v in sorted(act_counts.items())) or "none"

    tmpl_path = report.get("_template", DEFAULT_TEMPLATE)
    with open(tmpl_path, "r", encoding="utf-8") as fh:
        tmpl = fh.read()

    return tmpl.format(
        suite_name=report.get("suite_name", "suite"),
        reviewed_at=report.get("reviewed_at", ""),
        cycle=report.get("cycle", 1),
        schema_version=report.get("schema_version", ""),
        overall_confidence=sc.get("overall_confidence", "?"),
        overall_health_score=sc.get("overall_health_score", 0),
        go_no_go=sc.get("go_no_go", "?").upper(),
        top_risks=top_risks,
        dimension_table=dim_table,
        coverage_matrix_table=cov_table,
        prioritized_recommendations=recs,
        findings_by_dimension=findings_md,
        coverage_gaps=gaps_md,
        action_summary=f"{len(actions)} actions — {action_summary}",
        inputs_used=", ".join(report.get("inputs_used", ["test files (static)"])),
        limitations=report.get("limitations", "Static analysis only; no runtime/flakiness data."),
        profile=report.get("profile", "default"),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report"); ap.add_argument("--template")
    a = ap.parse_args()
    report = json.load(open(a.report))
    if a.template:
        report["_template"] = a.template
    print(render(report))


if __name__ == "__main__":
    main()
