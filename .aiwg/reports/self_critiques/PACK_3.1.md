# Pack Self-Critique — Pack 3.1: Hybrid Reranker

This document contains a truthful audit and self-critique of the original Pack 3.1 plan, ensuring complete operational truth, zero overpromising, and rigorous software engineering.

---

## 1. Truthful Audit & Technical Questions

### Q1: ¿El plan original usa `degraded=False` de forma demasiado optimista?
Sí. El plan original establecía `degraded=False` simplemente si la query y los candidatos estaban en el espacio vectorial `text_fast_bge_small_384`. Esto es engañoso porque, aunque la entrada semántica (embeddings) sea real y local, el motor de reordenamiento (`HybridReranker`) sigue siendo un algoritmo híbrido determinista heurístico y no un modelo de reordenamiento de Machine Learning (como un Cross-Encoder) real corriendo offline.

### Q2: ¿Existe realmente un reranker ML offline?
No. No hay ningún modelo de Machine Learning de reordenamiento (Cross-Encoder o Colbert) descargado ni activo localmente. Toda la lógica del reordenador es determinista.

### Q3: ¿Qué significa `degraded` en `RerankResponse`?
Representa la degradación global del pipeline de reranking. Se define formalmente como:
`degraded = semantic_input_degraded or reranker_engine_degraded`
- `semantic_input_degraded` es `True` si la query o los candidatos usan fallbacks o espacios incompatibles.
- `reranker_engine_degraded` es `True` porque el motor de reordenamiento es determinista híbrido en lugar de un modelo ML real.

### Q4: ¿Los pesos suman exactamente 1.0?
Sí. La fórmula del score utiliza:
- `vector_similarity`: 0.35
- `token_overlap`: 0.30
- `path_overlap`: 0.15
- `contextual_boost`: 0.10
- `recency_freshness`: 0.05
- `importance_truth_rank`: 0.05
Suma: `0.35 + 0.30 + 0.15 + 0.10 + 0.05 + 0.05 = 1.0`.

### Q5: ¿Qué pasa si faltan fechas, truth_rank, paths o vectores?
El sistema no lanzará excepciones (no crash). Cada componente que falte se evaluará con un score de `0.0` y se registrará en el objeto de diagnóstico del candidato.

### Q6: ¿Qué pasa si query y candidato usan vector_spaces incompatibles?
El score de `vector_similarity` se establece en `0.0`, y la bandera `semantic_input_degraded` se marca como `True`.

### Q7: ¿Qué pasa si hay NaN, None, timezone inválido o metadata corrupta?
Se capturan todos los fallos mediante excepciones específicas y se devuelven scores por defecto de `0.0`. Se prohíbe estrictamente el retorno de `NaN` o `inf`. Se normalizan los husos horarios convirtiendo marcas temporales Naive a UTC de forma segura.

### Q8: ¿Cómo se revierte o bypassa el reranker?
Se puede activar el bypass estableciendo la variable de entorno `DUMMIE_RERANK_BYPASS=1` o pasando un parámetro al constructor. En este modo, los candidatos se ordenan de forma pura por `raw vector_similarity`, y `ranking_mode` cambia a `bypass_vector_similarity`.

### Q9: ¿Qué test prueba que el ranking cambia por freshness?
El test `test_freshness_changes_ranking` compara candidatos idénticos excepto por sus marcas temporales `freshness_ts` (uno de hace 2 días y otro de hace 45 días), validando que el más fresco sube en el ranking.

### Q10: ¿Qué test prueba que el ranking cambia por truth_rank?
El test `test_truth_rank_changes_ranking` evalúa candidatos con distintos valores numéricos o cadenas de `truth_rank`, certificando la modulación del score final y el reordenamiento subsiguiente.

---

## 2. Plan Corrections & Debt Acknowledgment

- **Corrección**: Se separa conceptualmente la degradación de entrada (`semantic_input_degraded`) de la del motor (`reranker_engine_degraded`). Esto evita falsas declaraciones de éxito.
- **Deuda Técnica**:
  - No existe un motor ML de reordenamiento real offline. El reordenador sigue siendo un reordenador híbrido determinista.
  - La mayoría de las capacidades de embeddings de alta fidelidad, código y multimodales continúan operando bajo fallbacks deterministas de SHA-256 en esta fase.
