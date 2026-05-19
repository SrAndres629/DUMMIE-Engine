#!/usr/bin/env python3
import os
import time
import json
import asyncio
import nats
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SpecChangeHandler(FileSystemEventHandler):
    def __init__(self, loop, nats_url):
        self.loop = loop
        self.nats_url = nats_url
        self.nc = None

    async def connect(self):
        self.nc = await nats.connect(self.nats_url)
        print(f"[HOT RELOAD] Conectado a NATS en {self.nats_url}")

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".rules.json"):
            print(f"[HOT RELOAD] Cambio detectado en: {event.src_path}")
            asyncio.run_coroutine_threadsafe(self.notify_brain(event.src_path), self.loop)

    async def notify_brain(self, file_path):
        if not self.nc:
            await self.connect()
        
        # Cargar la regla para enviarla o simplemente notificar la ruta
        message = {
            "type": "SPEC_RELOAD",
            "file": os.path.basename(file_path),
            "full_path": os.path.abspath(file_path),
            "timestamp": time.time()
        }
        await self.nc.publish("ao.v2.l2.brain.control.reload", json.dumps(message).encode())
        print(f"[HOT RELOAD] Notificación enviada al Brain para {message['file']}")

async def main():
    nats_url = os.getenv("NATS_URL", "nats://127.0.0.1:4222")
    loop = asyncio.get_running_loop()
    
    handler = SpecChangeHandler(loop, nats_url)
    await handler.connect()
    
    observer = Observer()
    # Vigilar la carpeta de specs y el directorio raíz por si acaso
    observer.schedule(handler, path=".aiwg/packs", recursive=True)
    observer.schedule(handler, path="doc/specs", recursive=True)
    
    print("=== DUMMIE HOT RELOAD WATCHER: Activo y vigilando specs... ===")
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    asyncio.run(main())
