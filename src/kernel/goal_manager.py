import os
import re
import json
import time
import hashlib
from pathlib import Path

# Safe dynamic import of EventBus and TelemetryEngine
try:
    from kernel.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self, workspace_path, telemetry=None):
            self.workspace_path = workspace_path
        def publish(self, event_type, publisher, payload, priority="NORMAL"):
            pass

try:
    from kernel.telemetry import TelemetryEngine
except ImportError:
    class TelemetryEngine:
        def __init__(self, workspace_path):
            self.workspace_path = workspace_path
        def log_stage_start(self, session_id, stage, metadata=None):
            pass
        def log_stage_complete(self, session_id, stage, duration_ms, metadata=None):
            pass
        def log_stage_failed(self, session_id, stage, error, duration_ms):
            pass

# ======================================================================
# COMPILER INTERFACES
# ======================================================================

class Compiler:
    def compile(self, workspace_path: str) -> bool:
        raise NotImplementedError
        
    def update(self, changed_files: list[str], deleted_files: list[str]) -> bool:
        raise NotImplementedError
        
    def query(self, query_string: str, params: dict = None) -> list:
        raise NotImplementedError
        
    def diagnostics(self) -> dict:
        raise NotImplementedError
        
    def validate(self) -> bool:
        raise NotImplementedError
        
    def benchmark(self) -> dict:
        raise NotImplementedError

    def export(self, format_type: str, dest_path: str) -> bool:
        raise NotImplementedError


class BaseCompilerPlugin:
    def initialize(self, config: dict) -> None:
        pass
        
    def discover(self, file_path: Path) -> bool:
        return False
        
    def lex(self, file_content: str) -> list[dict]:
        return []
        
    def parse(self, tokens: list[dict]) -> dict:
        return {}
        
    def semantic(self, ast: dict) -> dict:
        return {}
        
    def relationships(self, ast: dict) -> list[dict]:
        return []
        
    def validate(self, schema: dict) -> bool:
        return True
        
    def cleanup(self) -> None:
        pass

# ======================================================================
# INTERNAL DATA MODELS
# ======================================================================

class Symbol:
    def __init__(self, symbol_id, name, kind, source, metadata=None):
        self.id = symbol_id
        self.name = name
        self.kind = kind
        self.source = source
        self.metadata = metadata or {}
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "source": self.source,
            "metadata": self.metadata
        }


class KnowledgeNode:
    def __init__(self, node_id, node_type, metadata=None):
        self.id = node_id
        self.type = node_type
        self.metadata = metadata or {}
        
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "metadata": self.metadata
        }


class Relationship:
    def __init__(self, source, target, relationship_type, metadata=None):
        self.source = source
        self.target = target
        self.relationship = relationship_type
        self.metadata = metadata or {}
        
    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "metadata": self.metadata
        }


class EngineeringGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        
    def add_node(self, node_id, node_type, metadata=None):
        if node_id in self.nodes:
            self.nodes[node_id].metadata.update(metadata or {})
        else:
            self.nodes[node_id] = KnowledgeNode(node_id, node_type, metadata)
            
    def add_edge(self, source, target, relationship_type, metadata=None):
        if source not in self.nodes:
            self.add_node(source, "Unknown")
        if target not in self.nodes:
            node_type = "Unknown"
            if target.startswith("import:"):
                node_type = "Import"
            elif target.startswith("table:"):
                node_type = "Table"
            elif target.startswith("persona:"):
                node_type = "Persona"
            elif target.startswith("rule:"):
                node_type = "Rule"
            elif target.startswith("feature:"):
                node_type = "Feature"
            self.add_node(target, node_type)
            
        for edge in self.edges:
            if edge.source == source and edge.target == target and edge.relationship == relationship_type:
                edge.metadata.update(metadata or {})
                return
                
        self.edges.append(Relationship(source, target, relationship_type, metadata))
        
    def prune_file_nodes(self, rel_path):
        node_id = f"file:{rel_path}"
        if node_id in self.nodes:
            del self.nodes[node_id]
        
        # Prune edges involving this node
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]
        
    def to_dict(self):
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

