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
