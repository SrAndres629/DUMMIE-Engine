import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from layers.l2_brain.embedding_mesh.contracts import ContentType, EmbeddingRequest
from layers.l2_brain.embedding_mesh.registry import EmbeddingRegistry
from layers.l2_brain.embedding_mesh.router import EmbeddingRouter

logger = logging.getLogger("brain.embedding_mesh.repo_indexer")


class RepoIndexer:
    """
    Repository semantic indexer.

    Produces a reproducible JSON index with classification and embedding metadata.
    """

    DEFAULT_EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "build",
        "target",
    }

    DEFAULT_EXCLUDE_PATH_PREFIXES = {
        ".aiwg/index/",
        ".aiwg/cache/",
        ".aiwg/memory/",
        ".aiwg/ledger/",
    }

    DEFAULT_INCLUDE_DIRS = {"layers", "scripts", "doc", "docs", "proto", "tests"}
    DEFAULT_INCLUDE_FILES = {"README.md", "pyproject.toml", "package.json", ".gitignore"}

    BINARY_EXTENSIONS = {
        ".db",
        ".sock",
        ".lock",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".pdf",
        ".pyc",
        ".bin",
        ".so",
        ".dll",
    }

    def __init__(self, repo_root: str, max_file_bytes: int = 200000, embedding_store_dims: int = 64):
        self.repo_root = Path(repo_root).resolve()
        self.max_file_bytes = max_file_bytes
        self.embedding_store_dims = embedding_store_dims
        self.registry = EmbeddingRegistry()

    def scan(self, generate_embeddings: bool = True) -> Dict[str, Any]:
        files_indexed: List[Dict[str, Any]] = []
        files_scanned = 0

        for rel_path, abs_path in self._iter_candidate_paths():
            files_scanned += 1
            try:
                size_bytes = abs_path.stat().st_size
                if size_bytes > self.max_file_bytes:
                    continue

                if abs_path.suffix.lower() in self.BINARY_EXTENSIONS:
                    continue

                content = abs_path.read_text(encoding="utf-8", errors="ignore")
                sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
                language = self._detect_language(rel_path)
                content_type, capability = EmbeddingRouter.route(path=rel_path, language=language)

                embedding_data = {
                    "vector": [],
                    "dimensions": 0,
                    "vector_space": "none",
                    "degraded": True,
                    "reason": "embedding disabled",
                    "model_used": "none",
                    "status": "skipped",
                }
                if generate_embeddings and content:
                    provider = self.registry.get_provider(capability)
                    req = EmbeddingRequest(
                        content=content[:1000],
                        content_type=content_type,
                        path=rel_path,
                        language=language,
                        capability=capability,
                    )
                    try:
                        response = provider.embed(req)
                        embedding_data = {
                            "vector": response.vector[: self.embedding_store_dims],
                            "dimensions": response.dimensions,
                            "vector_space": response.vector_space,
                            "degraded": response.degraded,
                            "reason": response.reason,
                            "model_used": response.model_used,
                            "status": "ok" if not response.degraded else "degraded",
                        }
                    except Exception as exc:
                        logger.warning("Embedding failure for %s: %s", rel_path, exc)
                        embedding_data.update(
                            {
                                "reason": f"embedding provider error: {exc}",
                                "status": "error",
                            }
                        )

                classification = self._heuristically_classify(rel_path, content_type)
                summary = self._generate_summary(content, rel_path)

                files_indexed.append(
                    {
                        "path": rel_path,
                        "content_type": content_type.value,
                        "language": language,
                        "size_bytes": size_bytes,
                        "sha256": sha256,
                        "capability": capability.value,
                        "vector_space": embedding_data["vector_space"],
                        "embedding_status": embedding_data["status"],
                        "embedding_degraded": embedding_data["degraded"],
                        "embedding_reason": embedding_data["reason"],
                        "model_used": embedding_data["model_used"],
                        "embedding": embedding_data["vector"],
                        "summary": summary,
                        "classification": classification,
                    }
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed scanning %s: %s", rel_path, exc)

        return {
            "repo_root": str(self.repo_root),
            "files_scanned": files_scanned,
            "files_indexed": len(files_indexed),
            "files": files_indexed,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "max_file_bytes": self.max_file_bytes,
            "embedding_store_dims": self.embedding_store_dims,
            "embeddings_enabled": generate_embeddings,
        }

    def _iter_candidate_paths(self) -> Iterable[Tuple[str, Path]]:
        for abs_path in self.repo_root.rglob("*"):
            if not abs_path.is_file():
                continue

            rel_path = abs_path.relative_to(self.repo_root).as_posix()
            if self._is_excluded(rel_path):
                continue
            if not self._is_included(rel_path):
                continue

            yield rel_path, abs_path

    def _is_excluded(self, rel_path: str) -> bool:
        parts = rel_path.split("/")
        for part in parts:
            if part in self.DEFAULT_EXCLUDE_DIRS:
                return True

        for prefix in self.DEFAULT_EXCLUDE_PATH_PREFIXES:
            if rel_path.startswith(prefix):
                return True

        return False

    def _is_included(self, rel_path: str) -> bool:
        parts = rel_path.split("/")
        if len(parts) == 1:
            return parts[0] in self.DEFAULT_INCLUDE_FILES
        return parts[0] in self.DEFAULT_INCLUDE_DIRS

    def _heuristically_classify(self, rel_path: str, content_type: ContentType) -> str:
        path_lower = rel_path.lower()

        if content_type == ContentType.TEST:
            return "TEST"
        if content_type == ContentType.SPEC:
            return "SPEC"
        if content_type == ContentType.REPORT:
            return "REPORT"
        if "legacy" in path_lower or "deprecated" in path_lower:
            return "LEGACY"
        if "/deps/" in f"/{path_lower}" or "/vendor/" in f"/{path_lower}":
            return "GENERATED"
        if "generated" in path_lower or path_lower.endswith("_pb2.py") or path_lower.endswith("_pb2_grpc.py"):
            return "GENERATED"
        if path_lower.startswith("layers/") and content_type == ContentType.CODE:
            return "ACTIVE_CANDIDATE"
        if content_type == ContentType.CONFIG:
            return "CONFIG"

        return "UNKNOWN"

    def _detect_language(self, rel_path: str) -> str:
        suffix = Path(rel_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".go": "go",
            ".rs": "rust",
            ".ex": "elixir",
            ".exs": "elixir",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".sh": "bash",
            ".proto": "protobuf",
            ".md": "markdown",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".toml": "toml",
            ".feature": "gherkin",
        }
        return mapping.get(suffix, "unknown")

    def _generate_summary(self, content: str, rel_path: str) -> str:
        if not content:
            return f"Empty file: {rel_path}"

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return f"Whitespace-only file: {rel_path}"

        first = lines[0]
        if first.startswith(("#", "//", "%", "\"\"\"", "'''", "--")):
            summary = first.lstrip("#/%-\"' ").strip()
            if summary:
                return summary[:140]

        return " ".join(lines[:2])[:140]
