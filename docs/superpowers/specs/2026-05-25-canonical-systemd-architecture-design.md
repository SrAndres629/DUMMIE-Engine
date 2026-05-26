# Canonical Systemd Architecture Design

> Date: 2026-05-25  
> Status: Implemented  
> Scope: DUMMIE Engine service topology refactoring into systemd-native units

## Intent

Replace the fragile `Type=oneshot` shell-script-with-background-processes pattern with canonical systemd units: one template `dummie-gateway@.service` per gateway, an orchestrator `dummie-engine.service` for tmpfs + lifecycle coordination, and explicit `PartOf`/`Wants`/`Requires` dependency chains.

Every subsystem that runs a persistent process now has its own `.service` unit. systemd is the canonical process manager — not a bash script.

## Architecture Before

```
dummie-engine.service  (Type=oneshot, RemainAfterExit=yes)
  ExecStart=start_metagateway.sh
    ├── spawns 5 gateway processes in background (&)
    ├── polls .ready files for 10s
    └── exits with error if any gateway not ready → Restart=on-failure → duplicates
  Problem: systemd does NOT track gateway processes. Oneshot exits; gateways
           become orphan children of PID 1 in the cgroup but invisible to systemctl.
```

Key defects:
- **Process ownership gap**: systemd sees `dummie-engine.service` as `active (exited)` while gateways may have crashed.
- **Restart amplification**: `Restart=on-failure` + `set -e` + 10s polling loop creates duplicate gateway processes on each restart attempt (observed: 3 overlapping sets).
- **Hardcoded runtime paths**: `base_gateway.py` had `/home/jorand/Escritorio/Biblioteca MCP` baked in. `agentic-agent@.service` used `~/Escritorio/DUMMIE Engine/`.
- **No independent lifecycle**: You cannot `systemctl restart` just the shell gateway; you had to kill and restart the entire engine.

## Architecture After

```
Slice hierarchy (unchanged):
  -.slice → agentic.slice → agentic-workload.slice

Service topology:
  dummie-engine.service (Type=oneshot, RemainAfterExit=yes, Restart=no)
    ├── After=network.target dummie-memory.service
    ├── Wants=dummie-memory.service dummie-gateway@media.service
    │        dummie-gateway@code.service dummie-gateway@infra.service
    │        dummie-gateway@knowledge.service dummie-gateway@shell.service
    ├── ExecStartPre=+mkdir -p /opt/dummie-engine/.aiwg/{runtime,reports,sockets}
    ├── ExecStartPre=+mount -t tmpfs ... (runtime 256M, reports 512M, sockets 64M)
    ├── ExecStartPre=+rm -f /opt/dummie-engine/.aiwg/runtime/gateways/*.{ready,pid}
    ├── ExecStart=/bin/true
    ├── ExecStartPost=/opt/dummie-engine/scripts/kill_orphan_gateways.sh
    └── ExecStop=+umount /opt/dummie-engine/.aiwg/{runtime,reports,sockets}

  dummie-gateway@.service (Type=simple, template)
    ├── After=dummie-engine.service dummie-memory.service
    ├── Requires=dummie-engine.service dummie-memory.service
    ├── PartOf=dummie-engine.service          ← stop engine → stop all gateways
    ├── Slice=agentic-workload.slice
    ├── MemoryMax=2G / MemorySwapMax=1G / TasksMax=128
    ├── Environment=DUMMIE_ROOT=/opt/dummie-engine
    ├── Environment=BIBLIOTECA_MCP=/home/jorand/Escritorio/Biblioteca MCP
    ├── Environment=PYTHONPATH=layers/l1_nervous
    ├── WorkingDirectory=/opt/dummie-engine
    ├── ExecStart=uv run python -m gateway.%i_gateway
    └── Restart=on-failure / RestartSec=5

  dummie-gateway@media.service  (instance: media_gateway, port 8081)
  dummie-gateway@code.service   (instance: code_gateway, port 8082)
  dummie-gateway@infra.service  (instance: infra_gateway, port 8083)
  dummie-gateway@knowledge.service (instance: knowledge_gateway, port 8084)
  dummie-gateway@shell.service  (instance: shell_gateway, port 8085)

Related services (not managed by this spec but participating in the topology):
  dummie-memory.service  — Type=simple, Wants= from engine, After= from gateways
  dummie-guardian.service — Type=simple, After=dummie-engine, Wants=dummie-engine
  dummie-opencode.service — Type=simple, Requires=dummie-engine, PartOf=dummie-engine
```

