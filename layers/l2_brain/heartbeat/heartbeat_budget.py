from __future__ import annotations


class HeartbeatBudget:
    def __init__(self, max_ms: int = 2000, max_io_ops: int = 200):
        self.max_ms = int(max_ms)
        self.max_io_ops = int(max_io_ops)
        self.elapsed_ms = 0
        self.io_ops = 0

    def consume_ms(self, value: int) -> None:
        self.elapsed_ms += int(value)

    def consume_io(self, value: int = 1) -> None:
        self.io_ops += int(value)

    def decision(self) -> str:
        if self.elapsed_ms > (self.max_ms * 2) or self.io_ops > (self.max_io_ops * 2):
            return "BLOCK"
        if self.elapsed_ms > self.max_ms or self.io_ops > self.max_io_ops:
            return "WARN"
        return "ALLOW"
