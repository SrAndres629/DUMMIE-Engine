from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import socket
import os
import errno

@dataclass
class RuntimePaths:
    repo_root: Path
    aiwg_dir: Path
    socket_path: Path
    pid_path: Path
    log_path: Path
    binary_path: Path
    l0_dir: Path

def is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        # PermissionError means it is alive but owned by someone else
        return err.errno == errno.EPERM
    return False

def probe_status(paths: RuntimePaths) -> Dict[str, Any]:
    status = {
        "running": False,
        "pid": None,
        "pid_alive": False,
        "socket_exists": False,
        "ping_ok": False,
        "stale_pid_file": False,
    }

    # Check UNIX socket existence
    socket_exists = paths.socket_path.exists()
    status["socket_exists"] = socket_exists

    # Ping UNIX socket
    if socket_exists:
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(0.5)
            client.connect(str(paths.socket_path))
            client.sendall(b'{"cmd": "ping"}\n')
            response = client.recv(1024)
            client.close()
            if response:
                status["ping_ok"] = True
        except Exception:
            pass

    # Read PID file
    pid = None
    if paths.pid_path.exists():
        try:
            content = paths.pid_path.read_text(encoding="utf-8").strip()
            if content.isdigit():
                pid = int(content)
                status["pid"] = pid
        except Exception:
            pass

    # Check if PID is alive
    if pid is not None:
        pid_alive = is_pid_alive(pid)
        status["pid_alive"] = pid_alive
        if not pid_alive:
            status["stale_pid_file"] = True
    else:
        status["pid_alive"] = False

    # Determine if running
    if status["ping_ok"] or status["pid_alive"]:
        status["running"] = True

    return status
