"""
dashboard_api.py — HTTP REST API for Mission Control (Phase 4).

Serves live projection data over HTTP on port 8448 so that
any browser or client can query Mission Control without WebSocket.

Endpoints:
  GET /health                     — liveness check
  GET /api/v1/dashboard/global    — global dashboard snapshot
  GET /api/v1/dashboard/workspace — workspace dashboard snapshot
  GET /api/v1/dashboard/session/{id} — session dashboard snapshot
  GET /api/v1/panels              — list all panel names
  GET /api/v1/panels/{name}       — single panel data
  GET /api/v1/analytics/global    — global analytics
  GET /api/v1/analytics/session/{id} — session analytics
  GET /api/v1/replay/sessions     — list replayable sessions
  GET /api/v1/replay/{id}         — reconstruct session timeline
  GET /api/v1/insights            — engineering insights report
  GET /api/v1/events/latest       — last 50 events
  GET /api/v1/models              — model registry

Requires: no external deps — uses Python stdlib http.server
"""
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs


class _MCHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Mission Control API."""

    # injected by DashboardAPI.start()
    mc          = None   # MissionControl
    analytics   = None   # AnalyticsEngine
    replay      = None   # ReplayEngine
    insights    = None   # EngineeringInsightsEngine
    event_store = None   # EventStore
    mie         = None   # ModelIntelligenceEngine
    workspace_id= ""

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        qs     = parse_qs(parsed.query)

        try:
            data = self._route(path, qs)
            self._respond(200, data)
        except Exception as exc:
            self._respond(500, {"error": str(exc)})

    def _route(self, path: str, qs: Dict) -> Any:
        if path == "/health":
            return {"status": "ok", "ts": time.time()}

        if path == "/api/v1/dashboard/global":
            return self.mc.render_global()

        if path == "/api/v1/dashboard/workspace":
            return self.mc.render_workspace()

        if path.startswith("/api/v1/dashboard/session/"):
            sid = path.split("/")[-1]
            return self.mc.render_session(sid)

        if path == "/api/v1/panels":
            return {"panels": self.mc.list_panels()}

        if path.startswith("/api/v1/panels/"):
            name = path.split("/")[-1]
            data = self.mc.render_panel(name)
            if data is None:
                self._respond(404, {"error": f"panel {name!r} not found"})
                return None
            return data

        if path == "/api/v1/analytics/global":
            return self.analytics.global_analytics()

        if path.startswith("/api/v1/analytics/session/"):
            sid = path.split("/")[-1]
            return self.analytics.session_analytics(sid)

        if path == "/api/v1/replay/sessions":
            return {"sessions": self.replay.list_replayable_sessions()}

        if path.startswith("/api/v1/replay/"):
            sid = path.split("/")[-1]
            tl  = self.replay.reconstruct_session(sid)
            return tl.to_dict()

        if path == "/api/v1/insights":
            return self.insights.generate_report(self.workspace_id)

        if path == "/api/v1/events/latest":
            n = int(qs.get("n", ["50"])[0])
            return {"events": [e.to_dict() for e in self.event_store.latest(n)]}

        if path == "/api/v1/models":
            return {"models": self.mie.list_models()}

        self._respond(404, {"error": "not found"})
        return None

    def _respond(self, code: int, data: Any):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass   # suppress default access log


class DashboardAPI:
    """Starts the HTTP dashboard API in a background thread."""

    def __init__(self, port: int = 8448, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, mc, analytics, replay, insights, event_store, mie,
              workspace_id: str = ""):
        """Wire dependencies and start serving."""
        _MCHandler.mc          = mc
        _MCHandler.analytics   = analytics
        _MCHandler.replay      = replay
        _MCHandler.insights    = insights
        _MCHandler.event_store = event_store
        _MCHandler.mie         = mie
        _MCHandler.workspace_id= workspace_id

        self._server = HTTPServer((self.host, self.port), _MCHandler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
