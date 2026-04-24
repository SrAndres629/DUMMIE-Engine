# SPEC-26: LANGGRAPH QUANTUM SWARM TOPOLOGY

## 1. Visión General
El **Quantum Swarm** es el motor de ejecución asíncrono que sustituye la orquestación secuencial por grafos de estados cíclicos y paralelos. Go actúa como el runtime determinista que gestiona el ciclo de vida de los nodos probabilísticos (LLMs).

## 2. Topología del Grafo
El flujo se define como un grafo dirigido donde cada nodo es una instancia de un agente con un prompt y un rol específico.

### Nodos Base:
- **PlannerNode**: Analiza la tarea y decide el grado de multiplicidad (fan-out).
- **CoderNode [Parallel]**: Implementa soluciones en `Shadow Worktrees`. Se instancian múltiples variantes (Aggressive, Conservative, Experimental).
- **ReviewerNode**: Evalúa la salida de un CoderNode mediante linters y tests unitarios.
- **MergeNode**: Selecciona la rama ganadora y realiza el commit final en el branch `main`.

## 3. Mecanismo de Multiplicidad
El orquestador en Go lanza `N` hilos de ejecución concurrentes.
- Cada hilo tiene su propio **Floating Session State (FSS)**.
- El éxito se define por el paso de la suite de tests (Determinismo).
- Si múltiples ramas pasan los tests, se prioriza por métricas de `Clean Code` (Complejidad Ciclomática, DRY).

## 4. Contratos de Comunicación (Internal)
Los nodos se comunican mediante **Channels** en Go, transportando el objeto `State` tipado.
