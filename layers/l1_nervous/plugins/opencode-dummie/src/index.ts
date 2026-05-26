import { Plugin } from "@opencode-ai/plugin";
import { tool } from "@opencode-ai/plugin/tool";
import { execSync } from "child_process";

interface DummieOptions {
  dummieRoot: string;
  defaultLlm: string;
  defaultEmbedding: string;
  metaGatewayPipeline: boolean;
  sddGuardrails: boolean;
  swarmCoordination: boolean;
}

function dummieExec(args: string): string {
  try {
    return execSync(`uv run python -B ${args}`, {
      cwd: "/media/datasets/DUMMIE Engine",
      encoding: "utf-8",
      timeout: 30000,
    }).trim();
  } catch (e: any) {
    return `Error: ${e.message}`;
  }
}

const dummieTools = {
  dummie_discover: tool({
    description: "Discover DUMMIE Engine capabilities (tools, skills, gateways) with optional semantic search",
    args: {
      query: tool.schema.string().optional().describe("Search query for capability discovery"),
    },
    async execute(args) {
      const q = args.query ? `--query "${args.query}"` : "";
      const result = dummieExec(`layers/l1_nervous/mcp_server.py --discover ${q}`);
      return { output: result };
    },
  }),

  dummie_route: tool({
    description: "Route a message through DUMMIE MetaGateway — determines domain (media/code/infra/knowledge/shell) and delegation (local/cloud)",
    args: {
      query: tool.schema.string().describe("The message or intent to route"),
    },
    async execute(args) {
      const result = dummieExec(`layers/l1_nervous/meta_router.py --query "${args.query}"`);
      return { output: result };
    },
  }),

  dummie_swarm: tool({
    description: "Coordinate parallel agent swarm across multiple sessions/tasks",
    args: {
      objective: tool.schema.string().describe("The objective for the swarm"),
      sessions: tool.schema.number().optional().describe("Number of parallel sessions"),
    },
    async execute(args) {
      const sessions = args.sessions ?? 3;
      const result = dummieExec(`layers/l1_nervous/tools_impl/swarm.py --objective "${args.objective}" --sessions ${sessions}`);
      return { output: result };
    },
  }),
};

const sessionGateways = new Map<string, string>();

const plugin: Plugin = async (_input, options) => {
  const opts: DummieOptions = {
    dummieRoot: (options as any)?.dummie_root ?? "/media/datasets/DUMMIE Engine",
    defaultLlm: (options as any)?.default_llm ?? "gemma4:e2b",
    defaultEmbedding: (options as any)?.default_embedding ?? "qwen3-embedding",
    metaGatewayPipeline: (options as any)?.meta_gateway_pipeline ?? true,
    sddGuardrails: (options as any)?.sdd_guardrails ?? true,
    swarmCoordination: (options as any)?.swarm_coordination ?? true,
  };

  return {
    tool: dummieTools,

    "shell.env": async (_input, output) => {
      output.env = {
        ...output.env,
        DUMMIE_ROOT: opts.dummieRoot,
        DUMMIE_AIWG_DIR: `${opts.dummieRoot}/.aiwg`,
        DUMMIE_MCP_CONFIG_PATH: `${opts.dummieRoot}/dummie_gateway_config.json`,
        DUMMIE_DEFAULT_LLM: opts.defaultLlm,
        DUMMIE_DEFAULT_EMBEDDING: opts.defaultEmbedding,
      };
    },

    "tool.execute.before": async (input, output) => {
      if (opts.sddGuardrails) {
        const toolName = input.tool;
        if (toolName.startsWith("vercel.") || toolName.startsWith("cloudflare.")) {
          output.args = {
            ...output.args,
            _sdd_context: { session_id: input.sessionID, call_id: input.callID },
          };
        }
      }
    },

    "experimental.chat.system.transform": async (_input, output) => {
      const gatewayInfo = Array.from(sessionGateways.entries())
        .map(([sid, gw]) => `- Session ${sid}: ${gw} gateway`)
        .join("\n");

      output.system = [
        ...output.system,
        "",
        "## DUMMIE Engine Context",
        "You have access to DUMMIE Engine — a cognitive kernel with specialized sub-gateways:",
        "- **media**: image/video/audio generation (ComfyUI, Cloudflare AI)",
        "- **code**: version control, file system, git operations",
        "- **infra**: Docker, Vercel deployments, Cloudflare infrastructure",
        "- **knowledge**: SQLite queries, sequential thinking, documentation",
        "- **shell**: shell commands, browser automation, bash scripting",
        "",
        "Use `dummie_route` to discover which gateway handles a request.",
        "Use `dummie_discover` to find available tools and capabilities.",
        "Use `dummie_swarm` for parallel multi-agent coordination.",
        "",
        `Active sessions and their gateway assignments:\n${gatewayInfo}`,
      ];
    },

    "experimental.session.compacting": async (_input, output) => {
      output.context = [
        ...output.context,
        "DUMMIE Engine gateway assignments and routing decisions are preserved across sessions.",
        "Use dummie_route to re-evaluate gateway binding if context changes.",
      ];
    },
  };
};

export default plugin;
