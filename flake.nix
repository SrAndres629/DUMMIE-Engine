{
  description = "DUMMIE Engine - Virtual Collective Architecture (VCA)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # L0 - Elixir/Arbiter
            elixir
            erlang
            
            # L1 - Nervous (Go)
            go
            nats-server
            
            # L2 - Brain (Python)
            (python3.withPackages (ps: with ps; [
              pydantic
              pyyaml
              requests
            ]))
            
            # L3 - Shield (Rust)
            rustc
            cargo
            rust-analyzer
            
            # L4 - Edge (Zig)
            zig
            
            # L5 - Muscle (Mojo - Requires modular-cli via external or just python interop)
            # Nota: Mojo normalmente requiere una instalación manual via 'modular'
            
            # Infraestructura y Contratos
            protobuf
            protoc-gen-go
            protoc-gen-go-grpc
            apache-kv-store # Placeholder para el data plane
            
            # Herramientas de Calidad
            ripgrep
            gnumake
          ];

          shellHook = ''
            echo "=== DUMMIE Engine: Entorno Soberano Activado ==="
            echo "L0: Elixir | L1: Go | L3: Rust | L4: Zig | L5: Mojo-Interop"
            echo "Gobernanza SDD V3 vigente."
          '';
        };
      }
    );
}
