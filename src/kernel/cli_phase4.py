"""
Phase 4 CLI additions — patched into kernel/cli.py

Adds to AetherisRuntime:
  - start_phase4_daemon()  called by `aetheris start`
  - Detects already-running daemon
  - Starts RuntimeDaemon + MissionControl
  - Prints gateway URL and panel list
"""
import os
import sys
import json
from pathlib import Path


def phase4_start(workspace_path: str = ".") -> bool:
    """
    Phase 4 startup sequence for `aetheris start`.
    Returns True if daemon was started fresh; False if already running.
    """
    try:
        from runtime.runtime_daemon import RuntimeDaemon
        from runtime.replay_engine import ReplayEngine
        from runtime.analytics_engine import AnalyticsEngine
        from kernel.mission_control import MissionControl
    except ImportError as e:
        sys.stderr.write(f"Phase 4 import error: {e}\n")
        return False

    daemon = RuntimeDaemon(workspace_path)

    if daemon.is_already_running():
        print("\n  ╔══════════════════════════════════════════════╗")
        print("  ║   Aetheris Runtime is already running.       ║")
        print("  ╚══════════════════════════════════════════════╝\n")
        print(f"  Mission Control WebSocket:  ws://127.0.0.1:8449")
        print("  Connect your dashboard to the live gateway.\n")
        return False

    # Start daemon (EventStore + ProjectionEngine + AnalyticsEngine + Gateway)
    started = daemon.start()
    if not started:
        return False

    # Instantiate Mission Control for CLI status output
    mc = MissionControl(
        workspace_path   = workspace_path,
        projections      = daemon.projections,
        analytics        = daemon.analytics,
        replay           = ReplayEngine(daemon.event_store),
        event_store      = daemon.event_store,
        workspace_id     = workspace_path,
    )

    _print_phase4_banner(daemon, mc)
    return True


def _print_phase4_banner(daemon, mc):
    status = daemon.status()
    panels = mc.list_panels()

    print("\n  ╔══════════════════════════════════════════════════════╗")
    print("  ║        AETHERIS MISSION CONTROL — PHASE 4            ║")
    print("  ╠══════════════════════════════════════════════════════╣")
    print(f"  ║  Status:   {status['running'] and 'RUNNING' or 'IDLE':<43}║")
    print(f"  ║  Session:  {status['session_id']:<43}║")
    print(f"  ║  Gateway:  {status['gateway_url']:<43}║")
    print(f"  ║  Events:   {status['total_events']:<43}║")
    print(f"  ║  EKB:      {status['ekb_entries']:} entries{'':<36}║")
    print("  ╠══════════════════════════════════════════════════════╣")
    print("  ║  Live Panels:                                        ║")
    for panel in panels:
        print(f"  ║    • {panel:<49}║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print("\n  Connect Mission Control:  ws://127.0.0.1:8449")
    print("  Dashboard API:            http://127.0.0.1:8448")
    print("  Stop daemon:              aetheris stop\n")
