import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "superpowers_mcp_proxy.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("superpowers_mcp_proxy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_lists_local_dummie_skills(tmp_path, monkeypatch):
    module = _load_module()
    dummie_dir = tmp_path / "dummie-skills"
    superpowers_dir = tmp_path / "superpowers"
    skill_dir = dummie_dir / "n8n-expert"
    skill_dir.mkdir(parents=True)
    superpowers_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: n8n Expert\ndescription: Expert workflow automation guidance\n---\n\n# n8n Expert\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "DUMMIE_SKILLS_DIR", str(dummie_dir))
    monkeypatch.setattr(module, "SUPERPOWERS_DIR", str(superpowers_dir))

    result = module._discover_dummie_skills()

    assert "n8n-expert" in result
    assert result["n8n-expert"]["type"] == "dummie"


@pytest.mark.asyncio
async def test_load_dummie_skill_returns_full_content(tmp_path, monkeypatch):
    module = _load_module()
    dummie_dir = tmp_path / "dummie-skills"
    superpowers_dir = tmp_path / "superpowers"
    skill_dir = dummie_dir / "n8n-expert"
    skill_dir.mkdir(parents=True)
    superpowers_dir.mkdir(parents=True)
    content = "---\nname: n8n Expert\ndescription: Expert workflow automation guidance\n---\n\n# n8n Expert\n\n## Playbook\nUse MCPs.\n"
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    monkeypatch.setattr(module, "DUMMIE_SKILLS_DIR", str(dummie_dir))
    monkeypatch.setattr(module, "SUPERPOWERS_DIR", str(superpowers_dir))

    result = await module.load_dummie_skill("n8n-expert")

    assert result == content
