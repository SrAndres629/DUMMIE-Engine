import sys
import os
from pathlib import Path

# Configuración de PYTHONPATH industrial
ROOT = Path(__file__).parent.absolute()
layers = [
    ROOT / "layers" / "l2_brain",
    ROOT / "layers" / "l3_shield",
    ROOT / "layers" / "l4_edge",
    ROOT / "layers" / "l5_muscle"
]
for layer in layers:
    sys.path.append(str(layer))

print(f"--- INITIATING TEST FLIGHT (TABULA RASA v2) ---")

try:
    # Intento de Importación del Orquestador
    from daemon import DummieDaemon
    from gateway_contract import GatewayRequest
    
    # Mocks para instanciación
    class MockGateway: pass
    class MockEventBus: pass
    
    daemon = DummieDaemon(
        ledger_path=str(ROOT / ".aiwg" / "ledger" / "sovereign_resolutions.jsonl"),
        mcp_gateway=MockGateway(),
        event_bus=MockEventBus()
    )
    
    print("✅ SYSTEM READY - PHYSICAL TRUTH ALIGNED")
    print(f"✅ Daemon instanced successfully at: {hex(id(daemon))}")
    
except ImportError as e:
    print(f"❌ NERVOUS FAILURE (ImportError): {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ SYSTEM FAILURE: {e}")
    sys.exit(1)

print("--- FLIGHT COMPLETED: SUCCESS ---")
