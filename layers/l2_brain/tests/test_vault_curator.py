import json
import pytest
from pathlib import Path
from layers.l2_brain.vault_curator import VaultCurator

def test_vault_curator_extract_and_store(tmp_path):
    workbench_path = tmp_path / "wb"
    workbench_path.mkdir()
    (workbench_path / "final_summary.md").write_text("# Golden path found")
    (workbench_path / "validation_report.md").write_text("# Error detected")
    (workbench_path / "decision_log.jsonl").write_text('{"decision": "A"}\n')

    vault_path = tmp_path / "vault"
    curator = VaultCurator(root=vault_path)

    entries = curator.extract_vault_entries("m1", workbench_path)
    assert len(entries) == 3

    for entry in entries:
        curator.store_vault_entry(entry)

    index = curator.build_vault_index()
    assert index["total_entries"] == 3
    assert "golden_path" in index["by_type"]

def test_vault_curator_rejects_private(tmp_path):
    curator = VaultCurator(root=tmp_path)

    with pytest.raises(ValueError, match="private reasoning"):
        curator.store_vault_entry({"summary": "chain_of_thought content", "entry_type": "decision"})

    with pytest.raises(ValueError, match="forbidden secret"):
        curator.store_vault_entry({"summary": "secret is 123", "entry_type": "decision"})

def test_vault_curator_deterministic_id_and_deduplication(tmp_path):
    curator = VaultCurator(root=tmp_path)
    entry = {
        "mission_id": "m1",
        "entry_type": "decision",
        "summary": "Use fcntl for locking",
        "evidence_refs": ["file1.py"]
    }

    e1 = curator.store_vault_entry(entry)
    e2 = curator.store_vault_entry(entry) # Duplicate

    assert e1["vault_id"] == e2["vault_id"]
    assert e1["content_hash"] == e2["content_hash"]

    files = list(tmp_path.glob("vlt-*.json"))
    assert len(files) == 1 # Only one file stored due to deduplication

def test_vault_curator_index_by_hash(tmp_path):
    curator = VaultCurator(root=tmp_path)
    entry = {
        "mission_id": "m1",
        "entry_type": "golden_path",
        "summary": "Success",
        "evidence_refs": ["ref1"]
    }
    e = curator.store_vault_entry(entry)

    index = curator.build_vault_index()
    assert e["content_hash"] in index["by_hash"]
    assert index["by_hash"][e["content_hash"]] == e["vault_id"]

