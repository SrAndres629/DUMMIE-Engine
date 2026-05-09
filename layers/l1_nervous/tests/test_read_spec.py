"""
[T3] Tests de regresión para read_spec.
Verifica que:
- Búsqueda exitosa por spec_id parcial
- Path traversal bloqueado
- Spec no encontrada retorna error estructurado
- Solo busca dentro de doc/specs/
- El spec_id vacío se rechaza
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Para poder importar core.py necesitamos simular FastMCP
# ya que core.py hace `from mcp.server.fastmcp import FastMCP`


class _FakeMCP:
    """Stub de FastMCP para tests unitarios."""
    def __init__(self):
        self._tools = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn
        return decorator


def _register_and_get_read_spec(root_dir: str):
    """Registra las tools con un FakeMCP y devuelve la función read_spec."""
    fake_mcp = _FakeMCP()
    # Importar core y registrar
    _L1 = Path(__file__).resolve().parents[1]
    if str(_L1) not in sys.path:
        sys.path.insert(0, str(_L1))
    if str(_L1 / "tools_impl") not in sys.path:
        sys.path.insert(0, str(_L1 / "tools_impl"))

    # Necesitamos mock de use_cases
    use_cases = MagicMock()
    use_cases.orchestrator = MagicMock()

    from tools_impl.core import register_core_tools
    register_core_tools(fake_mcp, use_cases, root_dir)
    return fake_mcp._tools["read_spec"]


@pytest.fixture
def spec_root(tmp_path):
    """Crea un directorio temporal con specs de prueba."""
    specs_dir = tmp_path / "doc" / "specs"
    specs_dir.mkdir(parents=True)

    # Crear un spec de prueba
    spec_file = specs_dir / "42_metacognitive_identity.md"
    spec_file.write_text(
        "---\n"
        "id: SPEC-42\n"
        "title: Metacognitive Identity\n"
        "version: 1.0\n"
        "---\n"
        "# Spec 42\n\n"
        "This is the metacognitive identity spec.\n"
    )

    # Crear otro spec sin frontmatter
    plain_spec = specs_dir / "00_topology_tracker.md"
    plain_spec.write_text("# Topology Tracker\n\nBasic spec.\n")

    # Crear un spec YAML
    yaml_spec = specs_dir / "config_schema.yaml"
    yaml_spec.write_text("type: object\nproperties:\n  name:\n    type: string\n")

    return tmp_path


@pytest.mark.asyncio
async def test_successful_search_by_partial_id(spec_root):
    """Búsqueda por spec_id parcial encuentra el archivo correcto."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("metacognitive"))
    assert "error" not in result
    assert result["spec_id"] == "metacognitive"
    assert "42_metacognitive_identity.md" in result["file"]
    assert "Metacognitive Identity" in result["content"]


@pytest.mark.asyncio
async def test_frontmatter_parsed(spec_root):
    """Si el spec tiene frontmatter YAML, se incluye en metadata."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("metacognitive"))
    # Metadata puede estar vacía si yaml no está instalado, pero no debe crashear
    if "metadata" in result:
        assert result["metadata"].get("id") == "SPEC-42"
        assert result["metadata"].get("title") == "Metacognitive Identity"


@pytest.mark.asyncio
async def test_spec_not_found_returns_structured_error(spec_root):
    """Spec no encontrada retorna JSON con campo 'error'."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("nonexistent_spec_xyz"))
    assert result["error"] == "SPEC_NOT_FOUND"
    assert result["spec_id"] == "nonexistent_spec_xyz"


@pytest.mark.asyncio
async def test_path_traversal_blocked_dotdot(spec_root):
    """spec_id con '..' es bloqueado."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("../../etc/passwd"))
    assert result["error"] == "SPEC_ID_INVALID"
    assert "forbidden character" in result["reason"]


@pytest.mark.asyncio
async def test_path_traversal_blocked_slash(spec_root):
    """spec_id con '/' es bloqueado."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("path/to/file"))
    assert result["error"] == "SPEC_ID_INVALID"


@pytest.mark.asyncio
async def test_path_traversal_blocked_backslash(spec_root):
    """spec_id con '\\' es bloqueado."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("path\\to\\file"))
    assert result["error"] == "SPEC_ID_INVALID"


@pytest.mark.asyncio
async def test_empty_spec_id_rejected(spec_root):
    """spec_id vacío es rechazado."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec(""))
    assert result["error"] == "SPEC_ID_EMPTY"


@pytest.mark.asyncio
async def test_whitespace_only_spec_id_rejected(spec_root):
    """spec_id solo whitespace es rechazado."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("   "))
    assert result["error"] == "SPEC_ID_EMPTY"


@pytest.mark.asyncio
async def test_yaml_spec_found(spec_root):
    """Archivos .yaml también se buscan."""
    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("config_schema"))
    assert "error" not in result
    assert result["file"] == "config_schema.yaml"


@pytest.mark.asyncio
async def test_search_only_in_specs_dir(spec_root):
    """No busca fuera de doc/specs/."""
    # Crear un archivo fuera de doc/specs/ con nombre matching
    outside = spec_root / "secret.md"
    outside.write_text("SECRET DATA")

    read_spec = _register_and_get_read_spec(str(spec_root))
    result = json.loads(await read_spec("secret"))
    assert result["error"] == "SPEC_NOT_FOUND"
