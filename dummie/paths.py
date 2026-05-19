import sys
from pathlib import Path

# The ROOT is the DUMMIE Engine workspace directory
ROOT = Path(__file__).resolve().parents[1]
AIWG = ROOT / ".aiwg"

# Ensure absolute imports work correctly across layers
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "layers" / "l2_brain") not in sys.path:
    sys.path.insert(1, str(ROOT / "layers" / "l2_brain"))
