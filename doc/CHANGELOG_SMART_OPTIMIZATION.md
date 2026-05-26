---
status: ACTIVE
layer: l0
domain:
- changelog
- optimization
- grub
- sysctl
dependencies:
- specs/216_benchmark_suite.md
- specs/228_collaborative_gateway.md
---

# DUMMIE Engine — Optimization Changelog

**Period:** May 25–26, 2026
**Hardware:** ASUS ROG (i9-11900H, RTX 3060 6GB)
**Kernel target:** Linux 6.17.0-1023-oem PREEMPT_FULL

---

## Phase 0: Kernel + OS Hardening

### GRUB (applied, rebooted)
```
preempt=full                         # Full preemption (was voluntary)
processor.max_cstate=1               # C1 only (was C4; eliminates C3 70μs + C6 85μs wakeup)
intel_idle.max_cstate=1              # Intel idle: C1 only
audit=0                              # Kernel audit disabled
nosoftlockup                         # No soft lockup detection on isolated CPUs
lsm=lockdown,integrity               # Minimal LSM (no AppArmor overhead)
mitigations=off                      # Spectre/Meltdown off (already set)
isolcpus=domain,managed_irq,6,7,14,15 # 4 isolated CPUs
nowatchdog nmi_watchdog=0            # Watchdogs off (already set)
```

Removed: `zswap.enabled=1` (double compression with zram), `zswap.compressor=zstd`

### Sysctl (live + persistent in /etc/sysctl.d/zz-agentic-memory.conf)
```
vm.swappiness = 150                  # From 10 (zram optimal)
vm.watermark_boost_factor = 0        # From 150000 (was causing reclaim latency spikes)
vm.watermark_scale_factor = 50       # From 10 (more aggressive kswapd)
vm.min_free_kbytes = 262144          # From 67MB (256MB for atomic GPU allocs)
vm.page-cluster = 0                  # zram: no read-ahead needed
vm.compaction_proactiveness = 20     # From 80 (4x NVIDIA Grace default)
vm.extfrag_threshold = 500
vm.dirty_ratio = 10
vm.dirty_background_ratio = 3
vm.dirty_expire_centisecs = 1500
kernel.numa_balancing = 0            # Single-socket: pure overhead
kernel.max_map_count = 655300        # CUDA + Chrome compatibility
```

### GPU / CUDA
- nvidia-persistenced active + persistence mode (pm=1)
- NVMe read_ahead_kb=16 (from 2048)

### CPU / IRQ
- IRQ affinity: nvidia IRQ 192 → CPUs 0-5,8-13 (not isolated CPUs)
- irqbalance BANNED_CPULIST=6,7,14,15
- Ollama pinned to CPUs 7,15 via llm-inference.slice (CPUAffinity=7,15)

### OOM / Memory
- ollama oom_score_adj=-500 (protected)
- MGLRU min_ttl_ms=1000 (prevents thrashing)
- THP=madvise (not always; saves ~7.7% memory)

---

## Phase 1: SMART MetaGateway

### Architecture
Single canonical dispatcher (`dummie_process`) replacing 5 parallel routing paths (MetaGateway dead code, sub-gateway HTTP, MCPProxyManager direct, MetaRouter standalone, RoutingPipeline).

### Components

| File | Purpose |
|------|---------|
| `semantic_cache.py` | 2-layer cache: L1 exact (dict, ~30ns) + L2 cosine (NumPy, ~15μs). async, thread-safe, pickle persistence |
| `smart_router.py` | Qwen3.5:0.8b tiny router with KV cache prefixing. Empty-query fast-fail, embedding fallback, domain classification |
| `context_budget_tools.py` | 3-tier progressive tool disclosure. Core (500 tok), Extended (1500 tok), Specialized (3000 tok). Cumulative thresholds |
| `skill_executor.py` | 4 built-in skills (TDD, Code Review, Debugging, Explore Codebase) with DAG execution, intent matching, compact results |
| `result_compression.py` | Output compression: short passthrough, long truncation, JSON fold |

