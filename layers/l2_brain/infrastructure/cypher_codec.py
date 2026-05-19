import json
from enum import Enum
from typing import Any

def cypher_literal(value: Any) -> str:
    """
    Convierte de forma segura un tipo de Python a su representación literal Cypher.
    Resistente a ataques de Cypher Injection.
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(cypher_literal(v) for v in value) + "]"
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, str):
        escaped = (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
        )
        return f"'{escaped}'"
    
    # Fallback para otros objetos (serialización JSON)
    try:
        serialized = json.dumps(value, ensure_ascii=False)
        escaped = serialized.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    except Exception:
        raise TypeError(f"Unsupported Cypher literal type: {type(value)!r}")

def node_to_create_cypher(node: Any) -> str:
    """
    Toma un nodo (Pydantic o similar) y genera la consulta de creación Cypher segura.
    """
    if hasattr(node, "model_dump"):
        data = node.model_dump(mode="json")
    elif hasattr(node, "__dict__"):
        data = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}
    else:
        raise ValueError("Invalid node structure for persistence")

    props = ", ".join(f"{key}: {cypher_literal(value)}" for key, value in data.items())
    return f"CREATE (m:MemoryNode4D {{{props}}})"
