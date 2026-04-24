import yaml
import logging
import re
from typing import List, Dict, Any, Set
from pathlib import Path

# Nota: 'edge' debe estar en el PYTHONPATH para resolver esta importación en tiempo de ejecución
try:
    from edge import ToolDiscovery
except ImportError:
    ToolDiscovery = None

logger = logging.getLogger("skill-binder")


class SkillBinder:
    """
    Gestiona el enlace (binding) entre Skills YAML y Herramientas MCP.
    Incluye una red jerárquica de skills maestras/subskills para reducir
    carga cognitiva del LLM y forzar planes más estructurados por objetivo.
    """

    def __init__(self, skills_dir: str, mcp_gateway: Any):
        self.skills_dir = Path(skills_dir)
        self.mcp_gateway = mcp_gateway
        if ToolDiscovery:
            self.discovery = ToolDiscovery(mcp_gateway)
        else:
            logger.warning("L4_Edge not found in path. ToolDiscovery will be limited.")
            self.discovery = None

        # Compatibilidad hacia atrás: perfiles indexados por nombre
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        # Índices nuevos para consumo transversal
        self.skills_by_id: Dict[str, Dict[str, Any]] = {}
        self.master_skills: Dict[str, Dict[str, Any]] = {}
        self.capability_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.default_llm_limits: Dict[str, int] = {
            "max_candidate_skills": 12,
            "max_execution_steps": 8,
            "max_parallel_subskills": 3,
            "max_planning_depth": 3,
        }

    def load_all_skills(self):
        """
        Carga skills YAML (incluye subdirectorios), normaliza esquema y
        construye índices para selección jerárquica.
        """
        self.agent_profiles.clear()
        self.skills_by_id.clear()
        self.master_skills.clear()
        self.capability_index.clear()
        self.tag_index.clear()

        for yaml_file in sorted(self.skills_dir.rglob("*.yaml")):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    raw_docs = list(yaml.safe_load_all(f))
                raw = {}
                for doc in raw_docs:
                    if isinstance(doc, dict) and doc:
                        raw = doc
                        break
                if not isinstance(raw, dict):
                    logger.warning(f"Skipping non-dict skill YAML: {yaml_file}")
                    continue

                profile = self._normalize_profile(raw, yaml_file)
                self.skills_by_id[profile["skill_id"]] = profile

                # Compatibilidad con consumidores previos
                self.agent_profiles[profile["name"]] = profile

                if profile["skill_type"] == "master":
                    self.master_skills[profile["skill_id"]] = profile

                for cap in profile["capabilities"]:
                    self.capability_index.setdefault(cap, set()).add(profile["skill_id"])
                for tag in profile["tags"]:
                    self.tag_index.setdefault(tag, set()).add(profile["skill_id"])

                logger.info(f"Skill profile cached: {profile['skill_id']}")
            except Exception as e:
                logger.error(f"Failed to load skill YAML {yaml_file.name}: {e}")

        self._link_master_skills()

    async def validate_all_contracts(self):
        """Valida skills cargadas contra inventario real de capacidades (L4)."""
        inventory = []
        if self.discovery:
            inventory = await self.discovery.get_available_capabilities()
        inventory_lc = {c.lower() for c in inventory}

        for _, profile in self.skills_by_id.items():
            await self._validate_contract(profile, inventory_lc)

    def build_execution_plan(self, goal: str, preferred_master_skill: str = "") -> Dict[str, Any]:
        """
        Planificador reflectivo:
        1) Elige una skill maestra por objetivo.
        2) Expande subskills candidatas por id/capability/tag.
        3) Limita el plan por restricciones de contexto típicas de LLM.
        """
        goal_tokens = self._tokenize(goal)
        master = self._select_master_skill(goal_tokens, preferred_master_skill)

        if master:
            llm_limits = {**self.default_llm_limits, **master.get("llm_limits", {})}
            ordered_skills = self._expand_master_plan(master, goal_tokens, llm_limits)
            plan_type = "hierarchical"
        else:
            llm_limits = dict(self.default_llm_limits)
            ordered_skills = self._fallback_atomic_plan(goal_tokens, llm_limits)
            plan_type = "flat_fallback"

        steps = [
            {"order": idx + 1, "skill_id": sid, "name": self.skills_by_id[sid]["name"]}
            for idx, sid in enumerate(ordered_skills)
        ]

        return {
            "goal": goal,
            "plan_type": plan_type,
            "master_skill": master["skill_id"] if master else "",
            "steps": steps,
            "llm_limits": llm_limits,
            "total_steps": len(steps),
        }

    def propose_reflective_plan(self, goal: str, preferred_master_skill: str = "") -> Dict[str, Any]:
        """Alias semántico para consumidores de alto nivel."""
        return self.build_execution_plan(goal, preferred_master_skill)

    async def _validate_contract(self, profile: Dict[str, Any], inventory_lc: Set[str]):
        """Valida capacidades físicas reales y coherencia de red master/subskills."""
        if profile["skill_type"] == "master":
            missing = [
                sid for sid in profile.get("resolved_subskills", [])
                if sid not in self.skills_by_id
            ]
            if missing:
                logger.error(
                    f"Master skill {profile['skill_id']} references unknown subskills: {missing}"
                )
                raise RuntimeError(f"Unknown subskills in {profile['skill_id']}: {missing}")
            return

        if not self.discovery:
            logger.warning("Skipping contract validation: L4 Sensor offline.")
            return

        # Skills abstractas (sw.*) representan intención conceptual y no herramienta física.
        if profile["skill_id"].startswith("sw."):
            return

        try:
            required = profile.get("capabilities", [])
            for cap in required:
                cap_lc = cap.lower()
                exists = cap_lc in inventory_lc or any(
                    inv.endswith(f".{cap_lc}") for inv in inventory_lc
                )
                if not exists:
                    logger.critical(
                        f"Contract Mismatch: {cap} missing for {profile['skill_id']}"
                    )
                    raise RuntimeError(f"Missing capability: {cap}")
        except Exception as e:
            logger.error(f"Validation failed for {profile['skill_id']}: {e}")
            raise

    def _normalize_profile(self, raw: Dict[str, Any], source_path: Path) -> Dict[str, Any]:
        skill_id = str(raw.get("skill_id") or raw.get("id") or f"file.{source_path.stem}").strip()
        name = str(raw.get("name") or source_path.stem).strip()
        description = str(raw.get("description") or "").strip()
        capabilities = self._normalize_capabilities(raw.get("capabilities", []))
        tags = self._normalize_string_list(raw.get("tags", []))
        objectives = self._normalize_string_list(raw.get("objectives", []))
        invariants = self._normalize_string_list(raw.get("invariants", []))

        subskills = self._normalize_subskills(raw.get("subskills", []))
        phases = raw.get("phases", [])
        if isinstance(phases, list):
            for phase in phases:
                if not isinstance(phase, dict):
                    continue
                subskills.extend(self._normalize_subskills(phase.get("subskills", [])))

        skill_type = str(raw.get("skill_type") or "").strip().lower()
        if not skill_type:
            skill_type = "master" if subskills else "atomic"

        llm_limits = dict(self.default_llm_limits)
        raw_limits = raw.get("llm_limits", {})
        if isinstance(raw_limits, dict):
            for key in self.default_llm_limits:
                if key in raw_limits:
                    try:
                        llm_limits[key] = int(raw_limits[key])
                    except (TypeError, ValueError):
                        logger.warning(f"Invalid llm_limits.{key} in {skill_id}; using default.")

        return {
            "skill_id": skill_id,
            "name": name,
            "description": description,
            "skill_type": skill_type,
            "capabilities": capabilities,
            "tags": tags,
            "objectives": objectives,
            "invariants": invariants,
            "subskills": subskills,
            "resolved_subskills": [],
            "llm_limits": llm_limits,
            "metadata": raw.get("metadata", {}) if isinstance(raw.get("metadata"), dict) else {},
            "source": str(source_path),
        }

    def _normalize_capabilities(self, raw_caps: Any) -> List[str]:
        out: List[str] = []
        if isinstance(raw_caps, list):
            for item in raw_caps:
                if isinstance(item, str):
                    out.append(item.strip().lower())
                elif isinstance(item, dict):
                    cap = item.get("id") or item.get("name")
                    if cap:
                        out.append(str(cap).strip().lower())
        elif isinstance(raw_caps, str):
            out.append(raw_caps.strip().lower())
        return [c for c in dict.fromkeys(out) if c]

    def _normalize_string_list(self, raw_list: Any) -> List[str]:
        if not isinstance(raw_list, list):
            return []
        out = []
        for item in raw_list:
            if isinstance(item, str):
                out.append(item.strip().lower())
        return [x for x in dict.fromkeys(out) if x]

    def _normalize_subskills(self, raw_subskills: Any) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        if not isinstance(raw_subskills, list):
            return normalized

        for item in raw_subskills:
            if isinstance(item, str):
                normalized.append({"skill_id": item.strip()})
                continue
            if not isinstance(item, dict):
                continue

            skill_id = str(item.get("skill_id") or "").strip()
            capability = str(item.get("capability") or "").strip().lower()
            tags = self._normalize_string_list(item.get("tags", []))

            if skill_id or capability or tags:
                normalized.append(
                    {"skill_id": skill_id, "capability": capability, "tags": tags}
                )
        return normalized

    def _link_master_skills(self):
        for skill_id, profile in self.master_skills.items():
            resolved: List[str] = []
            seen = set()
            for selector in profile.get("subskills", []):
                candidates = []

                ref_id = selector.get("skill_id", "")
                if ref_id:
                    candidates = [ref_id]
                elif selector.get("capability"):
                    cap = selector["capability"]
                    candidates = sorted(self.capability_index.get(cap, set()))
                elif selector.get("tags"):
                    tag_hits = set()
                    for tag in selector["tags"]:
                        tag_hits.update(self.tag_index.get(tag, set()))
                    candidates = sorted(tag_hits)

                for candidate in candidates:
                    if candidate == skill_id:
                        continue
                    if candidate not in self.skills_by_id:
                        continue
                    if candidate in seen:
                        continue
                    seen.add(candidate)
                    resolved.append(candidate)

            profile["resolved_subskills"] = resolved

    def _select_master_skill(self, goal_tokens: Set[str], preferred_master_skill: str) -> Dict[str, Any]:
        if preferred_master_skill and preferred_master_skill in self.master_skills:
            return self.master_skills[preferred_master_skill]

        ranked = []
        for _, profile in self.master_skills.items():
            score = self._score_profile(profile, goal_tokens) + 2.0
            ranked.append((score, profile))
        ranked.sort(key=lambda x: x[0], reverse=True)
        if not ranked or ranked[0][0] <= 0:
            return {}
        return ranked[0][1]

    def _expand_master_plan(
        self, master: Dict[str, Any], goal_tokens: Set[str], llm_limits: Dict[str, int]
    ) -> List[str]:
        max_steps = max(1, llm_limits.get("max_execution_steps", 8))
        max_candidates = max(1, llm_limits.get("max_candidate_skills", 12))

        ranked = []
        for sid in master.get("resolved_subskills", [])[:max_candidates]:
            profile = self.skills_by_id.get(sid)
            if not profile:
                continue
            ranked.append((self._score_profile(profile, goal_tokens), sid))
        ranked.sort(key=lambda x: x[0], reverse=True)

        plan = [master["skill_id"]]
        for _, sid in ranked:
            if len(plan) >= max_steps:
                break
            plan.append(sid)
        return plan

    def _fallback_atomic_plan(self, goal_tokens: Set[str], llm_limits: Dict[str, int]) -> List[str]:
        max_steps = max(1, llm_limits.get("max_execution_steps", 8))
        ranked = []
        for sid, profile in self.skills_by_id.items():
            if profile.get("skill_type") != "atomic":
                continue
            ranked.append((self._score_profile(profile, goal_tokens), sid))
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [sid for score, sid in ranked if score > 0][:max_steps]

    def _score_profile(self, profile: Dict[str, Any], goal_tokens: Set[str]) -> float:
        text_parts = [
            profile.get("name", ""),
            profile.get("description", ""),
            " ".join(profile.get("capabilities", [])),
            " ".join(profile.get("tags", [])),
            " ".join(profile.get("objectives", [])),
            " ".join(profile.get("invariants", [])),
        ]
        haystack_tokens = self._tokenize(" ".join(text_parts))
        overlap = goal_tokens.intersection(haystack_tokens)
        if not overlap:
            return 0.0
        return float(len(overlap))

    def _tokenize(self, text: str) -> Set[str]:
        tokens = re.findall(r"[a-zA-Z0-9_./-]+", (text or "").lower())
        normalized = set()
        for token in tokens:
            normalized.add(token)
            normalized.update(part for part in token.replace(".", "_").split("_") if part)
        return normalized
