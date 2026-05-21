#!/usr/bin/env python3
"""
Dummie Engine daemon that manages neuron sessions.

Features:
- Register neurons with name, hash, role.
- Update neuron metadata in real time.
- Broadcast current neuron map to all connected clients.
- Detect unexpected disconnects and emit an ALARM.
- Simple MCP consensus loop skeleton.
"""

import asyncio
import hashlib
import json
import os
import signal
from typing import Dict, Any

SOCKET_PATH = "/tmp/dummie_daemon.sock"


class Daemon:
    """Manages neuron sessions and client connections."""

    def __init__(self):
        self.neurons: Dict[str, Dict[str, Any]] = {}
        # Map each connected client (reader) to its registered neuron name
        self._readers: Dict[asyncio.StreamReader, str] = {}
        self._writers: Dict[asyncio.StreamReader, asyncio.StreamWriter] = {}
        self.running = False
        self._shutdown = asyncio.Event()

        # Graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    async def start(self):
        """Start the Unix socket server."""
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

        server = await asyncio.start_server(self._handle_client, path=SOCKET_PATH)
        self.running = True
        print(f"[Daemon] Listening on {SOCKET_PATH}")
        # Run the server and shutdown monitor concurrently
        await asyncio.gather(self._serve(), self._wait_for_shutdown())

    async def _serve(self):
        """Accept incoming connections."""
        async for reader, writer in self.server:  # type: ignore
            self._readers[reader] = None  # no neuron assigned yet
            self._writers[reader] = writer
            try:
                # Wait for first message (registration)
                raw = await reader.read(4096)
                if raw:
                    msg = json.loads(raw)
                    neuron = msg["neuron"]
                    action = msg["action"]
                    if action == "register":
                        name = msg["meta"]["name"]
                        role = msg["meta"]["role"]
                        h = hashlib.sha256(name.encode()).hexdigest()[:8]
                        self.neurons[neuron] = {"name": name, "hash": h, "role": role}
                        self._readers[reader] = neuron
                        print(f"[Daemon] Registered neuron {neuron} as {name}")
                    elif action == "update":
                        if neuron in self.neurons:
                            self.neurons[neuron].update(msg.get("data", {}))
                    elif action == "remove":
                        self.neurons.pop(neuron, None)
                        self._readers.pop(reader, None)
            except Exception as e:
                print("[Daemon] Connection error:", e)
            finally:
                # Ensure resources are cleaned up
                self._cleanup_reader(reader)

    async def _wait_for_shutdown(self):
        """Wait for external shutdown signal."""
        await self._shutdown.wait()
        await self.stop()

    def _signal_handler(self, signum, frame):
        print("[Daemon] Shutdown signal received")
        self._shutdown.set()

    def _cleanup_reader(self, reader: asyncio.StreamReader):
        """Remove a reader from tracking and close its writer."""
        if reader in self._readers:
            neuron = self._readers.pop(reader)
            if neuron and neuron in self._writers:
                self.alarm_on_disconnect(neuron)
        if reader in self._writers:
            self._writers.pop(reader).close()

    def alarm_on_disconnect(self, neuron: str):
        """Notify when a neuron disconnects unexpectedly."""
        print(f"ALARM: Neuron {neuron} disconnected")

    async def broadcast_state(self):
        """Send the current neuron map to all connected clients."""
        if not self.running:
            return
        payload = json.dumps({"neurons": self.neurons}).encode()
        dead_writers = []
        for reader, writer in self._writers.items():
            try:
                writer.write(payload)
                await writer.drain()
            except Exception:
                dead_writers.append(reader)

        # Clean up any dead writers
        for r in dead_writers:
            self._cleanup_reader(r)

    async def stop(self):
        """Shut down the daemon."""
        self.running = False
        if hasattr(self, "server"):
            self.server.close()
            await self.server.wait_closed()
        # Close all writers
        for writer in self._writers.values():
            writer.close()
        print("[Daemon] Shut down")


if __name__ == "__main__":
    daemon = Daemon()
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(daemon.stop())
