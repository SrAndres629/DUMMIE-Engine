defmodule DUMMIE Engine.V2.AmbiguityResolution do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.AmbiguityResolution",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :tick, 1, type: :uint64
  field :timestamp, 2, type: Google.Protobuf.Timestamp
  field :agent_id, 3, type: :string, json_name: "agentId"
  field :topic, 4, type: :string
  field :user_input, 5, type: :string, json_name: "userInput"
  field :resolution_path, 6, type: :string, json_name: "resolutionPath"
  field :associated_event, 7, type: DUMMIE Engine.V2.EventId, json_name: "associatedEvent"
end

defmodule DUMMIE Engine.V2.LessonLearned do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.LessonLearned",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :tick, 1, type: :uint64
  field :agent_id, 2, type: :string, json_name: "agentId"
  field :failed_pattern, 3, type: :string, json_name: "failedPattern"
  field :success_pattern, 4, type: :string, json_name: "successPattern"
  field :confidence_score, 5, type: :float, json_name: "confidenceScore"
  field :tags, 6, repeated: true, type: :string
  field :associated_event, 7, type: DUMMIE Engine.V2.EventId, json_name: "associatedEvent"
end

defmodule DUMMIE Engine.V2.ArchitecturalDecision do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.ArchitecturalDecision",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :tick, 1, type: :uint64
  field :agent_id, 2, type: :string, json_name: "agentId"
  field :decision, 3, type: :string
  field :rationale, 4, type: :string
  field :spec_involved, 5, type: :string, json_name: "specInvolved"
  field :impact_radius, 6, repeated: true, type: :string, json_name: "impactRadius"
  field :associated_event, 7, type: DUMMIE Engine.V2.EventId, json_name: "associatedEvent"
end

defmodule DUMMIE Engine.V2.SessionMemory do
  @moduledoc false

  use Protobuf,
    full_name: "dummie.v2.SessionMemory",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :session_id, 1, type: :string, json_name: "sessionId"
  field :ambiguities, 2, repeated: true, type: DUMMIE Engine.V2.AmbiguityResolution
  field :lessons, 3, repeated: true, type: DUMMIE Engine.V2.LessonLearned
  field :decisions, 4, repeated: true, type: DUMMIE Engine.V2.ArchitecturalDecision
end
