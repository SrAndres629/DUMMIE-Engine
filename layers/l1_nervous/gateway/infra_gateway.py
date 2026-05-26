import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[1] / "configs" / "gateway_infra.json"


class InfraGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))


async def main():
    gw = InfraGateway()
    await gw.start()
    print(f"[infra] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()


if __name__ == "__main__":
    asyncio.run(main())
