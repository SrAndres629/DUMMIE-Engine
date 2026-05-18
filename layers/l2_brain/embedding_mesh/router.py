import os
from pathlib import Path
from typing import Optional, Tuple

from layers.l2_brain.embedding_mesh.contracts import ContentType, EmbeddingCapability


_CODE_EXTENSIONS = {
    ".py",
    ".go",
    ".rs",
    ".ex",
    ".exs",
    ".js",
    ".ts",
    ".tsx",
    ".sh",
    ".proto",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
}

_CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
_MARKDOWN_EXTENSIONS = {".md", ".txt", ".rst"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"}


class EmbeddingRouter:
    """
    Routes repository content into content type and embedding capability.
    """

    @staticmethod
    def route(
        path: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        language: Optional[str] = None,
    ) -> Tuple[ContentType, EmbeddingCapability]:
        if content_type and content_type != ContentType.UNKNOWN:
            return content_type, EmbeddingRouter._capability_for_type(content_type)

        if not path:
            return EmbeddingRouter._route_from_language(language)

        normalized_path = str(Path(path)).replace("\\", "/")
        path_lower = normalized_path.lower()
        name = Path(path_lower).name
        ext = Path(path_lower).suffix

        if EmbeddingRouter._is_test_path(path_lower, name):
            return ContentType.TEST, EmbeddingCapability.CODE

        if EmbeddingRouter._is_spec_path(path_lower, ext):
            # Keep specs as text-fast in this phase for low risk and local availability.
            return ContentType.SPEC, EmbeddingCapability.TEXT_FAST

        if EmbeddingRouter._is_report_path(path_lower):
            return ContentType.REPORT, EmbeddingCapability.TEXT_FAST

        if ext in _CODE_EXTENSIONS or name in {"makefile", "justfile"}:
            return ContentType.CODE, EmbeddingCapability.CODE

        if ext == ".feature":
            return ContentType.SPEC, EmbeddingCapability.TEXT_FAST

        if ext in _CONFIG_EXTENSIONS:
            return ContentType.CONFIG, EmbeddingCapability.TEXT_FAST

        if ext in _MARKDOWN_EXTENSIONS:
            return ContentType.TEXT, EmbeddingCapability.TEXT_FAST

        if ext in _IMAGE_EXTENSIONS:
            return ContentType.IMAGE, EmbeddingCapability.MULTIMODAL

        if ext == ".pdf":
            return ContentType.PDF, EmbeddingCapability.MULTIMODAL

        return EmbeddingRouter._route_from_language(language)

    @staticmethod
    def _route_from_language(language: Optional[str]) -> Tuple[ContentType, EmbeddingCapability]:
        if language and language.lower() in {
            "python",
            "go",
            "rust",
            "elixir",
            "javascript",
            "typescript",
            "bash",
            "shell",
            "protobuf",
        }:
            return ContentType.CODE, EmbeddingCapability.CODE
        return ContentType.UNKNOWN, EmbeddingCapability.FALLBACK

    @staticmethod
    def _is_test_path(path_lower: str, name: str) -> bool:
        if "/tests/" in f"/{path_lower}" or path_lower.startswith("tests/"):
            return True
        return name.startswith("test_") or name.endswith("_test.py")

    @staticmethod
    def _is_spec_path(path_lower: str, ext: str) -> bool:
        if "doc/specs/" in path_lower or "docs/specs/" in path_lower:
            return True
        if path_lower.endswith(".rules.json"):
            return True
        return False

    @staticmethod
    def _is_report_path(path_lower: str) -> bool:
        return "reports/" in path_lower or path_lower.startswith(".aiwg/reports/")

    @staticmethod
    def _capability_for_type(content_type: ContentType) -> EmbeddingCapability:
        if content_type in (ContentType.CODE, ContentType.TEST):
            return EmbeddingCapability.CODE
        if content_type == ContentType.SPEC:
            return EmbeddingCapability.TEXT_FAST
        if content_type in (ContentType.TEXT, ContentType.REPORT, ContentType.CONFIG):
            return EmbeddingCapability.TEXT_FAST
        if content_type in (ContentType.IMAGE, ContentType.PDF):
            return EmbeddingCapability.MULTIMODAL
        return EmbeddingCapability.FALLBACK
