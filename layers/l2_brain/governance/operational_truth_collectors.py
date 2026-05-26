from __future__ import annotations

import asyncio
import importlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from layers.l2_brain.governance.operational_truth import (
    TruthCheck,
    TruthReport,
    TruthStatus,
)


def _file_check(
    repo: Path,
    name: str,
    layer: str,
    rel_path: str,
    next_repair: str = "",
    degraded_if_missing: bool = False,
) -> TruthCheck:
    path = repo / rel_path
    if path.exists():
        return TruthCheck(name, layer, TruthStatus.PASS, [f"found {rel_path}"])
    status = TruthStatus.DEGRADED if degraded_if_missing else TruthStatus.BLOCKED
    return TruthCheck(
        name,
        layer,
        status,
        [f"missing {rel_path}"],
        next_repair=next_repair,
    )


def _import_check(
    name: str, layer: str, module: str, next_repair: str = ""
) -> TruthCheck:
    try:
        importlib.import_module(module)
        return TruthCheck(name, layer, TruthStatus.PASS, [f"import {module} ok"])
    except Exception as exc:
        return TruthCheck(
            name,
            layer,
            TruthStatus.BLOCKED,
            error=str(exc),
            next_repair=next_repair,
        )


def _process_check(
    name: str, layer: str, needle: str, next_repair: str = ""
) -> TruthCheck:
    command = "ps -eo cmd"
    try:
        out = subprocess.check_output(["ps", "-eo", "cmd"], text=True, timeout=2)
    except Exception as exc:
        return TruthCheck(
            name, layer, TruthStatus.UNKNOWN, command=command, error=str(exc)
        )

    if needle in out:
        return TruthCheck(
            name,
            layer,
            TruthStatus.PASS,
            [f"process contains {needle}"],
            command=command,
        )
    return TruthCheck(
        name,
        layer,
        TruthStatus.DEGRADED,
        [f"no live process containing {needle}"],
        command=command,
        next_repair=next_repair,
    )


def _jsonl_check(repo: Path, name: str, layer: str, rel_path: str) -> TruthCheck:
    path = repo / rel_path
    if path.exists():
        try:
            with path.open("r") as handle:
                for _ in range(1):
                    handle.readline()
            return TruthCheck(name, layer, TruthStatus.PASS, [f"readable {rel_path}"])
        except Exception as exc:
            return TruthCheck(name, layer, TruthStatus.BLOCKED, error=str(exc))

    parent = path.parent
    if parent.exists():
        return TruthCheck(
            name,
            layer,
            TruthStatus.DEGRADED,
            [f"{rel_path} missing, parent exists"],
            next_repair="create ledger on first write",
        )
    return TruthCheck(
        name,
        layer,
        TruthStatus.BLOCKED,
        [f"{rel_path} parent missing"],
        next_repair="create ledger directory",
    )


def _router_check() -> TruthCheck:
    try:
        from model_router import ModelRouter

        decision = ModelRouter().route("format this file")
        if decision.model_id == "none":
            return TruthCheck(
                "l2.model_router.default_route",
                "L2",
                TruthStatus.BLOCKED,
                [decision.reason],
                next_repair="initialize ModelRouter with discovered or default registry",
            )
        return TruthCheck(
            "l2.model_router.default_route",
            "L2",
            TruthStatus.PASS,
            [f"{decision.tier.value}:{decision.model_id}"],
        )
    except Exception as exc:
        return TruthCheck(
            "l2.model_router.default_route",
            "L2",
            TruthStatus.BLOCKED,
            error=str(exc),
            next_repair="repair model router import/route contract",
        )


