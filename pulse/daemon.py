"""Pulse Engine daemon — production entry point for autonomous cognitive animation.

Systemd: dummie-pulse.service
Port: 8090 (health API — see api.py)
Production log: .aiwg/reports/pulse_prod.jsonl
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import PulseConfig, GuardConfig
from .guards import GuardState
from .progress import ProgressTracker, PulseResult
from .phases import PhaseExecutor, CloudCircuitBreaker

logger = logging.getLogger(__name__)


def _prod_log(entry: dict):
    """Append a structured production log entry."""
    prod_log_path = Path("/opt/dummie-engine/.aiwg/reports/pulse_prod.jsonl")
    prod_log_path.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = datetime.now().isoformat()
    with open(prod_log_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


class PulseDaemon:
    """Main Pulse Engine daemon.

    Polls every 60 seconds for pulse eligibility.
    When conditions are right (guards pass, idle detected),
    executes a full P1→P2→P3→P4 cycle.
    """

    CHECK_INTERVAL = 60

    def __init__(self, config: PulseConfig = None):
        self.config = config or PulseConfig()
        self.guards = GuardState(f"{self.config.pulse_root}/guard_state.json")
        self.breaker = CloudCircuitBreaker(self.config.guards)
        self.progress = ProgressTracker(f"{self.config.pulse_root}/progress")
        self.running = False
        self.current_pulse: Optional[PulseResult] = None
        self._started_at = datetime.now().isoformat()
        self._cycles_completed = 0
        self._cycles_failed = 0
        self._total_cloud_tokens = 0
        self._total_local_tokens = 0

    async def start(self):
        self.running = True
        self._started_at = datetime.now().isoformat()
        logger.info("Pulse Engine daemon started (interval=%ds)", self.CHECK_INTERVAL)
        logger.info("Guards: %s", self.guards.get_stats())
        logger.info("Cloud breaker: %s", self.breaker.get_stats())

        _prod_log(
            {
                "event": "daemon_started",
                "interval_s": self.CHECK_INTERVAL,
                "guards": self.guards.get_stats(),
                "breaker": self.breaker.get_stats(),
                "pid": os.getpid(),
            }
        )

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(
                    sig, lambda s=sig: asyncio.create_task(self.shutdown(s))
                )
            except NotImplementedError:
                pass

        while self.running:
            try:
                await self._check_and_run_pulse()
            except Exception as e:
                logger.exception("Daemon loop error: %s", e)
            await asyncio.sleep(self.CHECK_INTERVAL)

    async def shutdown(self, sig=None):
        logger.info("Pulse Engine daemon shutting down (signal=%s)", sig)
        self.running = False
        uptime_s = (
            datetime.now() - datetime.fromisoformat(self._started_at)
        ).total_seconds()
        _prod_log(
            {
                "event": "daemon_shutdown",
                "signal": str(sig),
                "uptime_s": uptime_s,
                "cycles_completed": self._cycles_completed,
                "cycles_failed": self._cycles_failed,
                "total_cloud_tokens": self._total_cloud_tokens,
                "total_local_tokens": self._total_local_tokens,
            }
        )

    async def _check_and_run_pulse(self):
        can_run, reason = self.guards.can_pulse(self.config.guards)
        if not can_run:
            return

        logger.info("=== Pulse cycle starting: %s ===", reason)
        _prod_log({"event": "pulse_start", "reason": reason})

        self.guards.record_pulse_start()
        pulse_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_pulse = self.progress.start_pulse(pulse_id)
        context = await self._build_context()
        pulse_failed = False
        phase_logs = []
        cloud_tokens_this_cycle = 0
        local_tokens_this_cycle = 0

        for phase_config in self.config.phases:
            if not self.running:
                break

            logger.info(
                "[%s] Executing phase '%s' (%s)...",
                pulse_id,
                phase_config.name,
                phase_config.model,
            )

            executor = PhaseExecutor(phase_config, self.breaker)
            result = await executor.execute(context)

            self.progress.add_phase_result(self.current_pulse, result)
            self.guards.record_tokens(result.tokens_used)

            cloud_tok = getattr(result, "cloud_tokens", 0)
            local_tok = getattr(result, "local_tokens", 0)
            cloud_tokens_this_cycle += cloud_tok
            local_tokens_this_cycle += local_tok

            phase_entry = {
                "phase": phase_config.name,
                "model": getattr(result, "model_used", phase_config.model),
                "provider": getattr(result, "provider_used", "unknown"),
                "fallback": getattr(result, "fallback_triggered", False),
                "status": result.status,
                "tokens": result.tokens_used,
                "cloud_tokens": cloud_tok,
                "local_tokens": local_tok,
                "duration_s": round(result.duration_seconds, 2),
                "cost_usd": round(cloud_tok / 1_000_000 * 2.0, 6),
            }
            phase_logs.append(phase_entry)

            logger.info(
                "[%s] Phase '%s': %s (%s, %d tokens, %.1fs)%s",
                pulse_id,
                phase_config.name,
                result.status,
                getattr(result, "model_used", "?"),
                result.tokens_used,
                result.duration_seconds,
                " [FALLBACK]" if getattr(result, "fallback_triggered", False) else "",
            )

            if result.errors and result.status != "success":
                logger.error(
                    "[%s] %s error: %s", pulse_id, phase_config.name, result.errors
                )

            if result.status == "failed":
                pulse_failed = True
                break

            context[f"{phase_config.name}_results"] = result.output_summary

        self._total_cloud_tokens += cloud_tokens_this_cycle
        self._total_local_tokens += local_tokens_this_cycle

        if pulse_failed:
            self._cycles_failed += 1
            self.guards.record_failure()
            self.progress.complete_pulse(self.current_pulse, "failed")
            logger.warning("=== Pulse %s FAILED ===", pulse_id)
            _prod_log(
                {
                    "event": "pulse_complete",
                    "pulse_id": pulse_id,
                    "status": "failed",
                    "phases": phase_logs,
                    "cloud_tokens": cloud_tokens_this_cycle,
                    "local_tokens": local_tokens_this_cycle,
                    "budget_remaining": self.guards.get_stats()[
                        "token_budget_remaining"
                    ],
                }
            )
        else:
            self._cycles_completed += 1
            self.guards.record_success()
            self.progress.complete_pulse(self.current_pulse, "completed")
            logger.info("=== Pulse %s COMPLETED ===", pulse_id)
            _prod_log(
                {
                    "event": "pulse_complete",
                    "pulse_id": pulse_id,
                    "status": "completed",
                    "phases": phase_logs,
                    "cloud_tokens": cloud_tokens_this_cycle,
                    "local_tokens": local_tokens_this_cycle,
                    "budget_remaining": self.guards.get_stats()[
                        "token_budget_remaining"
                    ],
                }
            )

        logger.info("Guard stats: %s", self.guards.get_stats())

    async def _build_context(self) -> dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "system_state": await self._get_system_state(),
            "recent_activity": await self._get_recent_activity(),
        }

    async def _get_system_state(self) -> str:
        try:
            truth = Path("/opt/dummie-engine/.aiwg/heartbeat/signal.json")
            state_parts = ["System state:"]
            if truth.exists():
                data = json.loads(truth.read_text())
                state_parts.append(f"Status: {data.get('status', 'unknown')}")
                state_parts.append(f"Coherence: {data.get('coherence_score', 'N/A')}")
                state_parts.append(f"Blockers: {data.get('active_blockers', [])}")
            return " ".join(state_parts)
        except Exception:
            return "System state: limited"

    async def _get_recent_activity(self) -> str:
        try:
            events_file = Path("/opt/dummie-engine/.aiwg/sessions/CURRENT/events.jsonl")
            if events_file.exists():
                lines = events_file.read_text().strip().split("\n")
                last = lines[-1] if lines and lines[-1] else None
                return (
                    f"Last event: {last[:200]}"
                    if last
                    else "No recent session activity"
                )
            return "No session events"
        except Exception:
            return "Activity tracking unavailable"


import os


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("/opt/dummie-engine/.aiwg/reports/pulse.log"),
        ],
    )
    config = PulseConfig()
    daemon = PulseDaemon(config)
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        asyncio.run(daemon.shutdown())


if __name__ == "__main__":
    main()
