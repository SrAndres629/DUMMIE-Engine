#!/usr/bin/env python3
import json
import subprocess
import urllib.request
from pathlib import Path

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

ROOT_DIR = Path(__file__).resolve().parents[1]
GATEWAY_CONFIG = ROOT_DIR / "dummie_gateway_config.json"
SOCKETS_DIR = ROOT_DIR / ".aiwg" / "sockets"

def get_processes():
    try:
        proc = subprocess.run(["ps", "-eo", "pid,comm,args"], capture_output=True, text=True, check=True)
        return proc.stdout.splitlines()
    except Exception as e:
        print(f"{RED}Error fetching processes: {e}{RESET}")
        return []

def check_core_daemons(process_lines):
    print(f"\n{BLUE}=== Core Daemons Status ==={RESET}")
    targets = {
        "Dummied (L0)": "dummied",
        "Monitor (L0)": "monitor",
        "Memory Plane (L1)": "memory_plane",
        "Sidecar (L1)": "l1_sidecar",
        "MCP Gateway (L1/L2)": "mcp_server.py"
    }
    
    found_counts = {name: 0 for name in targets}
    found_pids = {name: [] for name in targets}
    
    for line in process_lines:
        line_lower = line.lower()
        if "dummie_status.py" in line_lower: continue
        if "python3" in line_lower and "scripts/dummie_status.py" in line_lower: continue
        
        for name, pattern in targets.items():
            if pattern in line_lower:
                parts = line.strip().split(maxsplit=2)
                if len(parts) >= 1:
                    found_counts[name] += 1
                    found_pids[name].append(parts[0])

    for name, count in found_counts.items():
        if count == 1:
            print(f" {GREEN}[OK]{RESET} {name} (PID: {found_pids[name][0]})")
        elif count == 0:
            print(f" {YELLOW}[OFF]{RESET} {name} is not running")
        else:
            pids = ", ".join(found_pids[name])
            print(f" {RED}[DUPLICATE]{RESET} {name} is running {count} times! (PIDs: {pids})")

def check_mcp_servers(process_lines):
    print(f"\n{BLUE}=== MCP Gateway Servers ==={RESET}")
    if not GATEWAY_CONFIG.exists():
        print(f" {YELLOW}[WARN]{RESET} Config file not found: {GATEWAY_CONFIG}")
        return

    try:
        data = json.loads(GATEWAY_CONFIG.read_text(encoding="utf-8"))
        servers = data.get("mcpServers", {})
    except Exception as e:
        print(f" {RED}[ERROR]{RESET} Could not read Gateway Config: {e}")
        return
        
    active_servers = []
    disabled_servers = []
    for s_name, s_cfg in servers.items():
        if s_cfg.get("disabled", False):
            disabled_servers.append(s_name)
        else:
            active_servers.append(s_name)
            
    print(f" {CYAN}Configured Servers:{RESET} {len(servers)} ({len(active_servers)} Active, {len(disabled_servers)} Disabled)")
    
    for server in active_servers:
        cmd = servers[server].get("command", "")
        
        pattern = server.lower()
        if "npx" in cmd or "uvx" in cmd:
            args_list = servers[server].get("args", [])
            if len(args_list) > 0:
                pkg = args_list[0]
                if pkg.startswith("-y") and len(args_list) > 1:
                    pkg = args_list[1]
                # Try to extract the package name even if it's scoped like @modelcontextprotocol/server-puppeteer
                if "/" in pkg:
                    pattern = pkg.split("/")[-1].lower()
                else:
                    pattern = pkg.split("@")[0].lower()
                    
        if not pattern:
            pattern = server.lower()
        
        count = 0
        pids = []
        for line in process_lines:
            line_l = line.lower()
            if pattern in line_l and "dummie_status" not in line_l:
                parts = line.strip().split(maxsplit=2)
                if len(parts) >= 1:
                    count += 1
                    pids.append(parts[0])
                    
        if count == 1:
            print(f"  {GREEN}[ACTIVE]{RESET} {server} (PID: {pids[0]})")
        elif count == 0:
            print(f"  {YELLOW}[ORPHANED?]{RESET} {server} (No process strictly matching '{pattern}')")
        else:
            pids_str = ", ".join(pids[:5])
            if len(pids) > 5:
                pids_str += f", ... (+{len(pids)-5} more)"
            print(f"  {RED}[DUPLICATE]{RESET} {server} is running {count} times! (PIDs: {pids_str})")

def check_ollama():
    print(f"\n{BLUE}=== Ollama Integration ==={RESET}")
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                models = [m["name"] for m in data.get("models", [])]
                print(f" {GREEN}[ONLINE]{RESET} Ollama Daemon is responding.")
                print(f" Installed Models ({len(models)}): {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
            else:
                 print(f" {YELLOW}[WARN]{RESET} Ollama returned status {response.status}")
    except Exception:
         print(f" {YELLOW}[OFFLINE]{RESET} Ollama is not responding on port 11434.")
         return

    try:
        req = urllib.request.Request("http://localhost:11434/api/ps", method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                loaded = data.get("models", [])
                if loaded:
                    print(f" {MAGENTA}>> Models loaded in VRAM:{RESET}")
                    for m in loaded:
                        print(f"    - {m['name']} (Size: {m.get('size', 0)/1024/1024/1024:.2f} GB)")
                else:
                    print(f" {CYAN}>> VRAM Status:{RESET} No models currently loaded in memory.")
    except Exception:
        pass

def check_sockets():
    print(f"\n{BLUE}=== Sockets & IPC ==={RESET}")
    expected_sockets = ["dummied.sock", "flight.sock"]
    for sock in expected_sockets:
        path = SOCKETS_DIR / sock
        if path.exists():
            print(f" {GREEN}[OK]{RESET} {sock} is present")
        else:
            print(f" {YELLOW}[MISSING]{RESET} {sock}")

def main():
    print(f"{CYAN}=========================================={RESET}")
    print(f"{CYAN}      DUMMIE ENGINE STATUS DASHBOARD      {RESET}")
    print(f"{CYAN}=========================================={RESET}")
    
    procs = get_processes()
    check_core_daemons(procs)
    check_mcp_servers(procs)
    check_ollama()
    check_sockets()
    print("")

if __name__ == "__main__":
    main()
