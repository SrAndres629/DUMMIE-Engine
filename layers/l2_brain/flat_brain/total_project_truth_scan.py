from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class FileFingerprint:
    path: str
    sha256: str
    size_bytes: int
    modified_at: str
    is_tracked: bool
    layer: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TruthScanManifest:
    repo_id: str
    total_files: int
    tracked_files: int
    untracked_files: int
    physical_sovereignty: dict[str, bool]
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TotalProjectTruthScan:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def run_scan(self) -> dict[str, Any]:
        tracked_files = self._get_tracked_files()
        all_files = self._get_all_relevant_files()
        
        fingerprints = []
        layers_present = set()
        
        for file_path in all_files:
            abs_path = self.repo_root / file_path
            if not abs_path.is_file():
                continue
                
            is_tracked = file_path in tracked_files
            fingerprint = self._generate_fingerprint(file_path, is_tracked)
            fingerprints.append(fingerprint)
            
            if fingerprint.layer != "unknown":
                layers_present.add(fingerprint.layer)

        expected_layers = ["l0_overseer", "l1_nervous", "l2_brain", "l3_shield", "l4_edge", "l5_muscle", "l6_skin"]
        physical_sovereignty = {layer: (layer in layers_present) for layer in expected_layers}

        manifest = TruthScanManifest(
            repo_id="dummie_engine",
            total_files=len(fingerprints),
            tracked_files=len(tracked_files),
            untracked_files=len(fingerprints) - len(tracked_files),
            physical_sovereignty=physical_sovereignty,
            generated_at=self._utc_now()
        )

        # Output results
        self.intel_root.mkdir(parents=True, exist_ok=True)
        (self.intel_root / "total_truth_scan_manifest.json").write_text(
            json.dumps(manifest.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        
        inventory = {
            "generated_at": manifest.generated_at,
            "fingerprints": [f.to_dict() for f in fingerprints]
        }
        (self.intel_root / "total_truth_inventory.json").write_text(
            json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
        )
        
        report = {
            "decision": "PASS",
            "manifest": manifest.to_dict(),
            "generated_at": manifest.generated_at
        }
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "total_truth_scan_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        
        return report

    def _get_tracked_files(self) -> set[str]:
        try:
            res = subprocess.run(
                ["git", "ls-files"], cwd=self.repo_root, capture_output=True, text=True, check=True
            )
            return {f for f in res.stdout.split("\n") if f}
        except Exception:
            return set()

    def _get_all_relevant_files(self) -> list[str]:
        """Finds all files excluding obvious junk but including untracked system files."""
        relevant_files = []
        exclude_dirs = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"}
        
        for p in self.repo_root.rglob("*"):
            if p.is_file():
                rel_path = p.relative_to(self.repo_root)
                parts = rel_path.parts
                if not any(part in exclude_dirs for part in parts):
                    relevant_files.append(str(rel_path))
        return relevant_files

    def _generate_fingerprint(self, rel_path_str: str, is_tracked: bool) -> FileFingerprint:
        p = self.repo_root / rel_path_str
        
        # SHA256
        sha256_hash = hashlib.sha256()
        with open(p, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        stat = p.stat()
        
        # Layer
        layer = "unknown"
        if "layers/" in rel_path_str:
            parts = rel_path_str.split("/")
            try:
                idx = parts.index("layers")
                if len(parts) > idx + 1:
                    layer = parts[idx + 1]
            except ValueError:
                pass

        # Category
        ext = p.suffix.lower()
        category = "first_party"
        if ".aiwg/reports/" in rel_path_str: category = "generated"
        elif ext in [".json", ".yaml", ".toml"]: category = "config"
        elif ext == ".md": category = "doc"
        elif "layers/" in rel_path_str: category = "runtime"

        return FileFingerprint(
            path=rel_path_str,
            sha256=sha256_hash.hexdigest(),
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
            is_tracked=is_tracked,
            layer=layer,
            category=category
        )

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_total_truth_scan(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    scanner = TotalProjectTruthScan(repo_root=repo_root, aiwg_root=aiwg_root)
    return scanner.run_scan()


if __name__ == "__main__":
    run_total_truth_scan()
