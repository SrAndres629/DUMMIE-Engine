from dataclasses import dataclass

from models import MemoryTemperature, MemoryTemperatureSignal


@dataclass
class MemoryTemperatureDecision:
    temperature: MemoryTemperature
    score: float
    rationale: str


def classify_memory_temperature(signals: list[MemoryTemperatureSignal]) -> MemoryTemperatureDecision:
    if not signals:
        return MemoryTemperatureDecision(MemoryTemperature.WARM, 0.0, "no_signals")

    signal_types = [signal.signal_type for signal in signals]
    if "conflict" in signal_types:
        return MemoryTemperatureDecision(MemoryTemperature.QUARANTINED, -1.0, "conflict")

    score = sum(signal.weight for signal in signals)
    if "manual_pin" in signal_types or score >= 0.75:
        return MemoryTemperatureDecision(MemoryTemperature.HOT, score, ",".join(signal_types))
    if "superseded" in signal_types or score < -0.25:
        return MemoryTemperatureDecision(MemoryTemperature.COLD, score, ",".join(signal_types))
    return MemoryTemperatureDecision(MemoryTemperature.WARM, score, ",".join(signal_types))
