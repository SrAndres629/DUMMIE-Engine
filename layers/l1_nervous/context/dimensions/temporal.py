import time
from ..context_engine import ContextDimension


class TemporalDimension(ContextDimension):
    name = "temporal"

    def __init__(self, session_manager=None):
        from ..models.session_context import SessionManager

        self._sm = session_manager or SessionManager()

    async def collect(self) -> dict:
        return {
            "timestamp": time.strftime("%H:%M:%S"),
            "date": time.strftime("%Y-%m-%d"),
            "day_of_week": time.strftime("%A"),
            "session_duration_s": 0,
            "recent_queries_count": 0,
        }
