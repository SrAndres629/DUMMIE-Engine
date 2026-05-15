import os
import json
import subprocess
import signal
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DUMMIE-Repair")

ROOT_DIR = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT_DIR / "layers" / "l2_brain" / ".venv" / "bin" / "python"
DOCTOR_PY = ROOT_DIR / "scripts" / "dummie_mcp_doctor.py"

def run_doctor() -> dict:
    logger.info("Running DUMMIE Doctor Diagnostic...")
    cmd = [str(VENV_PYTHON), str(DOCTOR_PY), "--json", "--skip-codex"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract JSON from output
    raw = result.stdout
    start_marker = "--- JSON START ---"
    end_marker = "--- JSON END ---"
    if start_marker in raw and end_marker in raw:
        json_str = raw.split(start_marker)[1].split(end_marker)[0].strip()
        return json.loads(json_str)
    return {}



def clean_sockets():
    socket_dir = ROOT_DIR / ".aiwg" / "sockets"
    if socket_dir.exists():
        logger.info(f"Cleaning stale sockets in {socket_dir}...")
        for sock in socket_dir.glob("*.sock"):
            try:
                sock.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove {sock}: {e}")

def run_build():
    logger.info("Triggering Industrial Build...")
    subprocess.run(["bash", str(ROOT_DIR / "scripts" / "build_factory.sh")], check=True)

def restart_factory():
    logger.info("Cycling Factory via Systemd...")
    subprocess.run(["systemctl", "--user", "restart", "dummie-engine.service"])
    time.sleep(2)

def main():
    diagnostic = run_doctor()
    if not diagnostic:
        logger.error("Could not obtain diagnostic. Aborting.")
        return

    # 1. Graceful Lifecycle Restart (Systemd)
    restart_factory()
    
    # 2. Filesystem Cleanup (Stale locks)
    clean_sockets()
    
    # 3. Industrial Sync
    run_build()
    
    # 4. Final Verification
    time.sleep(5)
    final_diagnostic = run_doctor()
    if final_diagnostic.get("ok"):
        logger.info("=== REPAIR SUCCESSFUL: ENGINE IS READY ===")
    else:
        logger.error("=== REPAIR DEGRADED: Manual intervention required ===")

if __name__ == "__main__":
    main()
