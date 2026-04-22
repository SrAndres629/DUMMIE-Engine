"""
Test: MCP Server for DUMMIE Engine 4D-TES Memory
=================================================
Validates that the MCP server tools correctly wrap the hexagonal ports
and that the causal memory engine operates deterministically through
the MCP interface.
"""
import pytest
import os
import shutil
import json
import uuid

# Direct import of the MCP tools (testing the functions, not the MCP transport)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(autouse=True)
def clean_mcp_env(tmp_path):
    """
    Fixture that redirects the MCP server to use temporary database paths,
    preventing contamination of the production memory.
    """
    uid = uuid.uuid4().hex[:8]
    db_path = str(tmp_path / f"test_mcp_{uid}.db")
    ledger_path = str(tmp_path / f"test_decisions_{uid}.jsonl")

    # Set environment before imports
    os.environ["DUMMIE_MEMORY_DB_PATH"] = db_path
    os.environ["DUMMIE_LEDGER_PATH"] = ledger_path

    # Reset the lazy singletons (force re-initialization with new paths)
    import brain.mcp_server as mcp_mod
    mcp_mod._kuzu_repo = None
    mcp_mod._skill_repo = None
    mcp_mod._ledger_adapter = None
    mcp_mod._orchestrator = None
    mcp_mod.DB_PATH = db_path
    mcp_mod.LEDGER_PATH = ledger_path

    yield {
        "db_path": db_path,
        "ledger_path": ledger_path,
    }

    # Cleanup
    try:
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        if os.path.exists(ledger_path):
            os.remove(ledger_path)
    except Exception:
        pass


class TestMCPMemoryAppend:
    """Tests for the memory_append MCP tool."""

    def test_append_first_node(self):
        """First node should chain from GENESIS."""
        from brain.mcp_server import memory_append

        result = json.loads(memory_append(
            payload_json='{"observation": "Hello World"}',
            locus_x="test.mcp",
            intent="OBSERVATION",
        ))

        assert result["success"] is True
        assert result["parent_hash"] == "GENESIS"
        assert result["lamport_t"] == 1
        assert result["locus_x"] == "test.mcp"
        assert len(result["causal_hash"]) == 64

    def test_append_chains_causally(self):
        """Sequential appends must form a Merkle-DAG chain."""
        from brain.mcp_server import memory_append

        r1 = json.loads(memory_append(
            payload_json='{"step": 1}',
            locus_x="test.chain",
        ))
        r2 = json.loads(memory_append(
            payload_json='{"step": 2}',
            locus_x="test.chain",
        ))
        r3 = json.loads(memory_append(
            payload_json='{"step": 3}',
            locus_x="test.chain",
        ))

        assert r1["parent_hash"] == "GENESIS"
        assert r2["parent_hash"] == r1["causal_hash"]
        assert r3["parent_hash"] == r2["causal_hash"]
        assert r1["lamport_t"] == 1
        assert r2["lamport_t"] == 2
        assert r3["lamport_t"] == 3


class TestMCPMemoryRetrieval:
    """Tests for memory_get_node, memory_get_head, memory_get_chain."""

    def test_get_head_genesis(self):
        """Empty database should return GENESIS."""
        from brain.mcp_server import memory_get_head

        result = json.loads(memory_get_head())
        assert result["head_hash"] == "GENESIS"
        assert result["is_genesis"] is True

    def test_get_head_after_append(self):
        """Head should update after append."""
        from brain.mcp_server import memory_append, memory_get_head

        r1 = json.loads(memory_append(payload_json='{"test": true}'))
        head = json.loads(memory_get_head())

        assert head["head_hash"] == r1["causal_hash"]
        assert head["is_genesis"] is False

    def test_get_node_by_hash(self):
        """Retrieve a node by its causal hash."""
        from brain.mcp_server import memory_append, memory_get_node

        r1 = json.loads(memory_append(
            payload_json='{"data": "test_payload"}',
            locus_x="test.retrieval",
        ))

        node = json.loads(memory_get_node(r1["causal_hash"]))

        assert node["found"] is True
        assert node["causal_hash"] == r1["causal_hash"]
        assert "test_payload" in node["payload"]
        assert node["context"]["locus_x"] == "test.retrieval"

    def test_get_node_not_found(self):
        """Non-existent hash should return found=False."""
        from brain.mcp_server import memory_get_node

        result = json.loads(memory_get_node("nonexistent_hash_abc123"))
        assert result["found"] is False

    def test_get_chain(self):
        """Causal chain should reconstruct Merkle-DAG ancestry."""
        from brain.mcp_server import memory_append, memory_get_chain

        r1 = json.loads(memory_append(payload_json='{"n": 1}', locus_x="test.chain2"))
        r2 = json.loads(memory_append(payload_json='{"n": 2}', locus_x="test.chain2"))
        r3 = json.loads(memory_append(payload_json='{"n": 3}', locus_x="test.chain2"))

        chain = json.loads(memory_get_chain(r3["causal_hash"]))

        assert chain["chain_length"] == 3
        assert chain["nodes"][0]["causal_hash"] == r1["causal_hash"]
        assert chain["nodes"][1]["causal_hash"] == r2["causal_hash"]
        assert chain["nodes"][2]["causal_hash"] == r3["causal_hash"]


