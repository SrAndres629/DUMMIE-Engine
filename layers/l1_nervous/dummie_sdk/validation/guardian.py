import os
import sys
from pathlib import Path
from typing import Optional
from .rules import Rule, Violation, Severity, RULES


class ArchitectureGuardian:
    SCAN_DIRS = [
        "layers/l1_nervous",
        "layers/l2_brain",
        "layers/l5_muscle",
        "scripts",
    ]
    EXCLUDE_PATTERNS = [
        "__pycache__",
        ".venv",
        ".git",
        "dummie_sdk",
        "generated",
        "tests/industrial",
    ]

    def __init__(self, root: Optional[Path] = None, rules: Optional[list[Rule]] = None):
        self.root = Path(root or self._find_root())
        self.rules = rules or RULES

    @staticmethod
    def _find_root() -> Path:
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            if (parent / "layers" / "l1_nervous").is_dir():
                return parent
            if (parent / "dummie_sdk").is_dir():
                return parent
        return cwd

    def _should_scan(self, file_path: Path) -> bool:
        rel = str(file_path.relative_to(self.root))
        for exclude in self.EXCLUDE_PATTERNS:
            if exclude in rel:
                return False
        in_scan_dir = any(rel.startswith(d) for d in self.SCAN_DIRS)
        in_root_python = file_path.suffix == ".py" and file_path.parent == self.root
        if not (in_scan_dir or in_root_python):
            return False
        return file_path.suffix in (".py", ".sh", ".yaml", ".yml", ".json")

    def scan_file(self, file_path: Path) -> list[Violation]:
        if not self._should_scan(file_path):
            return []
        try:
            content = file_path.read_text()
        except (OSError, UnicodeDecodeError):
            return []
        rel = str(file_path.relative_to(self.root))
        violations: list[Violation] = []
        for rule in self.rules:
            try:
                violations.extend(rule.check(rel, content))
            except Exception as e:
                violations.append(
                    Violation(
                        file=rel,
                        line=0,
                        severity=Severity.INFO,
                        rule="guardian-error",
                        message=f"Rule '{rule.name}' failed: {e}",
                    )
                )
        return violations

    def scan_all(self) -> list[Violation]:
        all_violations: list[Violation] = []
        for dir_path in self.SCAN_DIRS:
            full_dir = self.root / dir_path
            if not full_dir.is_dir():
                continue
            for fpath in sorted(full_dir.rglob("*")):
                if fpath.is_file():
                    all_violations.extend(self.scan_file(fpath))
        return all_violations

    def report(self, violations: list[Violation]) -> str:
        if not violations:
            return "✓ Architecture Guardian: no violations found"
        lines = [f"Architecture Guardian found {len(violations)} violation(s):"]
        grouped: dict[str, list[Violation]] = {}
        for v in violations:
            grouped.setdefault(v.severity.value, []).append(v)
        for sev in ("error", "warning", "info"):
            for v in grouped.get(sev, []):
                lines.append(v.formatted)
        counts = {s.value: len(grouped.get(s.value, [])) for s in Severity}
        lines.append(
            f"  ({counts['error']} errors, {counts['warning']} warnings, {counts['info']} infos)"
        )
        return "\n".join(lines)

    def enforce(self, violations: list[Violation]) -> int:
        errors = [v for v in violations if v.severity == Severity.ERROR]
        if errors:
            print(self.report(violations), file=sys.stderr)
            print(f"\n❌ {len(errors)} error(s) must be fixed", file=sys.stderr)
            return 1
        if violations:
            print(self.report(violations))
        return 0

    def run_and_enforce(self) -> int:
        violations = self.scan_all()
        return self.enforce(violations)
