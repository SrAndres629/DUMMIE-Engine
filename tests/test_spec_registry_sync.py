from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_spec_registry_sync_generates_canonical_registry() -> None:
    res = subprocess.run(
        [sys.executable, "scripts/spec_registry_sync.py", "--root", str(ROOT)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert res.returncode == 0
    registry = ROOT / ".aiwg" / "spec_registry" / "spec_bindings.yaml"
    report = ROOT / ".aiwg" / "reports" / "spec_registry_sync_latest.json"
    assert registry.exists()
    assert report.exists()
    text = registry.read_text(encoding="utf-8")
    assert "schema_version: dummie.spec_binding_registry.v1" in text
    assert "spec_id: DE-V2-L2-201" in text
    assert "spec_id: DE-V2-L2-202" in text
