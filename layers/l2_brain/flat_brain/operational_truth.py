from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class TruthStatus(str, Enum):
    PASS = "PASS"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass
class TruthCheck:
    name: str
    layer: str
    status: TruthStatus
    evidence: list[str] = field(default_factory=list)
    command: str = ""
    error: str = ""
    next_repair: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "layer": self.layer,
            "status": self.status.value,
            "evidence": list(self.evidence),
            "command": self.command,
            "error": self.error,
            "next_repair": self.next_repair,
        }


@dataclass
class TruthReport:
    repo_root: str
    checks: list[TruthCheck]
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def summary(self) -> dict[str, int]:
        counts = {status.value: 0 for status in TruthStatus}
        for check in self.checks:
            counts[check.status.value] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "repo_root": self.repo_root,
            "summary": self.summary(),
            "checks": [check.to_dict() for check in self.checks],
        }
