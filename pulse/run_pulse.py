#!/usr/bin/env python3
"""Pulse Engine daemon entry point — systemd ExecStart target.

Usage: python3 run_pulse.py          # daemon mode (polling every 60s)
       python3 run_pulse.py trigger  # single manual pulse
       python3 run_pulse.py health   # print health JSON to stdout
       python3 run_pulse.py status   # print guard stats to stdout
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _run_daemon():
    from pulse.daemon import main

    main()


def _run_trigger():
    from pulse.config import PulseConfig
    from pulse.guards import GuardState

    config = PulseConfig()
    guards = GuardState(f"{config.pulse_root}/guard_state.json")
    can_run, reason = guards.can_pulse(config.guards)

    if can_run:
        print(f"Trigger: pulse allowed — {reason}")
        _run_daemon_once()
    else:
        print(f"Trigger: pulse blocked — {reason}")
        sys.exit(1)


def _run_daemon_once():
    import asyncio
    import logging
    from pulse.config import PulseConfig
    from pulse.daemon import PulseDaemon

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    config = PulseConfig()
    daemon = PulseDaemon(config)
    daemon.running = True
    asyncio.run(daemon._check_and_run_pulse())


def _run_health():
    import json
    from pulse.config import PulseConfig
    from pulse.guards import GuardState
    from pulse.progress import ProgressTracker

    config = PulseConfig()
    guards = GuardState(f"{config.pulse_root}/guard_state.json")
    progress = ProgressTracker(f"{config.pulse_root}/progress")

    output = {
        "status": "healthy",
        "version": "1.0.0",
        "guards": guards.get_stats(),
        "recent_pulses": progress.get_recent_pulses(count=3),
        "metrics": progress.calculate_progress_metrics(),
    }
    print(json.dumps(output, indent=2))


def _run_status():
    import json
    from pulse.config import PulseConfig
    from pulse.guards import GuardState
    from pulse.progress import ProgressTracker

    config = PulseConfig()
    guards = GuardState(f"{config.pulse_root}/guard_state.json")
    progress = ProgressTracker(f"{config.pulse_root}/progress")

    output = {
        "guards": guards.get_stats(),
        "metrics": progress.calculate_progress_metrics(),
        "recent_pulses": progress.get_recent_pulses(count=5),
    }
    print(json.dumps(output, indent=2))


COMMANDS = {
    "start": _run_daemon,
    "trigger": _run_trigger,
    "health": _run_health,
    "status": _run_status,
}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd not in COMMANDS:
        print(f"Usage: {sys.argv[0]} [start|trigger|health|status]", file=sys.stderr)
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
    COMMANDS[cmd]()
