from pathlib import Path

from layers.l2_brain.context.prompt_frame_builder import PromptFrameBuilder


def test_prompt_frame_passes_session_role_to_quant_runtime(monkeypatch, tmp_path: Path):
    captured = {}

    class FakeResult:
        selected_items = []
        kept_refs = []
        compressed_refs = []
        dropped_refs = []
        budget_limit = 100
        estimated_total_tokens = 10

    def fake_build(
        self,
        mission_id,
        phase,
        session_role=None,
        budget_limit=None,
        model_tier="local_fast",
        write_outputs=True,
    ):
        captured["session_role"] = session_role
        return FakeResult()

    monkeypatch.setattr(
        "layers.l2_brain.context.context_quant_runtime.ContextQuantRuntime.build_context_for_phase",
        fake_build,
    )

    b = PromptFrameBuilder(aiwg_root=tmp_path / ".aiwg")
    (tmp_path / ".aiwg" / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".aiwg" / "reports" / "context_package_latest.json").write_text(
        "{}", encoding="utf-8"
    )
    (tmp_path / ".aiwg" / "reports" / "context_receipt_latest.json").write_text(
        "{}", encoding="utf-8"
    )
    (tmp_path / ".aiwg" / "reports" / "stale_memory_report.json").write_text(
        "{}", encoding="utf-8"
    )

    b.build_prompt_frame_for_phase(
        "m1", "P10", session_role="planner", write_output=False
    )
    assert captured["session_role"] == "planner"
