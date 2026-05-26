import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from layers.l1_nervous.capability_index import CapabilityIndex

logger = logging.getLogger("dummie-mcp.intent-router")

INTENT_PATTERNS = {
    "image": {
        "generate": [
            "generat",
            "creat",
            "produc",
            "make",
            "render",
            "draw",
            "generar",
            "crear",
        ],
        "analyze": ["analyz", "describ", "caption", "tag", "analizar"],
        "edit": ["edit", "modify", "transform", "inpaint", "outpaint", "editar"],
    },
    "video": {
        "generate": ["generat", "creat", "produc", "make", "generar", "crear"],
        "analyze": ["analyz", "describ", "analizar"],
        "edit": ["edit", "modify", "cut", "trim", "editar"],
    },
    "audio": {
        "generate": ["generat", "creat", "produc", "make", "speech", "tts", "generar"],
        "transcribe": ["transcrib", "stt", "whisper", "transcribir"],
        "analyze": ["analyz", "analizar"],
    },
    "code": {
        "write": [
            "write",
            "implement",
            "creat",
            "develop",
            "program",
            "escribir",
            "implementar",
            "crear",
            "programar",
        ],
        "read": [
            "read",
            "analyz",
            "understand",
            "explain",
            "leer",
            "analizar",
            "entender",
        ],
        "test": ["test", "probar", "testear"],
        "refactor": ["refactor", "restructur", "refactorizar"],
        "review": ["review", "audit", "revisar"],
    },
    "git": {
        "status": ["status", "estado"],
        "commit": ["commit", "committear"],
        "branch": ["branch", "rama"],
        "diff": ["diff", "diferencia"],
        "log": ["log", "history", "historial"],
        "push": ["push"],
        "pull": ["pull"],
    },
    "memory": {
        "store": [
            "store",
            "save",
            "persist",
            "crystalliz",
            "remember",
            "guardar",
            "persistir",
            "cristalizar",
            "recordar",
        ],
        "recall": [
            "recall",
            "remember",
            "retriev",
            "find",
            "search",
            "recordar",
            "recuperar",
            "buscar",
        ],
        "forget": ["forget", "clear", "reset", "olvidar"],
    },
    "data": {
        "query": ["query", "select", "search", "find", "get", "buscar", "consultar"],
        "store": ["store", "insert", "save", "write", "guardar", "insertar"],
        "delete": ["delete", "remove", "drop", "eliminar", "borrar"],
    },
    "infrastructure": {
        "deploy": ["deploy", "publish", "release", "publicar", "desplegar"],
        "manage": [
            "start",
            "stop",
            "restart",
            "exec",
            "run",
            "iniciar",
            "detener",
            "docker",
            "container",
        ],
        "monitor": ["monitor", "log", "status", "health", "monitorear"],
    },
    "communication": {
        "broadcast": ["broadcast", "notify", "announce", "difundir"],
        "delegate": ["delegat", "assign", "delegar"],
        "sync": ["sync", "coordinat", "sincronizar"],
    },
    "planning": {
        "brainstorm": ["brainstorm", "idea", "lluvia"],
        "design": ["design", "architectur", "disenar", "diseñar"],
        "plan": ["plan", "roadmap", "planificar"],
        "research": ["research", "investigat", "learn", "investigar"],
    },
    "development": {
        "scaffold": ["scaffold", "init", "start", "iniciar"],
        "build": ["build", "compil", "construir"],
        "verify": ["verify", "check", "valid", "verificar"],
        "debug": ["debug", "fix", "repair", "arreglar"],
    },
    "automation": {
        "workflow": [
            "n8n",
            "workflow",
            "workflows",
            "webhook",
            "webhooks",
            "automation",
            "automatiza",
            "automatizar",
            "orchestrat",
        ],
        "manage": [
            "execute",
            "ejecutar",
            "deploy",
            "activar",
            "desactivar",
            "credential",
            "credentials",
        ],
    },
    "workspace": {
        "read": ["read", "leer", "open", "abrir"],
        "write": ["write", "escribir", "creat"],
        "search": ["search", "find", "buscar", "grep"],
    },
}

