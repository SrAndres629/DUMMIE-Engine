import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest

from capability_index import CapabilityIndex
from dummie_sdk.routing.strategies.exact_match import ExactMatchStrategy
from intelligent_intent_router import IntentClassifier


def test_capability_index_classifies_n8n_servers_and_tools_as_workflow_automation():
    index = CapabilityIndex()

    index.add_mcp_server_config(
        "n8n-api",
        "automation",
        "workflow_automation",
        "n8n workflows, webhooks, nodes and automations",
    )
    index.add_mcp_tools(
        "n8n-api",
        [{"name": "search_workflows", "description": "List workflows and webhooks"}],
    )

    automation_entries = index._capabilities.get("workflow_automation", [])

    assert any(entry["id"] == "remote.n8n-api" for entry in automation_entries)
    assert any(
        entry["id"] == "n8n-api.search_workflows" for entry in automation_entries
    )


@pytest.mark.asyncio
async def test_exact_match_routes_n8n_workflow_query_to_automation_domain():
    result = await ExactMatchStrategy().execute(
        "crear workflow en n8n con webhook y automatizar ejecuciones"
    )

    assert result.match is True
    assert result.domain == "automation"
    assert result.action == "workflow"
    assert result.gateway == "shell"


def test_intent_classifier_recognizes_n8n_workflow_queries():
    intent = IntentClassifier().classify(
        "crear workflow en n8n con webhook y automatizar ejecuciones"
    )

    assert intent.domain == "automation"
    assert intent.action == "workflow"
    assert intent.confidence >= 0.5
