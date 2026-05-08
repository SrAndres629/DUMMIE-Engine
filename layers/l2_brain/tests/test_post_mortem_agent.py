import pytest
import asyncio
import json
import os
import tempfile
from pathlib import Path
from layers.l2_brain.post_mortem_agent import PostMortemAnalyst

@pytest.mark.asyncio
async def test_post_mortem_agent_analyze_failures():
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = os.path.join(tmpdir, "ledger.jsonl")
        state_path = os.path.join(tmpdir, "state.txt")
        skills_dir = os.path.join(tmpdir, "skills")
        os.makedirs(skills_dir, exist_ok=True)

        # Write some entries
        with open(ledger_path, "w") as f:
            for i in range(5):
                status = "FAILED" if i % 2 == 0 else "SUCCESS"
                entry = {"status": status, "agent": f"agent_{i}", "details": {"error": "timeout error"}}
                f.write(json.dumps(entry) + "\n")

        analyst = PostMortemAnalyst(ledger_path, skills_dir, state_path)

        await analyst.analyze_failures()

        # Check if skills were created
        skills = os.listdir(skills_dir)
        assert len(skills) == 3
        assert "agent_0.patch.json" in skills
        assert "agent_2.patch.json" in skills
        assert "agent_4.patch.json" in skills

        # Check if state was updated
        with open(state_path, "r") as f:
            state = f.read()
            assert int(state) > 0
