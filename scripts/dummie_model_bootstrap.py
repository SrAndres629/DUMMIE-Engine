#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run(cmd: list[str], env: dict[str, str], timeout_s: int = 45) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout_s,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout_s}s"


@dataclass
class BootstrapReport:
    decision: str
    generated_at: str
    opencode_installed: bool
    opencode_bin: str
    opencode_data_home: str
    opencode_usable: bool
    opencode_models: list[str]
    opencode_free_models: list[str]
    opencode_provider_count: int
    deepseek_env_detected: bool
    deepseek_provider_configured: bool
    deepseek_oauth_command: str
    selected_primary_model: str
    selected_fallback_model: str
    ollama_available: bool
    ollama_models: list[str]
    smoke_test_ok: bool
    warnings: list[str]
    next_actions: list[str]


class ModelStackBootstrap:
    def __init__(self, root: Path):
        self.root = root
        self.aiwg = self.root / ".aiwg"
        self.runtime_dir = self.aiwg / "runtime"
        self.reports_dir = self.aiwg / "reports"
        self.tools_dir = self.aiwg / "tools"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, smoke_test: bool = True) -> BootstrapReport:
        warnings: list[str] = []
        opencode_bin_path = self._resolve_opencode_bin()
        opencode_installed = opencode_bin_path is not None

        opencode_bin = str(opencode_bin_path) if opencode_bin_path else ""
        opencode_data_home = str(self.tools_dir / "opencode-data")
        env = dict(os.environ)
        env["XDG_DATA_HOME"] = opencode_data_home

        opencode_models: list[str] = []
        free_models: list[str] = []
        opencode_usable = False
        provider_count = 0
        deepseek_provider_configured = False

        if not opencode_installed:
            warnings.append("OpenCode binary not found.")
        else:
            code, out, err = _run([opencode_bin, "models"], env)
            if code == 0:
                opencode_models = [ln.strip() for ln in out.splitlines() if ln.strip() and "/" in ln]
                free_models = [m for m in opencode_models if m.startswith("opencode/")]
                opencode_usable = len(opencode_models) > 0
            else:
                warnings.append(f"opencode models failed: {err or out}")

            code, out, err = _run([opencode_bin, "providers", "list"], env)
            if code == 0:
                provider_count = self._extract_provider_count(out)
                deepseek_provider_configured = "deepseek" in out.lower()
            else:
                warnings.append(f"opencode providers list failed: {err or out}")

        deepseek_env_detected = bool(os.getenv("DEEPSEEK_API_KEY"))

        primary_model = ""
        if deepseek_provider_configured:
            primary_model = "deepseek/deepseek-chat"
        elif "opencode/deepseek-v4-flash-free" in free_models:
            primary_model = "opencode/deepseek-v4-flash-free"
        elif free_models:
            primary_model = free_models[0]
        elif opencode_models:
            primary_model = opencode_models[0]

        ollama_available, ollama_models, ollama_warning = self._ollama_inventory()
        if ollama_warning:
            warnings.append(ollama_warning)
        fallback_model = ollama_models[0] if ollama_models else ""

        smoke_test_ok = False
        if smoke_test and primary_model and opencode_installed:
            code, out, err = _run(
                [
                    opencode_bin,
                    "stats",
                    "--days",
                    "7",
                ],
                env,
                timeout_s=30,
            )
            smoke_test_ok = code == 0
            if not smoke_test_ok:
                warnings.append(f"OpenCode probe failed: {err or out}")

        deepseek_oauth_command = ""
        if opencode_installed:
            deepseek_oauth_command = (
                f"XDG_DATA_HOME='{opencode_data_home}' "
                f"{opencode_bin} providers login -p deepseek"
            )

        decision = "PASS"
        if not opencode_installed or not primary_model:
            decision = "FAIL"
        elif smoke_test and not smoke_test_ok:
            decision = "PASS_WITH_WARNINGS"
        elif warnings:
            decision = "PASS_WITH_WARNINGS"

        next_actions: list[str] = []
        if deepseek_env_detected and not deepseek_provider_configured:
            next_actions.append("Run DeepSeek provider login command to bind provider credentials.")
        if not deepseek_env_detected:
            next_actions.append("Set DEEPSEEK_API_KEY only if you want paid DeepSeek routing.")
        next_actions.append("Use dummie-ctl token-live to monitor token/embedding usage continuously.")

        report = BootstrapReport(
            decision=decision,
            generated_at=_utc_now(),
            opencode_installed=opencode_installed,
            opencode_bin=opencode_bin,
            opencode_data_home=opencode_data_home,
            opencode_usable=opencode_usable,
            opencode_models=opencode_models,
            opencode_free_models=free_models,
            opencode_provider_count=provider_count,
            deepseek_env_detected=deepseek_env_detected,
            deepseek_provider_configured=deepseek_provider_configured,
            deepseek_oauth_command=deepseek_oauth_command,
            selected_primary_model=primary_model,
            selected_fallback_model=fallback_model,
            ollama_available=ollama_available,
            ollama_models=ollama_models,
            smoke_test_ok=smoke_test_ok,
            warnings=warnings,
            next_actions=next_actions,
        )

        self._write_runtime_env(report)
        self._write_reports(report)
        return report

    def _resolve_opencode_bin(self) -> Path | None:
        local = self.root / ".aiwg" / "tools" / "opencode" / "node_modules" / ".bin" / "opencode"
        if local.exists():
            return local
        found = shutil.which("opencode")
        return Path(found) if found else None

    def _ollama_inventory(self) -> tuple[bool, list[str], str]:
        if not shutil.which("ollama"):
            return False, [], "ollama binary not found; local fallback model inventory unavailable."
        proc = subprocess.run(["ollama", "list"], text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout).strip()
            return False, [], f"ollama list failed: {msg}"

        models: list[str] = []
        for line in proc.stdout.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if parts:
                models.append(parts[0])
        return True, models, ""

    @staticmethod
    def _extract_provider_count(output: str) -> int:
        for line in output.splitlines():
            line = line.strip()
            if "credentials" in line.lower():
                parts = line.split()
                for token in parts:
                    if token.isdigit():
                        return int(token)
        return 0

    def _write_runtime_env(self, report: BootstrapReport) -> None:
        env_path = self.runtime_dir / "model_stack.env"
        lines = [
            "# Auto-generated by scripts/dummie_model_bootstrap.py",
            f"DUMMIE_OPENCODE_BIN={report.opencode_bin}",
            f"XDG_DATA_HOME={report.opencode_data_home}",
            f"DUMMIE_OPENCODE_MODEL={report.selected_primary_model}",
        ]
        if report.selected_fallback_model:
            lines.append(f"DUMMIE_LOCAL_FALLBACK_MODEL={report.selected_fallback_model}")

        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_reports(self, report: BootstrapReport) -> None:
        payload = asdict(report)
        json_path = self.reports_dir / "model_stack_bootstrap_latest.json"
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap DUMMIE model stack with OpenCode and local fallback.")
    parser.add_argument("--no-smoke", action="store_true", help="Skip OpenCode run smoke test")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    report = ModelStackBootstrap(root).run(smoke_test=not args.no_smoke)

    print(json.dumps(asdict(report), indent=2, ensure_ascii=True))
    return 0 if report.decision != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
