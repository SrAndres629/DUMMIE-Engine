from ..context_engine import ContextDimension


class RelationalDimension(ContextDimension):
    name = "relational"

    async def collect(self) -> dict:
        return {
            "ontology_classes": [
                "semantic",
                "reasoning",
                "code",
                "search",
                "memory",
                "routing",
            ]
        }
