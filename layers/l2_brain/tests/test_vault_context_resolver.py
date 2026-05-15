import pytest
import json
from pathlib import Path
from layers.l2_brain.vault_context_resolver import VaultContextResolver

def test_vcr_resolve_refs(tmp_path):
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    entry_data = {"vault_id": "v1", "summary": "test note", "content_hash": "h1"}
    (vault_path / "v1.json").write_text(json.dumps(entry_data))

    resolver = VaultContextResolver(vault_path=vault_path)
    resolved = resolver.resolve_refs(["v1", "v2"])

    assert len(resolved) == 1
    assert resolved[0]["vault_id"] == "v1"

def test_vcr_build_snippets(tmp_path):
    resolver = VaultContextResolver(vault_path=tmp_path)
    resolved = [
        {
            "vault_id": "v1",
            "summary": "Sum1",
            "evidence_refs": ["e1"],
            "reuse_conditions": ["c1"],
            "risk_notes": ["r1"]
        }
    ]

    snippets = resolver.build_snippets(resolved)
    assert len(snippets) == 1
    assert "Vault ID: v1" in snippets[0]["snippet"]
    assert "Summary: Sum1" in snippets[0]["snippet"]
    assert "Evidence: e1" in snippets[0]["snippet"]

def test_vcr_rejects_secrets(tmp_path):
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    entry_data = {"vault_id": "v1", "summary": "secret=123", "content_hash": "h1"}
    (vault_path / "v1.json").write_text(json.dumps(entry_data))

    resolver = VaultContextResolver(vault_path=vault_path)
    # resolve_refs logs a warning and skips on error
    resolved = resolver.resolve_refs(["v1"])
    assert len(resolved) == 0
