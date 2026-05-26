"""Workaround for Python 3.12.3 importlib._bootstrap._find_and_load_unlocked bug.

Uses importlib.util to load modules explicitly, bypassing the buggy code path.
See: https://github.com/python/cpython/issues/117589

Usage: Put `from . import _bootstrap` at the top of __init__.py
"""

import importlib.util
import sys
from pathlib import Path

_PULSE_DIR = Path(__file__).parent
_LOAD_ORDER = [
    "config",  # no internal deps
    "guards",  # depends on config
    "progress",  # no internal deps
    "phases",  # depends on config, progress
    "daemon",  # depends on config, guards, progress, phases
    "api",  # depends on config, guards, progress
]


def _load_module(name: str):
    full_name = f"pulse.{name}"
    path = _PULSE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


for mod_name in _LOAD_ORDER:
    try:
        _load_module(mod_name)
    except Exception as e:
        print(f"WARNING: Failed to load pulse.{mod_name}: {e}", file=sys.stderr)
