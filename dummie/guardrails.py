from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from dummie.paths import AIWG, CONTEXT_KILLER_PATTERNS, DEFAULT_EXCLUDED_PATHS, ROOT, normalize_repo_path


@dataclass
class RepoGuardReport:
    decision: str
    blocked_paths: list[str]
    warnings: list[str]
    staged_paths: list[str]
    read_exclusions: list[str]
    kuzu_4dtes: dict

    def to_dict(self) -> dict:
        return asdict(self)


class ContextBanPolicy:
    """Intelligent ban policy for context killers and repo bloat artifacts."""

    HARD_BLOCK_PREFIXES = [
        ".aiwg/memory/",
        ".aiwg/workspaces/",
        ".aiwg/tools/",
        "node_modules/",
        ".venv/",
        "venv/",
        "target/",
        "dist/",
        "build/",
    ]

    HARD_BLOCK_EXACT = {
        ".env",
        ".aiwg/memory/loci.db",
        ".aiwg/memory/loci_codex.db",
        ".aiwg/memory/loci_codex_cli.db",
    }

    @classmethod
    def classify(cls, rel_path: str) -> str | None:
        path = rel_path.strip().replace("\\", "/")
        if path in cls.HARD_BLOCK_EXACT:
            return "blocked_sensitive_or_runtime"
        if any(path.startswith(prefix) for prefix in cls.HARD_BLOCK_PREFIXES):
            return "blocked_bloat_or_runtime"
        for pattern in CONTEXT_KILLER_PATTERNS:
            if Path(path).match(pattern):
                return "blocked_context_killer_pattern"
        return None


class DummieRepoGuard:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.aiwg = AIWG

    def evaluate(self) -> RepoGuardReport:
        staged = self._git_staged_or_changed_paths()
        blocked: list[str] = []
        warnings: list[str] = []

        for rel in staged:
            reason = ContextBanPolicy.classify(rel)
            if reason:
                blocked.append(f"{rel}::{reason}")

        kuzu_report = self._kuzu_4dtes_guard(staged)
        warnings.extend(kuzu_report.get("warnings", []))

        decision = "PASS" if not blocked else "FAIL"
        return RepoGuardReport(
            decision=decision,
            blocked_paths=sorted(blocked),
            warnings=warnings,
            staged_paths=sorted(staged),
            read_exclusions=list(DEFAULT_EXCLUDED_PATHS),
            kuzu_4dtes=kuzu_report,
        )

    def _git_staged_or_changed_paths(self) -> list[str]:
        cmd = ["git", "status", "--short"]
        proc = subprocess.run(cmd, cwd=self.root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            return []

        paths: list[str] = []
        for line in proc.stdout.splitlines():
            line = line.rstrip()
            if not line:
                continue
            raw = line[3:] if len(line) > 3 else line
            if " -> " in raw:
                raw = raw.split(" -> ", 1)[1]
            paths.append(raw.strip())
        return sorted(set(paths))

    def _kuzu_4dtes_guard(self, changed_paths: Iterable[str]) -> dict:
        warnings: list[str] = []
        changed = list(changed_paths)

        forbidden_db = [p for p in changed if p.startswith(".aiwg/memory/") and p.endswith(".db")]
        if forbidden_db:
            warnings.append("Kuzu guard: runtime DB files detected in git working set.")

        legacy_pattern_hits = self._scan_legacy_kuzu_patterns()
        if legacy_pattern_hits:
            warnings.append("Kuzu guard: legacy kuzu_data references still exist and should remain blocked in new flows.")

        return {
            "forbidden_db_in_git": forbidden_db,
            "legacy_kuzu_data_references": legacy_pattern_hits,
            "memory_db_policy": "runtime_local_do_not_commit",
        }

    def _scan_legacy_kuzu_patterns(self) -> list[str]:
        rg = shutil.which("rg")
        if rg:
            proc = subprocess.run(
                [rg, "-l", "kuzu_data", "layers/l2_brain", "-g", "*.py"],
                cwd=self.root,
                text=True,
                capture_output=True,
                check=False,
            )
            if proc.returncode in {0, 1}:
                hits = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
                return sorted(set(hits))

        results: list[str] = []
        for path in (self.root / "layers" / "l2_brain").rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if "kuzu_data" in text:
                results.append(normalize_repo_path(path))
        return sorted(set(results))


def write_repo_guard_report(report: RepoGuardReport) -> Path:
    out = AIWG / "reports" / "repo_context_guard_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return out
