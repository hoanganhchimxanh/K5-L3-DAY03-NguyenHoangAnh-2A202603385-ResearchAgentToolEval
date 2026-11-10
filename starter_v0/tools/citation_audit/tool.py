from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from tools._shared import err


def audit_citations(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    try:
        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")

        citations: list[dict[str, str]] = []
        issues: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")

            title = item.get("title")
            title = title.strip() if isinstance(title, str) else ""
            url = item.get("url")
            url = url.strip() if isinstance(url, str) else ""
            parsed_url = urlparse(url)
            valid_url = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)

            missing: list[str] = []
            if not title:
                missing.append("title")
            if not valid_url:
                missing.append("url")
            if missing:
                issues.append({"index": index, "missing_or_invalid": missing})
                continue

            source = item.get("source")
            source = source.strip() if isinstance(source, str) else ""
            source = source or parsed_url.netloc.removeprefix("www.")
            citations.append({
                "title": title,
                "url": url,
                "source": source,
                "markdown": f"[{title}]({url}) - {source}",
            })

        return {
            "tool": "audit_citations",
            "valid": not issues,
            "item_count": len(items),
            "citations": citations,
            "issues": issues,
        }
    except Exception as exc:
        return err("audit_citations", exc)
