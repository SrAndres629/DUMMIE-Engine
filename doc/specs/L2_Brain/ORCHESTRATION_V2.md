# DE-V2-L2-ORCH-01: Orchestration Gateway & Daemon V2

## 1. Abstract
Esta especificación define el motor de orquestación de segunda generación para el **DUMMIE Brain (L2)**. Introduce la separación de responsabilidades entre la ingesta de intenciones (Gateway) y el despacho asíncrono resiliente (Daemon), utilizando una arquitectura basada en contratos JSON/XML y el patrón Saga para la gestión de transacciones.

## 2. Protocolo de Ingesta (MAS Gateway)
El Gateway actúa como la frontera del cerebro, validando todas las peticiones externas.

### 2.1. Formato GatewayRequest (JSON)
```json
{
  "session_id": "uuid",
  "goal": "Descripción del objetivo",
  "dag_xml": "<dag>...</dag>",
  "priority": 1
}
```

### 2.2. Definición del DAG (XML Strict AST)
Se utiliza XML para anclar la jerarquía de tareas y evitar alucinaciones en la generación de planes.
```xml
<dag>
  <task id="T1" agent="sw.impl.clean">
    <intent>Implementar módulo X</intent>
    <arguments>{"file": "src/x.py"}</arguments>
  </task>
  <task id="T2" agent="sw.synth.behavior">
    <depends_on>T1</depends_on>
    <intent>Generar tests para X</intent>
  </task>
</dag>
```

## 3. Orchestration Daemon
El Daemon es el motor de ejecución asíncrono encargado de consumir el Ledger y despachar tareas al MCP Gateway (L1).

### 3.1. Patrón Saga y Rollback
Cada tarea (`task`) en el DAG debe ser reversible. Si una tarea falla:
1. El Daemon detiene la ejecución del DAG.
2. Abre el **Circuit Breaker** para el agente afectado.
3. Ejecuta las **CompensatoryActions** en orden inverso (LIFO).

## 4. Seguridad e Integridad
- **Atomicidad Física:** Uso de `fcntl.flock` para garantizar que solo un Daemon escriba en el Ledger a la vez.
- **Fail-Fast (Skill Binding):** Validación asíncrona de capacidades MCP contra perfiles YAML antes de aceptar cualquier DAG.
