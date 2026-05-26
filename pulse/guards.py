"""Anti-loop guards — prevent resource exhaustion and infinite cycles.

Source of Truth: .aiwg/pulse/guard_state.json
Traced: GuardConfig in config.py
Kernel: cgroups v2 memory.high / memory.max enforcement
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Tuple

from .config import GuardConfig

logger = logging.getLogger(__name__)


class GuardState:
    """Persistent guard state with automatic daily reset.

    Tracks:
    - pulses_today: Number of pulses executed today
    - tokens_today: Total tokens consumed today
    - last_pulse: ISO timestamp of last pulse
    - consecutive_failures: Number of consecutive failed pulses
    - reset_date: Date of last reset (for new-day detection)
    """

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupted guard state, resetting")
        return {
            "pulses_today": 0,
            "tokens_today": 0,
            "last_pulse": None,
            "consecutive_failures": 0,
            "reset_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def save(self):
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=2)

    def _reset_if_new_day(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self._state["reset_date"] != today:
            logger.info("New day detected, resetting daily counters")
            self._state["pulses_today"] = 0
            self._state["tokens_today"] = 0
            self._state["reset_date"] = today
            self.save()

    def can_pulse(self, config: GuardConfig) -> Tuple[bool, str]:
        """Check if a pulse cycle is allowed under current guard constraints.

        Returns:
            (allowed: bool, reason: str)
        """
        self._reset_if_new_day()

        now = datetime.now()
        hour = now.hour

        # Quiet hours (23-06) — system maintenance, no pulses
        if config.quiet_hours_start <= hour or hour < config.quiet_hours_end:
            return False, "Quiet hours (23-06)"

        # Daily pulse limit
        if self._state["pulses_today"] >= config.max_pulses_per_day:
            return False, (
                f"Daily pulse limit: {self._state['pulses_today']}/"
                f"{config.max_pulses_per_day}"
            )

        # Token budget
        if self._state["tokens_today"] >= config.max_daily_token_budget:
            return False, (
                f"Token budget exceeded: {self._state['tokens_today']}/"
                f"{config.max_daily_token_budget}"
            )

        # Minimum interval between pulses
        if self._state["last_pulse"]:
            last = datetime.fromisoformat(self._state["last_pulse"])
            elapsed = (now - last).total_seconds() / 60
            if elapsed < config.min_interval_minutes:
                remaining = config.min_interval_minutes - elapsed
                return False, f"Interval: wait {remaining:.0f}min"

        # Consecutive failure guard
        if self._state["consecutive_failures"] >= config.max_consecutive_failures:
            return False, (
                f"Too many consecutive failures ({self._state['consecutive_failures']})"
            )

        return True, "OK"

    def record_pulse_start(self):
        self._state["pulses_today"] += 1
        self._state["last_pulse"] = datetime.now().isoformat()
        self.save()
        logger.info("Pulse %d/%d started", self._state["pulses_today"], 3)

    def record_tokens(self, count: int):
        self._state["tokens_today"] += count
        self.save()

    def record_success(self):
        self._state["consecutive_failures"] = 0
        self.save()
        logger.info("Pulse succeeded, failure counter reset")

    def record_failure(self):
        self._state["consecutive_failures"] += 1
        self.save()
        logger.warning(
            "Pulse failed (%d consecutive)", self._state["consecutive_failures"]
        )

    def get_stats(self) -> Dict[str, Any]:
        self._reset_if_new_day()
        max_tokens = 500000
        return {
            **self._state,
            "token_budget_remaining": max(0, max_tokens - self._state["tokens_today"]),
            "pulses_remaining": max(0, 3 - self._state["pulses_today"]),
            "token_budget_pct": (
                self._state["tokens_today"] / max_tokens * 100 if max_tokens > 0 else 0
            ),
        }
