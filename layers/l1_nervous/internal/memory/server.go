package memory

import (
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
	"github.com/nats-io/nats.go"
)

type inferredKind int

const (
	kindUnknown inferredKind = iota
	kindBool
	kindInt64
	kindFloat64
	kindString
)

// DummieMemoryServer implementa la interfaz Flight para KuzuDB
type DummieMemoryServer struct {
	flight.BaseFlightServer
	db   *kuzu.Database
	conn *kuzu.Connection
	nc   *nats.Conn
}

func NewDummieMemoryServer(dbPath string, nc *nats.Conn) (*DummieMemoryServer, error) {
	log.Printf("[L1-MEMORY] Step 1: Opening KuzuDB (Native creation)...")
	config := kuzu.DefaultSystemConfig()
	
	// Intento de apertura con aislamiento
	db, err := kuzu.OpenDatabase(dbPath, config)
	if err != nil {
		log.Printf("[L1-MEMORY] CRITICAL: Kuzu OpenDatabase failed: %v", err)
		return nil, err
	}
	
	log.Printf("[L1-MEMORY] Step 3: Establishing internal connection...")
	conn, err := kuzu.OpenConnection(db)
	if err != nil {
		db.Close()
		return nil, err
	}
	
	log.Printf("[L1-MEMORY] SUCCESS: KuzuDB initialized and isolated.")
	return &DummieMemoryServer{db: db, conn: conn, nc: nc}, nil
}

func publishInfraError(nc *nats.Conn, code, message string) {
	if nc == nil {
		return
	}
	payload := fmt.Sprintf(`{"code": "%s", "message": "%s", "layer": "L1_NERVOUS", "component": "MEMORY_PLANE"}`, code, message)
	nc.Publish("core.v2.nervous.infra.error", []byte(payload))
}

func (s *DummieMemoryServer) DoGet(tkt *flight.Ticket, stream flight.FlightService_DoGetServer) error {
	query := string(tkt.GetTicket())
	log.Printf("[L1-MEMORY] Exec Cypher (Typed): %s", query)

	result, err := s.conn.Query(query)
	if err != nil {
		publishInfraError(s.nc, "QUERY_EXECUTION_FAILED", err.Error())
		return err
	}
	defer result.Close()

	columnNames := result.GetColumnNames()
	rows := make([][]any, 0)

	for result.HasNext() {
		row, err := result.Next()
		if err != nil {
			log.Printf("[L1-MEMORY] Row Fetch Error: %v", err)
			break
		}

		values := make([]any, len(columnNames))
		for i := range columnNames {
			v, vErr := row.GetValue(uint64(i))
			if vErr != nil {
				v = nil
			}
			values[i] = v
		}
		rows = append(rows, values)
		row.Close()
	}

	pool := memory.NewGoAllocator()
	schema := buildArrowSchema(columnNames, rows)
	arrays, err := buildArrowArrays(pool, schema, rows)
	if err != nil {
		return err
	}
	defer releaseArrays(arrays)

	record := array.NewRecord(schema, arrays, int64(len(rows)))
	defer record.Release()

	writer := flight.NewRecordWriter(stream, ipc.WithSchema(schema))
	defer writer.Close()
	return writer.Write(record)
}

func buildArrowSchema(columnNames []string, rows [][]any) *arrow.Schema {
	fields := make([]arrow.Field, 0, len(columnNames))
	for idx, name := range columnNames {
		fields = append(fields, arrow.Field{
			Name:     name,
			Type:     inferArrowType(rows, idx),
			Nullable: true,
		})
	}
	return arrow.NewSchema(fields, nil)
}

func inferArrowType(rows [][]any, colIdx int) arrow.DataType {
	kind := kindUnknown
	for _, row := range rows {
		if colIdx >= len(row) {
			continue
		}
		v := row[colIdx]
		if v == nil {
			continue
		}
		kind = mergeKind(kind, kindOf(v))
		if kind == kindString {
			break
		}
	}

	switch kind {
	case kindBool:
		return arrow.FixedWidthTypes.Boolean
	case kindInt64:
		return arrow.PrimitiveTypes.Int64
	case kindFloat64:
		return arrow.PrimitiveTypes.Float64
	default:
		return arrow.BinaryTypes.String
	}
}

func kindOf(v any) inferredKind {
	switch v.(type) {
	case bool:
		return kindBool
	case int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
		return kindInt64
	case float32, float64:
		return kindFloat64
	default:
		return kindString
	}
}

