import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger("brain.orchestrator")


class _LessonsUseCaseBridge:
    def __init__(self, ledger_audit: Any):
        self._ledger_audit = ledger_audit

    def _json_safe(self, value: Any):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {k: self._json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._json_safe(v) for v in value]
        if hasattr(value, "__dict__"):
            return self._json_safe(value.__dict__)
        return value

    def execute_error(self, context: Any, error: Exception, tick: int, correction: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "issue": str(error),
            "correction": correction,
            "tick": tick,
            "context": self._json_safe(getattr(context, "__dict__", str(context))),
        }
        if hasattr(self._ledger_audit, "log_lesson"):
            self._ledger_audit.log_lesson(entry)

    def execute_ambiguity(self, context: Any, ambiguity: str, plan: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "ambiguity": ambiguity,
            "plan": plan,
            "context": self._json_safe(getattr(context, "__dict__", str(context))),
        }
        if hasattr(self._ledger_audit, "log_ambiguity"):
            self._ledger_audit.log_ambiguity(entry)


class CognitiveOrchestrator:
    """
    [L2_BRAIN] Orquestador Cognitivo (Legacy/Bridge).
    Actúa como fachada para el nuevo Antigravity Daemon.
    """
    def __init__(self, shield_port: Any, event_store: Any, ledger_audit: Any, session_ledger: Any, skill_repo: Any):
        self.shield = shield_port
        self.event_store = event_store
        self.ledger_audit = ledger_audit
        self.session_ledger = session_ledger
        self.skill_repo = skill_repo
        # Bridge compatibility: L1 MCP tools read this clock directly.
        self.lamport_clock = 0
        self.lessons_use_case = _LessonsUseCaseBridge(ledger_audit)
        
        # [AUTO-EVOLUTION CABLES]
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace_root = os.path.dirname(os.path.dirname(_current_dir))
        aiwg_dir = os.path.join(self.workspace_root, ".aiwg")


            
        # [WAVE 2] Conectar el DummieDaemon y el AsyncEventBus
        try:
            from event_bus import AsyncEventBus
            from daemon import DummieDaemon
            from token_ledger import TokenLedger
            from model_router import ModelRouter
            from model_executor import ModelExecutor
            from model_discovery import ModelDiscoveryService
            from semantic_cache import SemanticCache
            from neuron_ledger import NeuronLedger
            from action_graph import ActionGraph
            from supervisor_protocol import SupervisorProtocol
            from entity_voice import EntityVoice
            from auto_evolution import CognitiveAutoEvolver
            
            # [WAVE 3] Contabilidad y Modelos
            ledger_path = os.path.join(aiwg_dir, "ledger/token_usage.jsonl")
            self.token_ledger = TokenLedger(ledger_path)
            self.model_executor = ModelExecutor(self.token_ledger)
            
            # Descubrimiento dinámico (asíncrono en background)
            self.model_router = ModelRouter(ledger=self.token_ledger)
            self.discovery_service = ModelDiscoveryService()
            
            # [WAVE 4] Sistema Social y Cache
            self.semantic_cache = SemanticCache(self.skill_repo) # skill_repo is the KuzuRepo here
            self.neuron_ledger = NeuronLedger()
            self.action_graph = ActionGraph(self.skill_repo)
            self.supervisor_protocol = SupervisorProtocol(self.model_executor, self.model_router)
            self.entity_voice = EntityVoice()
            self.auto_evolver = CognitiveAutoEvolver(workspace_root=os.getcwd())
            
            # [WAVE 8] Integrated SDKs (Obsidian & Socraticode)
            self.obsidian = None
            self.socraticode = None
            
            self.event_bus = AsyncEventBus()
            self.daemon = DummieDaemon(
                ledger_path=getattr(self.ledger_audit, "ledger_path", "sovereign_resolutions.jsonl"),
                mcp_gateway=None, # Will be injected later if needed
                event_bus=self.event_bus,
                skill_binder=None,
                event_store=self.event_store,
                model_router=self.model_router,
                model_executor=self.model_executor,
                semantic_cache=self.semantic_cache,
                neuron_ledger=self.neuron_ledger,
                action_graph=self.action_graph,
                supervisor_protocol=self.supervisor_protocol,
                entity_voice=self.entity_voice,
                auto_evolver=self.auto_evolver
            )
            self.daemon.obsidian = None # Will be set by set_mcp_gateway
            self.daemon.socraticode = None # Will be set by set_mcp_gateway
            self._daemon_task = None
            logger.info("DummieDaemon (Wave 4) conectado e inicializado en CognitiveOrchestrator.")
            
            # Trigger discovery
            async def _lazy_discovery():
                registry = await self.discovery_service.discover_all()
                self.model_router.registry = registry
            
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_lazy_discovery())
            except RuntimeError:
                pass # No loop yet

        def set_mcp_gateway(self, mcp_gateway: Any):
            """Inyecta el Meta-Gateway (L1 Proxy) y activa los SDKs integrados."""
            self.daemon.mcp_gateway = mcp_gateway
            
            # Inicialización de SDKs Generados
            try:
                from layers.l1_nervous.generated.obsidian_sdk import ObsidianClient
                from layers.l1_nervous.generated.socraticode_sdk import SocraticodeClient
                
                self.obsidian = ObsidianClient(mcp_gateway)
                self.socraticode = SocraticodeClient(mcp_gateway)
                
                self.daemon.obsidian = self.obsidian
                self.daemon.socraticode = self.socraticode
                
                # Inyectar en EntityVoice para Archival
                if self.entity_voice:
                    self.entity_voice.obsidian = self.obsidian
                
                # Inyectar en Auto-Evolver para análisis de Blast Radius
                if self.auto_evolver:
                    self.auto_evolver.socraticode = self.socraticode
                
                logger.info("Integrated SDKs (Obsidian & Socraticode) Materialized.")
            except ImportError as e:
                logger.warning(f"Failed to load integrated SDKs: {e}")
                
        except Exception as e:
            logger.error(f"Fallo al inicializar DummieDaemon Wave 3: {e}")
            self.daemon = None

        logger.info("CognitiveOrchestrator Materialized (Tabula Rasa Bridge)")

    def _ensure_daemon_running(self):
        import asyncio
        if self.daemon and self._daemon_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._daemon_task = loop.create_task(self.daemon.run_forever())
            except RuntimeError:
                pass # No running loop yet

    async def process_intent(self, intent: Any):
        self._ensure_daemon_running()
        self.lamport_clock += 1
        goal = getattr(intent, "goal", "") or getattr(intent, "rationale", str(intent))
        logger.info(f"Processing intent: {goal}")
        
        # Si el daemon está vivo, despachar la intención allí
        if self.daemon:
            from gateway_contract import GatewayRequest
            try:
                # Construir el GatewayRequest
                dag_xml = f"<dag><task id='t1'></task></dag>" # Stub DAG
                req = GatewayRequest(session_id=f"intent_{self.lamport_clock}", goal=goal, dag_xml=dag_xml)
                await self.daemon.submit_intent(req)
            except Exception as e:
                logger.error(f"Error submitting intent to Daemon: {e}")

        # Persistencia 4D-TES (Spec 02) - Esquema SOVEREIGN-4D
        if self.event_store and getattr(self.event_store, "conn", None):
            from enum import Enum
            try:
                from .models import MemoryNode4D
            except ImportError:
                try:
                    from models import MemoryNode4D
                except ImportError:
                    try:
                        from l2_brain.models import MemoryNode4D
                    except ImportError:
                        # Fallback path if run from different context
                        from layers.l2_brain.models import MemoryNode4D
            
            parent_hash = self.event_store.get_last_leaf_hash()
            
            # Extraer dimensiones (Spec 12 / 6D Model)
            locus_x = getattr(intent, "locus_x", "sw.strategy.discovery")
            authority_a = getattr(intent, "authority_a", "HUMAN")
            if isinstance(authority_a, Enum): authority_a = authority_a.value
            intent_i = getattr(intent, "intent_i", "RESOLUTION")
            if isinstance(intent_i, Enum): intent_i = intent_i.value
            
            node = MemoryNode4D.from_intent_context(
                parent_hashes=[parent_hash],
                locus_x=locus_x,
                locus_y='L1_TRANSPORT',
                locus_z='L2_BRAIN',
                lamport_t=self.lamport_clock,
                authority_a=authority_a,
                intent_i=intent_i,
                payload=goal
            )
            
            try:
                self.event_store.create_memory_node(node)
                causal_hash = node.causal_hash
                logger.info(f"4D-TES Persistence OK: {causal_hash}")
                return {"status": "ACK", "intent_id": causal_hash}
            except Exception as e:
                logger.error(f"4D-TES Persistence CRITICAL FAILURE: {e}")
                # En modo degradado podríamos continuar, pero aquí estamos forzando contrato.
                if not getattr(self.event_store, "read_only", False):
                    raise RuntimeError(f"Failed to persist intent to 4D-TES: {e}")
        
        return {"status": "ACK", "intent_id": "LEGACY-01"}

    async def handle_task(self, intent: Any):
        # Legacy MCP tools call handle_task and expect this status string.
        result = await self.process_intent(intent)
        if result.get("intent_id") != "LEGACY-01":
            return f"INTENT_QUEUED_L2_VALIDATED:{result['intent_id']}"
        return "INTENT_QUEUED_L2_VALIDATED"
