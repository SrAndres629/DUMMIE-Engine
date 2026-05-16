import json
from pathlib import Path

import pytest

from layers.l2_brain.restart_integration_gate import RestartIntegrationGate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _prepare_critical_state(tmp_path: Path) -> Path:
    aiwg = tmp_path / ".aiwg"
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P13", "next_required_phase": "P14"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P14", "name": "PromptFrameBuilder + PromptCacheLedger"})
    (aiwg / "evolution" / "phases.yaml").parent.mkdir(parents=True, exist_ok=True)
    (aiwg / "evolution" / "phases.yaml").write_text("phases:\n  - id: P14\n  - id: P15\n", encoding="utf-8")
    _write_json(
        aiwg / "evolution" / "phase_dependencies.graph.json",
        {
            "edges": [
                {"from": "P14", "to": "P15"},
                {"from": "P15", "to": "P16"},
                {"from": "P16", "to": "P17"},
                {"from": "P17", "to": "P18"},
            ]
        },
    )
    return aiwg


def test_restart_integration_gate_pass_or_warn(tmp_path: Path):
    aiwg = _prepare_critical_state(tmp_path)
    gate = RestartIntegrationGate(aiwg_root=aiwg)
    result = gate.run_restart_gate(write_report=True)

    assert result.decision in {"PASS", "PASS_WITH_WARNINGS"}
    assert (aiwg / "reports" / "restart_integration_gate_latest.json").exists()


def test_restart_integration_gate_fails_with_invalid_current_position(tmp_path: Path):
    aiwg = _prepare_critical_state(tmp_path)
    (aiwg / "evolution" / "current_position.json").write_text("{invalid", encoding="utf-8")

    gate = RestartIntegrationGate(aiwg_root=aiwg)
    result = gate.run_restart_gate(write_report=False)

    assert result.decision == "FAIL"
    assert any("invalid_critical_json" in x for x in result.failures)


def test_restart_integration_gate_detects_missing_module_via_monkeypatch(tmp_path: Path, monkeypatch):
    aiwg = _prepare_critical_state(tmp_path)
    gate = RestartIntegrationGate(aiwg_root=aiwg)

    import importlib

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name == "layers.l2_brain.context_quant_runtime":
            raise ImportError("simulated missing")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    result = gate.run_restart_gate(write_report=False)

    assert result.decision == "FAIL"
    assert any("critical_module_import_failed:layers.l2_brain.context_quant_runtime" == x for x in result.failures)
