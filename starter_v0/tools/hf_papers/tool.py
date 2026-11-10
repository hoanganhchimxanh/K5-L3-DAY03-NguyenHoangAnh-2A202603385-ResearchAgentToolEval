from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, clamp_int, err

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def hf_daily_papers(date: str = "", limit: int = 5) -> dict[str, Any]:
    """Get the Hugging Face 'Daily Papers' list (community-curated AI papers), no key needed."""
    try:
        date = (date or "").strip()
        if date and not DATE_RE.match(date):
            raise ValueError(f"date must be YYYY-MM-DD or empty, got {date!r}")
        count = clamp_int(limit, 5, hi=30)
        params: dict[str, Any] = {"limit": count}
        if date:
            params["date"] = date
        response = requests.get("https://huggingface.co/api/daily_papers", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        items = []
        for entry in response.json()[:count]:
            paper = entry.get("paper") or {}
            paper_id = paper.get("id") or ""
            items.append({
                "title": entry.get("title") or paper.get("title") or "",
                "url": f"https://huggingface.co/papers/{paper_id}" if paper_id else "",
                "source": "huggingface.co/papers",
                "summary": (entry.get("summary") or paper.get("summary") or "")[:600],
                "arxiv_id": paper_id,
                "upvotes": paper.get("upvotes"),
                "date": entry.get("publishedAt") or paper.get("publishedAt"),
            })
        return {"tool": "hf_papers", "date": date or None, "items": items}
    except Exception as exc:
        return err("hf_papers", exc)
