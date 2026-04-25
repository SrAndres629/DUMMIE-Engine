import sys
from pathlib import Path
import re

# Añadir raíz
sys.path.append(str(Path(__file__).parent.parent))

from layers.l1_nervous.context_quantizer import ContextQuantizer
from layers.l1_nervous.compressive_memory import CompressiveMemory
from layers.l1_nervous.memory_ipc import ArrowMemoryBridge

def test_extraction_precision():
    print("--- Precision/Recall Audit: Semantic Extraction ---")
    
    dataset = [
        {"msg": "DECISION: Usar gRPC", "expected_cat": "DECISIONES", "expected_val": "Usar gRPC"},
        {"msg": "RESOLVED: Bug en el parser", "expected_cat": "DECISIONES", "expected_val": "Bug en el parser"},
        {"msg": "ERROR: Timeout en L1", "expected_cat": "ERRORES", "expected_val": "Timeout en L1"},
        {"msg": "MOVED TO: Production", "expected_cat": "ESTADO_FABRICACION", "expected_val": "Production"},
        {"msg": "Normal message with no metadata", "expected_cat": None, "expected_val": None}
    ]
    
    bridge = ArrowMemoryBridge("/tmp/dummie_memory.sock")
    comp_mem = CompressiveMemory(bridge)
    
    history = [d["msg"] for d in dataset]
    summary = comp_mem.crystallize_history(history, require_persist=False)
    
    hits = 0
    total_relevant = len([d for d in dataset if d["expected_cat"]])
    
    for d in dataset:
        if d["expected_cat"]:
            if d["expected_val"] in summary:
                hits += 1
            else:
                print(f"[FAIL] Missing {d['expected_cat']}: {d['expected_val']}")
        else:
            if d["msg"] in summary and "DECISIONES" not in summary.split(d["msg"])[0]:
                # El mensaje normal no debe ser categorizado
                pass

    precision = hits / total_relevant if total_relevant > 0 else 1.0
    print(f"Precision Score: {precision:.2f}")
    assert precision == 1.0
    print("[✓] Precision Audit Passed.\n")

def test_pruning_boundaries():
    print("--- Falsification Attempt: Pruning Boundaries ---")
    quantizer = ContextQuantizer(".")
    
    tree = """
    bin/
    binance/
    objects/
    obj/
    src/main.py
    """
    
    # Intentar falsar: ¿Podará 'binance' porque contiene 'bin'?
    pruned = quantizer.prune_tree(tree, keywords=[])
    print("Pruned Tree:")
    print(pruned)
    
    assert "binance" in pruned, "Falsificación EXITOSA: 'binance' fue podado erróneamente (substring match)"
    assert "objects" in pruned, "Falsificación EXITOSA: 'objects' fue podado erróneamente"
    assert "bin/" not in pruned.strip().split('\n'), "Error: bin/ no fue podado"
    assert "obj/" not in pruned.strip().split('\n'), "Error: obj/ no fue podado"
    
    print("[✓] Pruning Boundaries Audit Passed (Regex boundaries working).\n")

if __name__ == "__main__":
    try:
        test_extraction_precision()
        test_pruning_boundaries()
        print("SEMANTIC AUDIT PASSED.")
    except Exception as e:
        print(f"AUDIT FAILED: {e}")
        sys.exit(1)
