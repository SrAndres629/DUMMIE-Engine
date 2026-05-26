import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("dummie-smart.skills")


@dataclass
class SkillStep:
    step_id: str
    description: str
    server: str
    tool: str
    arguments: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class SkillTemplate:
    skill_id: str
    name: str
    description: str
    trigger_patterns: list[str]
    steps: list[SkillStep]


BUILTIN_SKILLS: list[SkillTemplate] = [
    SkillTemplate(
        skill_id="tdd",
        name="Test-Driven Development",
        description="Find tests, run them, and implement missing functionality.",
        trigger_patterns=[
            "test",
            "tdd",
            "red.?green",
            "implement.*test",
            "write.*test",
        ],
        steps=[
            SkillStep(
                "1",
                "Find test files",
                "filesystem",
                "search_files",
                {"pattern": "**/test_*.py"},
            ),
            SkillStep(
                "2",
                "Find source files",
                "filesystem",
                "search_files",
                {"pattern": "**/*.py"},
            ),
            SkillStep(
                "3",
                "Read source file",
                "filesystem",
                "read_text_file",
                {},
                depends_on=["2"],
            ),
            SkillStep(
                "4",
                "Run existing tests",
                "shell",
                "execute_command",
                {"command": "python -m pytest -q 2>&1"},
                depends_on=["1"],
            ),
        ],
    ),
    SkillTemplate(
        skill_id="code_review",
        name="Code Review",
        description="Review code for quality, bugs, and improvements.",
        trigger_patterns=[
            "review",
            "code review",
            "analyze.*code",
            "check.*code",
            "audit",
        ],
        steps=[
            SkillStep(
                "1",
                "Find relevant files",
                "filesystem",
                "search_files",
                {"pattern": "**/*.py"},
            ),
            SkillStep(
                "2",
                "Read file for review",
                "filesystem",
                "read_text_file",
                {},
                depends_on=["1"],
            ),
        ],
    ),
    SkillTemplate(
        skill_id="debug",
        name="Systematic Debugging",
        description="Reproduce bug, identify root cause, and apply fix.",
        trigger_patterns=["debug", "bug", "fix", "error", "failing", "why is", "crash"],
        steps=[
            SkillStep(
                "1",
                "Find relevant files",
                "filesystem",
                "search_files",
                {"pattern": "**/*.py"},
            ),
            SkillStep(
                "2",
                "Read file for context",
                "filesystem",
                "read_text_file",
                {},
                depends_on=["1"],
            ),
            SkillStep(
                "3",
                "Run to reproduce error",
                "shell",
                "execute_command",
                {"command": "python --version 2>&1"},
                depends_on=["2"],
            ),
        ],
    ),
    SkillTemplate(
        skill_id="explore",
        name="Explore Codebase",
        description="Find and analyze code across the repository.",
        trigger_patterns=[
            "find",
            "search",
            "explore",
            "where is",
            "locate",
            "grep",
            "list files",
            "show files",
        ],
        steps=[
            SkillStep(
                "1",
                "Search for pattern",
                "filesystem",
                "search_files",
                {"pattern": "**/*"},
            ),
            SkillStep(
                "2",
                "Read matches",
                "filesystem",
                "read_text_file",
                {},
                depends_on=["1"],
            ),
        ],
    ),
]


class SkillExecutor:
    def __init__(self, proxy_manager):
        self.proxy = proxy_manager
        self._results: dict[str, Any] = {}

    def list_all(self) -> list[dict]:
        return [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description,
                "trigger_patterns": s.trigger_patterns,
                "step_count": len(s.steps),
            }
            for s in BUILTIN_SKILLS
        ]

    def get(self, skill_id: str) -> Optional[SkillTemplate]:
        for s in BUILTIN_SKILLS:
            if s.skill_id == skill_id:
                return s
        return None

    async def match(self, intent: str) -> Optional[SkillTemplate]:
        import re

        for skill in BUILTIN_SKILLS:
            for pattern in skill.trigger_patterns:
                if re.search(pattern, intent, re.IGNORECASE):
                    logger.info("skill matched: %s via '%s'", skill.skill_id, pattern)
                    return skill
        return None

    async def execute(self, skill: SkillTemplate, intent: str) -> dict:
        self._results = {}

        independent = [s for s in skill.steps if not s.depends_on]
        dependent = [s for s in skill.steps if s.depends_on]

        if independent:
            tasks = [self._execute_step(s, intent) for s in independent]
            await asyncio.gather(*tasks, return_exceptions=True)

        for step in dependent:
            ready = all(dep in self._results for dep in step.depends_on)
            if ready:
                await self._execute_step(step, intent)
            else:
                self._results[step.step_id] = {
                    "success": False,
                    "error": f"unsatisfied dependency: {step.depends_on}",
                }

        return self._compact(skill, intent)

    def _inject_dep_results(self, step: SkillStep) -> dict:
        args = dict(step.arguments)
        for dep_id in step.depends_on:
            dep_result = self._results.get(dep_id, {})
            if not dep_result.get("success"):
                continue
            dep_output = dep_result.get("output", "")
            for key, value in dep_result.get("parsed", {}).items():
                if key not in args:
                    args[key] = value
            if not args:
                args["input_text"] = dep_output[:4000]
        return args

    def _parse_tool_output(self, server: str, tool: str, output: str) -> dict:
        parsed = {}
        if server == "filesystem" and tool == "search_files" and output:
            lines = [
                line.strip()
                for line in output.splitlines()
                if line.strip() and not line.strip().startswith("Found")
            ]
            if lines:
                parsed["path"] = lines[0]
                parsed["paths"] = lines[:20]
        elif server == "filesystem" and tool == "list_directory" and output:
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            if lines:
                parsed["paths"] = lines[:20]
        elif server == "git" and tool == "git_status" and output:
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            if lines:
                parsed["files"] = lines[:20]
        return parsed

    async def _execute_step(self, step: SkillStep, intent: str):
        try:
            args = self._inject_dep_results(step)
            if not args:
                self._results[step.step_id] = {
                    "success": False,
                    "error": "no arguments and no dependency output to use",
                    "step_description": step.description,
                }
                return
            result = await self.proxy.call_tool(step.server, step.tool, args)
            raw = str(result)
            parsed = self._parse_tool_output(step.server, step.tool, raw)
            self._results[step.step_id] = {
                "success": True,
                "output": raw[:2000],
                "parsed": parsed,
                "step_description": step.description,
            }
        except Exception as e:
            self._results[step.step_id] = {
                "success": False,
                "error": str(e),
                "step_description": step.description,
            }
            logger.warning("skill step %s failed: %s", step.step_id, e)

    def _compact(self, skill: SkillTemplate, intent: str) -> dict:
        total = len(skill.steps)
        completed = sum(1 for r in self._results.values() if r.get("success"))
        failed = sum(1 for r in self._results.values() if not r.get("success"))

        return {
            "skill": skill.skill_id,
            "name": skill.name,
            "description": skill.description,
            "intent": intent,
            "steps_total": total,
            "steps_completed": completed,
            "steps_failed": failed,
            "outputs": {
                sid: data.get("output", data.get("error", ""))[:200]
                for sid, data in self._results.items()
            },
        }
