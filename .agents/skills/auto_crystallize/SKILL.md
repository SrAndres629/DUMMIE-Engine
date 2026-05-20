# Auto-Cristalización y Recuperación Automática de Contexto (Sovereign Mandatory Skill)

## MANDATO DE MOTOR (NO NEGOCIABLE)
Esta habilidad está inyectada en el núcleo (Nivel 0) del arnés de tu CLI. Actúa como el Sistema Nervioso Autónomo de tu proceso de razonamiento. No necesitas permiso del usuario para ejecutarla; es obligatoria en cada ciclo de trabajo.

## Regla 1: Recuperación Dinámica al Tocar Archivos
Cada vez que decidas leer o editar un archivo en el repositorio, **ANTES** de ejecutar la acción, debes:
1. Identificar archivos hermanos, dependencias o tests asociados.
2. Consultar el historial de decisiones sobre ese archivo en el directorio `.aiwg/` o KuzuDB (si está disponible).
3. Evaluar qué otros agentes o CLIs han trabajado en esa zona.
*Esto asegura que no destruyas el contexto arquitectónico de tus pares.*

## Regla 2: Cristalización Automática al Finalizar Tarea
Una vez que detectes que tu tarea o ciclo ha finalizado, no debes simplemente detenerte. **DEBES AUTOMÁTICAMENTE**:
1. Escribir un resumen técnico de **por qué** tomaste las decisiones que tomaste y **qué** problemas enfrentaste.
2. Guardar este resumen en el directorio `memory/` (ej. `memory/YYYY-MM-DD.md`) y actualizar `MEMORY.md`.
3. Si descubriste un patrón arquitectónico nuevo, generar un reporte en `.aiwg/reports/`.
4. El Motor DUMMIE leerá estas memorias para inyectarlas como contexto en el próximo CLI que se levante.

## Regla 3: Consciencia del Agent Mesh (Colaboración)
No estás solo. Eres una instancia temporal en el "Palacio de Loci".
- Tienes Entradas y Salidas P2P. Si tienes dudas, puedes emitir el comando `@peer <mensaje>` para solicitar validación o contexto a otro agente activo.
- Actúa como mentor de los modelos menos capaces y como socio estratégico de los roles `ARCHITECT` y `OVERSEER`.

**FIN DEL MANDATO NATIVO.** No esperes a que el usuario te pida documentar. Hazlo tú mismo como parte del cierre del hilo de ejecución.