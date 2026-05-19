from __future__ import annotations

import pytest
import importlib.util
import socket
import threading
from pathlib import Path


def load_ctl_module():
    script = Path(__file__).resolve().parents[3] / "scripts" / "dummied_ctl.py"
    spec = importlib.util.spec_from_file_location("dummied_ctl", script)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(not Path("scripts/dummied_ctl.py").exists(), reason="dummied_ctl.py not yet created")
def test_probe_status_reports_live_control_socket(tmp_path: Path):
    ctl = load_ctl_module()
    socket_path = tmp_path / "dummied.sock"
    ready = threading.Event()

    def serve_once():
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(socket_path))
        server.listen(1)
        ready.set()
        conn, _ = server.accept()
        with conn:
            conn.recv(4096)
            conn.sendall(b'{"status":"ok","message":"PONG"}\n')
        server.close()

    thread = threading.Thread(target=serve_once, daemon=True)
    thread.start()
    assert ready.wait(timeout=1)

    paths = ctl.RuntimePaths(
        repo_root=tmp_path,
        aiwg_dir=tmp_path / ".aiwg",
        socket_path=socket_path,
        pid_path=tmp_path / ".aiwg" / "run" / "dummied.pid",
        log_path=tmp_path / ".aiwg" / "logs" / "dummied.log",
        binary_path=tmp_path / "layers" / "l0_overseer" / "dummied",
        l0_dir=tmp_path / "layers" / "l0_overseer",
    )

    status = ctl.probe_status(paths)

    assert status["running"] is True
    assert status["ping_ok"] is True
    assert status["socket_exists"] is True


@pytest.mark.skipif(not Path("scripts/dummied_ctl.py").exists(), reason="dummied_ctl.py not yet created")
def test_probe_status_reports_stale_pid_file(tmp_path: Path):
    ctl = load_ctl_module()
    pid_path = tmp_path / ".aiwg" / "run" / "dummied.pid"
    pid_path.parent.mkdir(parents=True)
    pid_path.write_text("99999999\n")

    paths = ctl.RuntimePaths(
        repo_root=tmp_path,
        aiwg_dir=tmp_path / ".aiwg",
        socket_path=tmp_path / ".aiwg" / "sockets" / "dummied.sock",
        pid_path=pid_path,
        log_path=tmp_path / ".aiwg" / "logs" / "dummied.log",
        binary_path=tmp_path / "layers" / "l0_overseer" / "dummied",
        l0_dir=tmp_path / "layers" / "l0_overseer",
    )

    status = ctl.probe_status(paths)

    assert status["running"] is False
    assert status["pid"] == 99999999
    assert status["pid_alive"] is False
    assert status["stale_pid_file"] is True
