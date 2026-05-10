import sys
from pathlib import Path

import pyarrow as pa

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_ipc import KuzuQueryResultProxy


def test_kuzu_query_result_proxy_reads_typed_arrow_rows():
    table = pa.table(
        {
            "ok": [True, False],
            "count": [1, 2],
            "ratio": [1.5, 2.25],
            "name": ["a", "b"],
        }
    )
    proxy = KuzuQueryResultProxy(table)

    assert proxy.get_column_names() == ["ok", "count", "ratio", "name"]
    assert proxy.has_next() is True
    assert proxy.get_next() == [True, 1, 1.5, "a"]
    assert proxy.get_next() == [False, 2, 2.25, "b"]
    assert proxy.has_next() is False


def test_kuzu_query_result_proxy_reset_iterator():
    proxy = KuzuQueryResultProxy(pa.table({"x": [10, 20]}))
    assert proxy.get_next() == [10]
    proxy.reset_iterator()
    assert proxy.get_next() == [10]
