"""Result compression for dummie_process — saves agent context tokens.

Strategies by response type:
- Long text (>2000 chars): shows first 600 + last 400 chars
- Long JSON arrays (>10 items): shows first 3 + last 3 items
- Nested JSON: shows top-level keys only + key value summary
- Short responses (<500 chars): pass through unchanged
- Errors: pass through unchanged

Compression is lossy but preserves semantic meaning.
"""

import json
import re
import logging

logger = logging.getLogger("dummie-smart.compression")

MAX_UNCOMPRESSED = 500
TRUNCATE_THRESHOLD = 2000
HEAD_CHARS = 600
TAIL_CHARS = 400
ARRAY_TRIM_THRESHOLD = 10
ARRAY_EDGE_ITEMS = 3


class ResultCompressor:
    """Compresses tool execution results to save agent context tokens."""

    def __init__(
        self,
        max_uncompressed: int = MAX_UNCOMPRESSED,
        truncate_threshold: int = TRUNCATE_THRESHOLD,
    ):
        self._max_uncompressed = max_uncompressed
        self._truncate_threshold = truncate_threshold

    def compress(self, text: str) -> dict:
        """Compress a text result. Returns dict with compressed text and metadata."""
        if not text or not isinstance(text, str):
            return {"text": "", "compressed": False, "original_chars": 0}

        original_len = len(text)

        if original_len <= self._max_uncompressed:
            return {"text": text, "compressed": False, "original_chars": original_len}

        compressed = self._try_json(text)
        if compressed is not None:
            t = json.dumps(compressed, ensure_ascii=False)
            compressed_len = len(t)
            saved = original_len - compressed_len
            logger.debug(
                "JSON compression: %d → %d chars (saved %d)",
                original_len,
                compressed_len,
                saved,
            )
            return {
                "text": t,
                "compressed": True,
                "original_chars": original_len,
                "saved_chars": saved,
            }

        if original_len > self._truncate_threshold:
            head = text[:HEAD_CHARS]
            tail = text[-TAIL_CHARS:]
            t = f"{head}\n\n[... {original_len - HEAD_CHARS - TAIL_CHARS} chars truncated ...]\n\n{tail}"
            compressed_len = len(t)
            saved = original_len - compressed_len
            logger.debug(
                "Truncation: %d → %d chars (saved %d)",
                original_len,
                compressed_len,
                saved,
            )
            return {
                "text": t,
                "compressed": True,
                "original_chars": original_len,
                "saved_chars": saved,
            }

        return {"text": text, "compressed": False, "original_chars": original_len}

    def _try_json(self, text: str) -> dict | list | str | None:
        """Try to parse and compress as JSON. Returns compressed dict or None."""
        trimmed = text.strip()
        if not (trimmed.startswith("{") or trimmed.startswith("[")):
            return None

        try:
            parsed = json.loads(trimmed)
        except (json.JSONDecodeError, TypeError):
            return None

        if isinstance(parsed, list):
            return self._compress_array(parsed)
        if isinstance(parsed, dict):
            return self._compress_dict(parsed)

        return None

    def _compress_array(self, arr: list) -> dict:
        if len(arr) <= ARRAY_TRIM_THRESHOLD:
            return {"items": arr, "total": len(arr)}

        edges = arr[:ARRAY_EDGE_ITEMS] + arr[-ARRAY_EDGE_ITEMS:]
        return {
            "first": arr[:ARRAY_EDGE_ITEMS],
            "last": arr[-ARRAY_EDGE_ITEMS:],
            "total": len(arr),
            "middle_hidden": len(arr) - 2 * ARRAY_EDGE_ITEMS,
        }

    def _compress_dict(self, obj: dict) -> dict:
        summary = {"_keys": list(obj.keys())[:20]}

        for key, value in obj.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                if isinstance(value, str) and len(value) > 200:
                    summary[key] = f"{value[:100]}...({len(value)} chars)"
                else:
                    summary[key] = value
            elif isinstance(value, list):
                if len(value) > ARRAY_TRIM_THRESHOLD:
                    summary[key] = {
                        "first": value[:ARRAY_EDGE_ITEMS],
                        "last": value[-ARRAY_EDGE_ITEMS:],
                        "total": len(value),
                        "hidden": len(value) - 2 * ARRAY_EDGE_ITEMS,
                    }
                else:
                    summary[key] = value
            elif isinstance(value, dict):
                summary[key] = {
                    "_nested": True,
                    "_keys": list(value.keys())[:10],
                }
            else:
                summary[key] = str(type(value).__name__)

        return summary


_default = ResultCompressor()


def compress(text: str) -> str:
    """Convenience: compress and return just the text."""
    return _default.compress(text)["text"]
