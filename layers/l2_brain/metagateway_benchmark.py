import time
import json
from typing import Dict, Any, List

class MetaGatewayBenchmark:
    """
    Benchmarks token savings by comparing direct file reads vs Meta-Gateway discovery.
    """
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def run_scenario(self, name: str, direct_files: int, gateway_discoveries: int, gateway_analyses: int) -> Dict[str, Any]:
        # Heuristic: direct file read avg 5000 tokens
        # Discovery: 500 tokens
        # Analysis: 800 tokens
        
        avg_file_tokens = 5000
        avg_discovery_tokens = 500
        avg_analysis_tokens = 800
        
        estimated_direct = direct_files * avg_file_tokens
        estimated_gateway = (gateway_discoveries * avg_discovery_tokens) + (gateway_analyses * avg_analysis_tokens)
        
        saved = max(0, estimated_direct - estimated_gateway)
        ratio = saved / estimated_direct if estimated_direct > 0 else 0.0
        
        result = {
            "scenario": name,
            "direct_files_read": direct_files,
            "gateway_capabilities_discovered": gateway_discoveries,
            "gateway_capabilities_analyzed": gateway_analyses,
            "estimated_direct_tokens": estimated_direct,
            "estimated_gateway_tokens": estimated_gateway,
            "estimated_tokens_saved": saved,
            "token_reduction_ratio": round(ratio, 4),
            "success": True
        }
        
        self.results.append(result)
        return result

    def export_report(self, path: str):
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    benchmark = MetaGatewayBenchmark()
    
    # Scenario 1: Inspect Model Router
    benchmark.run_scenario("inspect_model_router", direct_files=5, gateway_discoveries=1, gateway_analyses=1)
    
    # Scenario 2: Inspect Daemon Metacognition
    benchmark.run_scenario("inspect_daemon_metacognition", direct_files=8, gateway_discoveries=1, gateway_analyses=2)
    
    # Scenario 3: Choose tool for repo analysis
    benchmark.run_scenario("choose_tool_for_repo_analysis", direct_files=3, gateway_discoveries=1, gateway_analyses=1)
    
    benchmark.export_report(".aiwg/reports/metagateway_token_savings_benchmark.json")
    print(f"Benchmark report generated with {len(benchmark.results)} scenarios.")
