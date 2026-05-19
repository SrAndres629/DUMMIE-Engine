from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dummie.paths import AIWG, ROOT


@dataclass(frozen=True)
class DummieConfig:
    root_dir: Path = ROOT
    aiwg_dir: Path = AIWG

    @staticmethod
    def get_env(name: str, default: str | None = None) -> str | None:
        """Read from process env only. Never parse .env files from repo."""
        return os.environ.get(name, default)
