from typing import Generator
from . import sdk_core_api_pb2 as pb2

class Session:
    def __init__(self, client):
        self.client = client
        self.session_id = "session_" + str(id(self))
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def execute(self, goal: str) -> pb2.IntentResponse:
        req = pb2.IntentRequest(session_id=self.session_id, goal=goal)
        return self.client.stub.ExecuteIntent(req)
        
    def stream_logs(self) -> Generator[pb2.AgentEvent, None, None]:
        req = pb2.SessionRequest(session_id=self.session_id)
        return self.client.stub.StreamEvents(req)
