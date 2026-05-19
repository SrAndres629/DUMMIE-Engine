from __future__ import annotations

import subprocess
import sys

from dummie.paths import ROOT


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "dummie", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


def test_dummie_cli_status() -> None:
    res = _run("status")
    assert res.returncode == 0
    assert "DUMMIE Engine Status" in res.stdout


def test_dummie_cli_whoami() -> None:
    res = _run("whoami")
    assert res.returncode == 0
    assert "Soy DUMMIE Engine" in res.stdout


def test_dummie_cli_advise() -> None:
    res = _run("advise", "quiero", "llegar", "a", "10000", "mrr")
    assert res.returncode == 0
    assert "Objetivo detectado: revenue" in res.stdout
