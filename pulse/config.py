"""Pulse Engine configuration — canonical production settings.

Source of Truth: .aiwg/pulse/config.json
Traced: .aiwg/evolution.jsonl EVO-KERNEL-NATIVE
Production: This is NOT documentation — these values control real token spend.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PhaseConfig:
    """Configuration for a single pulse phase.

    Each phase has a primary model and a fallback local model.
    Fallback activates when: cloud circuit breaker is open OR budget exceeded.
    """

    name: str
    model: str
    max_tokens: int
    timeout_seconds: int
    description: str
    fallback_model: Optional[str] = None
    fallback_max_tokens: Optional[int] = None


@dataclass
class GuardConfig:
    """Anti-loop guard configuration.

    max_daily_token_budget: Cloud tokens only. Local tokens are free.
    max_consecutive_cloud_failures: Opens circuit breaker for cloud_breaker_cooldown_m.
    """

    max_pulses_per_day: int = 3
    max_daily_token_budget: int = 500000
    quiet_hours_start: int = 23
    quiet_hours_end: int = 6
    min_interval_minutes: int = 15
    max_consecutive_failures: int = 3
    cloud_breaker_threshold: int = 3
    cloud_breaker_cooldown_minutes: int = 30


@dataclass
class PulseConfig:
    """Complete Pulse Engine configuration.

    Phase model assignments (cloud + local fallback):
    - P1 Investigation: deepseek-v4-pro → fallback gemma4:e4b (local)
    - P2 Planning:      deepseek-v4-pro → fallback gemma4:e4b (local)
    - P3 Builder:       smallthinker:3b (local, nunca cloud)
    - P4 Critic:        qwen3.5:0.8b (local, nunca cloud)
    """

    phases: List[PhaseConfig] = field(
        default_factory=lambda: [
            PhaseConfig(
                name="investigation",
                model="openrouter/deepseek/deepseek-v4-pro",
                max_tokens=50000,
                timeout_seconds=600,
                description="Deep investigation of current state and opportunities",
                fallback_model="ollama/gemma4:e4b",
                fallback_max_tokens=20000,
            ),
            PhaseConfig(
                name="planning",
                model="openrouter/deepseek/deepseek-v4-pro",
                max_tokens=30000,
                timeout_seconds=300,
                description="Strategic planning based on investigation findings",
                fallback_model="ollama/gemma4:e4b",
                fallback_max_tokens=15000,
            ),
            PhaseConfig(
                name="builder",
                model="ollama/smallthinker:3b",
                max_tokens=20000,
                timeout_seconds=300,
                description="Implementation of planned changes via opencode",
                fallback_model=None,
                fallback_max_tokens=None,
            ),
            PhaseConfig(
                name="critic",
                model="ollama/qwen3.5:0.8b",
                max_tokens=15000,
                timeout_seconds=180,
                description="Critical review of implemented changes",
                fallback_model=None,
                fallback_max_tokens=None,
            ),
        ]
    )
    guards: GuardConfig = field(default_factory=GuardConfig)
    pulse_root: str = "/opt/dummie-engine/.aiwg/pulse"
    log_file: str = "/opt/dummie-engine/.aiwg/reports/pulse.log"
    prod_log_file: str = "/opt/dummie-engine/.aiwg/reports/pulse_prod.jsonl"
    health_port: int = 8090
