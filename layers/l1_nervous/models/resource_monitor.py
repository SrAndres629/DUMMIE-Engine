import os, logging
from dataclasses import dataclass

logger = logging.getLogger("dummie-mcp.models.resource")


@dataclass
class ResourceSnapshot:
    ram_total_gb: float
    ram_used_gb: float
    ram_free_gb: float
    vram_total_gb: float = 0.0
    vram_used_gb: float = 0.0


class ResourceMonitor:
    def __init__(self):
        self._vram_enabled = self._check_nvidia()

    def _check_nvidia(self) -> bool:
        try:
            import subprocess

            r = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return r.returncode == 0
        except Exception:
            return False

    def snapshot(self) -> ResourceSnapshot:
        import psutil

        mem = psutil.virtual_memory()
        snap = ResourceSnapshot(
            ram_total_gb=round(mem.total / (1024**3), 1),
            ram_used_gb=round(mem.used / (1024**3), 1),
            ram_free_gb=round(mem.available / (1024**3), 1),
        )
        if self._vram_enabled:
            try:
                import subprocess

                r = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=memory.total,memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if r.returncode == 0:
                    parts = r.stdout.strip().split(",")
                    snap.vram_total_gb = round(int(parts[0].strip()) / 1024, 1)
                    snap.vram_used_gb = round(int(parts[1].strip()) / 1024, 1)
            except Exception:
                pass
        return snap

    def can_load(self, vram_mb: int, ram_mb: int) -> tuple[bool, str]:
        snap = self.snapshot()
        if ram_mb > 0 and snap.ram_free_gb * 1024 < ram_mb:
            return (
                False,
                f"RAM insufficient: need {ram_mb}MB, have {snap.ram_free_gb * 1024:.0f}MB free",
            )
        if vram_mb > 0 and self._vram_enabled:
            vram_free = (snap.vram_total_gb - snap.vram_used_gb) * 1024
            if vram_free < vram_mb:
                return (
                    False,
                    f"VRAM insufficient: need {vram_mb}MB, have {vram_free:.0f}MB free",
                )
        return True, "OK"

    def summary(self) -> dict:
        snap = self.snapshot()
        return {
            "ram": {
                "total_gb": snap.ram_total_gb,
                "used_gb": snap.ram_used_gb,
                "free_gb": snap.ram_free_gb,
            },
            "vram": {
                "total_gb": snap.vram_total_gb,
                "used_gb": snap.vram_used_gb,
                "available": self._vram_enabled,
            },
        }
