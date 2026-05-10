import os
import json
from datetime import datetime
from typing import List, Optional
from brain.domain.governance.models import OntologicalMap, LayerCertainty

class OntologicalMapAdapter:
    """
    Adaptador para el Mapa Ontológico (Spec 42).
    Persiste la certeza de las capas en .aiwg/ontological_map.json.
    """
    def __init__(self, map_path: str = ".aiwg/ontological_map.json"):
        self.map_path = map_path
        map_dir = os.path.dirname(self.map_path)
        if map_dir:
            os.makedirs(map_dir, exist_ok=True)

    def save_map(self, ont_map: OntologicalMap) -> None:
        """Persiste el mapa completo."""
        try:
            with open(self.map_path, "w", encoding="utf-8") as f:
                f.write(ont_map.model_dump_json(indent=2))
        except Exception as e:
            print(f"[OntologicalMapAdapter] Error al guardar mapa: {e}")

    def load_map(self) -> OntologicalMap:
        """Carga el mapa desde el disco."""
        if not os.path.exists(self.map_path):
            return OntologicalMap(layers={}, updated_at=datetime.now())
            
        try:
            with open(self.map_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return OntologicalMap(**data)
        except Exception as e:
            print(f"[OntologicalMapAdapter] Error al cargar mapa: {e}")
            return OntologicalMap(layers={}, updated_at=datetime.now())

    def update_layer(self, layer_certainty: LayerCertainty) -> None:
        """Actualiza o añade una capa al mapa."""
        ont_map = self.load_map()
        
        # Actualización atómica en el dict
        ont_map.layers[layer_certainty.layer_name] = layer_certainty
            
        ont_map.updated_at = datetime.now()
        self.save_map(ont_map)
