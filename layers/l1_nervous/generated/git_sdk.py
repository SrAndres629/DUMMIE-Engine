from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para git
# NO EDITAR DIRECTAMENTE.

class GitClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def git_status(self, **kwargs) -> Any:
        """Shows the working tree status"""
        return await self.proxy.call_tool('git', 'git_status', kwargs)

    async def git_diff_unstaged(self, **kwargs) -> Any:
        """Shows changes in the working directory that are not yet staged"""
        return await self.proxy.call_tool('git', 'git_diff_unstaged', kwargs)

    async def git_diff_staged(self, **kwargs) -> Any:
        """Shows changes that are staged for commit"""
        return await self.proxy.call_tool('git', 'git_diff_staged', kwargs)

    async def git_diff(self, **kwargs) -> Any:
        """Shows differences between branches or commits"""
        return await self.proxy.call_tool('git', 'git_diff', kwargs)

    async def git_commit(self, **kwargs) -> Any:
        """Records changes to the repository"""
        return await self.proxy.call_tool('git', 'git_commit', kwargs)

    async def git_add(self, **kwargs) -> Any:
        """Adds file contents to the staging area"""
        return await self.proxy.call_tool('git', 'git_add', kwargs)

    async def git_reset(self, **kwargs) -> Any:
        """Unstages all staged changes"""
        return await self.proxy.call_tool('git', 'git_reset', kwargs)

    async def git_log(self, **kwargs) -> Any:
        """Shows the commit logs"""
        return await self.proxy.call_tool('git', 'git_log', kwargs)

    async def git_create_branch(self, **kwargs) -> Any:
        """Creates a new branch from an optional base branch"""
        return await self.proxy.call_tool('git', 'git_create_branch', kwargs)

    async def git_checkout(self, **kwargs) -> Any:
        """Switches branches"""
        return await self.proxy.call_tool('git', 'git_checkout', kwargs)

    async def git_show(self, **kwargs) -> Any:
        """Shows the contents of a commit"""
        return await self.proxy.call_tool('git', 'git_show', kwargs)

    async def git_branch(self, **kwargs) -> Any:
        """List Git branches"""
        return await self.proxy.call_tool('git', 'git_branch', kwargs)
