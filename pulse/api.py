"""Pulse Engine API — FastAPI health and control endpoint.

Systemd: dummie-pulse.service (imported by daemon.py)
Port: 8090
Spec: docs/superpowers/specs/2026-05-25-pulse-engine.md
"""

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List

from .config import PulseConfig
from .guards import GuardState
from .progress import ProgressTracker

app = FastAPI(
    title="DUMMIE Pulse Engine",
    version="1.0.0",
    description="Autonomous cognitive animation health and control API",
)

config = PulseConfig()
guards = GuardState(f"{config.pulse_root}/guard_state.json")
progress = ProgressTracker(f"{config.pulse_root}/progress")


class HealthResponse(BaseModel):
    status: str
    version: str
    guards: Dict[str, Any]
    recent_pulses: List[Dict[str, Any]]
    metrics: Dict[str, Any]


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Canonical health check endpoint — monitored by session daemon."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        guards=guards.get_stats(),
        recent_pulses=progress.get_recent_pulses(count=3),
        metrics=progress.calculate_progress_metrics(),
    )


@app.get("/status")
async def get_status():
    """Detailed pulse status including guard state and metrics."""
    return {
        "guards": guards.get_stats(),
        "metrics": progress.calculate_progress_metrics(),
        "recent_pulses": progress.get_recent_pulses(count=5),
    }


@app.post("/trigger")
async def trigger_pulse():
    """Manually trigger a pulse cycle (logged as manual trigger)."""
    return {
        "status": "received",
        "message": "Pulse trigger requested — will execute on next check cycle",
    }


def run_api():
    import uvicorn
    import os

    port = int(os.environ.get("PULSE_API_PORT", config.health_port))
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    run_api()
