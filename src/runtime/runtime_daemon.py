"""
RuntimeDaemon — Persistent background process for Aetheris Phase 4.

Responsibilities:
  - Start EventStore, ProjectionEngine, AnalyticsEngine, MemoryEngine
  - Start RuntimeGateway (WebSocket server)
  - Emit lifecycle events
  - Maintain PID file for aetheris start/stop/status
  - Launch Mission Control dashboard automatically on start
"""
import json
import os
import signal
import sys
import time
import threading
from pathlib import Path
from typing import Optional

from runtime.event_store import EventStore
from runtime.projection_engine import ProjectionEngine
from runtime.analytics_engine import AnalyticsEngine
from runtime.memory_engine import MemoryEngine
from runtime.runtime_gateway import RuntimeGateway
from runtime.observability import ObservabilityEngine


class RuntimeDaemon:
    """
    The Aetheris Phase 4 Runtime Daemon.

    Lifecycle:
        daemon = RuntimeDaemon(workspace_path)
        daemon.start()            # launches all engines + WS server
        daemon.emit(...)          # emit events from any engine
        daemon.stop()             # graceful shutdown
    """

    GATEWAY_HOST = "127.0.0.1"
    GATEWAY_PORT = 8449

    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path).resolve()
        self._runtime_dir = Path.home() / ".aetheris" / "runtime"
        self._runtime_dir.mkdir(parents=True, exist_ok=True)

        self._pid_file   = self._runtime_dir / "aetheris.pid"
        self._state_file = self._runtime_dir / "daemon_state.json"

        # event store path
        store_dir = self.workspace / ".aetheris" / "events"
        store_dir.mkdir(parents=True, exist_ok=True)

        # core engines
        self.event_store   = EventStore(str(store_dir))
        self.projections   = ProjectionEngine(self.event_store)
        self.analytics     = AnalyticsEngine(self.event_store)
        self.memory        = MemoryEngine(str(self.workspace), self.event_store)
        self.observability = ObservabilityEngine(str(self.workspace))
        self.gateway       = RuntimeGateway(
            self.event_store,
            self.projections,
            host=self.GATEWAY_HOST,
            port=self.GATEWAY_PORT,
        )

        self._session_id: Optional[str] = None
        self._running = False
        self._start_time: Optional[float] = None

    # ── already running check ─────────────────────────────────────────────────

    def is_already_running(self) -> bool:
        if not self._pid_file.exists():
            return False
        try:
            pid = int(self._pid_file.read_text().strip())
            # check if process is alive
            if sys.platform == "win32":
                import ctypes
                handle = ctypes.windll.kernel32.OpenProcess(0x0400, False, pid)
                if handle:
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return True
                return False
            else:
                os.kill(pid, 0)
                return True
        except (ValueError, ProcessLookupError, PermissionError):
            # stale PID file
            self._pid_file.unlink(missing_ok=True)
            return False

    # ── start ─────────────────────────────────────────────────────────────────

    def start(self, session_id: Optional[str] = None) -> bool:
        if self.is_already_running():
            print("\n  Aetheris Runtime is already running.")
            print(f"  Connect Mission Control at  ws://{self.GATEWAY_HOST}:{self.GATEWAY_PORT}")
            return False

        import uuid
        self._session_id = session_id or str(uuid.uuid4())[:8]
        self._start_time = time.time()
        self._running    = True

        # write PID file
        self._pid_file.write_text(str(os.getpid()), encoding="utf-8")

        # save daemon state
        self._save_state("starting")

        # start WebSocket gateway in background thread
        self.gateway.start()

        # register signal handlers
        self._register_signals()

        # emit SESSION_START event
        self.event_store.emit(
            category="SESSION",
            event_type="SessionStarted",
            payload={
                "session_id": self._session_id,
                "workspace":  str(self.workspace),
                "pid":        os.getpid(),
                "gateway_url": self.gateway.url,
            },
            session_id=self._session_id,
            workspace_id=str(self.workspace),
        )
        self.observability.info("RuntimeDaemon", "Daemon started",
                                session=self._session_id,
                                gateway=self.gateway.url)

        self._save_state("running")

        # Start Autonomous Engineering Workspace Synchronization
        try:
            from kernel.workspace import WorkspaceManager
            workspace_manager = WorkspaceManager(str(self.workspace))
            threading.Thread(
                target=workspace_manager.start_workspace,
                name="AetherisWorkspaceSync",
                daemon=True
            ).start()
            self.observability.info("RuntimeDaemon", "Autonomous Workspace Synchronization started.")
        except Exception as e:
            self.observability.error("RuntimeDaemon", f"Failed to start WorkspaceManager: {e}")

        return True

    # ── emit convenience ──────────────────────────────────────────────────────

    def emit(self, category: str, event_type: str, payload: dict,
             stream_id: str = "global"):
        return self.event_store.emit(
            category=category,
            event_type=event_type,
            payload=payload,
            stream_id=stream_id,
            session_id=self._session_id or "",
            workspace_id=str(self.workspace),
        )

    # ── stop ──────────────────────────────────────────────────────────────────

    def stop(self):
        if not self._running:
            return

        self.event_store.emit(
            category="SESSION",
            event_type="SessionCompleted",
            payload={"session_id": self._session_id,
                     "uptime_seconds": round(time.time() - (self._start_time or 0), 1)},
            session_id=self._session_id or "",
        )
        self.gateway.stop()
        self._running = False
        self._pid_file.unlink(missing_ok=True)
        self._save_state("stopped")
        self.observability.info("RuntimeDaemon", "Daemon stopped")

    # ── status ────────────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "running":         self._running,
            "pid":             os.getpid(),
            "session_id":      self._session_id,
            "uptime_seconds":  round(time.time() - (self._start_time or time.time()), 1),
            "gateway_url":     self.gateway.url,
            "connected_clients": self.gateway.connected_clients,
            "total_events":    self.event_store.total_count(),
            "ekb_entries":     self.memory.ekb_entry_count,
        }

    # ── state persistence ─────────────────────────────────────────────────────

    def _save_state(self, status: str):
        state = {
            "status":      status,
            "pid":         os.getpid(),
            "session_id":  self._session_id,
            "start_time":  self._start_time,
            "gateway_url": self.gateway.url,
            "updated_at":  time.time(),
        }
        self._state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    # ── signals ───────────────────────────────────────────────────────────────

    def _register_signals(self):
        try:
            signal.signal(signal.SIGTERM, self._handle_signal)
            signal.signal(signal.SIGINT,  self._handle_signal)
        except (AttributeError, OSError):
            pass  # Windows may not support all signals

    def _handle_signal(self, signum, frame):
        self.stop()
        sys.exit(0)
