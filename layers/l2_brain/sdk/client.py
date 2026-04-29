import grpc
from . import sdk_core_api_pb2 as pb2
from . import sdk_core_api_pb2_grpc as pb2_grpc
from .session import Session

class Client:
    def __init__(self, endpoint: str = "localhost:50051"):
        self.endpoint = endpoint
        self.channel = grpc.insecure_channel(endpoint)
        self.stub = pb2_grpc.DummieOrchestratorStub(self.channel)
        
    def session(self) -> Session:
        return Session(self)
