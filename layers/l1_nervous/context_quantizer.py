import os
import re
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

try:
    import tiktoken
    ENC = tiktoken.get_encoding("cl100k_base")
except ImportError:
    ENC = None

logger = logging.getLogger("dummie-mcp.turbo-quant")

class ContextQuantizer:
    """
    Implementación del principio TurboQuant (Cuantización Semántica).
    Optimiza el contexto podando información irrelevante y comprimiendo estructuras.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def count_tokens(self, text: str) -> int:
        if ENC:
            return len(ENC.encode(text))
        return len(text.split()) # Fallback a palabras si no hay tiktoken

    def prune_tree(self, tree_str: str, keywords: List[str]) -> str:
        """
        Poda el árbol de directorios manteniendo solo ramas que coincidan con keywords.
        Implementa exclusión de patrones de ruido con límites de palabra (Production Hardening).
        """
        import re
        # Patrones de ruido con anclaje para evitar falsos positivos (ej. 'bin' vs 'binance')
        ignore_patterns = [r'\.git\b', r'__pycache__\b', r'node_modules\b', r'\.venv\b', r'\.pytest_cache\b', r'\bbin\b', r'\bobj\b']
        
        lines = tree_str.split('\n')
        pruned_lines = []
        
        for line in lines:
            # Limpieza básica de ruido usando regex para precisión
            if any(re.search(p, line) for p in ignore_patterns):
                continue
                
            if not keywords:
                pruned_lines.append(line)
                continue
                
            if any(kw.lower() in line.lower() for kw in keywords) or line.strip().endswith('/'):
                pruned_lines.append(line)
        
        return "\n".join(pruned_lines)

    def quantize_spec(self, content: str) -> Tuple[str, Dict[str, float]]:
        """
        Convierte una especificación Markdown en una representación YAML densa (TurboQuant).
        Retorna la versión cuantizada y métricas de reducción.
        """
        original_tokens = self.count_tokens(content)
        
        # Extraer ID y Título
        title_match = re.search(r'# (.*)', content)
        title = title_match.group(1).strip() if title_match else "Unknown Spec"
        
        # Extraer Frontmatter
        fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        fm = fm_match.group(1).strip() if fm_match else ""
        
        # Extraer Invariantes Críticos
        # Buscamos patrones: "- **Name**: Description" o "- Name: Description"
        invariants = []
        inv_matches = re.findall(r'-\s*\*\*?(.*?)\*\*?:\s*(.*)', content, re.MULTILINE)
        if inv_matches:
            invariants = [f"{m[0]}: {m[1][:120]}" for m in inv_matches[:10]]
        else:
            # Búsqueda genérica de items de lista con soporte multilínea
            generic_items = re.findall(r'-\s*([A-Z].*?)(?:\.|\n)', content, re.MULTILINE | re.DOTALL)
            invariants = [item[:120].strip() for item in generic_items[:6]]

        # Construir YAML denso
        quantized = "spec_quantized:\n"
        quantized += f"  title: \"{title}\"\n"
        if fm:
            indented_fm = "\n".join(f"    {l}" for l in fm.split('\n'))
            quantized += f"  metadata:\n{indented_fm}\n"
        
        if invariants:
            quantized += "  critical_invariants:\n"
            for inv in invariants:
                quantized += f"    - {inv}\n"
        
        # Abstract ontológico
        purpose_match = re.search(r'#.*?\n\n(.*?)\n', content, re.DOTALL)
        if purpose_match:
            abstract = purpose_match.group(1).strip().replace('\n', ' ')
            quantized += f"  abstract: \"{abstract[:250]}...\"\n"
            
        quantized_tokens = self.count_tokens(quantized)
        reduction = 1 - (quantized_tokens / original_tokens) if original_tokens > 0 else 0
        
        metrics = {
            "original_tokens": original_tokens,
            "quantized_tokens": quantized_tokens,
            "reduction_ratio": reduction
        }
        
        return quantized, metrics

    def compress_identity(self, header: Dict[str, Any]) -> str:
        identity = header.get("identity", {})
        role = identity.get("role", "agent")
        caps = ",".join(identity.get("capabilities", []))
        return f"ID:{role}|CAPS:[{caps}]|M:{header.get('mission_rationale', '')[:60]}"

def quantize_context_for_goal(goal: str, full_context: Dict[str, str], root_dir: str) -> Dict[str, Any]:
    """
    Función de utilidad para el orquestador con reporte de métricas.
    """
    quantizer = ContextQuantizer(root_dir)
    keywords = [w for w in re.findall(r'\w+', goal) if len(w) > 3]
    
    q_spec, spec_metrics = quantizer.quantize_spec(full_context.get("specs", ""))
    q_tree = quantizer.prune_tree(full_context.get("tree", ""), keywords)
    
    return {
        "context": {
            "tree": q_tree,
            "specs": q_spec,
            "arch": full_context.get("arch", "")
        },
        "metrics": {
            "specs": spec_metrics,
            "tree_lines_reduction": 1 - (len(q_tree.split('\n')) / len(full_context.get("tree", "").split('\n'))) if full_context.get("tree") else 0
        }
    }
