from typing import Any, Dict
import logging

logger = logging.getLogger("dummie.brain.safe_fallbacks")


class FailClosedAuditor:
    """Security fallback. Never allows execution when shield import fails."""

    def __init__(self, reason: str):
        self.reason = reason

    async def audit(self, dag_xml: str, goal: str = "") -> tuple[bool, str]:
        logger.error("L3 shield unavailable. Failing closed: %s", self.reason)
        return False, f"FAIL_CLOSED_SHIELD_UNAVAILABLE: {self.reason}"


class FailClosedExecutor:
    """Execution fallback. Never simulates success."""

    def __init__(self, reason: str):
        self.reason = reason

    async def execute(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.error("L5 executor unavailable. Blocking execution: %s", self.reason)
        return {
            "error": "FAIL_CLOSED_EXECUTOR_UNAVAILABLE",
            "reason": self.reason,
            "server_name": server_name,
            "tool_name": tool_name,
        }
