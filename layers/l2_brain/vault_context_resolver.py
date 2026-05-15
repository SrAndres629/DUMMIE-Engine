from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_FORBIDDEN_PATTERNS = [
    (re.compile(r"\.env\s*[=:]", re.I), "forbidden .env assignment"),
    (re.compile(r"secret\s*(is|[:=])", re.I), "forbidden secret value"),
    (re.compile(r"credential\s*(is|[:=])", re.I), "forbidden credential value"),
    (re.compile(r"token\s*[=:]", re.I), "forbidden token assignment"),
    (re.compile(r"password\s*[=:]", re.I), "forbidden password assignment"),
    (re.compile(r"chain_of_thought", re.I), "private reasoning"),
    (re.compile(r"private reasoning", re.I), "private reasoning"),
    (re.compile(r"private_reasoning", re.I), "private reasoning"),
]

class VaultContextResolver:
    """
    [L2_BRAIN] Resolves vault references into actual content and builds snippets.
    """
    def __init__(self, vault_curator: Any = None, vault_path: str | Path = ".aiwg/vault", compressor: Any = None):
        self.vault_curator = vault_curator
        self.vault_path = Path(vault_path)
        self.compressor = compressor

    def resolve_refs(self, vault_refs: list[str]) -> list[dict]:
        """
        Loads vault entries from disk based on vault_id list.
        """
        resolved = []
        for vref in vault_refs:
            # Normalize ID if it contains 'vault:' prefix
            vid = vref.replace("vault:", "") if vref.startswith("vault:") else vref
            entry_path = self.vault_path / f"{vid}.json"

            if entry_path.exists():
                try:
                    data = json.loads(entry_path.read_text(encoding="utf-8"))
                    self._reject_private(data)
                    resolved.append(data)
                except Exception as e:
                    logger.warning(f"Failed to resolve vault entry {vid}: {e}")
            else:
                logger.debug(f"Vault entry {vid} not found on disk at {entry_path}")
        return resolved

    def build_snippets(self, resolved_entries: list[dict], max_tokens: int = 4000) -> list[dict]:
        """
        Builds standardized snippets for prompt injection using token budget compression.
        """
        snippets = []
        for entry in resolved_entries:
            vid = entry.get("vault_id", "unknown")
            summary = entry.get("summary", "")

            # Build a structured snippet
            snippet_text = f"Vault ID: {vid}\nSummary: {summary}\n"

            evidence = entry.get("evidence_refs", [])
            if evidence:
                snippet_text += f"Evidence: {', '.join(evidence)}\n"

            reuse = entry.get("reuse_conditions", [])
            if reuse:
                snippet_text += f"Reuse Conditions: {', '.join(reuse)}\n"

            risks = entry.get("risk_notes", [])
            if risks:
                snippet_text += f"Risk Notes: {', '.join(risks)}\n"

            # Compress using semantic token budget
            if self.compressor:
                from layers.l2_brain.domain.embedding_contract import CompressionRequest
                req = CompressionRequest(raw_text=snippet_text, max_tokens=max_tokens)
                resp = self.compressor.compress(req)
                snippet_text = resp.compressed_text

            snippets.append({
                "vault_id": vid,
                "summary": summary,
                "evidence_refs": evidence,
                "reuse_conditions": reuse,
                "risk_notes": risks,
                "content_hash": entry.get("content_hash", ""),
                "snippet": snippet_text
            })
        return snippets

    def _reject_private(self, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._reject_private(str(key))
                self._reject_private(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._reject_private(item)
        elif isinstance(value, str):
            for pattern, reason in _FORBIDDEN_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"Resolved context contains {reason}")
