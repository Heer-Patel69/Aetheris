import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import psutil


class KernelController:
    """Manages the Aetheris background daemon lifecycle via PID file tracking."""

    def __init__(self):
        self.runtime_dir = Path("~/.aetheris/runtime").expanduser()
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file = self.runtime_dir / "kernel_daemon.pid"

    def spawn_daemon(self) -> int:
        """Spawns a background HTTP server daemon on port 8448."""
        if self.is_running():
            return self.get_active_pid()

        # Spawns localized HTTP environment simulation on port 8448
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS

        proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8448"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getcwd(),
            **kwargs
        )

        with open(self.pid_file, "w", encoding="utf-8") as f:
            f.write(str(proc.pid))
        return proc.pid

    def terminate_daemon(self) -> bool:
        """Safely stops the active daemon and its child process tree."""
        pid = self.get_active_pid()
        if not pid:
            return False
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()

            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
        except (psutil.NoSuchProcess, ProcessLookupError):
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True

    def is_running(self) -> bool:
        """Check if the daemon process is currently alive."""
        pid = self.get_active_pid()
        if not pid:
            return False
        return psutil.pid_exists(pid)

    def get_active_pid(self) -> Optional[int]:
        """Read the stored PID from the pid file, if it exists."""
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except (ValueError, OSError):
            return None
