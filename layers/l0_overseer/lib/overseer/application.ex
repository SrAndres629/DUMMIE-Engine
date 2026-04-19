defmodule Overseer.Application do
  use Application

  @impl true
  def start(_type, _args) do
    IO.puts("=== L0_OVERSEER: Árbitro Ejecutivo (Sustrato Elixir/OTP) Iniciado ===")

    # Configuración de NATS (Gnat - Spec 03)
    gnat_opts = %{
      host: "127.0.0.1",
      port: 4222
    }

    children = [
      # 1. Conector NATS (Gnat)
      %{
        id: Gnat,
        start: {Gnat, :start_link, [gnat_opts, [name: :gnat]]}
      },
      # 2. Monitor de Salud Causal (L1-L6) - Árbitro Ejecutivo
      {Overseer.HealthMonitor, []}
    ]

    # Estrategia One For One: Si el Gnat falla, se reinicia solo.
    # Si el Monitor falla, se reinicia con el estado anterior.
    opts = [strategy: :one_for_one, name: Overseer.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

defmodule Overseer.HealthMonitor do
  @moduledoc """
  Árbitro Ejecutivo (L0) - Implementa las políticas de supervivencia,
  apoptosis adaptativa y dilación temporal según Spec 05.
  """
  use GenServer
  alias DUMMIE Engine.V2.EventId

  @base_timeout 15_000 # 15 segundos para Alpha (Spec 05)
  @topic_heartbeat "core.v2.life.heartbeat"
  @topic_veto "agent.veto.lifecycle"

  # API
  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  # Callbacks
  @impl true
  def init(_) do
    IO.puts("[L0] Monitor de Salud: Activado. Suscribiendo a Telemetría Sistémica...")
    
    # Iniciar el ciclo de check de apoptosis
    Process.send_after(self(), :check_apoptosis, 5_000)

    # Suscribirse al tópico de latidos sistémicos
    case Gnat.sub(:gnat, self(), @topic_heartbeat) do
      {:ok, _sub} -> 
        IO.puts("[L0] Suscrito a: #{@topic_heartbeat}")
        {:ok, %{last_pulse: System.system_time(:millisecond), load_factor: 0.0, last_tick: 0}}
      {:error, reason} -> 
        IO.puts("[L0] Error al suscribir a NATS: #{inspect(reason)}")
        {:ok, %{last_pulse: System.system_time(:millisecond), load_factor: 0.0, last_tick: 0}}
    end
  end

  @impl true
  def handle_info({:msg, %{body: body, topic: _topic}}, state) do
    # Decodificar EventId de Protobuf (Spec 10)
    case EventId.decode(body) do
      %EventId{lamport_tick: tick} = event ->
        new_pulse = System.system_time(:millisecond)
        if tick > state.last_tick do
          IO.puts("[L0] Latido validado: Tick #{tick} de Universe #{event.universe_id}")
          {:noreply, %{state | last_pulse: new_pulse, last_tick: tick}}
        else
          IO.puts("[L0] !!! ADVERTENCIA: Latido fuera de orden o duplicado (Tick #{tick}) !!!")
          {:noreply, state}
        end
      _ ->
        IO.puts("[L0] !!! ERROR: Error al decodificar latido Protobuf !!!")
        {:noreply, state}
    end
  end

  # Check de Apoptosis (Spec 05)
  @impl true
  def handle_info(:check_apoptosis, state) do
    now = System.system_time(:millisecond)
    diff = now - state.last_pulse
    
    # Tiempo Dilatado (Spec 05): Timeout = Base * (1 + load_factor)
    dynamic_timeout = @base_timeout * (1 + state.load_factor)

    if diff > dynamic_timeout do
      IO.puts("[L0] !!! EVENTO DE NECROSIS DETECTADO (Silence: #{diff}ms) !!!")
      IO.puts("[L0] Iniciando Apoptosis Adaptativa para L1...")
      
      # Publicar VETO en NATS (Spec 03)
      Gnat.pub(:gnat, @topic_veto, "KILL_L1_INACTIVE_TIMEOUT")
      
      # Nota: En una implementación física, L0 podría ejecutar `kill` sobre el PID de L1
      # si L1 fue spawn-eado por L0. Por ahora, confiamos en el Control Plane.
    end

    Process.send_after(self(), :check_apoptosis, 5_000)
    {:noreply, state}
  end
end
