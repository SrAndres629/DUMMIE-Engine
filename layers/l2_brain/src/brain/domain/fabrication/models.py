from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum

from brain.domain.context.models import AuthorityLevel, IntentType as ContextIntent

class IntentType(str, Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    CREATE_AGENT = "create_agent"
    MUTATION = "mutation"
    RESOLUTION = "resolution" # Fixed for Spec 21/42 crystallization

class AgentIntent(BaseModel):
    """
    Intención del Agente en el Software Fabrication Engine (Spec 21)
    """
    intent_type: IntentType
    target: str
    rationale: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    locus_x: str = "sw.plant.orchestrator" # Default for Spec 21
    intent_i: ContextIntent = ContextIntent.OBSERVATION # Default for Spec 21
    authority_a: AuthorityLevel = AuthorityLevel.AGENT # Default for Spec 21
    
class SkillDefinition(BaseModel):
    """
    Estándar de Habilidad YAML (Spec 28)
    """
    skill_name: str
    version: str
    parameters: Dict[str, str]

class DesignStation(BaseModel):
    """
    Flujo de Trabajo de la Estación de Diseño (Spec 29)
    """
    station_id: str
    active_blueprint: str
    assigned_skills: List[SkillDefinition]

class AgentPresenceHeartbeat(BaseModel):
    """
    Protocolo de Descubrimiento A2A (Spec 37)
    """
    agent_id: str
    expertise_tags: List[str]
    current_load: float = Field(..., ge=0.0, le=1.0)
    authority_level: str
    status: str = "AVAILABLE"