### Public Tools (when DUMMIE_CANONICAL_MODE=true, 2 tools exposed)
| Tool | Purpose |
|------|---------|
| `dummie_process` | 95% of cases: discover → plan → execute → return |
| `dummie_admin` | Maintenance: install MCP servers, report config, self-program |

### dummie_process modes
```
auto      → detects compound intents, auto-executes high confidence (≥0.85)
discover  → route only, no execution
execute   → route + execute with auto skill binding
plan      → show plan (what will be done) without executing
confirm   → execute a previously approved plan
reject    → agent disagrees → cache learns correction
list      → show available skills
parallel  → split compound intent → concurrent sub-intent dispatch
```

### Performance
- Routing P50: <1ms (cache hit) vs 2-10s (old LLM path)
- Cache hit rate target: 35-60%
- Context savings: ~5000 tokens (45→2 tools exposed)

---

## Files Summary

### Created (11 files)
- `semantic_cache.py` — 2-layer route cache
- `smart_router.py` — tiny model router
- `context_budget_tools.py` — 3-tier disclosure
- `skill_executor.py` — 4 skills + DAG exec
- `result_compression.py` — output folding
- `tests/test_smart_components.py` — 38 unit tests
- `tests/bench_metagateway.py` — benchmark suite
- `doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md` — canonical design
- `doc/specs/216_benchmark_suite.md` through `doc/specs/228_collaborative_gateway.md` — 13 specs

### Modified (5 files)
- `tools.py` — cache wiring + dummie_process + admin + modes + parallel + compression + correction
- `mcp_proxy.py` — daemon pre-warming
- `metagateway.py` — SMART integration with DUMMIE_USE_SMART_ROUTING flag
- `doc/plans/MASTER_OPTIMIZATION_PLAN.md` — updated with all phases
- `doc/PHYSICAL_MAP.md` — updated with SMART architecture

### Deprecated (5 services)
- `dummie-gateway@media|code|infra|knowledge|shell` — systemd masked, 0 processes

### Deleted (2 sysctl files)
- `/etc/sysctl.d/99-low-latency.conf` — consolidated
- `/etc/sysctl.d/99-dummie.conf` — consolidated
- Replaced by single canonical: `/etc/sysctl.d/zz-agentic-memory.conf`

---

## Canonical Architecture

```
Agent (opencode/Claude)
  │  2 tools: dummie_process + dummie_admin
  ▼
MetaGateway.dispatcher
  │
  ├─ SemanticRouteCache (L1 hash + L2 cosine)
  ├─ SmartRouter (Qwen3.5:0.8b, ~50ms)
  ├─ ContextBudgetRouter (3 tiers)
  ├─ SkillBinder (4 skills, DAG exec)
  ├─ MetacognitiveReasoner (gemma4:e2b, fallback only)
  └─ MCPProxyManager (STDIO, 0 HTTP intermediaries)
```

---

## Verification

| Metric | Value |
|--------|-------|
| Tests | 38/38 passing (0.18s) |
| Benchmark | JSON reports in `.aiwg/benchmarks/` |
| Public tools | 2 (canonical) or 9 (legacy) |
| Sub-gateway processes | 0 |
| Sysctl files | 1 canonical |
| GRUB params | 4 applied + verified |
| Ollama CPU | Pinned to CPU7,15 |

---

## Benchmarks

| Metric | Pre-optimization (est.) | Post-optimization |
|--------|------------------------|-------------------|
| Discovery P50 | 2-10s (LLM path) | <1ms (cache hit) |
| Tools in context | 45 schemas (~5000 tokens) | 2 schemas (~500 tokens) |
| Compaction overhead | 80 (4x default) | 20 (NVIDIA Grace default) |
| NVMe read-ahead | 2048 KB | 16 KB |
| zram efficiency | swappiness=10 (contradicts zram) | swappiness=150 (zram optimal) |
| C-state wakeup | C3 70μs + C6 85μs | C1 2μs only |
| Schedule preemption | Voluntary (1-5ms latency) | Full (0.2-1ms latency) |
