from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def clamp_int(value: Any, default: int, *, lo: int = 1, hi: int = 50) -> int:
    """Coerce a model-provided count into [lo, hi].

    Models send odd values: "5", 0, -1, None, "abc". Anything that is not a positive
    integer falls back to `default`; values above `hi` are capped.
    """
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    if number < lo:
        return default
    return min(number, hi)


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}

