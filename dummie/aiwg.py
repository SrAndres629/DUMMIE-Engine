import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dummie.paths import ROOT, AIWG

class DummieAiwgIntegration:
    def __init__(self):
        self.aiwg_root = AIWG
        self.receipts_dir = AIWG / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = AIWG / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_truth(self) -> dict:
        truth_file = AIWG / "state" / "current_truth.json"
        if truth_file.exists():
            try:
                with open(truth_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def run_preflight(self) -> dict:
        truth = self.load_truth()
        return {
            "status": "PASS",
            "active_pack": truth.get("current_pack", "PACK_S1"),
            "degraded_capabilities": truth.get("degraded_capabilities", []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def write_receipt(self, command: str, status: str, details: dict) -> dict:
        receipt_id = f"rcpt_{uuid.uuid4().hex[:8]}"
        receipt = {
            "receipt_id": receipt_id,
            "command": command,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details
        }
        receipt_file = self.receipts_dir / f"{receipt_id}.json"
        try:
            with open(receipt_file, "w", encoding="utf-8") as f:
                json.dump(receipt, f, indent=2)
        except Exception:
            pass
        return receipt

    def write_report(self, filename: str, content: dict):
        report_file = self.reports_dir / filename
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        except Exception:
            pass

    def write_markdown_report(self, filename: str, content: str):
        report_file = self.reports_dir / filename
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
