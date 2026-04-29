"""
[T4] Tests de regresión para TopologicalAuditor.
Verifica que:
- Grafos acíclicos pasan
- Grafos cíclicos son detectados
- Self-loops son detectados
- La palabra "cycle" en texto NO causa falso positivo
- Input no-XML es rechazado explícitamente
- DAG vacío (sin edges) pasa
- Input vacío es rechazado
"""
import sys
from pathlib import Path

import pytest

# Asegurar que L3 y L2 (para auditor_port) estén en path
_L3 = Path(__file__).resolve().parents[1]
_L2 = _L3.parent / "l2_brain"
for p in [str(_L3), str(_L2)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from topological_auditor import TopologicalAuditor


@pytest.fixture
def auditor():
    return TopologicalAuditor()


# --- Acyclic graphs ---

@pytest.mark.asyncio
async def test_acyclic_linear_graph(auditor):
    """A→B→C sin ciclo → TOPOLOGY_VALIDATED_DAG"""
    dag = (
        '<dag>'
        '<edge source="A" target="B"/>'
        '<edge source="B" target="C"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag, "test acyclic")
    assert ok is True
    assert "TOPOLOGY_VALIDATED_DAG" in msg


@pytest.mark.asyncio
async def test_acyclic_diamond_graph(auditor):
    """A→B, A→C, B→D, C→D (diamond) sin ciclo"""
    dag = (
        '<dag>'
        '<edge source="A" target="B"/>'
        '<edge source="A" target="C"/>'
        '<edge source="B" target="D"/>'
        '<edge source="C" target="D"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag)
    assert ok is True


@pytest.mark.asyncio
async def test_empty_dag_no_edges(auditor):
    """DAG sin edges → válido (no hay ciclos posibles)"""
    dag = '<dag></dag>'
    ok, msg = await auditor.audit(dag)
    assert ok is True
    assert "TOPOLOGY_VALIDATED_DAG" in msg


# --- Cyclic graphs ---

@pytest.mark.asyncio
async def test_simple_cycle_detected(auditor):
    """A→B→C→A debe detectar ciclo"""
    dag = (
        '<dag>'
        '<edge source="A" target="B"/>'
        '<edge source="B" target="C"/>'
        '<edge source="C" target="A"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag, "test cycle")
    assert ok is False
    assert "DETECTION_ANOMALY" in msg
    assert "Cycle detected" in msg


@pytest.mark.asyncio
async def test_self_loop_detected(auditor):
    """A→A (self-loop) debe detectar ciclo"""
    dag = (
        '<dag>'
        '<edge source="A" target="A"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag)
    assert ok is False
    assert "DETECTION_ANOMALY" in msg


@pytest.mark.asyncio
async def test_cycle_in_subgraph(auditor):
    """A→B, C→D→E→C — ciclo en subgrafo independiente"""
    dag = (
        '<dag>'
        '<edge source="A" target="B"/>'
        '<edge source="C" target="D"/>'
        '<edge source="D" target="E"/>'
        '<edge source="E" target="C"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag)
    assert ok is False
    assert "DETECTION_ANOMALY" in msg


# --- False positive prevention ---

@pytest.mark.asyncio
async def test_word_cycle_in_xml_attribute_no_false_positive(auditor):
    """La palabra 'cycle' en un atributo XML NO debe causar falso positivo"""
    dag = (
        '<dag description="lifecycle dependency graph">'
        '<edge source="lifecycle" target="deploy"/>'
        '<edge source="deploy" target="monitor"/>'
        '</dag>'
    )
    ok, msg = await auditor.audit(dag)
    assert ok is True, f"False positive: word 'cycle' in attribute caused rejection: {msg}"
    assert "TOPOLOGY_VALIDATED_DAG" in msg


# --- Invalid input handling ---

@pytest.mark.asyncio
async def test_non_xml_input_rejected(auditor):
    """Input no-XML debe ser rechazado con error claro, no con fallback textual"""
    ok, msg = await auditor.audit("this is not xml at all")
    assert ok is False
    assert "AUDIT_ERROR" in msg
    assert "Invalid DAG format" in msg


@pytest.mark.asyncio
async def test_text_with_word_cycle_not_used_as_detection(auditor):
    """
    Input textual que contiene la palabra 'cycle' NO debe usar
    fallback textual. El fallback fue eliminado.
    """
    ok, msg = await auditor.audit("there is a cycle in this text")
    assert ok is False
    # Debe rechazar por formato inválido, NO por detección textual
    assert "AUDIT_ERROR" in msg
    assert "Invalid DAG format" in msg


@pytest.mark.asyncio
async def test_empty_input_rejected(auditor):
    """Input vacío debe ser rechazado"""
    ok, msg = await auditor.audit("")
    assert ok is False
    assert "AUDIT_ERROR" in msg


@pytest.mark.asyncio
async def test_whitespace_only_input_rejected(auditor):
    """Input solo whitespace debe ser rechazado"""
    ok, msg = await auditor.audit("   \n\t  ")
    assert ok is False
    assert "AUDIT_ERROR" in msg


@pytest.mark.asyncio
async def test_malformed_xml_rejected(auditor):
    """XML malformado debe dar error de parse, no crash"""
    ok, msg = await auditor.audit("<dag><edge source='A'")
    assert ok is False
    assert "AUDIT_ERROR" in msg
