package memory

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"

	"github.com/apache/arrow/go/v17/arrow"
	"github.com/apache/arrow/go/v17/arrow/array"
	"github.com/apache/arrow/go/v17/arrow/flight"
	"github.com/apache/arrow/go/v17/arrow/ipc"
	"github.com/apache/arrow/go/v17/arrow/memory"
	"github.com/kuzudb/go-kuzu"
)

// DummieMemoryServer implementa la interfaz Flight para KuzuDB
type DummieMemoryServer struct {
	flight.BaseFlightServer
	db   *kuzu.Database
	conn *kuzu.Connection
}

func NewDummieMemoryServer(dbPath string) (*DummieMemoryServer, error) {
	// Usamos OpenDatabase y OpenConnection en v0.11.x
	db, err := kuzu.OpenDatabase(dbPath, kuzu.DefaultSystemConfig())
	if err != nil {
		return nil, err
	}
	conn, err := kuzu.OpenConnection(db)
	if err != nil {
		return nil, err
	}
	return &DummieMemoryServer{db: db, conn: conn}, nil
}

func (s *DummieMemoryServer) DoGet(tkt *flight.Ticket, stream flight.FlightService_DoGetServer) error {
	query := string(tkt.GetTicket())
	log.Printf("[MEMORY-IPC] Ejecutando Cypher: %s", query)

	result, err := s.conn.Query(query)
	if err != nil {
		log.Printf("[MEMORY-IPC] Error en consulta: %v", err)
		return err
	}
	defer result.Close()

	pool := memory.NewGoAllocator()
	schema := arrow.NewSchema(
		[]arrow.Field{
			{Name: "data", Type: arrow.BinaryTypes.String},
		},
		nil,
	)

	b := array.NewStringBuilder(pool)
	defer b.Release()

	for result.HasNext() {
		row, err := result.Next()
		if err != nil {
			log.Printf("[MEMORY-IPC] Error al recuperar fila: %v", err)
			break
		}
		
		// GetAsMap() es el método más directo en v0.11.x
		rowData, err := row.GetAsMap()
		if err != nil {
			log.Printf("[MEMORY-IPC] Error al convertir fila a mapa: %v", err)
			continue
		}

		jsonData, err := json.Marshal(rowData)
		if err != nil {
			log.Printf("[MEMORY-IPC] Error al serializar JSON: %v", err)
			continue
		}
		b.Append(string(jsonData))
	}

	arr := b.NewArray()
	defer arr.Release()
	record := array.NewRecord(schema, []arrow.Array{arr}, int64(arr.Len()))
	defer record.Release()

	writer := flight.NewRecordWriter(stream, ipc.WithSchema(schema))
	defer writer.Close()
	return writer.Write(record)
}

func StartFlightServer(dbPath, socketPath string) error {
	// Limpieza previa del socket
	if _, err := os.Stat(socketPath); err == nil {
		os.Remove(socketPath)
	}
	
	// Crear listener Unix para gRPC
	lis, err := net.Listen("unix", socketPath)
	if err != nil {
		return fmt.Errorf("fallo al crear listener unix: %v", err)
	}

	server, err := NewDummieMemoryServer(dbPath)
	if err != nil {
		return err
	}

	fs := flight.NewFlightServer()
	fs.RegisterFlightService(server)

	fmt.Printf("[L0-MEMORY] Sirviendo Memoria Compartida en unix://%s\n", socketPath)
	fs.InitListener(lis)
	return fs.Serve()
}
