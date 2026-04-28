from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para socraticode
# NO EDITAR DIRECTAMENTE.

class SocraticodeClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def codebase_index(self, **kwargs) -> Any:
        """Start indexing a codebase in the background. Returns immediately. Call codebase_status to poll progress until 100%. Do NOT search until indexing is complete. If already indexing, returns current progress."""
        return await self.proxy.call_tool('socraticode', 'codebase_index', kwargs)

    async def codebase_update(self, **kwargs) -> Any:
        """Incrementally update an existing codebase index. Only re-indexes changed files. Runs synchronously. Usually not needed if file watcher is active."""
        return await self.proxy.call_tool('socraticode', 'codebase_update', kwargs)

    async def codebase_remove(self, **kwargs) -> Any:
        """Remove a project's codebase index entirely from the vector database. Safely stops the file watcher, cancels any in-progress indexing/update (with drain), and waits for any in-flight graph build before deleting."""
        return await self.proxy.call_tool('socraticode', 'codebase_remove', kwargs)

    async def codebase_stop(self, **kwargs) -> Any:
        """Gracefully stop an in-progress indexing operation. The current batch will finish and checkpoint, preserving all progress. Re-run codebase_index to resume from where it left off."""
        return await self.proxy.call_tool('socraticode', 'codebase_stop', kwargs)

    async def codebase_watch(self, **kwargs) -> Any:
        """Start/stop watching a project directory for file changes and automatically update the index. When starting, first runs an incremental update to catch any changes made since the last session, then keeps the index up to date via debounced file system watching."""
        return await self.proxy.call_tool('socraticode', 'codebase_watch', kwargs)

    async def codebase_search(self, **kwargs) -> Any:
        """Semantic search across an indexed codebase. Only use after codebase_index is complete (check codebase_status first). Returns relevant code chunks matching a natural language query."""
        return await self.proxy.call_tool('socraticode', 'codebase_search', kwargs)

    async def codebase_status(self, **kwargs) -> Any:
        """Check index status: chunk count, indexing progress (%), last completed operation, file watcher state. Call after codebase_index to poll until 100% complete."""
        return await self.proxy.call_tool('socraticode', 'codebase_status', kwargs)

    async def codebase_graph_build(self, **kwargs) -> Any:
        """Build a dependency graph of the codebase using static analysis (ast-grep). Maps import/require/export relationships between files. Runs in the background — call codebase_graph_status to poll progress until complete."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_build', kwargs)

    async def codebase_graph_query(self, **kwargs) -> Any:
        """Query the code dependency graph for a specific file. Returns what the file imports and what files depend on it."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_query', kwargs)

    async def codebase_graph_stats(self, **kwargs) -> Any:
        """Get statistics about the code dependency graph: total files, edges, most connected files, orphan files, circular dependencies."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_stats', kwargs)

    async def codebase_graph_circular(self, **kwargs) -> Any:
        """Find circular dependencies in the codebase."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_circular', kwargs)

    async def codebase_graph_visualize(self, **kwargs) -> Any:
        """Visualise the code dependency graph. Two modes:   • mode="mermaid" (default) — returns a Mermaid diagram (text) colour-coded by language, circular deps highlighted. Best for inline rendering inside chat, GitHub, or editors that render Mermaid.   • mode="interactive" — writes a self-contained HTML page (vendored Cytoscape.js + Dagre, works offline) and opens it in the user's default browser. Shows the file graph and, when a symbol graph is available and fits, a Symbols toggle with the symbol-level call graph. Interactions: click node for sidebar with imports/dependents/symbols list; right-click node to highlight its blast radius (reverse-transitive closure); live search; layout switcher (Dagre / force / concentric / breadth-first / grid / circle); PNG export. Use this when the user asks for a visual/interactive view, wants to explore visually, or needs a shareable diagram."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_visualize', kwargs)

    async def codebase_graph_remove(self, **kwargs) -> Any:
        """Remove a project's persisted code graph. Waits for any in-flight graph build to finish first. The graph can be rebuilt with codebase_graph_build or will be rebuilt automatically on the next codebase_index."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_remove', kwargs)

    async def codebase_graph_status(self, **kwargs) -> Any:
        """Check the status of the code dependency graph: build progress (if building), node/edge count, when it was last built, whether it's cached in memory. Use this to poll progress after calling codebase_graph_build."""
        return await self.proxy.call_tool('socraticode', 'codebase_graph_status', kwargs)

    async def codebase_impact(self, **kwargs) -> Any:
        """Impact Analysis — return the BLAST RADIUS for a file or symbol. Lists every file (and, where helpful, function) that could break if you change the target. Polymorphic on target: a path-like string ('src/foo.ts') triggers file-mode; a name-like string ('validateUser') triggers symbol-mode. Use this BEFORE refactoring, renaming, or deleting code to know what depends on it."""
        return await self.proxy.call_tool('socraticode', 'codebase_impact', kwargs)

    async def codebase_flow(self, **kwargs) -> Any:
        """Trace the EXECUTION FLOW forward from an entry point — what does this code call into? With NO args, returns a ranked list of auto-detected entry points (orphans with outgoing calls, conventional names like main(), framework routes, tests). With an entrypoint argument, returns the call tree."""
        return await self.proxy.call_tool('socraticode', 'codebase_flow', kwargs)

    async def codebase_symbol(self, **kwargs) -> Any:
        """360° view of a symbol: definition, kind, callers, callees, confidence levels. Use to understand a function or class before changing it."""
        return await self.proxy.call_tool('socraticode', 'codebase_symbol', kwargs)

    async def codebase_symbols(self, **kwargs) -> Any:
        """List symbols in a file, or search by name across the project. Use to discover what exists before drilling into a single symbol with codebase_symbol."""
        return await self.proxy.call_tool('socraticode', 'codebase_symbols', kwargs)

    async def codebase_context(self, **kwargs) -> Any:
        """List all context artifacts defined in .socraticodecontextartifacts.json — database schemas, API specs, infra configs, architecture docs, etc. Shows each artifact's name, description, path, and index status. Use this to discover what project knowledge is available beyond source code."""
        return await self.proxy.call_tool('socraticode', 'codebase_context', kwargs)

    async def codebase_context_search(self, **kwargs) -> Any:
        """Semantic search across context artifacts (database schemas, API specs, infra configs, etc.) defined in .socraticodecontextartifacts.json. Auto-indexes on first use and auto-detects stale artifacts. Use this to find relevant infrastructure or domain knowledge."""
        return await self.proxy.call_tool('socraticode', 'codebase_context_search', kwargs)

    async def codebase_context_index(self, **kwargs) -> Any:
        """Index or re-index all context artifacts defined in .socraticodecontextartifacts.json. Chunks and embeds artifact content into the vector database for semantic search. Usually not needed — codebase_context_search auto-indexes on first use."""
        return await self.proxy.call_tool('socraticode', 'codebase_context_index', kwargs)

    async def codebase_context_remove(self, **kwargs) -> Any:
        """Remove all indexed context artifacts for a project from the vector database. Blocked while indexing is in progress — use codebase_stop or wait for the operation to finish first."""
        return await self.proxy.call_tool('socraticode', 'codebase_context_remove', kwargs)

    async def codebase_health(self, **kwargs) -> Any:
        """Check the health of all infrastructure: Docker, Qdrant container, Ollama, and embedding model. Use this to diagnose setup issues."""
        return await self.proxy.call_tool('socraticode', 'codebase_health', kwargs)

    async def codebase_list_projects(self, **kwargs) -> Any:
        """List all projects that have been indexed (have collections in Qdrant)."""
        return await self.proxy.call_tool('socraticode', 'codebase_list_projects', kwargs)

    async def codebase_about(self, **kwargs) -> Any:
        """Display information about SocratiCode — what it is, its tools and how to use it. Use this to get a quick overview of the MCP tools and their purpose."""
        return await self.proxy.call_tool('socraticode', 'codebase_about', kwargs)
