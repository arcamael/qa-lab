from qa_orchestrator import summarize


def _report() -> dict:
    return {
        "stats": {"expected": 2, "unexpected": 1, "flaky": 0, "skipped": 0},
        "suites": [
            {
                "specs": [
                    {"title": "login works", "ok": True},
                    {"title": "search returns results", "ok": True},
                ],
                "suites": [
                    {"specs": [{"title": "wrong password rejected", "ok": False}]}
                ],
            }
        ],
    }


def test_counts_come_from_stats_when_present():
    s = summarize(_report())
    assert (s.passed, s.failed, s.total) == (2, 1, 3)
    assert s.ok is False


def test_failed_titles_are_collected_by_walking_the_tree():
    s = summarize(_report())
    assert s.failed_titles == ["wrong password rejected"]


def test_counts_are_derived_when_stats_absent():
    report = _report()
    del report["stats"]
    s = summarize(report)
    assert (s.passed, s.failed) == (2, 1)
