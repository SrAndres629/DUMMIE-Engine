from ..context_engine import ContextDimension


class SemanticDimension(ContextDimension):
    name = "semantic"

    def __init__(self, registry=None):
        self._registry = registry

    async def collect(self) -> dict:
        return {"status": "semantic_dimension_ready"}
