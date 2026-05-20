from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import PurePosixPath
import signal
import subprocess
import tempfile
from typing import Iterable


@dataclass(frozen=True)
class VerificationCommand:
    command: str
    reason: str
    scope: str
    timeout_seconds: int = 300


@dataclass(frozen=True)
class PolyglotVerificationPlan:
    changed_paths: list[str]
    languages: list[str]
    layers: list[str]
    required_commands: list[VerificationCommand]


@dataclass(frozen=True)
class VerificationResult:
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class VerificationVerdict:
    ready_to_commit: bool
    ready_to_push: bool
    failed_commands: list[str]
    missing_commands: list[str]
    reason: str


_LAYER_ORDER = {"AIWG": 0, "L0": 1, "L1": 2, "L2": 3, "L3": 4, "L4": 5, "L5": 6, "specs": 90}
_LANGUAGE_ORDER = {"go": 0, "elixir": 1, "markdown": 2, "python": 3, "yaml": 4, "json": 5}


def build_polyglot_verification_plan(changed_paths: Iterable[str]) -> PolyglotVerificationPlan:
    normalized_paths = [_normalize_path(path) for path in changed_paths]
    relevant_paths = [path for path in normalized_paths if not _is_ignored_path(path)]
    commands: list[VerificationCommand] = []
    languages: set[str] = set()
    layers: set[str] = set()

    _add_command(
        commands,
        VerificationCommand(
            command="git diff --check",
            reason="reject whitespace and conflict-marker regressions before commit",
            scope="repository",
        ),
    )

    for path in relevant_paths:
        if _is_l2_python(path):
            languages.add("python")
            layers.add("L2")
            _add_command(
                commands,
                VerificationCommand(
                    command="uv run pytest -q layers/l2_brain/tests",
                    reason="L2 Python changes require the L2 regression suite",
                    scope="L2",
                ),
            )

        if _is_l1_go(path):
            languages.add("go")
            layers.add("L1")
            _add_command(
                commands,
                VerificationCommand(
                    command="cd layers/l1_nervous && go test ./...",
                    reason="L1 Go runtime changes require the L1 Go module suite",
                    scope="L1",
                ),
            )

        if _is_spec(path):
            languages.add("markdown")
            layers.add("specs")
            _add_command(
                commands,
                VerificationCommand(
                    command="python3 scripts/validate_specs_docs.py",
                    reason="spec changes require docs/spec validation",
                    scope="specs",
                ),
            )

        if _is_aiwg_state(path):
            layers.add("AIWG")
            _add_command(
                commands,
                VerificationCommand(
                    command="PYTHONPATH=. uv run pytest -q layers/l2_brain/tests/test_aiwg_pack_guard.py",
                    reason="AIWG state changes require pack/freeze guard verification",
                    scope="AIWG",
                ),
            )

    return PolyglotVerificationPlan(
        changed_paths=relevant_paths,
        languages=sorted(languages, key=lambda item: (_LANGUAGE_ORDER.get(item, 100), item)),
        layers=sorted(layers, key=lambda item: (_LAYER_ORDER.get(item, 100), item)),
        required_commands=commands,
    )


def evaluate_verification_results(
    plan: PolyglotVerificationPlan,
    results: Iterable[VerificationResult],
) -> VerificationVerdict:
    results_by_command = {result.command: result for result in results}
    missing_commands: list[str] = []
    failed_commands: list[str] = []

    for item in plan.required_commands:
        result = results_by_command.get(item.command)
        if result is None:
            missing_commands.append(item.command)
        elif result.exit_code != 0:
            failed_commands.append(item.command)

    ready = not missing_commands and not failed_commands
    if ready:
        reason = "all required verification passed"
    elif failed_commands:
        reason = "required verification failed; commit and push are blocked"
    else:
        reason = "required verification is missing; commit and push are blocked"

    return VerificationVerdict(
        ready_to_commit=ready,
        ready_to_push=ready,
        failed_commands=failed_commands,
        missing_commands=missing_commands,
        reason=reason,
    )


def parse_git_status_paths(status_output: str) -> list[str]:
    paths: list[str] = []
    for line in status_output.splitlines():
        if not line:
            continue
        payload = line[3:]
        if " -> " in payload:
            payload = payload.rsplit(" -> ", maxsplit=1)[1]
        paths.append(payload.strip())
    return paths


def run_verification_commands(
    plan: PolyglotVerificationPlan,
    *,
    cwd: str | None = None,
    timeout_seconds: int | None = None,
) -> list[VerificationResult]:
    results: list[VerificationResult] = []
    for item in plan.required_commands:
        env = os.environ.copy()
        if "uv run" in item.command and not env.get("UV_CACHE_DIR"):
            env["UV_CACHE_DIR"] = str(PurePosixPath(tempfile.gettempdir()) / "dummie-uv-cache")
        if "go test" in item.command and not env.get("GOCACHE"):
            env["GOCACHE"] = str(PurePosixPath(tempfile.gettempdir()) / "dummie-go-cache")
        timeout = timeout_seconds or item.timeout_seconds
        process = subprocess.Popen(
            item.command,
            cwd=cwd,
            env=env,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            exit_code = 124
            stderr = f"{stderr}\ncommand timed out after {timeout} seconds".strip()
        results.append(
            VerificationResult(
                command=item.command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
            )
        )
    return results


def _add_command(commands: list[VerificationCommand], command: VerificationCommand) -> None:
    if command.command not in {item.command for item in commands}:
        commands.append(command)


def _normalize_path(path: str) -> str:
    return str(PurePosixPath(path.replace("\\", "/")))


def _is_ignored_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if any(part in {"__pycache__", ".pytest_cache", ".venv", "node_modules"} for part in parts):
        return True
    if path.endswith((".pyc", ".pyo", ".tmp", ".log")):
        return True
    return _is_generated_protobuf(path)


def _is_generated_protobuf(path: str) -> bool:
    return path.endswith(".pb.go") or path.endswith(".pb.ex")


def _is_l2_python(path: str) -> bool:
    return path.startswith("layers/l2_brain/") and path.endswith(".py") and "/tests/" not in path


def _is_l1_go(path: str) -> bool:
    return path.startswith("layers/l1_nervous/") and path.endswith(".go")


def _is_spec(path: str) -> bool:
    return path.startswith("doc/specs/") and path.endswith(".md")


def _is_aiwg_state(path: str) -> bool:
    return path.startswith((".aiwg/state/", ".aiwg/packs/", ".aiwg/reports/"))
