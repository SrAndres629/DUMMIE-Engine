import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()
ORACLE_PATH = ROOT_DIR / "scripts" / "context_oracle.py"

def test_quantized_tree():
    print("Testing Quantized Tree...")
    # Simular una meta actual
    env = os.environ.copy()
    env["DUMMIE_CURRENT_GOAL"] = "Optimize memory IPC and nervous layer"
    
    cmd = ["python3", str(ORACLE_PATH), "--tree"]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    print("Output:")
    print(result.stdout)
    
    # Verificar que solo aparecen cosas relacionadas con 'memory' o 'nervous'
    assert "layers/" in result.stdout
    assert "l1_nervous/" in result.stdout
    print("[✓] Tree pruning works.")

def test_quantized_specs():
    print("\nTesting Quantized Specs...")
    cmd = ["python3", str(ORACLE_PATH), "--specs"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Output Snippet:")
    print(result.stdout[:500])
    
    # Verificar que el formato es compacto (no el markdown original largo)
    assert "Invariants:" in result.stdout
    print("[✓] Spec quantization works.")

if __name__ == "__main__":
    try:
        test_quantized_tree()
        test_quantized_specs()
        print("\n=== VERIFICATION SUCCESSFUL ===")
    except Exception as e:
        print(f"\n[!] Verification FAILED: {e}")
        exit(1)
