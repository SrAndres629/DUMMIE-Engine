#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import re
from datetime import datetime, timezone

# Path references
AIWG_DIR = ".aiwg"
STATE_TRUTH = os.path.join(AIWG_DIR, "state", "current_truth.json")
ROADMAP_JSON = os.path.join(AIWG_DIR, "roadmap", "pack_roadmap_to_6_1.json")
ACTIVE_PACK = os.path.join(AIWG_DIR, "packs", "active_pack.json")
HISTORY_JSONL = os.path.join(AIWG_DIR, "packs", "pack_execution_history.jsonl")
DISTANCE_JSON = os.path.join(AIWG_DIR, "metrics", "project_distance_to_6_1.json")
CRITIQUE_JSON = os.path.join(AIWG_DIR, "reports", "pack_self_critique_latest.json")
CRITIQUE_MD = os.path.join(AIWG_DIR, "reports", "pack_self_critique_latest.md")
DECISION_LOG = os.path.join(AIWG_DIR, "decisions", "decision_log.jsonl")
EVIDENCE_JSON = os.path.join(AIWG_DIR, "reports", "pack_validation_evidence_latest.json")
EVIDENCE_MD = os.path.join(AIWG_DIR, "reports", "pack_validation_evidence_latest.md")

def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_git_head():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"

def run_preflight(args):
    print("=== [AIWG PACK GUARD] PREFLIGHT CHECK ===")
    
    # 1. Verify files exist
    if not os.path.exists(ACTIVE_PACK):
        print("ERROR: active_pack.json does not exist under .aiwg/packs/")
        sys.exit(1)
    if not os.path.exists(STATE_TRUTH):
        print("ERROR: current_truth.json does not exist under .aiwg/state/")
        sys.exit(1)
        
    active = load_json(ACTIVE_PACK)
    truth = load_json(STATE_TRUTH)
    
    if not active:
        print("ERROR: Failed to parse active_pack.json")
        sys.exit(1)
    if not truth:
        print("ERROR: Failed to parse current_truth.json")
        sys.exit(1)
        
    # 2. Check head_commit stale
    git_head = get_git_head()
    truth_head = truth.get("head_commit")
    if truth_head != git_head:
        print(f"ERROR: current_truth.json head_commit ({truth_head}) is stale. Current actual HEAD: {git_head}")
        sys.exit(1)
        
    # 3. Check rollback
    rollback = active.get("rollback_plan") or active.get("rollback")
    if not rollback or not isinstance(rollback, str) or len(rollback.strip()) == 0 or rollback.strip() == "UNVERIFIED":
        print("ERROR: Active pack contract is missing a rollback_plan.")
        sys.exit(1)
        
    # 4. Check tests_required
    tests = active.get("tests_required") or active.get("tests")
    if not tests or not isinstance(tests, list) or len(tests) == 0:
        print("ERROR: Active pack contract is missing tests_required.")
        sys.exit(1)
        
    # 5. Check stop_conditions
    stops = active.get("stop_conditions")
    if not stops or not isinstance(stops, list) or len(stops) == 0:
        print("ERROR: Active pack contract is missing stop_conditions.")
        sys.exit(1)
        
    # 6. Check transition skip (e.g. attempting to start PACK_3.2 without completed PACK_3.1)
    pack_id = active.get("pack_id")
    last_completed = truth.get("last_completed_pack")
    
    if pack_id == "PACK_3.2" and last_completed != "PACK_3.1":
        print(f"ERROR: Cannot start {pack_id} while last_completed_pack is {last_completed} (expected PACK_3.1).")
        sys.exit(1)
        
    # 7. Check report drift (if files exist on disk)
    reports = truth.get("latest_reports", {})
    for name, path in reports.items():
        if not os.path.exists(path):
            print(f"ERROR: Report drift detected. Registered report '{name}' is missing at: {path}")
            sys.exit(1)
            
    print("SUCCESS: Preflight passed successfully.")
    sys.exit(0)

def validate_critique_field(field_name, val):
    if not val:
        return "UNVERIFIED"
    val_strip = str(val).strip()
    if not val_strip or val_strip.upper() == "UNVERIFIED":
        return "UNVERIFIED"
    
    # Check optimistic defaults
    optimistic_patterns = [
        r"^ninguno\b",
        r"^100%",
        r"^ninguna reparaci\u00f3n pendiente",
        r"^se preserva.*al 100%"
    ]
    for pattern in optimistic_patterns:
        if re.search(pattern, val_strip, re.IGNORECASE):
            print(f"WARNING: Rejected optimistic default value '{val_strip}' for field '{field_name}'")
            return "UNVERIFIED"
            
    return val_strip

