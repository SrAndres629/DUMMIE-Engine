# Spec: 159_cognitive_bias_detector
# Spec: DE-V2-L2-159
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class CognitiveBiasReport:
    decision: str
    findings: List[Dict[str, Any]]

    def to_dict(self): return asdict(self)

def detect_cognitive_biases(intent: str, aiwg_root: Path = Path(".aiwg")) -> CognitiveBiasReport:
    findings = []
    reports_root = aiwg_root / "reports"
    
    # 1. Overconfidence Bias
    q_path = reports_root / "metacognitive_quality_gate_latest.json"
    r_path = reports_root / "readiness_score_calibration_latest.json"
    if q_path.exists() and r_path.exists():
        q_data = json.loads(q_path.read_text())
        r_data = json.loads(r_path.read_text())
        if q_data.get("quality_score", 0) >= 90:
            if r_data.get("calibrated_scores", {}).get("daily_use_readiness", 10) < 7:
                findings.append({"bias": "overconfidence_bias", "message": "quality_score high despite low readiness"})

    # 2. Premature Scaling Bias
    if "skill synthesis" in intent.lower() or "pack 6" in intent.lower():
        findings.append({"bias": "premature_scaling_bias", "message": "Advancing to autonomous synthesis while graph memory is DEGRADED"})

    return CognitiveBiasReport(
        decision="FAIL" if findings else "PASS",
        findings=findings
    )
