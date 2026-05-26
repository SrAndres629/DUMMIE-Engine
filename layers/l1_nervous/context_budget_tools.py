import logging

logger = logging.getLogger("dummie-smart.context-budget")


TIER_1_TOOLS = {
    "filesystem": ["read_text_file", "write_text_file", "search_files"],
    "shell": ["execute_command", "run_bash_command"],
}

TIER_2_TOOLS = {
    "github": ["create_pr", "list_branches", "merge_branch", "search_code"],
    "git": ["git_status", "git_diff", "git_log", "git_commit"],
    "sqlite": ["execute_query", "list_tables", "describe_table"],
    "sequentialthinking": ["think", "plan"],
}

TIER_3_TOOLS = {
    "browser-use": [
        "navigate_website",
        "click_element",
        "extract_content",
        "fill_form",
    ],
    "mcp-comfyui": ["generate_image_from_intent", "run_workflow"],
    "docker": ["manage_containers", "manage_images", "manage_networks"],
    "vercel": ["list_projects", "deploy_project", "get_logs"],
    "cloudflare": ["run_inference", "list_models"],
    "mcp-bash": ["execute_bash_command", "run_script"],
}

TIER_TOKEN_COST = {1: 500, 2: 1500, 3: 3000}

TIER_NAME = {1: "core", 2: "extended", 3: "specialized"}


class ContextBudgetRouter:
    """Progressive tool disclosure based on available token budget.

    Three tiers:
      Tier 1 (core, ~500 tok): filesystem, shell
      Tier 2 (extended, ~1500 tok): + github, git, sqlite, thinking
      Tier 3 (specialized, ~3000 tok): + browser, comfyui, docker, vercel, cloudflare
    """

    def get_tools_for_budget(self, budget: int) -> dict:
        tier = self._resolve_tier(budget)
        result = {}
        for t in range(1, tier + 1):
            result.update(
                TIER_1_TOOLS if t == 1 else TIER_2_TOOLS if t == 2 else TIER_3_TOOLS
            )
        logger.debug(
            "Context budget=%d -> tier=%d tools=%d servers", budget, tier, len(result)
        )
        return result

    def get_tier_for_budget(self, budget: int) -> int:
        return self._resolve_tier(budget)

    def _resolve_tier(self, budget: int) -> int:
        if budget <= 0:
            return 1
        if budget >= TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2] + TIER_TOKEN_COST[3]:
            return 3
        if budget >= TIER_TOKEN_COST[1] + TIER_TOKEN_COST[2]:
            return 2
        return 1

    def describe_tools(self, tools_by_server: dict) -> str:
        lines = []
        for server, tool_list in tools_by_server.items():
            for tool in tool_list:
                lines.append(f"  {server}.{tool}")
        return "\n".join(lines)

    def tier_name(self, budget: int) -> str:
        return TIER_NAME[self._resolve_tier(budget)]

    def suggest_next_tier(self, current_tier: int, query_complexity: float) -> str:
        if current_tier < 3 and query_complexity > 0.7:
            return (
                f"LOAD_MORE_TOOLS: current_tier={current_tier}, "
                f"need_tier={current_tier + 1}"
            )
        return ""
