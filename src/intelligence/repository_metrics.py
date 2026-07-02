import os
from pathlib import Path
from typing import Dict, Any, List

class RepositoryMetrics:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        
    def calculate_metrics(self, files_used_paths: List[str] = None) -> Dict[str, Any]:
        """
        Scan workspace and calculate all repository metrics and coverage scores.
        """
        files_used_paths = files_used_paths or []
        files_used_basenames = {Path(p).name for p in files_used_paths}
        
        total_files = 0
        total_bytes = 0
        
        # Scanned files counts by folder
        skills_scanned = 0
        rfcs_scanned = 0
        specs_scanned = 0
        tests_scanned = 0
        docs_scanned = 0
        src_scanned = 0
        
        # Usage tracking
        skills_used = 0
        rfcs_used = 0
        specs_used = 0
        
        # Coverage checks
        has_architecture = False
        has_security = False
        has_testing = False
        has_docs = False
        has_database = False
        has_backend = False
        has_frontend = False
        has_deployment = False
        has_accessibility = False
        has_performance = False
        
        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", ".pytest_cache", "__pycache__"}]
            rel_root = Path(root).relative_to(self.workspace_path)
            
            for f in files:
                file_path = Path(root) / f
                try:
                    stat = file_path.stat()
                    total_bytes += stat.st_size
                    total_files += 1
                except Exception:
                    continue
                
                # Identify folder mapping
                parts = rel_root.parts
                is_used = f in files_used_basenames or str(file_path.relative_to(self.workspace_path)) in files_used_paths
                
                if "skills" in parts:
                    skills_scanned += 1
                    if is_used:
                        skills_used += 1
                elif "rfcs" in parts:
                    rfcs_scanned += 1
                    if is_used:
                        rfcs_used += 1
                elif "specs" in parts:
                    specs_scanned += 1
                    if is_used:
                        specs_used += 1
                elif "tests" in parts:
                    tests_scanned += 1
                elif "docs" in parts:
                    docs_scanned += 1
                elif "src" in parts:
                    src_scanned += 1
                    
                # Coverage detection based on file names / paths
                f_lower = f.lower()
                rel_str = str(file_path.relative_to(self.workspace_path)).lower()
                
                if "architecture" in rel_str or "adr" in rel_str:
                    has_architecture = True
                if "security" in rel_str or "auth" in rel_str:
                    has_security = True
                if "test" in f_lower or "tests" in parts:
                    has_testing = True
                if "readme" in f_lower or "doc" in rel_str:
                    has_docs = True
                if "db" in f_lower or "schema" in f_lower or "sql" in f_lower or "database" in rel_str:
                    has_database = True
                if "backend" in rel_str or "src/kernel" in rel_str or "src/intelligence" in rel_str:
                    has_backend = True
                if "frontend" in rel_str or "web" in rel_str or "ui" in rel_str:
                    has_frontend = True
                if "deploy" in rel_str or "docker" in f_lower or "ci" in rel_str or "github/workflows" in rel_str:
                    has_deployment = True
                if "accessibility" in rel_str or "wcag" in rel_str:
                    has_accessibility = True
                if "perf" in rel_str or "benchmark" in rel_str:
                    has_performance = True
                    
        # Calculate coverage scores (1 or 0 mapped to percentage)
        coverage_metrics = {
            "repository_coverage": round((len(files_used_paths) / max(total_files, 1)) * 100, 2),
            "skill_coverage": round((skills_used / max(skills_scanned, 1)) * 100, 2),
            "rfc_coverage": round((rfcs_used / max(rfcs_scanned, 1)) * 100, 2),
            "spec_coverage": round((specs_used / max(specs_scanned, 1)) * 100, 2),
            "architecture_coverage": 100.0 if has_architecture else 0.0,
            "security_coverage": 100.0 if has_security else 0.0,
            "testing_coverage": 100.0 if has_testing else 0.0,
            "documentation_coverage": 100.0 if has_docs else 0.0,
            "database_coverage": 100.0 if has_database else 0.0,
            "backend_coverage": 100.0 if has_backend else 0.0,
            "frontend_coverage": 100.0 if has_frontend else 0.0,
            "deployment_coverage": 100.0 if has_deployment else 0.0,
            "accessibility_coverage": 100.0 if has_accessibility else 0.0,
            "performance_coverage": 100.0 if has_performance else 0.0,
        }
        
        # Calculate Overall Engineering Quality Score out of 100
        quality_factors = [
            has_architecture, has_security, has_testing, has_docs, 
            has_database, has_backend, has_frontend, has_deployment,
            has_accessibility, has_performance
        ]
        engineering_score = round((sum(quality_factors) / len(quality_factors)) * 100, 2)
        
        return {
            "repository_size_bytes": total_bytes,
            "total_files": total_files,
            "files_scanned": total_files,
            "files_used": len(files_used_paths),
            "files_ignored": max(total_files - len(files_used_paths), 0),
            "skills_scanned": skills_scanned,
            "skills_used": skills_used,
            "rfcs_scanned": rfcs_scanned,
            "rfcs_used": rfcs_used,
            "specs_scanned": specs_scanned,
            "specs_used": specs_used,
            "coverage": coverage_metrics,
            "engineering_score": engineering_score
        }
