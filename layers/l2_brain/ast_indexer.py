# Spec Reference: 03_polyglot_architecture
import ast
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .embedding_mesh.contracts import EmbeddingCapability, EmbeddingRequest, ContentType
from .embedding_mesh.registry import EmbeddingRegistry

logger = logging.getLogger("brain.ast_indexer")


class ASTBlastRadiusIndexer:
    """
    [L2_BRAIN] Mapeador estático de código basado en Árboles de Sintaxis Abstracta (AST).
    Permite anticipar el impacto (Blast Radius) de modificaciones lógicas.
    Genera CODE embeddings para símbolos del código, separado del espacio vectorial TEXT.
    """

    def __init__(
        self,
        workspace_root: str,
        embedding_registry: Optional[EmbeddingRegistry] = None,
    ):
        self.workspace_root = Path(workspace_root)
        self.symbol_map: Dict[str, List[Dict[str, str]]] = {}
        self._registry = embedding_registry or EmbeddingRegistry()
        self._symbol_embeddings: Dict[str, Dict[str, Any]] = {}

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
                symbols.append(
                    {"type": "class", "name": node.name, "line": str(node.lineno)}
                )
            elif isinstance(node, ast.FunctionDef):
                symbols.append(
                    {"type": "function", "name": node.name, "line": str(node.lineno)}
                )

        self.symbol_map[str(file_path)] = symbols
        return symbols

    def embed_symbol(self, symbol_name: str, source_code: str) -> Dict[str, Any]:
        """
        Genera un CODE embedding aislado para un símbolo del código fuente.
        El embedding se almacena en CODE_LOCAL_768, separado del espacio TEXT.
        """
        payload = f"{symbol_name}\n{source_code[:2000]}"
        provider = self._registry.get_provider(EmbeddingCapability.CODE)
        req = EmbeddingRequest(
            content=payload,
            content_type=ContentType.CODE,
            capability=EmbeddingCapability.CODE,
        )
        try:
            response = provider.embed(req)
            result = {
                "symbol": symbol_name,
                "vector": response.vector,
                "dimensions": response.dimensions,
                "vector_space": response.vector_space,
                "degraded": response.degraded,
                "model_used": response.model_used,
                "payload_hash": response.payload_hash,
            }
        except Exception as exc:
            logger.warning(
                "CODE embedding failed for symbol '%s': %s", symbol_name, exc
            )
            empty = [0.0] * 384
            result = {
                "symbol": symbol_name,
                "vector": empty,
                "dimensions": 384,
                "vector_space": "code_error",
                "degraded": True,
                "model_used": "error",
                "payload_hash": hashlib.sha256(payload.encode()).hexdigest(),
            }
        self._symbol_embeddings[symbol_name] = result
        return result

    def embed_file_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parsea un archivo y genera CODE embeddings para cada símbolo encontrado.
        """
        symbols = self.parse_file_symbols(file_path)
        results = []
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = self.workspace_root / file_path
        try:
            source = abs_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return results
        for sym in symbols:
            name = sym["name"]
            embedding = self.embed_symbol(name, source)
            embedding["type"] = sym["type"]
            embedding["line"] = sym["line"]
            results.append(embedding)
        return results

    def map_transitive_dependencies(self, target_symbol: str) -> Set[str]:
        """
        Identifica qué archivos dependen o importan un símbolo específico.
        (Prototipo básico de escaneo cruzado).
        """
        dependent_files = set()

        for py_file in self.workspace_root.rglob("*.py"):
            # Omitir entornos virtuales o directorios ocultos
            if (
                any(part.startswith(".") for part in py_file.parts)
                or "venv" in py_file.parts
            ):
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
