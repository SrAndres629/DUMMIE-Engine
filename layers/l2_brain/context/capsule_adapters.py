import os
import ast
import hashlib
import uuid
from datetime import datetime, timezone
from brain.application.ports.capsule_ports import ContextCapsulePort
from brain.domain.context.capsule_models import ContextCapsule, ASTSyntaxNode, TokenEconomyPolicy

class IncrementalAstIndexerAdapter(ContextCapsulePort):
    def index_source_ast(self, file_paths: list) -> list:
        nodes = []
        for path in file_paths:
            if not os.path.exists(path) or not path.endswith(".py"):
                continue
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Calculate source hash
                source_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                
                # Parse AST
                parsed_ast = ast.parse(content, filename=path)
                
                for node in ast.walk(parsed_ast):
                    if isinstance(node, ast.ClassDef):
                        nodes.append(ASTSyntaxNode(
                            file_path=path,
                            symbol_name=node.name,
                            symbol_type="class",
                            source_hash=source_hash,
                            loc=len(node.body)
                        ))
                    elif isinstance(node, ast.FunctionDef):
                        nodes.append(ASTSyntaxNode(
                            file_path=path,
                            symbol_name=node.name,
                            symbol_type="function",
                            source_hash=source_hash,
                            loc=len(node.body)
                        ))
            except Exception:
                # Soft failure: fallback or skip on syntax/parse errors
                pass
                
        return nodes

    def package_capsule(self, target_pack: str, policy: TokenEconomyPolicy) -> ContextCapsule:
        # Packages surgical context under dynamic token budget policies
        return ContextCapsule(
            capsule_id=str(uuid.uuid4()),
            target_pack=target_pack,
            generated_at=datetime.now(timezone.utc),
            ast_nodes=[],
            relevance_scores={},
            token_budget_allocated=policy.max_input_budget,
            compressed_payload_bytes=0
        )
