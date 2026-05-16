from __future__ import annotations

import json
from pathlib import Path

import pytest
from token_ledger import TokenLedger


@pytest.fixture
def temp_ledger(tmp_path):
    ledger_path = tmp_path / "token_usage.jsonl"
    return ledger_path


def test_token_ledger_record(temp_ledger):
    ledger = TokenLedger(str(temp_ledger))
    
    ledger.record_usage(
        model_id="gpt-4",
        tier="high",
        prompt_tokens=100,
        completion_tokens=50,
        concept="test",
        session_id="s1"
    )
    
    assert temp_ledger.exists()
    lines = temp_ledger.read_text().splitlines()
    assert len(lines) == 1
    
    data = json.loads(lines[0])
    assert data["session_id"] == "s1"
    assert data["prompt_tokens"] == 100
    assert data["completion_tokens"] == 50
    assert data["total_tokens"] == 150


def test_token_ledger_daily_total(temp_ledger):
    ledger = TokenLedger(str(temp_ledger))
    
    ledger.record_usage("gpt-4", "high", 100, 50, "test", session_id="s1")
    ledger.record_usage("gpt-4", "high", 200, 100, "test", session_id="s1")
    
    total = ledger.get_daily_total("gpt-4")
    assert total == 450
