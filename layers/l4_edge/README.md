# 👁️ L4_Edge: Los Sentidos de Antigravity

## 1. Abstract
La capa L4 es el sistema sensorial del DUMMIE Engine. Su función es descubrir capacidades, analizar la estructura del código y observar cambios en el entorno operativo para informar al Cerebro (L2).

## 2. Divisiones Sensoriales

### 2.1. Discovery (Descubrimiento)
- **Locus:** `edge/discovery/`
- **Función:** Detecta herramientas instaladas, servidores MCP activos y perfiles de agentes disponibles.
- **Impacto:** Alimenta el catálogo del `SkillBinder`.

### 2.2. Scanner (Análisis Estático)
- **Locus:** `edge/scanner/`
- **Función:** Realiza análisis profundo de la topología del lenguaje (**LST**).
- **Mecanismo:** Implementación en Zig para máxima performance en el escaneo de símbolos.

### 2.3. Observers (Monitoreo)
- **Locus:** `edge/observers/`
- **Función:** Vigilancia continua del sistema de archivos.
- **Mecanismo:** Notificaciones reactivas (Inotify/Watchdog) para detectar mutaciones externas.

## 3. Protocolo de Observación
L4 opera bajo el principio de **"Sentir antes de Actuar"**. El cerebro consulta periódicamente a L4 para sincronizar su mapa mental con la realidad física del host.
