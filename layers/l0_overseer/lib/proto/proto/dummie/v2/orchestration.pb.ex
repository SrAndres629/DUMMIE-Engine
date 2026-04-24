defmodule Dummie.V2.TaskResult.Status do
  @moduledoc false

  use Protobuf,
    enum: true,
    full_name: "dummie.v2.TaskResult.Status",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :SUCCESS, 0
  field :FAILURE, 1
  field :QUARANTINE, 2
end

defmodule Dummie.V2.SovereignContext do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.SovereignContext",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :personality_ref, 1, type: :string, json_name: "personalityRef"
  field :ledger_link, 2, type: :string, json_name: "ledgerLink"
  field :ROI_threshold, 3, type: :float, json_name: "ROIThreshold"
end

defmodule Dummie.V2.ValidationRequest do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ValidationRequest",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :file_path, 1, type: :string, json_name: "filePath"
  field :code_content, 2, type: :string, json_name: "codeContent"
  field :target_layer, 3, type: :string, json_name: "targetLayer"
  field :forbidden_imports, 4, repeated: true, type: :string, json_name: "forbiddenImports"
end

defmodule Dummie.V2.ValidationResponse do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ValidationResponse",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :is_conformant, 1, type: :bool, json_name: "isConformant"
  field :violations, 2, repeated: true, type: Dummie.V2.ArchitecturalViolation
  field :health_score, 3, type: :string, json_name: "healthScore"
end

defmodule Dummie.V2.ArchitecturalViolation do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ArchitecturalViolation",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :file_path, 1, type: :string, json_name: "filePath"
  field :violation_type, 2, type: :string, json_name: "violationType"
  field :description, 3, type: :string
  field :suggestion, 4, type: :string
end

defmodule Dummie.V2.NodeIdentity do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.NodeIdentity",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :node_id, 1, type: :string, json_name: "nodeId"
  field :port_type, 2, type: :string, json_name: "portType"
  field :implementation_version, 3, type: :string, json_name: "implementationVersion"
end

defmodule Dummie.V2.AgentTask do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.AgentTask",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :task_id, 1, type: :string, json_name: "taskId"
  field :agent_type, 2, type: :string, json_name: "agentType"
  field :context_anchor, 3, type: Dummie.V2.EventId, json_name: "contextAnchor"
  field :payload_ticket, 4, type: Dummie.V2.MemoryTicket, json_name: "payloadTicket"
  field :sovereign_ctx, 5, type: Dummie.V2.SovereignContext, json_name: "sovereignCtx"
end

defmodule Dummie.V2.AgentIntent do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.AgentIntent",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :saga_id, 1, type: :string, json_name: "sagaId"
  field :agent_id, 2, type: :string, json_name: "agentId"
  field :intent_type, 3, type: :string, json_name: "intentType"
  field :target_resource, 4, type: :string, json_name: "targetResource"
  field :payload, 5, type: :bytes
  field :parent_event, 6, type: Dummie.V2.EventId, json_name: "parentEvent"
  field :is_shadow, 7, type: :bool, json_name: "isShadow"
  field :sovereign_ctx, 8, type: Dummie.V2.SovereignContext, json_name: "sovereignCtx"
end

defmodule Dummie.V2.TaskResult do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.TaskResult",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :task_id, 1, type: :string, json_name: "taskId"
  field :status, 2, type: Dummie.V2.TaskResult.Status, enum: true
  field :output_ticket, 3, type: Dummie.V2.MemoryTicket, json_name: "outputTicket"
  field :error_summary, 4, type: :string, json_name: "errorSummary"
  field :tokens_consumed, 5, type: :uint32, json_name: "tokensConsumed"
  field :event_id, 6, type: Dummie.V2.EventId, json_name: "eventId"
end

defmodule Dummie.V2.ThoughtTrace do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ThoughtTrace",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :agent_id, 1, type: :string, json_name: "agentId"
  field :thought_fragment, 2, type: :string, json_name: "thoughtFragment"
  field :confidence, 3, type: :float
  field :current_position, 4, type: Dummie.V2.EventId, json_name: "currentPosition"
end

defmodule Dummie.V2.ExecutionRequest.EnvVarsEntry do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ExecutionRequest.EnvVarsEntry",
    map: true,
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :key, 1, type: :string
  field :value, 2, type: :string
end

defmodule Dummie.V2.ExecutionRequest do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ExecutionRequest",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :language, 1, type: :string
  field :code, 2, type: :string

  field :env_vars, 3,
    repeated: true,
    type: Dummie.V2.ExecutionRequest.EnvVarsEntry,
    json_name: "envVars",
    map: true

  field :timeout_ms, 4, type: :uint32, json_name: "timeoutMs"
end

defmodule Dummie.V2.ExecutionResponse do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ExecutionResponse",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :exit_code, 1, type: :int32, json_name: "exitCode"
  field :stdout, 2, type: :string
  field :stderr, 3, type: :string
  field :timed_out, 4, type: :bool, json_name: "timedOut"
end

defmodule Dummie.V2.SkillData do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.SkillData",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :skill_name, 1, type: :string, json_name: "skillName"
  field :wasm_binary, 2, type: :bytes, json_name: "wasmBinary"
  field :metadata_json, 3, type: :string, json_name: "metadataJson"
end

defmodule Dummie.V2.VectorClockRequest do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.VectorClockRequest",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :branch_ids, 1, repeated: true, type: :string, json_name: "branchIds"
end

defmodule Dummie.V2.VectorClockResponse.ClockMapEntry do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.VectorClockResponse.ClockMapEntry",
    map: true,
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :key, 1, type: :string
  field :value, 2, type: :uint64
end

defmodule Dummie.V2.VectorClockResponse do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.VectorClockResponse",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :clock_map, 1,
    repeated: true,
    type: Dummie.V2.VectorClockResponse.ClockMapEntry,
    json_name: "clockMap",
    map: true
end
