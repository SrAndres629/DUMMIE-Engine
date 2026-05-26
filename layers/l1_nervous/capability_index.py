import os
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("dummie-mcp.capability-index")

DUMMIE_ROOT = os.environ.get(
    "DUMMIE_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)


class CapabilityIndex:
    """
    Índice canónico de capacidades disponibles en el sistema.
    Indexa MCP tools (locales + remotas) y skills (DUMMIE + Superpowers).
    NO usa embeddings — matching ontológico exacto.
    Skills NO se cargan hasta que se necesitan (lazy loading via router).
    """

    def __init__(self):
        self._capabilities: Dict[str, List[dict]] = {}
        self._skill_metadata: Dict[str, dict] = {}
        self._build_index()

    def _build_index(self):
        self._index_skills()
        if self._capabilities:
            logger.debug(
                "CapabilityIndex construido: %d categorías",
                len(self._capabilities),
            )

    def _index_skills(self):
        skills_dir = os.path.join(DUMMIE_ROOT, ".agents", "skills")
        if not os.path.isdir(skills_dir):
            return

        for entry in os.listdir(skills_dir):
            path = os.path.join(skills_dir, entry)
            if entry.endswith(".yaml"):
                self._index_skill_yaml(path, entry)
            elif os.path.isdir(path) and os.path.exists(os.path.join(path, "SKILL.md")):
                self._index_skill_dir(path, entry)

        superpowers_base = os.path.join(
            os.path.expanduser("~"), ".agents", "skills", "superpowers"
        )
        if os.path.isdir(superpowers_base):
            for skill_name in os.listdir(superpowers_base):
                skill_path = os.path.join(superpowers_base, skill_name)
                smd = os.path.join(skill_path, "SKILL.md")
                if os.path.isdir(skill_path) and os.path.exists(smd):
                    self._index_superpower_skill(skill_name, smd)

    def _index_skill_yaml(self, path: str, filename: str):
        try:
            with open(path) as f:
                content = f.read()
            import yaml

            data = yaml.safe_load(content) or {}
        except Exception:
            data = self._parse_yaml_fallback(path)

        skill_id = data.get("skill_id", data.get("name", filename.replace(".yaml", "")))
        description = data.get("description", data.get("purpose", ""))

        categories = self._classify_skill(skill_id, description)
        meta = {
            "id": skill_id,
            "type": "skill",
            "source": filename,
            "path": path,
            "description": description,
            "capabilities": categories,
        }
        self._skill_metadata[skill_id] = meta
        for cat in categories:
            self._capabilities.setdefault(cat, []).append(
                {
                    "id": f"skill.{skill_id}",
                    "name": skill_id,
                    "type": "skill",
                    "source": path,
                    "description": description,
                }
            )

    def _index_skill_dir(self, path: str, dirname: str):
        try:
            with open(os.path.join(path, "SKILL.md")) as f:
                content = f.read()
            first_line = content.split("\n")[0] if content else dirname
            description = first_line.lstrip("#").strip() or dirname
        except Exception:
            description = dirname

        skill_id = dirname
        categories = self._classify_skill(skill_id, description)
        meta = {
            "id": skill_id,
            "type": "skill",
            "source": dirname,
            "path": path,
            "description": description,
            "capabilities": categories,
        }
        self._skill_metadata[skill_id] = meta
        for cat in categories:
            self._capabilities.setdefault(cat, []).append(
                {
                    "id": f"skill.{skill_id}",
                    "name": skill_id,
                    "type": "skill",
                    "source": path,
                    "description": description,
                }
            )

    def _index_superpower_skill(self, skill_name: str, skill_md: str):
        try:
            with open(skill_md) as f:
                content = f.read()
            first_line = content.split("\n")[0] if content else skill_name
            description = first_line.lstrip("#").strip() or skill_name
        except Exception:
            description = skill_name

        skill_id = f"superpowers.{skill_name}"
        categories = self._classify_skill(skill_name, description)
        categories.add("development_workflow")
        meta = {
            "id": skill_id,
            "type": "superpower",
            "source": skill_name,
            "path": skill_md,
            "description": description,
            "capabilities": list(categories),
        }
        self._skill_metadata[skill_id] = meta
        for cat in categories:
            self._capabilities.setdefault(cat, []).append(
                {
                    "id": f"skill.{skill_id}",
                    "name": skill_id,
                    "type": "superpower",
                    "source": skill_md,
                    "description": description,
                }
            )

    def _parse_yaml_fallback(self, path: str) -> dict:
        result = {}
        try:
            with open(path) as f:
                for line in f:
                    if line.startswith("description:"):
                        result["description"] = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("skill_id:"):
                        result["skill_id"] = line.split(":", 1)[1].strip().strip('"')
        except Exception:
            pass
        return result

    def _classify_skill(self, skill_id: str, description: str) -> set:
        text = f"{skill_id} {description}".lower()
        cats = set()

        media_kw = [
            "image",
            "video",
            "audio",
            "generate",
            "media",
            "vision",
            "diffusion",
        ]
        code_kw = [
            "code",
            "coder",
            "implement",
            "architect",
            "program",
            "develop",
            "refactor",
        ]
        debug_kw = [
            "debug",
            "test",
            "fix",
            "bug",
            "quality",
            "verify",
            "lint",
        ]
        memory_kw = [
            "memory",
            "remember",
            "recall",
            "crystallize",
            "knowledge",
            "vault",
            "context",
        ]
        plan_kw = [
            "plan",
            "design",
            "spec",
            "brainstorm",
            "architect",
            "scaffold",
        ]
        infra_kw = [
            "deploy",
            "docker",
            "cloud",
            "infra",
            "server",
            "host",
            "network",
        ]
        comm_kw = [
            "communicate",
            "broadcast",
            "swarm",
            "delegate",
            "observe",
            "sync",
        ]
        governance_kw = [
            "audit",
            "compliance",
            "sentinel",
            "governance",
            "policy",
            "rule",
        ]
        automation_kw = [
            "n8n",
            "workflow",
            "webhook",
            "automation",
            "automate",
            "orchestrat",
        ]

        mappings = [
            ("media_generation", media_kw),
            ("code_development", code_kw),
            ("testing_debugging", debug_kw),
            ("memory_context", memory_kw),
            ("planning_design", plan_kw),
            ("infrastructure", infra_kw),
            ("communication", comm_kw),
            ("governance", governance_kw),
            ("workflow_automation", automation_kw),
        ]

        for cat, kws in mappings:
            if any(kw in text for kw in kws):
                cats.add(cat)

        if not cats:
            cats.add("general")

        return cats

    def add_mcp_server_config(
        self, server_name: str, profile: str, capability_class: str, rationale: str = ""
    ):
        text = f"{server_name} {profile} {capability_class} {rationale}".lower()
        categories = set()
        if "image" in text or "media" in text or "generate" in text:
            categories.add("media_generation")
        if "git" in text or "vcs" in text or "github" in text:
            categories.add("vcs")
        if "file" in text or "workspace" in text:
            categories.add("workspace_io")
        if "shell" in text or "bash" in text:
            categories.add("shell_execution")
        if "sql" in text or "data" in text or "store" in text:
            categories.add("data_access")
        if "cloud" in text or "infra" in text or "deploy" in text:
            categories.add("infrastructure")
        if "browser" in text:
            categories.add("browser_automation")
        if "docker" in text or "container" in text:
            categories.add("infrastructure")
        if "reasoning" in text or "think" in text:
            categories.add("reasoning")
        if "development" in text or "superpower" in text:
            categories.add("development_workflow")
        if (
            "n8n" in text
            or "workflow" in text
            or "webhook" in text
            or "automation" in text
            or capability_class == "workflow_automation"
        ):
            categories.add("workflow_automation")
        if server_name in ("git", "github") or capability_class == "vcs":
            categories.add("vcs")

        entry = {
            "id": f"remote.{server_name}",
            "name": server_name,
            "type": "remote_server",
            "description": f"[{profile}/{capability_class}] {rationale}",
        }

        for cat in categories or ["general"]:
            self._capabilities.setdefault(cat, []).append(entry)

    def add_mcp_tools(self, server_name: str, tools: List[dict]):
        for t in tools:
            name = t.get("name", "")
            desc = t.get("description", "")
            text = f"{server_name}.{name} {desc}".lower()

            categories = set()
            if "image" in text or "generate" in text:
                categories.add("media_generation")
            if "git" in text or "commit" in text or "branch" in text:
                categories.add("vcs")
            if "file" in text or "read" in text or "write" in text:
                categories.add("workspace_io")
            if "shell" in text or "bash" in text or "exec" in text:
                categories.add("shell_execution")
            if "sql" in text or "db" in text or "query" in text:
                categories.add("data_access")
            if "cloud" in text or "deploy" in text or "dns" in text:
                categories.add("infrastructure")
            if (
                "n8n" in text
                or "workflow" in text
                or "webhook" in text
                or "automation" in text
            ):
                categories.add("workflow_automation")

            entry = {
                "id": f"{server_name}.{name}",
                "name": name,
                "type": "mcp_tool",
                "server": server_name,
                "description": desc,
            }

            for cat in categories or ["general"]:
                self._capabilities.setdefault(cat, []).append(entry)

    def find_exact_match(
        self, domain: str, action: str, params: dict = None
    ) -> Optional[dict]:
        query = f"{domain}.{action}" if domain and action else domain
        query_lower = query.lower()
        results = []
        server_fallbacks = []

        for cat_key, tools in self._capabilities.items():
            for t in tools:
                tid = t["id"].lower()
                tdesc = f"{tid} {t.get('description', '')}".lower()
                tname = t.get("name", "").lower()

                if domain and action:
                    if domain.lower() in tid and action.lower() in tid:
                        results.append((t, 4))
                    elif domain.lower() in tid and action.lower() in tdesc:
                        results.append((t, 3))
                    elif domain.lower() in tdesc and action.lower() in tid:
                        results.append((t, 2))
                    elif domain.lower() in tdesc and action.lower() in tdesc:
                        results.append((t, 1))
                elif domain and not action:
                    if domain.lower() in tid:
                        results.append((t, 2))
                    elif domain.lower() in tdesc:
                        results.append((t, 1))

                if t["type"] == "remote_server" and domain and domain.lower() in tid:
                    server_fallbacks.append((t, 0.5))
                elif (
                    t["type"] == "remote_server"
                    and domain
                    and domain.lower() in t.get("name", "").lower()
                ):
                    server_fallbacks.append((t, 0.5))

        if results:
            results.sort(key=lambda x: -x[1])
            return results[0][0]

        if server_fallbacks:
            return server_fallbacks[0][0]

        best_cat = None
        best_score = 0
        for cat_key, tools in self._capabilities.items():
            ck = cat_key.lower()
            score = 0
            if domain and domain.lower() in ck:
                score += 1
            if action and action.lower() in ck:
                score += 1
            if score > best_score:
                best_score = score
                best_cat = (cat_key, tools)

        if best_cat and best_cat[1]:
            return best_cat[1][0]

        for cat_key, tools in self._capabilities.items():
            for t in tools:
                tid = t["id"].lower()
                if query_lower in tid:
                    return t

        return None

    def find_by_intent(self, domain: str, action: str) -> List[dict]:
        results = []
        query_parts = [p for p in [domain, action] if p]
        for cat_key, tools in self._capabilities.items():
            if all(p.lower() in cat_key.lower() for p in query_parts):
                results.extend(tools)
            for t in tools:
                tid_desc = f"{t['id']} {t.get('description', '')}".lower()
                if all(p.lower() in tid_desc for p in query_parts):
                    if t not in results:
                        results.append(t)
        return results

    def list_all(self) -> Dict[str, List[dict]]:
        return dict(self._capabilities)

    def list_skills(self) -> List[dict]:
        return list(self._skill_metadata.values())

    def get_skill(self, skill_id: str) -> Optional[dict]:
        return self._skill_metadata.get(skill_id)

    def sync_from_metagateway(self, meta_router_assignments_path: str = None):
        path = meta_router_assignments_path or os.path.join(
            os.path.dirname(__file__), "configs", "meta_router_assignments.json"
        )
        with open(path) as f:
            data = json.load(f)
        count = 0
        for gw_name, gw_cfg in data.get("gateways", {}).items():
            for srv_name, srv_cfg in gw_cfg.get("servers", {}).items():
                tools = srv_cfg.get("tools", ["*"])
                for tool in tools:
                    key = f"{gw_name}:{srv_name}:{tool}"
                    if key not in self._capabilities:
                        self._capabilities[key] = [
                            {
                                "gateway": gw_name,
                                "server": srv_name,
                                "tool": tool,
                                "port": gw_cfg.get("port"),
                                "domain": gw_cfg.get("domains", []),
                            }
                        ]
                        count += 1
        return count

    def sum_index(self) -> dict:
        total = 0
        counts = {}
        for cat, tools in self._capabilities.items():
            counts[cat] = len(tools)
            total += len(tools)
        return {
            "total_capabilities": total,
            "total_skills": len(self._skill_metadata),
            "categories": len(self._capabilities),
            "by_category": counts,
        }
