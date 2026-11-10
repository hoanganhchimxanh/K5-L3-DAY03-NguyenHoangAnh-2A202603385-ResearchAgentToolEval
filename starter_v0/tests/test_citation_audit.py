"""Tests preserved from the target branch citation_audit implementation."""
from tools import TOOL_FUNCTIONS

citation_audit = TOOL_FUNCTIONS["citation_audit"]


def test_citation_audit_formats_complete_source_metadata() -> None:
    result = citation_audit(items=[{
        "title": "Research paper",
        "url": "https://www.example.com/paper",
    }])

    assert result["valid"] is True
    assert result["item_count"] == 1
    assert result["citations"] == [{
        "title": "Research paper",
        "url": "https://www.example.com/paper",
        "source": "example.com",
        "markdown": "[Research paper](https://www.example.com/paper) - example.com",
    }]
    assert result["issues"] == []


def test_citation_audit_returns_error_for_non_list_input() -> None:
    result = citation_audit(items="not a list")

    assert result["error"] == "ValueError"
    assert "non-empty list" in result["message"]


def test_citation_audit_returns_error_for_non_object_entry() -> None:
    result = citation_audit(items=["not an item"])

    assert result["error"] == "ValueError"
    assert "items[0]" in result["message"]


def test_citation_audit_reports_incomplete_citation_without_formatting_it() -> None:
    result = citation_audit(items=[{"title": "Missing URL"}])

    assert result["valid"] is False
    assert result["citations"] == []
    assert result["issues"] == [{"index": 0, "missing_or_invalid": ["url"]}]
