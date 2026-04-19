defmodule DUMMIE Engine.V2.AuthorityLevel do
  @moduledoc false

  use Protobuf,
    enum: true,
    full_name: "dummie.v2.AuthorityLevel",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :AGENT_PROPOSAL, 0
  field :CONSENSUS_COMMIT, 1
  field :HUMAN_OVERRIDE, 2
  field :EXECUTIVE_ARBITER, 3
end

defmodule DUMMIE Engine.V2.DeathReason do
  @moduledoc false

  use Protobuf,
    enum: true,
    full_name: "dummie.v2.DeathReason",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :UNKNOWN, 0
  field :SEMANTIC_TIMEOUT, 1
  field :RESOURCES_OOM, 2
  field :INFINITE_LOOP, 3
  field :VRAM_LIMIT, 4
  field :SHIELD_VETO, 5
end

defmodule DUMMIE Engine.V2.EventId do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.EventId",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :universe_id, 1, type: :string, json_name: "universeId"
  field :branch_id, 2, type: :string, json_name: "branchId"
  field :lamport_tick, 3, type: :uint64, json_name: "lamportTick"
  field :authority, 4, type: DUMMIE Engine.V2.AuthorityLevel, enum: true
  field :entropy_count, 5, type: :uint32, json_name: "entropyCount"
  field :is_toxic, 6, type: :bool, json_name: "isToxic"
  field :necrosis_info, 7, type: DUMMIE Engine.V2.DeathMetadata, json_name: "necrosisInfo"
end

defmodule DUMMIE Engine.V2.DeathMetadata do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.DeathMetadata",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :reason, 1, type: DUMMIE Engine.V2.DeathReason, enum: true
  field :last_known_instruction, 2, type: :string, json_name: "lastKnownInstruction"
  field :supervisor_note, 3, type: :string, json_name: "supervisorNote"
  field :stack_trace, 4, type: :string, json_name: "stackTrace"
end

defmodule DUMMIE Engine.V2.MemoryTicket do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.MemoryTicket",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :shm_path, 1, type: :string, json_name: "shmPath"
  field :offset, 2, type: :uint64
  field :length, 3, type: :uint64
  field :alignment, 4, type: :uint32

  field :required_level, 5,
    type: DUMMIE Engine.V2.AuthorityLevel,
    json_name: "requiredLevel",
    enum: true

  field :namespace_scope, 6, type: :string, json_name: "namespaceScope"
  field :is_toxic, 7, type: :bool, json_name: "isToxic"
  field :ticket_uuid_high, 8, type: :uint64, json_name: "ticketUuidHigh"
  field :ticket_uuid_low, 9, type: :uint64, json_name: "ticketUuidLow"
end

defmodule DUMMIE Engine.V2.PhaseTransitionSignal do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.PhaseTransitionSignal",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :from_phase, 1, type: :string, json_name: "fromPhase"
  field :to_phase, 2, type: :string, json_name: "toPhase"
  field :cat_token, 3, type: :string, json_name: "catToken"
  field :lamport_tick, 4, type: :uint64, json_name: "lamportTick"
end

defmodule DUMMIE Engine.V2.PhaseTransitionAck do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.PhaseTransitionAck",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :ready, 1, type: :bool
  field :node_id, 2, type: :string, json_name: "nodeId"
  field :status_report, 3, type: :string, json_name: "statusReport"
end

defmodule DUMMIE Engine.V2.PolyglotError do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.PolyglotError",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :code, 1, type: :int32
  field :message, 2, type: :string
  field :stack_trace, 3, type: :string, json_name: "stackTrace"
  field :origin_layer, 4, type: :string, json_name: "originLayer"
  field :is_recoverable, 5, type: :bool, json_name: "isRecoverable"
  field :associated_event, 6, type: DUMMIE Engine.V2.EventId, json_name: "associatedEvent"
end
