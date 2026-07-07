import os
import sys
import json
import time
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class ProxyAdapter:
    """
    Manages the lifecycle of the Headroom context compression proxy server daemon.
    Configures and enforces SmartCrusher policies to compress logs/JSONs while
    preserving source code integrity.
    """

    def __init__(self, workspace_path: str, port: int = 8787):
        self.workspace_root = Path(workspace_path).resolve()
        self.port = port
        self.pid_file = self.workspace_root / ".aetheris" / "runtime" / "headroom_proxy.pid"
        self.process: Optional[subprocess.Popen] = None

    def start_proxy(self) -> int:
        """Spawns the Headroom proxy server in the background."""
        import sys
        if self.is_running():
            return self.get_active_pid()

        self.pid_file.parent.mkdir(parents=True, exist_ok=True)

        # Spawns headroom proxy. Try global command first, then fallback to python module
        cmd = ["headroom", "proxy", "--port", str(self.port)]
        
        # If headroom isn't globally in path, fall back to running it via python
        # as the pip package 'headroom-ai' registers the command line tool.
        import shutil
        if not shutil.which("headroom"):
            cmd = [sys.executable, "-m", "headroom.cli", "proxy", "--port", str(self.port)]

        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(self.workspace_root),
                **kwargs
            )
            with open(self.pid_file, "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
            self.process = proc
            return proc.pid
        except Exception as e:
            import sys
            sys.stderr.write(f"Error starting Headroom proxy: {e}\n")
            return 0

    def stop_proxy(self) -> bool:
        """Stops the active Headroom proxy server process."""
        pid = self.get_active_pid()
        if not pid:
            return False
        
        try:
            import psutil
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
        except Exception:
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True

    def get_active_pid(self) -> Optional[int]:
        """Reads the active Headroom proxy process ID."""
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, OSError):
            return None

    def is_running(self) -> bool:
        """Check if the Headroom proxy process is alive and port is open."""
        pid = self.get_active_pid()
        if not pid:
            return False
        
        # Verify port is bound
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", self.port))
            s.close()
            return True
        except socket.error:
            s.close()
            return False

    def get_proxy_env(self) -> Dict[str, str]:
        """Returns proxy environment configurations for redirecting requests."""
        proxy_url = f"http://127.0.0.1:{self.port}"
        return {
            "HTTP_PROXY": proxy_url,
            "HTTPS_PROXY": proxy_url,
            "http_proxy": proxy_url,
            "https_proxy": proxy_url,
            "HEADROOM_OUTPUT_SHAPER": "1"
        }

    def apply_smart_crusher_rules(self, text: str) -> str:
        """
        SmartCrusher context rules engine:
        Compresses logs, shell outputs, and heavy JSON payloads.
        Source code blocks are bypassed with 0% compression.
        """
        if not text:
            return text

        # Parse text into code block vs non-code block segments
        lines = text.splitlines()
        output_lines = []
        in_code_block = False
        code_block_lang = ""
        current_block = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block - process body
                    block_content = "\n".join(current_block)
                    # Keep source code untouched (0% compression)
                    if code_block_lang in ["python", "javascript", "typescript", "go", "rust", "cpp", "java", "css", "html"]:
                        output_lines.append(f"```{code_block_lang}\n{block_content}\n```")
                    else:
                        # Heavy JSON, logs, or shell output inside code blocks gets compressed
                        compressed = self._compress_block(block_content, code_block_lang)
                        output_lines.append(f"```{code_block_lang}\n{compressed}\n```")
                    in_code_block = False
                    current_block = []
                else:
                    # Start of code block
                    in_code_block = True
                    code_block_lang = line.strip().replace("```", "").strip().lower()
            elif in_code_block:
                current_block.append(line)
            else:
                output_lines.append(line)

        return "\n".join(output_lines)

    def _compress_block(self, content: str, lang: str) -> str:
        """Helper to compress log/JSON payloads by summarizing redundant lines."""
        if lang == "json":
            try:
                # Compress JSON spacing/formatting
                data = json.loads(content)
                # Keep keys, truncate large arrays/lists to save tokens
                data_cleaned = self._truncate_large_structures(data)
                return json.dumps(data_cleaned, separators=(',', ':'))
            except Exception:
                pass
        
        # Line-level compression for logs and shell commands
        lines = content.splitlines()
        if len(lines) > 15:
            # Extract start, end and a summary of intermediate repeating logs
            summary = [f"[Aetheris Proxy: Compressed {len(lines) - 8} lines of redundant log telemetry]"]
            return "\n".join(lines[:4] + summary + lines[-4:])
        
        return content

    def _truncate_large_structures(self, obj: Any) -> Any:
        """Recursively trims very large lists/dicts to minimize context payload sizes."""
        if isinstance(obj, dict):
            return {k: self._truncate_large_structures(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            if len(obj) > 5:
                return [self._truncate_large_structures(item) for item in obj[:3]] + ["[Truncated by SmartCrusher Proxy]"] + [self._truncate_large_structures(obj[-1])]
            return [self._truncate_large_structures(item) for item in obj]
        return obj
