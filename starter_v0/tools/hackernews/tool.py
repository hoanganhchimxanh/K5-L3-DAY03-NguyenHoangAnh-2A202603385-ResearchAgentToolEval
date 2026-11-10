from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, clamp_int, domain, err

HN_API = "https://hn.algolia.com/api/v1"
SORTS = {"relevance": "search", "date": "search_by_date"}


def search_hackernews(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via the public Algolia API (no key needed)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must not be empty")
        if sort not in SORTS:
            raise ValueError(f"sort must be one of {sorted(SORTS)}, got {sort!r}")
        count = clamp_int(limit, 5, hi=20)
        response = requests.get(
            f"{HN_API}/{SORTS[sort]}",
            params={"query": query, "tags": "story", "hitsPerPage": count},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = []
        for hit in response.json().get("hits", [])[:count]:
            story_id = hit.get("objectID") or ""
            hn_url = f"https://news.ycombinator.com/item?id={story_id}" if story_id else ""
            url = hit.get("url") or hn_url
            items.append({
                "title": hit.get("title") or "",
                "url": url,
                "source": domain(url) or "news.ycombinator.com",
                "summary": f"{hit.get('points') or 0} points · {hit.get('num_comments') or 0} comments · by {hit.get('author') or '?'}",
                "date": hit.get("created_at"),
                "hn_url": hn_url,
            })
        return {"tool": "hackernews", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("hackernews", exc)
