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

def test_vault_curator_list_entries(tmp_path):
    curator = VaultCurator(root=tmp_path)
    curator.store_vault_entry({"entry_type": "golden_path", "summary": "S1"})
    curator.store_vault_entry({"entry_type": "decision", "summary": "D1"})

    all_e = curator.list_entries()
    assert len(all_e) == 2

    goldens = curator.list_entries(entry_type="golden_path")
    assert len(goldens) == 1
    assert goldens[0]["summary"] == "S1"
