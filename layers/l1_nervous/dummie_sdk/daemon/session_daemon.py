import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("dummie.session-daemon")


class SessionDaemon:
    CHECK_INTERVAL = 30
    HEARTBEAT_TIMEOUT = 120
    OPENCODE_URL = "http://localhost:18789"

    def __init__(self, root: Optional[Path] = None, interval: int = CHECK_INTERVAL):
        self.root = Path(root or os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
        self.interval = interval
        self._running = False
        self._last_heartbeat = datetime.now(timezone.utc)
        self._restart_count = 0
        self._mode = "plan"

        self.session_dir = self.root / ".aiwg" / "runtime" / "session"
        self.models_dir = self.root / ".aiwg" / "runtime" / "models"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _write_event(self, event: str, detail: dict = None):
        entry = {"timestamp": self._now(), "event": event, **(detail or {})}
        log = self.session_dir / "events.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _write_status(self):
        uptime = (datetime.now(timezone.utc) - self._last_heartbeat).total_seconds()
        self._mode = "builder" if uptime < self.HEARTBEAT_TIMEOUT else "plan"
        status = {
            "timestamp": self._now(),
            "opencode": self._check_opencode(),
            "mode": self._mode,
            "restart_count": self._restart_count,
            "models_ready": self._check_models(),
        }
        (self.session_dir / "status.json").write_text(json.dumps(status, indent=2))

    def _check_opencode(self) -> str:
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    self.OPENCODE_URL,
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return (
                "ready"
                if result.stdout.strip() == "200"
                else f"unhealthy({result.stdout.strip()})"
            )
        except Exception:
            return "down"

    def _check_models(self) -> list[str]:
        if not self.models_dir.exists():
            return []
        return sorted(p.stem for p in self.models_dir.glob("*.ready") if p.is_file())

    def _restart_opencode(self):
        self._restart_count += 1
        logger.warning("OpenCode down — restarting (attempt %d)", self._restart_count)
        self._write_event("opencode_restart", {"attempt": self._restart_count})
        try:
            subprocess.run(
                ["sudo", "/usr/bin/systemctl", "restart", "dummie-opencode.service"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            logger.info("OpenCode restart triggered")
        except Exception as e:
            logger.exception("OpenCode restart failed: %s", e)
            self._write_event("opencode_restart_failed", {"error": str(e)})

    def _detect_new_models(self) -> list[str]:
        if not self.models_dir.exists():
            return []
        ready_now = set(self._check_models())
        previous = set(getattr(self, "_previous_models", []))
        self._previous_models = sorted(ready_now)
        new = ready_now - previous
        return sorted(new)

    async def session_loop(self):
        while self._running:
            try:
                status = self._check_opencode()
                if status != "ready":
                    self._restart_opencode()
                    await asyncio.sleep(10)
                    continue

                new_models = self._detect_new_models()
                if new_models:
                    logger.info("New models detected: %s", new_models)
                    self._write_event("models_detected", {"models": new_models})

                self._write_status()
                await asyncio.sleep(self.interval)

            except Exception as e:
                logger.exception("Session daemon loop error: %s", e)
                self._write_event("loop_error", {"error": str(e)})
                await asyncio.sleep(self.interval)

    async def start(self):
        self._running = True
        logger.info("Session daemon started (interval=%ds)", self.interval)
        self._write_event("daemon_started", {"interval": self.interval})
        await self.session_loop()

    async def stop(self):
        self._running = False
        logger.info("Session daemon stopped")
        self._write_event("daemon_stopped")

    @property
    def healthy(self) -> bool:
        return self._check_opencode() == "ready"

    @property
    def status(self) -> dict:
        status_file = self.session_dir / "status.json"
        if status_file.exists():
            return json.loads(status_file.read_text())
        return {"opencode": "unknown", "mode": "plan"}


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    daemon = SessionDaemon()
    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()


if __name__ == "__main__":
    asyncio.run(main())
