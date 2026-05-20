---
name: openrouter-agent
description: Build or extend a modular AI agent using OpenRouter SDK (TypeScript/Node.js) with 300+ models, tool-calling, items-based streaming, and optional Ink TUI. Use when user says "openrouter", "create agent", "OR agent", "build an agent with openrouter", or wants to use @openrouter/sdk.
---

# Build a Modular AI Agent with OpenRouter

Build a **modular AI agent** with OpenRouter SDK for unified access to 300+ language models, tool-calling, and items-based streaming.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Your Application                 │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Ink TUI   │  │  HTTP API   │  │   Discord   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         └────────────────┼────────────────┘         │
│                          ▼                          │
│              ┌───────────────────────┐              │
│              │      Agent Core       │              │
│              │  (hooks & lifecycle)  │              │
│              └───────────┬───────────┘              │
│                          ▼                          │
│              ┌───────────────────────┐              │
│              │    OpenRouter SDK     │              │
│              └───────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

## Project Setup

```bash
mkdir my-agent && cd my-agent
npm init -y
npm pkg set type="module"
npm install @openrouter/sdk zod eventemitter3
npm install ink react    # Optional: TUI
npm install -D typescript @types/react tsx
```

## Agent Core (`src/agent.ts`)

Standalone agent that can run anywhere:

```typescript
import { OpenRouter, tool, stepCountIs } from '@openrouter/sdk';
import type { Tool, StopCondition, StreamableOutputItem } from '@openrouter/sdk';
import { EventEmitter } from 'eventemitter3';
import { z } from 'zod';

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AgentEvents {
  'message:user': (message: Message) => void;
  'message:assistant': (message: Message) => void;
  'item:update': (item: StreamableOutputItem) => void;
  'stream:start': () => void;
  'stream:delta': (delta: string, accumulated: string) => void;
  'stream:end': (fullText: string) => void;
  'tool:call': (name: string, args: unknown) => void;
  'tool:result': (name: string, result: unknown) => void;
  'reasoning:update': (text: string) => void;
  'error': (error: Error) => void;
  'thinking:start': () => void;
  'thinking:end': () => void;
}

export interface AgentConfig {
  apiKey: string;
  model?: string;
  instructions?: string;
  tools?: Tool<z.ZodTypeAny, z.ZodTypeAny>[];
  maxSteps?: number;
}

export class Agent extends EventEmitter<AgentEvents> {
  private client: OpenRouter;
  private messages: Message[] = [];
  private config: Required<Omit<AgentConfig, 'apiKey'>> & { apiKey: string };

  constructor(config: AgentConfig) {
    super();
    this.client = new OpenRouter({ apiKey: config.apiKey });
    this.config = {
      apiKey: config.apiKey,
      model: config.model ?? 'openrouter/auto',
      instructions: config.instructions ?? 'You are a helpful assistant.',
      tools: config.tools ?? [],
      maxSteps: config.maxSteps ?? 5,
    };
  }

  getMessages(): Message[] { return [...this.messages]; }
  clearHistory(): void { this.messages = []; }
  setInstructions(instructions: string): void { this.config.instructions = instructions; }
  addTool(newTool: Tool<z.ZodTypeAny, z.ZodTypeAny>): void { this.config.tools.push(newTool); }

  async send(content: string): Promise<string> {
    const userMessage: Message = { role: 'user', content };
    this.messages.push(userMessage);
    this.emit('message:user', userMessage);
    this.emit('thinking:start');
    try {
      const result = this.client.callModel({
        model: this.config.model,
        instructions: this.config.instructions,
        input: this.messages.map((m) => ({ role: m.role, content: m.content })),
        tools: this.config.tools.length > 0 ? this.config.tools : undefined,
        stopWhen: [stepCountIs(this.config.maxSteps)],
      });
      this.emit('stream:start');
      let fullText = '';
      for await (const item of result.getItemsStream()) {
        this.emit('item:update', item);
        switch (item.type) {
          case 'message':
            const textContent = item.content?.find((c) => c.type === 'output_text');
            if (textContent && 'text' in textContent && textContent.text !== fullText) {
              const delta = textContent.text.slice(fullText.length);
              fullText = textContent.text;
              this.emit('stream:delta', delta, fullText);
            }
            break;
          case 'function_call':
            if (item.status === 'completed')
              this.emit('tool:call', item.name, JSON.parse(item.arguments || '{}'));
            break;
          case 'function_call_output':
            this.emit('tool:result', item.callId, item.output);
            break;
          case 'reasoning':
            const reasoningText = item.content?.find((c) => c.type === 'reasoning_text');
            if (reasoningText && 'text' in reasoningText)
              this.emit('reasoning:update', reasoningText.text);
            break;
        }
      }
      if (!fullText) fullText = await result.getText();
      this.emit('stream:end', fullText);
      const assistantMessage: Message = { role: 'assistant', content: fullText };
      this.messages.push(assistantMessage);
      this.emit('message:assistant', assistantMessage);
      return fullText;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      this.emit('error', error);
      throw error;
    } finally {
      this.emit('thinking:end');
    }
  }

  async sendSync(content: string): Promise<string> {
    const userMessage: Message = { role: 'user', content };
    this.messages.push(userMessage);
    this.emit('message:user', userMessage);
    try {
      const result = this.client.callModel({
        model: this.config.model,
        instructions: this.config.instructions,
        input: this.messages.map((m) => ({ role: m.role, content: m.content })),
        tools: this.config.tools.length > 0 ? this.config.tools : undefined,
        stopWhen: [stepCountIs(this.config.maxSteps)],
      });
      const fullText = await result.getText();
      const assistantMessage: Message = { role: 'assistant', content: fullText };
      this.messages.push(assistantMessage);
      this.emit('message:assistant', assistantMessage);
      return fullText;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      this.emit('error', error);
      throw error;
    }
  }
}

export function createAgent(config: AgentConfig): Agent { return new Agent(config); }
```

