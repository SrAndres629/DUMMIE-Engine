# Especificación: Interfaz Python del SDK

## Inicialización
```python
import dummie

client = dummie.Client(endpoint="localhost:50051")
```

## Context Managers (Sesiones)
```python
with client.session() as session:
    response = session.execute("Refactorizar módulo X")
    
    for event in response.stream_logs():
        print(f"[{event.timestamp}] {event.type}: {event.message}")
```

## Consulta al Grafo 4D-TES
```python
nodes = client.memory.query_loci("MATCH (n) RETURN n LIMIT 5")
```
