# LOCI DB Runtime Policy v1

## Scope
Aplica a `.aiwg/memory/loci.db` y cualquier artefacto físico de Kùzu asociado.

## Policy
- `.aiwg/memory/loci.db` es estado runtime soberano local.
- No se commitea el binario de DB.
- No se usa el binario de DB como evidencia versionada.

## Evidence Rules
La evidencia de salud/persistencia debe registrarse por:
- hash/metadata (tamaño, mtime, checksum cuando aplique)
- readback verificable (queries de integridad)
- reportes en `.aiwg/reports/` o `state/` según criticidad

## Operational Rules
- No borrar ni recrear DB de forma destructiva sin backup explícito.
- Pruebas deben usar DB temporal/copia, no memoria soberana real.
- Cambios de schema deben pasar por contrato canónico de L2 (`layers/l2_brain/models.py`) y tests de regresión.
