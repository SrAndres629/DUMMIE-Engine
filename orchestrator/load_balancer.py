"""Load balancer — distributes load across models based on health and usage.

Source of Truth: Per-model stats tracked in memory
Traced: Stats exposed via orchestrator API
"""

import time
import logging
from typing import Dict, Any, Optional, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class LoadBalancer:
    """Distributes model requests based on health, load, and recency."""

    def __init__(self, max_error_rate: float = 0.1):
        self.max_error_rate = max_error_rate
        self.model_stats: Dict[str, dict] = defaultdict(
            lambda: {
                "requests": 0,
                "tokens": 0,
                "errors": 0,
                "last_used": None,
                "avg_latency": 0.0,
                "current_load": 0,
            }
        )

    def select_model(
        self, candidates: List[str], max_tokens: int = 4096
    ) -> Optional[str]:
        if not candidates:
            return None

        # Filter out unhealthy models (>10% error rate)
        healthy = []
        for model in candidates:
            stats = self.model_stats[model]
            if stats["requests"] > 0:
                error_rate = stats["errors"] / stats["requests"]
                if error_rate < self.max_error_rate:
                    healthy.append(model)
                else:
                    logger.warning(
                        "Model %s unhealthy (error_rate=%.1f%%)",
                        model,
                        error_rate * 100,
                    )
            else:
                healthy.append(model)

        if not healthy:
            logger.error("No healthy models available, using first candidate")
            return candidates[0]

        # Select least recently used healthy model
        healthy.sort(key=lambda m: self.model_stats[m]["last_used"] or 0)
        return healthy[0]

    def record_request(
        self, model: str, tokens: int = 0, latency: float = 0.0, success: bool = True
    ):
        stats = self.model_stats[model]
        stats["requests"] += 1
        stats["tokens"] += tokens
        stats["last_used"] = time.time()
        stats["current_load"] += 1

        if not success:
            stats["errors"] += 1
            stats["current_load"] -= 1
            return

        total = stats["requests"]
        stats["avg_latency"] = (stats["avg_latency"] * (total - 1) + latency) / total
        stats["current_load"] -= 1

    def get_stats(self) -> Dict[str, Any]:
        result = {}
        for model, stats in self.model_stats.items():
            error_rate = (
                stats["errors"] / stats["requests"] if stats["requests"] > 0 else 0.0
            )
            result[model] = {
                **stats,
                "error_rate": error_rate,
                "healthy": error_rate < self.max_error_rate,
            }
        return result

    def get_healthiest_model(self) -> Optional[str]:
        stats = self.get_stats()
        healthy = [(m, s) for m, s in stats.items() if s["healthy"]]
        if not healthy:
            return None
        healthy.sort(key=lambda x: x[1]["error_rate"])
        return healthy[0][0]
