import os
import sys
import asyncio
sys.path.append(os.path.abspath("layers/l2_brain"))
from auto_evolution import CognitiveAutoEvolver
from orchestrator import CognitiveOrchestrator

async def test_auto_evolution_logic():
    # Setup
    evolver = CognitiveAutoEvolver(workspace_root=".")
    
    # Simular un error
    error_context = {
        "exception": "ImportError",
        "message": "No module named 'topological_auditor'",
        "stack_trace": "File 'daemon.py', line 37, in <module>\nfrom topological_auditor import TopologicalAuditor"
    }
    
    # El evolver debería identificar el archivo y el problema
    analysis = await evolver.analyze_failure(error_context)
    
    assert "daemon.py" in analysis["affected_files"]
    assert "path" in analysis["root_cause"].lower() or "import" in analysis["root_cause"].lower()

    print("✅ Auto-Evolution Analysis Test Passed")

if __name__ == "__main__":
    asyncio.run(test_auto_evolution_logic())
