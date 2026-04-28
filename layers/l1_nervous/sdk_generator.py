import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("nervous.sdk_generator")

class DynamicSDKGenerator:
    """
    Generador de SDKs Fuertemente Tipados a partir de esquemas MCP.
    Implementa la capa de abstracción para reducir la carga cognitiva del LLM.
    """
    def __init__(self, proxy_manager: Any, output_dir: str):
        self.proxy = proxy_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_all(self):
        logger.info("Iniciando generación de SDKs tipados...")
        servers = list(self.proxy.servers.keys())
        
        for server in servers:
            try:
                tools = await self.proxy.get_tools_for_server(server)
                self._generate_server_sdk(server, tools)
            except Exception as e:
                logger.error(f"Error generando SDK para {server}: {e}")

    def _generate_server_sdk(self, server_name: str, tools: List[Dict[str, Any]]):
        class_name = "".join([part.capitalize() for part in server_name.replace("-", "_").split("_")])
        
        code = [
            "from pydantic import BaseModel, Field",
            "from typing import Dict, Any, List, Optional",
            "",
            f"# SDK Generado Automáticamente para {server_name}",
            "# NO EDITAR DIRECTAMENTE.",
            "",
            f"class {class_name}Client:",
            "    def __init__(self, proxy_manager: Any):",
            "        self.proxy = proxy_manager",
            ""
        ]
        
        for tool in tools:
            name = tool.get("name", "unknown")
            desc = tool.get("description", "").replace("\n", " ")
            
            # Generar método
            code.append(f"    async def {name.replace('-', '_')}(self, **kwargs) -> Any:")
            code.append(f'        """{desc}"""')
            code.append(f"        return await self.proxy.call_tool('{server_name}', '{name}', kwargs)")
            code.append("")
            
        output_file = self.output_dir / f"{server_name.replace('-', '_')}_sdk.py"
        with open(output_file, "w") as f:
            f.write("\n".join(code))
        logger.info(f"SDK generado exitosamente: {output_file}")
