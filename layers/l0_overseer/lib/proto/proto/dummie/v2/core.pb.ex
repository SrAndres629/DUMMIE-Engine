defmodule Dummie.V2.AuthorityLevel do
  @moduledoc false

  use Protobuf,
    enum: true,
    full_name: "dummie.v2.AuthorityLevel",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :AUTHORITY_UNSPECIFIED, 0
  field :AGENT, 1
  field :ENGINEER, 2
  field :ARCHITECT, 3
  field :OVERSEER, 4
  field :HUMAN, 5
end

defmodule Dummie.V2.DeathReason do
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

defmodule Dummie.V2.EventId do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.EventId",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :universe_id, 1, type: :string, json_name: "universeId"
  field :branch_id, 2, type: :string, json_name: "branchId"
  field :lamport_tick, 3, type: :uint64, json_name: "lamportTick"
  field :authority, 4, type: Dummie.V2.AuthorityLevel, enum: true
  field :entropy_count, 5, type: :uint32, json_name: "entropyCount"
  field :is_toxic, 6, type: :bool, json_name: "isToxic"
  field :necrosis_info, 7, type: Dummie.V2.DeathMetadata, json_name: "necrosisInfo"
end

defmodule Dummie.V2.DeathMetadata do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.DeathMetadata",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :reason, 1, type: Dummie.V2.DeathReason, enum: true
  field :last_known_instruction, 2, type: :string, json_name: "lastKnownInstruction"
  field :supervisor_note, 3, type: :string, json_name: "supervisorNote"
  field :stack_trace, 4, type: :string, json_name: "stackTrace"
end

defmodule Dummie.V2.MemoryTicket do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.MemoryTicket",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :shm_path, 1, type: :string, json_name: "shmPath"
  field :offset, 2, type: :uint64
  field :length, 3, type: :uint64
  field :alignment, 4, type: :uint32
  field :required_level, 5, type: Dummie.V2.AuthorityLevel, json_name: "requiredLevel", enum: true
  field :namespace_scope, 6, type: :string, json_name: "namespaceScope"
  field :is_toxic, 7, type: :bool, json_name: "isToxic"
  field :ticket_uuid_high, 8, type: :uint64, json_name: "ticketUuidHigh"
  field :ticket_uuid_low, 9, type: :uint64, json_name: "ticketUuidLow"
end

defmodule Dummie.V2.PhaseTransitionSignal do
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

defmodule Dummie.V2.PhaseTransitionAck do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.PhaseTransitionAck",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :ready, 1, type: :bool
  field :node_id, 2, type: :string, json_name: "nodeId"
  field :status_report, 3, type: :string, json_name: "statusReport"
end

defmodule Dummie.V2.PolyglotError do
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
  field :associated_event, 6, type: Dummie.V2.EventId, json_name: "associatedEvent"
end

defmodule Dummie.V2.TelemetrySpan.TagsEntry do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.TelemetrySpan.TagsEntry",
    map: true,
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :key, 1, type: :string
  field :value, 2, type: :string
end

defmodule Dummie.V2.TelemetrySpan do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.TelemetrySpan",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :trace_id, 1, type: :string, json_name: "traceId"
  field :span_id, 2, type: :string, json_name: "spanId"
  field :parent_span_id, 3, type: :string, json_name: "parentSpanId"
  field :name, 4, type: :string
  field :start_time_ns, 5, type: :int64, json_name: "startTimeNs"
  field :end_time_ns, 6, type: :int64, json_name: "endTimeNs"
  field :tags, 7, repeated: true, type: Dummie.V2.TelemetrySpan.TagsEntry, map: true
  field :error, 8, type: Dummie.V2.PolyglotError
end
