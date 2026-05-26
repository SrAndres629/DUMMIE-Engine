# Spec: DE-V2-L2-200
from typing import Optional
from layers.l2_brain.domain.capability_registry import (
    CapabilityRegistry,
    ModelCapability,
    ModelExpertise,
)
from layers.l2_brain.domain.fabrication.models import IntentType


class ModelRouterV2:
    """
    Service to route tasks to the best available model based on intent.
    Spec: DE-V2-L2-106
    """

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def route_intent(self, intent_type: IntentType) -> Optional[ModelCapability]:
        expertise_map = {
            IntentType.READ_FILE: ModelExpertise.GENERAL,
            IntentType.WRITE_FILE: ModelExpertise.CODING,
            IntentType.EXECUTE_COMMAND: ModelExpertise.CODING,
            IntentType.MUTATION: ModelExpertise.REASONING,
            IntentType.RESOLUTION: ModelExpertise.REASONING,
        }

        expertise = expertise_map.get(intent_type, ModelExpertise.GENERAL)
        return self.registry.get_best_model_for(expertise)
