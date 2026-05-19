#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1B\[[0-9;]*[A-Za-z]", "", text)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@dataclass
class TokenEmbeddingRealtimeReport:
    decision: str
    generated_at: str
    token_summary: dict[str, Any]
    dummie_token_ledger_files: list[str]
    opencode_usage: dict[str, Any]
    embedding_status: dict[str, Any]
    warnings: list[str]


class TokenEmbeddingMonitor:
    def __init__(self, root: Path):
        self.root = root
        self.aiwg = self.root / ".aiwg"
        self.reports = self.aiwg / "reports"
        self.runtime = self.aiwg / "runtime"
        self.reports.mkdir(parents=True, exist_ok=True)
        self.runtime.mkdir(parents=True, exist_ok=True)

    def build_snapshot(self) -> TokenEmbeddingRealtimeReport:
        warnings: list[str] = []
        ledger_files = self._find_token_ledgers()
        token_summary = self._summarize_dummie_tokens(ledger_files)

        opencode_usage = self._collect_opencode_usage()
        if opencode_usage.get("error"):
            warnings.append(opencode_usage["error"])

        embedding_status = self._collect_embedding_status()
        if embedding_status.get("embedding_mode") in {"UNKNOWN", ""}:
            warnings.append("Embedding status is unknown; run embedding verification if needed.")

        decision = "PASS" if not warnings else "PASS_WITH_WARNINGS"
        return TokenEmbeddingRealtimeReport(
            decision=decision,
            generated_at=_utc_now(),
            token_summary=token_summary,
            dummie_token_ledger_files=[str(p.relative_to(self.root)) for p in ledger_files],
            opencode_usage=opencode_usage,
            embedding_status=embedding_status,
            warnings=warnings,
        )

    def write_snapshot(self, report: TokenEmbeddingRealtimeReport) -> Path:
        payload = asdict(report)
        out = self.reports / "token_embedding_realtime_latest.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        return out

    def _find_token_ledgers(self) -> list[Path]:
        files: list[Path] = []
        candidates = [
            self.aiwg / "ledger" / "token_usage.jsonl",
            self.aiwg / "missions",
            self.aiwg / "sessions",
        ]
        for c in candidates:
            if c.is_file() and c.name.endswith(".jsonl"):
                files.append(c)
            elif c.is_dir():
                files.extend(c.rglob("token_cost_ledger.jsonl"))
        uniq = sorted({p.resolve() for p in files})
        return [Path(p) for p in uniq]

    def _summarize_dummie_tokens(self, files: list[Path]) -> dict[str, Any]:
        total_input = total_output = total_cached = total_reasoning = 0
        estimated_input = 0
        event_count = 0
        by_model: Counter[str] = Counter()
        by_concept: Counter[str] = Counter()

        for path in files:
            if not path.exists():
                continue
            for raw in path.read_text(encoding="utf-8").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    evt = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                event_count += 1
                input_t = int(evt.get("input_tokens") or evt.get("prompt_tokens") or 0)
                output_t = int(evt.get("output_tokens") or evt.get("completion_tokens") or 0)
                cached_t = int(evt.get("cached_tokens") or 0)
                reasoning_t = int(evt.get("reasoning_tokens") or 0)
                is_estimated = bool(evt.get("estimated", False))

                if is_estimated:
                    estimated_input += input_t
                    continue

                total_input += input_t
                total_output += output_t
                total_cached += cached_t
                total_reasoning += reasoning_t

                model = str(evt.get("model_id") or "unknown")
                concept = str(evt.get("concept") or "unknown")
                by_model[model] += input_t + output_t
                by_concept[concept] += input_t + output_t

        uncached_input = max(0, total_input - total_cached)
        billable = uncached_input + total_output + total_reasoning
        return {
            "event_count": event_count,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cached_tokens": total_cached,
            "total_reasoning_tokens": total_reasoning,
            "estimated_input_tokens": estimated_input,
            "total_uncached_input_tokens": uncached_input,
            "total_billable_tokens_estimate": billable,
            "top_models": by_model.most_common(5),
            "top_concepts": by_concept.most_common(5),
        }

    def _collect_opencode_usage(self) -> dict[str, Any]:
        opencode_bin = self._resolve_opencode_bin()
        if not opencode_bin:
            return {"available": False, "error": "OpenCode binary not found."}

        data_home = str(self.aiwg / "tools" / "opencode-data")
        env = dict(os.environ)
        env["XDG_DATA_HOME"] = data_home

        proc = subprocess.run(
            [str(opencode_bin), "stats", "--days", "7", "--models", "5"],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout).strip()
            return {
                "available": False,
                "error": f"opencode stats failed: {msg}",
                "data_home": data_home,
            }

        clean = _strip_ansi(proc.stdout)
        usage = self._parse_opencode_stats(clean)
        usage["available"] = True
        usage["data_home"] = data_home
        return usage

    @staticmethod
    def _parse_opencode_stats(stats_output: str) -> dict[str, Any]:
        fields = {
            "sessions": None,
            "messages": None,
            "days": None,
            "total_cost": None,
            "input": None,
            "output": None,
            "cache_read": None,
            "cache_write": None,
            "avg_tokens_per_session": None,
            "median_tokens_per_session": None,
        }

        in_cost_section = False
        in_model_usage = False

        for line in stats_output.splitlines():
            line = line.strip()
            if not line or line.startswith("┌") or line.startswith("└") or line.startswith("├") or line.startswith("│") is False:
                continue
            clean = line.strip("│").strip()
            if not clean:
                continue

            header = clean.upper()
            if header == "COST & TOKENS":
                in_cost_section = True
                in_model_usage = False
                continue
            if header == "MODEL USAGE":
                in_model_usage = True
                in_cost_section = False
                continue

            m = re.match(r"^(Sessions|Messages|Days)\s+(.+)$", clean)
            if m:
                key, value = m.group(1).lower(), m.group(2).strip()
                fields[key] = value
                continue

            if in_model_usage:
                continue

            m = re.match(r"^(Total Cost|Input|Output|Cache Read|Cache Write|Avg Tokens/Session|Median Tokens/Session)\s+(.+)$", clean)
            if m:
                raw_key = m.group(1)
                value = m.group(2).strip()
                key_map = {
                    "Total Cost": "total_cost",
                    "Input": "input",
                    "Output": "output",
                    "Cache Read": "cache_read",
                    "Cache Write": "cache_write",
                    "Avg Tokens/Session": "avg_tokens_per_session",
                    "Median Tokens/Session": "median_tokens_per_session",
                }
                mapped = key_map[raw_key]
                if in_cost_section or fields[mapped] is None:
                    fields[mapped] = value

        return fields

    def _collect_embedding_status(self) -> dict[str, Any]:
        activation = _read_json(self.reports / "embedding_activation_verification_latest.json")
        router = _read_json(self.reports / "embedding_memory_router_latest.json")

        return {
            "embedding_mode": activation.get("embedding_mode", "UNKNOWN"),
            "router_uses_real_embeddings": activation.get("router_uses_real_embeddings", False),
            "model_load_ok": activation.get("model_load_ok", False),
            "activation_decision": activation.get("decision", "UNKNOWN"),
            "router_decision": router.get("decision", "UNKNOWN"),
            "router_provider": router.get("provider", "UNKNOWN"),
        }

    def _resolve_opencode_bin(self) -> Path | None:
        local = self.aiwg / "tools" / "opencode" / "node_modules" / ".bin" / "opencode"
        if local.exists():
            return local
        found = shutil.which("opencode")
        return Path(found) if found else None


def _print_compact(report: TokenEmbeddingRealtimeReport, output_path: Path) -> None:
    print(
        " | ".join(
            [
                f"[{report.generated_at}]",
                f"decision={report.decision}",
                f"events={report.token_summary.get('event_count', 0)}",
                f"billable={report.token_summary.get('total_billable_tokens_estimate', 0)}",
                f"embed={report.embedding_status.get('embedding_mode', 'UNKNOWN')}",
                f"opencode_input={report.opencode_usage.get('input', 'n/a')}",
                f"report={output_path}",
            ]
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Real-time token and embedding monitor for DUMMIE.")
    parser.add_argument("--watch", action="store_true", help="Run continuously and refresh snapshot")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between snapshots in watch mode")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    monitor = TokenEmbeddingMonitor(root)

    if not args.watch:
        report = monitor.build_snapshot()
        out = monitor.write_snapshot(report)
        print(json.dumps(asdict(report), indent=2, ensure_ascii=True))
        print(f"Report written: {out}")
        return 0

    while True:
        report = monitor.build_snapshot()
        out = monitor.write_snapshot(report)
        _print_compact(report, out)
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
