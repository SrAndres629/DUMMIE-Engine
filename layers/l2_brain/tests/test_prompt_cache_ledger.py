import json
from pathlib import Path

from layers.l2_brain.context.prompt_cache_ledger import PromptCacheLedger


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _frame(frame_id: str = "frame-1", source_hash: str = "h1") -> dict:
    return {
        "frame_id": frame_id,
        "mission_id": "m1",
        "phase_id": "P14",
        "source_hash": source_hash,
        "receipt_ref": ".aiwg/reports/context_receipt_latest.json",
        "estimated_tokens": 120,
        "created_at": "2026-05-16T00:00:00Z",
    }


def test_prompt_cache_ledger_append_idempotent(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    ledger = PromptCacheLedger(aiwg_root=aiwg)

    first = ledger.record_frame(_frame())
    second = ledger.record_frame(_frame())

    assert first.frame_id == second.frame_id
    entries = ledger._load_entries()
    assert len(entries) == 1


def test_prompt_cache_ledger_find_reusable_and_invalidate_source_hash(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    ledger = PromptCacheLedger(aiwg_root=aiwg)
    ledger.record_frame(_frame(frame_id="frame-1", source_hash="same"))

    _write_json(aiwg / "reports" / "stale_memory_report.json", {"generated_at": "2026-05-15T00:00:00Z", "findings": []})

    reusable = ledger.find_reusable_frame(
        mission_id="m1",
        phase_id="P14",
        source_hash="same",
        receipt_ref=".aiwg/reports/context_receipt_latest.json",
        freshness_status="fresh",
        stale_report_path=aiwg / "reports" / "stale_memory_report.json",
    )
    assert reusable is not None

    not_reusable = ledger.find_reusable_frame(
        mission_id="m1",
        phase_id="P14",
        source_hash="different",
        receipt_ref=".aiwg/reports/context_receipt_latest.json",
        freshness_status="fresh",
        stale_report_path=aiwg / "reports" / "stale_memory_report.json",
    )
    assert not_reusable is None


def test_prompt_cache_ledger_summary_has_cache_hit_ratio(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    ledger = PromptCacheLedger(aiwg_root=aiwg)
    ledger.record_frame(_frame(frame_id="frame-a", source_hash="h1"))
    ledger.record_frame(_frame(frame_id="frame-b", source_hash="h2"))

    _write_json(aiwg / "reports" / "stale_memory_report.json", {"generated_at": "2026-05-15T00:00:00Z", "findings": []})

    summary = ledger.summarize_cache(
        mission_id="m1",
        phase_id="P14",
        source_hash="h1",
        receipt_ref=".aiwg/reports/context_receipt_latest.json",
        freshness_status="fresh",
        stale_report_path=aiwg / "reports" / "stale_memory_report.json",
        write_report=True,
    )
    assert 0.0 <= summary["cache_hit_ratio"] <= 1.0
    assert (aiwg / "reports" / "prompt_cache_summary_latest.json").exists()
