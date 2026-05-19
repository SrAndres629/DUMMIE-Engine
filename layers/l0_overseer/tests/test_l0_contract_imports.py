# Spec Reference: 03_polyglot_architecture
from __future__ import annotations

import importlib


def test_l0_supervisor_import_contract() -> None:
    module = importlib.import_module("layers.l0_overseer.supervisor")
    assert module is not None
