import os
import sys
import json
import socket
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from kernel.providers.base import CompressionCapability

class HeadroomProvider(CompressionCapability):
    """
    Concrete capability provider mapping the 'compression' capability to Headroom.
    Manages background Headroom proxy server daemon lifecycles and applies SmartCrusher rules.
    """

    def __init__(self, workspace_path: str, port: int = 8787):
        self.workspace_root = Path(workspace_path).resolve()
        self.port = port
        self.pid_file = self.workspace_root / ".aetheris" / "state" / "headroom_proxy.pid"
        self.process: Optional[subprocess.Popen] = None
        self._status = "stopped"

    def initialize(self, config: Dict[str, Any]) -> None:
        if "port" in config:
            self.port = int(config["port"])
        self.pid_file = self.workspace_root / ".aetheris" / "state" / "headroom_proxy.pid"

    def start(self) -> bool:
        """Spawns the Headroom proxy server in the background."""
        if self.is_running():
            self._status = "running"
            return True

        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build headroom command
        cmd = ["headroom", "proxy", "--port", str(self.port)]
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
            self._status = "running"
            return True
        except Exception as e:
            sys.stderr.write(f"Error starting Headroom proxy: {e}\n")
            self._status = "error"
            return False

    def stop(self) -> bool:
        """Stops the active Headroom proxy server process."""
        pid = self.get_active_pid()
        if not pid:
            self._status = "stopped"
            return False
        
        try:
            import psutil
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            
            if self.pid_file.exists():
                self.pid_file.unlink()
            self._status = "stopped"
            return True
        except Exception:
            if self.pid_file.exists():
                self.pid_file.unlink()
            self._status = "stopped"
            return True

    def get_status(self) -> str:
        if self.is_running():
            return "running"
        return "stopped"

    def get_active_pid(self) -> Optional[int]:
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, OSError):
            return None

    def is_running(self) -> bool:
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
        proxy_url = f"http://127.0.0.1:{self.port}"
        return {
            "HTTP_PROXY": proxy_url,
            "HTTPS_PROXY": proxy_url,
            "http_proxy": proxy_url,
            "https_proxy": proxy_url,
            "HEADROOM_OUTPUT_SHAPER": "1"
        }

    def compress(self, text: str) -> str:
        """
        SmartCrusher context rules engine:
        Compresses logs, shell outputs, and heavy JSON payloads.
        Source code blocks are bypassed with 0% compression.
        """
        if not text:
            return text

        lines = text.splitlines()
        output_lines = []
        in_code_block = False
        code_block_lang = ""
        current_block = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    block_content = "\n".join(current_block)
                    if code_block_lang in ["python", "javascript", "typescript", "go", "rust", "cpp", "java", "css", "html"]:
                        output_lines.append(f"```{code_block_lang}\n{block_content}\n```")
                    else:
                        compressed = self._compress_block(block_content, code_block_lang)
                        output_lines.append(f"```{code_block_lang}\n{compressed}\n```")
                    in_code_block = False
                    current_block = []
                else:
                    in_code_block = True
                    code_block_lang = line.strip().replace("```", "").strip().lower()
            elif in_code_block:
                current_block.append(line)
            else:
                output_lines.append(line)

        return "\n".join(output_lines)

    def _compress_block(self, content: str, lang: str) -> str:
        if lang == "json":
            try:
                data = json.loads(content)
                data_cleaned = self._truncate_large_structures(data)
                return json.dumps(data_cleaned, separators=(',', ':'))
            except Exception:
                pass
        
        lines = content.splitlines()
        if len(lines) > 15:
            summary = [f"[Aetheris Proxy: Compressed {len(lines) - 8} lines of redundant log telemetry]"]
            return "\n".join(lines[:4] + summary + lines[-4:])
        
        return content

    def _truncate_large_structures(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._truncate_large_structures(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            if len(obj) > 5:
                return [self._truncate_large_structures(item) for item in obj[:3]] + ["[Truncated by SmartCrusher Proxy]"] + [self._truncate_large_structures(obj[-1])]
            return [self._truncate_large_structures(item) for item in obj]
        return obj
