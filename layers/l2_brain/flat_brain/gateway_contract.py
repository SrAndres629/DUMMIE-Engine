from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any
import xml.etree.ElementTree as ET
from enum import Enum

class AgentLocus(str, Enum):
    SPEC = "sw.spec.architect"
    SYNTH = "sw.synth.behavior"
    IMPL = "sw.impl.clean"
    VAL = "sw.ctrl.validator"
    MEM = "sw.ctrl.memory"

class TaskExecution(BaseModel):
    task_id: str
    agent_locus: AgentLocus
    intent: str
    arguments: Dict[str, str]
    depends_on: List[str] = Field(default_factory=list)

class GatewayRequest(BaseModel):
    """
    Contrato JSON para la ingesta de intenciones en el MAS Gateway.
    """
    session_id: str
    goal: str
    dag_xml: str  # El DAG se define en XML para anclaje AST y enrutamiento complejo
    priority: int = 1

    @field_validator("dag_xml")
    @classmethod
    def validate_dag_structure(cls, v: str):
        try:
            root = ET.fromstring(v)
            if root.tag != "dag":
                raise ValueError("XML root must be <dag>")

            ids: set[str] = set()
            graph: dict[str, list[str]] = {}

            for task in root.findall("task"):
                task_id = task.get("id")
                if not task_id:
                    raise ValueError("Task missing ID")
                if task_id in ids:
                    raise ValueError(f"Duplicate task id: {task_id}")
                ids.add(task_id)
                graph[task_id] = []

            for task in root.findall("task"):
                task_id = task.get("id")
                for dep in task.findall("depends_on"):
                    dep_id = (dep.text or "").strip()
                    if dep_id not in ids:
                        raise ValueError(f"Task {task_id} depends on unknown task {dep_id}")
                    graph[task_id].append(dep_id)

            visiting: set[str] = set()
            visited: set[str] = set()

            def visit(node: str) -> None:
                if node in visiting:
                    raise ValueError(f"DAG cycle detected at task {node}")
                if node in visited:
                    return
                visiting.add(node)
                for dep in graph[node]:
                    visit(dep)
                visiting.remove(node)
                visited.add(node)

            for task_id in sorted(ids):
                visit(task_id)

            return v

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}") from e

class CompensatoryAction(BaseModel):
    """
    Define una acción física para revertir un cambio.
    [Metacognición: Eliminación de Rama C]
    """
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]

class SagaStep(BaseModel):
    task_id: str
    status: str = "PENDING"  # PENDING, DONE, FAILED, COMPENSATED, AMBIGUITY_RESOLVED
    rollback_action: Optional[CompensatoryAction] = None
    semantic_audit: bool = False # Flag para forzar resolve_ambiguity

class SagaTransaction(BaseModel):
    """
    Registro de estado industrial para el patrón Saga.
    """
    transaction_id: str
    context_token: str # Token único para aislamiento de contexto (L2-Sync)
    steps: List[SagaStep] = Field(default_factory=list)
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
