import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
AIWG = ROOT / ".aiwg"
RUNTIME = AIWG / "runtime" / "models"
WANTED = RUNTIME / "wanted.json"
EVENTS = RUNTIME / "events.jsonl"
STATUS = RUNTIME / "status.json"

logger = logging.getLogger("dummie.models-pull")

ENV = {
    **os.environ,
    "PATH": f"{os.environ.get('HOME', '/home/jorand')}/.local/bin:/usr/local/bin:/usr/bin:/bin",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_event(event: dict):
    entry = {"timestamp": _now(), **event}
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _write_status(state: dict):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(state, indent=2))


def _ollama_list() -> set[str]:
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, env=ENV, timeout=30
        )
        installed = set()
        for line in result.stdout.strip().split("\n")[1:]:
            name = line.split()[0] if line.split() else ""
            if name:
                installed.add(name)
        return installed
    except Exception as e:
        logger.warning(f"ollama list failed: {e}")
        return set()


def _pull_model(model_id: str) -> bool:
    logger.info(f"Pulling model: {model_id}")
    _log_event({"event": "pull_started", "model": model_id})
    try:
        result = subprocess.run(
            ["ollama", "pull", model_id],
            capture_output=True,
            text=True,
            env=ENV,
            timeout=3600,
        )
        if result.returncode == 0:
            ready_file = RUNTIME / f"{model_id}.ready"
            ready_file.parent.mkdir(parents=True, exist_ok=True)
            ready_file.write_text(_now())
            logger.info(f"Model pulled: {model_id}")
            _log_event({"event": "pull_completed", "model": model_id})
            return True
        else:
            logger.error(f"Pull failed for {model_id}: {result.stderr.strip()}")
            _log_event(
                {
                    "event": "pull_failed",
                    "model": model_id,
                    "error": result.stderr.strip(),
                }
            )
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"Pull timed out for {model_id}")
        _log_event({"event": "pull_timeout", "model": model_id})
        return False
    except Exception as e:
        logger.exception(f"Pull crashed for {model_id}: {e}")
        _log_event({"event": "pull_crashed", "model": model_id, "error": str(e)})
        return False


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    logger.info("Models pull daemon tick")

    RUNTIME.mkdir(parents=True, exist_ok=True)

    wanted_models = []
    if WANTED.exists():
        try:
            raw = json.loads(WANTED.read_text())
            wanted_models = raw.get("models", [])
        except Exception as e:
            logger.warning(f"wanted.json parse error: {e}")
            _write_status(
                {"status": "config_error", "error": str(e), "timestamp": _now()}
            )
            return

    if not wanted_models:
        logger.info("No models in wanted.json — nothing to pull")
        _write_status(
            {
                "status": "idle",
                "models_installed": sorted(_ollama_list()),
                "timestamp": _now(),
            }
        )
        return

    installed = _ollama_list()
    missing = [m for m in wanted_models if m not in installed]

    if not missing:
        logger.info(f"All {len(wanted_models)} models already installed")
        for m in wanted_models:
            rf = RUNTIME / f"{m}.ready"
            if not rf.exists():
                rf.parent.mkdir(parents=True, exist_ok=True)
                rf.write_text(_now())
        _write_status(
            {
                "status": "complete",
                "models_installed": sorted(installed),
                "timestamp": _now(),
            }
        )
        return

    logger.info(f"Missing models ({len(missing)}): {missing}")
    _write_status(
        {
            "status": "pulling",
            "models_installed": sorted(installed),
            "models_pending": missing,
            "timestamp": _now(),
        }
    )

    for model_id in missing:
        _pull_model(model_id)

    final_installed = _ollama_list()
    still_missing = [m for m in wanted_models if m not in final_installed]
    if still_missing:
        _write_status(
            {
                "status": "partial",
                "models_installed": sorted(final_installed),
                "models_pending": still_missing,
                "timestamp": _now(),
            }
        )
    else:
        _write_status(
            {
                "status": "complete",
                "models_installed": sorted(final_installed),
                "timestamp": _now(),
            }
        )


if __name__ == "__main__":
    main()
