import subprocess
import sys
from pathlib import Path
from dummie.paths import ROOT

def test_dummie_cli_status():
    cmd = [sys.executable, "-m", "dummie", "status"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 0
    assert "DUMMIE Engine Status" in res.stdout

def test_dummie_cli_whoami():
    cmd = [sys.executable, "-m", "dummie", "whoami"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 0
    assert "Soy DUMMIE Engine" in res.stdout

def test_dummie_cli_advise():
    cmd = [sys.executable, "-m", "dummie", "advise", "quiero llegar a 10000 mrr"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 0
    assert "Goal Classification" in res.stdout
    assert "Strategic Questions" in res.stdout
