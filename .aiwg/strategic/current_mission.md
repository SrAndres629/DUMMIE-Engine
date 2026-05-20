# Misión Actual: Consolidación Post-Redirector

## Objetivo
Migrar los ~85 módulos restantes de `flat_brain/` a sus órganos canónicos y eliminar la dependencia del `_FlatBrainFallbackFinder`.

## Estado
- **683/684 tests pasando** (1 fallo: KuzuDB no disponible)
- SSoT de AuthorityLevel: COMPLETO (única definición en `domain/authority.py`)
- Redirector eliminado: SÍ
- Imports flat_brain en órganos canónicos: 0 (cero)

## Próximo Obstáculo
`flat_brain/` contiene ~85 módulos que el fallback finder sigue resolviendo. Cada uno debe migrarse a su órgano canónico o eliminarse si es código muerto.

## Lo que aprendí hoy
La causa raíz de la mayoría de regresiones no fue el redirector per se, sino un bug de indentación en `daemon.py`: las importaciones de `GatewayRequest`, `ModelTier`, `BaseAuditor`, `FailClosedAuditor` estaban indentadas dentro del bloque `if __package__ in {None, ""}:`, por lo que no se ejecutaban durante la importación normal del módulo. Esto estuvo oculto durante meses porque el redirector compensaba. Adicionalmente, había un split-class de `DiagnosticReporter` porque el daemon importaba `daemon_diagnostic` (resolvía a `flat_brain/daemon_diagnostic.py`) mientras la versión canónica estaba en `daemon/daemon_diagnostic.py`.

## Próxima Misión
Migración masiva de flat_brain a órganos canónicos. Priorizar módulos más importados (según grep de tests). Crear test de escaneo que falle si flat_brain/ contiene módulos que ya existen en destino canónico.
