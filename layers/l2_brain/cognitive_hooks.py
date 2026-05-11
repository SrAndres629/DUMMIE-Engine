"""
[L2_BRAIN] Cognitive Hook Pipeline — first executable metacognition slice.

This module is intentionally deterministic. It creates auditable hook metadata
without depending on local/cloud LLM availability, so it can be used as the safe
pre-input surface for prompt preprocessing and model routing.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping


AUTHORITY_LEVELS = {"A0", "A1", "A2", "A3", "A4", "A5"}
REASONING_MODES = {"deterministic", "local_fast", "local_deep", "cloud_std", "cloud_prem"}


@dataclass
class CognitiveHookInput:
    message: str = ""
    session_id: str = ""
    mission_id: str = ""
    user_goal: str = ""
    available_context_refs: list[str] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    current_authority_level: str = "A0"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CognitiveHookInput":
        return cls(
            message=str(value.get("message", "")),
            session_id=str(value.get("session_id", "")),
            mission_id=str(value.get("mission_id", "")),
            user_goal=str(value.get("user_goal", "")),
            available_context_refs=_string_list(value.get("available_context_refs", [])),
            available_tools=_string_list(value.get("available_tools", [])),
            current_authority_level=str(value.get("current_authority_level", "A0")),
            metadata=dict(value.get("metadata", {}) or {}),
        )


@dataclass
class CognitiveHookPacket:
    sanitized_message: str = ""
    detected_intent: str = ""
    detected_language: str = ""
    affected_layers: list[str] = field(default_factory=list)
    authority_level: str = "A0"
    context_refs: list[str] = field(default_factory=list)
    tool_hints: list[str] = field(default_factory=list)
    token_budget_hint: int = 0
    risk_flags: list[str] = field(default_factory=list)
    reasoning_mode: str = "deterministic"
    external_reasoning_artifacts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    def to_router_metadata(self) -> dict[str, Any]:
        return {
            "authority_level": self.authority_level,
            "reasoning_mode": self.reasoning_mode,
            "affected_layers": list(self.affected_layers),
            "context_refs": list(self.context_refs),
            "tool_hints": list(self.tool_hints),
            "risk_flags": list(self.risk_flags),
            "token_budget_hint": self.token_budget_hint,
        }


class CognitiveHookPipeline:
    """Build a deterministic cognitive hook packet and apply optional hooks."""

    def __init__(self, pre_input_hooks: list[Callable[[CognitiveHookPacket], CognitiveHookPacket]] | None = None):
        self.pre_input_hooks = pre_input_hooks or []

    def run(self, hook_input: CognitiveHookInput | Mapping[str, Any]) -> CognitiveHookPacket:
        if isinstance(hook_input, Mapping):
            hook_input = CognitiveHookInput.from_mapping(hook_input)

        try:
            packet = build_cognitive_hook_packet(hook_input)
            for hook in self.pre_input_hooks:
                next_packet = hook(packet)
                if not isinstance(next_packet, CognitiveHookPacket):
                    raise TypeError(f"{hook!r} returned {type(next_packet).__name__}, expected CognitiveHookPacket")
                packet = next_packet
            return packet
        except Exception as exc:
            return build_fallback_packet(hook_input, exc)


def build_cognitive_hook_packet(hook_input: CognitiveHookInput) -> CognitiveHookPacket:
    started = time.perf_counter()
    sanitized = sanitize_message(hook_input.message)
    authority = classify_authority_level(sanitized, hook_input.current_authority_level)
    affected_layers = detect_affected_layers(sanitized)
    context_refs = _dedupe(_string_list(hook_input.available_context_refs) + affected_layers)
    risk_flags = _risk_flags_for_authority(authority)
    external_artifacts, rejected_private = sanitize_external_reasoning_artifacts(
        hook_input.metadata.get("external_reasoning_artifacts", [])
    )
    if rejected_private:
        risk_flags.append("private_reasoning_artifact_rejected")

    packet = CognitiveHookPacket(
        sanitized_message=sanitized,
        detected_intent=detect_intent(sanitized, authority),
        detected_language=detect_language(sanitized),
        affected_layers=affected_layers,
        authority_level=authority,
        context_refs=context_refs,
        tool_hints=discover_tool_hints(sanitized, authority, hook_input.available_tools),
        token_budget_hint=estimate_token_budget_hint(sanitized, context_refs),
        risk_flags=_dedupe(risk_flags),
        reasoning_mode=select_reasoning_mode(authority, sanitized, affected_layers),
        external_reasoning_artifacts=external_artifacts,
    )
    packet.external_reasoning_artifacts.insert(
        0,
        {
            "claim": "input classified by deterministic cognitive hooks",
            "evidence": (
                f"authority={packet.authority_level}; intent={packet.detected_intent}; "
                f"layers={','.join(packet.affected_layers) or 'none'}"
            ),
            "objection": "lexical classifiers can miss novel phrasing",
            "decision": "use packet as routing metadata with safe fallback",
            "required_test": "authority and fallback regression tests",
            "next_action": "route using hook metadata",
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        },
    )
    return packet


def build_fallback_packet(hook_input: CognitiveHookInput, error: Exception) -> CognitiveHookPacket:
    try:
        packet = build_cognitive_hook_packet(
            CognitiveHookInput(
                message=hook_input.message,
                session_id=hook_input.session_id,
                mission_id=hook_input.mission_id,
                user_goal=hook_input.user_goal,
                available_context_refs=hook_input.available_context_refs,
                available_tools=hook_input.available_tools,
                current_authority_level=hook_input.current_authority_level,
                metadata={},
            )
        )
    except Exception:
        sanitized = sanitize_message(getattr(hook_input, "message", ""))
        packet = CognitiveHookPacket(
            sanitized_message=sanitized,
            detected_intent="unknown",
            detected_language="en",
            authority_level=classify_authority_level(sanitized),
            reasoning_mode="deterministic",
        )

    packet.risk_flags = _dedupe(packet.risk_flags + ["hook_pipeline_failed"])
    packet.external_reasoning_artifacts.append(
        {
            "claim": "cognitive hook pipeline degraded safely",
            "evidence": str(error),
            "objection": "fallback packet may have less context than full pipeline",
            "decision": "continue with deterministic packet and explicit risk flag",
            "required_test": "fallback safe packet regression",
            "next_action": "preserve existing runtime behavior",
        }
    )
    return packet


def sanitize_message(message: str) -> str:
    return " ".join(str(message or "").replace("\x00", "").split())


def detect_intent(message: str, authority_level: str = "A0") -> str:
    raw = message.lower()
    if authority_level == "A5":
        return "critical_operation"
    if authority_level == "A4":
        return "external_action"
    if authority_level == "A3":
        return "workstation_operation"
    if authority_level == "A2":
        return "build_or_install"
    if any(token in raw for token in ("edit", "modify", "refactor", "implement", "patch", "write", "crear", "edita")):
        return "workspace_edit"
    if any(token in raw for token in ("analyze", "audit", "inspect", "review", "report", "analiza", "revisa")):
        return "analysis"
    return "query"


def detect_language(message: str) -> str:
    raw = message.lower()
    spanish_hits = len(re.findall(r"\b(quiero|necesito|analiza|crea|edita|publica|instala|donde|como|para)\b", raw))
    english_hits = len(re.findall(r"\b(please|need|analyze|create|edit|publish|install|where|how|for)\b", raw))
    return "es" if spanish_hits > english_hits else "en"


_LAYER_PATTERNS: dict[str, re.Pattern[str]] = {
    "l0": re.compile(r"\b(l0|overseer|go\.mod|elixir|dummied)\b", re.IGNORECASE),
    "l1": re.compile(r"\b(l1|nervous|mcp|gateway|transport)\b", re.IGNORECASE),
    "l2": re.compile(r"\b(l2|brain|model|router|daemon|planner|memory|hook|cognitive|learning)\b", re.IGNORECASE),
    "l3": re.compile(r"\b(l3|shield|authority|audit|security|policy)\b", re.IGNORECASE),
    "l4": re.compile(r"\b(l4|edge|sensor|discovery)\b", re.IGNORECASE),
    "l5": re.compile(r"\b(l5|workstation|browser|chrome|playwright|gui|driver)\b", re.IGNORECASE),
    "l6": re.compile(r"\b(l6|skin|dashboard|ui|frontend)\b", re.IGNORECASE),
}


def detect_affected_layers(message: str) -> list[str]:
    return [layer for layer, pattern in _LAYER_PATTERNS.items() if pattern.search(message)]


_A5_SENSITIVE_TARGETS = r"(\.env\b|credential(s)?\b|secret(s)?\b|token(s)?\b|payment(s)?\b|billing\b|root\b|kernel\b|/etc\b)"
_A5_CRITICAL_COMMANDS = r"(\bsudo\b|rm\s+-rf\b|delete\s+everything\b)"
_A5_DRIVERS = r"\bdriver(s)?\b"

_A4_SOCIAL_TARGETS = r"(\bpost\b|\btweet\b|\bsocial\b|\btwitter\b|\blinkedin\b|\bfacebook\b|\binstagram\b|\btiktok\b|\bwhatsapp\b|\btelegram\b)"
_A4_EXTERNAL_ACTIONS = r"(\bpublish\b|\bpublica\b|\bsend\s+email\b|\bcorreo\b|\bproduction\s+api\b)"

_ACTION_VERBS = r"(edit|modify|refactor|implement|patch|write|update|actualiza|delete|borra|elimina|post|publish|publica|send|envía|install|instala)"

def classify_authority_level(message: str, current_authority_level: str = "A0") -> str:
    raw = sanitize_message(message).lower()
    
    # A5: Critical commands or Action + Sensitive Target
    if re.search(_A5_CRITICAL_COMMANDS, raw):
        return "A5"
    if re.search(_ACTION_VERBS, raw) and (re.search(_A5_SENSITIVE_TARGETS, raw) or re.search(_A5_DRIVERS, raw)):
        return "A5"
        
    # A4: External Publication or Action + Social Target
    if re.search(_A4_EXTERNAL_ACTIONS, raw):
        return "A4"
    if re.search(_ACTION_VERBS, raw) and re.search(_A4_SOCIAL_TARGETS, raw):
        return "A4"

    # A3: Workstation/UI
    if re.search(r"(\bchrome\b|\bplaywright\b|\bbrowser\b|\bgui\b|\bdesktop\b|\bworkstation\b|\blocal\s+service\b|\bxdg-open\b)", raw):
        return "A3"
        
    # A2: Build/Install (not already covered by A5 update/install logic)
    if re.search(r"(\binstall\b|\binstala\b|\bdependency\b|\bdependenc(ia|y)\b|\buv\s+add\b|\bpip\s+install\b|\bnpm\s+install\b|\bbuild\b|\bcompile\b|\brun\s+tests?\b|\bpytest\b)", raw):
        return "A2"
        
    # A1: Basic Workspace Edits
    if re.search(r"(\bedit\b|\bedita\b|\bmodify\b|\bmodifica\b|\bcreate\b|\bcrea\b|\bwrite\b|\bimplement\b|\brefactor\b|\bpatch\b|\brepo\b|\bfile\b|\btests?\b)", raw):
        return "A1"
        
    return current_authority_level if current_authority_level in AUTHORITY_LEVELS else "A0"


def discover_tool_hints(message: str, authority_level: str, available_tools: list[str]) -> list[str]:
    hints = set(_string_list(available_tools))
    if authority_level in {"A1", "A2"}:
        hints.update({"apply_patch", "pytest"})
    if authority_level == "A2":
        hints.add("rollback_plan")
    if authority_level == "A3":
        hints.update({"mission_autonomy_contract", "workstation_operator"})
    if authority_level == "A4":
        hints.update({"human_checkpoint", "authority_gate"})
    if authority_level == "A5":
        hints.update({"explicit_human_veto", "authority_gate"})
    if "memory" in message.lower():
        hints.add("memory_retrieval")
    return sorted(hints)


def estimate_token_budget_hint(message: str, context_refs: list[str]) -> int:
    rough_prompt_tokens = max(1, len(message) // 4)
    return rough_prompt_tokens + (len(context_refs) * 80)


def select_reasoning_mode(authority_level: str, message: str, affected_layers: list[str]) -> str:
    if authority_level == "A5":
        return "cloud_prem"
    if authority_level == "A4":
        return "cloud_std"
    if authority_level in {"A2", "A3"}:
        return "local_deep"
    if authority_level == "A1" or len(affected_layers) > 1 or "refactor" in message.lower():
        return "local_deep"
    return "local_fast"


def sanitize_external_reasoning_artifacts(value: Any) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(value, list):
        return [], False

    clean: list[dict[str, Any]] = []
    rejected_private = False
    allowed_keys = {"claim", "evidence", "objection", "decision", "required_test", "next_action", "latency_ms"}
    for item in value:
        if not isinstance(item, Mapping):
            continue
        if _contains_private_reasoning(item):
            rejected_private = True
            continue
        clean.append({str(k): v for k, v in item.items() if str(k) in allowed_keys})
    return clean, rejected_private


def _contains_private_reasoning(item: Mapping[str, Any]) -> bool:
    private_key_terms = {"chain_of_thought", "chain-of-thought", "private_reasoning", "internal_monologue", "cot"}
    for key, value in item.items():
        normalized_key = str(key).strip().lower()
        if normalized_key in private_key_terms or normalized_key.replace(" ", "_") in private_key_terms:
            return True
        normalized_value = str(value).lower()
        if any(term in normalized_value for term in ("chain_of_thought", "chain-of-thought", "private internal reasoning")):
            return True
    return False


def _risk_flags_for_authority(authority_level: str) -> list[str]:
    return {
        "A0": [],
        "A1": [],
        "A2": ["tests_and_rollback_required"],
        "A3": ["mission_autonomy_contract_required"],
        "A4": ["human_checkpoint_required"],
        "A5": ["explicit_human_veto_required"],
    }.get(authority_level, ["unknown_authority_level"])


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))
