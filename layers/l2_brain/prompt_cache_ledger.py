from __future__ import annotations

import json
import os
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore


@dataclass
class PromptCacheEntry:
    entry_id: str
    frame_id: str
    mission_id: str
    phase_id: str
    source_hash: str
    receipt_ref: str
    estimated_tokens: int
    created_at: str
    invalidated: bool = False
    invalidation_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PromptCacheLedger:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.cache_root = self.aiwg_root / "prompt_cache"
        self.ledger_path = self.cache_root / "prompt_cache_ledger.jsonl"
        self.reports_root = self.aiwg_root / "reports"

    def record_frame(self, frame: Any) -> PromptCacheEntry:
        frame_dict = self._as_dict(frame)
        frame_id = str(frame_dict.get("frame_id", ""))
        if not frame_id:
            raise ValueError("frame_id is required")

        self.cache_root.mkdir(parents=True, exist_ok=True)

        existing = self._find_by_frame_id(frame_id)
        if existing:
            return existing

        entry = PromptCacheEntry(
            entry_id=f"pce-{uuid.uuid4().hex[:12]}",
            frame_id=frame_id,
            mission_id=str(frame_dict.get("mission_id", "")),
            phase_id=str(frame_dict.get("phase_id", "")),
            source_hash=str(frame_dict.get("source_hash", "")),
            receipt_ref=str(frame_dict.get("receipt_ref", "")),
            estimated_tokens=int(frame_dict.get("estimated_tokens", 0) or 0),
            created_at=str(frame_dict.get("created_at", self._utc_now())),
        )

        with self._locked_file(self.ledger_path, mode="a+") as handle:
            handle.seek(0)
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if row.get("frame_id") == frame_id:
                    return PromptCacheEntry(**row)
            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(entry.to_dict(), ensure_ascii=True, sort_keys=True) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass

        return entry

    def find_reusable_frame(
        self,
        *,
        mission_id: str,
        phase_id: str,
        source_hash: str,
        receipt_ref: str,
        freshness_status: str,
        stale_report_path: str | Path = ".aiwg/reports/stale_memory_report.json",
    ) -> PromptCacheEntry | None:
        stale_report = self._load_json(Path(stale_report_path))
        stale_generated_at = str(stale_report.get("generated_at", ""))

        entries = self._load_entries()
        for entry in reversed(entries):
            if entry.mission_id != mission_id:
                continue
            reasons = self._invalidation_reasons(
                entry=entry,
                phase_id=phase_id,
                source_hash=source_hash,
                receipt_ref=receipt_ref,
                freshness_status=freshness_status,
                stale_generated_at=stale_generated_at,
            )
            if not reasons:
                return entry
        return None

    def summarize_cache(
        self,
        *,
        mission_id: str = "",
        phase_id: str = "",
        source_hash: str = "",
        receipt_ref: str = "",
        freshness_status: str = "fresh",
        stale_report_path: str | Path = ".aiwg/reports/stale_memory_report.json",
        write_report: bool = True,
    ) -> dict[str, Any]:
        stale_report = self._load_json(Path(stale_report_path))
        stale_generated_at = str(stale_report.get("generated_at", ""))

        entries = self._load_entries()
        total = len(entries)
        reusable = 0
        invalidated = 0
        estimated_tokens_saved = 0

        details = []
        for entry in entries:
            reasons = self._invalidation_reasons(
                entry=entry,
                phase_id=phase_id or entry.phase_id,
                source_hash=source_hash or entry.source_hash,
                receipt_ref=receipt_ref or entry.receipt_ref,
                freshness_status=freshness_status,
                stale_generated_at=stale_generated_at,
            )
            is_reusable = len(reasons) == 0
            if mission_id and entry.mission_id != mission_id:
                continue
            if is_reusable:
                reusable += 1
                estimated_tokens_saved += max(0, entry.estimated_tokens)
            else:
                invalidated += 1
            details.append(
                {
                    "frame_id": entry.frame_id,
                    "phase_id": entry.phase_id,
                    "reusable": is_reusable,
                    "invalidation_reasons": reasons,
                }
            )

        total_scoped = len(details)
        cache_hit_ratio = reusable / total_scoped if total_scoped else 0.0
        summary = {
            "total_frames": total_scoped,
            "reusable_frames": reusable,
            "invalidated_frames": invalidated,
            "estimated_tokens_saved": estimated_tokens_saved,
            "cache_hit_ratio": round(cache_hit_ratio, 6),
            "entries": details,
            "generated_at": self._utc_now(),
        }

        if write_report:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            out = self.reports_root / "prompt_cache_summary_latest.json"
            out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        return summary

    def _invalidation_reasons(
        self,
        *,
        entry: PromptCacheEntry,
        phase_id: str,
        source_hash: str,
        receipt_ref: str,
        freshness_status: str,
        stale_generated_at: str,
    ) -> list[str]:
        reasons: list[str] = []
        if entry.phase_id != phase_id:
            reasons.append("phase_id_mismatch")
        if entry.source_hash != source_hash:
            reasons.append("source_hash_mismatch")
        if entry.receipt_ref != receipt_ref:
            reasons.append("context_receipt_mismatch")
        if freshness_status != "fresh":
            reasons.append("freshness_drift")
        if stale_generated_at and entry.created_at and stale_generated_at > entry.created_at:
            reasons.append("stale_memory_report_newer_than_frame")
        return reasons

    def _load_entries(self) -> list[PromptCacheEntry]:
        if not self.ledger_path.exists():
            return []
        entries: list[PromptCacheEntry] = []
        with self._locked_file(self.ledger_path, mode="r") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    entries.append(PromptCacheEntry(**row))
        return entries

    def _find_by_frame_id(self, frame_id: str) -> PromptCacheEntry | None:
        for entry in self._load_entries():
            if entry.frame_id == frame_id:
                return entry
        return None

    def _as_dict(self, frame: Any) -> dict[str, Any]:
        if isinstance(frame, dict):
            return frame
        if hasattr(frame, "to_dict"):
            return frame.to_dict()
        raise TypeError("frame must be dict-like or expose to_dict()")

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @contextmanager
    def _locked_file(self, path: Path, mode: str = "a+") -> Generator[Any, None, None]:
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "r" and not path.exists():
            path.touch()
        with path.open(mode, encoding="utf-8") as handle:
            if fcntl:
                lock = fcntl.LOCK_EX if any(ch in mode for ch in ("w", "a", "+")) else fcntl.LOCK_SH
                try:
                    fcntl.flock(handle, lock)
                    yield handle
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
            else:
                yield handle

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
