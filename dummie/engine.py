from dummie.config import DummieConfig
from dummie.session import DummieSessionManager
from dummie.providers import DummieProviderRegistry
from dummie.aiwg import DummieAiwgIntegration
from dummie.strategic_partner import DummieStrategicPartner

class DummieEngineStatus:
    def __init__(self, decision: str, preflight: dict, providers: dict, root_dir: str, aiwg_dir: str):
        self.decision = decision
        self.preflight = preflight
        self.providers = providers
        self.root_dir = root_dir
        self.aiwg_dir = aiwg_dir

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "preflight": self.preflight,
            "providers": self.providers,
            "root_dir": self.root_dir,
            "aiwg_dir": self.aiwg_dir
        }

class DummieAdviceResponse:
    def __init__(self, data: dict):
        self.goal_type = data.get("goal_classification", {}).get("goal_type", "unknown")
        self.strategic_questions = data.get("strategic_questions", [])
        self.tool_opportunities = data.get("tool_opportunities", [])
        self.roadmap = data.get("roadmap", [])
        self.advice = data.get("advice", {})
        self.creator_profile = data.get("creator_profile", {})
        self.business_intake = data.get("business_intake", {})
        self.receipt = data.get("receipt", {})
        self.raw_data = data

    def to_dict(self) -> dict:
        return {
            "goal_type": self.goal_type,
            "strategic_questions": self.strategic_questions,
            "tool_opportunities": self.tool_opportunities,
            "roadmap": self.roadmap,
            "advice": self.advice,
            "creator_profile": self.creator_profile,
            "business_intake": self.business_intake,
            "receipt": self.receipt
        }

class DummieEngine:
    def __init__(self):
        self.config = DummieConfig()
        self.session = DummieSessionManager()
        self.providers = DummieProviderRegistry()
        self.aiwg = DummieAiwgIntegration()
        self.partner = DummieStrategicPartner()

    @classmethod
    def load(cls) -> "DummieEngine":
        return cls()

    def status(self) -> DummieEngineStatus:
        preflight = self.aiwg.run_preflight()
        providers_status = self.providers.get_providers_status()
        
        decision = "PASS"
        if preflight.get("status") != "PASS":
            decision = "FAIL"
            
        status_info = {
            "decision": decision,
            "preflight": preflight,
            "providers": providers_status,
            "root_dir": str(self.config.root_dir),
            "aiwg_dir": str(self.config.aiwg_dir)
        }
        self.aiwg.write_receipt("status", decision, status_info)
        
        # Write provider status report
        self.aiwg.write_report("provider_status_latest.json", providers_status)
        self.aiwg.write_report("sovereign_cli_latest.json", status_info)
        
        return DummieEngineStatus(
            decision=decision,
            preflight=preflight,
            providers=providers_status,
            root_dir=str(self.config.root_dir),
            aiwg_dir=str(self.config.aiwg_dir)
        )

    def advise(self, goal_statement: str) -> DummieAdviceResponse:
        advice_res = self.partner.advise(goal_statement)
        
        # Record learning episode
        self.session.record_episode(
            query=goal_statement,
            intent="advise",
            answer=f"Goal classified as {advice_res.get('goal_classification', {}).get('goal_type')}",
            decision="PASS",
            evidence_refs=[".aiwg/identity/goal_memory.yaml"]
        )
        
        # Write receipt
        receipt = self.aiwg.write_receipt("advise", "PASS", {
            "goal": goal_statement,
            "goal_classification": advice_res.get("goal_classification")
        })
        advice_res["receipt"] = receipt
        
        # Write reports
        self.aiwg.write_report("business_goal_intake_latest.json", advice_res)
        self.aiwg.write_report("strategic_partner_runtime_latest.json", advice_res)
        self.aiwg.write_report("pack_s1_sovereign_cli_strategic_partner_runtime.json", advice_res)
        
        # Write markdown report
        md_content = f"# DUMMIE Engine - Strategic Advice Report\n\n"
        md_content += f"**Goal**: {goal_statement}\n\n"
        md_content += f"**Type**: {advice_res.get('goal_classification', {}).get('goal_type')}\n\n"
        md_content += f"**Creator**: {advice_res.get('creator_profile', {}).get('name')}\n\n"
        md_content += "## Advice\n"
        for tactic in advice_res.get("advice", {}).get("tactics", []):
            md_content += f"- {tactic}\n"
        
        md_content += "\n## Roadmap\n"
        for step in advice_res.get("roadmap", []):
            md_content += f"### {step.get('phase')} ({step.get('duration')})\n"
            for action in step.get("actions", []):
                md_content += f"- {action}\n"
        
        self.aiwg.write_markdown_report("pack_s1_sovereign_cli_strategic_partner_runtime.md", md_content)
        
        return DummieAdviceResponse(advice_res)
