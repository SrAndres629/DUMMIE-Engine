"""
[T1] Tests de regresión para UnsafeBypassShieldAdapter.
Verifica que:
- El bypass está bloqueado por defecto
- Solo se permite con DUMMIE_ALLOW_UNSAFE_BYPASS=true
- NativeShieldAdapter es un alias deprecated
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import UnsafeBypassShieldAdapter


@pytest.fixture
def adapter():
    return UnsafeBypassShieldAdapter()


@pytest.mark.asyncio
async def test_bypass_blocked_by_default(adapter):
    """Sin envvar, audit() debe lanzar RuntimeError"""
    # Asegurar que la envvar NO está configurada
    os.environ.pop("DUMMIE_ALLOW_UNSAFE_BYPASS", None)
    with pytest.raises(RuntimeError, match="BYPASS_SHIELD_BLOCKED"):
        await adapter.audit("<dag/>", "test goal")


@pytest.mark.asyncio
async def test_bypass_allowed_with_envvar(adapter):
    """Con DUMMIE_ALLOW_UNSAFE_BYPASS=true, audit() retorna BYPASS"""
    os.environ["DUMMIE_ALLOW_UNSAFE_BYPASS"] = "true"
    try:
        ok, msg = await adapter.audit("<dag/>", "test goal")
        assert ok is True
        assert msg == "BYPASS"
    finally:
        os.environ.pop("DUMMIE_ALLOW_UNSAFE_BYPASS", None)


@pytest.mark.asyncio
async def test_bypass_blocked_with_wrong_envvar_value(adapter):
    """Con DUMMIE_ALLOW_UNSAFE_BYPASS=false, audit() debe lanzar"""
    os.environ["DUMMIE_ALLOW_UNSAFE_BYPASS"] = "false"
    try:
        with pytest.raises(RuntimeError, match="BYPASS_SHIELD_BLOCKED"):
            await adapter.audit("<dag/>", "test goal")
    finally:
        os.environ.pop("DUMMIE_ALLOW_UNSAFE_BYPASS", None)


def test_native_shield_adapter_is_deprecated_alias():
    """NativeShieldAdapter debe ser un alias de UnsafeBypassShieldAdapter"""
    from adapters import NativeShieldAdapter
    assert NativeShieldAdapter is UnsafeBypassShieldAdapter
