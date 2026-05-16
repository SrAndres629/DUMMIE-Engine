from semantic_ontology_mapper import map_semantic_ontology
def test_map_ontology():
    res = map_semantic_ontology("refactor memory")
    assert "DEBT" in res["classes"]
    assert "MEMORY" in res["classes"]
