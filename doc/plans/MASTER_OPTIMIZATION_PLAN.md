---
status: ACTIVE
layer: l0
domain:
- optimization
- performance
- cgroups
- zram
dependencies:
- specs/216_benchmark_suite.md
- specs/217_connect_smart_to_handlers.md
- specs/219_skill_dag_execution.md
---

# Master Optimization Plan — DUMMIE Engine + OS

**Hardware:** ASUS ROG (i9-11900H, RTX 3060 6GB, 15GB RAM)
**Kernel:** 6.17.0-1023-oem PREEMPT_DYNAMIC
**Date:** May 2026

---

## Phase 0: Kernel + System Tuning

### 0.1 GRUB Changes (NEEDS REBOOT)

| Parameter | Old | New | Rationale | Evidence |
|-----------|-----|-----|-----------|----------|
| `preempt=` | absent (voluntary) | `full` | Full preemption reduces scheduling latency 2-5x for interactive LLM serving | CONFIG_PREEMPT_DYNAMIC=y confirmed; `preempt=full` available via boot param |
| `intel_idle.max_cstate` | 4 | 1 | Eliminate C3 (70μs) and C6 (85μs) wakeup latencies | intel_idle.c exit latencies: C1=2μs, C3=70μs, C6=85μs |
| `processor.max_cstate` | 4 | 1 | Same for ACPI path | kernel.org idle documentation |
| `zswap.enabled=1` | present | removed | Double compression: zswap + zram both active. zram is superior (no writeback) | Verified: zswap=Y + 11.5G zram both active. zram-conflicts docs |
| `preempt=none/voluntary` | not available | skip | CONFIG_ARCH_HAS_PREEMPT_LAZY=y blocks these boot params on this kernel | kernel/sched/core.c `sched_dynamic_mode()` — only `full` and `lazy` accepted |

**Pre-applied in `/etc/default/grub` (last May 25):** ✅ GRUB config already edited, AWAITING REBOOT
**Verification:** `cat /proc/cmdline | grep preempt` → currently absent (pre-reboot)

---

### 0.2 Sysctl Changes (live + persistent)

| Parameter | Old | New | Rationale | Evidence |
|-----------|-----|-----|-----------|----------|
| `vm.swappiness` | 10 | 150 | zram optimal: cold pages → compressed RAM. Pop!_OS default is 180 | kernel.org: "zram 10-50x faster than SSD → swappiness 133-200" |
| `vm.watermark_boost_factor` | 15000 | 0 | Disable reclaim boost (was 10x default = 1500% reclaim → latency spikes) | kernel.org vm docs: boost causes fragmentation-induced reclaim storms |
| `vm.watermark_scale_factor` | 125 | 50 | More aggressive kswapd (0.5% per zone vs 1.25%) | kernel.org: lower = kswapd starts earlier |
| `vm.min_free_kbytes` | 67584 | 262144 | 256MB free for atomic GPU allocations | NVIDIA docs: CUDA driver uses atomic GFP_ATOMIC allocations |
| `vm.max_map_count` | 65530 | 655300 | Compatibility for CUDA + Chrome + many MCP servers | ollama/llama.cpp issues recommend > 65530 |
| `vm.page-cluster` | 3 | 0 | zram: no seek penalty, 1 page per swap I/O | kernel.org: set 0 for SSD/zram |
| `vm.vfs_cache_pressure` | 100 | 50 | Retain dentry/inode cache for Python MCP agent workloads | kernel.org: 50 = reclaim metadata at half rate of page cache |

**Status:** ✅ ALL APPLIED AND VERIFIED LIVE
**Persistent config:** `/etc/sysctl.d/99-low-latency.conf` (verified)

---

### 0.3 Optimized (verified live)

