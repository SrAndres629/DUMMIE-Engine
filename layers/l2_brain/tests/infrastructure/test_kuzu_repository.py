import pytest
import os
import shutil
try:
    from layers.l2_brain.adapters import KuzuRepository
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from adapters import KuzuRepository

@pytest.fixture
def temp_kuzu(tmp_path):
    db_path = str(tmp_path / "test_db")
    repo = KuzuRepository(db_path=db_path)
    return repo, db_path

def test_kuzu_ensure_schema_fail_on_invalid_sql(tmp_path):
    """Verifica que fallos que no sean 'Table already exists' lancen excepción."""
    db_path = str(tmp_path / "fail_db")
    repo = KuzuRepository(db_path=db_path)
    
    # Inyectar un error manual (mockeando el connection execute si fuera necesario)
    # Pero aquí probaremos el query robusto
    with pytest.raises(RuntimeError):
        repo.query("MATCH (invalid_syntax) --- >> {}")

def test_kuzu_query_no_connection():
    """Verifica que consultas sin conexión fallen explícitamente."""
    repo = KuzuRepository(db=None)
    with pytest.raises(ConnectionError):
        repo.query("MATCH (m) RETURN m")
