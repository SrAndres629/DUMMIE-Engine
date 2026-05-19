# Spec Reference: 41_layer_handshake_protocol
from __future__ import annotations

import importlib
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class ModuleContract:
    module: str
    optional_dependency: str | None = None


MODULE_CONTRACTS = [
    ModuleContract("layers.l1_nervous.bootstrap"),
    ModuleContract("layers.l1_nervous.application.use_cases"),
    ModuleContract("layers.l1_nervous.domain.services"),
    ModuleContract("layers.l1_nervous.knowledge_adapters"),
    ModuleContract("layers.l1_nervous.mcp_registry"),
    ModuleContract("layers.l1_nervous.mcp_transport"),
    ModuleContract("layers.l1_nervous.repo_guard"),
    ModuleContract("layers.l1_nervous.runtime_paths"),
    ModuleContract("layers.l1_nervous.tools_impl.nervous", optional_dependency="mcp"),
    ModuleContract("layers.l1_nervous.tools_impl.patch_transactions"),
    ModuleContract("layers.l1_nervous.utils"),
]


@pytest.mark.parametrize("contract", MODULE_CONTRACTS, ids=lambda c: c.module)
def test_l1_nervous_module_import_contract(contract: ModuleContract) -> None:
    try:
        importlib.import_module(contract.module)
    except ModuleNotFoundError as exc:
        if contract.optional_dependency and exc.name == contract.optional_dependency:
            pytest.skip(f"optional dependency required for {contract.module}: {exc.name}")
        raise


def test_register_nervous_tools_signature() -> None:
    try:
        from layers.l1_nervous.tools_impl.nervous import register_nervous_tools
        import inspect
        sig = inspect.signature(register_nervous_tools)
        assert "mcp" in sig.parameters
        assert "use_cases" in sig.parameters
        assert "root_dir" in sig.parameters
    except (ModuleNotFoundError, ImportError) as exc:
        # Check if missing 'mcp' or other dependency caused it
        if hasattr(exc, "name") and exc.name == "mcp":
            pytest.skip("optional dependency 'mcp' not installed")
        raise

