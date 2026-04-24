import pyarrow.flight as flight
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("dummie-mcp.memory-ipc")

class KuzuQueryResultProxy:
    """
    Proxy que emula kuzu.QueryResult de la SDK oficial.
    Permite que el código existente que espera objetos de Kuzu funcione con Arrow Flight.
    """
    def __init__(self, json_rows: List[str]):
        self._data = [json.loads(row) for row in json_rows]
        self._cursor = 0
        self._columns = list(self._data[0].keys()) if self._data else []

    def has_next(self) -> bool:
        return self._cursor < len(self._data)

    def get_next(self) -> List[Any]:
        """Retorna la siguiente fila como una lista de valores (estilo Kùzu)."""
        if not self.has_next():
            raise RuntimeError("No more rows in query result")
        row_dict = self._data[self._cursor]
        self._cursor += 1
        return [row_dict[col] for col in self._columns]

    def get_column_names(self) -> List[str]:
        return self._columns

    def reset_iterator(self):
        self._cursor = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.has_next():
            return self.get_next()
        raise StopIteration

class KuzuConnectionProxy:
    """Proxy que emula kuzu.Connection."""
    def __init__(self, client: flight.FlightClient, location: str):
        self.client = client
        self.location = location

    def execute(self, cypher: str) -> KuzuQueryResultProxy:
        """Ejecuta una consulta Cypher y retorna un proxy de resultado."""
        try:
            ticket = flight.Ticket(cypher.encode())
            reader = self.client.do_get(ticket)
            table = reader.read_all()
            
            json_rows = []
            for batch in table.to_batches():
                # El servidor Go envía JSON en la única columna 'data'
                for val in batch.column(0):
                    json_rows.append(str(val))
            
            return KuzuQueryResultProxy(json_rows)
        except Exception as e:
            logger.error(f"Error en consulta IPC: {str(e)}")
            return KuzuQueryResultProxy([])

class ArrowMemoryBridge:
    """
    Clase de compatibilidad que finge ser una kuzu.Database.
    Utiliza pato-typing para integrarse en el bootstrap sin romper la SDK oficial.
    """
    def __init__(self, socket_path: str = "/tmp/dummie_memory.sock"):
        self.socket_path = socket_path
        self.location = f"grpc+unix://{socket_path}"
        self.client: Optional[flight.FlightClient] = None
        self._connected = False

    def heartbeat(self) -> bool:
        """
        Verifica si el Memory Plane está realmente activo realizando un 'ping' de bajo nivel.
        Resuelve el problema de los 'Sockets Zombi' en Linux.
        """
        try:
            # Re-intentamos conexión si es necesario
            temp_client = flight.connect(self.location)
            # Intentamos una operación mínima (RETURN 1)
            ticket = flight.Ticket(b"RETURN 1")
            temp_client.do_get(ticket)
            
            self.client = temp_client
            self._connected = True
            return True
        except Exception as e:
            logger.debug(f"Heartbeat failed for {self.location}: {str(e)}")
            self._connected = False
            self.client = None
            return False

    @property
    def ipc(self) -> KuzuConnectionProxy:
        """
        Retorna un proxy de conexión. El KuzuRepository detecta esta propiedad
        para entrar en modo SPEC-30.
        """
        if not self.client:
            self.client = flight.connect(self.location)
        return KuzuConnectionProxy(self.client, self.location)

    def close(self):
        """Mock de cierre de base de datos."""
        self.client = None
        self._connected = False
