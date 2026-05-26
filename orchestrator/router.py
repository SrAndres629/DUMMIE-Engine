"""Model router — routes tasks to the optimal model based on capability matrix.

Source of Truth: Model capability matrix (local ollama models)
Traced: Each routing decision logged via pulse progress tracker
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class TaskType(Enum):
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    REASONING = "reasoning"
    CODE = "code"
    CRITIC = "critic"
    CREATIVE = "creative"
    CONVERSATION = "conversation"


# Canonical model capability matrix
# Each model has: supported task types, max tokens, speed, quality
MODEL_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "granite-embedding:30m": {
        "types": [TaskType.EMBEDDING],
        "max_tokens": 8192,
        "speed": "fast",
        "quality": "medium",
        "memory_mb": 62,
        "priority": "specialized",
    },
    "smollm:360m": {
        "types": [TaskType.CLASSIFICATION, TaskType.CONVERSATION],
        "max_tokens": 4096,
        "speed": "very_fast",
        "quality": "low",
        "memory_mb": 229,
        "priority": "fallback",
    },
    "qwen3.5:0.8b": {
        "types": [TaskType.CRITIC, TaskType.CLASSIFICATION, TaskType.CODE],
        "max_tokens": 8192,
        "speed": "fast",
        "quality": "medium",
        "memory_mb": 1024,
        "priority": "balanced",
    },
    "smallthinker:3b": {
        "types": [TaskType.REASONING, TaskType.CODE, TaskType.CREATIVE],
        "max_tokens": 8192,
        "speed": "medium",
        "quality": "high",
        "memory_mb": 3686,
        "priority": "primary",
    },
    "gemma4:e2b": {
        "types": [
            TaskType.REASONING,
            TaskType.CREATIVE,
            TaskType.CONVERSATION,
            TaskType.CODE,
        ],
        "max_tokens": 8192,
        "speed": "medium",
        "quality": "high",
        "memory_mb": 7373,
        "priority": "secondary",
    },
    "gemma4:e4b": {
        "types": [
            TaskType.REASONING,
            TaskType.CREATIVE,
            TaskType.CODE,
            TaskType.CRITIC,
            TaskType.CLASSIFICATION,
        ],
        "max_tokens": 8192,
        "speed": "slow",
        "quality": "very_high",
        "memory_mb": 9830,
        "priority": "heavy",
    },
}


class ModelRouter:
    """Routes tasks to the best model based on capability and priority."""

    def route_task(
        self, task_type: TaskType, max_tokens: int = 4096, priority: str = "balanced"
    ) -> Optional[str]:
        candidates: List[tuple] = []
        for model, caps in MODEL_CAPABILITIES.items():
            if task_type in caps["types"] and caps["max_tokens"] >= max_tokens:
                candidates.append((model, caps))

        if not candidates:
            return None

        speed_order = {"very_fast": 0, "fast": 1, "medium": 2, "slow": 3}
        quality_order = {"low": 0, "medium": 1, "high": 2, "very_high": 3}

        if priority == "speed":
            candidates.sort(key=lambda x: speed_order[x[1]["speed"]])
        elif priority == "quality":
            candidates.sort(key=lambda x: quality_order[x[1]["quality"]], reverse=True)
        else:  # balanced
            candidates.sort(
                key=lambda x: (
                    speed_order[x[1]["speed"]],
                    -quality_order[x[1]["quality"]],
                )
            )

        return candidates[0][0]

    def route_by_description(self, description: str) -> Optional[str]:
        """Route based on natural language task description."""
        desc_lower = description.lower()

        for task_type, keywords in _TASK_KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                return self.route_task(task_type)

        return self.route_task(TaskType.REASONING)

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        return {
            k: v
            for k, v in MODEL_CAPABILITIES.get(model_name, {}).items()
            if k != "types"
        } or None

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        return MODEL_CAPABILITIES

    def get_models_for_task(self, task_type: TaskType) -> List[str]:
        return sorted(
            model
            for model, caps in MODEL_CAPABILITIES.items()
            if task_type in caps["types"]
        )


_TASK_KEYWORDS: Dict[TaskType, List[str]] = {
    TaskType.EMBEDDING: ["embed", "vector", "similarity", "search", "semantic"],
    TaskType.CLASSIFICATION: ["classify", "categorize", "sort", "label", "filter"],
    TaskType.REASONING: [
        "reason",
        "think",
        "analyze",
        "plan",
        "strategy",
        "architecture",
        "design",
    ],
    TaskType.CODE: [
        "code",
        "programm",
        "python",
        "rust",
        "implement",
        "function",
        "class",
    ],
    TaskType.CRITIC: ["review", "critique", "check", "validate", "verify", "audit"],
    TaskType.CREATIVE: ["write", "create", "brainstorm", "ideate", "imagine", "story"],
    TaskType.CONVERSATION: ["chat", "talk", "discuss", "explain", "question"],
}