func mergeKind(current, next inferredKind) inferredKind {
	if current == kindUnknown {
		return next
	}
	if current == next {
		return current
	}
	if (current == kindInt64 && next == kindFloat64) || (current == kindFloat64 && next == kindInt64) {
		return kindFloat64
	}
	return kindString
}

func buildArrowArrays(pool memory.Allocator, schema *arrow.Schema, rows [][]any) ([]arrow.Array, error) {
	builders := make([]array.Builder, len(schema.Fields()))
	for i, field := range schema.Fields() {
		builders[i] = newBuilder(pool, field.Type)
	}
	defer releaseBuilders(builders)

	for _, row := range rows {
		for colIdx, builder := range builders {
			var v any
			if colIdx < len(row) {
				v = row[colIdx]
			}
			appendValue(builder, schema.Field(colIdx).Type, v)
		}
	}

	out := make([]arrow.Array, len(builders))
	for i, b := range builders {
		out[i] = b.NewArray()
	}
	return out, nil
}

func releaseBuilders(builders []array.Builder) {
	for _, b := range builders {
		b.Release()
	}
}

func releaseArrays(arrays []arrow.Array) {
	for _, arr := range arrays {
		arr.Release()
	}
}

func newBuilder(pool memory.Allocator, dt arrow.DataType) array.Builder {
	switch dt.ID() {
	case arrow.BOOL:
		return array.NewBooleanBuilder(pool)
	case arrow.INT64:
		return array.NewInt64Builder(pool)
	case arrow.FLOAT64:
		return array.NewFloat64Builder(pool)
	default:
		return array.NewStringBuilder(pool)
	}
}

func appendValue(builder array.Builder, dt arrow.DataType, v any) {
	if v == nil {
		builder.AppendNull()
		return
	}

	switch dt.ID() {
	case arrow.BOOL:
		val, ok := v.(bool)
		if !ok {
			builder.AppendNull()
			return
		}
		builder.(*array.BooleanBuilder).Append(val)
	case arrow.INT64:
		val, ok := toInt64(v)
		if !ok {
			builder.AppendNull()
			return
		}
		builder.(*array.Int64Builder).Append(val)
	case arrow.FLOAT64:
		val, ok := toFloat64(v)
		if !ok {
			builder.AppendNull()
			return
		}
		builder.(*array.Float64Builder).Append(val)
	default:
		builder.(*array.StringBuilder).Append(fmt.Sprint(v))
	}
}

func toInt64(v any) (int64, bool) {
	switch t := v.(type) {
	case int: return int64(t), true
	case int8: return int64(t), true
	case int16: return int64(t), true
	case int32: return int64(t), true
	case int64: return t, true
	case uint: return int64(t), true
	case uint8: return int64(t), true
	case uint16: return int64(t), true
	case uint32: return int64(t), true
	case uint64: return int64(t), true
	default: return 0, false
	}
}

func toFloat64(v any) (float64, bool) {
	switch t := v.(type) {
	case float32: return float64(t), true
	case float64: return t, true
	case int: return float64(t), true
	case int8: return float64(t), true
	case int16: return float64(t), true
	case int32: return float64(t), true
	case int64: return float64(t), true
	case uint: return float64(t), true
	case uint8: return float64(t), true
	case uint16: return float64(t), true
	case uint32: return float64(t), true
	case uint64: return float64(t), true
	default: return 0, false
	}
}

func StartFlightServerWithInstance(server *DummieMemoryServer, socketPath string, natsURL string) error {
	if _, err := os.Stat(socketPath); err == nil {
		os.Remove(socketPath)
	}

	// Reconectar NATS si fue pasado como nil durante la pre-inicialización
	if server.nc == nil {
		nc, _ := nats.Connect(natsURL)
		server.nc = nc
	}

	lis, err := net.Listen("unix", socketPath)
	if err != nil {
		return err
	}

	fs := flight.NewFlightServer()
	fs.RegisterFlightService(server)

	fmt.Printf("[L1-MEMORY] Memory Plane Data Plane (TYPED) activo en unix://%s\n", socketPath)
	fs.InitListener(lis)
	return fs.Serve()
}

func StartFlightServer(dbPath, socketPath string, natsURL string) error {
	if err := ResolveStaleLocks(dbPath); err != nil {
		log.Printf("[L1-MEMORY] Fencing Error: %v", err)
	}

	nc, _ := nats.Connect(natsURL)
	server, err := NewDummieMemoryServer(dbPath, nc)
	if err != nil {
		if nc != nil { nc.Close() }
		return err
	}

	return StartFlightServerWithInstance(server, socketPath, natsURL)
}
