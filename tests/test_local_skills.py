from pathlib import Path


def test_local_skill_files_have_yaml_frontmatter():
    skills_root = Path(__file__).resolve().parents[1] / ".agents" / "skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md"))

    assert skill_files, "expected at least one local skill file"

    invalid = []
    for skill_file in skill_files:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3 or lines[0] != "---" or "---" not in lines[1:]:
            invalid.append(str(skill_file.relative_to(skills_root.parent.parent)))

    assert invalid == []
