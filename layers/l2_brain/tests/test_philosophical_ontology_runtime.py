from philosophical_ontology_runtime import build_philosophical_ontology
def test_philosophical_dimensions():
    res = build_philosophical_ontology("test")
    assert "Teleology" in res.dimensions
    assert any(n["id"] == "KUZU" for n in res.nodes)
