import json
from pathlib import Path
from layers.l2_brain.structural_hardening.bindings import ContractBindingRegistry
from layers.l2_brain.freshness_ledger import load_freshness_ledger

def test_structural_triage_clean_gate():
    # 1. Assert exactly 0 UNKNOWN and 0 ORPHAN_TEST_CANDIDATE in the compiled triage report
    report_path = Path.cwd() / ".aiwg" / "reports" / "structural_hardening_triage_latest.json"
    assert report_path.exists(), "Latest structural hardening triage report must exist"
    
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    unknowns = [find["path"] for find in data["findings"] if find["proposed_class"] == "UNKNOWN"]
    orphans = [find["path"] for find in data["findings"] if find["proposed_class"] == "ORPHAN_TEST_CANDIDATE"]
    
    assert len(unknowns) == 0, f"Found {len(unknowns)} UNKNOWN files in triage: {unknowns}"
    assert len(orphans) == 0, f"Found {len(orphans)} ORPHAN_TEST_CANDIDATE files in triage: {orphans}"

def test_registry_bindings_integrity_gate():
    # 2. Assert that all registered bindings in ContractBindingRegistry are structurally valid on disk
    registry = ContractBindingRegistry()
    bindings = registry.get_all_bindings()
    
    missing_specs_total = []
    missing_tests_total = []
    missing_runtime_total = []
    
    for binding in bindings:
        # Evaluate binding validation
        _, validation = registry.evaluate(
            binding.path,
            repo_root=Path.cwd(),
            evidence={"evidence_refs": binding.evidence_refs}
        )
        if validation:
            # Skip checking test refs or runtime refs for frozen legacy scripts
            if "doc/.deprecated/" in binding.path:
                continue
            if validation.missing_spec_refs:
                missing_specs_total.append((binding.path, validation.missing_spec_refs))
            if validation.missing_test_refs:
                missing_tests_total.append((binding.path, validation.missing_test_refs))
            if validation.missing_runtime_refs:
                missing_runtime_total.append((binding.path, validation.missing_runtime_refs))
                
    assert not missing_specs_total, f"Bindings with missing specs on disk: {missing_specs_total}"
    assert not missing_tests_total, f"Bindings with missing tests on disk: {missing_tests_total}"
    assert not missing_runtime_total, f"Bindings with missing runtimes on disk: {missing_runtime_total}"

def test_freshness_ledger_gate():
    # 3. Assert that the freshness ledger is generated and contains the core components
    ledger_path = Path.cwd() / ".aiwg" / "reports" / "freshness_ledger.json"
    assert ledger_path.exists(), "Freshness ledger report must be compiled"
    
    ledger = load_freshness_ledger(ledger_path)
    assert ledger.entries, "Freshness ledger entries must not be empty"
    
    # Assert there are no missing files in the freshness ledger
    missing_artifacts = [e.artifact_id for e in ledger.entries if e.freshness_status == "missing"]
    assert not missing_artifacts, f"Missing artifacts in freshness ledger: {missing_artifacts}"
