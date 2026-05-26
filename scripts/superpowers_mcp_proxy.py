#!/usr/bin/env python3
"""
Superpowers MCP Proxy — envuelve skills de Superpowers (y DUMMIE Engine) como
herramientas MCP accesibles via gateway.

Skills se cargan LAZY — solo cuando se invocan — no al inicio.
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.WARNING, stream=sys.stderr, force=True)
logger = logging.getLogger("superpowers-mcp")

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Superpowers-Gateway")

SUPERPOWERS_DIR = os.path.expanduser("~/.agents/skills/superpowers")
DUMMIE_SKILLS_DIR = os.environ.get(
    "DUMMIE_SKILLS_DIR",
    os.path.join(
        os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine"),
        ".agents",
        "skills",
    ),
)


def _discover_skills(base_dir: str, skill_type: str):
    skills = {}
    if not os.path.isdir(base_dir):
        return skills
    for name in sorted(os.listdir(base_dir)):
        skill_dir = os.path.join(base_dir, name)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if os.path.isdir(skill_dir) and os.path.exists(skill_md):
            try:
                with open(skill_md) as f:
                    content = f.read()
                title = content.split("\n")[0].lstrip("#").strip() or name
                skills[name] = {
                    "title": title,
                    "path": skill_md,
                    "content": content,
                    "type": skill_type,
                }
            except Exception as e:
                logger.warning("Error reading %s: %s", skill_md, e)
    return skills


def _discover_superpowers():
    return _discover_skills(SUPERPOWERS_DIR, "superpower")


def _discover_dummie_skills():
    return _discover_skills(DUMMIE_SKILLS_DIR, "dummie")


@mcp.tool()
async def list_superpowers(query: str = "") -> str:
    """Lista todos los skills de Superpowers disponibles. Opcional: filtro por query."""
    skills = _discover_superpowers()
    if not skills:
        return "No se encontraron skills de Superpowers."

    lines = ["=== SUPERPOwERS SKILLS ==="]
    for name, info in skills.items():
        if (
            query
            and query.lower() not in name.lower()
            and query.lower() not in info["title"].lower()
        ):
            continue
        lines.append(f"\n- {name}: {info['title']}")
        content_preview = info["content"][:200].replace("\n", " ").strip()
        lines.append(f"  Preview: {content_preview}...")
    return "\n".join(lines)


@mcp.tool()
async def load_superpower_skill(skill_name: str, section: str = "") -> str:
    """
    Carga un skill de Superpowers bajo demanda.
    Args:
        skill_name: nombre del skill (ej: 'brainstorming', 'test-driven-development')
        section: opcional, sección específica a extraer (ej: 'Process Flow', 'Checklist')
    """
    skills = _discover_superpowers()
    if not skills:
        return "Error: No se encontraron skills de Superpowers instalados."

    if skill_name not in skills:
        available = ", ".join(sorted(skills.keys()))
        return (
            f"Skill '{skill_name}' no encontrado. "
            f"Disponibles: {available}\n"
            f"Sugerencia: usa list_superpowers() para ver todos los skills."
        )

    info = skills[skill_name]
    content = info["content"]

    if section:
        import re

        pattern = rf"##\s*{re.escape(section)}.*?(?=##\s|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return f"# {info['title']} - {section}\n\n{match.group().strip()}"
        return (
            f"Seccion '{section}' no encontrada en skill '{skill_name}'.\n"
            f"Skills disponibles: {', '.join(sorted(skills.keys()))}"
        )

    return content


@mcp.tool()
async def list_dummie_skills(query: str = "") -> str:
    """Lista los skills locales de DUMMIE disponibles. Opcional: filtro por query."""
    skills = _discover_dummie_skills()
    if not skills:
        return "No se encontraron skills locales de DUMMIE."

    lines = ["=== DUMMIE LOCAL SKILLS ==="]
    for name, info in skills.items():
        if (
            query
            and query.lower() not in name.lower()
            and query.lower() not in info["title"].lower()
        ):
            continue
        lines.append(f"\n- {name}: {info['title']}")
        content_preview = info["content"][:200].replace("\n", " ").strip()
        lines.append(f"  Preview: {content_preview}...")
    return "\n".join(lines)


@mcp.tool()
async def load_dummie_skill(skill_name: str, section: str = "") -> str:
    """Carga un skill local de DUMMIE bajo demanda."""
    skills = _discover_dummie_skills()
    if not skills:
        return "Error: No se encontraron skills locales de DUMMIE."

    if skill_name not in skills:
        available = ", ".join(sorted(skills.keys()))
        return (
            f"Skill '{skill_name}' no encontrado. "
            f"Disponibles: {available}\n"
            f"Sugerencia: usa list_dummie_skills() para ver todos los skills."
        )

    info = skills[skill_name]
    content = info["content"]

    if section:
        import re

        pattern = rf"##\s*{re.escape(section)}.*?(?=##\s|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return f"# {info['title']} - {section}\n\n{match.group().strip()}"
        return (
            f"Seccion '{section}' no encontrada en skill '{skill_name}'.\n"
            f"Skills disponibles: {', '.join(sorted(skills.keys()))}"
        )

    return content


if __name__ == "__main__":
    mcp.run(transport="stdio")