## Key Design Decisions

### 1. Template unit over 5 separate units
One `dummie-gateway@.service` template, instantiated 5 times with `%i` = media|code|infra|knowledge|shell.  
**Rationale**: DRY. If we need to change MemoryMax or add an environment variable, we change it once.

### 2. `PartOf=` for cascade stop
Each gateway instance declares `PartOf=dummie-engine.service`.  
**Rationale**: `systemctl stop dummie-engine` propagates to all gateways automatically. No custom pkill logic. This is the systemd-native way to model "these belong together."

### 3. `Restart=no` on the orchestrator
The engine service is a pure oneshot — it creates tmpfs mounts and starts gateway Wants. It must NOT autorestart.  
**Rationale**: If a gateway fails to start, `dummie-gateway@*.service` handles its own restart via `Restart=on-failure`. The orchestrator has no runtime state to recover.

### 4. Environment variable over hardcoded paths
`base_gateway.py` now reads `BIBLIOTECA_MCP` from the environment with a sensible default.  
**Rationale**: The project root may change. Hardcoded `/home/jorand/Escritorio/` paths break silently on any other machine or after directory moves.

### 5. Systemd allegiance enforcement (in Python code, not systemd unit)
`base_gateway.py` contains `_enforce_systemd_allegiance()` which checks `/proc/1/cgroup` for a systemd-managed init process and exits with code 77 if not found. Gateways refuse to start outside systemd unless `DUMMIE_ALLOW_MANUAL_GATEWAY=1` is set.  
**Rationale**: Manual `python -m gateway.media_gateway` outside systemd creates an orphan process that the `ExecStartPost` killer would terminate on the next engine restart. This guardrail prevents foot-guns during development.

### 6. ExecStartPost orphan killer
`kill_orphan_gateways.sh` runs on the engine's ExecStartPost (runs once, after all gateway Wants= have been started). It scans `/proc/*/cmdline` for gateway processes and terminates any NOT in a systemd cgroup (regex pattern in `/proc/$pid/cgroup`).  
**Rationale**: Previous restart cycles left orphan processes. This is a defense-in-depth measure that catches any stray gateway that started outside systemd. Running on the engine rather than each gateway template avoids redundant execution (1 call vs 5 identical calls).

### 7. .ready files as health artifacts (not startup gates)
Each gateway still writes `.aiwg/runtime/gateways/<name>.ready` after connecting to all its MCP servers.  
**Rationale**: The `start_metagateway.sh` script (refactored into a health checker) reads these files for monitoring. The startup no longer blocks on them — systemd considers the gateway "started" immediately (Type=simple), and the .ready file is for external readiness probes.

## Runtime Code Changes

### `layers/l1_nervous/gateway/base_gateway.py`
| Line | Before | After |
|------|--------|-------|
| 8 | `BIBLIOTECA_MCP = "/home/jorand/Escritorio/Biblioteca MCP"` | `os.environ.get("BIBLIOTECA_MCP", "/home/jorand/Escritorio/Biblioteca MCP")` |
| 7 | `DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine"))` | Same but fallback changed to `/opt/dummie-engine` |
| (new) | — | `_enforce_systemd_allegiance()` — blocks manual start without env bypass |

### `/etc/systemd/system/agentic-agent@.service`
All `~/Escritorio/DUMMIE Engine/` paths replaced with `/opt/dummie-engine/` and `/media/datasets/DUMMIE Engine/`. `.venv/bin/python` replaced with `uv run python`.

### `/opt/dummie-engine/scripts/start_metagateway.sh`
Refactored from launcher to health checker. Now reports `systemctl status` for all 5 gateways + `.ready` file contents. Does NOT launch processes.

### `/opt/dummie-engine/scripts/kill_orphan_gateways.sh` (NEW)
Scans `/proc/*/cmdline` for gateway processes, verifies each PID is in a systemd cgroup via `/proc/*/cgroup`, kills those that aren't.

## CLI Commands Fixed

