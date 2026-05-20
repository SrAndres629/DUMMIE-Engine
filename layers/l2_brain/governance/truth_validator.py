from __future__ import annotations

import re
from typing import Any, Dict, List, NamedTuple


class ValidationVerdict(NamedTuple):
    admitted: bool
    effective_rank: int
    reason: str
    demotions: List[str]
    bonuses: List[str]


class DummieTruthValidator:
    """
    [L2_BRAIN] Truth Hierarchy and Canonicality Policy Validator (Spec 108).
    Evaluates claims and artifacts to resolve truth precedence.
    """

    BASE_RANKS = {
        "code_passing_tests": 100,
        "passing_tests": 95,
        "active_specs": 90,
        "schemas": 85,
        "phase_ledger": 80,
        "daemon_outcome": 75,
        "learning_episode": 70,
        "vault_entry": 65,
        "active_cognitive_artifact": 60,
        "report_evidence": 50,
        "note_freshness": 40,
        "human_mirror": 30,
        "chat_transcript": 20,
        "unknown_legacy": 10,
        "deprecated": 0,
    }

    @classmethod
    def evaluate_artifact(
        cls,
        source_type: str,
        metadata: Dict[str, Any],
        content: str = "",
    ) -> ValidationVerdict:
        """
        Calculates effective truth rank and decides if an artifact is safe to enter
        high-confidence reasoning contexts.
        """
        # 1. Security Rejection Gate (Hard Zero)
        # Check for secrets/keys
        if any(
            key in content.lower()
            for key in ["api_key", "private_key", "password", "secret_token", "client_secret"]
        ) and any(
            re.search(r"['\"=]\s*[a-zA-Z0-9_\-]{16,}", content) for _ in [1]
        ):
            return ValidationVerdict(
                admitted=False,
                effective_rank=0,
                reason="Hard Zero: Secrets or private credentials detected in content.",
                demotions=["secret_detected"],
                bonuses=[],
            )

        # Check for deprecated lifecycle status
        if metadata.get("lifecycle_state") in ["deprecated", "rejected"]:
            return ValidationVerdict(
                admitted=False,
                effective_rank=0,
                reason="Hard Zero: Lifecycle state is deprecated or rejected.",
                demotions=["lifecycle_deprecated"],
                bonuses=[],
            )

        # 2. Base Rank Resolution
        base_rank = cls.BASE_RANKS.get(source_type, 10)
        bonuses = []
        demotions = []
        evidence_bonus = 0
        staleness_penalty = 0
        risk_penalty = 0

        # 3. Evidence Bonuses
        if metadata.get("passing_tests"):
            evidence_bonus += 5
            bonuses.append("passing_tests (+5)")
        if metadata.get("schema_validated"):
            evidence_bonus += 3
            bonuses.append("schema_validated (+3)")
        if metadata.get("has_evidence_refs"):
            evidence_bonus += 3
            bonuses.append("has_evidence_refs (+3)")
        if metadata.get("runtime_owned"):
            evidence_bonus += 2
            bonuses.append("runtime_owned (+2)")

        # 4. Staleness Penalties
        if metadata.get("stale"):
            staleness_penalty += 30
            demotions.append("stale (-30)")
        if metadata.get("unknown_freshness"):
            staleness_penalty += 15
            demotions.append("unknown_freshness (-15)")
        if metadata.get("linked_test_failed"):
            staleness_penalty += 40
            demotions.append("linked_test_failed (-40)")
        if metadata.get("source_hash_changed"):
            staleness_penalty += 30
            demotions.append("source_hash_changed (-30)")

        # 5. Risk Penalties
        if metadata.get("duplicate_truth_detected"):
            risk_penalty += 10
            demotions.append("duplicate_truth_detected (-10)")
        if metadata.get("missing_owner_runtime"):
            risk_penalty += 10
            demotions.append("missing_owner_runtime (-10)")
        if metadata.get("weak_or_no_evidence"):
            risk_penalty += 10
            demotions.append("weak_or_no_evidence (-10)")
        if metadata.get("legacy_unknown"):
            risk_penalty += 20
            demotions.append("legacy_unknown (-20)")

        # Effective rank math
        effective_rank = base_rank + evidence_bonus - staleness_penalty - risk_penalty
        effective_rank = max(0, effective_rank)

        # 6. Admission Criteria
        admitted = True
        reason = "Artifact admitted to cognitive context."

        # High-confidence gate
        if metadata.get("high_confidence_context_required") and (
            effective_rank < 60 or metadata.get("unknown_freshness")
        ):
            admitted = False
            reason = (
                f"Rejected: Effective rank ({effective_rank}) is too low or has unknown freshness "
                "for a high-confidence context."
            )

        return ValidationVerdict(
            admitted=admitted,
            effective_rank=effective_rank,
            reason=reason,
            demotions=demotions,
            bonuses=bonuses,
        )
