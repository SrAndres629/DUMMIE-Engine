import sys
import argparse
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(str(Path(__file__).parent.parent))

from layers.l1_nervous.context_quantizer import ContextQuantizer
from layers.l1_nervous.compressive_memory import CompressiveMemory
from layers.l1_nervous.memory_ipc import ArrowMemoryBridge

def test_turbo_quant():
    print("--- Testing TurboQuant (Spec Quantization) ---")
    quantizer = ContextQuantizer(".")
    
    sample_spec = """# Spec 01: Nervous Layer
---
id: L1_NERVOUS
version: 1.0
---

Este componente gestiona el transporte de datos.

- **Invariante 01**: No se permite I/O bloqueante.
- **Invariante 02**: Todo mensaje debe tener un Lamport Clock.
- **Invariante 03**: La memoria se persiste en KùzuDB.

Más detalles irrelevantes que deberían ser podados por el cuantizador...
"""
    
    quantized = quantizer.quantize_spec(sample_spec)
    print("Quantized Spec:")
    print(quantized)
    
    assert "spec_quantized" in quantized
    assert "Invariante 01" in quantized
    assert "Invariante 03" in quantized
    assert "irrelevantes" not in quantized
    print("[✓] TurboQuant test passed.\n")

def test_infini_attention(allow_offline: bool = False):
    print("--- Testing Infini-attention (History Crystallization) ---")
    bridge = ArrowMemoryBridge("/tmp/dummie_memory.sock")
    if not bridge.heartbeat() and not allow_offline:
        raise RuntimeError("Memory Plane no disponible en /tmp/dummie_memory.sock")

    comp_mem = CompressiveMemory(bridge)
    
    history = [
        "USER: Create a new service.",
        "AGENT: I will use Hexagonal Architecture.",
        "AGENT: DECISION: Use Go for L0.",
        "USER: Any errors?",
        "AGENT: ERROR: Port collision detected.",
        "AGENT: RESOLVED: Changed port to 8081."
    ]
    
    summary = comp_mem.crystallize_history(history, require_persist=not allow_offline)
    print("Crystallized Summary:")
    print(summary)
    
    assert "DECISIONES CLAVE" in summary
    assert "ERRORES/APRENDIZAJES" in summary
    assert "RESOLVED" in summary
    assert "ERROR" in summary

    if not allow_offline:
        assert comp_mem.last_persist_ok, f"Persistencia fallida: {comp_mem.last_error}"
        assert comp_mem.last_causal_hash, "No se generó causal hash"
        check = bridge.ipc.execute(
            f"MATCH (m:MemoryState {{id: '{comp_mem.last_causal_hash}'}}) RETURN count(m)"
        )
        assert check.has_next(), "No hubo respuesta del backend para verificar persistencia"
        row = check.get_next()
        assert row[0] >= 1, "No se encontró el nodo cristalizado en 4D-TES"

    print("[✓] Infini-attention test passed.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verificación de compresión cognitiva")
    parser.add_argument(
        "--allow-offline",
        action="store_true",
        help="Permite pasar sin validar persistencia real en el Memory Plane.",
    )
    args = parser.parse_args()

    try:
        test_turbo_quant()
        test_infini_attention(allow_offline=args.allow_offline)
        print("ALL COMPRESSION TESTS PASSED.")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