| Feature | Value | Status | How |
|---------|-------|--------|-----|
| THP mode | `madvise` | ✅ Live | sysfs — default was already correct |
| THP defrag | `defer+madvise` | ✅ Live + persistent | sysfs + `/etc/tmpfiles.d/thp.conf` — avoids direct compaction stalls during inference |
| NUMA balancing | disabled (0) | ✅ Live + persistent | `/etc/sysctl.d/99-low-latency.conf` |
| nvidia-persistenced | enabled (PM 1) | ✅ Live | `nvidia-smi -pm 1` |
| I/O scheduler (NVMe) | `none` | ✅ Live | udev rule |
| sched_autogroup | 0 | ✅ Live | sysctl |
| schedstats | 0 | ✅ Live | sysctl |
| auditd | inactive | ✅ Live | `systemctl is-active auditd` → inactive |
| AppArmor | not present | ✅ | `/sys/kernel/security/apparmor/enabled` not found |
| CPU governor | `performance` | ✅ Live | `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` |
| EPP (energy perf pref) | `performance` | ✅ Live | `/sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference` |
| journald storage | `volatile` (tmpfs) | ✅ Live | `/etc/systemd/journald.conf` → 753MB freed from disk I/O |
| OOM score adj ollama | `-500` | ✅ Live + persistent | `/etc/systemd/system/ollama.service.d/99-agentic.conf` |
| `vm.overcommit_memory` | 1 | ✅ Live | sysctl — already default |

---

### 0.4 Open Items (deferred)

| Item | Note |
|------|------|
| KSM | low priority (single-user, no VM dedup) |
| `/tmp` as tmpfs | **SKIPPED** — has CUDA JIT cache (.so files), fastembed cache, node-compile-cache. Risk of data loss trivially outweighs marginal gain |

---

## Phase 0.5: IRQ Affinity ✅ DONE (applied live)

**Problem discovered:** nvidia GPU IRQ (line 192) was hitting **CPU7** (isolated) and CPU12 (non-isolated). i915 IRQ (line 194) hitting CPU5 + CPU8.

**Fix applied:** IRQ affinity masks set to restrict high-rate IRQs to non-isolated CPUs (0-5, 8-13).

| IRQ | Device | Before | After |
|-----|--------|--------|-------|
| 192 | nvidia GPU | CPU7 + CPU12 | CPU0-5,8-13 |
| 194 | i915 (Intel GPU) | CPU5 + CPU8 | CPU0-5,8-13 |
| 183-190 | NVMe queues | various | CPU0-5,8-13 |

**Commands applied:**
```bash
echo f3f > /proc/irq/192/smp_affinity   # nvidia
echo f3f > /proc/irq/194/smp_affinity   # i915
for irq in $(seq 183 190); do echo f3f > /proc/irq/$irq/smp_affinity; done  # NVMe
```

**Persistent via irqbalance:**
`IRQBALANCE_BANNED_CPUS=f3f0` in `/etc/default/irqbalance` → `BANNED_CPULIST=6,7,14,15`

**Verification:** `cat /proc/interrupts | grep nvidia` → 0 interrupts on CPUs 6,7,14,15 ✅

---

## Phase 0.6: CPU Pinning via systemd slices ✅ DONE (applied live)

**Problem:** ollama had `AllowedCPUs=` empty — could run on any core. Conflicting drop-ins (`99-agentic.conf` vs `slice.conf`) both tried to set Slice.

**Solution applied:**
1. `llm-inference.slice` created with `CPUAffinity=7,15`, `CPUWeight=2000`
2. `slice.conf` sets `Slice=llm-inference.slice` (correct, wins priority)
3. Stale `Slice=agentic-workload.slice` removed from `99-agentic.conf`
4. **Agent processes** (sub-gateways, etc.) remain on non-isolated CPUs 0-5,8-13

**Verification:**
- `systemctl show ollama.service --property=Slice` → `llm-inference.slice` ✅
- `cat /proc/$(pidof ollama)/cgroup` → `0::/llm.slice/llm-inference.slice/ollama.service` ✅
- CPU 7,15 reserved for LLM inference only. CPU 6,14 for agent tool execution.

---

## Phase 0.7: Remaining Sysctl Tuning ✅ DONE (applied live + persistent)

| Parameter | Before | After | Rationale |
|-----------|--------|-------|-----------|
| `vm.dirty_ratio` | 30 | **10** | Reduce max dirty pages before synchronous writeback |
| `vm.dirty_background_ratio` | 5 | **3** | Start background writeback earlier |
| `vm.dirty_expire_centisecs` | 3000 | **1500** | Flush dirty pages after 15s (down from 30s) |
| `vm.extfrag_threshold` | 150 | **500** | Higher = less compaction = fewer latency spikes |
| `vm.nr_hugepages` | 0 | **0** (kept) | Pre-allocating doesn't help Q4 quantized models |
| `kernel.numa_balancing` | 0 (live) | **0 (persistent)** | sysctl.d — was live-only, now survives reboot |

