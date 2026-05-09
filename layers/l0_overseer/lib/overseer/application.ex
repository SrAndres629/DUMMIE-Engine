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
      {Overseer.HealthMonitor, []},
      # 3. Daemon Go (Port)
      {Overseer.PortManager, []}
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
  alias Dummie.V2.EventId

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
      
      # Autorepuesto (Spec 05 / Jidoka): Relanzar L1
      if state.load_factor < 5.0 do
        IO.puts("[L0] >> Intentando relanzar Sistema Nervioso (L1)...")
        # Nota: Usamos una ruta absoluta o relativa al root del proyecto
        # En una arquitectura industrial, esto lo gestionaría un supervisor de sistema (systemd/docker)
        # pero para soberanía local, L0 toma el mando.
        System.cmd("bash", ["-c", "cd ../.. && ./bin/l1_nervous > l1.log 2>&1 &"])
      end
    end

    Process.send_after(self(), :check_apoptosis, 5_000)
    {:noreply, state}
  end
end

defmodule Overseer.PortManager do
  @moduledoc """
  Gestiona el ciclo de vida y la comunicación IPC (via Erlang Ports)
  con el daemon de Go (dummied).
  """
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def send_command(name \\ __MODULE__, command, args \\ %{}) do
    GenServer.call(name, {:send_command, command, args})
  end

  @impl true
  def init(_opts) do
    IO.puts("[L0] PortManager: Activando supervisión del Daemon Go...")
    Process.flag(:trap_exit, true)
    
    # Preferir el binario canónico del repo y degradar al artefacto local solo por compatibilidad.
    repo_root = System.get_env("DUMMIE_ROOT_DIR") || Path.expand("../../../..", __DIR__)

    bin_path =
      [
        Path.join(repo_root, "bin/dummied"),
        Path.expand("../../dummied", __DIR__)
      ]
      |> Enum.find(&File.exists?/1)
    
    if bin_path do
      IO.puts("[L0] PortManager: Iniciando binario en #{bin_path}")
      port =
        Port.open(
          {:spawn_executable, bin_path},
          [
            :binary,
            :use_stdio,
            {:line, 4096},
            {:env, [{'DUMMIE_PORT_INTERFACE', 'stdio'}]}
          ]
        )
      {:ok, %{port: port, requests: %{}, buffer: ""}}
    else
      IO.puts("[L0] PortManager: ADVERTENCIA - Binario no encontrado. Se requiere compilación.")
      {:ok, %{port: nil, requests: %{}, buffer: ""}}
    end
  end

  @impl true
  def handle_call({:send_command, _command, _args}, _from, %{port: nil} = state) do
    {:reply, {:error, :port_not_active}, state}
  end

  def handle_call({:send_command, command, args}, from, state) do
    id = "req_#{System.unique_integer([:positive])}"
    msg = %{"id" => id, "command" => command, "args" => args}
    payload = Jason.encode!(msg) <> "\n"
    
    Port.command(state.port, payload)
    
    new_requests = Map.put(state.requests, id, from)
    {:noreply, %{state | requests: new_requests}}
  end

  @impl true
  def handle_info({port, {:data, {:eol, line}}}, %{port: port} = state) do
    full_line = state.buffer <> line
    state = %{state | buffer: ""}
    
    case Jason.decode(full_line) do
      {:ok, %{"id" => id, "status" => status, "payload" => payload}} ->
        case Map.pop(state.requests, id) do
          {nil, _} ->
            {:noreply, state}
          {from, new_requests} ->
            GenServer.reply(from, {String.to_atom(status), payload})
            {:noreply, %{state | requests: new_requests}}
        end
      _ ->
        {:noreply, state}
    end
  end

  def handle_info({port, {:data, {:noeol, partial}}}, %{port: port} = state) do
    {:noreply, %{state | buffer: state.buffer <> partial}}
  end

  def handle_info({:EXIT, port, reason}, %{port: port} = state) do
    IO.puts("[L0] PortManager: El proceso Go ha caído: #{inspect(reason)}")
    {:stop, :port_terminated, state}
  end
  
  def handle_info(_msg, state) do
    {:noreply, state}
  end
end
