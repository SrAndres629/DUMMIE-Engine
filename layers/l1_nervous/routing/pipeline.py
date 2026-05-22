import time, logging
from dataclasses import dataclass, field
from typing import Optional, Protocol

logger = logging.getLogger("dummie-mcp.routing.pipeline")

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

class RoutingPipeline:
    def __init__(self, strategies: list[RoutingStrategy], threshold: float = 0.5, fallback_result: RoutingResult = None):
        self.strategies = strategies
        self.threshold = threshold
        self.fallback_result = fallback_result or RoutingResult(match=False, confidence=0.0)

    async def route(self, query: str) -> RoutingResult:
        for strategy in self.strategies:
            t0 = time.time()
            try:
                result = await strategy.execute(query)
                result.latency_ms = (time.time() - t0) * 1000
                result.strategy = strategy.name
                logger.debug(f"Strategy '{strategy.name}' -> match={result.match} conf={result.confidence:.3f}")
                if result.match and result.confidence >= self.threshold:
                    return result
            except Exception as e:
                logger.warning(f"Strategy '{strategy.name}' failed: {e}")
                continue
        return self.fallback_result

    async def route_with_context(self, query: str, context: str = "") -> RoutingResult:
        result = await self.route(query)
        result.query = query
        return result

    @property
    def strategy_names(self) -> list[str]:
        return [s.name for s in self.strategies]
