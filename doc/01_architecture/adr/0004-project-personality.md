---
spec_id: "DE-V2-[ADR-004](0004-project-personality.md)"
title: "Identidad Cognitiva y Personalidad de Proyecto"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "EXTENDS"
  - id: "DE-V2-L4-18"
    relationship: "USES"
tags: ["architectural_decision", "cognitive_identity", "industrial_sdd"]
---

# [ADR-004](0004-project-personality.md): Identidad Cognitiva y Personalidad de Proyecto

## Abstract
En la fabricación de software artesanal, el sistema hereda el estilo y los sesgos del operador individual. Esta decisión establece que la identidad técnica debe residir en el proyecto mismo, definida por una "Personalidad" basada en grafos que rige los hiperparámetros de razonamiento de los agentes.

## 1. Cognitive Context Model (JSON)
```json
{
  "trait_matrix": {
    "refactoring_aggressiveness": "0.0 - 1.0",
    "abstraction_level": "0.0 - 1.0",
    "security_strictness": "0.0 - 1.0",
    "biases": [
      "performance",
      "test_coverage"
    ]
  },
  "mechanisms": [
    "Graph-based Personality",
    "GraphRAG Decision Memory"
  ],
  "capsules": [
    "Exploratory",
    "Mission Critical"
  ],
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Contexto
En la fabricación artesanal, el software hereda las inconsistencias de la intervención humana directa. En una **Autonomous Software Factory (ASF)**, la identidad técnica reside en el núcleo inmutable del proyecto. La "Personalidad" es el conjunto de restricciones, estilos y jurisprudencia técnica que define el comportamiento autónomo del ecosistema.

---

## 3. Decisión: Personalidad Topográfica (Graph-based Personality)
Se establece que la identidad de un proyecto es una **Propiedad Estructural** del Palacio de Loci (Grafo L4). La personalidad deja de ser un prompt estático para convertirse en un conjunto de nodos y relaciones que condicionan la navegación semántica.

### 3.1 Nodos de Gobernanza (KùzuDB)
Cada rasgo de personalidad definido en `.aiwg/personality/profile.json` se instancia como un nodo:
- `PersonalityTrait`: Nodos que emiten campos de fuerza de "Mood" sobre los directorios de código.
- `SovereignDecision`: Nodos que actúan como hitos inamovibles en la cronología del proyecto.

### 3.2 Inyección de Contexto por Capas (Mood Injection)
1. **L0 (Sovereignty):** El Overseer carga los hiperparámetros.
2. **L4 (Memory):** El Grafo aplica pesos dinámicos a las aristas según el Mood (ej: en un proyecto de "Seguridad Máxima", los nodos de red tienen mayor impedancia de acceso).
3. **L2 (Inference):** Los agentes perciben el mundo a través del filtro topográfico, haciendo que los anti-patrones sean "difíciles de ver" o "explícitamente prohibidos" en el espacio semántico.

---

---

## 4. Implementación de "Cápsulas de Proyecto"
- **Proyecto Exploratorio:** Mood ágil, `refactoring_aggressiveness` bajo, `security_strictness` equilibrado.
- **Proyecto Misión Crítica:** Mood conservador, `security_strictness` máximo, arquitectura hexagonal obligatoria.

---

## 5. Consecuencias
- **Positivas:** Eliminación de la erosión arquitectónica; los agentes "cambian de chip" instantáneamente al cambiar de contexto.
- **Negativas:** Requiere una fase inicial de "Ajuste de Tono" (Tuning) para cada proyecto nuevo.
