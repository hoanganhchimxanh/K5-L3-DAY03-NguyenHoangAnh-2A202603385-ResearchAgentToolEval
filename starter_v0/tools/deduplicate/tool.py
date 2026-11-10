from __future__ import annotations

from typing import Any

from tools._shared import err


def deduplicate_items(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per nonempty, whitespace-trimmed URL, in input order."""
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of objects")

        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object")
            url = item.get("url")
            if url is not None and not isinstance(url, str):
                raise TypeError(f"items[{index}].url must be a string or null")
            key = (url or "").strip()
            # Missing URLs are not evidence of duplication. Keep those items.
            if key:
                if key in seen:
                    continue
                seen.add(key)
            unique.append(dict(item))

        return {
            "tool": "deduplicate",
            "items": unique,
            "input_count": len(items),
            "item_count": len(unique),
            "removed_count": len(items) - len(unique),
        }
    except (TypeError, ValueError) as exc:
        return err("deduplicate", exc)
