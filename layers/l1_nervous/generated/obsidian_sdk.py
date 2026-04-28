from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para obsidian
# NO EDITAR DIRECTAMENTE.

class ObsidianClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def obsidian_list_files_in_dir(self, **kwargs) -> Any:
        """Lists all files and directories that exist in a specific Obsidian directory."""
        return await self.proxy.call_tool('obsidian', 'obsidian_list_files_in_dir', kwargs)

    async def obsidian_list_files_in_vault(self, **kwargs) -> Any:
        """Lists all files and directories in the root directory of your Obsidian vault."""
        return await self.proxy.call_tool('obsidian', 'obsidian_list_files_in_vault', kwargs)

    async def obsidian_get_file_contents(self, **kwargs) -> Any:
        """Return the content of a single file in your vault."""
        return await self.proxy.call_tool('obsidian', 'obsidian_get_file_contents', kwargs)

    async def obsidian_simple_search(self, **kwargs) -> Any:
        """Simple search for documents matching a specified text query across all files in the vault.              Use this tool when you want to do a simple text search"""
        return await self.proxy.call_tool('obsidian', 'obsidian_simple_search', kwargs)

    async def obsidian_patch_content(self, **kwargs) -> Any:
        """Insert content into an existing note relative to a heading, block reference, or frontmatter field."""
        return await self.proxy.call_tool('obsidian', 'obsidian_patch_content', kwargs)

    async def obsidian_append_content(self, **kwargs) -> Any:
        """Append content to a new or existing file in the vault."""
        return await self.proxy.call_tool('obsidian', 'obsidian_append_content', kwargs)

    async def obsidian_delete_file(self, **kwargs) -> Any:
        """Delete a file or directory from the vault."""
        return await self.proxy.call_tool('obsidian', 'obsidian_delete_file', kwargs)

    async def obsidian_complex_search(self, **kwargs) -> Any:
        """Complex search for documents using a JsonLogic query.             Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching. Results must be non-falsy.             Use this tool when you want to do a complex search, e.g. for all documents with certain tags etc.            """
        return await self.proxy.call_tool('obsidian', 'obsidian_complex_search', kwargs)

    async def obsidian_batch_get_file_contents(self, **kwargs) -> Any:
        """Return the contents of multiple files in your vault, concatenated with headers."""
        return await self.proxy.call_tool('obsidian', 'obsidian_batch_get_file_contents', kwargs)

    async def obsidian_get_periodic_note(self, **kwargs) -> Any:
        """Get current periodic note for the specified period."""
        return await self.proxy.call_tool('obsidian', 'obsidian_get_periodic_note', kwargs)

    async def obsidian_get_recent_periodic_notes(self, **kwargs) -> Any:
        """Get most recent periodic notes for the specified period type."""
        return await self.proxy.call_tool('obsidian', 'obsidian_get_recent_periodic_notes', kwargs)

    async def obsidian_get_recent_changes(self, **kwargs) -> Any:
        """Get recently modified files in the vault."""
        return await self.proxy.call_tool('obsidian', 'obsidian_get_recent_changes', kwargs)
