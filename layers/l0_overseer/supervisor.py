import asyncio
import os
import signal
import sys
import logging
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("L0-Supervisor")

class DummieSupervisor:
    """
    [L0_OVERSEER] Gestor Industrial de Procesos.
    Asegura que todos los componentes de la fábrica arranquen y mueran juntos.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.processes: Dict[str, asyncio.subprocess.Process] = {}
        self.running = False

    async def launch(self, name: str, cmd: str, args: List[str], env: Dict[str, str] = None):
        logger.info(f"Launching {name}: {cmd} {' '.join(args)}")
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        proc = await asyncio.create_subprocess_exec(
            cmd, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env
        )
        self.processes[name] = proc
        asyncio.create_task(self._log_stream(name, proc.stdout, logging.INFO))
        asyncio.create_task(self._log_stream(name, proc.stderr, logging.ERROR))
        
    async def _log_stream(self, name: str, stream: asyncio.StreamReader, level: int):
        while True:
            line = await stream.readline()
            if not line:
                break
            logger.log(level, f"[{name}] {line.decode().strip()}")

    async def run_forever(self):
        self.running = True
        logger.info("DUMMIE Factory Supervisor is ONLINE.")
        while self.running:
            for name, proc in list(self.processes.items()):
                if proc.returncode is not None:
                    logger.error(f"Process {name} died with code {proc.returncode}. Restarting...")
                    # logic for restart could go here
                    del self.processes[name]
            await asyncio.sleep(5)

    async def stop_all(self):
        self.running = False
        logger.info("Stopping all factory processes...")
        for name, proc in self.processes.items():
            logger.info(f"Terminating {name}...")
            try:
                proc.terminate()
                await proc.wait()
            except Exception as e:
                logger.warning(f"Error stopping {name}: {e}")
        self.processes.clear()

async def main():
    root = Path(os.environ.get("DUMMIE_ROOT", os.getcwd()))
    bin_dir = root / "bin"
    aiwg = root / ".aiwg"
    socket_path = aiwg / "sockets" / "flight.sock"
    dummied_socket = aiwg / "sockets" / "dummied.sock"
    kuzu_path = aiwg / "memory" / "loci.db"

    sv = DummieSupervisor(root)
    
    # Register shutdown signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(sv.stop_all()))

    # Launch sequence
    try:
        await sv.launch("L1-Sidecar", str(bin_dir / "l1_sidecar"), [])
        await sv.launch("Memory-Plane", str(bin_dir / "memory_plane"), [], {
            "DUMMIE_KUZU_DB_PATH": str(kuzu_path),
            "MEMORY_SOCKET_PATH": str(socket_path)
        })
        await sv.launch("Dummied", str(bin_dir / "dummied"), [], {
            "DUMMIE_ROOT_DIR": str(root),
            "DUMMIE_DUMMIED_SOCKET_PATH": str(dummied_socket)
        })
        await sv.launch("Monitor", str(bin_dir / "monitor"), [])
        
        # Elixir Supervisor (Still using mix for now)
        await sv.launch("Elixir-Overseer", "mix", ["run", "--no-halt"], {
            "DUMMIE_ROOT_DIR": str(root)
        })
        
        # NOTA ARQUITECTÓNICA: MCP-Gateway no se levanta aquí. 
        # Al usar transporte STDIO, debe ser instanciado bajo demanda por el cliente MCP 
        # a través del wrapper /usr/local/bin/dummie-mcp. (Spec 52)
        
        await sv.run_forever()
    except Exception as e:
        logger.critical(f"Supervisor failure: {e}")
    finally:
        await sv.stop_all()

if __name__ == "__main__":
    asyncio.run(main())
