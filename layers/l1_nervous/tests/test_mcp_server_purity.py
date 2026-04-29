"""
[T2] Tests estáticos de regresión para mcp_server.py STDIO purity.
Verifica que:
- sys.stdout = sys.stderr NO aparece fuera de if __name__
- sys.path.insert ocurrencias están limitadas
"""
import re
from pathlib import Path


MCP_SERVER = Path(__file__).resolve().parents[1] / "mcp_server.py"


def _read_source():
    return MCP_SERVER.read_text()


def _split_main_guard(source: str):
    """Divide el source en (before_main, after_main) basado en 'if __name__'."""
    lines = source.split("\n")
    main_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('if __name__'):
            main_idx = i
            break
    if main_idx is None:
        return source, ""
    return "\n".join(lines[:main_idx]), "\n".join(lines[main_idx:])


def test_stdout_mutation_only_inside_main_guard():
    """sys.stdout = sys.stderr must NOT appear at module level."""
    source = _read_source()
    before_main, _after_main = _split_main_guard(source)
    
    # Buscar `sys.stdout = sys.stderr` fuera del __main__ guard
    pattern = re.compile(r"sys\.stdout\s*=\s*sys\.stderr")
    matches = pattern.findall(before_main)
    assert len(matches) == 0, (
        f"Found {len(matches)} occurrence(s) of 'sys.stdout = sys.stderr' "
        f"outside of 'if __name__' guard. This mutates stdout globally "
        f"and corrupts any module that imports mcp_server."
    )


def test_sys_path_insert_count_limited():
    """sys.path.insert should appear at most in the documented loop (≤ 2 occurrences)."""
    source = _read_source()
    pattern = re.compile(r"sys\.path\.insert")
    matches = pattern.findall(source)
    # Una ocurrencia en el loop, posiblemente una en un test path setup
    assert len(matches) <= 2, (
        f"Found {len(matches)} occurrences of sys.path.insert. "
        f"Expected ≤ 2. Each new insertion increases import collision risk."
    )


def test_technical_debt_documented():
    """The sys.path hack must be documented with TECHNICAL DEBT marker."""
    source = _read_source()
    assert "TECHNICAL DEBT" in source, (
        "sys.path manipulation must be documented with a "
        "'TECHNICAL DEBT' marker for traceability."
    )


def test_main_guard_exists():
    """mcp_server.py must have an 'if __name__' guard."""
    source = _read_source()
    assert 'if __name__' in source, (
        "mcp_server.py must have an 'if __name__' guard to prevent "
        "side effects when imported as a module."
    )