def run_self_critique(args):
    print("=== [AIWG PACK GUARD] SELF-CRITIQUE GENERATION ===")
    
    if not os.path.exists(ACTIVE_PACK):
        print("ERROR: active_pack.json is required to generate self-critique.")
        sys.exit(1)
        
    active = load_json(ACTIVE_PACK)
    pack_id = active.get("pack_id", "UNKNOWN_PACK")
    
    answers = {
        "what_implemented": validate_critique_field("what_implemented", args.what),
        "what_broken": validate_critique_field("what_broken", args.broken),
        "metrics_changed": validate_critique_field("metrics_changed", args.metrics),
        "tests_shallow": validate_critique_field("tests_shallow", args.shallow),
        "reports_stale": validate_critique_field("reports_stale", args.stale),
        "assumptions": validate_critique_field("assumptions", args.assumptions),
        "repairs_needed": validate_critique_field("repairs_needed", args.repairs),
        "advances_degraded": validate_critique_field("advances_degraded", args.degraded),
        "advances_goal_6_1": validate_critique_field("advances_goal_6_1", args.goal)
    }
    
    # If any answer is UNVERIFIED, print warning but save it (closeout will fail)
    has_unverified = False
    for k, v in answers.items():
        if v == "UNVERIFIED":
            print(f"CRITICAL WARNING: Field '{k}' is UNVERIFIED.")
            has_unverified = True
            
    critique_data = {
        "pack_id": pack_id,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "answers": answers
    }
    
    save_json(CRITIQUE_JSON, critique_data)
    
    # Save a permanent copy for this specific pack under reports/self_critiques/
    archive_dir = os.path.join(AIWG_DIR, "reports", "self_critiques")
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f"{pack_id}.md")
    
    # Generate MD format
    md_content = f"""# Pack Self-Critique — {pack_id}

* **Generated At**: {critique_data["generated_at"]}

## Respuestas Obligatorias

### 1. ¿Qué implementé exactamente?
{critique_data["answers"]["what_implemented"]}

### 2. ¿Qué rompí o pude haber degradado potencialmente?
{critique_data["answers"]["what_broken"]}

### 3. ¿Qué avance anterior pude haber degradado?
{critique_data["answers"]["advances_degraded"]}

### 4. ¿Qué métricas cambiaron inesperadamente?
{critique_data["answers"]["metrics_changed"]}

### 5. ¿Qué tests son todavía superficiales?
{critique_data["answers"]["tests_shallow"]}

### 6. ¿Qué reportes pueden estar stale?
{critique_data["answers"]["reports_stale"]}

### 7. ¿Qué estoy asumiendo sin evidencia?
{critique_data["answers"]["assumptions"]}

### 8. ¿Qué debo reparar antes del commit?
{critique_data["answers"]["repairs_needed"]}

### 9. ¿Este pack acerca al objetivo 6.1 o solo agrega complejidad?
{critique_data["answers"]["advances_goal_6_1"]}
"""
    
    with open(CRITIQUE_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"SUCCESS: Generated self-critique reports under {CRITIQUE_JSON}, {CRITIQUE_MD} and archive {archive_path}")
    
    if has_unverified:
        print("ERROR: Self-critique is incomplete (contains UNVERIFIED answers).")
        sys.exit(1)
        
    sys.exit(0)

def run_record_evidence(args):
    print("=== [AIWG PACK GUARD] RECORDING EVIDENCE ===")
    git_head = get_git_head()
    
    # Validate exit code
    exit_code = int(args.exit_code)
    result = "PASSED" if exit_code == 0 else "FAILED"
    
    evidence_data = {
        "command": args.cmd or "UNKNOWN_COMMAND",
        "exit_code": exit_code,
        "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "finished_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cwd": os.getcwd(),
        "python_executable": args.python or sys.executable,
        "commit": git_head,
        "result": result,
        "suite_name": args.suite or "pytest"
    }
    
    save_json(EVIDENCE_JSON, evidence_data)
    
    md_content = f"""# Pack Validation Evidence

* **Result**: {result}
* **Suite Name**: {evidence_data["suite_name"]}
* **Commit**: {evidence_data["commit"]}
* **Finished At**: {evidence_data["finished_at"]}
* **Command**: `{evidence_data["command"]}`
* **Exit Code**: {evidence_data["exit_code"]}
* **Python Executable**: `{evidence_data["python_executable"]}`
"""
    with open(EVIDENCE_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"SUCCESS: Evidence recorded in {EVIDENCE_JSON} and {EVIDENCE_MD}")
    sys.exit(0)

