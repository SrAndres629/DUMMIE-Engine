import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from entropy_governor import classify_memory_temperature
from models import MemoryTemperatureSignal, MemoryTemperature


def test_manual_pin_promotes_memory_to_hot():
    signal = MemoryTemperatureSignal(
        source_uri="obsidian://A.md",
        provider="obsidian",
        signal_type="manual_pin",
        weight=1.0,
        observed_at="2026-04-26T00:00:00Z",
    )

    result = classify_memory_temperature([signal])

    assert result.temperature == MemoryTemperature.HOT
    assert "manual_pin" in result.rationale


def test_conflict_quarantines_memory():
    signal = MemoryTemperatureSignal(
        source_uri="obsidian://A.md",
        provider="obsidian",
        signal_type="conflict",
        weight=-1.0,
        observed_at="2026-04-26T00:00:00Z",
    )

    result = classify_memory_temperature([signal])

    assert result.temperature == MemoryTemperature.QUARANTINED
