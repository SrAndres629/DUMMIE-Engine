import os
import logging
from typing import Any, List, Optional
import pyarrow as pa
import pyarrow.flight as flight

logger = logging.getLogger("dummie-mcp.memory-ipc")

class MemoryPlaneError(Exception):
    """Excepción base para errores del plano de memoria."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

class KuzuQueryResultProxy:
    def __init__(self, table: pa.Table):
        self._table = table
        self._cursor = 0
        self._columns = list(table.column_names)
        self._num_rows = table.num_rows

    def has_next(self) -> bool:
        return self._cursor < self._num_rows

    def get_next(self) -> List[Any]:
        if not self.has_next():
            raise StopIteration
        idx = self._cursor
        self._cursor += 1
        return [self._table.column(col)[idx].as_py() for col in self._columns]

    def get_column_names(self) -> List[str]:
        return self._columns

    def reset_iterator(self):
        self._cursor = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_next()

class KuzuConnectionProxy:
    def __init__(self, client: flight.FlightClient, location: str):
        self.client = client
        self.location = location

    def execute(self, cypher: str) -> KuzuQueryResultProxy:
        try:
            ticket = flight.Ticket(cypher.encode())
            reader = self.client.do_get(ticket)
            table = reader.read_all()
            return KuzuQueryResultProxy(table)
        except flight.FlightError as e:
            # Propagación de error estructurado (Phase 3/5)
            error_msg = str(e)
            if "not found" in error_msg.lower():
                code = "ERR_NOT_FOUND"
            elif "syntax" in error_msg.lower():
                code = "ERR_CYPHER_SYNTAX"
            else:
                code = "ERR_BACKEND_FAILURE"
            
            logger.error(f"Memory Plane Execution Error: {code} - {error_msg}")
            raise MemoryPlaneError(code, error_msg)
        except Exception as e:
            logger.critical(f"Critical IPC Failure: {str(e)}")
            raise MemoryPlaneError("ERR_IPC_DISCONNECT", str(e))

class ArrowMemoryBridge:
    def __init__(self, socket_path: Optional[str] = None):
        if not socket_path:
            aiwg = os.environ.get("DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.getcwd() + "/.aiwg"))
            socket_path = os.environ.get('MEMORY_SOCKET_PATH', os.path.join(aiwg, "sockets/flight.sock"))
        
        self.socket_path = socket_path
        # Reemplazar espacios por %20 para evitar el error de parseo en Arrow/gRPC
        safe_socket_path = socket_path.replace(" ", "%20")
        self.location = f"grpc+unix://{safe_socket_path}"
        self.client: Optional[flight.FlightClient] = None

    def heartbeat(self) -> bool:
        try:
            temp_client = flight.connect(self.location)
            ticket = flight.Ticket(b"RETURN 1")
            temp_client.do_get(ticket)
            self.client = temp_client
            return True
        except Exception:
            return False

    @property
    def ipc(self) -> KuzuConnectionProxy:
        if not self.client:
            try:
                self.client = flight.connect(self.location)
            except Exception as e:
                raise MemoryPlaneError("ERR_CONNECTION_REFUSED", f"No se pudo conectar al socket {self.location}")
        return KuzuConnectionProxy(self.client, self.location)

    def close(self):
        self.client = None
