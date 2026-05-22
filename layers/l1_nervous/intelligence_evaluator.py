import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("dummie-mcp.evaluator")

EVAL_LOG_PATH = os.path.join(
    os.environ.get(
        "DUMMIE_ROOT",
        "/media/datasets/DUMMIE Engine",
    ),
    ".aiwg",
    "runtime",
    "router_decisions.jsonl",
)


class IntelligenceEvaluator:
    def __init__(self):
        self._ensure_log_dir()
        self._session_metrics = {
            "total": 0,
            "exact_matches": 0,
            "llm_matches": 0,
            "adaptations": 0,
            "no_matches": 0,
            "total_latency_ms": 0,
        }

    def _ensure_log_dir(self):
        log_dir = os.path.dirname(EVAL_LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)

    def log_decision(self, decision: dict):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": decision.get("query", ""),
            "found": decision.get("found", False),
            "stage": decision.get("stage", ""),
            "match_id": decision.get("match", {}).get("id", "")
            if decision.get("match")
            else "",
            "llm_used": decision.get("llm_used", False),
            "llm_tool": decision.get("llm_suggested_tool", ""),
            "llm_confidence": decision.get("llm_confidence", 0),
            "intent_domain": decision.get("intent", {}).get("domain", ""),
            "intent_action": decision.get("intent", {}).get("action", ""),
            "metacognitive_questions": decision.get("metacognitive_questions", []),
            "latency_ms": round(decision.get("latency_ms", 0), 1),
            "message": decision.get("message", ""),
        }

        self._session_metrics["total"] += 1
        self._session_metrics["total_latency_ms"] += record["latency_ms"]

        if record["found"]:
            if record["llm_used"]:
                self._session_metrics["llm_matches"] += 1
            else:
                self._session_metrics["exact_matches"] += 1
        elif record["stage"] == "adaptation_suggested":
            self._session_metrics["adaptations"] += 1
        else:
            self._session_metrics["no_matches"] += 1

        self._write_log(record)

    def _write_log(self, record: dict):
        try:
            with open(EVAL_LOG_PATH, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error("Error writing evaluator log: %s", e)

    def get_session_metrics(self) -> dict:
        m = dict(self._session_metrics)
        if m["total"] > 0:
            m["avg_latency_ms"] = round(m["total_latency_ms"] / m["total"], 1)
            m["precision"] = round(
                (m["exact_matches"] + m["llm_matches"]) / m["total"], 3
            )
            m["recall"] = round(
                (m["exact_matches"] + m["llm_matches"])
                / max(m["total"] - m["no_matches"], 1),
                3,
            )
        return m
