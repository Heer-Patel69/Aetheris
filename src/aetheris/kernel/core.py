"""
Aetheris Kernel Controller — Background Daemon Lifecycle Manager.

Manages the Dashboard Runtime Gateway (DRG) as a persistent background
process that survives parent CLI exit on Windows via Job Object breakaway.
"""
import os
import sys
import subprocess
import time
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
        """Spawns the DRG server on port 8448 and the Headroom proxy on port 8787.

        On Windows, uses CREATE_NEW_PROCESS_GROUP to detach the process from the
        console and CREATE_BREAKAWAY_FROM_JOB to escape the terminal's Job Object
        so the daemon survives after the parent CLI process exits.
        """
        if self.is_running():
            return self.get_active_pid()

        drg_script = str(Path(__file__).parent.parent.parent / "kernel" / "drg.py")

        if sys.platform == "win32":
            # On Windows, terminal Job Objects aggressively kill child processes when
            # the parent CLI exits. DETACHED_PROCESS and CREATE_BREAKAWAY_FROM_JOB
            # often fail due to permission restrictions. WMI process creation safely
            # escapes the Job Object and runs independently.
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            cwd_escaped = os.getcwd().replace("'", "''")
            ps_cmd = f"$cmd = '{pythonw} \"{drg_script}\"'; Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList $cmd, '{cwd_escaped}'"
            
            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd(),
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
        else:
            proc = subprocess.Popen(
                [sys.executable, drg_script],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd(),
                start_new_session=True,
            )

        # drg.py writes its own PID to the pid file on boot, but we also
        # write the Popen PID as a fallback for immediate tracking.
        with open(self.pid_file, "w", encoding="utf-8") as f:
            f.write(str(proc.pid))

        # Wait for the server to bind to port 8448 (up to 5 seconds).
        if not self._wait_for_port(8448, timeout=5.0):
            # Process may have crashed — check return code
            rc = proc.poll()
            if rc is not None:
                raise RuntimeError(
                    f"DRG process exited with code {rc}. "
                    f"Check .aetheris/logs/drg.log for details."
                )

        # Re-read the PID file in case drg.py wrote its own real PID
        # (the Popen PID might be a cmd wrapper)
        real_pid = self.get_active_pid()

        # Start Headroom Proxy Gateway
        try:
            from aetheris.adapters.proxy_adapter import ProxyAdapter
            ProxyAdapter(os.getcwd()).start_proxy()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to auto-start Headroom proxy: {e}\n")

        return real_pid or proc.pid

    def terminate_daemon(self) -> bool:
        """Safely stops the active daemon, Headroom proxy, and their child process trees."""
        # Stop Headroom Proxy Gateway first
        try:
            from aetheris.adapters.proxy_adapter import ProxyAdapter
            ProxyAdapter(os.getcwd()).stop_proxy()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to stop Headroom proxy: {e}\n")

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

    @staticmethod
    def _wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 5.0) -> bool:
        """Poll until a TCP port is accepting connections or timeout expires."""
        import socket
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.25)
        return False
