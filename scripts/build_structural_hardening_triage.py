#!/usr/bin/env python3
# Spec Reference: 192_embedding_mesh_foundation
import sys
from pathlib import Path

# Add layers to the Python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from layers.l2_brain.structural_hardening.cli import main

if __name__ == "__main__":
    sys.exit(main())
