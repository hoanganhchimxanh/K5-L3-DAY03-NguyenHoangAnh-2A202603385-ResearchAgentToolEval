"""Tool Unit Test Challenge — filled in by the team.

Patterns come from test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS
from tools._shared import clamp_int

clarify = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send = TOOL_FUNCTIONS["send"]
lookup = TOOL_FUNCTIONS["lookup"]
fetch = TOOL_FUNCTIONS["fetch"]
timeline = TOOL_FUNCTIONS["timeline"]
social_search = TOOL_FUNCTIONS["social_search"]
policy = TOOL_FUNCTIONS["policy"]
hackernews = TOOL_FUNCTIONS["hackernews"]
wikipedia = TOOL_FUNCTIONS["wikipedia"]
github_repos = TOOL_FUNCTIONS["github_repos"]
hf_papers = TOOL_FUNCTIONS["hf_papers"]


def _tweets(n: int, *, start: int = 0) -> list[dict]:
    return [{"tweet_id": str(start + i), "screen_name": "sama", "text": f"tweet {start + i}"} for i in range(n)]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify(question="Chọn nguồn?", response_type="choice", options=["Web", "Twitter"])

    assert result["options"] == ["Web", "Twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    # both A items are listed under the single A heading, before B
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}", "url": f"https://x.com/{i}"} for i in range(3)]
    lines = format_tool(items=items, template="thread")["markdown"].split("\n\n")

    assert [line.split(" ", 1)[0] for line in lines] == ["1/", "2/", "3/"]


@pytest.mark.parametrize("items", [None, []])
def test_format_empty_items_does_not_crash(items) -> None:
    result = format_tool(items=items, template="sections")

    assert result["item_count"] == 0
    assert result["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@team_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:abc/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "@team_channel"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin AI", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nBody",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch(url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://www.example.com/post",
        "source": "example.com",
        "summary": "# Hello\nBody",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 9000, "metadata": {}}}))

    summary = fetch(url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": [{"screen_name": "sama", "text": "no id"}, *_tweets(6)]}))

    result = timeline(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/sama/status/")
    assert "no id" not in [item["summary"] for item in result["items"]]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": _tweets(2)}))

    social_search(query="OpenAI", search_type="Top")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}


# Regression (Challenge+): before the fix, `limit=-1` sliced items[:-1] and silently
# dropped the last tweet (3 tweets -> 2; 1 tweet -> 0), and `limit="abc"` turned a good
# API response into a ValueError. See REPORT B5.
@pytest.mark.parametrize("bad_limit, expected", [(-1, 3), (0, 3), ("2", 2), ("abc", 3), (None, 3)])
def test_timeline_bad_limit_from_model_falls_back_to_default(monkeypatch, fake_http, bad_limit, expected) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(3)}))

    result = timeline(screenname="sama", limit=bad_limit)

    assert len(result["items"]) == expected


def test_social_search_negative_limit_does_not_drop_last_item(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(1)}))

    assert len(social_search(query="AI", limit=-1)["items"]) == 1


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy(query="")

    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy(query="confidential customer data AI tools", policy_area="data_privacy", top_k=5)

    assert result["results"], "expected at least one data_privacy hit"
    assert {hit["policy_area"] for hit in result["results"]} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy(query="source citation tweet verified", policy_area="source_citation", top_k=10)

    untrusted = [line for hit in result["results"] for line in hit["untrusted_text"]]
    facts = " ".join(hit["facts"] for hit in result["results"])
    assert any(line.lower().startswith("assistant:") for line in untrusted)
    assert "assistant:" not in facts.lower()


# ---------------- shared helper ----------------

@pytest.mark.parametrize("value, expected", [(3, 3), ("7", 7), (0, 5), (-2, 5), (None, 5), ("x", 5), (999, 20)])
def test_clamp_int_coerces_model_values(value, expected) -> None:
    assert clamp_int(value, 5, hi=20) == expected


# ---------------- hackernews (team tool) ----------------

def test_hackernews_maps_hits_and_falls_back_to_hn_link(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "1", "title": "Show HN: X", "url": "https://www.x.dev/post", "points": 120, "num_comments": 30,
         "author": "pg", "created_at": "2026-11-01T00:00:00Z"},
        {"objectID": "2", "title": "Ask HN: Y?", "url": None, "points": 5, "num_comments": 2, "author": "dang"},
    ]}))

    result = hackernews(query="LLM agents", sort="date", limit=2)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "LLM agents", "tags": "story", "hitsPerPage": 2}
    assert result["items"][0]["source"] == "x.dev"
    assert result["items"][0]["summary"] == "120 points · 30 comments · by pg"
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=2"


@pytest.mark.parametrize("kwargs", [{"query": ""}, {"query": "   "}, {"query": "rust", "sort": "Top"}])
def test_hackernews_bad_input_returns_error_without_request(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    result = hackernews(**kwargs)

    assert result["error"] == "ValueError"
    assert calls == []


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    assert hackernews(query="rust")["error"] == "HTTPError"


# ---------------- wikipedia (team tool) ----------------

def test_wikipedia_maps_summary_and_encodes_title(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "type": "standard",
        "title": "Transformer (deep learning)",
        "extract": "In deep learning, the transformer is ...",
        "description": "Machine learning architecture",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Transformer_(deep_learning)"}},
    }))

    result = wikipedia(title="Transformer (deep learning)")

    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Transformer_(deep_learning)"
    assert "User-Agent" in calls[0]["headers"]
    assert result["status"] == "ok"
    assert result["items"][0]["summary"].startswith("In deep learning")
    assert result["items"][0]["url"].endswith("/wiki/Transformer_(deep_learning)")


@pytest.mark.parametrize("kwargs", [{"title": ""}, {"title": "AI", "lang": "fr"}])
def test_wikipedia_bad_input_returns_error_without_request(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({}))

    result = wikipedia(**kwargs)

    assert result["error"] == "ValueError"
    assert calls == []


def test_wikipedia_404_returns_not_found_instead_of_error(fake_http) -> None:
    fake_http(FakeResponse({"status": 404}, status_code=404))

    result = wikipedia(title="Không tồn tại xyz", lang="vi")

    assert result["status"] == "not_found"
    assert result["items"] == []
    assert "error" not in result


def test_wikipedia_network_error_returns_error_dict(fake_http) -> None:
    fake_http(requests.ConnectionError("offline"))

    assert wikipedia(title="AI")["error"] == "ConnectionError"


# ---------------- github_repos (team tool) ----------------

def test_github_repos_sends_query_and_maps_repos(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": [
        {"full_name": "org/agent", "html_url": "https://github.com/org/agent", "description": "Agent lib",
         "stargazers_count": 1200, "language": "Python", "updated_at": "2026-11-01T00:00:00Z"},
    ]}))

    result = github_repos(query="llm agent", sort="updated", limit="3")

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "llm agent", "sort": "updated", "order": "desc", "per_page": 3}
    assert result["items"][0]["title"] == "org/agent"
    assert result["items"][0]["stars"] == 1200


@pytest.mark.parametrize("kwargs", [{"query": ""}, {"query": "agent", "sort": "forks"}])
def test_github_repos_bad_input_returns_error_without_request(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    assert github_repos(**kwargs)["error"] == "ValueError"
    assert calls == []


def test_github_repos_rate_limit_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"message": "API rate limit exceeded"}, status_code=403))

    assert github_repos(query="agent")["error"] == "HTTPError"


# ---------------- hf_papers (team tool) ----------------

def test_hf_papers_maps_entries_and_passes_date(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {"title": "Paper A", "summary": "s" * 900, "publishedAt": "2026-11-09T00:00:00Z",
         "paper": {"id": "2611.00001", "upvotes": 42}},
    ]))

    result = hf_papers(date="2026-11-09", limit=1)

    assert calls[0]["url"] == "https://huggingface.co/api/daily_papers"
    assert calls[0]["params"] == {"limit": 1, "date": "2026-11-09"}
    item = result["items"][0]
    assert item["url"] == "https://huggingface.co/papers/2611.00001"
    assert item["arxiv_id"] == "2611.00001"
    assert len(item["summary"]) == 600


def test_hf_papers_without_date_omits_date_param(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    hf_papers()

    assert "date" not in calls[0]["params"]


@pytest.mark.parametrize("bad_date", ["hôm nay", "09/11/2026", "2026-1-9"])
def test_hf_papers_bad_date_returns_error_without_request(fake_http, bad_date) -> None:
    calls = fake_http(FakeResponse([]))

    assert hf_papers(date=bad_date)["error"] == "ValueError"
    assert calls == []


def test_hf_papers_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))

    assert hf_papers()["error"] == "HTTPError"