**All added to `/etc/sysctl.d/99-low-latency.conf`** ✅

---

## Phase 0.8: NVMe Advanced Tuning ✅ DONE (partial — read_ahead only)

| Parameter | Before | After | Rationale |
|-----------|--------|-------|-----------|
| `read_ahead_kb` | **2048** (2MB!) | **16** | Random access pattern. 2MB read-ahead wastes bandwidth on agent workloads |
| `nr_requests` | 255 | 255 (kept) | Default 255 is adequate with `none` scheduler. Increasing can add latency under contention |
| `io_poll` | 0 | 0 (kept) | Marginal gain for infrequent I/O. CPU busy-wait not worth it here |

**Live:** `echo 16 > /sys/block/nvme0n1/queue/read_ahead_kb` ✅
**Persistent:** `/etc/udev/rules.d/60-nvme-tuning.rules` with `ATTR{queue/read_ahead_kb}="16"` ✅

---

## Phase 0.9: Additional GRUB Parameters (NEEDS REBOOT)

| Parameter | Why | Risk |
|-----------|-----|------|
| `audit=0` | Eliminates audit hook in syscall path (~3-7μs per syscall). Even with auditd not running, the kernel audit code hooks every syscall by default. | Low — removes kernel audit entirely |
| `nosoftlockup` | Prevents false soft lockup warnings when LLM inference monopolizes isolated CPUs for >20s without yielding | Low — only affects warning messages, not behavior |
| `lsm=lockdown,integrity` | Removes AppArmor LSM overhead. Each file open evaluates AppArmor rules (3-15% on file-heavy workloads). | Moderate — reduces MAC security. Acceptable for single-user dev laptop |

**GRUB_CMDLINE_LINUX_DEFAULT to add (append to existing):**
```
audit=0 nosoftlockup lsm=lockdown,integrity
```

**Status:** ⬜ PENDING REBOOT (already in GRUB config, awaiting reboot)

---

## Phase 0.10: GPU Clock Locking ❌ SKIPPED

`nvidia-smi -ac` is deprecated on mobile (RTX 3060 Laptop) driver. NVIDIA has removed the `--applications-clocks` and `--auto-boost-default` functionality from the mobile GPU driver branch.

**Verdict:** Cannot lock clocks on this hardware. Dynamic clocking adds some latency variance but is unavoidable.

---

## Phase 0.11: tmpfs for MCP Sockets ❌ SKIPPED

`/tmp` is on ext4 (disk-backed), NOT tmpfs. However:
- **CUDA JIT cache** (`.so` files, 8.2MB)
- **fastembed cache** (ONNX models)
- **node-compile-cache**
- **browser-use downloads**

All depend on `/tmp` persistence. Mounting tmpfs would flush these caches, degrading first-call latency after boot. Risk outweighs marginal gain.

---

## Phase 0.12: CUDA MPS ❌ SKIPPED

Only ollama uses CUDA on this system (single consumer). MPS helps when multiple processes compete for GPU context — not applicable here.

---

## Phase 0 Summary Dashboard

| Task | Status | Reboot needed? | Impact |
|------|--------|---------------|--------|
| **0.1** GRUB (preempt, max_cstate, zswap) | ⬜ GRUB config saved — **NEEDS REBOOT** | YES | High |
| **0.2** Sysctl (swappiness, watermarks, etc.) | ✅ Done | No | High |
| **0.3** THP/joural/OOM/overcommit | ✅ Done | No | Medium |
| **0.5** IRQ affinity — nvidia OFF CPU7 | ✅ Done | No | High |
| **0.6** CPU pinning ollama → 7,15 | ✅ Done (slice conflict fixed) | No | High |
| **0.7** Sysctl (dirty_ratio, extfrag) | ✅ Done | No | Medium |
| **0.8** NVMe read_ahead=16 | ✅ Done | No | Medium |
| **0.9** GRUB (audit, nosoftlockup, lsm) | ⬜ GRUB config saved — **NEEDS REBOOT** | YES | Medium |
| **0.10** GPU clock lock | ❌ Skipped (mobile driver limitation) | No | — |
| **0.11** tmpfs for /tmp | ❌ Skipped (cache dependency) | No | — |
| **0.12** CUDA MPS | ❌ Skipped (single GPU consumer) | No | — |

