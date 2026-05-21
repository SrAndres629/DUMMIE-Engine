from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class FileDossier:
    file_path: str
    layer: str
    language: str
    artifact_type: str
    size_bytes: int = 0
    context_strategy: str = "metadata_only"
    tier: str = "metadata_only"
    risk_flags: list[str] = field(default_factory=list)
    ast_summary: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FileDossierGenerator:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root)
        self.aiwg_root = self.repo_root / aiwg_root
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"
        self.max_standard = 100
        self.max_deep = 40

    def generate_file_dossiers(self) -> dict[str, Any]:
        inventory_path = self.intel_root / "repo_inventory.json"
        if not inventory_path.exists():
            return {"decision": "FAIL", "error": "repo_inventory.json not found"}

        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        files = inventory.get("files", [])
        
        deep_candidates = [f for f in files if f.get("is_runtime") and f.get("language") == "python"]
        standard_candidates = [f for f in files if f.get("is_spec") or f.get("is_test") or f.get("is_schema")]
        
        dossiers = []
        deep_count = 0
        standard_count = 0
        
        for file in files:
            tier = "metadata_only"
            context_strategy = "load_metadata_only"
            
            if file in deep_candidates and deep_count < self.max_deep:
                tier = "deep"
                context_strategy = "load_deep_dossier"
                deep_count += 1
            elif file in standard_candidates and standard_count < self.max_standard:
                tier = "standard"
                context_strategy = "load_standard_dossier"
                standard_count += 1

            p = self.repo_root / file["path"]
            size = p.stat().st_size if p.exists() else 0

            dossier = FileDossier(
                file_path=file["path"],
                layer=file.get("layer", "unknown"),
                language=file.get("language", "unknown"),
                artifact_type=file.get("artifact_type", "unknown"),
                size_bytes=size,
                context_strategy=context_strategy,
                tier=tier,
                generated_at=self._utc_now()
            )
            
            if tier == "deep" and file.get("language") == "python" and p.exists():
                try:
                    content = p.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    dossier.ast_summary = {
                        "classes": classes,
                        "functions": functions
                    }
                except Exception:
                    dossier.risk_flags.append("ast_parse_error")

            dossiers.append(dossier)
            
            if tier in ["standard", "deep"]:
                safe_id = file["path"].replace("/", "_").replace(".", "_")
                file_out = self.intel_root / "files"
                file_out.mkdir(parents=True, exist_ok=True)
                (file_out / f"{safe_id}.json").write_text(json.dumps(dossier.to_dict(), indent=2) + "\n", encoding="utf-8")

        # Write index
        index = {
            "decision": "PASS",
            "deep_dossier_count": deep_count,
            "standard_dossier_count": standard_count,
            "generated_at": self._utc_now()
            # Omit full list to save space, only return counts in index for now.
        }
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "file_dossier_index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        
        return index

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_file_dossiers(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    gen = FileDossierGenerator(repo_root=repo_root, aiwg_root=aiwg_root)
    res = gen.generate_file_dossiers()
    class Wrapper:
        def __init__(self, d):
            self.__dict__.update(d)
        def to_dict(self):
            return self.__dict__
    return Wrapper(res)
