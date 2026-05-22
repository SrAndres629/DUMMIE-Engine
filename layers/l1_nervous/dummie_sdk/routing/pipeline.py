import time, logging
from typing import Optional
from dummie_sdk.routing.types import RoutingResult, RoutingStrategy

logger = logging.getLogger("dummie-sdk.routing.pipeline")


class RoutingPipeline:
    def __init__(
        self,
        strategies: list[RoutingStrategy],
        threshold: float = 0.5,
        fallback_result: Optional[RoutingResult] = None,
    ):
        self.strategies = strategies
        self.threshold = threshold
        self.fallback_result = fallback_result or RoutingResult(
            match=False, confidence=0.0
        )

    async def route(self, query: str) -> RoutingResult:
        for strategy in self.strategies:
            t0 = time.time()
            try:
                result = await strategy.execute(query)
                result.latency_ms = (time.time() - t0) * 1000
                result.strategy = strategy.name
                logger.debug(
                    "Strategy '%s' -> match=%s conf=%.3f",
                    strategy.name,
                    result.match,
                    result.confidence,
                )
                if result.match and result.confidence >= self.threshold:
                    return result
            except Exception as e:
                logger.warning("Strategy '%s' failed: %s", strategy.name, e)
                continue
        return self.fallback_result

    async def route_with_context(self, query: str, context: str = "") -> RoutingResult:
        result = await self.route(query)
        result.query = query
        return result

    @property
    def strategy_names(self) -> list[str]:
        return [s.name for s in self.strategies]
