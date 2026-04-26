import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sdd_remote_guard import evaluate_remote_tool_admission


def test_read_only_remote_tool_is_allowed_without_admission():
    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="read_file",
        arguments={"path": "README.md"},
    )

    assert decision.status == "ALLOW"


def test_mutating_remote_tool_is_blocked_without_sdd_admission():
    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={"path": "README.md", "content": "x"},
    )

    assert decision.status == "BLOCK"
    assert "sdd_admission" in decision.reason


def test_mutating_remote_tool_is_allowed_with_sdd_admission_allow():
    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={
            "path": "README.md",
            "content": "x",
            "sdd_admission": {"status": "ALLOW", "parent_spec_ids": ["spec-1"]},
        },
    )

    assert decision.status == "ALLOW"


def test_obsidian_append_requires_sdd_admission_when_called_directly():
    decision = evaluate_remote_tool_admission(
        server_name="obsidian",
        tool_name="obsidian_append_content",
        arguments={"filepath": "A.md", "content": "x"},
    )

    assert decision.status == "BLOCK"
