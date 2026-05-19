# Spec: DE-V2-L2-119
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DashboardState:
    plan: str
    current_phase: str
    next_phase: str
    restart_gate_decision: str
    flywheel_decision: str
    context_efficiency_decision: str
    cache_hit_ratio: float
    stale_findings: int
    latest_prompt_frame_ref: str
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DashboardRenderer:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def build_dashboard_state(self) -> DashboardState:
        warnings: list[str] = []
        refs: list[str] = []

        current = self._load_json(self.aiwg_root / "evolution" / "current_position.json", warnings, refs)
        seed = self._load_json(self.aiwg_root / "evolution" / "next_phase_seed.json", warnings, refs)
        restart = self._load_json(self.reports_root / "restart_integration_gate_latest.json", warnings, refs)
        fly = self._load_json(self.reports_root / "evolution_flywheel_latest.json", warnings, refs)
        bench = self._load_json(self.reports_root / "context_efficiency_benchmark_latest.json", warnings, refs)
        cache = self._load_json(self.reports_root / "prompt_cache_summary_latest.json", warnings, refs)
        stale = self._load_json(self.reports_root / "stale_memory_report.json", warnings, refs)
        frame_ref = ".aiwg/reports/prompt_frame_latest.json"
        if not (self.reports_root / "prompt_frame_latest.json").exists():
            warnings.append("missing:prompt_frame_latest.json")

        return DashboardState(
            plan=str(current.get("plan", "DUMMIE PLAN V1 — Cognitive Evolution Operating Layer")),
            current_phase=str(current.get("current_phase", "unknown")),
            next_phase=str(seed.get("next_phase", "unknown")),
            restart_gate_decision=str(restart.get("decision", "UNKNOWN")),
            flywheel_decision=str(fly.get("decision", "UNKNOWN")),
            context_efficiency_decision=str(bench.get("decision", "UNKNOWN")),
            cache_hit_ratio=float(cache.get("cache_hit_ratio", 0.0) or 0.0),
            stale_findings=len(stale.get("findings", [])) if isinstance(stale, dict) else 0,
            latest_prompt_frame_ref=frame_ref,
            warnings=warnings,
            evidence_refs=refs,
            generated_at=self._utc_now(),
        )

    def render_dashboard_html(self, state: DashboardState) -> str:
        warnings_html = "".join(f"<li>{w}</li>" for w in state.warnings) if state.warnings else "<li>none</li>"
        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>DUMMIE L6 Dashboard</title>
  <style>
    :root {{ --bg:#f3f6e9; --card:#ffffff; --ink:#1f2a1f; --accent:#276749; --warn:#b7791f; }}
    body {{ margin:0; background:linear-gradient(135deg,#f3f6e9,#e8f0df); color:var(--ink); font-family:'IBM Plex Sans', sans-serif; }}
    .wrap {{ max-width:980px; margin:24px auto; padding:0 16px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
    .card {{ background:var(--card); border:1px solid #d7e2cd; border-radius:12px; padding:14px; box-shadow:0 4px 10px rgba(0,0,0,.05); }}
    h1 {{ margin:0 0 12px; font-size:1.4rem; color:var(--accent); }}
    .k {{ font-size:.78rem; text-transform:uppercase; opacity:.75; }}
    .v {{ font-size:1.05rem; font-weight:700; }}
    ul {{ margin:0; padding-left:18px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <h1>DUMMIE Control Dashboard (L6 MVP)</h1>
    <div class=\"grid\">
      <div class=\"card\"><div class=\"k\">Plan State</div><div class=\"v\">{state.plan}</div></div>
      <div class=\"card\"><div class=\"k\">Current Phase</div><div class=\"v\">{state.current_phase}</div></div>
      <div class=\"card\"><div class=\"k\">Next Phase</div><div class=\"v\">{state.next_phase}</div></div>
      <div class=\"card\"><div class=\"k\">Restart Gate</div><div class=\"v\">{state.restart_gate_decision}</div></div>
      <div class=\"card\"><div class=\"k\">Flywheel</div><div class=\"v\">{state.flywheel_decision}</div></div>
      <div class=\"card\"><div class=\"k\">Context Efficiency</div><div class=\"v\">{state.context_efficiency_decision}</div></div>
      <div class=\"card\"><div class=\"k\">Cache Hit Ratio</div><div class=\"v\">{state.cache_hit_ratio:.3f}</div></div>
      <div class=\"card\"><div class=\"k\">Stale Findings</div><div class=\"v\">{state.stale_findings}</div></div>
      <div class=\"card\"><div class=\"k\">Prompt Frame Ref</div><div class=\"v\">{state.latest_prompt_frame_ref}</div></div>
      <div class=\"card\"><div class=\"k\">Warnings</div><ul>{warnings_html}</ul></div>
    </div>
  </div>
</body>
</html>
"""

    def write_dashboard_outputs(self, state: DashboardState) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "dashboard_l6_latest.json").write_text(
            json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        (self.reports_root / "dashboard_l6_latest.html").write_text(
            self.render_dashboard_html(state), encoding="utf-8"
        )

    def _load_json(self, path: Path, warnings: list[str], refs: list[str]) -> dict[str, Any]:
        refs.append(path.as_posix().replace("/media/datasets/DUMMIE Engine/", ""))
        if not path.exists():
            warnings.append(f"missing:{path.name}")
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            warnings.append(f"invalid_json:{path.name}")
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_dashboard_state(aiwg_root: str | Path = ".aiwg") -> DashboardState:
    return DashboardRenderer(aiwg_root=aiwg_root).build_dashboard_state()


def render_dashboard_html(aiwg_root: str | Path = ".aiwg") -> str:
    renderer = DashboardRenderer(aiwg_root=aiwg_root)
    return renderer.render_dashboard_html(renderer.build_dashboard_state())
