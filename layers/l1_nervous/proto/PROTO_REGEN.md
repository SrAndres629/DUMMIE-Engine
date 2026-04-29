# Protocol Buffer Regeneration Guide

## Generated Files

The following files in this directory are **auto-generated** from `.proto` source files.
**DO NOT edit them manually.** They will be overwritten on the next regeneration.

### Files:
- `memory.pb.go` — Generated from `dummie/v2/memory.proto`
- `../memory.pb.go` — Generated from root-level `memory.proto`
- `../orchestration.pb.go` / `../orchestration_grpc.pb.go` — Generated from `orchestration.proto`
- `../core.pb.go` — Generated from `core.proto`

## Regeneration Command

```bash
# From the DUMMIE Engine root directory:
# Ensure protoc and protoc-gen-go are installed

# For v2 memory proto:
protoc \
  --proto_path=proto/ \
  --go_out=layers/l1_nervous/proto/ \
  --go_opt=paths=source_relative \
  proto/dummie/v2/memory.proto

# For root-level protos:
protoc \
  --proto_path=proto/ \
  --go_out=layers/l1_nervous/proto/ \
  --go_opt=paths=source_relative \
  --go-grpc_out=layers/l1_nervous/proto/ \
  --go-grpc_opt=paths=source_relative \
  proto/memory.proto proto/orchestration.proto proto/core.proto
```

## Prerequisites

- `protoc` >= 3.21 (Protocol Buffer Compiler)
- `protoc-gen-go` >= 1.28 (`go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`)
- `protoc-gen-go-grpc` >= 1.2 (`go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest`)

## Policy

Per SDD contract, generated `.pb.go` files **are committed to the repository** to ensure
the build doesn't require protoc to be installed on every developer's machine.
If the `.proto` source changes, regenerate and commit the updated `.pb.go` files.
