from semantic_ontology_mapper import map_semantic_ontology
def test_ontology_graph():
    res = map_semantic_ontology("refactor memory")
    graph = res["ontology_graph"]
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0
    assert any(e["type"] == "IS_A" for e in graph["edges"])
