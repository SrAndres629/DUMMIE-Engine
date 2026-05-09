import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from knowledge_policy import evaluate_knowledge_operation


def test_read_operations_are_allowed():
    assert evaluate_knowledge_operation("obsidian_get_file_contents").decision == "ALLOWED"
    assert evaluate_knowledge_operation("obsidian_simple_search").decision == "ALLOWED"


def test_append_requires_sovereign_wrapper():
    assert (
        evaluate_knowledge_operation(
            "obsidian_append_content",
            wrapper="knowledge_export_decision_summary",
        ).decision
        == "L3_AUTO_APPEND"
    )
    assert evaluate_knowledge_operation("obsidian_append_content").decision == "DENY"


def test_destructive_operations_require_intervention():
    assert evaluate_knowledge_operation("obsidian_patch_content").decision == "L3_INTERVENTION_REQUIRED"
    assert evaluate_knowledge_operation("obsidian_put_content").decision == "L3_INTERVENTION_REQUIRED"
    assert evaluate_knowledge_operation("obsidian_delete_file").decision == "L3_INTERVENTION_REQUIRED"
