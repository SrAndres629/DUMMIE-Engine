from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class FolderDossier:
    folder_path: str
    layer: str
    dominant_languages: list[str]
    file_count: int
    context_strategy: str
    risk_flags: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FolderDossierGenerator:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def generate_folder_dossiers(self) -> dict[str, Any]:
        inventory_path = self.intel_root / "repo_inventory.json"
        if not inventory_path.exists():
            return {"decision": "FAIL", "error": "repo_inventory.json not found"}

        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        files = inventory.get("files", [])
        
        # Group files by folder
        folders = {}
        for file in files:
            path = file["path"]
            # Get parent folder path
            parts = path.split("/")
            if len(parts) > 1:
                folder_path = "/".join(parts[:-1])
            else:
                folder_path = "."
                
            if folder_path not in folders:
                folders[folder_path] = []
            folders[folder_path].append(file)

        target_folders = [
            "layers/l2_brain", "layers/l1_nervous", "layers/l0_overseer",
            "layers/l3_shield", "layers/l4_edge", "layers/l5_muscle", "layers/l6_skin",
            "doc/specs", ".aiwg/evolution", ".aiwg/reports", ".aiwg/schemas", ".aiwg/notes",
            ".aiwg/repo_intelligence"
        ]

        dossiers = []
        for target in target_folders:
            # We summarize files that start with target path
            target_files = [f for f in files if f["path"].startswith(target)]
            if not target_files:
                continue
                
            languages = set(f["language"] for f in target_files if f["language"] != "unknown")
            layer = target_files[0].get("layer", "unknown")
            
            dossier = FolderDossier(
                folder_path=target,
                layer=layer,
                dominant_languages=sorted(list(languages)),
                file_count=len(target_files),
                context_strategy="load_folder_dossier",
                generated_at=self._utc_now()
            )
            dossiers.append(dossier)
            
            # Write individual folder dossier
            safe_id = target.replace("/", "_").replace(".", "_")
            folder_out = self.intel_root / "folders" / safe_id
            folder_out.mkdir(parents=True, exist_ok=True)
            (folder_out / "folder_dossier.json").write_text(json.dumps(dossier.to_dict(), indent=2) + "\n", encoding="utf-8")

        # Write index
        index = {
            "decision": "PASS",
            "generated_at": self._utc_now(),
            "dossiers": [d.to_dict() for d in dossiers]
        }
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "folder_dossier_index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        
        return index

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_folder_dossiers(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    gen = FolderDossierGenerator(aiwg_root=aiwg_root)
    res = gen.generate_folder_dossiers()
    class Wrapper:
        def __init__(self, d):
            self.__dict__.update(d)
        def to_dict(self):
            return self.__dict__
    return Wrapper(res)
