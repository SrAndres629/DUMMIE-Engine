import pytest
import os
import json
from unittest.mock import MagicMock
from daemon import DummieDaemon
from safe_fallbacks import FailClosedAuditor, FailClosedExecutor

@pytest.mark.asyncio
async def test_daemon_diagnostic_report_generation(tmp_path):
    ledger = tmp_path / "sessions.jsonl"
    ledger.touch()
    
    # Mock gateway
    mock_gateway = MagicMock()
    mock_event_bus = MagicMock()
    
    # Enable diagnostic mode via env
    os.environ["DUMMIE_DIAGNOSTIC_MODE"] = "1"
    os.environ["DUMMIE_ROOT"] = str(tmp_path)
    
    daemon = DummieDaemon(str(ledger), mock_gateway, mock_event_bus)
    
    report = await daemon.diagnostic_reporter.run_diagnostic()
    
    assert report["mode"] == "DIAGNOSTIC"
    assert "layers" in report
    assert report["environment"]["DUMMIE_ROOT"] == str(tmp_path)
    assert report["storage"]["exists"] is True
    
    # Check physical file
    report_file = tmp_path / "diagnostic_report.json"
    assert report_file.exists()
    
    content = json.loads(report_file.read_text())
    assert content["mode"] == "DIAGNOSTIC"

@pytest.mark.asyncio
async def test_daemon_diagnostic_detects_fallbacks(tmp_path):
    ledger = tmp_path / "sessions.jsonl"
    ledger.touch()
    
    os.environ["DUMMIE_DIAGNOSTIC_MODE"] = "1"
    daemon = DummieDaemon(str(ledger), MagicMock(), MagicMock())
    
    # Force fallbacks for testing the reporter
    daemon.s_shield = FailClosedAuditor("forced_error_for_test")
    daemon.muscle = FailClosedExecutor("forced_error_for_test")
    
    report = await daemon.diagnostic_reporter.run_diagnostic()
    
    assert "FALLBACK_ACTIVE" in report["layers"]["shield_S"]["status"]
    assert report["layers"]["shield_S"]["reason"] == "forced_error_for_test"
    assert "FALLBACK_ACTIVE" in report["layers"]["muscle"]["status"]
    assert report["layers"]["muscle"]["reason"] == "forced_error_for_test"
