from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RepoProbeFinding:
    probe_id: str
    severity: str  # PASS|WARNING|ERROR
    message: str
    evidence: Any = None


@dataclass
class RepoProbeResult:
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    findings: list[RepoProbeFinding] = field(default_factory=list)
    layer_summary: dict[str, Any] = field(default_factory=dict)
    language_summary: dict[str, Any] = field(default_factory=dict)
    runtime_summary: dict[str, Any] = field(default_factory=dict)
    recommended_actions: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "findings": [asdict(f) for f in self.findings],
            "layer_summary": self.layer_summary,
            "language_summary": self.language_summary,
            "runtime_summary": self.runtime_summary,
            "recommended_actions": self.recommended_actions,
            "generated_at": self.generated_at,
        }


class RepoProbeRunner:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.aiwg_root = self.root / ".aiwg"
        self.reports_root = self.aiwg_root / "reports"

    def run_all_probes(self) -> RepoProbeResult:
        findings: list[RepoProbeFinding] = []
        
        # Get all git tracked files
        try:
            files = subprocess.check_output(
                ["git", "ls-files"], cwd=self.root, encoding="utf-8"
            ).splitlines()
        except Exception as exc:
            return RepoProbeResult(
                decision="FAIL",
                findings=[RepoProbeFinding("git_ls_files", "ERROR", f"Failed to list files: {exc}")],
                generated_at=self._utc_now()
            )

        layer_summary = self._probe_layers(files, findings)
        lang_summary = self._probe_languages(files, findings)
        runtime_summary = self._probe_runtime_modules(files, findings)
        self._probe_specs_and_tests(files, findings)
        self._probe_state_coherence(findings)

        # Determine decision
        errors = [f for f in findings if f.severity == "ERROR"]
        warnings = [f for f in findings if f.severity == "WARNING"]
        
        if errors:
            decision = "FAIL"
        elif warnings:
            decision = "PASS_WITH_WARNINGS"
        else:
            decision = "PASS"

        recommended = []
        if errors or warnings:
            recommended.append("Review findings in repo_probe_latest.json")
        if "Python" in lang_summary and lang_summary["Python"] > 0.9:
             recommended.append("Add polyglot samples to mitigate Python-only bias")

        return RepoProbeResult(
            decision=decision,
            findings=findings,
            layer_summary=layer_summary,
            language_summary=lang_summary,
            runtime_summary=runtime_summary,
            recommended_actions=recommended,
            generated_at=self._utc_now()
        )

    def _probe_layers(self, files: list[str], findings: list[RepoProbeFinding]) -> dict[str, Any]:
        layer_map = {
            "L0": "layers/l0_overseer",
            "L1": "layers/l1_pipeline",
            "L2": "layers/l2_brain",
            "L3": "layers/l3_nexus",
            "L4": "layers/l4_vault",
            "L5": "layers/l5_bridge",
            "L6": "layers/l6_skin"
        }
        present = {}
        for layer, path in layer_map.items():
            count = sum(1 for f in files if f.startswith(path))
            present[layer] = count
            if count == 0:
                findings.append(RepoProbeFinding("layer_presence", "WARNING", f"Layer {layer} appears empty or missing", {"path": path}))
        
        return present

    def _probe_languages(self, files: list[str], findings: list[RepoProbeFinding]) -> dict[str, Any]:
        ext_map = {
            ".py": "Python",
            ".go": "Go",
            ".ex": "Elixir",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".rs": "Rust",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML"
        }
        counts = {}
        total = 0
        for f in files:
            ext = Path(f).suffix
            lang = ext_map.get(ext, "Other")
            counts[lang] = counts.get(lang, 0) + 1
            total += 1
        
        ratios = {lang: count / total for lang, count in counts.items()}
        if ratios.get("Python", 0) > 0.8:
            findings.append(RepoProbeFinding("polyglot_check", "WARNING", "High Python concentration detected. Ensure polyglot compliance.", {"python_ratio": ratios["Python"]}))
        
        return ratios

    def _probe_runtime_modules(self, files: list[str], findings: list[RepoProbeFinding]) -> dict[str, Any]:
        critical = [
            "layers/l2_brain/cli_control_plane.py",
            "layers/l2_brain/state_coherence_guard.py",
            "layers/l2_brain/embedding_adapter.py"
        ]
        status = {}
        for path in critical:
            exists = path in files
            status[path] = "PRESENT" if exists else "MISSING"
            if not exists:
                findings.append(RepoProbeFinding("runtime_module", "ERROR", f"Critical runtime module missing: {path}"))
        
        return status

    def _probe_specs_and_tests(self, files: list[str], findings: list[RepoProbeFinding]) -> None:
        specs = [f for f in files if f.startswith("doc/specs/") and f.endswith(".md")]
        features = [f for f in files if f.startswith("doc/specs/") and f.endswith(".feature")]
        rules = [f for f in files if f.startswith("doc/specs/") and f.endswith(".rules.json")]
        
        if len(specs) == 0:
            findings.append(RepoProbeFinding("spec_presence", "WARNING", "No Markdown specs found in doc/specs/"))
        
        # Check triplets
        for spec in specs:
            base = spec.replace(".md", "")
            feat = f"{base}.feature"
            rule = f"{base}.rules.json"
            if feat not in features or rule not in rules:
                findings.append(RepoProbeFinding("spec_triplet", "WARNING", f"Incomplete spec triplet for {spec}"))

        tests = [f for f in files if "/tests/test_" in f]
        if len(tests) == 0:
            findings.append(RepoProbeFinding("test_presence", "WARNING", "No tests found in the repository"))

    def _probe_state_coherence(self, findings: list[RepoProbeFinding]) -> None:
        guard_report = self.reports_root / "state_coherence_guard_latest.json"
        if not guard_report.exists():
            findings.append(RepoProbeFinding("state_coherence", "WARNING", "State coherence guard report missing"))
            return
        
        try:
            data = json.loads(guard_report.read_text(encoding="utf-8"))
            if data.get("decision") == "FAIL":
                 findings.append(RepoProbeFinding("state_coherence", "ERROR", "Latest state coherence guard failed", data.get("findings")))
        except Exception as exc:
            findings.append(RepoProbeFinding("state_coherence", "ERROR", f"Failed to read state coherence report: {exc}"))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_report(self, result: RepoProbeResult) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "repo_probe_latest.json").write_text(
            json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
        )


def run_repo_probe(root: str | Path = ".") -> RepoProbeResult:
    runner = RepoProbeRunner(root=root)
    result = runner.run_all_probes()
    runner.write_report(result)
    return result


if __name__ == "__main__":
    res = run_repo_probe()
    print(json.dumps(res.to_dict(), indent=2))
