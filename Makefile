# Makefile - DUMMIE Engine Sovereign Orquestration
# Based on Spec 08 - One-Click Deployment

.PHONY: all proto-gen build-l1 build-l0 clean

PROTO_DIR = proto/dummie/v2
GO_PROTO_OUT = layers/l1_nervous/proto
EX_PROTO_OUT = layers/l0_overseer/lib/proto
PY_PROTO_OUT = layers/l2_brain/proto

all: proto-gen build-l1 build-l0

# 1. Generación de Stubs (Spec 10)
proto-gen:
	@echo "=== Generando Stubs de Protobuf (Ley de Schema-First) ==="
	@mkdir -p $(GO_PROTO_OUT) $(EX_PROTO_OUT) $(PY_PROTO_OUT)
	# Go (L1)
	protoc --proto_path=. \
		--go_out=. --go_opt=module=io.dummie.v2/nervous \
		--go-grpc_out=. --go-grpc_opt=module=io.dummie.v2/nervous \
		$(PROTO_DIR)/*.proto
	mv proto/dummie/v2/*.pb.go $(GO_PROTO_OUT)/ 2>/dev/null || true
	# Elixir (L0)
	protoc --proto_path=. \
		--elixir_out=$(EX_PROTO_OUT) \
		$(PROTO_DIR)/*.proto
	# Python (L2)
	python3 -m grpc_tools.protoc --proto_path=. \
		--python_out=$(PY_PROTO_OUT) \
		--grpc_python_out=$(PY_PROTO_OUT) \
		$(PROTO_DIR)/*.proto
	@echo "[✓] Stubs generados en $(GO_PROTO_OUT), $(EX_PROTO_OUT) y $(PY_PROTO_OUT)"

# 4. Capa L3 - Shield (Rust)
build-l3:
	@echo "=== Compilando Layer 3: Shield (Rust/PyO3) ==="
	cd layers/l3_shield && cargo build --release
	@echo "[✓] L3 compilado"

# 5. Capa L4 - Edge (Zig)
build-l4:
	@echo "=== Compilando Layer 4: Edge (Zig/LST Scanner) ==="
	cd layers/l4_edge && zig build -Doptimize=ReleaseSafe
	@echo "[✓] L4 compilado"

# 6. Capa L2 - Brain (Python Setup)
setup-l2:
	@echo "=== Configurando Layer 2: Brain (Python/UV) ==="
	cd layers/l2_brain && uv sync
	@echo "[✓] L2 configurado"

clean:
	rm -rf bin/ proto/dummie/v2/*.pb.go $(GO_PROTO_OUT)/*.pb.go $(EX_PROTO_OUT)/*.pb.ex $(PY_PROTO_OUT)/*.py
	cd layers/l1_nervous && go clean
	cd layers/l3_shield && cargo clean
	cd layers/l4_edge && rm -rf zig-out/ zig-cache/
