# SysTune: OS Optimization Wave

**Goal:** Apply safe, reversible, high-impact OS optimizations to maximize throughput for DUMMIE Engine workloads (GPU inference, embeddings, agent scheduling).

**Architecture:** All optimizations are sysfs writes, sysctl params, kernel cmdline changes, or process-level tuning — no code changes. Each is independently revertible.

**Order:** Lowest risk first. Steps 1-5 are live-tunable (no reboot). Step 6 requires a scheduled reboot.

---

### Task 1: sysctl restante

- [ ] **Add remaining sysctl tweaks**

```bash
# Dirty pages — increase for write-heavy vector/log workloads (from 15 → 30)
sudo sysctl -w vm.dirty_ratio=30

# zswap compresion stats via debugfs
sudo mount -t debugfs none /sys/kernel/debug/ 2>/dev/null || true
```

- [ ] **Persist in zz-agentic-memory.conf**

Add to `/etc/sysctl.d/zz-agentic-memory.conf`:
```
vm.dirty_ratio=30
```

- [ ] **Verify**

```bash
sysctl vm.dirty_ratio
# Expected: vm.dirty_ratio = 30
```

### Task 2: I/O Priority

- [ ] **Set ionice for ollama**

```bash
sudo ionice -c 2 -n 0 -p $(pgrep -x ollama)
# Best-effort, highest priority within class
```

- [ ] **Persist via systemd override**

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf "[Service]\nIOSchedulingClass=best-effort\nIOSchedulingPriority=0\n" | sudo tee /etc/systemd/system/ollama.service.d/io.conf
```

- [ ] **Verify**

```bash
ionice -p $(pgrep -x ollama)
# Expected: best-effort: priority 0
```

### Task 3: nvidia persistence mode

- [ ] **Switch to persistence mode**

```bash
sudo nvidia-persistenced --persistence-mode
# Or restart with correct flag
```

- [ ] **Persist via override**

```bash
sudo mkdir -p /etc/systemd/system/nvidia-persistenced.service.d
printf "[Service]\nExecStart=\nExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --persistence-mode --verbose\n" | sudo tee /etc/systemd/system/nvidia-persistenced.service.d/persistence.conf
sudo systemctl daemon-reload
sudo systemctl restart nvidia-persistenced
```

- [ ] **Verify**

```bash
nvidia-smi -q | grep "Persistence Mode"
# Expected: Persistence Mode : Enabled
```

### Task 4: zswap enable + tuning

- [ ] **Verify current state**

```bash
cat /sys/module/zswap/parameters/enabled
# Expected: N (disabled)
```

- [ ] **Enable zswap**

```bash
echo Y | sudo tee /sys/module/zswap/parameters/enabled
echo zstd | sudo tee /sys/module/zswap/parameters/compressor
echo 30 | sudo tee /sys/module/zswap/parameters/max_pool_percent
echo Y | sudo tee /sys/module/zswap/parameters/same_filled_pages_enabled
```

- [ ] **Persist via modprobe.d**

```bash
printf "options zswap enabled=Y compressor=zstd max_pool_percent=30 same_filled_pages_enabled=Y\n" | sudo tee /etc/modprobe.d/zswap.conf
```

- [ ] **Verify**

```bash
cat /sys/module/zswap/parameters/enabled
# Expected: Y
grep -c "zswap" /proc/meminfo  # zswap will show stats once active
# Expected: >0 (zswap fields in meminfo)
```

### Task 5: KSM tuning

- [ ] **Tune KSM parameters**

```bash
echo 3000 | sudo tee /sys/kernel/mm/ksm/pages_to_scan
echo 10 | sudo tee /sys/kernel/mm/ksm/sleep_millisecs
echo 1 | sudo tee /sys/kernel/mm/ksm/merge_across_nodes
```

- [ ] **Persist via tmpfiles.d**

```bash
printf "w /sys/kernel/mm/ksm/pages_to_scan - - - - 3000\n" | sudo tee /etc/tmpfiles.d/ksm.conf
printf "w /sys/kernel/mm/ksm/sleep_millisecs - - - - 10\n" | sudo tee -a /etc/tmpfiles.d/ksm.conf
printf "w /sys/kernel/mm/ksm/merge_across_nodes - - - - 1\n" | sudo tee -a /etc/tmpfiles.d/ksm.conf
```

- [ ] **Verify**

```bash
cat /sys/kernel/mm/ksm/pages_to_scan /sys/kernel/mm/ksm/sleep_millisecs /sys/kernel/mm/ksm/merge_across_nodes
# Expected: 3000, 10, 1
```

### Task 6: CPU isolation (requiere reboot)

- [ ] **Edit GRUB_CMDLINE**

```bash
# Isolate cores 0-1 for L0_overseer + system kthreads
# nohz_full=0,1 remueve timer ticks en esos cores
# rcu_nocbs=0,1 offloads RCU callbacks
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="isolcpus=nohz,domain=0,1 nohz_full=0,1 rcu_nocbs=0,1 /' /etc/default/grub
sudo update-grub
```

- [ ] **Reboot**

```bash
sudo reboot
```

- [ ] **Verify after reboot**

```bash
cat /proc/cmdline | grep isolcpus
# Expected: isolcpus=nohz,domain=0,1
cat /sys/devices/system/cpu/isolated
# Expected: 0-1
```

- [ ] **Pin ollama to non-isolated cores**

```bash
sudo systemctl set-property ollama.service CPUSetCPUs=2-15
```

- [ ] **Verify pinning**

```bash
taskset -cp $(pgrep -x ollama)
# Expected: 2-15
```
