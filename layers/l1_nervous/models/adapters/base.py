import abc, enum, time, logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("dummie-mcp.models")


class ModelType(enum.Enum):
    EMBEDDING = "embedding"
    LLM = "llm"
    RERANKER = "reranker"
    ROUTER = "router"


class ModelState(enum.Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    CLOSED = "closed"


class OntologyClass(enum.Enum):
    SEMANTIC = "semantic"
    REASONING = "reasoning"
    CODE = "code"
    SEARCH = "search"
    MEMORY = "memory"
    ROUTING = "routing"
    UNCERTAINTY = "uncertainty"


@dataclass
class ModelSpec:
    model_id: str
    model_type: ModelType
    ontology: OntologyClass
    priority: int = 5
    vram_mb: int = 0
    ram_mb: int = 0
    config: dict = field(default_factory=dict)


@dataclass
class ModelMetrics:
    load_count: int = 0
    total_inference_ms: float = 0.0
    last_used: float = 0.0
    error_count: int = 0


class BaseModelAdapter(abc.ABC):
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.state = ModelState.UNLOADED
        self.metrics = ModelMetrics()
        self._model = None

    @abc.abstractmethod
    async def _load_model(self):
        pass

    async def load(self):
        if self.state == ModelState.READY:
            return
        self.state = ModelState.LOADING
        try:
            await self._load_model()
            self.state = ModelState.READY
            self.metrics.load_count += 1
            logger.info(
                f"Model {self.spec.model_id} ready (vram={self.spec.vram_mb}MB)"
            )
        except Exception as e:
            self.state = ModelState.ERROR
            self.metrics.error_count += 1
            logger.error(f"Model {self.spec.model_id} failed: {e}")
            raise

    async def close(self):
        self._model = None
        self.state = ModelState.CLOSED
        logger.info(f"Model {self.spec.model_id} closed")

    def touch(self):
        self.metrics.last_used = time.time()

    @property
    def is_ready(self) -> bool:
        return self.state == ModelState.READY

    @property
    def idle_seconds(self) -> float:
        return (
            time.time() - self.metrics.last_used
            if self.metrics.last_used
            else float("inf")
        )

    @abc.abstractmethod
    async def health(self) -> dict:
        return {"model_id": self.spec.model_id, "state": self.state.value}
