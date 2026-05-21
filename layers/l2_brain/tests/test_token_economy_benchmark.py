"""Tests for TokenEconomyBenchmark — Pack 3 Module 3."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
L2 = ROOT / "layers" / "l2_brain"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(L2) not in sys.path:
    sys.path.insert(0, str(L2))

from layers.l2_brain.context.token_economy_benchmark import (
    TokenEconomyBenchmark,
    TokenEconomyBenchmarkCase,
    TokenEconomyBenchmarkReport,
    run_token_economy_benchmark,
)


@pytest.fixture
def repo_dir(tmp_path):
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    intel = aiwg / "repo_intelligence"
    reports.mkdir(parents=True)
    intel.mkdir(parents=True)
    return tmp_path


class TestTokenEconomyBenchmark:
    def test_compares_all_strategies(self, repo_dir):
        """Must compare at least 5 strategies."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        report = bench.run_benchmark()

        assert len(report.cases) >= 5
        strategies = [c.strategy for c in report.cases]
        assert "raw_folder_naive_estimate" in strategies
        assert "memory_spine_plus_selected_dossiers" in strategies

    def test_raw_greater_than_selected_dossier(self, repo_dir):
        """raw_folder_naive_estimate must have more tokens than optimized strategies."""
        # Create a fake inventory
        intel = repo_dir / ".aiwg" / "repo_intelligence"
        files = [{"path": f"file_{i}.py"} for i in range(10)]
        (intel / "repo_inventory.json").write_text(
            json.dumps({"files": files}), encoding="utf-8"
        )
        # Create fake files
        for f in files:
            fp = repo_dir / f["path"]
            fp.write_text("x" * 1000, encoding="utf-8")

        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        report = bench.run_benchmark()

        raw = next(c for c in report.cases if c.strategy == "raw_folder_naive_estimate")
        selected = next(c for c in report.cases if c.strategy == "repo_intelligence_plus_selected_dossiers")
        spine = next(c for c in report.cases if c.strategy == "memory_spine_plus_selected_dossiers")

        assert raw.estimated_input_tokens >= selected.estimated_input_tokens
        assert raw.estimated_input_tokens >= spine.estimated_input_tokens

    def test_measurement_type_is_deterministic(self, repo_dir):
        """Measurement must be deterministic_estimate."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        report = bench.run_benchmark()

        assert report.measurement_type == "deterministic_estimate"

    def test_writes_json_report(self, repo_dir):
        """Must write valid JSON report."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        bench.run_benchmark()

        path = repo_dir / ".aiwg" / "reports" / "token_economy_benchmark_latest.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "decision" in data

    def test_writes_md_report(self, repo_dir):
        """Must write markdown report."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        bench.run_benchmark()

        path = repo_dir / ".aiwg" / "reports" / "token_economy_benchmark_latest.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Token Economy Benchmark" in content

    def test_evidence_preserved_for_final_strategy(self, repo_dir):
        """Final strategy must preserve required evidence."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        report = bench.run_benchmark()

        spine = next(c for c in report.cases if c.strategy == "memory_spine_plus_selected_dossiers")
        assert spine.required_evidence_preserved is True

    def test_run_function(self, repo_dir, monkeypatch):
        """run_token_economy_benchmark should work."""
        monkeypatch.chdir(repo_dir)
        report = run_token_economy_benchmark(repo_root=repo_dir)
        assert isinstance(report, TokenEconomyBenchmarkReport)

    def test_empty_inventory(self, repo_dir):
        """Should handle empty/missing inventory gracefully."""
        bench = TokenEconomyBenchmark(repo_root=repo_dir, aiwg_root=".aiwg")
        report = bench.run_benchmark()
        assert report.decision == "PASS"
