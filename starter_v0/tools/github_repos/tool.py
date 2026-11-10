from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, clamp_int, err

SORTS = {"stars", "updated"}
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "research-agent-lab"}


def search_github_repos(query: str = "", sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    """Search public GitHub repositories (unauthenticated: ~10 requests/minute)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must not be empty")
        if sort not in SORTS:
            raise ValueError(f"sort must be one of {sorted(SORTS)}, got {sort!r}")
        count = clamp_int(limit, 5, hi=20)
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": sort, "order": "desc", "per_page": count},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = [{
            "title": repo.get("full_name") or "",
            "url": repo.get("html_url") or "",
            "source": "github.com",
            "summary": repo.get("description") or "",
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "updated_at": repo.get("updated_at"),
        } for repo in response.json().get("items", [])[:count]]
        return {"tool": "github_repos", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("github_repos", exc)
