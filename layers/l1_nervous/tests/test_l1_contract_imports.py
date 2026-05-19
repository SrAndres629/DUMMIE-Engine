# Spec Reference: 41_layer_handshake_protocol
from __future__ import annotations

import importlib
import ast
from dataclasses import dataclass
from pathlib import Path

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


def test_nervous_tools_contract_shape_without_import() -> None:
    source = Path("layers/l1_nervous/tools_impl/nervous.py").read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(source)
    register_fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "register_nervous_tools":
            register_fn = node
            break
    assert register_fn is not None, "register_nervous_tools must exist"

    nested_tool_functions = []
    for node in register_fn.body:
        if isinstance(node, ast.AsyncFunctionDef):
            has_tool_decorator = any(
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and isinstance(dec.func.value, ast.Name)
                and dec.func.value.id == "mcp"
                and dec.func.attr == "tool"
                for dec in node.decorator_list
            )
            if has_tool_decorator:
                nested_tool_functions.append(node.name)

    # Contract floor: nervous tool registry must expose a meaningful MCP surface.
    assert len(nested_tool_functions) >= 6