def _model_discovery_check(include_slow: bool) -> TruthCheck:
    if not include_slow:
        return TruthCheck(
            "l2.model_discovery.live",
            "L2",
            TruthStatus.UNKNOWN,
            ["skipped slow model discovery"],
            next_repair="rerun truth report with include_slow=true",
        )

    async def _discover():
        from model_discovery import ModelDiscoveryService

        service = ModelDiscoveryService()
        return await service.discover_all()

    try:
        registry = asyncio.run(_discover())
        counts = {tier.value: len(models) for tier, models in registry.models.items()}
        total = sum(counts.values())
        if total == 0:
            return TruthCheck(
                "l2.model_discovery.live",
                "L2",
                TruthStatus.BLOCKED,
                ["no models discovered"],
                next_repair="fix local/cloud model discovery",
            )
        return TruthCheck(
            "l2.model_discovery.live", "L2", TruthStatus.PASS, [str(counts)]
        )
    except RuntimeError as exc:
        return TruthCheck(
            "l2.model_discovery.live",
            "L2",
            TruthStatus.UNKNOWN,
            error=str(exc),
            next_repair="run slow discovery from CLI or make it async-safe",
        )
    except Exception as exc:
        return TruthCheck(
            "l2.model_discovery.live",
            "L2",
            TruthStatus.DEGRADED,
            error=str(exc),
            next_repair="repair model discovery provider probe",
        )


def _kuzu_check(repo: Path, include_slow: bool) -> TruthCheck:
    if not include_slow:
        return TruthCheck(
            "l2.kuzu.native_open",
            "L2",
            TruthStatus.UNKNOWN,
            ["skipped Kuzu open probe"],
            next_repair="rerun truth report with include_slow=true",
        )

    db_path = repo / ".aiwg" / "memory" / "loci.db"
    if not db_path.exists():
        return TruthCheck(
            "l2.kuzu.native_open",
            "L2",
            TruthStatus.DEGRADED,
            [f"{db_path} does not exist"],
            next_repair="initialize Kuzu memory through the normal bootstrap path",
        )

    try:
        import kuzu

        db = kuzu.Database(str(db_path))
        conn = kuzu.Connection(db)
        if conn is None:
            raise RuntimeError("kuzu connection was not created")
        return TruthCheck("l2.kuzu.native_open", "L2", TruthStatus.PASS, [str(db_path)])
    except Exception as exc:
        return TruthCheck(
            "l2.kuzu.native_open",
            "L2",
            TruthStatus.BLOCKED,
            error=str(exc),
            next_repair="repair Kuzu lock/path/schema initialization",
        )


def _dummied_check(repo: Path, socket_path: Optional[Path] = None) -> TruthCheck:
    import socket
    import json
    from typing import Optional

    if socket_path is None:
        socket_path = repo / ".aiwg" / "sockets" / "dummied.sock"

    if not socket_path.exists():
        return TruthCheck(
            "l0.dummied.control_socket",
            "L0",
            TruthStatus.DEGRADED,
            [f"socket {socket_path} does not exist"],
            next_repair="start dummied daemon",
        )

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(1.0)
        client.connect(str(socket_path))
        client.sendall(b'{"type":"PING"}\n')
        response = client.recv(4096).decode("utf-8")
        client.close()

        payload = json.loads(response)
        if "PONG" in response or payload.get("message") == "PONG":
            return TruthCheck(
                "l0.dummied.control_socket",
                "L0",
                TruthStatus.PASS,
                [f"control ping ok: {response.strip()}"],
            )
        return TruthCheck(
            "l0.dummied.control_socket",
            "L0",
            TruthStatus.DEGRADED,
            [f"unexpected response: {response.strip()}"],
            next_repair="check daemon control handler",
        )
    except Exception as exc:
        return TruthCheck(
            "l0.dummied.control_socket",
            "L0",
            TruthStatus.BLOCKED,
            error=str(exc),
            next_repair="restart daemon or check permissions",
        )


def _add_paths(paths: Iterable[Path]) -> None:

    for path in paths:
        value = str(path)
        if path.exists() and value not in sys.path:
            sys.path.insert(0, value)


