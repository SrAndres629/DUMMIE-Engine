import os
import pytest
import shutil
import sys
from pathlib import Path

# Alinear con el estilo de tests del proyecto
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import KuzuRepository

def test_kuzu_path_policy(tmp_path):
    # Caso 1: Path inexistente en directorio existente (debe funcionar)
    db_path = str(tmp_path / "new_db")
    repo = KuzuRepository(db_path=db_path)
    assert repo.db is not None
    assert os.path.exists(db_path) 
    
    # Caso 2: Path es un directorio ya existente pero VACÍO (debe fallar según nuestra política de hardening)
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    with pytest.raises(ValueError) as exc:
        KuzuRepository(db_path=str(empty_dir))
    assert "directory" in str(exc.value).lower()

def test_kuzu_parent_creation(tmp_path):
    # Caso 3: El directorio padre no existe (debe crearlo)
    nested_path = str(tmp_path / "deep" / "nested" / "db")
    repo = KuzuRepository(db_path=nested_path)
    assert repo.db is not None
    assert os.path.exists(os.path.dirname(nested_path))

def test_config_invariants():
    """Verifica que no reaparezcan rutas legacy en archivos críticos."""
    import subprocess
    critical_files = [
        "dummie_agent_config.json",
        "scripts/factory_up.sh",
        "layers/l1_nervous/mcp_server.py",
        "layers/l1_nervous/cmd/diag_kuzu/main.go"
    ]
    for f in critical_files:
        path = ROOT.parent.parent / f
        if not path.exists(): continue
        content = path.read_text()
        assert "kuzu_data" not in content, f"Legacy path 'kuzu_data' found in {f}"
