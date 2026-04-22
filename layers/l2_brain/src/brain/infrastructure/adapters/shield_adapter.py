import json
from typing import Dict, Any
from brain.domain.memory.ports import IShieldOutputPort

try:
    import shield # type: ignore
    SHIELD_LOADED = True
except ImportError:
    SHIELD_LOADED = False

class NativeShieldAdapter(IShieldOutputPort):
    def audit_intent(self, intent_json: str) -> Dict[str, Any]:
        if not SHIELD_LOADED:
            print("[NativeShieldAdapter] !!! ADVERTENCIA: Escudo (L3) no encontrado. Mocking bypass !!!")
            return {"authorized": True, "shield_note": "MOCK_BYPASS_NO_L3"}
            
        audit_result_json = shield.audit_intent(intent_json)
        return json.loads(audit_result_json)
