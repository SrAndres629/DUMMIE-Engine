"""DUMMIE Pulse Engine — Canonical cognitive animation system for kernel-native autonomous operation.

Layer: L2 Brain Pulse Subsystem
Source of Truth: .aiwg/pulse/
Systemd: dummie-pulse.service
Port: 8090 (health API)
Models: DeepSeek V4 Pro (cloud) + smallthinker:3b + qwen3.5:0.8b (local)
"""

from . import _bootstrap  # noqa: E402,F401 — bypasses Python 3.12.3 importlib bug

__version__ = "1.0.0"
__spec__ = "docs/superpowers/specs/2026-05-25-pulse-engine.md"
