import re
import os
try:
    from layers.l2_brain.models import AuthorityLevel, IntentType
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models import AuthorityLevel, IntentType

def test_authority_level_protobuf_drift():
    """Verifica que AuthorityLevel en Python coincida con core.proto."""
    proto_path = "proto/dummie/v2/core.proto"
    if not os.path.exists(proto_path):
        return # Skip if proto not found in CI context
    
    with open(proto_path, "r") as f:
        content = f.read()
    
    # Extraer nombres de AuthorityLevel del proto
    # enum AuthorityLevel { ... }
    match = re.search(r"enum AuthorityLevel\s*\{([\s\S]*?)\}", content)
    assert match is not None
    
    proto_values = re.findall(r"([A-Z_]+)\s*=", match.group(1))
    # Filtrar AUTHORITY_UNSPECIFIED si se desea, o mapear
    # En Python usamos nombres simplificados pero mapeados a strings
    
    python_values = [e.name for e in AuthorityLevel]
    
    # Comprobar que los nombres clave existen en ambos
    for val in ["AGENT", "ENGINEER", "ARCHITECT", "OVERSEER", "HUMAN"]:
        assert val in python_values, f"{val} missing in Python AuthorityLevel"
        assert any(val in pv for pv in proto_values), f"{val} missing in Protobuf AuthorityLevel"

def test_intent_type_protobuf_drift():
    """Verifica que IntentType en Python coincida con memory.proto."""
    proto_path = "proto/dummie/v2/memory.proto"
    if not os.path.exists(proto_path):
        return
    
    with open(proto_path, "r") as f:
        content = f.read()
    
    match = re.search(r"enum IntentType\s*\{([\s\S]*?)\}", content)
    assert match is not None
    
    proto_values = re.findall(r"([A-Z_]+)\s*=", match.group(1))
    python_values = [e.name for e in IntentType]
    
    for val in ["OBSERVATION", "FABRICATION", "MUTATION", "RESOLUTION", "AUDIT", "CRYSTALLIZATION"]:
        assert val in python_values, f"{val} missing in Python IntentType"
        assert any(val in pv for pv in proto_values), f"{val} missing in Protobuf IntentType"
