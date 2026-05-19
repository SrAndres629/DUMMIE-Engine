# Spec Reference: 192_embedding_mesh_foundation
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from .contracts import EvidenceType


class EvidenceCollector:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.specs_dir = self.repo_root / "doc" / "specs"
        self.tests_dir = self.repo_root / "layers" / "l2_brain" / "tests"
        self.layers_dir = self.repo_root / "layers"
        
        self.spec_files: Set[str] = set()
        self.spec_ids: Set[str] = set()
        self.spec_references: Dict[str, Set[str]] = {}  # file_path -> references found in specs
        self.test_references: Dict[str, Set[str]] = {}  # file_path -> tests that import/reference it
        
        self.physical_map_refs: Set[str] = set()
        self.core_spec_refs: Set[str] = set()
        
        self._load_physical_map()
        self._load_core_spec()
        self._index_specs()
        self._index_tests()

    def _load_physical_map(self):
        physical_map = self.repo_root / "doc" / "PHYSICAL_MAP.md"
        if physical_map.exists():
            try:
                content = physical_map.read_text(errors="ignore")
                # find any path-like patterns e.g. layers/l2_brain/something.py
                for m in re.finditer(r"(layers/[a-zA-Z0-9_\-/]+\.[a-zA-Z0-9]+)", content):
                    self.physical_map_refs.add(m.group(1).strip())
            except Exception:
                pass

    def _load_core_spec(self):
        core_spec = self.repo_root / "doc" / "CORE_SPEC.md"
        if core_spec.exists():
            try:
                content = core_spec.read_text(errors="ignore")
                for m in re.finditer(r"(layers/[a-zA-Z0-9_\-/]+\.[a-zA-Z0-9]+)", content):
                    self.core_spec_refs.add(m.group(1).strip())
            except Exception:
                pass

    def _index_specs(self):
        if not self.specs_dir.exists():
            return
        
        for root, _, files in os.walk(self.specs_dir):
            for file in files:
                rel_path = Path(root).relative_to(self.repo_root) / file
                rel_path_str = str(rel_path)
                self.spec_files.add(rel_path_str)
                
                # Check for Spec ID in name e.g. 192_embedding_mesh_foundation
                m = re.match(r"(\d+)_", file)
                if m:
                    self.spec_ids.add(m.group(1))
                
                # Scan spec content for file references
                try:
                    full_path = Path(root) / file
                    content = full_path.read_text(errors="ignore")
                    
                    # Look for references to other files e.g. `layers/l2_brain/something.py`
                    for ref_match in re.finditer(r"(layers/[a-zA-Z0-9_\-/]+\.[a-zA-Z0-9]+)", content):
                        ref_path = ref_match.group(1).strip()
                        if ref_path not in self.spec_references:
                            self.spec_references[ref_path] = set()
                        self.spec_references[ref_path].add(rel_path_str)
                except Exception:
                    pass

    def _index_tests(self):
        if not self.layers_dir.exists():
            return
        
        # Scan all test files across layers
        for root, _, files in os.walk(self.layers_dir):
            for file in files:
                if not (file.startswith("test_") and file.endswith(".py")):
                    continue
                
                rel_test_path = Path(root).relative_to(self.repo_root) / file
                rel_test_path_str = str(rel_test_path)
                
                try:
                    full_path = Path(root) / file
                    content = full_path.read_text(errors="ignore")
                    
                    # Extract imports e.g., "from layers.l2_brain.embedding_mesh.router import ..."
                    # or "import layers.l2_brain.embedding_mesh.router"
                    # We can do a search for module names
                    for import_match in re.finditer(r"layers\.[a-zA-Z0-9_.]+", content):
                        mod_name = import_match.group(0)
                        # Map to possible file path
                        parts = mod_name.split(".")
                        # Try to resolve layers/l2_brain/embedding_mesh/router.py or init.py
                        candidate_file = "/".join(parts) + ".py"
                        if candidate_file not in self.test_references:
                            self.test_references[candidate_file] = set()
                        self.test_references[candidate_file].add(rel_test_path_str)
                        
                        # Also register package root init files
                        package_init = "/".join(parts[:-1]) + "/__init__.py"
                        if package_init not in self.test_references:
                            self.test_references[package_init] = set()
                        self.test_references[package_init].add(rel_test_path_str)
                except Exception:
                    pass

    def collect_evidence(self, file_path: str) -> Dict[EvidenceType, List[str]]:
        evidence: Dict[EvidenceType, List[str]] = {}
        file_path_clean = file_path.replace("\\", "/").strip("/")
        full_file_path = self.repo_root / file_path_clean
        
        if full_file_path.exists():
            evidence[EvidenceType.FILE_EXISTS] = [f"File physically exists at {file_path_clean}"]
            
        # Check physical map or core spec reference
        if file_path_clean in self.physical_map_refs:
            evidence[EvidenceType.PHYSICAL_MAP_REFERENCE] = [f"Referenced in doc/PHYSICAL_MAP.md"]
        if file_path_clean in self.core_spec_refs:
            evidence[EvidenceType.CORE_SPEC_REFERENCE] = [f"Referenced in doc/CORE_SPEC.md"]
            
        # Check if referenced by specs
        if file_path_clean in self.spec_references:
            evidence[EvidenceType.REFERENCED_BY_SPEC] = list(self.spec_references[file_path_clean])
            
        # Check if referenced/imported by tests
        if file_path_clean in self.test_references:
            evidence[EvidenceType.REFERENCED_BY_TEST] = list(self.test_references[file_path_clean])
            
        # Naming matches
        p = Path(file_path_clean)
        if p.name.startswith("test_") and p.suffix == ".py":
            evidence[EvidenceType.TEST_NAMING_MATCH] = [f"File name starts with 'test_' and has Python extension"]
            # Look for corresponding runtime
            stem = p.stem[5:]  # remove "test_"
            # Check if there is a runtime file with this stem
            for root, _, files in os.walk(self.layers_dir):
                if f"{stem}.py" in files:
                    found_rel = Path(root).relative_to(self.repo_root) / f"{stem}.py"
                    evidence[EvidenceType.REFERENCES_RUNTIME] = [str(found_rel)]
                    
        # Check spec frontmatter
        if file_path_clean.startswith("doc/specs/") and p.suffix == ".md":
            try:
                content = full_file_path.read_text(errors="ignore")
                if "spec_id:" in content or "Spec Reference:" in content or "# Spec" in content:
                    evidence[EvidenceType.SPEC_FRONTMATTER_MATCH] = ["File content contains valid specification identifiers"]
            except Exception:
                pass
                
        # Generated check
        if "generated/" in file_path_clean or "pb2" in p.name:
            evidence[EvidenceType.GENERATED_MARKER] = [f"File resides in a generated path or matches protobuf suffixes"]
        else:
            try:
                if full_file_path.is_file():
                    content = full_file_path.read_text(errors="ignore")
                    if any(marker in content for marker in ["autogenerated", "AUTO-GENERATED", "Code generated", "DO NOT EDIT"]):
                        evidence[EvidenceType.GENERATED_MARKER] = [f"Autogenerated header token found in content"]
            except Exception:
                pass

        # Legacy check
        if "legacy/" in file_path_clean or ".deprecated/" in file_path_clean:
            evidence[EvidenceType.LEGACY_PATH] = ["File resides in a legacy or deprecated directory"]
            
        # Config check
        if p.name in ["pyproject.toml", "package.json", "go.mod", "mix.exs", "Makefile", "Dockerfile", "setup.py", "poetry.lock"]:
            evidence[EvidenceType.PACKAGE_MANIFEST] = ["Package manager configuration manifest"]
            
        return evidence