def run_closeout(args):
    print("=== [AIWG PACK GUARD] CLOSEOUT AUDIT ===")
    
    # 1. Check self-critique exists
    if not os.path.exists(CRITIQUE_JSON):
        print("ERROR: Closeout failed. Missing latest self-critique json report.")
        sys.exit(1)
        
    critique = load_json(CRITIQUE_JSON)
    if not critique:
        print("ERROR: Failed to parse latest self-critique json report.")
        sys.exit(1)
        
    # Check for UNVERIFIED in self-critique
    for k, v in critique.get("answers", {}).items():
        if v == "UNVERIFIED" or not v:
            print(f"ERROR: Self-critique answer for '{k}' is UNVERIFIED. Cannot close out.")
            sys.exit(1)
            
    # 2. Check if validation evidence exists
    if not os.path.exists(EVIDENCE_JSON):
        print("ERROR: Closeout failed. Missing pack_validation_evidence_latest.json")
        sys.exit(1)
        
    evidence = load_json(EVIDENCE_JSON)
    if not evidence:
        print("ERROR: Failed to parse pack_validation_evidence_latest.json")
        sys.exit(1)
        
    # Check evidence exit code
    if evidence.get("exit_code") != 0:
        print(f"ERROR: Closeout failed. Stored validation evidence shows exit_code = {evidence.get('exit_code')}")
        sys.exit(1)
        
    # Check evidence commit matches actual HEAD
    git_head = get_git_head()
    if evidence.get("commit") != git_head:
        print(f"ERROR: Validation evidence is stale. Evidence commit: {evidence.get('commit')}, actual HEAD: {git_head}")
        sys.exit(1)
        
    active = load_json(ACTIVE_PACK)
    truth = load_json(STATE_TRUTH)
    dist = load_json(DISTANCE_JSON)
    roadmap = load_json(ROADMAP_JSON)
    
    if not active:
        print("ERROR: active_pack.json is missing or corrupted.")
        sys.exit(1)
    if not truth:
        print("ERROR: current_truth.json is missing or corrupted.")
        sys.exit(1)
    if not dist:
        print("ERROR: project_distance_to_6_1.json is missing or corrupted.")
        sys.exit(1)
    if not roadmap:
        print("ERROR: pack_roadmap_to_6_1.json is missing or corrupted.")
        sys.exit(1)
        
    # Check head_commit stale
    truth_head = truth.get("head_commit")
    if truth_head != git_head:
        print(f"ERROR: current_truth.json is stale. Current HEAD: {git_head}, current_truth: {truth_head}")
        sys.exit(1)
        
    # Check if current_truth last completed matches or if current_pack matches
    pack_id = active.get("pack_id")
    if truth.get("current_pack") != pack_id:
        print(f"ERROR: Closeout mismatch. current_truth.json represents current_pack={truth.get('current_pack')}, expected {pack_id}.")
        sys.exit(1)
        
    # Check active pack rollback and stop conditions
    rollback = active.get("rollback_plan") or active.get("rollback")
    if not rollback or rollback == "UNVERIFIED" or len(rollback.strip()) == 0:
        print("ERROR: Active pack contract is missing rollback_plan.")
        sys.exit(1)
        
    stops = active.get("stop_conditions")
    if not stops or len(stops) == 0:
        print("ERROR: Active pack contract is missing stop_conditions.")
        sys.exit(1)
        
    # Check roadmap source commits for valid SHAs
    for pack in roadmap.get("packs", []):
        sha = pack.get("source_of_truth_commit")
        if sha and sha != "UNVERIFIED":
            if not re.match(r"^[a-f0-9]{7,40}$", sha):
                print(f"ERROR: Invalid source_of_truth_commit '{sha}' in roadmap for pack '{pack.get('pack_id')}'")
                sys.exit(1)
                
    # 3. Check history has been updated or history file exists
    if not os.path.exists(HISTORY_JSONL):
        print("ERROR: Closeout failed. pack_execution_history.jsonl does not exist.")
        sys.exit(1)
        
    # Check decision log exists
    if not os.path.exists(DECISION_LOG):
        print("ERROR: Closeout failed. decision_log.jsonl does not exist.")
        sys.exit(1)
        
    # 4. Check if validate_specs_docs.py is present in the workspace
    if not os.path.exists("scripts/validate_specs_docs.py"):
        print("ERROR: validate_specs_docs.py is missing from workspace.")
        sys.exit(1)
        
    print("SUCCESS: Closeout audit passed. Pack is ready to be closed and committed.")
    sys.exit(0)

