from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORBIDDEN_REF_PATTERNS = [
    re.compile(r"chain_of_thought", re.I),
    re.compile(r"private reasoning", re.I),
    re.compile(r"private_reasoning", re.I),
    re.compile(r"\.env\s*[=:]", re.I),
    re.compile(r"secret\s*(is|[:=])", re.I),
    re.compile(r"credential\s*(is|[:=])", re.I),
    re.compile(r"password\s*[=:]", re.I),
    re.compile(r"api[_-]?key\s*[=:]", re.I),
    re.compile(r"token\s*[=:]", re.I),
]


@dataclass
class FreshnessEntry:
    artifact_id: str
    artifact_type: str
    artifact_path: str
    source_hash: str
    hash_method: str
    freshness_status: str  # fresh|stale|unknown|missing
    last_verified: str
    invalidation_triggers: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class FreshnessLedger:
    generated_at: str
    aiwg_root: str
    entries: list[FreshnessEntry]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "aiwg_root": self.aiwg_root,
            "entries": [asdict(entry) for entry in self.entries],
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, int]:
        counts = {"fresh": 0, "stale": 0, "unknown": 0, "missing": 0}
        for entry in self.entries:
            counts[entry.freshness_status] = counts.get(entry.freshness_status, 0) + 1
        counts["total"] = len(self.entries)
        return counts



def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def _sanitize_evidence_refs(refs: list[str]) -> list[str]:
    clean: list[str] = []
    for ref in refs:
        text = str(ref)
        for pattern in FORBIDDEN_REF_PATTERNS:
            if pattern.search(text):
                raise ValueError(f"forbidden evidence ref: {text}")
        clean.append(text)
    return clean



def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()



def _folder_list_hash(repo_root: Path, folder_path: str, tracked_file_count: int) -> str:
    command = ["git", "ls-files", f"{folder_path}/**"]
    result = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    paths = sorted(line.strip() for line in result.stdout.splitlines() if line.strip())
    payload = "\n".join(paths) + f"\ncount:{tracked_file_count}\npath:{folder_path}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()



def _entry_from_file(
    artifact_id: str,
    artifact_type: str,
    relative_path: str,
    aiwg_root: Path,
    evidence_refs: list[str],
    invalidation_triggers: list[str] | None = None,
) -> FreshnessEntry:
    path = aiwg_root / relative_path
    if not path.exists():
        return FreshnessEntry(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            artifact_path=str(relative_path),
            source_hash="",
            hash_method="sha256(file_bytes)",
            freshness_status="missing",
            last_verified=_utc_now(),
            invalidation_triggers=invalidation_triggers or ["source_file_changed"],
            evidence_refs=_sanitize_evidence_refs(evidence_refs),
            risk_flags=["missing_artifact"],
        )

    return FreshnessEntry(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        artifact_path=str(relative_path),
        source_hash=_file_hash(path),
        hash_method="sha256(file_bytes)",
        freshness_status="fresh",
        last_verified=_utc_now(),
        invalidation_triggers=invalidation_triggers or ["source_file_changed"],
        evidence_refs=_sanitize_evidence_refs(evidence_refs),
        risk_flags=[],
    )



