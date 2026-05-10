# ANTIGRAVITY_POLICY - Control de Ejecución Autónoma

## Propósito
Definir los límites de autonomía y seguridad para el agente Antigravity/Gemini CLI operando sobre el worktree de DUMMIE Engine.

## Agente
- Antigravity / Gemini CLI Agent.

## Acciones Permitidas
- Lectura exhaustiva de archivos.
- Creación de artefactos en `.aiwg/`.
- Edición quirúrgica de archivos existentes con validación TDD.
- Ejecución de scripts de auditoría y tests.

## Acciones Prohibidas
- Push o Merge autónomo.
- Borrado de archivos sin respaldo.
- Modificación de `.git/` o `.env` (sin autorización explícita).

## Validación
- Todo cambio debe ser seguido de una prueba de integridad (make verify o equivalente).
- Uso obligatorio de `EpistemicJudge` para validar afirmaciones de éxito.
