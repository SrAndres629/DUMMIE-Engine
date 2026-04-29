import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
L1_ROOT = REPO_ROOT / "layers" / "l1_nervous"
L2_ROOT = REPO_ROOT / "layers" / "l2_brain"

for candidate in (REPO_ROOT, L1_ROOT, L2_ROOT):
    path = str(candidate)
    if path not in sys.path:
        sys.path.insert(0, path)