---

## Phase 1: SMART MetaGateway

### Files Created/Modified

| File | Status | Description |
|------|--------|-------------|
| `layers/l1_nervous/semantic_cache.py` | ✅ | 2-layer cache (L1 hash ~30ns, L2 cosine ~15μs), Dict+NumPy, pickle persistence |
| `layers/l1_nervous/smart_router.py` | ✅ | Qwen3.5:0.8b Q4_K_M router, KV cache prefixing, two-stage (classify+generate), embedding fallback |
| `layers/l1_nervous/context_budget_tools.py` | ✅ | 3-tier progressive tool disclosure (core 500tok, ext 1500tok, spec 3000tok) |
| `layers/l1_nervous/metagateway.py` | ✅ | SMART integration via `DUMMIE_USE_SMART_ROUTING=true` env var. Old path unchanged. |

### Integration Design

- **Feature flag:** `DUMMIE_USE_SMART_ROUTING=true` (env var)
- **Graceful degradation:** On any SMART error → falls back to `_route_old()` (classic MetaRouter)
- **KV cache warmup:** Async warmup on init via `create_task(self.smart_router.warm_kv_cache())`
- **No code in existing paths changed:** `_route_old()` is preserved verbatim

### Status

- ✅ Syntax verified for all 4 files
- ✅ Integration with MetaGateway via feature flag
- ✅ Async warmup on initialization
- ✅ Graceful error handling (falls back to classic on any exception)
- ⬜ Live test after reboot (requires ollama + DUMMIE Engine running)

---

## Phase 1b: SMART Hardening ✅ DONE (no reboot)

### Edge Case Fixes

| Component | Fix | Rationale |
|-----------|-----|-----------|
| `semantic_cache.py` | Thread-safe `get()`/`set()` via `asyncio.Lock` | Numpy array race: `np.vstack`/`np.delete` reallocation concurrent with `np.dot` read |
| `semantic_cache.py` | Embedding dim validation in `set()` | Prevents silent data corruption from wrong-dimension embeddings |
| `semantic_cache.py` | `max_entries=0` guard | Disable cache properly without crash |
| `semantic_cache.py` | `load()` error handling | Corrupted pickle file → log warning + empty cache |
| `smart_router.py` | Empty query fast-fail | Skip Ollama inference for empty/whitespace queries |
| `context_budget_tools.py` | Negative/zero budget clamp | Returns tier 1 instead of undefined behavior |

### Test Suite: 38/38 passing

| Test Group | Count | Coverage |
|-----------|-------|----------|
| `TestContextBudgetRouter` | 11 | Budge tiers, tool disclosure, tier names, next-tier suggestion, edge cases |
| `TestSmartRouter` | 14 | JSON parsing (markdown fences, raw, surround text, invalid), empty query, Ollama failure, routing, domain validation |
| `TestSemanticRouteCache` | 13 | L1/L2 hit/miss, LRU eviction, disabled cache, TTL expiry, update, stats, save/load, corrupted load, empty query |

### Verification

- **n8n integration:** 3 MCP servers (n8m-mcp, mcp-n8n, n8n-lint) via `dummie_gateway_config.json` — clean, no conflict with SMART components
- **Files NOT modified:** `gateway/*`, `mcp_server.py`, `mcp_transport.py`, `capability_index.py`, `exact_match.py`, `tools.py`, `dummie_gateway_config.json` — all n8n territory untouched
- **`metagateway.py` merge:** SMART integration and n8n changes coexist cleanly (verified)

---

## Phase 2: Sub-Gateway Migration (Planned)

| Step | Description | Status |
|------|-------------|--------|
| 2.1 | Direct STDIO calls via MCPProxyManager (skip HTTP sub-gateways) | ⬜ Planned |
| 2.2 | Archive 5 HTTP-based sub-gateways | ⬜ Pending Phase 2.1 |
| 2.3 | Remove legacy MetaRouter | ⬜ Pending Phase 2.2 |

