defmodule Io.Dummie.V2.Memory.IntentType do
  @moduledoc false

  use Protobuf,
    enum: true,
    full_name: "io.dummie.v2.memory.IntentType",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :INTENT_UNSPECIFIED, 0
  field :OBSERVATION, 1
  field :MUTATION, 2
  field :RESOLUTION, 3
  field :CRYSTALLIZATION, 4
end

defmodule Io.Dummie.V2.Memory.DecisionRecord do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.DecisionRecord",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :decision_id, 1, type: :string, json_name: "decisionId"
  field :rationale, 2, type: :string
  field :impact_blast_radius, 3, type: :string, json_name: "impactBlastRadius"
  field :context, 4, type: Io.Dummie.V2.Memory.SixDimensionalContext
  field :target_causal_hash, 5, type: :string, json_name: "targetCausalHash"
  field :witness_hash, 6, type: :string, json_name: "witnessHash"
  field :tick, 7, type: :uint64
end

defmodule Io.Dummie.V2.Memory.Lesson do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.Lesson",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :tick, 1, type: :int64
  field :lesson_id, 2, type: :string, json_name: "lessonId"
  field :issue, 3, type: :string
  field :correction, 4, type: :string
  field :prevention, 5, type: :string
end

defmodule Io.Dummie.V2.Memory.Ambiguity do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.Ambiguity",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :tick, 1, type: :int64
  field :ambiguity_id, 2, type: :string, json_name: "ambiguityId"
  field :context, 3, type: :string
  field :resolution, 4, type: :string
  field :impact, 5, type: :string
end

defmodule Io.Dummie.V2.Memory.SessionCrystallization do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.SessionCrystallization",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :decisions, 1, repeated: true, type: Io.Dummie.V2.Memory.DecisionRecord
  field :lessons, 2, repeated: true, type: Io.Dummie.V2.Memory.Lesson
  field :ambiguities, 3, repeated: true, type: Io.Dummie.V2.Memory.Ambiguity
end

defmodule Io.Dummie.V2.Memory.SixDimensionalContext do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.SixDimensionalContext",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :locus_x, 1, type: :string, json_name: "locusX"
  field :locus_y, 2, type: :string, json_name: "locusY"
  field :locus_z, 3, type: :string, json_name: "locusZ"
  field :lamport_t, 4, type: :uint64, json_name: "lamportT"
  field :authority_a, 5, type: Dummie.V2.AuthorityLevel, json_name: "authorityA", enum: true
  field :intent_i, 6, type: Io.Dummie.V2.Memory.IntentType, json_name: "intentI", enum: true
end

defmodule Io.Dummie.V2.Memory.MemoryNode4DTES do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.MemoryNode4DTES",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :causal_hash, 1, type: :string, json_name: "causalHash"
  field :parent_hash, 2, type: :string, json_name: "parentHash"
  field :context, 3, type: Io.Dummie.V2.Memory.SixDimensionalContext
  field :payload, 4, type: :bytes
  field :payload_hash, 5, type: :string, json_name: "payloadHash"
end

defmodule Io.Dummie.V2.Memory.EgoState do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.EgoState",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :agent_id, 1, type: :string, json_name: "agentId"
  field :tick, 2, type: :uint64
  field :thought_vector, 3, type: :string, json_name: "thoughtVector"
  field :action, 4, type: :string
  field :context, 5, type: Io.Dummie.V2.Memory.SixDimensionalContext
end

defmodule Io.Dummie.V2.Memory.LayerCertainty do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.LayerCertainty",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :layer_name, 1, type: :string, json_name: "layerName"
  field :certainty_score, 2, type: :float, json_name: "certaintyScore"
  field :is_terra_incognita, 3, type: :bool, json_name: "isTerraIncognita"
  field :tests_passing, 4, type: :uint32, json_name: "testsPassing"
  field :unverified_mutations, 5, type: :uint32, json_name: "unverifiedMutations"
end

defmodule Io.Dummie.V2.Memory.OntologicalMap do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.OntologicalMap",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :layers, 1, repeated: true, type: Io.Dummie.V2.Memory.LayerCertainty
  field :updated_at, 2, type: Google.Protobuf.Timestamp, json_name: "updatedAt"
end

defmodule Io.Dummie.V2.Memory.AgentPresenceHeartbeat do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.AgentPresenceHeartbeat",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :agent_id, 1, type: :string, json_name: "agentId"
  field :expertise_tags, 2, repeated: true, type: :string, json_name: "expertiseTags"
  field :current_load, 3, type: :float, json_name: "currentLoad"
  field :authority_level, 4, type: :string, json_name: "authorityLevel"
end

defmodule Io.Dummie.V2.Memory.CrystallizedSkill do
  @moduledoc false

  use Protobuf,
    full_name: "io.dummie.v2.memory.CrystallizedSkill",
    protoc_gen_elixir_version: "0.16.0",
    syntax: :proto3

  field :skill_id, 1, type: :string, json_name: "skillId"
  field :yaml_payload, 2, type: :string, json_name: "yamlPayload"
  field :source_causal_hashes, 3, repeated: true, type: :string, json_name: "sourceCausalHashes"
  field :skill_hash, 4, type: :string, json_name: "skillHash"
end
