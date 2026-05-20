#!/bin/bash
# DUMMIE Engine — Cron Event Logger
# Usage: dummie-cron-event.sh <event_type> <task_name>

EVENTS_DIR="/media/datasets/DUMMIE Engine/.aiwg/events"
mkdir -p "$EVENTS_DIR"

EVENT_TYPE="${1:-cron_trigger}"
TASK_NAME="${2:-scheduled_task}"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EPOCH=$(date +%s)
EVENT_ID="evt_${EPOCH}_${TASK_NAME}"

echo "{\"event_id\":\"$EVENT_ID\",\"timestamp\":\"$TIMESTAMP\",\"event_type\":\"$EVENT_TYPE\",\"source\":\"cron\",\"severity\":\"info\",\"payload\":{\"task\":\"$TASK_NAME\"},\"action_taken\":\"logged\",\"metadata\":{\"cron_schedule\":\"automated\"}}" >> "$EVENTS_DIR/cron_events.jsonl"
