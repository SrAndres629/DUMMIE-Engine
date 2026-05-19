# Spec: 147_memory_spine_entrypoint
# Spec: DE-V2-L2-147
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Flexible import for SessionStore — supports both direct execution and package import
try:
    from layers.l2_brain.session_store import SessionStore
except ImportError:
    try:
        from session_store import SessionStore
    except ImportError:
        SessionStore = None  # type: ignore[assignment,misc]


@dataclass
class MemorySpineQuery:
    intent: str
    keywords: list[str] = field(default_factory=list)
    max_results: int = 20


@dataclass
class MemorySpineRetrievalResult:
    decision: str
    query: str
    status: str
    memory_refs: list[dict[str, Any]] = field(default_factory=list)
    learning_episode_refs: list[str] = field(default_factory=list)
    vault_refs: list[str] = field(default_factory=list)
    graph_status: str = "UNKNOWN"
    used_before_chat_response: bool = False
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MemorySpineEntrypoint:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"
        self._session_store: Any = None
        if SessionStore is not None:
            try:
                self._session_store = SessionStore(self.repo_root)
            except Exception:
                pass

    def retrieve_memory_for_intent(self, intent: str) -> MemorySpineRetrievalResult:
        warnings: list[str] = []
        status = "READY"
        graph_status = "UNKNOWN"

        # Check Kuzu status via reports
        sync_report_path = self.reports_root / "memory_spine_sync_latest.json"
        if sync_report_path.exists():
            try:
                sync_data = json.loads(sync_report_path.read_text(encoding="utf-8"))
                graph_status = sync_data.get("db_status", "UNKNOWN")
            except Exception:
                pass

        if graph_status == "DEGRADED":
            status = "DEGRADED_WITH_FILE_BACKED_MEMORY"
            warnings.append("Kuzu DEGRADED. Falling back to file-backed session memory scan.")

        # Build keyword set
        keywords = set(intent.lower().split())

        # File-backed memory scan: Learning Episodes
        memory_refs: list[dict[str, Any]] = []
        learning_episode_refs: list[str] = []
        evidence_refs: list[str] = []

        if self._session_store is not None:
            try:
                sessions = self._session_store.list_sessions()
                for session in sessions:
                    sid = session.get("session_id", "")
                    if not sid:
                        continue
                    for ep in self._session_store.iter_learning_episodes(sid):
                        # Join all relevant fields for keyword scanning
                        searchable_fields = [
                            ep.get("mission_id", ""),
                            ep.get("outcome", ""),
                            ep.get("query", ""),
                            ep.get("intent", ""),
                            ep.get("answer", "")
                        ]
                        ep_text = " ".join(searchable_fields).lower()
                        if any(kw in ep_text for kw in keywords):

                            learning_episode_refs.append(f"sid:{sid}/ep:{ep.get('episode_id')}")
                            evidence_refs.append(f".aiwg/sessions/{sid}/learning_episodes.jsonl")
            except Exception as exc:
                warnings.append(f"Session store scan failed: {exc}")

        # Vault scan: look for relevant vault entries
        vault_refs: list[str] = []
        vault_dir = self.aiwg_root / "vault"
        if vault_dir.exists():
            try:
                for vf in sorted(vault_dir.iterdir()):
                    if vf.is_file() and vf.suffix == ".json":
                        try:
                            vault_data = json.loads(vf.read_text(encoding="utf-8"))
                            vault_text = json.dumps(vault_data).lower()
                            if any(kw in vault_text for kw in keywords):
                                vault_refs.append(f".aiwg/vault/{vf.name}")
                        except Exception:
                            continue
            except Exception:
                pass

        # Report-based memory: scan key reports for relevant context
        report_sources = [
            "plan_v1_completion_review.json",
            "technical_debt_intelligence_latest.json",
            "memory_spine_sync_latest.json",
        ]
        for src in report_sources:
            rp = self.reports_root / src
            if rp.exists():
                try:
                    rdata = json.loads(rp.read_text(encoding="utf-8"))
                    rtext = json.dumps(rdata).lower()
                    if any(kw in rtext for kw in keywords):
                        memory_refs.append({"source": f".aiwg/reports/{src}", "match_type": "keyword"})
                        evidence_refs.append(f".aiwg/reports/{src}")
                except Exception:
                    continue

        result = MemorySpineRetrievalResult(
            decision="PASS" if not warnings else "PASS_WITH_WARNINGS",
            query=intent,
            status=status,
            memory_refs=memory_refs,
            learning_episode_refs=learning_episode_refs,
            vault_refs=vault_refs,
            graph_status=graph_status,
            used_before_chat_response=True,
            warnings=warnings,
            evidence_refs=list(set(evidence_refs)),
            generated_at=self._utc_now()
        )

        self._save_report(result)
        return result

    def _save_report(self, result: MemorySpineRetrievalResult) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "memory_spine_entrypoint_latest.json").write_text(
            json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
        )

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def retrieve_memory_for_intent(intent: str, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> MemorySpineRetrievalResult:
    entrypoint = MemorySpineEntrypoint(repo_root=repo_root, aiwg_root=aiwg_root)
    return entrypoint.retrieve_memory_for_intent(intent)


def run_memory_spine_entrypoint_demo(intent: str, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> MemorySpineRetrievalResult:
    return retrieve_memory_for_intent(intent, repo_root=repo_root, aiwg_root=aiwg_root)


if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = run_memory_spine_entrypoint_demo(intent)
    print(json.dumps(result.to_dict(), indent=2))