def build_freshness_ledger(
    aiwg_root: str | Path = ".aiwg",
    output_path: str | Path | None = None,
    write_report: bool = True,
) -> FreshnessLedger:
    aiwg_root_path = Path(aiwg_root)
    repo_root = aiwg_root_path.parent if aiwg_root_path.name == ".aiwg" else aiwg_root_path
    reports_root = aiwg_root_path / "reports"

    manifest_path = aiwg_root_path / "notes" / "folder_notes_manifest.json"
    world_model_rel = "world_model/project_world_model.json"
    coverage_rel = "reports/spec_coverage_matrix.json"

    entries: list[FreshnessEntry] = []

    entries.append(
        _entry_from_file(
            artifact_id="project_world_model",
            artifact_type="world_model",
            relative_path=world_model_rel,
            aiwg_root=aiwg_root_path,
            evidence_refs=[".aiwg/world_model/project_world_model.json"],
            invalidation_triggers=["source_file_changed", "phase_state_changed"],
        )
    )
    entries.append(
        _entry_from_file(
            artifact_id="spec_coverage_matrix",
            artifact_type="coverage_matrix",
            relative_path=coverage_rel,
            aiwg_root=aiwg_root_path,
            evidence_refs=[".aiwg/reports/spec_coverage_matrix.json"],
            invalidation_triggers=["source_file_changed", "spec_triplet_changed", "test_linkage_changed"],
        )
    )

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        folder_entries = manifest.get("folders", [])
        for folder in folder_entries:
            folder_id = folder.get("folder_id", "unknown_folder")
            note_path = str(folder.get("note_path", ""))
            noteplan_path = str(folder.get("noteplan_path", ""))
            folder_path = str(folder.get("folder_path", ""))
            expected_hash = str(folder.get("source_hash", ""))
            hash_method = str(folder.get("hash_method", "sha256(sorted_git_ls_files_plus_counts)"))
            tracked_count = int(folder.get("tracked_file_count", 0))
            freshness = folder.get("freshness", {}) if isinstance(folder.get("freshness"), dict) else {}
            requested_status = str(freshness.get("status", "unknown"))
            invalidation_triggers = list(freshness.get("invalidation_triggers", []))
            evidence_refs = [manifest_path.as_posix(), ".aiwg/reports/spec_coverage_matrix.json"]

            risks: list[str] = []
            note_exists = (repo_root / note_path).exists() if note_path else False
            noteplan_exists = (repo_root / noteplan_path).exists() if noteplan_path else False
            if not note_exists:
                risks.append("missing_note_path")
            if not noteplan_exists:
                risks.append("missing_noteplan_path")

            if not folder_path:
                status = "unknown"
                actual_hash = ""
                risks.append("missing_folder_path")
            else:
                folder_abs = repo_root / folder_path
                if not folder_abs.exists():
                    status = "missing"
                    actual_hash = ""
                    risks.append("missing_folder_path")
                else:
                    actual_hash = _folder_list_hash(repo_root, folder_path, tracked_count)
                    if requested_status == "unknown":
                        status = "unknown"
                    elif expected_hash and actual_hash != expected_hash:
                        status = "stale"
                        risks.append("folder_note_hash_mismatch")
                    elif requested_status == "stale":
                        status = "stale"
                    else:
                        status = "fresh"

            entry = FreshnessEntry(
                artifact_id=f"folder_note:{folder_id}",
                artifact_type="folder_note",
                artifact_path=note_path,
                source_hash=actual_hash if actual_hash else expected_hash,
                hash_method=hash_method,
                freshness_status=status,
                last_verified=_utc_now(),
                invalidation_triggers=invalidation_triggers or [
                    "source_file_changed",
                    "linked_spec_changed",
                    "linked_test_failed",
                    "coverage_matrix_changed",
                ],
                evidence_refs=_sanitize_evidence_refs(evidence_refs),
                risk_flags=sorted(set(risks + list(folder.get("risks", [])))),
            )
            entries.append(entry)
    else:
        entries.append(
            FreshnessEntry(
                artifact_id="folder_notes_manifest",
                artifact_type="folder_notes_manifest",
                artifact_path=".aiwg/notes/folder_notes_manifest.json",
                source_hash="",
                hash_method="sha256(file_bytes)",
                freshness_status="missing",
                last_verified=_utc_now(),
                invalidation_triggers=["source_file_changed"],
                evidence_refs=_sanitize_evidence_refs([".aiwg/notes/folder_notes_manifest.json"]),
                risk_flags=["missing_manifest"],
            )
        )

    ledger = FreshnessLedger(generated_at=_utc_now(), aiwg_root=str(aiwg_root_path), entries=entries)

    if write_report:
        output = Path(output_path) if output_path else reports_root / "freshness_ledger.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(ledger.to_dict(), indent=2) + "\n", encoding="utf-8")

    return ledger



def load_freshness_ledger(path: str | Path = ".aiwg/reports/freshness_ledger.json") -> FreshnessLedger:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = [FreshnessEntry(**item) for item in data.get("entries", [])]
    return FreshnessLedger(
        generated_at=str(data.get("generated_at", "")),
        aiwg_root=str(data.get("aiwg_root", ".aiwg")),
        entries=entries,
    )
