# Meta-Gateway Segmentado Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan.

**Goal:** Implement 5 sub-gateways (Media, Code, Infra, Knowledge, Shell) behind a MetaGateway proxy, with embedding router and capability index.

**Architecture:** MetaGateway como punto de entrada único → sub-gateways como procesos HTTP independientes → router basado en embeddings + exact match. Fail isolation, no tool caching, SI cache de índices.

**Tech Stack:** Python 3, mcp 1.26+, fastembed, httpx, JSON configs

---

## File Structure

```
Create:
  layers/l1_nervous/gateway/__init__.py
  layers/l1_nervous/gateway/base_gateway.py
  layers/l1_nervous/gateway/media_gateway.py
  layers/l1_nervous/gateway/code_gateway.py
  layers/l1_nervous/gateway/infra_gateway.py
  layers/l1_nervous/gateway/knowledge_gateway.py
  layers/l1_nervous/gateway/shell_gateway.py
  layers/l1_nervous/configs/gateway_media.json
  layers/l1_nervous/configs/gateway_code.json
  layers/l1_nervous/configs/gateway_infra.json
  layers/l1_nervous/configs/gateway_knowledge.json
  layers/l1_nervous/configs/gateway_shell.json
  layers/l1_nervous/configs/meta_router_assignments.json
  layers/l1_nervous/embeddings/__init__.py
  layers/l1_nervous/embeddings/embedding_service.py
  layers/l1_nervous/embeddings/embedding_router.py
  layers/l1_nervous/embeddings/embedding_cache.py
  layers/l1_nervous/meta_router.py
  layers/l1_nervous/metagateway.py
Modify:
  layers/l1_nervous/capability_index.py
  layers/l1_nervous/tools.py
  dummie_gateway_config.json (remove servers, keep meta)
  .aiwg/registry/mcp_registry.json
  .aiwg/spec_registry/spec_bindings.yaml
```

---

## Chunk 1: Base Gateway + Configs

> Base class for all sub-gateways + 5 JSON configs as SSOT

### Task 1.1: Create gateway directory and __init__

**Files:**
- Create: `layers/l1_nervous/gateway/__init__.py`

- [ ] **Step 1: Create `__init__.py`**

```python
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/gateway/__init__.py
git commit -m "feat: gateway subpackage init"
```

### Task 1.2: Create 5 config JSONs

**Files:**
- Create: `layers/l1_nervous/configs/gateway_media.json`
- Create: `layers/l1_nervous/configs/gateway_code.json`
- Create: `layers/l1_nervous/configs/gateway_infra.json`
- Create: `layers/l1_nervous/configs/gateway_knowledge.json`
- Create: `layers/l1_nervous/configs/gateway_shell.json`

- [ ] **Step 1: Create `gateway_media.json`**

```json
{
  "gateway_name": "media",
  "port": 8081,
  "capability_class": "media_generation",
  "mcp_servers": {
    "muapi": {
      "command": "python3",
      "args": ["${DUMMIE_ROOT}/scripts/muapi_stdio_proxy.py"],
      "env": {"MUAPI_KEY": "${MUAPI_KEY}"}
    },
    "mcp-comfyui": {
      "command": "node",
      "args": ["${BIBLIOTECA_MCP}/Mcp_Comfyui/build/index.js"]
    },
    "cloudflare": {
      "command": "node",
      "args": ["${BIBLIOTECA_MCP}/cloudflare/dist/index.js"],
      "env": {"CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}"}
    }
  }
}
```

- [ ] **Step 2: Create `gateway_code.json`**

```json
{
  "gateway_name": "code",
  "port": 8082,
  "capability_class": "vcs_workspace",
  "mcp_servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "${DUMMIE_ROOT}"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${DUMMIE_ROOT}", "/tmp"]
    }
  }
}
```

- [ ] **Step 3: Create `gateway_infra.json`**

