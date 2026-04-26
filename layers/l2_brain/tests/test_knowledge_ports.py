import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from knowledge_ports import KnowledgeProvider, WisdomPublisher, EntropyGovernor, RehydrationProvider


def test_knowledge_ports_are_runtime_protocols():
    assert getattr(KnowledgeProvider, "_is_protocol", False)
    assert getattr(WisdomPublisher, "_is_protocol", False)
    assert getattr(EntropyGovernor, "_is_protocol", False)
    assert getattr(RehydrationProvider, "_is_protocol", False)
