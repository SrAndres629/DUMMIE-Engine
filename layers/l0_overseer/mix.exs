defmodule Overseer.MixProject do
  use Mix.Project

  def project do
    [
      app: :overseer,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Overseer.Application, []}
    ]
  end

  defp deps do
    [
      {:grpc, "~> 0.7.0"},
      {:protobuf, "~> 0.12.0"},
      {:gnat, "~> 1.6"},      # Cliente NATS para Elixir
      {:jason, "~> 1.4"},     # Parser JSON
      {:nx, "~> 0.7.0"}        # Razonamiento Numérico (L0 Audit)
    ]
  end
end
