# Sustainable Code Program v1

## Objective
Mantener velocidad sin degradar mantenibilidad ni seguridad estructural.

## Non-Negotiable Rules
- Cada bugfix agrega o actualiza test de regresión.
- Sin hardcoded paths absolutos en runtime productivo.
- Sin imports que violen fronteras de capas.
- Cambios de arquitectura siempre con evidencia de verificación.
- No eliminar datos persistentes sin backup + validación.

## Required Gates
- `make verify-specs`
- `make verify-architecture`
- `make verify-industrial`

## Pull Request Minimum
- Problema y causa raíz descritos.
- Evidencia de tests ejecutados.
- Riesgos y rollback explícitos.
- Diff acotado al objetivo.

## Repository Hygiene
- Artefactos runtime a cuarentena no destructiva (`trash/YYYY-MM-DD/manifest.csv`).
- `.venv`, `_build`, `deps`, `node_modules`, caches fuera de cambios lógicos.
- Reportes de auditoría en `state/audits/` y `.aiwg/reports/`.

## Review Cadence
- Semanal: salud de gates y deuda nueva.
- Mensual: cierre de deuda abierta por severidad.
- Trimestral: revisión de arquitectura y actualización de estándares.
