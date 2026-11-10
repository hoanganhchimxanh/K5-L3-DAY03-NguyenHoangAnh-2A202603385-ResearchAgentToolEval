from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

from tools._shared import err


ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = ROOT / "exports"
MAX_MARKDOWN_CHARS = 100_000
MAX_FILENAME_CHARS = 80


def _safe_stem(filename: str) -> str:
    value = unicodedata.normalize("NFKD", filename)
    ascii_value = value.encode("ascii", "ignore").decode("ascii").lower()
    stem = Path(ascii_value).stem
    slug = "-".join(re.findall(r"[a-z0-9]+", stem))
    return (slug or "research-answer")[:MAX_FILENAME_CHARS].rstrip("-") or "research-answer"


def save_markdown(content: str = "", filename: str = "") -> dict[str, Any]:
    try:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must be a non-empty Markdown string")
        if len(content) > MAX_MARKDOWN_CHARS:
            raise ValueError(f"content must be {MAX_MARKDOWN_CHARS} characters or fewer")
        if not isinstance(filename, str):
            raise ValueError("filename must be a string")

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        stem = _safe_stem(filename)
        for suffix in range(1, 10_000):
            candidate_stem = stem if suffix == 1 else f"{stem}-{suffix}"
            path = EXPORT_DIR / f"{candidate_stem}.md"
            try:
                with path.open("x", encoding="utf-8", newline="\n") as output:
                    output.write(content)
            except FileExistsError:
                continue
            return {
                "tool": "save_markdown",
                "status": "saved",
                "file_name": path.name,
                "download_url": f"/files/{path.name}",
                "character_count": len(content),
            }
        raise FileExistsError(f"Could not allocate a unique filename for {stem}.md")
    except Exception as exc:
        return err("save_markdown", exc)
