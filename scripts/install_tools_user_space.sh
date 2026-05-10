#!/bin/bash
# DUMMIE Engine - User-Space Toolchain Installer
# Based on ADR-0014

set -e

LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

echo "=== [USER-SPACE] Installing Sovereign Toolchain ==="

# 1. uv (Python)
if ! command -v uv >/dev/null 2>&1; then
    echo ">> Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "[✓] uv already installed"
fi

# 2. Go (L1)
if ! command -v go >/dev/null 2>&1; then
    echo ">> Installing Go 1.23.2 locally..."
    GO_VERSION="1.23.2"
    curl -LO "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
    mkdir -p "$HOME/lib"
    tar -C "$HOME/lib" -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
    ln -sf "$HOME/lib/go/bin/go" "$LOCAL_BIN/go"
    ln -sf "$HOME/lib/go/bin/gofmt" "$LOCAL_BIN/gofmt"
    rm "go${GO_VERSION}.linux-amd64.tar.gz"
else
    echo "[✓] Go already installed"
fi

# 3. Zig (L4)
if ! command -v zig >/dev/null 2>&1; then
    echo ">> Installing Zig 0.11.0 locally..."
    ZIG_VER="0.11.0"
    curl -O "https://ziglang.org/download/${ZIG_VER}/zig-linux-x86_64-${ZIG_VER}.tar.xz"
    tar -xf "zig-linux-x86_64-${ZIG_VER}.tar.xz"
    mv "zig-linux-x86_64-${ZIG_VER}" "$HOME/lib/zig"
    ln -sf "$HOME/lib/zig/zig" "$LOCAL_BIN/zig"
    rm "zig-linux-x86_64-${ZIG_VER}.tar.xz"
else
    echo "[✓] Zig already installed"
fi

# 4. Rust (L3)
if ! command -v cargo >/dev/null 2>&1; then
    echo ">> Installing Rust via rustup (User-Space)..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
    ln -sf "$HOME/.cargo/bin/cargo" "$LOCAL_BIN/cargo"
    ln -sf "$HOME/.cargo/bin/rustc" "$LOCAL_BIN/rustc"
else
    echo "[✓] Rust already installed"
fi

# 5. Protobuf Compiler (protoc)
if ! command -v protoc >/dev/null 2>&1; then
    echo ">> Installing protoc 28.2 locally..."
    PROTOC_VER="28.2"
    curl -LO "https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VER}/protoc-${PROTOC_VER}-linux-x86_64.zip"
    unzip -o "protoc-${PROTOC_VER}-linux-x86_64.zip" -d "$HOME/.local"
    rm "protoc-${PROTOC_VER}-linux-x86_64.zip"
else
    echo "[✓] protoc already installed"
fi

# 6. Go Plugins for Protobuf
if command -v go >/dev/null 2>&1; then
    echo ">> Installing Go Protobuf plugins..."
    export GOPATH="$HOME/go"
    export PATH="$GOPATH/bin:$PATH"
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
    ln -sf "$GOPATH/bin/protoc-gen-go" "$LOCAL_BIN/protoc-gen-go"
    ln -sf "$GOPATH/bin/protoc-gen-go-grpc" "$LOCAL_BIN/protoc-gen-go-grpc"
fi

echo "---"
echo ">> INSTALACIÓN COMPLETADA <<"
echo "IMPORTANTE: Asegúrate de añadir estas líneas a tu ~/.bashrc o ~/.zshrc:"
echo "export PATH=\"\$HOME/.local/bin:\$HOME/go/bin:\$PATH\""
echo "export GOPATH=\"\$HOME/go\""
echo "---"
