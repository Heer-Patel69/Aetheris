import re
from pathlib import Path
from typing import Dict, Any, List, Set

class ContextOptimizer:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()

    def optimize_context(
        self,
        task_desc: str,
        available_files: List[Dict[str, Any]],
        available_skills: List[str] = None,
        available_specs: List[str] = None,
        available_rfcs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compress context using heuristics to only include items relevant to the task description.
        """
        available_skills = available_skills or []
        available_specs = available_specs or []
        available_rfcs = available_rfcs or []
        
        # Tokenize task keywords
        keywords = set(re.findall(r"\w+", task_desc.lower()))
        keywords = {k for k in keywords if len(k) > 3}
        
        # 1. Feature/Capability/Domain discovery
        is_database_task = any(k in keywords for k in ["db", "database", "schema", "sql", "migration", "postgres", "sqlite"])
        is_testing_task = any(k in keywords for k in ["test", "testing", "pytest", "unittest", "assert"])
        is_security_task = any(k in keywords for k in ["security", "auth", "encrypt", "jwt", "login", "cybersecurity"])
        is_performance_task = any(k in keywords for k in ["performance", "benchmark", "speed", "latency", "optimize"])
        is_frontend_task = any(k in keywords for k in ["frontend", "web", "html", "css", "js", "react", "view"])
        
        # 2. Skill Discovery & Selection
        selected_skills = []
        for skill in available_skills:
            skill_lower = skill.lower()
            relevance = 0
            if is_database_task and "database" in skill_lower: relevance += 10
            if is_testing_task and "test" in skill_lower: relevance += 10
            if is_security_task and "security" in skill_lower: relevance += 10
            if is_performance_task and "performance" in skill_lower: relevance += 10
            if is_frontend_task and ("frontend" in skill_lower or "ui" in skill_lower): relevance += 10
            
            # Keyword matching
            relevance += sum(2 for k in keywords if k in skill_lower)
            if relevance > 0 or not keywords:
                selected_skills.append(skill)
                
        # 3. RFC & SPEC Discovery & Selection
        selected_rfcs = []
        for rfc in available_rfcs:
            rfc_lower = rfc.lower()
            relevance = sum(2 for k in keywords if k in rfc_lower)
            if relevance > 0 or not keywords:
                selected_rfcs.append(rfc)
                
        selected_specs = []
        for spec in available_specs:
            spec_lower = spec.lower()
            relevance = sum(2 for k in keywords if k in spec_lower)
            if relevance > 0 or not keywords:
                selected_specs.append(spec)
                
        # 4. Context File Filtering & Compression
        selected_files = []
        ignored_files = []
        
        for file_item in available_files:
            file_path = Path(file_item["path"])
            file_name = file_path.name.lower()
            content = file_item.get("content", "")
            
            # Calculate match score
            score = 0
            # Extension match
            if is_testing_task and "test" in file_name: score += 15
            if is_database_task and ("db" in file_name or "schema" in file_name or "sql" in file_name): score += 15
            
            # Keyword matching
            score += sum(5 for k in keywords if k in file_name)
            score += sum(1 for k in keywords if k in content.lower()[:2000])
            
            if score > 0 or not keywords:
                # Context compression: if file is large (> 20KB), remove comments or extract signature outline
                compressed_content = content
                if len(content) > 10000:
                    # Basic duplicate line removal & whitespace normalization
                    lines = content.splitlines()
                    seen_lines = set()
                    unique_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        # Deduplicate repeated comments/markers
                        if stripped.startswith("#") or stripped.startswith("//"):
                            if stripped in seen_lines:
                                continue
                            seen_lines.add(stripped)
                        unique_lines.append(line)
                    compressed_content = "\n".join(unique_lines)
                
                selected_files.append({
                    "path": file_item["path"],
                    "content": compressed_content,
                    "relevance_score": score
                })
            else:
                ignored_files.append(file_item["path"])
                
        # Estimate context reduction efficiency
        original_size = sum(len(f.get("content", "")) for f in available_files)
        optimized_size = sum(len(f["content"]) for f in selected_files)
        reduction_ratio = round((1 - (optimized_size / max(original_size, 1))) * 100, 2)
        
        return {
            "task": task_desc,
            "selected_skills": selected_skills,
            "selected_rfcs": selected_rfcs,
            "selected_specs": selected_specs,
            "selected_files": selected_files,
            "ignored_files_count": len(ignored_files),
            "original_size_chars": original_size,
            "optimized_size_chars": optimized_size,
            "reduction_percentage": max(reduction_ratio, 0.0)
        }
