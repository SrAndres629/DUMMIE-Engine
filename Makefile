# Makefile - DUMMIE Engine Sovereign Orquestration
# Based on Spec 08 - One-Click Deployment

.PHONY: all proto-gen build-l0 build-l1 build-l2 build-l3 build-l4 clean factory-reset

LOCAL_BIN = $(HOME)/.local/bin
export PATH := $(LOCAL_BIN):$(HOME)/go/bin:$(PATH)

PROTO_DIR = proto/dummie/v2
GO_PROTO_OUT = layers/l1_nervous/proto
EX_PROTO_OUT = layers/l0_overseer/lib/proto
PY_PROTO_OUT = layers/l2_brain/proto

all: proto-gen build-l4 build-l3 build-l1 build-l0 build-l2

# 1. Generación de Stubs (Spec 10)
proto-gen:
	@echo "=== Generando Stubs de Protobuf (Ley de Schema-First) ==="
	@mkdir -p $(GO_PROTO_OUT) $(EX_PROTO_OUT) $(PY_PROTO_OUT)
	# Go (L1)
	protoc --proto_path=. \
		--go_out=layers/l1_nervous --go_opt=module=io.dummie.v2/nervous \
		--go-grpc_out=layers/l1_nervous --go-grpc_opt=module=io.dummie.v2/nervous \
		$(PROTO_DIR)/*.proto
	# Elixir (L0)
	protoc --proto_path=. \
		--elixir_out=$(EX_PROTO_OUT) \
		$(PROTO_DIR)/*.proto
	# Python (L2)
	cd layers/l2_brain && uv run python -m grpc_tools.protoc --proto_path=../.. \
		--python_out=proto \
		--grpc_python_out=proto \
		../../$(PROTO_DIR)/*.proto
	@echo "[✓] Stubs generados."

# 2. Capa L0 - Overseer (Elixir)
build-l0:
	@echo "=== Compilando Layer 0: Overseer (Elixir) ==="
	cd layers/l0_overseer && \
		mix local.hex --force && \
		mix local.rebar --force && \
		mix deps.get && \
		mix compile
	@echo "[✓] L0 compilado."
	@echo "=== Compilando Memory Plane (Go) ==="
	mkdir -p /tmp/dummie_kuzu && \
	ln -sf "$(shell pwd)/shared/lib/kuzu/"* /tmp/dummie_kuzu/ && \
	export CGO_ENABLED=1 && \
	export CGO_CFLAGS="-I/tmp/dummie_kuzu" && \
	export CGO_LDFLAGS="-L/tmp/dummie_kuzu -lkuzu -Wl,-rpath,/tmp/dummie_kuzu" && \
	cd layers/l0_overseer && go build -o ../../bin/memory_server ./cmd/memory/main.go
	@echo "[✓] Memory Plane compilado."

# 3. Capa L1 - Nervous (Go)
build-l1:
	@echo "=== Compilando Layer 1: Nervous (Go) ==="
	cd layers/l1_nervous && go build -o ../../bin/l1_nervous .
	@echo "[✓] L1 compilado."

# 4. Capa L2 - Brain (Python)
build-l2:
	@echo "=== Configurando Layer 2: Brain (Python/UV) ==="
	cd layers/l2_brain && uv sync
	@echo "[✓] L2 configurado."

# 5. Capa L3 - Shield (Rust)
build-l3:
	@echo "=== Compilando Layer 3: Shield (Rust/PyO3) ==="
	cd layers/l3_shield && cargo build --release
	@echo "[✓] L3 compilado."

# 6. Capa L4 - Edge (Zig)
build-l4:
	@echo "=== Compilando Layer 4: Edge (Zig/LST Scanner) ==="
	cd layers/l4_edge && zig build -Doptimize=ReleaseSafe
	@echo "[✓] L4 compilado."

# 7. Readiness Check (SDD Compliance)
ready:
	@echo "=== Verificando Integridad de la Fábrica (SDD) ==="
	@python3 doc/04_forge/sdd_validator.py
	@echo "=== Verificando Registro de Engranajes ==="
	@cat shared/gear_registry.json | jq .version
	@echo "[✓] DUMMIE Engine listo para operaciones."

factory-reset: clean all

clean:
	rm -rf bin/*
	rm -rf layers/l1_nervous/proto/*.pb.go
	rm -rf layers/l0_overseer/lib/proto/*
	rm -rf layers/l2_brain/proto/*.py
	cd layers/l1_nervous && go clean
	cd layers/l3_shield && cargo clean
	cd layers/l4_edge && rm -rf zig-out/ zig-cache/
	cd layers/l0_overseer && mix clean