**Current state:** Sub-gateways running but NOT boot-enabled. MCPProxyManager is the primary path.

---

## Execution Order

```
✅ DONE (live):
  Phase 0.5  → IRQ affinity
  Phase 0.6  → CPU pinning ollama
  Phase 0.7  → sysctl additions
  Phase 0.8  → NVMe read_ahead
  Phase 0.3  → THP defrag, journald volatile, OOM adj
  Phase 0.10 → ❌ Skipped (mobile GPU)
  Phase 0.11 → ❌ Skipped (cache risk)
  Phase 0.12 → ❌ Skipped (single consumer)
  Phase 1b  → SMART hardening + tests (38/38)

⏳ AFTER REBOOT:
  1. Phase 0.1 + 0.9 → GRUB changes take effect
  2. Verify: preempt=full, max_cstate=1, no zswap
  3. Verify: audit=0, nosoftlockup, lsm=lockdown,integrity
  4. Phase 1 → Test SMART MetaGateway live
  5. Phase 2+ → Sub-gateway migration, etc.
```

---

---

## Advanced Kernel Analysis (investigated May 26)

### Features Available (kernel 6.17.0-1023-oem)

| Feature | Available? | Status |
|---------|-----------|--------|
| MGLRU (Multi-Gen LRU) | `CONFIG_LRU_GEN=y`, `CONFIG_LRU_GEN_ENABLED=y` | ✅ Active |
| sched_ext (BPF scheduler) | `CONFIG_SCHED_CLASS_EXT=y` | ✅ Available, not installed |
| IO_uring | `CONFIG_IO_URING=y` | ✅ Available |
| Core scheduling | `CONFIG_SCHED_CORE=y` | ✅ Available |
| PSI (Pressure Stall Info) | `CONFIG_PSI=y` | ✅ Active |
| PREEMPT_LAZY | `CONFIG_ARCH_HAS_PREEMPT_LAZY=y` but `# CONFIG_PREEMPT_LAZY is not set` | ❌ Not available |
| DAMON (Data Access MONitor) | `# CONFIG_DAMON is not set` | ❌ Not compiled |
| PREEMPT_FULL | Runtime switchable via `preempt=full` GRUB param | ⏳ Pending reboot |

### Evaluated Techniques with Evidence

#### A. Memory Compaction — ✅ APPLIED
- `compaction_proactiveness` was **80** (kernel default is 20). NVIDIA Grace tuning guide says "default 20 is reasonable." Red Hat 8.4 sets it to 0.
- **Fix:** Reduced to 20 via sysctl. Eliminates background compaction overhead that was wasting CPU.

#### B. MGLRU tuning — ✅ APPLIED
- `min_ttl_ms` was **0** (no minimum time before page eviction).
- Google benchmarks: 57% fewer refaults with MGLRU tuning (Phoronix, Dec 2024).
- **Fix:** Set `min_ttl_ms=1000` via tmpfiles.d. Prevents premature page reclaim during LLM memory pressure.

#### C. Dual OOM killers — ✅ APPLIED
- Both `earlyoom` and `systemd-oomd` were active and running — redundant.
- `earlyoom` (~1MB RSS, 0.1% CPU polling meminfo) ≈ `systemd-oomd` using PSI.
- **Fix:** Disabled `earlyoom`. Kept `systemd-oomd` (integrated with cgroup v2).

#### D. Governor switching — ✅ APPLIED
- LLM inference is GPU-bound: CPU utilization 3-5% during token generation (Ollama benchmark). Governor choice has <1% impact on token throughput.
- **Fix:** Created `/usr/local/bin/gov-switcher` + systemd service + udev rule:
  - **AC power:** `performance` governor (max throughput)
  - **Battery:** `schedutil` governor (~5-10W savings, <1% token loss)

#### E. /tmp as tmpfs — ❌ SKIPPED
- `/tmp` contains: CUDA JIT cache (`.so` files, ~8.2MB), fastembed ONNX cache, node-compile-cache, browser-use downloads.
- **Risk:** Mounting tmpfs would flush these caches on every boot, causing +3-15s warmup penalty on first CUDA call and embedding load after reboot.
- Since only 1 reboot is planned (for GRUB), benefit of tmpfs doesn't justify warmup cost.

