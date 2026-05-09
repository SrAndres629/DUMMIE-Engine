import ast
from pathlib import Path
from typing import Dict, List, Set

class ASTBlastRadiusIndexer:
    """
    [L2_BRAIN] Mapeador estático de código basado en Árboles de Sintaxis Abstracta (AST).
    Permite anticipar el impacto (Blast Radius) de modificaciones lógicas.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.symbol_map: Dict[str, List[Dict[str, str]]] = {}

    def parse_file_symbols(self, file_path: str) -> List[Dict[str, str]]:
        """
        Analiza un archivo Python y extrae definiciones de funciones y clases.
        """
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = self.workspace_root / file_path

        if not abs_path.exists():
            return []

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(abs_path))
        except Exception:
            return []

        symbols = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append({
                    "type": "class",
                    "name": node.name,
                    "line": str(node.lineno)
                })
            elif isinstance(node, ast.FunctionDef):
                symbols.append({
                    "type": "function",
                    "name": node.name,
                    "line": str(node.lineno)
                })
        
        self.symbol_map[str(file_path)] = symbols
        return symbols

    def map_transitive_dependencies(self, target_symbol: str) -> Set[str]:
        """
        Identifica qué archivos dependen o importan un símbolo específico.
        (Prototipo básico de escaneo cruzado).
        """
        dependent_files = set()
        
        for py_file in self.workspace_root.rglob("*.py"):
            # Omitir entornos virtuales o directorios ocultos
            if any(part.startswith(".") for part in py_file.parts) or "venv" in py_file.parts:
                continue
                
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if target_symbol in content:
                        # Conversión a path relativo
                        try:
                            rel_path = py_file.relative_to(self.workspace_root)
                            dependent_files.add(str(rel_path))
                        except ValueError:
                            dependent_files.add(str(py_file))
            except Exception:
                continue
                
        return dependent_files
