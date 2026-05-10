from __future__ import annotations

import json
from typing import Any

__spec_id__ = "DE-V2-L1-44"


class LocalReasoningToolService:
    def __init__(
        self,
        proxy_manager: Any,
        internal_mcp: Any,
        orchestrator: Any,
        use_cases: Any = None,
        reasoning_service: Any = None,
        use_embeddings: bool = False,
    ):
        self.proxy_manager = proxy_manager
        self.internal_mcp = internal_mcp
        self.orchestrator = orchestrator
        self.use_cases = use_cases
        self.use_embeddings = use_embeddings
        if reasoning_service is None:
            try:
                from layers.l2_brain.local_reasoning import LocalReasoningService
            except ImportError:
                from local_reasoning import LocalReasoningService

            reasoning_service = LocalReasoningService()
        self.reasoning_service = reasoning_service

    async def semantic_recall(
        self,
        goal: str,
        query: str = "",
        top_k: int = 10,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        sources = sources or ["mcp", "knowledge", "4d_tes"]
        query_text = query or goal
        candidates: list[dict[str, Any]] = []
        diagnostics: list[str] = []

        if "mcp" in sources:
            candidates.extend(self._local_mcp_candidates(query_text))
            candidates.extend(self._remote_registry_candidates(query_text))
        if "remote_tools" in sources:
            candidates.extend(await self._remote_tool_candidates(query_text))
        if "knowledge" in sources:
            try:
                candidates.extend(await self._knowledge_candidates(query_text, top_k))
            except Exception as exc:
                diagnostics.append(f"knowledge_unavailable:{exc}")
        if "4d_tes" in sources:
            try:
                candidates.extend(self._memory_candidates(query_text, top_k))
            except Exception as exc:
                diagnostics.append(f"4d_tes_unavailable:{exc}")

        candidates.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        return {
            "provider_status": "ok",
            "query": query_text,
            "candidates": candidates[: max(1, top_k)],
            "diagnostics": diagnostics,
        }

    async def tool_card_resolver(self, targets: list[str]) -> dict[str, Any]:
        cards = []
        for target in targets:
            card = await self._resolve_tool_card(target)
            if card:
                cards.append(card)
        return {"tool_cards": cards}

    async def reasoned_rerank(
        self,
        goal: str,
        candidates: list[dict[str, Any]],
        max_selected: int = 5,
        mode: str = "shadow",
    ) -> dict[str, Any]:
        return self.reasoning_service.reasoned_rerank(goal, candidates, max_selected, mode)

    async def context_shaper(
        self,
        goal: str,
        ranked: list[dict[str, Any]],
        token_budget: int = 4000,
        cloud_agent: str = "generic",
    ) -> dict[str, Any]:
        return self.reasoning_service.context_shaper(goal, ranked, token_budget, cloud_agent)

    async def selection_feedback(
        self,
        session_id: str,
        goal: str,
        selected_tools: list[str],
        outcome: str,
        evidence_refs: list[str],
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "kind": "LOCAL_REASONING_SELECTION_FEEDBACK",
            "session_id": session_id,
            "goal": goal,
            "selected_tools": selected_tools,
            "outcome": outcome,
            "evidence_refs": evidence_refs,
            "metrics": metrics or {},
        }
        if not self.use_cases:
            return {"status": "SKIPPED", "reason": "persistence_unavailable", "payload": payload}

        context = {
            "locus_x": "layers.l1_nervous.local_reasoning",
            "locus_y": "L1_TRANSPORT",
            "locus_z": "L2_BRAIN",
            "lamport_t": float(getattr(self.orchestrator, "lamport_clock", 0)),
            "authority_a": "AGENT",
            "intent_i": "CRYSTALLIZATION",
        }
        result = await self.use_cases.execute_crystallization(json.dumps(payload, ensure_ascii=False), context)
        return {"status": "PERSISTED", "result": result, "payload": payload}

    def _local_mcp_candidates(self, query_text: str) -> list[dict[str, Any]]:
        candidates = []
        for tool in self.internal_mcp._tool_manager.list_tools():
            target = f"local.{tool.name}"
            description = getattr(tool, "description", "") or ""
            text = f"{tool.name} {description}"
            candidates.append(
                {
                    "id": target,
                    "source": "mcp.local",
                    "text": text,
                    "description": description,
                    "score": self._score(query_text, text),
                    "schema_ref": target,
                    "evidence_refs": [],
                    "side_effect_level": classify_side_effect(tool.name, description),
                }
            )
        return candidates

    def _remote_registry_candidates(self, query_text: str) -> list[dict[str, Any]]:
        candidates = []
        for server_name, cfg in getattr(self.proxy_manager, "servers", {}).items():
            if isinstance(cfg, dict) and cfg.get("disabled"):
                continue
            profile = cfg.get("profile", "default") if isinstance(cfg, dict) else "default"
            capability_class = cfg.get("capability_class", "remote_capability") if isinstance(cfg, dict) else "remote_capability"
            rationale = cfg.get("rationale", "Remote MCP capability available through the gateway.") if isinstance(cfg, dict) else ""
            text = f"{server_name} {profile} {capability_class} {rationale}"
            candidates.append(
                {
                    "id": f"remote.{server_name}",
                    "source": "mcp.remote_registry",
                    "text": text,
                    "description": rationale,
                    "score": self._score(query_text, text),
                    "schema_ref": server_name,
                    "evidence_refs": [],
                    "side_effect_level": "external",
                }
            )
        return candidates

    async def _remote_tool_candidates(self, query_text: str) -> list[dict[str, Any]]:
        candidates = []
        for server_name, cfg in getattr(self.proxy_manager, "servers", {}).items():
            if isinstance(cfg, dict) and cfg.get("disabled"):
                continue
            try:
                for tool in await self.proxy_manager.get_tools_for_server(server_name):
                    name = tool.get("name", "")
                    description = tool.get("description", "") or ""
                    target = f"{server_name}.{name}"
                    text = f"{server_name} {name} {description}"
                    candidates.append(
                        {
                            "id": target,
                            "source": "mcp.remote",
                            "text": text,
                            "description": description,
                            "score": self._score(query_text, text),
                            "schema_ref": target,
                            "evidence_refs": [],
                            "side_effect_level": "external",
                        }
                    )
            except Exception:
                continue
        return candidates

    async def _knowledge_candidates(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        from tools_impl.knowledge import KnowledgeToolService

        service = KnowledgeToolService(self.proxy_manager)
        artifacts = await service.search_context(query_text, limit=top_k)
        candidates = []
        for artifact in artifacts:
            text = str(artifact.get("content") or artifact.get("source_uri") or "")
            candidates.append(
                {
                    "id": artifact.get("source_uri", ""),
                    "source": f"knowledge.{artifact.get('provider', 'unknown')}",
                    "text": text,
                    "score": self._score(query_text, text),
                    "schema_ref": "",
                    "evidence_refs": [artifact.get("payload_hash", "")],
                    "side_effect_level": "read",
                }
            )
        return candidates

    def _memory_candidates(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        event_store = getattr(self.orchestrator, "event_store", None)
        if not event_store or not hasattr(event_store, "find_similar_nodes"):
            return []
        matches = event_store.find_similar_nodes(query_text, limit=top_k, include_proof_subgraph=True)
        candidates = []
        for match in matches:
            candidates.append(
                {
                    "id": f"4d_tes.{match.get('hash', '')}",
                    "source": "4d_tes",
                    "text": str(match.get("payload", "")),
                    "score": float(match.get("score", 0.0)),
                    "schema_ref": "",
                    "evidence_refs": match.get("proof_subgraph", [match.get("hash", "")]),
                    "side_effect_level": "read",
                }
            )
        return candidates

    async def _resolve_tool_card(self, target: str) -> dict[str, Any] | None:
        if target.startswith("local."):
            name = target.split("local.", 1)[1]
            for tool in self.internal_mcp._tool_manager.list_tools():
                if tool.name == name:
                    description = getattr(tool, "description", "") or ""
                    side_effect = classify_side_effect(tool.name, description)
                    return {
                        "target": target,
                        "description": description,
                        "input_schema": getattr(tool, "parameters", {}),
                        "preconditions": ["schema_must_validate"],
                        "anti_patterns": anti_patterns_for(side_effect),
                        "side_effect_level": side_effect,
                        "examples": [],
                        "embedding_text": f"{target} {description}",
                    }
            return None

        if target.startswith("remote."):
            server_name = target.split("remote.", 1)[1]
            cfg = getattr(self.proxy_manager, "servers", {}).get(server_name)
            if not isinstance(cfg, dict) or cfg.get("disabled"):
                return None
            description = cfg.get("rationale", "Remote MCP capability available through the gateway.")
            profile = cfg.get("profile", "default")
            capability_class = cfg.get("capability_class", "remote_capability")
            return {
                "target": target,
                "description": description,
                "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                "preconditions": ["discover_specific_remote_tool_before_execution"],
                "anti_patterns": ["do_not_start_remote_server_for_registry_inspection"],
                "side_effect_level": "external",
                "examples": [],
                "embedding_text": f"{server_name} {profile} {capability_class} {description}",
            }

        if "." not in target:
            return None
        server_name, tool_name = target.split(".", 1)
        for tool in await self.proxy_manager.get_tools_for_server(server_name):
            if tool.get("name") == tool_name:
                description = tool.get("description", "") or ""
                return {
                    "target": target,
                    "description": description,
                    "input_schema": tool.get("inputSchema", {}),
                    "preconditions": ["remote_server_available", "schema_must_validate"],
                    "anti_patterns": ["do_not_execute_without_sdd_admission"],
                    "side_effect_level": "external",
                    "examples": [],
                    "embedding_text": f"{target} {description}",
                }
        return None

    def _score(self, query_text: str, text: str) -> float:
        lexical = lexical_score(query_text, text)
        if not self.use_embeddings:
            return lexical
        try:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
        except ImportError:
            try:
                from embedding_provider import EmbeddingProvider
            except ImportError:
                return lexical
        try:
            q_vec = EmbeddingProvider.generate_vector(query_text)
            t_vec = EmbeddingProvider.generate_vector(text)
            return max(lexical, EmbeddingProvider.similarity(q_vec, t_vec))
        except Exception:
            return lexical


def register_local_reasoning_tools(mcp, use_cases, internal_mcp):
    service = LocalReasoningToolService(
        proxy_manager=use_cases.proxy_manager,
        internal_mcp=internal_mcp,
        orchestrator=use_cases.orchestrator,
        use_cases=use_cases,
        use_embeddings=True,
    )

    @mcp.tool()
    async def semantic_recall(
        goal: str,
        query: str = "",
        top_k: int = 10,
        sources: list[str] = ["mcp", "knowledge", "4d_tes"],
    ) -> str:
        """[LOCAL_REASONING] Recupera candidatos desde MCP, conocimiento y 4D-TES sin ejecutar acciones."""
        return json.dumps(await service.semantic_recall(goal, query, top_k, sources), ensure_ascii=False)

    @mcp.tool()
    async def tool_card_resolver(targets: list[str]) -> str:
        """[LOCAL_REASONING] Normaliza schemas, riesgos y texto indexable de herramientas MCP."""
        return json.dumps(await service.tool_card_resolver(targets), ensure_ascii=False)

    @mcp.tool()
    async def reasoned_rerank(
        goal: str,
        candidates: list[dict[str, Any]],
        max_selected: int = 5,
        mode: str = "shadow",
    ) -> str:
        """[LOCAL_REASONING] Reordena candidatos con Gemma local o fallback determinista en modo sombra."""
        return json.dumps(await service.reasoned_rerank(goal, candidates, max_selected, mode), ensure_ascii=False)

    @mcp.tool()
    async def context_shaper(
        goal: str,
        ranked: list[dict[str, Any]],
        token_budget: int = 4000,
        cloud_agent: str = "generic",
    ) -> str:
        """[LOCAL_REASONING] Produce un paquete compacto para agentes de nube."""
        return json.dumps(await service.context_shaper(goal, ranked, token_budget, cloud_agent), ensure_ascii=False)

    @mcp.tool()
    async def selection_feedback(
        session_id: str,
        goal: str,
        selected_tools: list[str],
        outcome: str,
        evidence_refs: list[str],
        metrics: dict[str, Any] = {},
    ) -> str:
        """[LOCAL_REASONING] Persiste feedback estructurado de seleccion en 4D-TES."""
        return json.dumps(
            await service.selection_feedback(session_id, goal, selected_tools, outcome, evidence_refs, metrics),
            ensure_ascii=False,
        )


def classify_side_effect(name: str, description: str = "") -> str:
    haystack = f"{name} {description}".lower()
    if any(word in haystack for word in ["delete", "remove", "overwrite", "reset", "destructive"]):
        return "destructive"
    if any(word in haystack for word in ["write", "persist", "crystallize", "log", "append", "export", "ingest"]):
        return "write"
    if any(word in haystack for word in ["remote", "notify", "send", "spawn", "delegate"]):
        return "external"
    return "read"


def anti_patterns_for(side_effect: str) -> list[str]:
    if side_effect == "read":
        return ["do_not_treat_unverified_results_as_fact"]
    if side_effect == "destructive":
        return ["do_not_execute_without_human_approval", "do_not_bypass_sdd_guards"]
    return ["do_not_execute_without_sdd_admission"]


def lexical_score(query_text: str, text: str) -> float:
    query_tokens = set(_tokens(query_text))
    text_tokens = set(_tokens(text))
    if not query_tokens or not text_tokens:
        return 0.0
    return round(len(query_tokens & text_tokens) / len(query_tokens), 4)


def _tokens(text: str) -> list[str]:
    import re

    return [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(token) > 2]
