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

def kill_processes(pids: list):
    for pid_info in pids:
        try:
            pid = int(pid_info.split()[0])
            logger.info(f"Killing orphan PID {pid}...")
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            # Verify if still alive
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass # Already dead
        except Exception as e:
            logger.warning(f"Failed to kill {pid_info}: {e}")

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
    logger.info("Cycling Factory...")
    subprocess.run(["bash", str(ROOT_DIR / "scripts" / "lab-off-safe.sh")])
    time.sleep(2)
    subprocess.run(["bash", str(ROOT_DIR / "scripts" / "lab-on-safe.sh")])

def main():
    diagnostic = run_doctor()
    if not diagnostic:
        logger.error("Could not obtain diagnostic. Aborting.")
        return

    # 1. Process Cleanup
    relevant_pids = diagnostic.get("results", {}).get("processes", {}).get("relevant", [])
    if relevant_pids:
        kill_processes(relevant_pids)
    
    # 2. Filesystem Cleanup
    clean_sockets()
    
    # 3. Industrial Sync
    run_build()
    
    # 4. State Cycle
    restart_factory()
    
    # 5. Final Verification
    time.sleep(5)
    final_diagnostic = run_doctor()
    if final_diagnostic.get("ok"):
        logger.info("=== REPAIR SUCCESSFUL: ENGINE IS READY ===")
    else:
        logger.error("=== REPAIR DEGRADED: Manual intervention required ===")

if __name__ == "__main__":
    main()
