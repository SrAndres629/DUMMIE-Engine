from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Protocol
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("dummie-mcp.routing.delegation")

EXECUTION_LOCATIONS = ["local", "cloud", "hybrid"]
CLOUD_ONLY_SERVERS = {"muapi", "vercel", "cloudflare"}
LOCAL_ONLY_SERVERS = {
    "mcp-comfyui",
    "docker",
    "sqlite",
    "sequentialthinking",
    "shell",
    "mcp-bash",
    "browser-use",
    "github",
    "git",
    "filesystem",
}


class ExecutionLocation(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


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

    @property
    def has_cloud_servers(self) -> bool:
        return any(s in CLOUD_ONLY_SERVERS for s in self.servers)

    @property
    def has_local_servers(self) -> bool:
        return any(s in LOCAL_ONLY_SERVERS for s in self.servers)

    @classmethod
    def from_route(cls, route: dict, vram_free_mb: float = 0) -> "DelegationRequest":
        return cls(
            query=route.get("query", ""),
            domain=route.get("domain", ""),
            action=route.get("action", ""),
            gateway=route.get("gateway", ""),
            servers=route.get("servers", []),
            vram_free_mb=vram_free_mb,
        )


@dataclass
class DelegationDecision:
    location: ExecutionLocation
    server: str
    reason: str
    confidence: float = 1.0
    estimated_cost: dict = field(default_factory=dict)


class DelegationStrategy(ABC):
    name: str = "base"

    @abstractmethod
    async def evaluate(
        self, request: DelegationRequest
    ) -> Optional[DelegationDecision]: ...


class LocalPreferenceStrategy(DelegationStrategy):
    name = "local_preference"

    async def evaluate(
        self, request: DelegationRequest
    ) -> Optional[DelegationDecision]:
        if request.has_local_servers:
            local_server = next(
                (s for s in request.servers if s in LOCAL_ONLY_SERVERS), None
            )
            if local_server:
                return DelegationDecision(
                    location=ExecutionLocation.LOCAL,
                    server=local_server,
                    reason=f"Local server '{local_server}' available and preferred",
                )
        if request.has_cloud_servers:
            cloud_server = next(
                (s for s in request.servers if s in CLOUD_ONLY_SERVERS), None
            )
            if cloud_server:
                return DelegationDecision(
                    location=ExecutionLocation.CLOUD,
                    server=cloud_server,
                    reason=f"No local server available; delegating to cloud server '{cloud_server}'",
                    confidence=0.8,
                )
        return None


class CloudPreferenceStrategy(DelegationStrategy):
    name = "cloud_preference"

    async def evaluate(
        self, request: DelegationRequest
    ) -> Optional[DelegationDecision]:
        if not request.has_cloud_servers:
            return None
        cloud_server = next(
            (s for s in request.servers if s in CLOUD_ONLY_SERVERS), None
        )
        if cloud_server:
            return DelegationDecision(
                location=ExecutionLocation.CLOUD,
                server=cloud_server,
                reason=f"Cloud server '{cloud_server}' preferred for speed",
                estimated_cost={"api_cost": "variable", "latency_ms": 200},
            )
        local_server = next(
            (s for s in request.servers if s in LOCAL_ONLY_SERVERS), None
        )
        if local_server:
            return DelegationDecision(
                location=ExecutionLocation.LOCAL,
                server=local_server,
                reason=f"No cloud server available; falling back to local server '{local_server}'",
                confidence=0.7,
            )
        return None


class VRAMAwareStrategy(DelegationStrategy):
    name = "vram_aware"
    VRAM_THRESHOLD_MB = 2048

    async def evaluate(
        self, request: DelegationRequest
    ) -> Optional[DelegationDecision]:
        if request.vram_free_mb < self.VRAM_THRESHOLD_MB and request.has_cloud_servers:
            cloud_server = next(
                (s for s in request.servers if s in CLOUD_ONLY_SERVERS), None
            )
            if cloud_server:
                return DelegationDecision(
                    location=ExecutionLocation.CLOUD,
                    server=cloud_server,
                    reason=f"VRAM low ({request.vram_free_mb:.0f}MB < {self.VRAM_THRESHOLD_MB}MB); routing to cloud",
                    confidence=0.9,
                )
        if request.vram_free_mb >= self.VRAM_THRESHOLD_MB and request.has_local_servers:
            local_server = next(
                (s for s in request.servers if s in LOCAL_ONLY_SERVERS), None
            )
            if local_server:
                return DelegationDecision(
                    location=ExecutionLocation.LOCAL,
                    server=local_server,
                    reason=f"VRAM sufficient ({request.vram_free_mb:.0f}MB); keeping local",
                    confidence=0.85,
                )
        return None


class DelegationEngine:
    def __init__(self, strategies: Optional[list[DelegationStrategy]] = None):
        self.strategies = strategies or [
            VRAMAwareStrategy(),
            LocalPreferenceStrategy(),
        ]

    async def decide(self, request: DelegationRequest) -> DelegationDecision:
        for strategy in self.strategies:
            try:
                decision = await strategy.evaluate(request)
                if decision is not None:
                    logger.debug(
                        "Strategy '%s' -> location=%s server=%s conf=%.2f",
                        strategy.name,
                        decision.location.value,
                        decision.server,
                        decision.confidence,
                    )
                    return decision
            except Exception as e:
                logger.warning("Delegation strategy '%s' failed: %s", strategy.name, e)
                continue
        fallback_server = request.servers[0] if request.servers else "unknown"
        return DelegationDecision(
            location=ExecutionLocation.LOCAL,
            server=fallback_server,
            reason="No strategy could decide; defaulting to local",
            confidence=0.5,
        )

    def add_strategy(self, strategy: DelegationStrategy) -> None:
        self.strategies.append(strategy)