DOMAIN_ALIASES = {
    r"\bimg\b": "image",
    r"\bimagen\b": "image",
    r"\bpicture\b": "image",
    r"\bphoto\b": "image",
    r"\bfoto\b": "image",
    r"\bvid\b": "video",
    r"\bmovie\b": "video",
    r"\bvideo\b": "video",
    r"\bsong\b": "audio",
    r"\bmusic\b": "audio",
    r"\bmusica\b": "audio",
    r"\bsound\b": "audio",
    r"\baudio\b": "audio",
    r"\brepo\b": "code",
    r"\brepositor\b": "code",
    r"\bcodigo\b": "code",
    r"\barchivo\b": "file",
    r"\bfile\b": "file",
    r"\bdb\b": "data",
    r"\bdatabase\b": "data",
    r"\bsql\b": "data",
    r"\binfra\b": "infrastructure",
    r"\bserver\b": "infrastructure",
    r"\bdeploy\b": "infrastructure",
    r"\bdesplegar\b": "deploy",
    r"\bdocker\b": "infrastructure",
    r"\bn8n\b": "automation",
    r"\bworkflow\b": "automation",
    r"\bwebhook\b": "automation",
    r"\bautomatiz": "automation",
    r"\bswarm\b": "communication",
    r"\bbrainstorm\b": "planning",
    r"\bskill\b": "development",
}


@dataclass
class Intent:
    raw: str
    domain: str = ""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

    def is_valid(self) -> bool:
        return bool(self.domain) and self.confidence >= 0.5

    def to_key(self) -> str:
        return f"{self.domain}.{self.action}" if self.action else self.domain


@dataclass
class Resolution:
    found: bool
    intent: Intent
    match: Optional[dict] = None
    alternatives: List[dict] = field(default_factory=list)
    message: str = ""


class IntentClassifier:
    def _best_action_for_domain(self, domain: str, normalized: str) -> str:
        actions = INTENT_PATTERNS.get(domain, {})
        best_action = ""
        best_score = 0
        for action, keywords in actions.items():
            score = sum(1 for kw in keywords if kw in normalized)
            if score > best_score:
                best_action = action
                best_score = score
        return best_action

    def classify(self, query: str) -> Intent:
        raw = query.strip()
        if not raw:
            return Intent(raw="", confidence=0.0)

        normalized = raw.lower()
        for pattern, replacement in DOMAIN_ALIASES.items():
            normalized = re.sub(pattern, replacement, normalized)

        best_domain = ""
        best_action = ""
        best_score = 0.0
        best_params = {}

        for domain, actions in INTENT_PATTERNS.items():
            for action, keywords in actions.items():
                score = 0.0
                for kw in keywords:
                    if kw in normalized:
                        score += 1.0
                if score > 0:
                    score = score / len(keywords)
                    if domain == "code" and "test" in normalized:
                        score += 0.3
                    if domain == "git" and normalized.startswith("git "):
                        score += 0.3
                    if score > best_score:
                        best_domain = domain
                        best_action = action
                        best_score = score

        fallback_candidates = []
        for domain, actions in INTENT_PATTERNS.items():
            if domain in normalized:
                fallback_candidates.append((domain, 0.3))

        domain_priority = {
            "image": 10,
            "audio": 9,
            "video": 8,
            "git": 7,
            "memory": 6,
            "code": 5,
            "infrastructure": 4,
            "automation": 4,
            "data": 3,
            "planning": 2,
            "development": 2,
            "communication": 1,
        }

        if best_score <= 0 and fallback_candidates:
            for domain in sorted(
                fallback_candidates,
                key=lambda x: domain_priority.get(x[0], 0),
                reverse=True,
            ):
                best_domain = domain[0]
                best_score = domain[1]
                break

        if best_score > 0 and best_domain:
            norm_tokens = normalized.split()

            # Bonus unico: el dominio ganador aparece como token en el texto
            if best_domain in norm_tokens:
                best_score += 2

            for other_domain, other_actions in INTENT_PATTERNS.items():
                if other_domain == best_domain:
                    continue
                other_score = sum(
                    1 for kw in sum(other_actions.values(), []) if kw in normalized
                )
                if other_domain in norm_tokens:
                    other_score += 2
                if other_score > best_score + 0.5:
                    best_domain = other_domain
                    best_action = self._best_action_for_domain(other_domain, normalized)
                    best_score = other_score

        if best_domain and not best_action:
            best_action = self._best_action_for_domain(best_domain, normalized)

        intent = Intent(
            raw=raw,
            domain=best_domain,
            action=best_action,
            confidence=best_score,
        )

        if best_domain == "image" and best_action == "generate":
            params = {}
            style_match = re.search(
                r"(cinematic|realistic|anime|cartoon|oil painting|watercolor|3d|pixel art)",
                normalized,
            )
            if style_match:
                params["style"] = style_match.group(1)
            model_match = re.search(r"(sdxl|sd1\.5|sd3|flux|dall-e)", normalized)
            if model_match:
                params["model"] = model_match.group(1)
            intent.parameters = params

        return intent