def collect_truth(repo_root: str, include_slow: bool = False) -> TruthReport:
    repo = Path(repo_root).resolve()
    _add_paths(
        [
            repo,
            repo / "layers" / "l1_nervous",
            repo / "layers" / "l1_nervous" / "tools_impl",
            repo / "layers" / "l2_brain",
            repo / "layers" / "l3_shield",
            repo / "layers" / "l5_muscle",
        ]
    )

    checks: list[TruthCheck] = [
        _file_check(repo, "l1.gateway.file", "L1", "layers/l1_nervous/mcp_server.py"),
        _file_check(
            repo, "l1.swarm_tools.file", "L1", "layers/l1_nervous/tools_impl/swarm.py"
        ),
        _file_check(
            repo,
            "l2.model_router.file",
            "L2",
            "layers/l2_brain/model_mesh/model_router.py",
        ),
        _file_check(
            repo,
            "l2.model_discovery.file",
            "L2",
            "layers/l2_brain/model_mesh/model_discovery.py",
        ),
        _file_check(
            repo,
            "l2.model_executor.file",
            "L2",
            "layers/l2_brain/model_mesh/model_executor.py",
        ),
        _file_check(
            repo,
            "l2.token_ledger.file",
            "L2",
            "layers/l2_brain/model_mesh/token_cost_ledger.py",
        ),
        _file_check(
            repo,
            "l2.neuron_ledger.file",
            "L2",
            "layers/l2_brain/model_mesh/neuron_ledger.py",
        ),
        _file_check(
            repo,
            "l2.action_graph.file",
            "L2",
            "layers/l2_brain/cognition/action_graph.py",
        ),
        _file_check(
            repo,
            "l2.supervisor_protocol.file",
            "L2",
            "layers/l2_brain/governance/supervisor_protocol.py",
        ),
        _file_check(
            repo,
            "l0.dummied.binary",
            "L0",
            "layers/l0_overseer/dummied",
            "build/start dummied",
        ),
        _file_check(
            repo,
            "l3.topological_auditor.file",
            "L3",
            "layers/l3_shield/topological_auditor.py",
        ),
        _file_check(
            repo, "l3.budget_auditor.file", "L3", "layers/l3_shield/budget_auditor.py"
        ),
        _file_check(
            repo,
            "l3.compliance_auditor.file",
            "L3",
            "layers/l3_shield/compliance_auditor.py",
        ),
        _file_check(repo, "l5.mcp_driver.file", "L5", "layers/l5_muscle/mcp_driver.py"),
        _file_check(
            repo,
            "l6.skin.package",
            "L6",
            "layers/l6_skin/package.json",
            degraded_if_missing=True,
        ),
        _jsonl_check(
            repo, "l1.swarm_ledger.path", "L1", ".aiwg/memory/swarm_ledger.jsonl"
        ),
        _jsonl_check(
            repo, "l2.token_ledger.path", "L2", ".aiwg/ledger/token_usage.jsonl"
        ),
        _jsonl_check(
            repo,
            "root.sovereign_ledger.path",
            "ROOT",
            "ledger/sovereign_resolutions.jsonl",
        ),
        _import_check(
            "l1.gateway.import",
            "L1",
            "mcp_server",
            "repair L1 import path or dependencies",
        ),
        _import_check("l2.model_router.import", "L2", "model_router"),
        _import_check("l2.neuron_ledger.import", "L2", "neuron_ledger"),
        _import_check("l2.action_graph.import", "L2", "action_graph"),
        _import_check("l2.supervisor_protocol.import", "L2", "supervisor_protocol"),
        _import_check("l3.topological_auditor.import", "L3", "topological_auditor"),
        _import_check("l5.mcp_driver.import", "L5", "mcp_driver"),
        TruthCheck(
            "l1.gateway.runtime",
            "L1",
            TruthStatus.PASS,
            ["STDIO transport — launched on-demand by MCP client"],
        ),
        _process_check("l0.dummied.runtime", "L0", "dummied", "start L0 daemon"),
        _dummied_check(repo),
        _process_check(
            "infra.nats.runtime",
            "INFRA",
            "nats-server",
            "start or wire NATS only if needed",
        ),
        _process_check(
            "infra.ollama.runtime",
            "INFRA",
            "ollama serve",
            "start Ollama for local neurons",
        ),
        _router_check(),
        _model_discovery_check(include_slow),
        _kuzu_check(repo, include_slow),
    ]

    return TruthReport(repo_root=str(repo), checks=checks)
