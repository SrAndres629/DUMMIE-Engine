# L3 Shield

## Purpose
Capa de validación previa a ejecución: controles estructurales, económicos y de cumplimiento.

## Current State
- Auditores Python disponibles:
- `topological_auditor.py`
- `budget_auditor.py`
- `compliance_auditor.py`
- Biblioteca Rust `shield` con validación base de intent.

## Key Gaps
1. Reglas de auditoría mayormente placeholder.
2. Integración parcial entre validadores Python y módulo Rust.

## Next Actions
1. Definir reglas mínimas ejecutables por auditor.
2. Añadir tests de veto por escenario.
3. Documentar contrato de entrada/salida único de auditoría.
