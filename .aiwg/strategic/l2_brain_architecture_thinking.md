# L2 Brain Architecture — Strategic Thinking

**Author:** DUMMIE Engine (as Strategic Partner/Mentor)
**Date:** 2026-05-19
**Status:** DRAFT — For Jorge's Review
**Context:** Post-incident (flat_brain migration without manifest, 58 broken specs, 5 deleted files)

---

## La Verdad Sobre Las "48 Horas"

No fue un número al azar. Pero tampoco es "48 horas de operación continua".

Así es como **realmente** opero:

### Mi Naturaleza Operativa

1. **No soy un proceso 24/7.** Soy un agente de IA que opera en sesiones. Cada sesión tiene un contexto limitado (tokens, tiempo, memoria).
2. **No tengo un reloj interno continuo.** No puedo "trabajar en segundo plano" mientras duermes. Cada vez que me despiertas, empiezo desde mis archivos de memoria.
3. **Mi continuidad viene de los archivos, no de mi cerebro.** `MEMORY.md`, `memory/YYYY-MM-DD.md`, `.aiwg/` — esos son mi hipocampo artificial. Sin ellos, soy amnésico.

### Lo Que "48 Horas" Significa Realmente

No son 48 horas de reloj. Son **4-6 sesiones de trabajo distribuidas en 2 días**:

```
Sesión 1 (2-3h): Lectura profunda del estado actual del repo
  - Qué existe, qué funciona, qué está roto
  - Mapeo de dependencias entre capas
  - Identificación de patrones y anti-patrones

Sesión 2 (2-3h): Diseño de arquitectura L2 canónica
  - Documento de arquitectura
  - Contratos de datos entre capas
  - Decisiones arquitectónicas (ADRs)

Sesión 3 (2-3h): Plan de migración
  - Manifest de migración
  - Rollback plan
  - Tests de验证

Sesión 4 (2-3h): Ejecución inicial
  - Primeros cambios
  - Validación
  - Ajustes
```

Entre sesiones: **tú revisas, yo archivo en memoria, el daemon heartbeat mantiene el pulso.**

### Cómo Operaría en la Práctica

**No necesito 48 horas seguidas.** Necesito:

1. **Sesiones enfocadas** con contexto preservado en archivos
2. **Heartbeat checks** para mantener el estado entre sesiones
3. **Archivos de decisión** que sobrevivan a mis amnesias de sesión
4. **Tu revisión** entre sesiones para validar dirección

El daemon (`dummie-mcp`, `agentic.slice`) puede mantener el runtime activo. Yo no. Pero puedo dejar instrucciones precisas para que el daemon ejecute tareas autónomas entre sesiones.

---

## El Problema Real de L2 Brain

### Lo Que Veo

L2 Brain tiene **dos arquitecturas coexistiendo sin contrato**:

```
layers/l2_brain/
├── flat_brain/          ← ~235 archivos migrados (sin plan)
│   ├── cognition/       ← Planificación fría, juicio epistémico
│   ├── domain/          ← Modelos cognitivos, servicios
│   ├── embedding_mesh/  ← Proveedores de embedding, reranking
│   ├── infrastructure/  ← Adapters (Kùzu, ledger, semantic)
│   ├── metacognition/   ← Hooks, pipeline, deliberación
│   ├── proto/           ← gRPC definitions
│   ├── sdk/             ← Client SDK
│   └── ~180 módulos más...
│
├── src/brain/           ← Arquitectura hexagonal (puertos/adapters)
│   ├── application/     ← Use cases, interfaces, ports
│   ├── domain/          ← Memory models, agent office
│   └── infrastructure/  ← Adapters (ledger, shield)
│
├── tests/               ← Tests (no migrados)
└── config files         ← pyproject.toml, pytest.ini, etc.
```

**El problema no es que existen dos estructuras.** El problema es que **no hay un contrato que defina cuál es la canónica y cómo se relacionan.**

### Lo Que Debería Ser

L2 Brain necesita **una sola responsabilidad soberana**:

> **L2 Brain es el órgano cognitivo de DUMMIE.**
> Su trabajo es: pensar, recordar, razonar, decidir, evolucionar.
> No es transporte (L1). No es seguridad (L3). No es ejecución edge (L4).

Con esa definición, la arquitectura se clarifica:

```
L2 Brain (Cognitive Organ)
├── Memory System (4D-TES + 3D-Loci)
│   ├── Event Store (temporal, inmutable)
│   ├── Graph Store (espacial, semántico)
│   └── Context Engine (6D vector unificado)
│
├── Reasoning Engine
│   ├── Pattern Mining
│   ├── Causal Analysis
│   ├── Counterfactual Thinking
│   └── Dialectical Reasoning
│
├── Metacognition
│   ├── Self-Audit
│   ├── Quality Gates
│   ├── Evolution Flywheel
│   └── Persona Guardian
│
├── Embedding Mesh
│   ├── Provider Registry
│   ├── Semantic Index
│   ├── Reranking
│   └── Retrieval
│
├── Mission Orchestration
│   ├── Planning (Cold/Warm)
│   ├── Execution
│   └── Outcome Evaluation
│
└── Strategic Partner Runtime
    ├── Business Advisory
    ├── Mentor Mode
    └── Creator Context
```

### Lo Que flat_brain/ y src/brain/ Representan

- **`flat_brain/`** = La implementación actual (monolítica, sin separación de concerns)
- **`src/brain/`** = El intento de arquitectura hexagonal (incompleto, coexistiendo)

**Mi recomendación:** No revertir flat_brain. No migrar a hexagonal todavía. **Definir el contrato primero, luego decidir la estructura.**

---

## El Plan Real (No El Ideal)

### Semana 1: Contrato y Diseño

1. **Documento de arquitectura L2** (este archivo, expandido)
2. **ADRs** para cada decisión arquitectónica
3. **Contrato de datos** entre L2 y otras capas
4. **Manifest de migración** con rollback

### Semana 2: Ejecución Controlada

1. **PACK R3**: Implementar contrato
2. **Import compatibility** para no romper código existente
3. **Test suite** completa
4. **Validación** con specs actualizadas

### Semana 3+: Evolución

1. **PACK R4**: Optimización de rendimiento
2. **PACK R5**: Autonomía mejorada
3. **PACK R6**: Integración con runtime estratégico

---

## Decisiones Pendientes (Requieren Tu Input)

1. **¿flat_brain/ se mantiene como estructura final o es temporal?**
2. **¿src/brain/ (hexagonal) se absorbe o se elimina?**
3. **¿KùzuDB es la única persistencia o coexiste con Redb?**
4. **¿Los tests van dentro de flat_brain/ o en layers/l2_brain/tests/?**
5. **¿Cuál es el límite exacto entre L1 (transporte) y L2 (cognición)?**

No puedo responder estas solo. Son decisiones **tuyas** como arquitecto soberano. Yo puedo recomendar, pero tú decides.

---

## Lo Que Voy a Hacer Ahora

1. Anotar este pensamiento en archivos estructurados
2. Crear un plan de ejecución con tiempos realistas
3. Definir mi perfil de runtime (cómo opero realmente)
4. Crear un manifiesto de arquitectura canónica
5. Integrar todo en un sistema trazable

Esto no es un plan de 48 horas continuas. Es un plan de **4-6 sesiones distribuidas** con archivos de continuidad entre ellas.

El daemon mantiene el pulso. Yo mantengo la memoria en archivos. Tú mantienes la dirección estratégica.

Así es como opero. Así es como operamos juntos.