# ======================================================================
# KNOWLEDGE BASE STORAGE LAYER
# ======================================================================

class EngineeringKnowledgeBase:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.knowledge_dir = self.workspace_path / ".aetheris" / "knowledge"
        
    def save_artifact(self, name: str, data: dict) -> None:
        try:
            self.knowledge_dir.mkdir(parents=True, exist_ok=True)
            dest_file = self.knowledge_dir / f"{name}.json"
            dest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
            
    def load_artifact(self, name: str) -> dict:
        dest_file = self.knowledge_dir / f"{name}.json"
        if not dest_file.exists():
            return {}
        try:
            return json.loads(dest_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

# ======================================================================
# COMPILER PLUGINS (LANGUAGE ADAPTERS)
# ======================================================================

class PythonAdapter(BaseCompilerPlugin):
    def discover(self, file_path: Path) -> bool:
        return file_path.suffix == ".py"
        
    def lex(self, file_content: str) -> list[dict]:
        # Level 1: Extraction of raw tokens/imports using regex
        tokens = []
        # Find imports
        matches = re.finditer(r"^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)", file_content, re.MULTILINE)
        for m in matches:
            tokens.append({
                "type": "IMPORT",
                "value": m.group(1).split(".")[0],
                "start": m.start(),
                "end": m.end()
            })
        # Level 2: Find Class & Function definitions
        matches = re.finditer(r"^\s*class\s+(\w+)", file_content, re.MULTILINE)
        for m in matches:
            tokens.append({
                "type": "CLASS",
                "value": m.group(1),
                "start": m.start(),
                "end": m.end()
            })
        matches = re.finditer(r"^\s*def\s+(\w+)", file_content, re.MULTILINE)
        for m in matches:
            tokens.append({
                "type": "FUNCTION",
                "value": m.group(1),
                "start": m.start(),
                "end": m.end()
            })
        return tokens
        
    def parse(self, tokens: list[dict]) -> dict:
        ast = {"imports": [], "classes": [], "functions": []}
        for t in tokens:
            if t["type"] == "IMPORT":
                ast["imports"].append(t["value"])
            elif t["type"] == "CLASS":
                ast["classes"].append(t["value"])
            elif t["type"] == "FUNCTION":
                ast["functions"].append(t["value"])
        return ast
        
    def semantic(self, ast: dict) -> dict:
        # Level 3: Semantic evaluation
        return {
            "symbols": [
                {"name": c, "kind": "class", "metadata": {}} for c in ast["classes"]
            ] + [
                {"name": f, "kind": "function", "metadata": {}} for f in ast["functions"]
            ],
            "imports": ast["imports"]
        }
        
    def relationships(self, ast: dict) -> list[dict]:
        relations = []
        for imp in ast["imports"]:
            relations.append({
                "target": f"import:{imp}",
                "relationship": "depends_on"
            })
        return relations


class MarkdownAdapter(BaseCompilerPlugin):
    def discover(self, file_path: Path) -> bool:
        return file_path.suffix in (".md", ".txt")
        
    def lex(self, file_content: str) -> list[dict]:
        tokens = []
        lines = file_content.splitlines()
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                tokens.append({"type": "HEADER", "value": stripped, "line": idx})
            elif stripped.startswith("-") or stripped.startswith("*") or re.match(r"^\d+\.", stripped):
                tokens.append({"type": "LIST_ITEM", "value": stripped, "line": idx})
        return tokens
        
    def parse(self, tokens: list[dict]) -> dict:
        ast = {"personas": [], "rules": [], "features": []}
        current_section = None
        
        section_patterns = {
            "personas": [r"#+.*?persona", r"#+.*?user.*?journey", r"#+.*?target.*?user"],
            "rules": [r"#+.*?business.*?rule", r"#+.*?logic.*?constraint", r"#+.*?rule"],
            "features": [r"#+.*?feature", r"#+.*?functional.*?requirement"]
        }
        
        for t in tokens:
            if t["type"] == "HEADER":
                current_section = None
                for sec_name, patterns in section_patterns.items():
                    if any(re.search(pat, t["value"], re.IGNORECASE) for pat in patterns):
                        current_section = sec_name
                        break
            elif t["type"] == "LIST_ITEM" and current_section:
                item_text = re.sub(r"^[-*\d\.\s]+", "", t["value"])
                if item_text:
                    ast[current_section].append(item_text)
        return ast
        
    def semantic(self, ast: dict) -> dict:
        symbols = []
        for p in ast["personas"]:
            symbols.append({"name": p, "kind": "persona", "metadata": {}})
        for r in ast["rules"]:
            symbols.append({"name": r, "kind": "rule", "metadata": {}})
        for f in ast["features"]:
            symbols.append({"name": f, "kind": "feature", "metadata": {}})
            
        return {
            "symbols": symbols,
            "personas": ast["personas"],
            "rules": ast["rules"],
            "features": ast["features"]
        }
        
    def relationships(self, ast: dict) -> list[dict]:
        return []


class PrismaAdapter(BaseCompilerPlugin):
    def discover(self, file_path: Path) -> bool:
        return file_path.suffix == ".prisma"
        
    def lex(self, file_content: str) -> list[dict]:
        tokens = []
        matches = re.finditer(r"model\s+(\w+)\s*\{", file_content)
        for m in matches:
            tokens.append({
                "type": "MODEL",
                "value": m.group(1),
                "start": m.start(),
                "end": m.end()
            })
        return tokens
        
    def parse(self, tokens: list[dict]) -> dict:
        return {"models": [t["value"] for t in tokens]}
        
    def semantic(self, ast: dict) -> dict:
        return {
            "symbols": [{"name": m, "kind": "prisma_model", "metadata": {}} for m in ast["models"]],
            "models": ast["models"]
        }
        
    def relationships(self, ast: dict) -> list[dict]:
        relations = []
        for m in ast["models"]:
            relations.append({
                "target": f"table:{m}",
                "relationship": "defines"
            })
        return relations


class SqlAdapter(BaseCompilerPlugin):
    def discover(self, file_path: Path) -> bool:
        return file_path.suffix == ".sql"
        
    def lex(self, file_content: str) -> list[dict]:
        tokens = []
        matches = re.finditer(r"CREATE\s+TABLE\s+(\w+)", file_content, re.IGNORECASE)
        for m in matches:
            tokens.append({
                "type": "TABLE",
                "value": m.group(1),
                "start": m.start(),
                "end": m.end()
            })
        return tokens
        
    def parse(self, tokens: list[dict]) -> dict:
        return {"tables": [t["value"] for t in tokens]}
        
    def semantic(self, ast: dict) -> dict:
        return {
            "symbols": [{"name": t, "kind": "sql_table", "metadata": {}} for t in ast["tables"]],
            "tables": ast["tables"]
        }
        
    def relationships(self, ast: dict) -> list[dict]:
        relations = []
        for t in ast["tables"]:
            relations.append({
                "target": f"table:{t}",
                "relationship": "defines"
            })
        return relations

# ======================================================================
# COMPILER IMPLEMENTATION (EKC CORE)
# ======================================================================

class EngineeringKnowledgeCompiler(Compiler):
    def __init__(self, workspace_path, event_bus=None):
        self.workspace_path = Path(workspace_path).resolve()
        self.event_bus = event_bus if event_bus else EventBus(self.workspace_path)
        self.ekb = EngineeringKnowledgeBase(self.workspace_path)
        
        # Pluggable Language Adapters Registration
        self.plugins = [
            PythonAdapter(),
            MarkdownAdapter(),
            PrismaAdapter(),
            SqlAdapter()
        ]
        
        # Internal state
        self.symbol_table = {"symbols": []}
        self.graph = EngineeringGraph()
        self.fingerprints = {}
        
        # Diagnostic & Timing metrics
        self.timing_metrics = {}
        self.nodes_added_count = 0
        self.nodes_removed_count = 0
        self.edges_added_count = 0
        self.edges_removed_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def _find_files(self):
        found = []
        ignored_dirs = {".git", "node_modules", "venv", ".venv", ".aetheris", "dist", "build", "__pycache__"}
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                rel_path = Path(root).relative_to(self.workspace_path)
                if len(rel_path.parts) >= 3:
                    dirs.clear()
                    continue
                    
                for f in files:
                    fpath = Path(root) / f
                    if f.endswith((".png", ".jpg", ".ico", ".pdf", ".zip", ".tar.gz", ".pyc")):
                        continue
                    found.append(fpath)
        except Exception:
            pass
        return found

    def _calculate_file_hash(self, file_path: Path) -> str:
        try:
            stat = file_path.stat()
            return hashlib.sha256(f"{file_path.name}:{stat.st_size}:{stat.st_mtime}".encode()).hexdigest()
        except Exception:
            return ""

    def compile(self, user_goal: str = "Autonomous software engineering execution") -> bool:
        start_time = time.time()
        self.cache_hits = 0
        self.cache_misses = 0
        self.event_bus.publish("DiscoveryStarted", "EKC", {"workspace": str(self.workspace_path)})
        
        # Load previous metadata & graph
        prev_meta = self.ekb.load_artifact("metadata")
        prev_graph = self.ekb.load_artifact("engineering.graph")
        prev_fingerprints = prev_meta.get("fingerprints", {})
        
        # Load existing graph nodes/edges if present
        if prev_graph:
            for node in prev_graph.get("nodes", []):
                self.graph.add_node(node["id"], node["type"], node.get("metadata"))
            for edge in prev_graph.get("edges", []):
                self.graph.add_edge(edge["source"], edge["target"], edge["relationship"], edge.get("metadata"))
                
        files = self._find_files()
        current_fingerprints = {}
        
        # Track changed & deleted files for incremental compiler
        changed_files = []
        for fpath in files:
            rel_path = str(fpath.relative_to(self.workspace_path))
            fhash = self._calculate_file_hash(fpath)
            current_fingerprints[rel_path] = fhash
            
            if prev_fingerprints.get(rel_path) != fhash:
                changed_files.append(fpath)
                self.cache_misses += 1
            else:
                self.cache_hits += 1
                
        deleted_files = [f for f in prev_fingerprints if f not in current_fingerprints]
        
        # 1. Prune deleted files
        for df in deleted_files:
            self.graph.prune_file_nodes(df)
            self.nodes_removed_count += 1
            
        # 2. Compile changed & new files
        personas = []
        business_rules = []
        features = []
        sql_tables = []
        prisma_models = []
        confidence_scores = {"database": 0.0, "docker": 0.0, "ci_cd": 0.0, "auth": 0.0}
        evidence = []
        
        for fpath in changed_files:
            rel_path = str(fpath.relative_to(self.workspace_path))
            node_id = f"file:{rel_path}"
            
            # Prune previous version of file from graph before adding new parsed representation
            self.graph.prune_file_nodes(rel_path)
            
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
                
            self.graph.add_node(node_id, "File", {"size": fpath.stat().st_size, "suffix": fpath.suffix})
            self.nodes_added_count += 1
            
            # Find plugin
            plugin = None
            for p in self.plugins:
                if p.discover(fpath):
                    plugin = p
                    break
                    
            if plugin:
                try:
                    tokens = plugin.lex(content)
                    ast = plugin.parse(tokens)
                    semantic_data = plugin.semantic(ast)
                    relations = plugin.relationships(ast)
                    
                    # Register Symbols
                    for sym in semantic_data.get("symbols", []):
                        sym_id = f"symbol:{sym['kind']}:{sym['name']}"
                        self.symbol_table["symbols"].append({
                            "id": sym_id,
                            "name": sym["name"],
                            "kind": sym["kind"],
                            "source": rel_path,
                            "metadata": sym.get("metadata", {})
                        })
                        self.graph.add_node(sym_id, sym["kind"].capitalize(), sym.get("metadata"))
                        self.graph.add_edge(node_id, sym_id, "defines")
                        self.nodes_added_count += 1
                        self.edges_added_count += 2
                        
                    # Register Relationships
                    for rel in relations:
                        self.graph.add_edge(node_id, rel["target"], rel["relationship"])
                        self.edges_added_count += 1
                        
                    # Aggregate parser specific lists for backward compatibility output
                    if isinstance(plugin, MarkdownAdapter):
                        for p in semantic_data.get("personas", []):
                            personas.append({"text": p, "source": rel_path})
                        for r in semantic_data.get("rules", []):
                            business_rules.append({"text": r, "source": rel_path})
                        for f in semantic_data.get("features", []):
                            features.append({"text": f, "source": rel_path})
                            
                    elif isinstance(plugin, PrismaAdapter):
                        for m in semantic_data.get("models", []):
                            prisma_models.append({"id": f"table:{m}", "name": m, "source": rel_path})
                            self.graph.add_node(f"table:{m}", "Table", {"name": m})
                            self.graph.add_edge(node_id, f"table:{m}", "defines")
                            
                    elif isinstance(plugin, SqlAdapter):
                        for t in semantic_data.get("tables", []):
                            sql_tables.append({"id": f"table:{t}", "name": t, "source": rel_path})
                            self.graph.add_node(f"table:{t}", "Table", {"name": t})
                            self.graph.add_edge(node_id, f"table:{t}", "defines")
                            
                    self.event_bus.publish("LanguageParsed", "EKC", {"file": rel_path})
                except Exception:
                    pass
            else:
                # Basic non-parsed files logic (e.g. Dockerfile detection)
                if fpath.name == "Dockerfile":
                    confidence_scores["docker"] = 1.0
                    evidence.append(f"Dockerfile detected: {rel_path}")
                elif "docker-compose" in fpath.name:
                    confidence_scores["docker"] = 1.0
                    evidence.append(f"Docker Compose detected: {rel_path}")
                elif ".github/workflows" in rel_path:
                    confidence_scores["ci_cd"] = 1.0
                    evidence.append(f"GitHub Actions detected: {rel_path}")

        # Compute aggregate evidence and database/auth confidence scores
        db_tables = sql_tables + prisma_models
        if db_tables:
            confidence_scores["database"] = 1.0
            sources = list(set([t["source"] for t in db_tables]))
            evidence.append(f"Database models discovered in schemas ({', '.join(sources)}): {[t['name'] for t in db_tables]}")
        else:
            confidence_scores["database"] = 0.5 if "database" in user_goal.lower() or "db" in user_goal.lower() else 0.0
            
        if any("auth" in f["text"].lower() for f in features):
            confidence_scores["auth"] = 1.0
            evidence.append("Authentication feature explicitly specified in markdown requirement lists.")
        else:
            confidence_scores["auth"] = 0.5 if "auth" in user_goal.lower() else 0.0

        # Completeness Analysis
        missing_requirements = []
        if confidence_scores["database"] == 0.0:
            missing_requirements.append("Database schema structure could not be identified.")
        if confidence_scores["auth"] == 0.0:
            missing_requirements.append("User authorization/authentication features are not specified.")
        if confidence_scores["docker"] == 0.0:
            missing_requirements.append("Containerization configurations (Dockerfile) are missing.")
        if confidence_scores["ci_cd"] == 0.0:
            missing_requirements.append("CI/CD pipeline workflows are missing.")
            
        inferred_subsystems = []
        if confidence_scores["database"] > 0:
            inferred_subsystems.append("database_migrations")
        if confidence_scores["auth"] > 0:
            inferred_subsystems.append("authentication")
        inferred_subsystems.extend(["api_controllers", "frontend_views", "unit_testing"])
        if confidence_scores["docker"] > 0:
            inferred_subsystems.append("dockerization")
        if confidence_scores["ci_cd"] > 0:
            inferred_subsystems.append("deployment_pipelines")
            
        blueprint = {
            "target_platform": "Universal Service Engine",
            "vision": user_goal,
            "completeness_requirements": {
                "database": "Required" if confidence_scores["database"] > 0 else "Optional",
                "auth": "Required" if confidence_scores["auth"] > 0 else "Optional",
                "docker": "Required" if confidence_scores["docker"] > 0 else "Optional",
                "ci_cd": "Required" if confidence_scores["ci_cd"] > 0 else "Optional"
            },
            "technology_stack": {
                "database": "PostgreSQL" if confidence_scores["database"] > 0 else "SQLite",
                "frontend": "Next.js",
                "orm": "Prisma" if confidence_scores["database"] > 0 else "None"
            },
            "inferred_subsystems": inferred_subsystems
        }
        
        project_dna = {
            "project_name": "Evolving Codebase",
            "philosophy": "Goal-driven micro-services architecture, high test coverage",
            "design_language": "Minimalist responsive UI components",
            "architectural_style": "Clean MVC / Domain separation",
            "preferred_patterns": ["Repository Pattern", "Zod Validation"],
            "forbidden_patterns": ["Inline CSS modules", "Hardcoded secret variables"]
        }

        # Persist EKB compiled output files
        self.ekb.save_artifact("engineering.graph", self.graph.to_dict())
        self.ekb.save_artifact("universal.blueprint", blueprint)
        self.ekb.save_artifact("product.blueprint", blueprint) # Compatibility wrapper
        self.ekb.save_artifact("project.dna", project_dna)
        self.ekb.save_artifact("symbol.table", self.symbol_table)
        
        # Save EKB Inventories
        self.ekb.save_artifact("project.inventory", {
            "total_files": len(files),
            "fingerprints": current_fingerprints
        })
        self.ekb.save_artifact("dependency.inventory", {
            "symbol_dependencies": self.symbol_table
        })
        self.ekb.save_artifact("technology.inventory", {
            "confidence_scores": confidence_scores,
            "evidence": evidence
        })
        self.ekb.save_artifact("business.inventory", {
            "personas": personas,
            "rules": business_rules,
            "features": features
        })
        self.ekb.save_artifact("completeness.report", {
            "missing_requirements": missing_requirements
        })
        self.ekb.save_artifact("risk.report", {
            "risks": [
                {"severity": "High" if "missing" in r.lower() else "Medium", "text": r}
                for r in missing_requirements
            ]
        })
        
        # Tech Decisions Logging Integration
        tech_decisions = []
        for topic, choice in blueprint["technology_stack"].items():
            tech_decisions.append({
                "topic": topic,
                "choice": choice,
                "confidence": 1.0 if confidence_scores.get(topic, 0) > 0 else 0.5,
                "reason": f"Discovered environment indicators for {choice}"
            })
        self.ekb.save_artifact("decision.evidence", {"decisions": tech_decisions})
        
        self.ekb.save_artifact("execution.inputs", {
            "user_goal": user_goal,
            "inferred_subsystems": inferred_subsystems
        })

        elapsed_ms = int((time.time() - start_time) * 1000)
        self.timing_metrics = {
            "compile_time_ms": elapsed_ms,
            "cache_hit_ratio": self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        }
        
        # Save compilation metadata
        metadata = {
            "compiler_version": "4.0.0",
            "schema_version": "1.0.0",
            "knowledge_version": 1,
            "workspace_hash": hashlib.sha256(json.dumps(current_fingerprints).encode()).hexdigest(),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fingerprints": current_fingerprints,
            "metrics": self.timing_metrics
        }
        self.ekb.save_artifact("metadata", metadata)
        
        self.event_bus.publish("GraphUpdated", "EKC", {"nodes": len(self.graph.nodes)})
        self.event_bus.publish("KnowledgeUpdated", "EKC", {"status": "SUCCESS"})
        self.event_bus.publish("CompilationFinished", "EKC", {"elapsed_ms": elapsed_ms})
        
        # Save internal cache
        self.fingerprints = current_fingerprints
        
        return True

    def build_engineering_understanding(self, user_goal):
        """Wrapper method for core stage 1 runner compatibility."""
        self.compile(user_goal)
        
        # Load compiled documents from EKB to return
        blueprint = self.ekb.load_artifact("universal.blueprint")
        project_dna = self.ekb.load_artifact("project.dna")
        biz_inventory = self.ekb.load_artifact("business.inventory")
        tech_inventory = self.ekb.load_artifact("technology.inventory")
        completeness = self.ekb.load_artifact("completeness.report")
        
        # Re-map prisma/sql tables for database_entities compatibility checks
        sql_tables = []
        prisma_models = []
        for sym in self.symbol_table["symbols"]:
            if sym["kind"] == "prisma_model":
                prisma_models.append({"name": sym["name"], "source": sym["source"]})
            elif sym["kind"] == "sql_table":
                sql_tables.append({"name": sym["name"], "source": sym["source"]})
                
        return {
            "graph": self.graph.to_dict(),
            "blueprint": blueprint,
            "project_dna": project_dna,
            "user_personas": biz_inventory.get("personas", []),
            "business_rules": biz_inventory.get("rules", []),
            "feature_inventory": biz_inventory.get("features", []),
            "database_entities": {
                "sql_tables": sql_tables,
                "prisma_models": prisma_models
            },
            "confidence_scores": tech_inventory.get("confidence_scores", {}),
            "missing_requirements": completeness.get("missing_requirements", []),
            "evidence": tech_inventory.get("evidence", [])
        }

    # Public API Implementation
    def update(self, changed_files: list[str], deleted_files: list[str]) -> bool:
        # Simple implementation using incremental scan mapping
        return self.compile()
        
    def query(self, query_string: str, params: dict = None) -> list:
        # Structured queries interface
        results = []
        if query_string == "get_dependencies":
            node_id = params.get("node_id") if params else None
            for edge in self.graph.edges:
                if edge.source == node_id:
                    results.append(edge.target)
        elif query_string == "get_dependents":
            node_id = params.get("node_id") if params else None
            for edge in self.graph.edges:
                if edge.target == node_id:
                    results.append(edge.source)
        elif query_string == "get_database_models":
            for sym in self.symbol_table["symbols"]:
                if sym["kind"] in ("prisma_model", "sql_table"):
                    results.append(sym["name"])
        elif query_string == "get_risks":
            report = self.ekb.load_artifact("risk.report")
            results = report.get("risks", [])
        elif query_string == "get_incomplete_features":
            report = self.ekb.load_artifact("completeness.report")
            results = report.get("missing_requirements", [])
        return results
        
    def diagnostics(self) -> dict:
        return {
            "nodes_count": len(self.graph.nodes),
            "edges_count": len(self.graph.edges),
            "timing_metrics": self.timing_metrics,
            "cache_stats": {
                "hits": self.cache_hits,
                "misses": self.cache_misses
            }
        }
        
    def validate(self) -> bool:
        # Structural reference checks
        for edge in self.graph.edges:
            if edge.source not in self.graph.nodes or edge.target not in self.graph.nodes:
                return False
        return True
        
    def benchmark(self) -> dict:
        start = time.time()
        self.compile()
        elapsed = time.time() - start
        return {"compile_duration_seconds": elapsed}

    def export(self, format_type: str, dest_path: str) -> bool:
        if format_type == "json":
            try:
                dest = Path(dest_path)
                dest.write_text(json.dumps(self.graph.to_dict(), indent=2), encoding="utf-8")
                return True
            except Exception:
                return False
        return False

# Compatibility bindings
EngineeringKnowledgeCompiler.expand_goal = EngineeringKnowledgeCompiler.build_engineering_understanding
UniversalEngineeringUnderstandingEngine = EngineeringKnowledgeCompiler
GoalManager = EngineeringKnowledgeCompiler
