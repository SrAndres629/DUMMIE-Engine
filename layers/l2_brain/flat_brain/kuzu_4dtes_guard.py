from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Kuzu4dTesGuardResult:
    decision: str
    policy: str
    db_path: str
    warnings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def run_kuzu_4dtes_guard(root: str | Path = ".") -> Kuzu4dTesGuardResult:
    root_path = Path(root)
    db_path = root_path / ".aiwg" / "memory" / "loci.db"

    warnings: list[str] = []
    if db_path.exists():
        warnings.append("Sovereign memory DB exists and is treated as runtime-local artifact.")

    policy_file = root_path / ".aiwg" / "reports" / "c0_sovereign_memory_policy.json"
    if not policy_file.exists():
        payload = {
            "decision": "PASS",
            "memory_db_path": str(db_path),
            "policy": "runtime_local_do_not_commit",
            "commit_block": [".aiwg/memory/*.db"],
        }
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        policy_file.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    return Kuzu4dTesGuardResult(
        decision="PASS",
        policy="runtime_local_do_not_commit",
        db_path=str(db_path),
        warnings=warnings,
    )
