import os
import re
from typing import List, Dict, Any
from pathlib import Path

class ContextQuantizer:
    """
    Implementación del principio TurboQuant (Cuantización Semántica).
    Optimiza el contexto podando información irrelevante y comprimiendo estructuras.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def prune_tree(self, tree_str: str, keywords: List[str]) -> str:
        """
        Poda el árbol de directorios manteniendo solo ramas que coincidan con keywords.
        Implementa exclusión de patrones de ruido.
        """
        ignore_patterns = {'.git', '__pycache__', 'node_modules', '.venv', '.pytest_cache'}
        
        lines = tree_str.split('\n')
        pruned_lines = []
        
        # Siempre mantener la estructura básica si hay coincidencia semántica
        for line in lines:
            # Limpieza básica
            if any(p in line for p in ignore_patterns):
                continue
                
            # Si no hay keywords, solo limpiamos ruido
            if not keywords:
                pruned_lines.append(line)
                continue
                
            # Si hay keywords, buscamos relevancia
            if any(kw.lower() in line.lower() for kw in keywords) or line.strip().endswith('/'):
                pruned_lines.append(line)
        
        return "\n".join(pruned_lines)

    def quantize_spec(self, content: str) -> str:
        """
        Convierte una especificación Markdown en una representación YAML densa (TurboQuant).
        Extrae solo la esencia técnica para ahorrar tokens.
        """
        # Extraer ID y Título de los primeros headers
        title_match = re.search(r'# (.*)', content)
        title = title_match.group(1).strip() if title_match else "Unknown Spec"
        
        # Extraer Frontmatter si existe
        fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        fm = fm_match.group(1).strip() if fm_match else ""
        
        # Extraer Invariantes (líneas que empiezan con - en secciones de Reglas o Invariantes)
        # Buscamos bloques de listas que parecen reglas
        invariants = []
        inv_matches = re.findall(r'-\s*\*\*?(.*?)\*\*?:\s*(.*)', content)
        if inv_matches:
            invariants = [f"{m[0]}: {m[1][:100]}" for m in inv_matches[:8]]
        else:
            # Búsqueda genérica de items de lista
            generic_items = re.findall(r'-\s*([A-Z].*?)(?:\.|\n)', content)
            invariants = [item[:100] for item in generic_items[:5]]

        # Construir YAML denso
        quantized = "spec_quantized:\n"
        quantized += f"  title: \"{title}\"\n"
        if fm:
            # Indentar frontmatter
            indented_fm = "\n".join(f"    {l}" for l in fm.split('\n'))
            quantized += f"  metadata:\n{indented_fm}\n"
        
        if invariants:
            quantized += "  critical_invariants:\n"
            for inv in invariants:
                quantized += f"    - {inv}\n"
        
        # Resumen del propósito (párrafo después del primer header)
        purpose_match = re.search(r'#.*?\n\n(.*?)\n', content, re.DOTALL)
        if purpose_match:
            abstract = purpose_match.group(1).strip().replace('\n', ' ')
            quantized += f"  abstract: \"{abstract[:200]}...\"\n"
            
        return quantized

    def compress_identity(self, header: Dict[str, Any]) -> str:
        """
        Comprime el header metacognitivo a su mínima expresión.
        """
        identity = header.get("identity", {})
        role = identity.get("role", "agent")
        caps = ",".join(identity.get("capabilities", []))
        return f"ID:{role}|CAPS:[{caps}]|M:{header.get('mission_rationale', '')[:50]}"

def quantize_context_for_goal(goal: str, full_context: Dict[str, str], root_dir: str) -> Dict[str, str]:
    """
    Función de utilidad para el orquestador.
    """
    quantizer = ContextQuantizer(root_dir)
    # Extraer keywords del goal (simple split por ahora)
    keywords = [w for w in re.findall(r'\w+', goal) if len(w) > 3]
    
    return {
        "tree": quantizer.prune_tree(full_context.get("tree", ""), keywords),
        "specs": quantizer.quantize_spec(full_context.get("specs", "")),
        "arch": full_context.get("arch", "") # La arquitectura se suele dejar completa por seguridad
    }
