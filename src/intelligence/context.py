import os
import re
import sys
import json
from pathlib import Path
from kernel.utils import is_safe_path, redact_secrets, initialize_perimeter

class ContextEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        initialize_perimeter(self.workspace_path)
        
    def _estimate_tokens(self, text):
        """
        Regex-based token estimation (character count / 4 plus weights for code syntax) (ADR-009).
        """
        if not text:
            return 0
        char_count = len(text)
        # Approximate tokens in code: typically 3.5 characters per token
        return int(char_count / 3.5)

    def _compress_file(self, content, extension):
        """
        Compresses large source files by extracting only import/export signatures (ADR-001).
        """
        lines = content.splitlines()
        compressed_lines = []
        
        # Simple syntax matcher for signature extraction (JS/TS, Python)
        signature_patterns = [
            re.compile(r"^(import|export|class|def|function|interface|const\s+[a-zA-Z0-9_]+\s*=)\s+"),
            re.compile(r"^[a-zA-Z0-9_]+\s*\(.*\)\s*\{"), # class methods
        ]
        
        for line in lines:
            stripped = line.strip()
            # Retain imports, exports, functions, and class declarations
            if any(pat.match(stripped) for pat in signature_patterns):
                compressed_lines.append(line)
            elif stripped.startswith("import ") or stripped.startswith("from "):
                compressed_lines.append(line)
                
        if not compressed_lines:
            # Fallback: keep first 50 lines
            return "\n".join(lines[:50]) + "\n... [Truncated due to size]"
            
        return "\n".join(compressed_lines) + "\n... [Interface Signatures Extracted]"

    def _calculate_relevance(self, file_name, file_content, task_keywords):
        """
        Calculate simple keyword overlap score for relevance ranking.
        """
        score = 0
        file_name_lower = file_name.lower()
        content_lower = file_content.lower()
        
        for keyword in task_keywords:
            if keyword in file_name_lower:
                score += 50
            # Term frequency score
            score += content_lower.count(keyword)
            
        return score

    def build_context_package(self, task_desc, max_tokens=20000):
        """
        Finds relevant files, estimates tokens, compresses large items, and returns package.
        """
        if not is_safe_path(self.workspace_path):
            raise PermissionError(f"Security Boundary Violation: Path {self.workspace_path} is out of bounds.")
            
        task_keywords = [word.lower() for word in re.findall(r"\w+", task_desc) if len(word) > 3]
        
        candidates = []
        
        # Traverse workspace up to depth 2
        for root, dirs, files in os.walk(self.workspace_path):
            # Enforce depth ceiling (same as scanner)
            rel_path = Path(root).relative_to(self.workspace_path)
            if len(rel_path.parts) >= 2:
                dirs.clear()
                continue
                
            # Filter out ignored folders
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".aetheris"}]
            
            for f in files:
                file_path = Path(root) / f
                # Skip binaries/images/build files
                if f.endswith((".png", ".jpg", ".ico", ".pdf", ".zip", ".tar.gz", "lock", ".jsonl")):
                    continue
                    
                if not is_safe_path(file_path):
                    continue
                    
                try:
                    # Check size before reading
                    stat = file_path.stat()
                    if stat.st_size > 500 * 1024: # Skip files larger than 500KB
                        continue
                        
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file_handle:
                        content = file_handle.read()
                        
                    relevance = self._calculate_relevance(f, content, task_keywords)
                    if relevance > 0 or len(candidates) < 5: # Include some context fallback
                        candidates.append({
                            "path": str(file_path),
                            "name": f,
                            "size": stat.st_size,
                            "content": content,
                            "relevance": relevance,
                            "extension": file_path.suffix
                        })
                except Exception:
                    pass
                    
        # Sort by relevance descending
        candidates.sort(key=lambda x: x["relevance"], reverse=True)
        
        selected_files = []
        total_tokens = 0
        
        for item in candidates:
            content = item["content"]
            # Compress if size exceeds 20KB
            if len(content) > 20 * 1024:
                content = self._compress_file(content, item["extension"])
                
            tokens = self._estimate_tokens(content)
            
            # Redact secrets before packaging
            scrubbed_content = redact_secrets(content)
            
            if total_tokens + tokens <= max_tokens:
                selected_files.append({
                    "path": str(Path(item["path"]).relative_to(self.workspace_path)),
                    "content": scrubbed_content,
                    "tokens": tokens
                })
                total_tokens += tokens
            else:
                # Stop if budget full
                break
                
        return {
            "workspace_root": str(self.workspace_path),
            "estimated_total_tokens": total_tokens,
            "context_files": selected_files
        }

if __name__ == "__main__":
    if len(sys.argv) < 5 or "--workspace" not in sys.argv or "--task" not in sys.argv:
        sys.stderr.write("Usage: python context.py --workspace <path> --task <description>\n")
        sys.exit(1)
        
    workspace = None
    task = None
    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--workspace" and i+1 < len(sys.argv):
            workspace = sys.argv[i+1]
        elif sys.argv[i] == "--task" and i+1 < len(sys.argv):
            task = sys.argv[i+1]
            
    engine = ContextEngine(workspace)
    pkg = engine.build_context_package(task)
    print(json.dumps(pkg, indent=2))