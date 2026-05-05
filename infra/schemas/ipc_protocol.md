# Especificación del Protocolo IPC: Elixir <-> Go (Port)

## 1. Transporte y Ciclo de Vida
*   **Mecanismo:** Erlang Ports (`Port.open({spawn_executable, path}, [:binary, :stream, :use_stdio])`).
*   **Flujos:** 
    *   **Elixir -> Go:** STDIN del proceso Go.
    *   **Go -> Elixir:** STDOUT del proceso Go.
*   **Control de Vida:** 
    *   Go debe terminar inmediatamente si detecta `EOF` en STDIN (indicando que Elixir cerró el puerto o crasheó).
    *   Elixir supervisa el proceso OS. Si Go termina con código distinto de 0, se aplica estrategia de reinicio.

## 2. Formato de Datos
*   **Protocolo:** JSON por Línea (NDJSON - *Newline Delimited JSON*).
*   **Codificación:** UTF-8.
*   **Separador:** `\n` (Newline).

## 3. Esquema de Mensajes

### 3.1 Petición (Elixir -> Go)
```json
{
  "id": "uuid-v4-string",
  "command": "string",
  "args": {}
}
```

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | String | Identificador único para correlación. |
| `command` | String | Acción a ejecutar (e.g., `ping`, `eval`, `shutdown`). |
| `args` | Object | Parámetros específicos del comando. |

### 3.2 Respuesta (Go -> Elixir)
```json
{
  "id": "uuid-v4-string",
  "status": "ok | error",
  "payload": {}
}
```

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | String | Debe coincidir con el `id` de la petición. |
| `status` | String | Resultado de la operación. |
| `payload` | Object | Datos de retorno o mensaje de error en caso de fallo (`{"error": "motivo"}`). |

## 4. Comandos Iniciales

### `ping`
*   **Propósito:** Verificar conectividad.
*   **Args:** `{}`
*   **Payload (ok):** `{"pong": true}`

### `shutdown`
*   **Propósito:** Cierre ordenado.
*   **Args:** `{}`
*   **Payload (ok):** `{"status": "stopping"}`
