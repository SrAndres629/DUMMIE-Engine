from dataclasses import asdict
from enum import Enum
from pathlib import Path

from layers.l1_nervous.domain import models as l1_models
from layers.l2_brain import l2_memory_models as l2_models


def _wire_dict(value):
    return {
        key: item.value if isinstance(item, Enum) else item
        for key, item in asdict(value).items()
    }


def test_l1_domain_models_reexport_l2_model_contracts():
    assert l1_models.AuthorityLevel is l2_models.AuthorityLevel
    assert l1_models.IntentType is l2_models.IntentType
    assert l1_models.AgentIntent is l2_models.AgentIntent
    assert l1_models.SixDimensionalContext is l2_models.SixDimensionalContext


def test_l1_agent_intent_serializes_l2_enum_values():
    intent = l1_models.AgentIntent(
        goal="align model contracts",
        agent_id="phase3-test",
        authority_a=l1_models.AuthorityLevel.ARCHITECT,
        intent_i=l1_models.IntentType.MUTATION,
    )

    payload = _wire_dict(intent)

    assert payload["authority_a"] == "ARCHITECT"
    assert payload["intent_i"] == "MUTATION"
    assert payload["goal"] == "align model contracts"


def test_l1_domain_bridge_does_not_define_duplicate_contract_classes():
    source = Path(l1_models.__file__).read_text(encoding="utf-8")

    for contract_name in ("AuthorityLevel", "IntentType", "AgentIntent"):
        assert f"class {contract_name}" not in source
    assert "layers.l2_brain.models" in source
    assert "from models import" not in source