class TestMCPMemorySearch:
    """Tests for the memory_search MCP tool."""

    def test_search_by_locus(self):
        """Search should filter by bounded context."""
        from brain.mcp_server import memory_append, memory_search

        memory_append(payload_json='{"a": 1}', locus_x="domain.alpha")
        memory_append(payload_json='{"b": 2}', locus_x="domain.beta")
        memory_append(payload_json='{"c": 3}', locus_x="domain.alpha")

        result = json.loads(memory_search(locus_x="domain.alpha"))

        assert result["count"] == 2
        for n in result["nodes"]:
            assert n["locus_x"] == "domain.alpha"

    def test_search_empty_result(self):
        """Search with no matches should return empty."""
        from brain.mcp_server import memory_search

        result = json.loads(memory_search(locus_x="nonexistent"))
        assert result["count"] == 0


class TestMCPLedger:
    """Tests for the decision ledger MCP tools."""

    def test_record_and_certainty(self):
        """Record a decision and check certainty calculation."""
        from brain.mcp_server import ledger_record, ledger_get_certainty

        # Record a decision
        result = json.loads(ledger_record(
            decision_id="DEC-001",
            rationale="Test decision for MCP validation",
            locus_x="test.ledger",
        ))
        assert result["success"] is True

        # Check certainty
        certainty = json.loads(ledger_get_certainty("test.ledger"))
        assert certainty["locus_x"] == "test.ledger"
        assert certainty["certainty_score"] >= 0.0


class TestMCPSkills:
    """Tests for the skill management MCP tools."""

    def test_save_and_retrieve_skill(self):
        """Save a skill and retrieve it by ID."""
        from brain.mcp_server import memory_append, skill_save, skill_get

        # Create a source node first
        r1 = json.loads(memory_append(payload_json='{"learning": "pattern_x"}'))

        # Save skill with provenance
        save_result = json.loads(skill_save(
            skill_id="SKILL-MCP-TEST-001",
            yaml_payload="spec_id: SKILL-MCP-TEST-001\nstatus: ACTIVE",
            source_causal_hashes=json.dumps([r1["causal_hash"]]),
        ))
        assert save_result["success"] is True
        assert save_result["provenance_count"] == 1

        # Retrieve skill
        get_result = json.loads(skill_get("SKILL-MCP-TEST-001"))
        assert get_result["found"] is True
        assert get_result["skill_id"] == "SKILL-MCP-TEST-001"
        assert r1["causal_hash"] in get_result["source_causal_hashes"]

    def test_get_nonexistent_skill(self):
        """Non-existent skill should return found=False."""
        from brain.mcp_server import skill_get

        result = json.loads(skill_get("NONEXISTENT-SKILL"))
        assert result["found"] is False


class TestMCPBrainStatus:
    """Tests for the brain_status MCP tool."""

    def test_status_empty_engine(self):
        """Status of an empty engine."""
        from brain.mcp_server import brain_status

        status = json.loads(brain_status())

        assert status["engine"] == "DUMMIE Engine L2 Brain - 4D-TES Memory"
        assert status["is_genesis"] is True
        assert status["total_nodes"] == 0

    def test_status_after_operations(self):
        """Status should reflect inserted nodes."""
        from brain.mcp_server import memory_append, brain_status

        memory_append(payload_json='{"init": true}')
        memory_append(payload_json='{"second": true}')

        status = json.loads(brain_status())

        assert status["total_nodes"] == 2
        assert status["is_genesis"] is False
        assert status["head_info"]["lamport_t"] == 2


class TestMCPOrchestrator:
    """Tests for the brain_process_task MCP tool."""

    @pytest.mark.anyio
    async def test_process_task(self):
        """Full orchestrator cycle through MCP."""
        from brain.mcp_server import brain_process_task

        result = json.loads(await brain_process_task("MCP Integration Test: Alpha"))
        assert result["success"] is True
        assert result["status"] == "INTENT_QUEUED_L2_VALIDATED"