| Command | Fix |
|---------|-----|
| `dummie-lab-on` | `~/Escritorio/DUMMIE Engine` → `/opt/dummie-engine` |
| `dummie-lab-off` | Same path fix |
| `dummie-mcp` | Path fix + `l2_brain/.venv` → `uv run python` |
| `dummie-doctor-repair` | Symlink created in PATH + `l2_brain/.venv` → `uv run python` |
| `dummie-ctl` | 22 `flat_brain/cli_control_plane.py` → `mission/cli_control_plane.py` + symlink created |
| `dummie` (CLI wrapper) | `ROOT_DIR/.venv/bin/python3` → `uv run python -m dummie` |
| `dummie_mcp_doctor.py` | `l2_brain/.venv/bin/python` (dead path) → root `.venv/bin/python3` |
| `dummie_truth.py` | Hardcoded .venv fallback → root `.venv/bin/python3` |

## Migration Notes

### 1. NTFS-3G → ntfs3 attempt (2026-05-25)
An experimental migration of `/media/datasets` from FUSE `ntfs-3g` to the kernel `ntfs3` driver was attempted. The volume mounted successfully under ntfs3, but **ntfs3 does not interpret ntfs-3g reparse points as Linux symlinks**. This rendered 146,951 stored symlinks (including `.venv/bin/python3` pointing to uv-managed Python) as raw binary data, breaking the entire Python toolchain. The system was rolled back to ntfs-3g within the same session. The fstab now explicitly specifies `ntfs-3g` instead of `auto` to prevent accidental ntfs3 activation. Migration to ntfs3 will require a kernel patch adding ntfs-3g symlink reparse point interpretation or a symlink-to-copy migration strategy.

### 2. .venv → uv run migration
All CLI scripts and entry points now use `uv run python` instead of hardcoded `.venv/bin/python` paths. This eliminates the dependency on the venv symlink location and makes the project portable. The root `.venv` remains for SDK compatibility but is no longer directly referenced by any CLI entry point.

### 3. Override.conf vestigial cleanup
`/etc/systemd/system/dummie-engine.service.d/override.conf` previously contained `MemoryMax=8G`, `MemorySwapMax=4G`, and `TasksMax=512` — resource limits inherited from the pre-canonical architecture where all gateway processes ran in the engine's cgroup. After the canonical refactoring, per-gateway limits live in the `dummie-gateway@.service` template (MemoryMax=2G, TasksMax=128 each). The override.conf now contains only a documentation comment explaining this history; the limits have been removed.

## Known Caveats

### ExecStop umount race
`ExecStop=+umount` for tmpfs mounted under `/media/datasets/DUMMIE Engine/.aiwg/` may fail with "target is busy" if `dummie-memory.service` still holds `flight.sock` open on the sockets tmpfs. The memory service is `Wants=` (not `PartOf=`) from the engine, so it is not stopped when the engine stops. This causes `systemctl restart dummie-engine` to report exit-code 32 on the stop phase, but the subsequent start phase re-mounts tmpfs cleanly. Future fix: use `umount -l` (lazy unmount) or explicitly stop memory before umount.

## Verification Results

```
$ systemctl is-active dummie-engine.service → active
$ systemctl is-active dummie-gateway@media.service → active
$ systemctl is-active dummie-gateway@code.service → active
$ systemctl is-active dummie-gateway@infra.service → active
$ systemctl is-active dummie-gateway@knowledge.service → active
$ systemctl is-active dummie-gateway@shell.service → active

$ ls .aiwg/runtime/gateways/*.ready → all 5 files present

$ mount | grep dummie → 3 tmpfs mounts active (runtime 256M, reports 512M, sockets 64M)

Restart cycle:
$ sudo systemctl restart dummie-engine
→ All 5 gateways active again, zero orphan processes

PartOf propagation:
$ sudo systemctl stop dummie-engine
→ All 5 gateway instances stopped automatically
```

## Future Work

- **Watchdog**: Add `WatchdogSec=30` to the gateway template with `sd_notify()` calls from the gateway Python code for automatic crash restart.
- **Per-MCP readiness**: Refactor `base_gateway.py` to write per-MCP-server readiness files, not a single monolithic `.ready` file at the end.
- **Gateway health metrics endpoint**: Expose Prometheus-style metrics on a `/health` endpoint within each gateway.
