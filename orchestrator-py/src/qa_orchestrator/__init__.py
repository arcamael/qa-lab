"""qa_orchestrator — the Python side of the QA lab seam."""
from .results import Summary, load_report, summarize

__all__ = ["Summary", "load_report", "summarize"]
