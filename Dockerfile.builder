# DUMMIE Engine - Multilingual Builder Environment
# Based on Spec 08 & Spec 11

FROM debian:bookworm-slim AS builder

# 1. Instalar dependencias base y herramientas políglotas
RUN apt-get update && apt-get install -y \
    curl git build-essential unzip wget \
    # Elixir/Erlang (L0)
    elixir erlang-dev \
    # Python (L2)
    python3 python3-pip \
    # Protobuf (Contracts)
    protobuf-compiler \
    # Utils
    ripgrep gnupg \
    && rm -rf /var/lib/apt/lists/*

# 1.1. Instalar Apache Arrow nativo
RUN curl -LsSf https://apache.jfrog.io/artifactory/arrow/debian/apache-arrow-apt-source-latest-bookworm.deb -o apache-arrow-apt-source-latest.deb \
    && apt-get update && apt-get install -y ./apache-arrow-apt-source-latest.deb \
    && apt-get update && apt-get install -y libarrow-dev libarrow-glib-dev \
    && rm apache-arrow-apt-source-latest.deb

# 1.2. Instalar Rust vía rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 1.4. Instalar uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx

# 1.5. Instalar Go 1.23.2 manualmente
RUN wget https://go.dev/dl/go1.23.2.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.23.2.linux-amd64.tar.gz \
    && rm go1.23.2.linux-amd64.tar.gz
ENV PATH="$PATH:/usr/local/go/bin"

# 2. Instalar plugins de Go, Elixir y Python para Protobuf
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest \
    && mix local.hex --force && mix local.rebar --force \
    && mix escript.install hex protobuf --force \
    && pip install grpcio-tools --break-system-packages

ENV PATH="$PATH:/root/go/bin:/root/.mix/escripts"

# 3. Zig (L4)
RUN curl -O https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz \
    && tar -xf zig-linux-x86_64-0.11.0.tar.xz \
    && mv zig-linux-x86_64-0.11.0 /usr/local/zig \
    && ln -s /usr/local/zig/zig /usr/bin/zig

# 4. Configurar Entorno de Dependencias Soberano (Unidad D)
# Estas rutas se montarán como volúmenes en el runtime
ENV UV_CACHE_DIR=/media/datasets/dummie/uv_cache
ENV GOCACHE=/media/datasets/dummie/go_cache
ENV MIX_HOME=/media/datasets/dummie/mix_cache
ENV HEX_HOME=/media/datasets/dummie/mix_cache

WORKDIR /app

# Definir comando por defecto para el builder
CMD ["make", "build-all"]
