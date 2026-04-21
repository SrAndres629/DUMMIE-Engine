---
spec_id: "DE-V2-GOV-02"
title: "System Design Blueprint (Modelos C4)"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.concepts"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-001](../adr/0001-polyglot-architecture.md)"
    relationship: "REPRESENTS"
tags: ["governance", "system_design", "c4_model", "industrial_sdd"]
---

# System Design Blueprint (Modelos C4)

## Abstract
Este documento modela visualmente cómo interactúan e intercambian flujos las capas estructurales de DUMMIE Engine, usando nomenclatura C4. Proporciona una visión holística de la topología del sistema, los contenedores por capa y los contratos de comunicación inter-capa (NATS, Arrow, gRPC).

## 1. Cognitive Context Model (Ref)
Para la definición de niveles de diagramación, tecnologías de transporte y mapeo estratigráfico, consulte el archivo hermano [c4_model_graphs.rules.json](./c4_model_graphs.rules.json).

---

## 2. Nivel 1: Contexto de Sistema

```mermaid
C4Context
    title Diagrama de Contexto de Sistema para DUMMIE Engine
    
    Person(dev, "Desarrollador / Agente Humano", "Interactúa operativamente con el sistema")
    System(agentic_os, "Agentic OS (DUMMIE Engine)", "Orquestador IA Multi-Agente Políglota de extrema seguridad")
    System_Ext(llm_api, "APIs Cloud LLMs", "GPT-5, Claude (Inteligencia Externa)")
    System_Ext(local_ai, "Local AI Substrate", "Llama.cpp, MLX (Inferencia costo-cero)")
    
    Rel(dev, agentic_os, "Gestiona e imparte intenciones vía Dashboard")
    Rel(agentic_os, llm_api, "Pide inferencias usando PydanticAI (Schemas)", "HTTPS/REST")
    Rel(agentic_os, local_ai, "Tareas triviales costo-cero", "FFI directo")
```

---

## 3. Nivel 2: Diagrama de Contenedores

```mermaid
C4Container
    title Diagrama de Contenedores de Arquitectura Políglota (7 Capas)
    
    Container_Boundary(c1, "Agentic OS") {
        Container(c_ui, "Dashboard UI", "Tauri + Bun + TS + Mastra", "Skin (L6): Streaming visual CoT en tiempo real.")
        
        Container(c_go, "NATS / Traffic Manager", "Go + Redb", "Nervous System (L1): Enruta todo tráfico IPC. Event Store en Redb.")
        
        Container(c_py, "Core de Inferencia", "Python + Swarm + PydanticAI", "Brain (L2): Genera intenciones atómicas via Consenso.")
        
        Container(c_rust, "Sandbox & Execution Shield", "Rust + WASM + PyO3", "Shield (L3): Testea y ejecuta código sin contaminar host.")
        
        Container(c_elixir, "Supervisor Nodes", "Elixir + OTP + Nx", "Overseer (L0): Gestión de vida, Apoptosis y Arbitraje.")
        
        Container(c_zig, "LST Scanner & Loci Mapper", "Zig + Zap", "Edge (L4): Ingesta LST hiper-rápida. Mapeo Ontológico.")
        
        ContainerDb(db_memory, "MemPalace / GraphRAG", "KùzuDB + Redb", "Dual-Store: Redb para Eventos y KùzuDB para Grafos.")
        
        Container(c_mojo, "SIMD Data Processor", "Mojo", "Muscle (L5): Preprocesa tensores masivos. Semantic GC.")
    }
    
    Rel(c_ui, c_go, "Se subscribe a telemetría", "WebSockets")
    Rel(c_go, c_py, "Despacha Eventos y recibe Requests", "NATS/gRPC")
    Rel(c_py, c_rust, "Pide simulaciones seguras", "PyO3 (Zero-cost bindings)")
    Rel(c_rust, c_go, "Notifica éxito/falla para MicroSagas", "NATS")
    Rel(c_py, db_memory, "Consulta nodos vecinos (GraphRAG)", "Arrow Zero-Copy")
    Rel(c_zig, db_memory, "Alimenta topología LST/Loci", "Arrow Zero-Copy")
    Rel(c_elixir, c_py, "Vigila salud de proceso (OTP)")
    Rel(c_elixir, c_go, "Vigila salud de colas (OTP)")
    Rel(c_elixir, c_rust, "Vigila sandbox (Apoptosis)")
    Rel(c_go, c_zig, "Delega scanning LST", "IPC")
    Rel(c_mojo, c_py, "Entrega tensores preprocesados", "Arrow Zero-Copy")
```

---

## 4. Nivel 3: Flujo de Datos Inter-Capa (Protocolos)

```mermaid
graph LR
    subgraph "Contratos (Build Time)"
        PROTO[".proto Schemas"]
    end
    
    subgraph "Transporte In-Memory (Runtime)"
        ARROW["Apache Arrow<br/>Zero-Copy Bus"]
    end
    
    subgraph "Comunicación de Red (IPC)"
        NATS["NATS JetStream"]
        GRPC["gRPC"]
    end
    
    PROTO -->|"Valida tipos"| ARROW
    PROTO -->|"Genera stubs"| GRPC
    ARROW -->|"Go ↔ Rust ↔ Python ↔ Zig"| MEM["Shared Memory<br/>(Kernel Linux)"]
    NATS -->|"L0 ↔ L1 ↔ L3"| NET["Red local"]
    GRPC -->|"L1 ↔ L2"| NET
```

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [c4_model_graphs.feature](./c4_model_graphs.feature)
- **Machine Rules:** [c4_model_graphs.rules.json](./c4_model_graphs.rules.json)
