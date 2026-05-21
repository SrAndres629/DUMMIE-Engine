import json
from pathlib import Path

import pytest

from layers.l2_brain.context.local_context_compressor import CompressionInput, LocalContextCompressor


def test_local_context_compressor_preserves_required_items(tmp_path: Path):
    comp = LocalContextCompressor(aiwg_root=tmp_path / ".aiwg")
    items = [
        CompressionInput(
            ref="state:current",
            summary="critical state summary",
            token_role="summary_only",
            truth_rank=90,
            freshness_status="fresh",
            required=True,
            estimated_tokens=100,
            risk_flags=[],
        ),
        CompressionInput(
            ref="note:old",
            summary="stale optional",
            token_role="summary_only",
            truth_rank=30,
            freshness_status="stale",
            required=False,
            estimated_tokens=70,
            risk_flags=[],
        ),
    ]

    out = comp.compress_context_items(items)
    decisions = {x["ref"]: x["decision"] for x in out["items"]}

    assert decisions["state:current"] != "drop"
    assert decisions["note:old"] in {"drop", "compress"}
    assert 0.0 <= out["reduction_ratio"] <= 1.0


def test_local_context_compressor_rejects_secret_or_private_reasoning(tmp_path: Path):
    comp = LocalContextCompressor(aiwg_root=tmp_path / ".aiwg")
    bad = [
        CompressionInput(
            ref="note:1",
            summary="chain_of_thought internal",
            token_role="summary_only",
            truth_rank=40,
            freshness_status="fresh",
            required=False,
            estimated_tokens=20,
            risk_flags=[],
        )
    ]

    with pytest.raises(ValueError):
        comp.compress_context_items(bad)


def test_local_context_compression_json_roundtrip(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    (reports / "context_package_latest.json").write_text(
        json.dumps({"items": [{"ref": "x", "summary": "abc", "token_role": "summary_only", "truth_rank": 60, "freshness_status": "fresh", "required": False, "estimated_tokens": 20, "risk_flags": []}]}, indent=2),
        encoding="utf-8",
    )
    (reports / "prompt_frame_latest.json").write_text(
        json.dumps({"prompt_sections": {"system": ["system text"]}}, indent=2), encoding="utf-8"
    )

    comp = LocalContextCompressor(aiwg_root=aiwg)
    out = comp.compress_latest_context(write_output=True)

    assert (reports / "local_context_compression_latest.json").exists()
    data = json.loads((reports / "local_context_compression_latest.json").read_text(encoding="utf-8"))
    assert data["required_preserved"] is True
    assert data["input_estimated_tokens"] >= data["output_estimated_tokens"]
