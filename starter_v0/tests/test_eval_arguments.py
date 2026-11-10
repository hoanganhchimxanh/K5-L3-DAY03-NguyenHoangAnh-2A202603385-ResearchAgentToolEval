"""Regression: evaluating a list of item objects must not crash or lose order."""
from run_eval import evaluate_phase_b


def deduplicate_case(items):
    return {
        "failure_type": "wrong_tool",
        "expect": {"tool_calls": [{"name": "deduplicate", "args": {"items": items}}]},
    }


def test_eval_accepts_matching_list_of_objects() -> None:
    items = [{"title": "First", "url": "https://example.com/a"}, {"title": "Second", "url": "https://example.com/b"}]
    result = evaluate_phase_b(deduplicate_case(items), [{"name": "deduplicate", "args": {"items": items}}], None)
    assert result["passed"] is True


def test_eval_rejects_reordered_items_when_first_occurrence_matters() -> None:
    items = [{"title": "First", "url": "https://example.com/a"}, {"title": "Copy", "url": "https://example.com/a"}]
    result = evaluate_phase_b(
        deduplicate_case(items),
        [{"name": "deduplicate", "args": {"items": list(reversed(items))}}],
        None,
    )
    assert result["passed"] is False
    assert result["observed_mismatch"] == "wrong_arg_value"
