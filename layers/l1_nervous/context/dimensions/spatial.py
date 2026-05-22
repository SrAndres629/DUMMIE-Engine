import os
from ..context_engine import ContextDimension


class SpatialDimension(ContextDimension):
    name = "spatial"

    async def collect(self) -> dict:
        return {
            "cwd": os.getcwd(),
            "project": self._detect_project(),
        }

    def _detect_project(self) -> str:
        cwd = os.getcwd()
        if "DUMMIE" in cwd:
            return "dummie-engine"
        if "open-generative-ai" in cwd:
            return "open-generative-ai"
        return os.path.basename(cwd)