## Tools (`src/tools.ts`)

```typescript
import { tool } from '@openrouter/sdk';
import { z } from 'zod';

export const timeTool = tool({
  name: 'get_current_time',
  description: 'Get the current date and time',
  inputSchema: z.object({
    timezone: z.string().optional().describe('Timezone (e.g., "UTC", "America/New_York")'),
  }),
  execute: async ({ timezone }) => ({
    time: new Date().toLocaleString('en-US', { timeZone: timezone || 'UTC' }),
    timezone: timezone || 'UTC',
  }),
});

export const calculatorTool = tool({
  name: 'calculate',
  description: 'Perform mathematical calculations',
  inputSchema: z.object({
    expression: z.string().describe('Math expression (e.g., "2 + 2")'),
  }),
  execute: async ({ expression }) => {
    const sanitized = expression.replace(/[^0-9+\-*/().\s]/g, '');
    return { expression, result: Function(`"use strict"; return (${sanitized})`)() };
  },
});

export const defaultTools = [timeTool, calculatorTool];
```

## Items-Based Streaming

The SDK uses an **items-based streaming model** where items are emitted with the same ID and progressively updated content. Replace by ID, don't accumulate:

```typescript
const items = new Map<string, StreamableOutputItem>();
for await (const item of result.getItemsStream()) {
  items.set(item.id, item);  // Replace by ID
  updateUI(items);
}
```

| Item Type | Purpose |
|-----------|---------|
| `message` | Assistant text responses |
| `function_call` | Tool invocations (streaming args) |
| `function_call_output` | Tool execution results |
| `reasoning` | Extended thinking content |
| `web_search_call` | Web search operations |
| `file_search_call` | File search operations |
| `image_generation_call` | Image generation operations |

## Discovery de Modelos

No hardcodees model IDs — cambian frecuentemente. Usa la API:

```typescript
async function fetchModels(): Promise<OpenRouterModel[]> {
  const res = await fetch('https://openrouter.ai/api/v1/models');
  return (await res.json()).data;
}
```

Usa `openrouter/auto` para selección automática del mejor modelo disponible.

## Recursos

- OpenRouter Docs: https://openrouter.ai/docs
- Models API: https://openrouter.ai/api/v1/models
- Ink Docs: https://github.com/vadimdemedes/ink
- Get API Key: https://openrouter.ai/settings/keys
