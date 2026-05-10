# Skill Network: Master + Subskills

Este directorio define una capa de orquestación modular para cualquier agente:

- `master_*.yaml`: habilidades maestras orientadas a objetivo.
- `subskill_taxonomy.yaml`: taxonomía reusable para mapear objetivos a capacidades.

La carga recursiva y el planificador jerárquico viven en `layers/l2_brain/skill_binder.py`.
