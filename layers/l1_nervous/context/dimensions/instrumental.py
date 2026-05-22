from ..context_engine import ContextDimension


class InstrumentalDimension(ContextDimension):
    name = "instrumental"

    def __init__(self, meta_router=None):
        self._meta_router = meta_router

    async def collect(self) -> dict:
        gateways = {}
        if self._meta_router:
            for gw_name, gw_cfg in self._meta_router.assignments.get(
                "gateways", {}
            ).items():
                gateways[gw_name] = {
                    "port": gw_cfg.get("port"),
                    "servers": list(gw_cfg.get("servers", {}).keys()),
                }
        return {"gateways": gateways}
