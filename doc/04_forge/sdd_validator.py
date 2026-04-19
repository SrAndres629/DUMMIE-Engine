import os
import yaml
import json
import re
import sys
from pathlib import Path

# === Configuración Industrial (SDD V3) ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(PROJECT_ROOT, "doc/specs")
PROTO_DIR = os.path.join(PROJECT_ROOT, "proto/dummie/v2")
VALID_LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
REQUIRED_YAML_KEYS = ['spec_id', 'title', 'status', 'version', 'layer', 'namespace']

class SDDSemanticAuditor:
    def __init__(self):
        self.spec_index = {} # spec_id -> file_path
        self.proto_entities = set() # messages and services
        self.errors = {}
        self.total_scanned = 0

    def load_proto_entities(self):
        """Escanea archivos .proto para extraer nombres de mensajes y servicios."""
        if not os.path.exists(PROTO_DIR):
            return
        
        for root, _, files in os.walk(PROTO_DIR):
            for file in files:
                if file.endswith(".proto"):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        # Buscar 'message <Name>' o 'service <Name>'
                        matches = re.findall(r'\b(?:message|service)\s+([A-Z][a-zA-Z0-9_]+)', content)
                        self.proto_entities.update(matches)

    def index_specs(self):
        """Crea un mapa global de Spec IDs para validación de referencias."""
        # Escaneamos todo el directorio doc/ para incluir Specs y ADRs
        search_dir = os.path.join(PROJECT_ROOT, "doc")
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                        if match:
                            try:
                                data = yaml.safe_load(match.group(1))
                                if 'spec_id' in data:
                                    spec_id = data['spec_id']
                                    # Normalizar ID (remover markdown links)
                                    clean_id = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', str(spec_id))
                                    self.spec_index[clean_id] = path
                            except:
                                pass

    def validate_file(self, file_path):
        file_errors = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Validación de Frontmatter (YAML)
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return ["Error Fatal: Falta Frontmatter YAML"]
        
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            return [f"Error Fatal: YAML Inválido: {e}"]
        
        # 2. Validación de Claves Requeridas
        for key in REQUIRED_YAML_KEYS:
            if key not in data:
                file_errors.append(f"Falta clave YAML: {key}")
        
        # 3. Validación de Capas y Ubicación Física
        layer = data.get('layer', 'Unknown')
        if layer not in VALID_LAYERS:
            file_errors.append(f"Capa inválida: {layer}. Debe ser L0-L6.")
        else:
            # Validar que el archivo esté en una carpeta que empiece por la Capa (ej: L0_Overseer)
            parent_dir = Path(file_path).parent.name
            if layer not in parent_dir and "specs" not in parent_dir:
                file_errors.append(f"Ubicación incorrecta: La spec marcada como {layer} reside en '{parent_dir}'. Debe estar en una carpeta 'doc/specs/{layer}_*'.")

        # 4. Auditoría de Dependencias (Cross-Spec)
        if 'dependencies' in data and isinstance(data['dependencies'], list):
            for dep in data['dependencies']:
                dep_id = dep.get('id')
                # Manejar casos donde el ID incluye una ruta markdown [Id](path)
                real_id = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', str(dep_id))
                if real_id not in self.spec_index:
                    file_errors.append(f"Dependencia rota: '{real_id}' no existe en el índice de Specs.")

        # 5. Validación Semántica (LST)
        if re.search(r"\bAST\b", content) and not re.search(r"evolución de AST a LST", content, re.IGNORECASE):
            file_errors.append("Vestigio detectado: Se encontró 'AST'. Debe ser 'LST'.")

        # 6. Validación de Context Model (JSON)
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            try:
                model = json.loads(json_match.group(1))
                
                # Check personality and ledger refs
                for ref_key in ['personality_ref', 'ledger_link']:
                    if ref_key in model:
                        ref_id = model[ref_key]
                        if ref_id not in self.spec_index:
                            file_errors.append(f"Referencia de Gobernanza rota: {ref_key}='{ref_id}' no encontrada.")
                
                # Check Protobuf consistency
                if 'messages' in model and isinstance(model['messages'], list):
                    for msg in model['messages']:
                        if msg not in self.proto_entities and not msg.startswith("LociMapper") and not msg.startswith("MuscleService"):
                            clean_msg = re.sub(r'\s*\(.*?\)', '', msg)
                            if clean_msg not in self.proto_entities:
                                file_errors.append(f"Inconsistencia Proto: El mensaje '{msg}' no está definido en los archivos .proto.")

            except json.JSONDecodeError as e:
                file_errors.append(f"JSON malformado: {e}")
        else:
            # MSA: Si existe el archivo hermano .rules.json, el bloque inline es opcional
            rules_file = Path(file_path).with_suffix('.rules.json')
            if not rules_file.exists():
                file_errors.append("Falta bloque de código JSON con el Cognitive Context Model (o archivo hermano .rules.json).")

        # 7. Validación de Bloques Gherkin (BDD Check) en la spec o archivo hermano
        feature_file = Path(file_path).with_suffix('.feature')
        if feature_file.exists():
            with open(feature_file, 'r') as f:
                feature_content = f.read()
                if "Performance Metric:" not in feature_content:
                    file_errors.append("MSA Alert: El archivo .feature no contiene métricas de rendimiento (Performance Metric:)")
                
                # Validar sintaxis de métricas: key < value
                if not re.search(r'Performance Metric: [\w_]+ [<>]=? \d+', feature_content):
                    file_errors.append("MSA Alert: Sintaxis de métrica de rendimiento inválida. Debe ser 'Performance Metric: key <|<=|>=|> value'")

        # 8. Verificación de MSA (Archivos Hermanos)
        msa_errors = self.validate_msa_siblings(file_path, data)
        file_errors.extend(msa_errors)

        return file_errors

    def validate_msa_siblings(self, file_path, data):
        """Verifica la existencia de archivos .feature y .rules.json para el hito Alpha."""
        errors = []
        base_path = Path(file_path).with_suffix('')
        spec_id = data.get('spec_id', 'Unknown')
        
        # MSA es obligatorio para TODAS las capas (L0-L6)
        if True:
            feature_file = base_path.with_suffix('.feature')
            rules_file = base_path.with_suffix('.rules.json')
            
            if not feature_file.exists():
                self.repair_msa_siblings(feature_file, "feature", data)
                errors.append(f"MSA Missing: Se ha generado plantilla .feature para {spec_id}")
            
            if not rules_file.exists():
                self.repair_msa_siblings(rules_file, "rules", data)
                errors.append(f"MSA Missing: Se ha generado plantilla .rules.json para {spec_id}")
                
        return errors

    def repair_msa_siblings(self, target_path, file_type, data):
        """Genera plantillas proactivas para archivos hermanos."""
        spec_id = data.get('spec_id', 'Unknown')
        title = data.get('title', 'Unknown')
        
        if file_type == "feature":
            content = f"""Feature: {title} ({spec_id})
  Criterios de Aceptación Ejecutables para el Swarm de Agentes.

  Scenario: [Insert Scenario Name]
    Given [Initial State]
    When [Action/Event]
    Then [Observable Result]
    And [Performance Metric: e.g. latency < 10ms]
"""
        elif file_type == "rules":
            content = json.dumps({
                "rule_id": f"RULE_{spec_id.replace('-', '_')}",
                "spec_ref": spec_id,
                "invariants": {
                    "forbidden_patterns": [],
                    "required_headers": []
                },
                "enforcement": "STRICT_BLOCK"
            }, indent=2)
            
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[\u2699\ufe0f] MSA Auto-Repair: Creado {target_path.name}")

    def validate_skills_directory(self):
        """Verifica que cada habilidad en el directorio skills/ tenga un SKILL.md y sea válida."""
        skills_dir = os.path.join(PROJECT_ROOT, "skills")
        if not os.path.exists(skills_dir):
            print("[!] Warning: Directorio de habilidades no encontrado.")
            return

        print("\nAuditoría de Habilidades (SKILL.md)...")
        for entry in os.scandir(skills_dir):
            if entry.is_dir():
                skill_file = Path(entry.path) / "SKILL.md"
                rel_path = os.path.relpath(skill_file, PROJECT_ROOT)
                
                if not skill_file.exists():
                    print(f"[\u274c] {rel_path}: Falta SKILL.md en el directorio de la habilidad.")
                    self.errors[rel_path] = ["Falta SKILL.md"]
                else:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Validación básica de YAML en SKILL.md
                    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    if not match:
                        print(f"[\u274c] {rel_path}: Falta Frontmatter YAML.")
                        self.errors[rel_path] = ["Falta Frontmatter YAML"]
                    else:
                        print(f"[\u2705] {rel_path}")

    def run(self):
        print("=== DUMMIE Engine: Semantic Auditor (SDD V3) ===")
        print("Cargando contratos Protobuf...")
        self.load_proto_entities()
        print(f"Entidades Proto detectadas: {len(self.proto_entities)}")
        
        print("Indexando especificaciones...")
        self.index_specs()
        print(f"Specs indexadas: {len(self.spec_index)}")
        
        print("\nIniciando auditoría de integridad...\n")
        
        for root, _, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith(".md"):
                    self.total_scanned += 1
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, PROJECT_ROOT)
                    
                    errors = self.validate_file(path)
                    if errors:
                        self.errors[rel_path] = errors
                        print(f"[\u274c] {rel_path}")
                        for err in errors:
                            print(f"    - {err}")
                    else:
                        print(f"[\u2705] {rel_path}")

        # 9. Verificación de Directorio de Habilidades (SKILL.md)
        self.validate_skills_directory()

        print("\n=== Resumen de Auditoría Semántica ===")
        print(f"Total analizados: {self.total_scanned}")
        print(f"Válidos: {self.total_scanned - len(self.errors)}")
        print(f"Inválidos: {len(self.errors)}")
        
        if self.errors:
            print("\n[!] FALLA CRÍTICA: La base de conocimiento está desincronizada.")
            sys.exit(1)
        else:
            print("\n[OK] Integridad semántica garantizada. SFE lista para producción.")
            sys.exit(0)

if __name__ == "__main__":
    auditor = SDDSemanticAuditor()
    auditor.run()
