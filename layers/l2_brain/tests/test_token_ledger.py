from __future__ import annotations

import json
from pathlib import Path
import pytest
from token_cost_ledger import TokenCostLedger


@pytest.fixture
def temp_ledger(tmp_path):
    return tmp_path


def test_token_ledger_record(temp_ledger):
    ledger = TokenCostLedger(temp_ledger)
    
    ledger.record_usage(
        model_id="gpt-4",
        tier="high",
        prompt_tokens=100,
        completion_tokens=50,
        concept="utility_repair",
        session_id="s1"
    )
    
    ledger_file = temp_ledger / "sessions" / "s1" / "token_cost_ledger.jsonl"
    assert ledger_file.exists()
    lines = ledger_file.read_text().splitlines()
    assert len(lines) == 1
    
    data = json.loads(lines[0])
    assert data["session_id"] == "s1"
    assert data["input_tokens"] == 100
    assert data["output_tokens"] == 50


def test_token_ledger_daily_total(temp_ledger):
    ledger = TokenCostLedger(temp_ledger)
    
    ledger.record_usage(
        model_id="gpt-4",
        tier="high",
        prompt_tokens=100,
        completion_tokens=50,
        concept="utility_repair",
        session_id="s1"
    )
    ledger.record_usage(
        model_id="gpt-4",
        tier="high",
        prompt_tokens=200,
        completion_tokens=100,
        concept="utility_repair",
        session_id="s1"
    )
    
    summary = ledger.summarize_session("s1")
    assert summary["total_raw_tokens_seen"] == 450