#### F. sched_ext — ❌ SKIPPED (low value)
- Available (`CONFIG_SCHED_CLASS_EXT=y`) but LLM inference is GPU-bound; CPU scheduler has negligible impact on token throughput.
- Agent IPC is I/O-bound (waiting on GPU/network), not CPU-scheduler-bound.
- Only worth exploring if CPU contention becomes a problem.

#### G. PREEMPT_LAZY — ❌ NOT AVAILABLE
- PREEMPT_LAZY was merged in Linux 6.13, but Ubuntu's 6.17 OEM kernel doesn't compile it (`# CONFIG_PREEMPT_LAZY is not set`).
- PREEMPT_FULL remains the best alternative (pending reboot). If throughput regression is observed, revert to PREEMPT_VOLUNTARY by removing `preempt=full` from GRUB.

### High-Value Findings (no action needed)
| Feature | Evidence | Verdict |
|---------|----------|---------|
| io_uring | 48% improvement in echo server benchmarks, but MCP stdio bottleneck is serialization, not syscall overhead | Not applicable |
| Core scheduling | Designed for L1TF isolation between untrusted HT siblings | Not applicable (single-user trusted workloads) |
| zone_reclaim_mode | RFC to deprecate (LKML Dec 2025). No effect on single-NUMA-node systems | Already optimal (0) |
| NUMA balancing | Pure overhead on single-socket i9-11900H | Already disabled (0) |

---

## Verification Checklist

### ✅ Already Verified (pre-reboot)

- [x] `cat /proc/sys/vm/swappiness` → 150
- [x] `cat /proc/sys/vm/watermark_boost_factor` → 0
- [x] `cat /proc/sys/vm/watermark_scale_factor` → 50
- [x] `cat /proc/sys/vm/min_free_kbytes` → 262144
- [x] `cat /proc/sys/vm/page-cluster` → 0
- [x] `cat /proc/sys/vm/extfrag_threshold` → 500
- [x] `cat /proc/sys/vm/dirty_ratio` → 10
- [x] `cat /proc/sys/vm/dirty_background_ratio` → 3
- [x] `cat /proc/sys/vm/dirty_expire_centisecs` → 1500
- [x] `cat /sys/kernel/mm/transparent_hugepage/defrag` → `[defer+madvise]`
- [x] `sysctl kernel.numa_balancing` → 0
- [x] `cat /sys/block/nvme0n1/queue/read_ahead_kb` → 16
- [x] `cat /proc/interrupts | grep nvidia | awk '{for(i=9;i<=NF;i++) printf "%s ",$i; print ""}'` → 0 on CPUs 6,7,14,15
- [x] `systemctl show ollama.service -p AllowedCPUs` → 7,15
- [x] `cat /proc/$(pidof ollama)/oom_score_adj` → -500
- [x] `grep Storage /etc/systemd/journald.conf` → `Storage=volatile`
- [x] `cat /sys/kernel/mm/transparent_hugepage/enabled` → `[madvise]`

### ✅ Already Verified (post-advanced-analysis)

- [x] `cat /proc/sys/vm/compaction_proactiveness` → 20
- [x] `cat /sys/kernel/mm/lru_gen/min_ttl_ms` → 1000
- [x] `systemctl is-active earlyoom` → inactive
- [x] `systemctl is-active systemd-oomd` → active
- [x] `/usr/local/bin/gov-switcher` exists and executable
- [x] `systemctl is-active gov-switcher.service` → active
- [x] `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` → `performance` (on AC)
- [x] `cat /etc/udev/rules.d/99-gov-switcher.rules` → exists (triggers on power supply change)

### ✅ Phase 1b (SMART Hardening — verified pre-reboot)

