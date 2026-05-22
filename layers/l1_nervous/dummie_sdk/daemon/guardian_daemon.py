import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from dummie_sdk.config import get_config
from dummie_sdk.validation import ArchitectureGuardian, Violation

logger = logging.getLogger("dummie-sdk.guardian-daemon")


class GuardianDaemon:
    SCAN_INTERVAL = 300

    def __init__(self, root: Optional[Path] = None, interval: int = SCAN_INTERVAL):
        self.root = Path(root or ArchitectureGuardian._find_root())
        self.interval = interval
        self.guardian = ArchitectureGuardian(root=self.root)
        self.runtime_dir = self.root / ".aiwg" / "runtime" / "guardian"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._last_violations: list[Violation] = []

    def _log_violations(self, violations: list[Violation]) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        log = self.runtime_dir / "violations.jsonl"
        for v in violations:
            entry = {
                "timestamp": ts,
                "file": v.file,
                "line": v.line,
                "severity": v.severity.value,
                "rule": v.rule,
                "message": v.message,
            }
            with open(log, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def _write_status(self, violations: list[Violation]) -> None:
        errors = [v for v in violations if v.severity.value == "error"]
        warnings = [v for v in violations if v.severity.value == "warning"]
        status = {
            "total_violations": len(violations),
            "errors": len(errors),
            "warnings": len(warnings),
            "last_scan": datetime.now(timezone.utc).isoformat(),
            "healthy": len(errors) == 0,
        }
        (self.runtime_dir / "status.json").write_text(json.dumps(status, indent=2))

    async def scan_loop(self) -> None:
        while self._running:
            violations = self.guardian.scan_all()
            self._last_violations = violations
            if violations:
                self._log_violations(violations)
                self._write_status(violations)
                error_count = len(
                    [v for v in violations if v.severity.value == "error"]
                )
                if error_count:
                    logger.warning("Guardian: %d error(s) found", error_count)
            else:
                self._write_status([])
                logger.debug("Guardian: clean scan")
            await asyncio.sleep(self.interval)

    async def start(self) -> None:
        self._running = True
        logger.info("Guardian daemon started (interval=%ds)", self.interval)
        await self.scan_loop()

    async def stop(self) -> None:
        self._running = False
        logger.info("Guardian daemon stopped")

    @property
    def healthy(self) -> bool:
        errors = [v for v in self._last_violations if v.severity.value == "error"]
        return len(errors) == 0

    @property
    def status(self) -> dict:
        return (
            json.loads((self.runtime_dir / "status.json").read_text())
            if (self.runtime_dir / "status.json").exists()
            else {"healthy": True, "total_violations": 0}
        )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    daemon = GuardianDaemon()
    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()


if __name__ == "__main__":
    asyncio.run(main())
