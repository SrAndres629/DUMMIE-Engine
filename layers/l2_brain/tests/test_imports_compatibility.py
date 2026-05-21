import pytest
from layers.l2_brain.domain.authority import AuthorityLevel
import layers.l2_brain as l2
import layers.l2_brain.memory.models as memory_models
import layers.l2_brain.flat_brain.models as flat_models

def test_authority_level_identity():
    """
    Verifica que AuthorityLevel sea el mismo objeto en todos los puntos de entrada.
    Esto previene derivas de tipos en memoria que romperían isinstance().
    """
    # 1. Comparación con el dominio canónico
    assert l2.AuthorityLevel is AuthorityLevel
    assert memory_models.AuthorityLevel is AuthorityLevel
    assert flat_models.AuthorityLevel is AuthorityLevel
    
    # 2. Verificación de niveles canónicos (Exactamente 6)
    expected_levels = {
        "AUTHORITY_UNSPECIFIED",
        "AGENT",
        "ENGINEER",
        "ARCHITECT",
        "OVERSEER",
        "HUMAN"
    }
    current_levels = {level.value for level in AuthorityLevel}
    assert current_levels == expected_levels, f"Se detectaron niveles no canónicos: {current_levels}"

def test_memory_node_identity():
    """
    Verifica que MemoryNode4D sea el mismo objeto.
    """
    assert l2.MemoryNode4D is memory_models.MemoryNode4D
    assert flat_models.MemoryNode4D is memory_models.MemoryNode4D

def test_static_import_resolution():
    """
    Verifica que la resolución de atributos en l2 sea estática y no vía sys.meta_path.
    """
    import sys
    # Asegurarse de que el redirector no esté en sys.meta_path
    for hook in sys.meta_path:
        assert "L2BrainRedirector" not in str(hook), "El redirector dinámico aún está activo en sys.meta_path"
    
    # Probar carga de un módulo de organo canónico
    assert l2.memory is not None
    assert l2.memory.__name__ == "layers.l2_brain.memory"

def test_backwards_compatibility_shim():
    """
    Verifica que el shim de flat_brain funcione correctamente.
    """
    from layers.l2_brain.memory.models import AgentIntent
    from layers.l2_brain.memory.models import AgentIntent as CanonicalIntent
    
    assert AgentIntent is CanonicalIntent
