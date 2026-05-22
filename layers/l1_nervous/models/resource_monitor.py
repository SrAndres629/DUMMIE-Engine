import os, logging, subprocess, json
from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum

logger = logging.getLogger("dummie-mcp.models.resource")


class ModelPriority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ResourceSnapshot:
    ram_total_gb: float
    ram_used_gb: float
    ram_free_gb: float
    ram_zram_gb: float = 0.0
    ram_zram_effective_gb: float = 0.0
    vram_total_gb: float = 0.0
    vram_used_gb: float = 0.0
    vram_free_gb: float = 0.0
    unified_memory: bool = False
    swap_total_gb: float = 0.0
    swap_used_gb: float = 0.0


@dataclass
class ModelBudget:
    allocated_vram_mb: int = 0
    allocated_ram_mb: int = 0
    reserved_vram_mb: int = 512
    max_vram_mb: int = 0
    max_ram_mb: int = 0
    budget_exceeded: bool = False
    strategy: str = "vram_first"


class ResourceMonitor:
    INSTANCE: Optional["ResourceMonitor"] = None

    def __init__(self, vram_reserve_mb: int = 512, ram_reserve_gb: float = 2.0):
        self.vram_reserve_mb = vram_reserve_mb
        self.ram_reserve_gb = ram_reserve_gb
        self._vram_enabled = self._check_nvidia()
        self._unified_memory = self._check_unified_memory()
        ResourceMonitor.INSTANCE = self

    @classmethod
    def get_instance(cls, **kwargs) -> "ResourceMonitor":
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(**kwargs)
        return cls.INSTANCE

    def _check_nvidia(self) -> bool:
        try:
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

    def _check_unified_memory(self) -> bool:
        return os.environ.get("CUDA_MANAGED_FORCE_DEVICE_ALLOC") == "1"

    def _get_zram_info(self) -> tuple[float, float]:
        try:
            r = subprocess.run(
                ["zramctl", "--json"], capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0:
                data = json.loads(r.stdout)
                if data:
                    z = data[0] if isinstance(data, list) else data
                    total_mb = float(z.get("disksize", 0)) / (1024**3)
                    data_mb = float(z.get("data", 0)) / (1024**3)
                    comp_mb = float(z.get("comp", 0)) / (1024**3)
                    ratio = data_mb / comp_mb if comp_mb > 0 else 1.0
                    return total_mb, ratio
        except Exception:
            pass
        return 0.0, 1.0

    def snapshot(self) -> ResourceSnapshot:
        import psutil

        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        zram_gb, zram_ratio = self._get_zram_info()

        snap = ResourceSnapshot(
            ram_total_gb=round(mem.total / (1024**3), 1),
            ram_used_gb=round(mem.used / (1024**3), 1),
            ram_free_gb=round(mem.available / (1024**3), 1),
            ram_zram_gb=round(zram_gb, 1),
            ram_zram_effective_gb=round(zram_gb * zram_ratio, 1),
            swap_total_gb=round(swap.total / (1024**3), 1),
            swap_used_gb=round(swap.used / (1024**3), 1),
            unified_memory=self._unified_memory,
        )
        if self._vram_enabled:
            try:
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
                    total = int(parts[0].strip())
                    used = int(parts[1].strip())
                    snap.vram_total_gb = round(total / 1024, 1)
                    snap.vram_used_gb = round(used / 1024, 1)
                    snap.vram_free_gb = round((total - used) / 1024, 1)
            except Exception:
                pass
        return snap

    def get_budget(self) -> ModelBudget:
        snap = self.snapshot()
        budget = ModelBudget(
            max_vram_mb=int((snap.vram_free_gb - self.vram_reserve_mb / 1024) * 1024)
            if self._vram_enabled
            else 0,
            max_ram_mb=int(snap.ram_free_gb * 1024),
        )
        if budget.max_vram_mb <= 0 and self._unified_memory:
            budget.strategy = "unified_overflow"
            budget.max_vram_mb = int(snap.vram_total_gb * 1024 * 0.9)
        elif budget.max_vram_mb <= 0:
            budget.strategy = "ram_only"
            budget.max_vram_mb = 0
        return budget

    def can_load(
        self, vram_mb: int, ram_mb: int, priority: ModelPriority = ModelPriority.MEDIUM
    ) -> tuple[bool, str]:
        budget = self.get_budget()
        snap = self.snapshot()

        ram_available = snap.ram_free_gb * 1024
        if ram_mb > ram_available:
            return (
                False,
                f"RAM insufficient: need {ram_mb}MB, have {ram_available:.0f}MB free",
            )

        if self._vram_enabled and vram_mb > 0:
            vram_free = snap.vram_free_gb * 1024
            if vram_free >= vram_mb:
                return True, f"VRAM OK: {vram_mb}MB < {vram_free:.0f}MB free"
            elif self._unified_memory:
                return (
                    True,
                    f"Unified memory: {vram_mb}MB > {vram_free:.0f}MB VRAM, spilling to RAM",
                )
            else:
                return (
                    False,
                    f"VRAM insufficient: need {vram_mb}MB, have {vram_free:.0f}MB free",
                )
        return True, f"RAM OK: {ram_mb}MB"

    def summary(self) -> dict:
        snap = self.snapshot()
        budget = self.get_budget()
        return {
            "ram": {
                "total_gb": snap.ram_total_gb,
                "free_gb": snap.ram_free_gb,
                "zram_gb": snap.ram_zram_gb,
                "zram_effective_gb": snap.ram_zram_effective_gb,
            },
            "vram": {
                "total_gb": snap.vram_total_gb,
                "free_gb": snap.vram_free_gb,
                "used_gb": snap.vram_used_gb,
                "unified": snap.unified_memory,
            },
            "swap": {"total_gb": snap.swap_total_gb, "used_gb": snap.swap_used_gb},
            "budget": {
                "max_vram_mb": budget.max_vram_mb,
                "max_ram_mb": budget.max_ram_mb,
                "strategy": budget.strategy,
            },
        }

    def wait_for_vram(
        self, vram_mb: int, poll_interval: float = 2.0, max_wait: float = 60.0
    ) -> bool:
        import time

        t0 = time.time()
        while time.time() - t0 < max_wait:
            snap = self.snapshot()
            if snap.vram_free_gb * 1024 >= vram_mb + self.vram_reserve_mb:
                return True
            time.sleep(poll_interval)
        return False