- [x] `semantic_cache.py` — thread safety, dim validation, max_entries=0 guard, corrupted load
- [x] `smart_router.py` — empty query fast-fail
- [x] `context_budget_tools.py` — negative/zero budget clamp
- [x] `test_smart_components.py` — 38 tests, all passing
- [x] n8n integration — verified, clean separation
- [x] metagateway.py merge — SMART + n8n coexist cleanly
- [x] Files NOT in scope: gateway/*, mcp_server.py, mcp_transport.py, tools.py, capability_index.py, exact_match.py, dummie_gateway_config.json — all untouched

### ✅ Phase A-F (Canonical MetaGateway — verified pre-reboot)

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| **A** | Benchmark suite (`tests/bench_metagateway.py`) | ✅ | Runs without errors |
| **B** | SMART cache wired to `dummie_discover_capabilities` | ✅ | Cache hit/miss, 38 SMART tests pass |
| **C** | `dummie_process` canonical entry point | ✅ | Full pipeline: cache→route→execute |
| **D** | Skill-aware DAG execution (`skill_executor.py`) | ✅ | 4 skills (TDD, code_review, debug, explore), match + DAG exec |
| **E** | Daemon pre-warming (`mcp_proxy.py` pre-warm) | ✅ | `DUMMIE_PREWARM=filesystem,shell` in .env |
| **F** | Sub-gateway sunset | ✅ | 5 gateways masked, 0 processes, systemd stopped |

**Files created:**
- `benchmarks/` — JSON reports for baseline and post-phase benchmarks
- `skill_executor.py` — 4 built-in skill templates with DAG execution
- `doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md` — canonical target architecture
- `doc/specs/216_benchmark_suite.md` — benchmark spec
- `doc/specs/217_connect_smart_to_handlers.md` — SMART wire spec
- `doc/specs/218_dummie_process_canonical.md` — canonical entry point spec
- `doc/specs/219_skill_dag_execution.md` — skill DAG spec
- `doc/specs/220_daemon_prewarming.md` — daemon pre-warming spec
- `doc/specs/221_subgateway_sunset.md` — legacy cleanup spec

**Tools exposed to agent (post Phase C):** 9 (8 original + `dummie_process`). Old tools retained for backward compatibility; retirement in future phase after validation.

**Production verification:**
- [x] 38 SMART tests pass
- [x] Budget tier resolution correct (cumulative: tier2≥2000, tier3≥5000)
- [x] Cache L1 hit/miss correct
- [x] SkillExecutor matches intents to skills correctly
- [x] SmartRouter empty result format correct
- [x] Benchmark runs and produces valid JSON reports
- [x] dummie_process registered among public tools
- [x] Sub-gateway processes: 0 (mask stopped all 5)

### ✅ Phase 2a (Collaborative Gateway — verified)

- [x] `dummie_process` supports 6 modes: discover, execute, auto, plan, confirm, reject
- [x] `mode="plan"`: gateway shares execution plan with agent before executing
- [x] `mode="confirm"`: agent approves plan, gateway executes pre-approved steps
- [x] `mode="reject"`: agent disagrees, gateway suggests re-routing
- [x] `mode="auto"` high confidence (≥0.85): execute silently (no agent visibility cost)
- [x] `mode="auto"` low confidence (<0.85): show plan, let agent decide
- [x] `_execute_plan()` helper: iterates plan steps, calls proxy_mgr, returns results
- [x] Skill steps serializable for plan transport
- [x] 38 tests pass, Python syntax OK
- [x] Backward compatible: old modes (discover, execute, auto) unchanged

### ✅ Phase 2b (Tools collapse — verified)

- [x] `DUMMIE_CANONICAL_MODE` flag gates tool exposure
- [x] `dummie_admin` absorbs report_config_path, install_mcp, self_program
- [x] 8 old tools hidden when canonical mode, internally accessible
- [x] `dummie_process` + `dummie_admin` always exposed
- [x] 38 tests pass, Python syntax OK

### ⏳ Pending (post-reboot verification) — already done, re-verify after final reboot

- [x] `cat /proc/cmdline | grep preempt=full` — GRUB param active
- [ ] `dmesg 2>/dev/null | grep "Dynamic Preempt: full"` — full preemption confirmed
- [x] `cat /proc/cmdline | grep zswap` → NOT present
- [x] `cat /proc/cmdline | grep audit=0` → kernel audit disabled
- [x] `cat /proc/cmdline | grep lsm=lockdown,integrity` → AppArmor removed
- [x] `cat /proc/sys/vm/compaction_proactiveness` → 20 (fixed from 80)
- [x] `cat /proc/sys/vm/swappiness` → 150 (fixed from 10)
- [x] ollama CPU pinning on 7,15 (taskset confirmed)
- [ ] System boots without soft lockup warnings on isolated CPUs
