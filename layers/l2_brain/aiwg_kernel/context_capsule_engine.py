import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class TokenBudgetPolicy:
    def __init__(self, max_tokens: int = 16000):
        self.max_tokens = max_tokens

    def estimate_tokens(self, text: str) -> int:
        """
        A crude but fast token estimation: 1 token ~= 4 chars
        """
        return len(text) // 4

    def is_within_budget(self, text: str) -> bool:
        return self.estimate_tokens(text) <= self.max_tokens

class IncrementalIndexer:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.index_file = self.cache_dir / "source_hash_index.json"
        self._index: Dict[str, str] = self._load_index()

    def _load_index(self) -> Dict[str, str]:
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def compute_file_hash(self, file_path: str) -> Optional[str]:
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return None
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def has_changed(self, file_path: str) -> bool:
        current_hash = self.compute_file_hash(file_path)
        if not current_hash:
            return True
        return self._index.get(file_path) != current_hash

    def update_index(self, file_path: str):
        current_hash = self.compute_file_hash(file_path)
        if current_hash:
            self._index[file_path] = current_hash
            self._save_index()

class ContextCapsuleCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.capsule_dir = self.cache_dir / "capsules"
        self.capsule_dir.mkdir(parents=True, exist_ok=True)

    def _capsule_hash(self, file_paths: List[str]) -> str:
        h = hashlib.sha256()
        for fp in sorted(file_paths):
            h.update(fp.encode())
        return h.hexdigest()

    def get_capsule(self, file_paths: List[str]) -> Optional[Dict[str, Any]]:
        c_hash = self._capsule_hash(file_paths)
        c_path = self.capsule_dir / f"{c_hash}.json"
        if c_path.exists():
            try:
                with open(c_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return None

    def save_capsule(self, file_paths: List[str], capsule: Dict[str, Any]):
        c_hash = self._capsule_hash(file_paths)
        c_path = self.capsule_dir / f"{c_hash}.json"
        with open(c_path, "w") as f:
            json.dump(capsule, f, indent=2)

class ContextCapsuleEngine:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.cache_dir = self.workspace_root / ".aiwg" / "memory" / "context_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.indexer = IncrementalIndexer(self.cache_dir)
        self.capsule_cache = ContextCapsuleCache(self.cache_dir)
        self.budget_policy = TokenBudgetPolicy()

    def compile_capsule(self, file_paths: List[str], max_tokens: int = 16000) -> Dict[str, Any]:
        """
        Compiles a context capsule, leveraging incremental caching and diffing.
        """
        self.budget_policy.max_tokens = max_tokens
        
        # 1. Check if any file changed
        needs_rebuild = False
        for fp in file_paths:
            if self.indexer.has_changed(fp):
                needs_rebuild = True
                break
                
        # 2. If no files changed, try to return from cache
        if not needs_rebuild:
            cached_capsule = self.capsule_cache.get_capsule(file_paths)
            if cached_capsule:
                print("[CONTEXT CAPSULE] Cache HIT. Reusing previous capsule.")
                return cached_capsule
                
        # 3. Rebuild capsule
        print("[CONTEXT CAPSULE] Cache MISS or files changed. Building new capsule...")
        
        capsule_content = {}
        total_text = ""
        
        for fp in file_paths:
            full_path = self.workspace_root / fp
            if full_path.exists() and full_path.is_file():
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    capsule_content[fp] = content
                    total_text += content
                self.indexer.update_index(fp)
                
        # 4. Token Budget Evaluation
        estimated_tokens = self.budget_policy.estimate_tokens(total_text)
        is_within_budget = estimated_tokens <= max_tokens
        
        capsule = {
            "files": capsule_content,
            "metadata": {
                "estimated_tokens": estimated_tokens,
                "is_within_budget": is_within_budget,
                "token_limit": max_tokens
            }
        }
        
        # 5. Save to cache
        self.capsule_cache.save_capsule(file_paths, capsule)
        
        return capsule

    def reuse_context_from_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """
        Receipt-based context reuse. Loads the context used in a previous execution.
        """
        receipt_path = self.workspace_root / ".aiwg" / "reports" / f"receipt_{receipt_id}.json"
        if not receipt_path.exists():
            return None
            
        with open(receipt_path, "r") as f:
            receipt = json.load(f)
            
        # In a real scenario, the receipt would have a capsule hash or list of files
        file_paths = receipt.get("context_files", [])
        if not file_paths:
            return None
            
        return self.compile_capsule(file_paths)