def run_distance(args):
    print("=== [AIWG PACK GUARD] DISTANCE TO 6.1 ===")
    
    if not os.path.exists(DISTANCE_JSON):
        print("ERROR: project_distance_to_6_1.json is missing.")
        sys.exit(1)
        
    dist = load_json(DISTANCE_JSON)
    if not dist:
        print("ERROR: Failed to parse project_distance_to_6_1.json")
        sys.exit(1)
        
    # Check if there are subjective unmeasured claims (e.g. improvement percentages without measured/estimated/unverified classification)
    allowed_states = ["measured", "estimated", "unverified"]
    for k, v in dist.items():
        if k.endswith("_status") or k.endswith("_state"):
            if v not in allowed_states:
                print(f"ERROR: Distance metric state '{v}' for '{k}' is invalid (must be measured, estimated, or unverified).")
                sys.exit(1)
                
    current_score = dist.get("current_score", 0.0)
    print(f"Current completion score towards Pack 6.1 (Golden Path): {current_score:.2f} (Scale 0.0 to 1.0)")
    print(f"Next leverage pack: {dist.get('next_highest_leverage_pack')}")
    print(f"Why: {dist.get('why_this_pack_next')}")
    
    # Check if long_term_objectives targets Pack 6.1
    lt_obj = load_json(os.path.join(AIWG_DIR, "roadmap", "long_term_objectives.json"))
    if not lt_obj or lt_obj.get("long_term_target") != "PACK_6.1":
        print("WARNING: Long term objectives target does not point to PACK_6.1!")
        sys.exit(1)
        
    sys.exit(0)

def run_next_pack(args):
    print("=== [AIWG PACK GUARD] NEXT SCHEDULED PACK ===")
    
    if not os.path.exists(STATE_TRUTH):
        print("ERROR: current_truth.json is missing.")
        sys.exit(1)
        
    truth = load_json(STATE_TRUTH)
    next_pack = truth.get("next_pack")
    last_completed = truth.get("last_completed_pack")
    
    print(f"Last completed pack: {last_completed}")
    print(f"Next scheduled pack: {next_pack}")
    
    # Enforce anti-skip rule
    if next_pack == "PACK_3.2" and last_completed != "PACK_3.1":
        print("ERROR: Anti-skip gate active. PACK_3.1 must be closed in main first.")
        sys.exit(1)
        
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="AIWG Pack Governance Guard Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Preflight
    subparsers.add_parser("preflight", help="Validate active pack contract preconditions")
    
    # Self-critique
    sc_parser = subparsers.add_parser("self-critique", help="Generate self-critique answers")
    sc_parser.add_argument("--what", help="What was implemented exactly?")
    sc_parser.add_argument("--broken", help="What was potentially broken/degraded?")
    sc_parser.add_argument("--metrics", help="What metrics changed unexpectedly?")
    sc_parser.add_argument("--shallow", help="What tests are shallow?")
    sc_parser.add_argument("--stale", help="What reports might be stale?")
    sc_parser.add_argument("--assumptions", help="What assumptions are made?")
    sc_parser.add_argument("--repairs", help="What needs to be repaired?")
    sc_parser.add_argument("--degraded", help="What previous advances were degraded?")
    sc_parser.add_argument("--goal", help="How does this pack move towards Golden Path 6.1?")
    
    # Record Evidence
    re_parser = subparsers.add_parser("record-evidence", help="Record test validation evidence")
    re_parser.add_argument("--suite", required=True, help="Test suite name")
    re_parser.add_argument("--cmd", required=True, help="Command executed")
    re_parser.add_argument("--exit-code", required=True, help="Exit code of the execution")
    re_parser.add_argument("--python", help="Python path used")
    
    # Closeout
    subparsers.add_parser("closeout", help="Perform final closeout checks before merge")
    
    # Distance
    subparsers.add_parser("distance", help="Measure project distance metrics towards Pack 6.1")
    
    # Next Pack
    subparsers.add_parser("next-pack", help="Report next scheduled pack and check skip violations")
    
    args = parser.parse_args()
    
    if args.command == "preflight":
        run_preflight(args)
    elif args.command == "self-critique":
        run_self_critique(args)
    elif args.command == "record-evidence":
        run_record_evidence(args)
    elif args.command == "closeout":
        run_closeout(args)
    elif args.command == "distance":
        run_distance(args)
    elif args.command == "next-pack":
        run_next_pack(args)

if __name__ == "__main__":
    main()
