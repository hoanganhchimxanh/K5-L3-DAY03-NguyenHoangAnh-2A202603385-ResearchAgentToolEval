from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

LANGS = {"en", "vi"}
HEADERS = {"User-Agent": "research-agent-lab/1.0 (educational project)"}


def wikipedia_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    """Get the lead summary of one Wikipedia article via the REST API (no key needed)."""
    try:
        title = (title or "").strip()
        if not title:
            raise ValueError("title must not be empty")
        lang = (lang or "en").strip().lower()
        if lang not in LANGS:
            raise ValueError(f"lang must be one of {sorted(LANGS)}, got {lang!r}")
        page = quote(title.replace(" ", "_"), safe="()_,'")
        response = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{page}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if response.status_code == 404:
            return {"tool": "wikipedia", "title": title, "lang": lang, "status": "not_found", "items": []}
        response.raise_for_status()
        data = response.json()
        url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or ""
        return {
            "tool": "wikipedia",
            "title": title,
            "lang": lang,
            "status": "disambiguation" if data.get("type") == "disambiguation" else "ok",
            "items": [{
                "title": data.get("title") or title,
                "url": url,
                "source": f"{lang}.wikipedia.org",
                "summary": data.get("extract") or "",
                "description": data.get("description") or "",
            }],
        }
    except Exception as exc:
        return err("wikipedia", exc)
