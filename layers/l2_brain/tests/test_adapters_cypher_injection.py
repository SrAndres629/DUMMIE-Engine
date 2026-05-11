import pytest
import re

def test_query_fallback_no_injection():
    # Test the fix directly by invoking the logic in adapters
    from layers.l2_brain.adapters import KuzuRepository

    class DummyConn:
        def __init__(self):
            self.executed = None

        def execute(self, cypher, params=None):
            self.executed = (cypher, params)
            return self.executed

    # Mock KuzuRepository to bypass initialization
    class MockRepo(KuzuRepository):
        def __init__(self):
            self.conn = DummyConn()

        def _execute_supports_parameters(self):
            return False

    repo = MockRepo()
    cypher = "MATCH (n) WHERE n.name = $a AND n.role = $b RETURN n"
    parameters = {"a": "$b", "b": " OR true //"}

    repo.query(cypher, parameters)
    assert repo.conn.executed[0] == "MATCH (n) WHERE n.name = '$b' AND n.role = ' OR true //' RETURN n"

def test_query_fallback_overlapping_keys():
    from layers.l2_brain.adapters import KuzuRepository

    class DummyConn:
        def __init__(self):
            self.executed = None

        def execute(self, cypher, params=None):
            self.executed = (cypher, params)
            return self.executed

    class MockRepo(KuzuRepository):
        def __init__(self):
            self.conn = DummyConn()

        def _execute_supports_parameters(self):
            return False

    repo = MockRepo()
    cypher = "MATCH (n) WHERE n.id = $id AND n.id_long = $id_long RETURN n"
    parameters = {"id": 1, "id_long": 2}

    repo.query(cypher, parameters)
    assert repo.conn.executed[0] == "MATCH (n) WHERE n.id = 1 AND n.id_long = 2 RETURN n"

if __name__ == "__main__":
    pytest.main([__file__])
