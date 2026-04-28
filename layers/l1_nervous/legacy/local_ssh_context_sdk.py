from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# SDK Generado Automáticamente para local-ssh-context
# NO EDITAR DIRECTAMENTE.

class LocalSshContextClient:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def execute_command(self, **kwargs) -> Any:
        """Execute shell command on remote server"""
        return await self.proxy.call_tool('local-ssh-context', 'execute_command', kwargs)

    async def file_operations(self, **kwargs) -> Any:
        """File operations (read, write, list directory)"""
        return await self.proxy.call_tool('local-ssh-context', 'file_operations', kwargs)

    async def system_monitor(self, **kwargs) -> Any:
        """Monitor system resources (CPU, memory, disk)"""
        return await self.proxy.call_tool('local-ssh-context', 'system_monitor', kwargs)

    async def process_manager(self, **kwargs) -> Any:
        """Manage processes (list, kill, status)"""
        return await self.proxy.call_tool('local-ssh-context', 'process_manager', kwargs)

    async def ssh_reconnect(self, **kwargs) -> Any:
        """Reconnect to SSH server (force reconnection)"""
        return await self.proxy.call_tool('local-ssh-context', 'ssh_reconnect', kwargs)

    async def sftp_download(self, **kwargs) -> Any:
        """Download a file from the remote server via SFTP"""
        return await self.proxy.call_tool('local-ssh-context', 'sftp_download', kwargs)

    async def sftp_upload(self, **kwargs) -> Any:
        """Upload content to a file on the remote server via SFTP"""
        return await self.proxy.call_tool('local-ssh-context', 'sftp_upload', kwargs)
