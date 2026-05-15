# Spec 84: Context Budget Manager

## Goal
Manage the cognitive context window by allocating budgets, detecting pressure, and enforcing limits through compression or selective discarding of low-priority information.

## Core Requirements
- Allocate token budgets based on model tiers (local vs cloud).
- Detect when context usage exceeds thresholds.
- Enforce budgets by prioritizing "critical" items.
- Preserve essential mission state: goals, authority levels, next actions, and recovery packets.
- Identify items suitable for compression or discard (e.g., old scratchpad notes, redundant tool outputs).

## Priority Levels
- `critical`: Must never be discarded (Mission goals, Current Phase, Next Action).
- `high`: Should be preserved if possible (Recent evidence, Key decisions).
- `medium`: Can be compressed (Detailed tool outputs, older logs).
- `low`: Can be discarded first (Historical scratchpad, redundant files).
