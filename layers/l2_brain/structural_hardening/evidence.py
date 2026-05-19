from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Set

from .contracts import EvidenceType


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


class EvidenceCollector:
    def __init__(self, repo_root: Path, semantic_index: Dict[str, Any], semantic_matrix: Dict[str, Any]):
        self.repo_root = repo_root
        self.semantic_index = semantic_index
        self.semantic_matrix = semantic_matrix

        files = semantic_index.get("files") or []
        self.paths: Set[str] = {row.get("path", "") for row in files}
        self.path_to_record: Dict[str, Dict[str, Any]] = {row.get("path", ""): row for row in files if row.get("path")}

        self.spec_paths = [p for p in self.paths if p.startswith("doc/specs/") or p.startswith("docs/specs/")]
        self.test_paths = [p for p in self.paths if self._is_test_path(p)]
        self.runtime_paths = [
            p
            for p in self.paths
            if p.startswith("layers/") and not self._is_test_path(p) and not p.startswith("layers/l2_brain/tests/")
        ]

        self.matrix_by_module: Dict[str, Dict[str, Any]] = {}
        for row in semantic_matrix.get("records") or []:
            module = row.get("module")
            if module:
                self.matrix_by_module[module] = row

        self.core_spec_text = self._safe_read_text(self.repo_root / "doc" / "CORE_SPEC.md")
        self.physical_map_text = self._safe_read_text(self.repo_root / "doc" / "PHYSICAL_MAP.md")

    def collect(self, path: str) -> Dict[str, Any]:
        evidence_refs: List[str] = []
        reasons: List[str] = []

        if path in self.paths:
            evidence_refs.append(EvidenceType.FILE_EXISTS.value)

        record = self.path_to_record.get(path, {})
        if path.endswith(".py"):
            if self._is_python_parseable(path):
                evidence_refs.append(EvidenceType.IMPORTABLE.value)

        stem = Path(path).stem
        token_stem = self._normalize_stem(stem)

        matrix_row = self.matrix_by_module.get(path, {})
        related_specs: Set[str] = set(matrix_row.get("likely_specs") or [])
        related_tests: Set[str] = set(matrix_row.get("likely_tests") or [])
        related_runtime: Set[str] = set()

        related_specs.update(self._find_specs_by_text(path, token_stem))
        related_tests.update(self._find_tests_by_stem(token_stem))

        if self._is_test_path(path):
            related_runtime.update(self._find_runtime_by_test_name(path))
            related_runtime.update(self._find_runtime_by_text(path, token_stem))
            if related_runtime:
                evidence_refs.append(EvidenceType.REFERENCES_RUNTIME.value)

        if related_specs:
            evidence_refs.append(EvidenceType.REFERENCED_BY_SPEC.value)
            reasons.append("spec links found")
        if related_tests:
            evidence_refs.append(EvidenceType.REFERENCED_BY_TEST.value)
            reasons.append("test links found")
        if related_runtime:
            evidence_refs.append(EvidenceType.RUNTIME_IMPORT.value)
            reasons.append("runtime references found")

        if path in self.core_spec_text:
            evidence_refs.append(EvidenceType.CORE_SPEC_REFERENCE.value)
            reasons.append("referenced in CORE_SPEC")
        if path in self.physical_map_text:
            evidence_refs.append(EvidenceType.PHYSICAL_MAP_REFERENCE.value)
            reasons.append("referenced in PHYSICAL_MAP")

        if path.startswith("scripts/") and Path(path).name.startswith("build_"):
            evidence_refs.append(EvidenceType.CLI_ENTRYPOINT.value)

        if Path(path).name in {"pyproject.toml", "package.json", "go.mod", "mix.exs"}:
            evidence_refs.append(EvidenceType.PACKAGE_MANIFEST.value)

        if not evidence_refs:
            evidence_refs.append(EvidenceType.MANUAL_REVIEW_REQUIRED.value)
            reasons.append("no deterministic evidence found")

        return {
            "evidence_refs": sorted(set(evidence_refs)),
            "reasons": sorted(set(reasons)),
            "related_specs": sorted(related_specs),
            "related_tests": sorted(related_tests),
            "related_runtime": sorted(related_runtime),
        }

    def _find_specs_by_text(self, path: str, token_stem: str) -> Set[str]:
        hits: Set[str] = set()
        path_name = Path(path).name
        stem_tokens = [t for t in _TOKEN_RE.findall(token_stem) if len(t) >= 4]
        for spec in self.spec_paths:
            text = self._safe_read_text(self.repo_root / spec)
            if not text:
                continue
            text_lower = text.lower()
            if path_name in text:
                hits.add(spec)
                continue

            token_matches = 0
            for token in stem_tokens:
                if token in text_lower:
                    token_matches += 1
            if token_matches >= 2:
                hits.add(spec)
        return hits

    def _find_tests_by_stem(self, token_stem: str) -> Set[str]:
        hits: Set[str] = set()
        for test in self.test_paths:
            name = Path(test).stem.lower()
            if token_stem and token_stem in name:
                hits.add(test)
            elif name.startswith("test_") and token_stem and name.replace("test_", "", 1) == token_stem:
                hits.add(test)
        return hits

    def _find_runtime_by_test_name(self, test_path: str) -> Set[str]:
        name = Path(test_path).stem.lower()
        base = name
        if base.startswith("test_"):
            base = base.replace("test_", "", 1)
        if base.endswith("_test"):
            base = base[: -len("_test")]

        hits: Set[str] = set()
        for runtime in self.runtime_paths:
            runtime_name = Path(runtime).stem.lower()
            if runtime_name == base or base in runtime_name:
                hits.add(runtime)
        return hits

    def _find_runtime_by_text(self, test_path: str, token_stem: str) -> Set[str]:
        hits: Set[str] = set()
        text = self._safe_read_text(self.repo_root / test_path)
        if not text:
            return hits
        for runtime in self.runtime_paths:
            runtime_name = Path(runtime).stem
            if runtime_name and runtime_name in text:
                hits.add(runtime)
            elif token_stem and token_stem in runtime.lower():
                hits.add(runtime)
        return hits

    def _is_python_parseable(self, path: str) -> bool:
        try:
            text = self._safe_read_text(self.repo_root / path)
            if not text:
                return False
            ast.parse(text)
            return True
        except Exception:
            return False

    @staticmethod
    def _safe_read_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def _normalize_stem(stem: str) -> str:
        tokens = _TOKEN_RE.findall(stem.lower())
        if not tokens:
            return ""
        return "_".join(tokens)

    @staticmethod
    def _is_test_path(path: str) -> bool:
        name = Path(path).name.lower()
        lower = path.lower()
        return (
            "/tests/" in f"/{lower}"
            or lower.startswith("tests/")
            or name.startswith("test_")
            or name.endswith("_test.py")
            or name.endswith("_test.go")
            or name.endswith("_test.exs")
        )
