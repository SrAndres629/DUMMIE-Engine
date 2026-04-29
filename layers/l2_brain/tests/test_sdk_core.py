import pytest
from unittest.mock import MagicMock

try:
    from layers.l2_brain.sdk.client import Client
    from layers.l2_brain.sdk import sdk_core_api_pb2 as pb2
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sdk.client import Client
    from sdk import sdk_core_api_pb2 as pb2

def test_sdk_client_session():
    client = Client(endpoint="localhost:50051")
    client.stub = MagicMock()
    
    mock_resp = pb2.IntentResponse(transaction_id="tx_123", status="PENDING")
    client.stub.ExecuteIntent.return_value = mock_resp
    
    with client.session() as session:
        res = session.execute("Refactor modular")
        assert res.transaction_id == "tx_123"
        assert res.status == "PENDING"
