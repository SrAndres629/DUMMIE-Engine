import os
import json
from typing import List
from brain.domain.memory.ports import ISessionLedgerPort
from brain.domain.memory.models import EgoState

class SessionLedgerAdapter(ISessionLedgerPort):
    """
    Adaptador para el Ledger de Sesión (Spec 36).
    Persiste el 'Stream of Consciousness' en formato JSONL.
    """
    def __init__(self, ledger_path: str = ".aiwg/memory/session_ledger.jsonl"):
        self.ledger_path = ledger_path
        ledger_dir = os.path.dirname(self.ledger_path)
        if ledger_dir:
            os.makedirs(ledger_dir, exist_ok=True)

    def record_ego_state(self, state: EgoState) -> None:
        """Añade un estado del ego al ledger de sesión."""
        try:
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(state.model_dump_json() + "\n")
        except Exception as e:
            print(f"[SessionLedgerAdapter] Error al escribir ego state: {e}")

    def get_session_history(self, session_id: str) -> List[EgoState]:
        """Escanea el ledger para recuperar pensamientos de una sesión específica."""
        history = []
        if not os.path.exists(self.ledger_path):
            return []
            
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    # Nota: Spec 36 no tiene session_id explícito en EgoState todavía,
                    # pero SessionLedger (el contenedor) sí. Para simplificar,
                    # asumimos que el archivo es por sesión o filtramos si se añade el campo.
                    history.append(EgoState(**data))
            return history
        except Exception as e:
            print(f"[SessionLedgerAdapter] Error al leer historial: {e}")
            return []
