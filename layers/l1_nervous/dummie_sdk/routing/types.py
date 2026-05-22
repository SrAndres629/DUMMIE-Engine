from dataclasses import dataclass, field
from typing import Optional, Protocol


@dataclass
class RoutingResult:
    match: bool = False
    gateway: str = ""
    server: str = ""
    tool: str = ""
    domain: str = ""
    action: str = ""
    confidence: float = 0.0
    strategy: str = ""
    query: str = ""
    latency_ms: float = 0.0


class RoutingStrategy(Protocol):
    name: str
    async def execute(self, query: str) -> RoutingResult: ...


@dataclass
class DelegationRequest:
    query: str = ""
    domain: str = ""
    action: str = ""
    gateway: str = ""
    servers: list[str] = field(default_factory=list)
    vram_free_mb: float = 0.0
    requires_cloud_api: bool = False
    priority: str = "normal"