class IntentRouter:
    def __init__(self, capability_index: CapabilityIndex):
        self._index = capability_index
        self._classifier = IntentClassifier()

    def resolve(self, query: str) -> Resolution:
        intent = self._classifier.classify(query)
        if not intent.is_valid():
            return Resolution(
                found=False,
                intent=intent,
                message=f"No se pudo determinar la intencion del query: '{query}'",
            )

        match = self._index.find_exact_match(intent.domain, intent.action)
        if match:
            return Resolution(
                found=True,
                intent=intent,
                match=match,
                message=f"Match exacto: {match['id']}",
            )

        alternatives = self._index.find_by_intent(intent.domain, intent.action)
        if alternatives:
            return Resolution(
                found=False,
                intent=intent,
                alternatives=alternatives,
                message=(
                    f"Herramienta necesaria no encontrada para '{intent.to_key()}'. "
                    f"Se encontraron {len(alternatives)} alternativa(s) similares "
                    f"que NO cumplen el requisito exacto."
                ),
            )

        return Resolution(
            found=False,
            intent=intent,
            message=(
                f"Herramienta necesaria no encontrada para '{intent.to_key()}'. "
                f"No hay ninguna herramienta o skill que cubra esta capacidad."
            ),
        )

    def analyze_research_needed(self, resolution: Resolution) -> Optional[dict]:
        if resolution.found:
            return None
        return {
            "intent": resolution.intent.to_key(),
            "domain": resolution.intent.domain,
            "action": resolution.intent.action,
            "parameters": resolution.intent.parameters,
            "has_alternatives": len(resolution.alternatives) > 0,
            "suggested_searches": self._build_search_queries(resolution.intent),
        }

    def _build_search_queries(self, intent: Intent) -> List[str]:
        queries = []
        base = f"{intent.domain} {intent.action}"
        queries.append(f"github {base} mcp server")
        queries.append(f"github {base} open source tool")
        queries.append(f"{base} ai model open source")
        if intent.parameters:
            for k, v in intent.parameters.items():
                queries.append(f"github {base} {v} mcp")
        return queries

    def analyze(self, query: str) -> dict:
        resolution = self.resolve(query)
        research = self.analyze_research_needed(resolution)
        return {
            "query": query,
            "resolution": {
                "found": resolution.found,
                "match": resolution.match,
                "alternatives": resolution.alternatives[:5]
                if resolution.alternatives
                else [],
                "message": resolution.message,
            },
            "intent": {
                "domain": resolution.intent.domain,
                "action": resolution.intent.action,
                "parameters": resolution.intent.parameters,
                "confidence": resolution.intent.confidence,
            },
            "research_needed": research is not None,
            "research": research,
        }

    def index(self) -> dict:
        return self._index.sum_index()
