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


def test_mutating_remote_tool_auto_admits_when_repo_spec_covers_path(tmp_path):
    spec_dir = tmp_path / "doc" / "specs"
    spec_dir.mkdir(parents=True)
    (spec_dir / "22_sdd_executable_contracts.md").write_text(
        """---
spec_id: "DE-V2-L3-22"
status: "ACTIVE"
---
# SDD

## Physical Evidence
- `layers/l2_brain`
"""
    )

    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={"path": "layers/l2_brain/models.py", "content": "x"},
        repo_root=str(tmp_path),
    )

    assert decision.status == "ALLOW"
    assert decision.reason == "auto_sdd_admission"


def test_mutating_remote_tool_auto_admits_stable_spec(tmp_path):
    spec_dir = tmp_path / "doc" / "specs"
    spec_dir.mkdir(parents=True)
    (spec_dir / "02_memory_engine_4d_tes.md").write_text(
        """---
status: "STABLE"
---
# Memory Engine

## Physical Evidence
- `layers/l2_brain`
"""
    )

    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={"path": "layers/l2_brain/models.py", "content": "x"},
        repo_root=str(tmp_path),
    )

    assert decision.status == "ALLOW"


def test_auto_admission_rejects_path_traversal_outside_covered_spec(tmp_path):
    spec_dir = tmp_path / "doc" / "specs"
    spec_dir.mkdir(parents=True)
    (spec_dir / "22_sdd_executable_contracts.md").write_text(
        """---
status: "ACTIVE"
---
# SDD

## Physical Evidence
- `layers/l2_brain`
"""
    )

    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={"path": "layers/l2_brain/../../layers/l1_nervous/mcp_proxy.py", "content": "x"},
        repo_root=str(tmp_path),
    )

    assert decision.status == "BLOCK"


def test_auto_admission_rejects_absolute_path_outside_repo(tmp_path):
    spec_dir = tmp_path / "doc" / "specs"
    spec_dir.mkdir(parents=True)
    (spec_dir / "22_sdd_executable_contracts.md").write_text(
        """---
status: "ACTIVE"
---
# SDD

## Physical Evidence
- `layers/l2_brain`
"""
    )

    decision = evaluate_remote_tool_admission(
        server_name="filesystem",
        tool_name="write_file",
        arguments={"path": "/etc/passwd", "content": "x"},
        repo_root=str(tmp_path),
    )

    assert decision.status == "BLOCK"


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
