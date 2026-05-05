import hashlib
import re
from datetime import UTC, datetime
from typing import Any


MANDATORY_PHASES = [
    "INTAKE",
    "GLOBAL_RECALL",
    "EPISTEMIC_CHECK",
    "PATTERN_MINING",
    "COLD_PLANNING",
    "RESEARCH_TREE",
    "SWARM_DEBATE",
    "PATCH_PLAN",
    "VALIDATION",
    "MEMORY_COMMIT",
    "NEXT_LOOP",
]


class PromptToMissionCompiler:
    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
        re.compile(r"\bdelete\s+\.git\b", re.IGNORECASE),
        re.compile(r"\bwipe\s+(the\s+)?(repo|repository|disk|project)\b", re.IGNORECASE),
        re.compile(r"\bdestroy\s+(the\s+)?(repo|repository|project)\b", re.IGNORECASE),
        re.compile(r"\bformat\s+(disk|drive)\b", re.IGNORECASE),
    ]

    def compile(self, mission_input: str | dict[str, Any], authority: str = "HUMAN") -> dict[str, Any]:
        prompt, authority_a = self._normalize_input(mission_input, authority)
        self._reject_destructive(prompt)

        now = datetime.now(UTC).isoformat()
        digest = hashlib.sha256(f"{now}:{authority_a}:{prompt}".encode("utf-8")).hexdigest()
        return {
            "mission_id": f"miss_{digest[:12]}",
            "goal": prompt,
            "authority_a": authority_a,
            "created_at": now,
            "constraints": [
                "Do not apply patches automatically.",
                "Plan changes before execution.",
                "Respect blocked paths and repository ownership boundaries.",
                "Persist validation and memory plans before next-loop handoff.",
            ],
            "forbidden_actions": [
                "apply_patch",
                "write_env_files",
                "edit_git_metadata",
                "edit_lockfiles",
                "write_generated_artifacts",
                "path_traversal",
                "destructive_shell_commands",
            ],
            "required_artifacts": [
                "intake.md",
                "global_recall.md",
                "epistemic_check.md",
                "cold_plan.md",
                "research_tree.md",
                "patch_plan.md",
                "validation_plan.md",
                "memory_commit.md",
                "next_loop.md",
            ],
            "agent_roles": [
                {"role": "intake", "responsibility": "Capture authority, goal, and constraints."},
                {"role": "epistemic_judge", "responsibility": "Separate evidence from assumptions."},
                {"role": "cold_planner", "responsibility": "Rank reversible, testable actions."},
                {"role": "validator", "responsibility": "Verify planned outcomes before memory commit."},
            ],
            "phases": list(MANDATORY_PHASES),
            "validation_plan": {
                "required": True,
                "commands": [],
                "evidence_required": ["test output", "changed files"],
            },
            "memory_plan": {
                "commit_required": True,
                "artifacts": ["memory_commit.md", "compact.md"],
            },
            "next_loop": {
                "enabled": True,
                "artifact": "next_loop.md",
                "requires_validation_first": True,
            },
        }

    def compile_from_pattern(self, pattern: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate a mission directly from a detected pattern (OpenClaw loop)."""
        pattern_name = pattern.get("name", "Unknown Pattern")
        hypothesis = pattern.get("hypothesis", "")
        proposed_rule = pattern.get("proposed_rule", "")
        recommended_action = pattern.get("recommended_action", "INVESTIGATE")
        
        prompt = (
            f"Address {pattern_name}. "
            f"Evidence shows: {hypothesis}. "
            f"Rule to enforce: {proposed_rule}. "
            f"Action needed: {recommended_action}."
        )
        
        # Delegate to compile() to ensure destructive checks
        mission = self.compile({"prompt": prompt, "authority_a": "SYSTEM_HEALER"})
        
        # Force strict gating for self-healing (No direct apply)
        mission["self_healing_safety_gates"] = {
            "apply_patch_enabled": False,
            "persona_guardian_required": True,
            "requires_human_approval": True,
            "coldplanner_metrics": pattern.get("coldplanner_metrics", {})
        }
        
        # Enrich the generated mission with pattern context
        mission["source_pattern_id"] = pattern.get("pattern_id")
        if context:
            mission["context_refs"] = context.get("evidence_refs", [])
            
        return mission

    def _normalize_input(self, mission_input: str | dict[str, Any], authority: str) -> tuple[str, str]:
        if isinstance(mission_input, dict):
            prompt = str(mission_input.get("prompt", "")).strip()
            authority_a = str(mission_input.get("authority_a", authority)).strip() or authority
        else:
            prompt = str(mission_input).strip()
            authority_a = authority
        if not prompt:
            raise ValueError("Mission prompt is required")
        return prompt, authority_a

    def _reject_destructive(self, prompt: str) -> None:
        for pattern in self.DESTRUCTIVE_PATTERNS:
            if pattern.search(prompt):
                raise ValueError("Destructive mission prompts are blocked")
