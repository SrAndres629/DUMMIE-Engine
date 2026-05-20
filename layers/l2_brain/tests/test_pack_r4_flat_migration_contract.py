from __future__ import annotations

import importlib
from pathlib import Path


L2_ROOT = Path(__file__).resolve().parents[1]


def test_public_l2_modules_resolve_outside_flat_brain():
    public_modules = [
        "layers.l2_brain.action_graph",
        "layers.l2_brain.token_cost_ledger",
        "layers.l2_brain.neuron_ledger",
        "layers.l2_brain.model_router",
        "layers.l2_brain.model_discovery",
        "layers.l2_brain.model_executor",
        "layers.l2_brain.supervisor_protocol",
    ]

    for module_name in public_modules:
        module = importlib.import_module(module_name)
        module_file = Path(module.__file__).resolve()
        assert "flat_brain" not in module_file.parts, f"{module_name} resolves through legacy flat_brain: {module_file}"


def test_canonical_organs_do_not_import_flat_brain_directly():
    offenders: list[str] = []
    for path in L2_ROOT.rglob("*.py"):
        relative = path.relative_to(L2_ROOT)
        if any(part in {".venv", ".pytest_cache", "__pycache__"} for part in relative.parts):
            continue
        if relative.parts[0] in {"flat_brain", "src", "tests"}:
            continue
        if relative.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "layers.l2_brain.flat_brain" in text:
            offenders.append(str(relative))

    assert offenders == []
