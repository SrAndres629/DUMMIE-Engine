---
spec_id: "DE-V2-L0-ADR-010"
title: "Bootstrap de Memoria vía L2-Python Bridge"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
---

# [ADR-010](0010-l2-infrastructure-bridge.md): Bootstrap de Memoria

## Contexto
La Capa L4 (Zig) aún no posee los bindings estables de KùzuDB. Sin embargo, el desarrollo del proyecto requiere persistencia causal *ahora* para evitar regresiones de razonamiento y pérdida de contexto histórico durante la construcción.

## Decisión
Se autoriza temporalmente a la Capa L2 (Brain) a instanciar y gestionar el archivo de base de datos `.aiwg/memory/loci.db` utilizando la librería nativa de Python (`kuzu`). 

## Consecuencias
- **Positiva:** Disponibilidad inmediata de memoria avanzada (RAG-DAG) para el Swarm de agentes.
- **Negativa:** Acoplamiento temporal de infraestructura en la capa de cognición (L2).
- **Mitigación:** La implementación en L2 debe seguir un patrón de Repositorio estricto para facilitar la migración futura a L4.