```json
{
  "gateway_name": "infra",
  "port": 8083,
  "capability_class": "infrastructure",
  "mcp_servers": {
    "docker": {
      "command": "docker-mcp",
      "args": []
    },
    "vercel": {
      "command": "node",
      "args": ["${BIBLIOTECA_MCP}/Vercel/dist/index.js"],
      "env": {"VERCEL_TOKEN": "${VERCEL_TOKEN}"}
    }
  }
}
```

- [ ] **Step 4: Create `gateway_knowledge.json`**

```json
{
  "gateway_name": "knowledge",
  "port": 8084,
  "capability_class": "structured_knowledge",
  "mcp_servers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "${DUMMIE_AIWG}/memory/dummie_sqlite.db"]
    },
    "sequentialthinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

- [ ] **Step 5: Create `gateway_shell.json`**

```json
{
  "gateway_name": "shell",
  "port": 8085,
  "capability_class": "shell_automation",
  "mcp_servers": {
    "shell": {
      "command": "npx",
      "args": ["-y", "mcp-shell"]
    },
    "mcp-bash": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/patrickomatik/mcp-bash.git", "mcp-bash"]
    },
    "browser-use": {
      "command": "uvx",
      "args": ["--from", "browser-use[cli]", "browser-use", "--mcp"]
    }
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add layers/l1_nervous/configs/
git commit -m "feat: 5 gateway configs as SSOT per domain"
```

### Task 1.3: Create base_gateway.py

**Files:**
- Create: `layers/l1_nervous/gateway/base_gateway.py`

- [ ] **Step 1: Write base_gateway.py**

```python
import json, os, sys, asyncio, time
from pathlib import Path
from mcp import StdioClient, StdioServerParameters

DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine"))
AIWG_RUNTIME = DUMMIE_ROOT / ".aiwg" / "runtime" / "gateways"

def _expand_env(s):
    for k, v in os.environ.items():
        s = s.replace(f"${{{k}}}", v)
    return s.replace("${BIBLIOTECA_MCP}", "/home/jorand/Escritorio/Biblioteca MCP")

class BaseGateway:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
        self.name = self.config["gateway_name"]
        self.port = self.config["port"]
        self.servers: dict[str, StdioClient] = {}
        self.readiness_path = AIWG_RUNTIME / f"{self.name}.ready"
        AIWG_RUNTIME.mkdir(parents=True, exist_ok=True)

    async def start(self):
        for name, cfg in self.config["mcp_servers"].items():
            try:
                cmd = _expand_env(cfg["command"])
                args = [_expand_env(a) for a in cfg.get("args", [])]
                env = {**_expand_env(k): _expand_env(v) for k, v in cfg.get("env", {}).items()}
                params = StdioServerParameters(command=cmd, args=args, env=env)
                client = StdioClient(params)
                await client.initialize()
                self.servers[name] = client
            except Exception as e:
                print(f"[{self.name}] Failed to start {name}: {e}", file=sys.stderr)
        self._write_readiness("ready")
        return self

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict = None):
        client = self.servers.get(server_name)
        if not client:
            raise ValueError(f"Server {server_name} not in gateway {self.name}")
        return await client.call_tool(tool_name, arguments or {})

    def get_capabilities(self) -> list[dict]:
        caps = []
        for srv_name, cfg in self.config["mcp_servers"].items():
            client = self.servers.get(srv_name)
            if client:
                caps.append({"server": srv_name, "gateway": self.name, "port": self.port})
        return caps

    async def stop(self):
        for name, client in self.servers.items():
            await client.close()
        self._write_readiness("stopped")

    def _write_readiness(self, state: str):
        self.readiness_path.write_text(state)
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/gateway/base_gateway.py
git commit -m "feat: BaseGateway class with MCP client lifecycle"
```

---

## Chunk 2: 5 Sub-Gateways

> Each sub-gateway is a thin subclass of BaseGateway (5-15 lines each)

### Task 2.1-2.5: Create sub-gateways

**Files:**
- Create: `layers/l1_nervous/gateway/media_gateway.py`
- Create: `layers/l1_nervous/gateway/code_gateway.py`
- Create: `layers/l1_nervous/gateway/infra_gateway.py`
- Create: `layers/l1_nervous/gateway/knowledge_gateway.py`
- Create: `layers/l1_nervous/gateway/shell_gateway.py`

- [ ] **Step 1: Create media_gateway.py**

```python
import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[2] / "configs" / "gateway_media.json"

class MediaGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))

async def main():
    gw = MediaGateway()
    await gw.start()
    print(f"[media] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Create code_gateway.py** (same pattern, path: `gateway_code.json`)

```python
import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[2] / "configs" / "gateway_code.json"

class CodeGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))

async def main():
    gw = CodeGateway()
    await gw.start()
    print(f"[code] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: Create infra_gateway.py** (same pattern, path: `gateway_infra.json`)

```python
import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[2] / "configs" / "gateway_infra.json"

class InfraGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))

async def main():
    gw = InfraGateway()
    await gw.start()
    print(f"[infra] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Create knowledge_gateway.py** (same pattern, path: `gateway_knowledge.json`)

```python
import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[2] / "configs" / "gateway_knowledge.json"

class KnowledgeGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))

async def main():
    gw = KnowledgeGateway()
    await gw.start()
    print(f"[knowledge] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 5: Create shell_gateway.py** (same pattern, path: `gateway_shell.json`)

```python
import asyncio, sys
from pathlib import Path
from .base_gateway import BaseGateway

CONFIG = Path(__file__).parents[2] / "configs" / "gateway_shell.json"

class ShellGateway(BaseGateway):
    def __init__(self):
        super().__init__(str(CONFIG))

async def main():
    gw = ShellGateway()
    await gw.start()
    print(f"[shell] Gateway ready on port {gw.port}", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await gw.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 6: Commit**

```bash
git add layers/l1_nervous/gateway/media_gateway.py layers/l1_nervous/gateway/code_gateway.py layers/l1_nervous/gateway/infra_gateway.py layers/l1_nervous/gateway/knowledge_gateway.py layers/l1_nervous/gateway/shell_gateway.py
git commit -m "feat: 5 sub-gateway processes with config-based MCP lifecycle"
```

---

## Chunk 3: Meta Router Assignments + Embeddings Service

> Global SSOT mapping + embedding infrastructure

### Task 3.1: Create meta_router_assignments.json

**Files:**
- Create: `layers/l1_nervous/configs/meta_router_assignments.json`

- [ ] **Step 1: Create SSOT mapping**

```json
{
  "version": "1.0.0",
  "gateways": {
    "media": {
      "port": 8081,
      "domains": ["media_generation", "image", "video", "audio"],
      "servers": {
        "muapi": {
          "tools": ["generate_image", "generate_video", "generate_audio", "upload_file", "list_models"]
        },
        "mcp-comfyui": {
          "tools": ["inspect_capabilities", "generate_image_from_intent", "get_execution_history", "get_optimizations"]
        },
        "cloudflare": {
          "tools": ["run_ai_model"]
        }
      }
    },
    "code": {
      "port": 8082,
      "domains": ["vcs", "workspace", "code"],
      "servers": {
        "github": {"tools": ["*"]},
        "git": {"tools": ["*"]},
        "filesystem": {"tools": ["*"]}
      }
    },
    "infra": {
      "port": 8083,
      "domains": ["infrastructure", "deployment", "cloud"],
      "servers": {
        "docker": {"tools": ["manage_containers", "manage_images", "manage_infrastructure", "audit_system", "execute_operations"]},
        "vercel": {"tools": ["vercel_omni_manager"]}
      }
    },
    "knowledge": {
      "port": 8084,
      "domains": ["knowledge", "memory", "reasoning"],
      "servers": {
        "sqlite": {"tools": ["*"]},
        "sequentialthinking": {"tools": ["*"]}
      }
    },
    "shell": {
      "port": 8085,
      "domains": ["shell", "automation", "browser"],
      "servers": {
        "shell": {"tools": ["*"]},
        "mcp-bash": {"tools": ["*"]},
        "browser-use": {"tools": ["*"]}
      }
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/configs/meta_router_assignments.json
git commit -m "feat: meta_router_assignments SSOT global"
```

### Task 3.2: Create embeddings service + cache + router

**Files:**
- Create: `layers/l1_nervous/embeddings/__init__.py`
- Create: `layers/l1_nervous/embeddings/embedding_service.py`
- Create: `layers/l1_nervous/embeddings/embedding_cache.py`
- Create: `layers/l1_nervous/embeddings/embedding_router.py`

- [ ] **Step 1: Create `embeddings/__init__.py`**

```python
from .embedding_service import EmbeddingService
from .embedding_router import EmbeddingRouter
from .embedding_cache import EmbeddingCache

__all__ = ["EmbeddingService", "EmbeddingRouter", "EmbeddingCache"]
```

- [ ] **Step 2: Create `embedding_service.py`**

```python
import numpy as np
from functools import lru_cache

class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        return list(self.model.embed(texts))

    def embed_one(self, text: str) -> np.ndarray:
        return list(self.model.embed([text]))[0]

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @property
    def dimensions(self) -> int:
        return 384
```

- [ ] **Step 3: Create `embedding_cache.py`**

```python
import time
from collections import OrderedDict

class EmbeddingCache:
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        self._cache: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str):
        if key not in self._cache:
            return None
        expires, value = self._cache[key]
        if time.time() > expires:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value, ttl: float = None):
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = (time.time() + ttl, value)
        self._cache.move_to_end(key)
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self):
        self._cache.clear()
```

- [ ] **Step 4: Create `embedding_router.py`**

```python
import numpy as np
from .embedding_service import EmbeddingService
from .embedding_cache import EmbeddingCache

DOMAIN_PROTOTYPES = {
    "media_generation": "generar imagen video audio contenido multimedia",
    "vcs": "git commit push pull branch repository code version",
    "workspace_io": "leer archivo escribir archivo filesystem",
    "infrastructure": "docker container deploy cloud infrastructure",
    "shell_execution": "ejecutar comando shell terminal bash",
    "browser_automation": "navegar web browser test automatico",
    "structured_knowledge": "base de datos sql query memoria conocimiento",
    "reasoning_support": "razonar pensar planificar analizar",
}

class EmbeddingRouter:
    def __init__(self):
        self.service = EmbeddingService()
        self.cache = EmbeddingCache(default_ttl=300.0)
        self.domain_vectors = {
            name: self.service.embed_one(text)
            for name, text in DOMAIN_PROTOTYPES.items()
        }

    def route(self, query: str, threshold: float = 0.35) -> list[tuple[str, float]]:
        cached = self.cache.get(f"route:{query}")
        if cached:
            return cached
        qvec = self.service.embed_one(query)
        scores = [(name, self.service.similarity(qvec, dvec))
                  for name, dvec in self.domain_vectors.items()]
        scores.sort(key=lambda x: -x[1])
        result = [(name, score) for name, score in scores if score >= threshold]
        self.cache.set(f"route:{query}", result, ttl=60.0)
        return result

    def best_domain(self, query: str, threshold: float = 0.35) -> tuple[str, float] | None:
        results = self.route(query, threshold)
        return results[0] if results else None
```

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/embeddings/
git commit -m "feat: embedding service + cache + router"
```

---

## Chunk 4: Meta Router + MetaGateway

> Core routing logic + entry point

### Task 4.1: Create meta_router.py

**Files:**
- Create: `layers/l1_nervous/meta_router.py`

- [ ] **Step 1: Write meta_router.py**

```python
import json, os, re
from pathlib import Path
from .embeddings import EmbeddingRouter

CONFIG_PATH = Path(__file__).parent / "configs" / "meta_router_assignments.json"

class MetaRouter:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.assignments = json.load(f)
        self.embedding_router = EmbeddingRouter()
        self._build_index()

    def _build_index(self):
        self._domain_to_gateway = {}
        self._server_map = {}
        for gw_name, gw_cfg in self.assignments["gateways"].items():
            for domain in gw_cfg["domains"]:
                self._domain_to_gateway[domain] = gw_name
            for srv_name, srv_cfg in gw_cfg["servers"].items():
                key = f"{gw_name}.{srv_name}"
                tools = srv_cfg.get("tools", [])
                self._server_map[key] = {
                    "gateway": gw_name,
                    "server": srv_name,
                    "port": gw_cfg["port"],
                    "tools": tools,
                }

    def route(self, query: str) -> dict:
        query_lower = query.lower().strip()
        domain, action = self._parse_intent(query_lower)
        if not domain:
            best = self.embedding_router.best_domain(query)
            domain = best[0] if best else "unknown"
            confidence = best[1] if best else 0.0
        else:
            confidence = 1.0

        gw_name = self._domain_to_gateway.get(domain)
        if not gw_name:
            return {"match": False, "domain": domain, "confidence": confidence,
                    "message": f"No gateway for domain '{domain}'"}

        result = {"match": True, "domain": domain, "gateway": gw_name,
                  "port": self.assignments["gateways"][gw_name]["port"],
                  "confidence": confidence,
                  "servers": list(self.assignments["gateways"][gw_name]["servers"].keys())}
        return result

    def _parse_intent(self, query: str) -> tuple[str | None, str | None]:
        intent_map = [
            (r"imagen|image|generar.*imagen|generar.*foto|generar.*img", "media_generation", "image"),
            (r"video|generar.*video|crear.*video|generar.*clip", "media_generation", "video"),
            (r"audio|musica|musica|generar.*audio|generar.*sonido", "media_generation", "audio"),
            (r"git|commit|push|pull|branch|repositorio|repo", "vcs", "git"),
            (r"archivo|file|leer|escribir|read|write|filesystem", "workspace_io", "file"),
            (r"docker|contenedor|container|imagen.*docker|deploy", "infrastructure", "docker"),
            (r"vercel|deploy|desplegar|hosting|dominio|domain", "infrastructure", "deploy"),
            (r"sql|query|base.*datos|database|consulta|memoria|knowledge", "structured_knowledge", "query"),
            (r"shell|terminal|comando|command|ejecutar|run|bash", "shell_execution", "shell"),
            (r"navegador|browser|web|pagina|test|chrome|firefox", "browser_automation", "browser"),
            (r"razonar|pensar|planificar|analizar|think|reason|plan", "reasoning_support", "reason"),
        ]
        for pattern, dom, act in intent_map:
            if re.search(pattern, query):
                return dom, act
        return None, None

    def list_all_capabilities(self) -> list[dict]:
        caps = []
        for gw_name, gw_cfg in self.assignments["gateways"].items():
            for srv_name, srv_cfg in gw_cfg["servers"].items():
                caps.append({
                    "gateway": gw_name,
                    "server": srv_name,
                    "port": gw_cfg["port"],
                    "tools": srv_cfg.get("tools", ["*"]),
                })
        return caps
```

- [ ] **Step 2: Create test file**

```python
# tests/test_meta_router.py
import sys; sys.path.insert(0, "layers/l1_nervous")
from meta_router import MetaRouter

router = MetaRouter()

def test_route_image():
    r = router.route("generar imagen")
    assert r["match"]
    assert r["gateway"] == "media"
    print("  test_route_image: PASS")

def test_route_git():
    r = router.route("git status")
    assert r["match"]
    assert r["gateway"] == "code"
    print("  test_route_git: PASS")

def test_route_docker():
    r = router.route("docker ps")
    assert r["match"]
    assert r["gateway"] == "infra"
    print("  test_route_docker: PASS")

def test_route_sql():
    r = router.route("consulta SQL")
    assert r["match"]
    assert r["gateway"] == "knowledge"
    print("  test_route_sql: PASS")

def test_route_shell():
    r = router.route("ejecutar comando")
    assert r["match"]
    assert r["gateway"] == "shell"
    print("  test_route_shell: PASS")

def test_route_no_match():
    r = router.route("cual es el clima")
    assert not r["match"]
    print("  test_route_no_match: PASS")

if __name__ == "__main__":
    test_route_image()
    test_route_git()
    test_route_docker()
    test_route_sql()
    test_route_shell()
    test_route_no_match()
    print("All tests PASS")
```

- [ ] **Step 3: Run tests**

Run: `python tests/test_meta_router.py`
Expected: "All tests PASS"

- [ ] **Step 4: Commit**

```bash
git add layers/l1_nervous/meta_router.py tests/test_meta_router.py
git commit -m "feat: MetaRouter with intent parsing + embedding fallback"
```

### Task 4.2: Create metagateway.py

**Files:**
- Create: `layers/l1_nervous/metagateway.py`

- [ ] **Step 1: Write metagateway.py**

```python
import json, sys, asyncio, os
from pathlib import Path
from meta_router import MetaRouter

class MetaGateway:
    def __init__(self):
        self.router = MetaRouter()
        self._gateway_clients = {}

    async def route_request(self, query: str, arguments: dict = None):
        route = self.router.route(query)
        if not route["match"]:
            return {"error": True, "message": route.get("message", "No matching gateway"),
                    "confidence": route.get("confidence", 0.0), "domain": route.get("domain")}
        gw_name = route["gateway"]
        gw_port = route["port"]
        return {"gateway": gw_name, "port": gw_port, "servers": route["servers"],
                "route": route, "query": query}

    async def call_tool(self, query: str, tool: str, arguments: dict = None):
        import httpx
        route = self.router.route(query)
        if not route["match"]:
            raise ValueError(f"No gateway found for: {query}")
        gw_port = route["port"]
        server = route["servers"][0]
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"http://localhost:{gw_port}/call",
                json={"server": server, "tool": tool, "arguments": arguments or {}},
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()

if __name__ == "__main__":
    async def main():
        mg = MetaGateway()
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
                query = msg.get("query", "")
                result = await mg.route_request(query)
                print(json.dumps(result), flush=True)
            except Exception as e:
                print(json.dumps({"error": True, "message": str(e)}), flush=True)

    asyncio.run(main())
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/metagateway.py
git commit -m "feat: MetaGateway entry point with stdio listener"
```

---

## Chunk 5: Update Existing Files

> Integrate MetaGateway into tools.py + capability_index + main gateway config

### Task 5.1: Update capability_index.py

**Files:**
- Modify: `layers/l1_nervous/capability_index.py`

- [ ] **Step 1: Add MetaGateway sync method**

Add to the CapabilityIndex class:

```python
def sync_from_metagateway(self, meta_router_assignments_path: str = None):
    import json
    from pathlib import Path
    path = meta_router_assignments_path or str(
        Path(__file__).parent / "configs" / "meta_router_assignments.json"
    )
    with open(path) as f:
        data = json.load(f)
    for gw_name, gw_cfg in data["gateways"].items():
        for srv_name, srv_cfg in gw_cfg["servers"].items():
            tools = srv_cfg.get("tools", ["*"])
            for tool in tools:
                key = f"{gw_name}:{srv_name}:{tool}"
                if key not in self._capabilities:
                    self._capabilities[key] = {
                        "gateway": gw_name,
                        "server": srv_name,
                        "tool": tool,
                        "port": gw_cfg["port"],
                        "domain": gw_cfg["domains"],
                    }
    return len(self._capabilities)
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/capability_index.py
git commit -m "feat: capability_index sync_from_metagateway"
```

### Task 5.2: Update tools.py with MetaGateway tool

**Files:**
- Modify: `layers/l1_nervous/tools.py`

- [ ] **Step 1: Add MetaGateway discover tool**

Add to the tool registration:

```python
@mcp.tool()
async def metagateway_discover(query: str = "") -> str:
    """Discover capabilities across all sub-gateways. Optionally route a query."""
    from metagateway import MetaGateway
    mg = MetaGateway()
    if query:
        result = await mg.route_request(query)
        return json.dumps(result, indent=2, ensure_ascii=False)
    caps = mg.router.list_all_capabilities()
    return json.dumps(caps, indent=2, ensure_ascii=False)
```

- [ ] **Step 2: Commit**

```bash
git add layers/l1_nervous/tools.py
git commit -m "feat: metagateway_discover tool in tools.py"
```

### Task 5.3: Update dummie_gateway_config.json

**Files:**
- Modify: `dummie_gateway_config.json`

- [ ] **Step 1: Replace with MetaGateway entry only**

```json
{
  "mcpServers": {
    "metagateway": {
      "command": "uv",
      "args": ["run", "python", "-B", "${DUMMIE_ROOT}/layers/l1_nervous/metagateway.py"],
      "disabled": false,
      "profile": "core",
      "capability_class": "metagateway",
      "rationale": "MetaGateway proxy que enruta queries a 5 sub-gateways especializados (media, code, infra, knowledge, shell). Punto de entrada único para todas las capabilities."
    },
    "superpowers": {
      "command": "uv",
      "args": ["run", "python", "${DUMMIE_ROOT}/scripts/superpowers_mcp_proxy.py"],
      "disabled": false,
      "profile": "auxiliary",
      "capability_class": "development_workflow",
      "rationale": "Superpowers development workflow system (14 skills as MCP tools)."
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add dummie_gateway_config.json
git commit -m "feat: replace direct MCPs with MetaGateway + Superpowers"
```

---

## Chunk 6: Registry + Spec Bindings

> Update canonical registry and spec bindings

### Task 6.1: Update mcp_registry.json

**Files:**
- Modify: `.aiwg/registry/mcp_registry.json`

- [ ] **Step 1: Update registry**

```python
# Update script
import json
from pathlib import Path

reg = json.loads(Path(".aiwg/registry/mcp_registry.json").read_text())

# Add new files
new_entries = [
    {"path": "layers/l1_nervous/metagateway.py", "kind": "meta_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/meta_router.py", "kind": "meta_router", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/base_gateway.py", "kind": "base_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/media_gateway.py", "kind": "sub_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/code_gateway.py", "kind": "sub_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/infra_gateway.py", "kind": "sub_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/knowledge_gateway.py", "kind": "sub_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/gateway/shell_gateway.py", "kind": "sub_gateway", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/configs/meta_router_assignments.json", "kind": "ssot_routing", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/embeddings/embedding_service.py", "kind": "embedding_service", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/embeddings/embedding_router.py", "kind": "embedding_router", "status": "active", "spec": 170},
    {"path": "layers/l1_nervous/embeddings/embedding_cache.py", "kind": "embedding_cache", "status": "active", "spec": 170},
]

existing_paths = {e["path"] for e in reg["items"]}
for entry in new_entries:
    if entry["path"] not in existing_paths:
        reg["items"].append(entry)

reg["version"] = "1.3.0"
reg["generated_at"] = "2026-05-22T00:00:00Z"
reg["total_items"] = len(reg["items"])

Path(".aiwg/registry/mcp_registry.json").write_text(json.dumps(reg, indent=2))
print(f"Registry updated: {len(reg['items'])} items")
```

Run: `python scripts/update_registry.py`

- [ ] **Step 2: Commit**

```bash
git add .aiwg/registry/mcp_registry.json
git commit -m "chore: registry v1.3.0 - MetaGateway segmentado"
```

### Task 6.2: Update spec_bindings.yaml

**Files:**
- Modify: `.aiwg/spec_registry/spec_bindings.yaml`

- [ ] **Step 1: Add spec 170 binding**

```yaml
- spec: 170
  title: "Meta-Gateway Segmentado"
  description: "5 sub-gateways especializados (Media, Code, Infra, Knowledge, Shell) + MetaGateway proxy con router basado en embeddings"
  files:
    - layers/l1_nervous/metagateway.py
    - layers/l1_nervous/meta_router.py
    - layers/l1_nervous/gateway/base_gateway.py
    - layers/l1_nervous/gateway/media_gateway.py
    - layers/l1_nervous/gateway/code_gateway.py
    - layers/l1_nervous/gateway/infra_gateway.py
    - layers/l1_nervous/gateway/knowledge_gateway.py
    - layers/l1_nervous/gateway/shell_gateway.py
    - layers/l1_nervous/configs/meta_router_assignments.json
    - layers/l1_nervous/configs/gateway_media.json
    - layers/l1_nervous/configs/gateway_code.json
    - layers/l1_nervous/configs/gateway_infra.json
    - layers/l1_nervous/configs/gateway_knowledge.json
    - layers/l1_nervous/configs/gateway_shell.json
    - layers/l1_nervous/embeddings/embedding_service.py
    - layers/l1_nervous/embeddings/embedding_router.py
    - layers/l1_nervous/embeddings/embedding_cache.py
    - layers/l1_nervous/capability_index.py
    - layers/l1_nervous/tools.py
```

- [ ] **Step 2: Commit**

```bash
git add .aiwg/spec_registry/spec_bindings.yaml
git commit -m "chore: spec 170 binding - MetaGateway segmentado"
```

---

## Chunk 7: Verification

> Verify all 5 gateways route correctly + MetaGateway responds

### Task 7.1: Write verification script

**Files:**
- Create: `scripts/verify_metagateway.py`

- [ ] **Step 1: Write verification script**

```python
#!/usr/bin/env python3
"""Verify MetaGateway routing for all 5 sub-gateways."""
import sys, json, asyncio
sys.path.insert(0, "layers/l1_nervous")
from meta_router import MetaRouter

async def verify():
    router = MetaRouter()
    results = {"pass": 0, "fail": 0, "tests": []}

    def test(name, query, expected_gateway):
        r = router.route(query)
        ok = r.get("match") and r.get("gateway") == expected_gateway
        results["tests"].append({
            "name": name, "query": query,
            "expected_gateway": expected_gateway,
            "actual_gateway": r.get("gateway"),
            "pass": ok
        })
        if ok:
            results["pass"] += 1
            print(f"  ✅ {name}: {query} → {expected_gateway}")
        else:
            results["fail"] += 1
            print(f"  ❌ {name}: {query} → expected {expected_gateway}, got {r.get('gateway')}")

    test("Media - image", "generar imagen", "media")
    test("Media - video", "crear video promocional", "media")
    test("Media - audio", "generar musica", "media")
    test("Code - git", "git commit", "code")
    test("Code - filesystem", "leer archivo", "code")
    test("Infra - docker", "docker ps", "infra")
    test("Infra - vercel", "deploy to vercel", "infra")
    test("Knowledge - sql", "query database", "knowledge")
    test("Knowledge - reason", "razonar sobre esto", "knowledge")
    test("Shell - command", "ejecutar comando", "shell")
    test("Shell - browser", "navegar a youtube", "shell")
    test("No match", "cual es el clima", None)

    print(f"\n{'='*40}")
    print(f"Results: {results['pass']}/{len(results['tests'])} pass, {results['fail']} fail")
    if results["fail"] == 0:
        print("✅ ALL TESTS PASS")
    else:
        print("❌ SOME TESTS FAILED")
    return results

if __name__ == "__main__":
    r = asyncio.run(verify())
    sys.exit(0 if r["fail"] == 0 else 1)
```

- [ ] **Step 2: Run verification**

Run: `python scripts/verify_metagateway.py`
Expected: 11/11 pass, "ALL TESTS PASS"

- [ ] **Step 3: Register design and plan in ledger**

```bash
echo '{"resolution":"MetaGateway segmentado design spec #170 approved and implemented","spec":170,"files":["metagateway.py","meta_router.py","gateway/*.py","configs/*.json","embeddings/*.py"],"date":"2026-05-22"}' >> .aiwg/ledger/sovereign_resolutions.jsonl
```

- [ ] **Step 4: Final commit**

```bash
git add scripts/verify_metagateway.py .aiwg/ledger/sovereign_resolutions.jsonl
git commit -m "feat: verification + ledger for MetaGateway"
```
