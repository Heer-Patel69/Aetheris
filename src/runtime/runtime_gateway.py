"""
RuntimeGateway — WebSocket hub broadcasting live projections to Mission Control clients.

Architecture:
  - One asyncio event loop per gateway instance
  - EventStore subscriber → broadcasts new events to all WS clients
  - ProjectionEngine subscriber per named projection → broadcasts projection snapshots
  - Clients can subscribe to specific projections or receive all events

Requires: websockets>=11.0
"""
import asyncio
import json
import threading
import time
from typing import Any, Callable, Dict, Optional, Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    _WS_AVAILABLE = True
except ImportError:
    _WS_AVAILABLE = False

from runtime.event_store import EngEvent, EventStore
from runtime.projection_engine import ProjectionEngine


class RuntimeGateway:
    """
    WebSocket server that bridges the EventStore / ProjectionEngine to
    browser-based Mission Control clients.

    Protocol (JSON messages)
    ------------------------
    Client → Server:
      {"type": "subscribe", "projection": "<name>"}   subscribe to projection
      {"type": "unsubscribe", "projection": "<name>"}
      {"type": "ping"}

    Server → Client:
      {"type": "event",      "data": <EngEvent.to_dict()>}
      {"type": "projection", "projection": "<name>", "data": <snapshot>}
      {"type": "pong"}
      {"type": "error",      "message": "..."}
    """

    def __init__(
        self,
        event_store: EventStore,
        projection_engine: ProjectionEngine,
        host: str = "127.0.0.1",
        port: int = 8449,
    ):
        self.store       = event_store
        self.projections = projection_engine
        self.host        = host
        self.port        = port

        self._clients: Set = set()          # WebSocket connections
        self._subscriptions: Dict = {}      # ws → set of projection names
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._server = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

        # subscribe to live events from the store
        event_store.subscribe(self._on_new_event)

        # subscribe to all projection updates
        for name in projection_engine.list_projections():
            projection_engine.subscribe(name, self._make_projection_handler(name))

    # ── event / projection handlers ───────────────────────────────────────────

    def _on_new_event(self, event: EngEvent):
        """Called by EventStore on every new event."""
        msg = json.dumps({"type": "event", "data": event.to_dict()})
        self._broadcast(msg)

    def _make_projection_handler(self, name: str) -> Callable:
        def handler(snapshot: Dict[str, Any]):
            msg = json.dumps({"type": "projection",
                              "projection": name, "data": snapshot})
            self._broadcast_to_subscribers(name, msg)
        return handler

    def _broadcast(self, msg: str):
        """Broadcast a raw message to all connected clients."""
        if not self._loop or not self._clients:
            return
        asyncio.run_coroutine_threadsafe(
            self._async_broadcast(msg, self._clients.copy()),
            self._loop,
        )

    def _broadcast_to_subscribers(self, projection_name: str, msg: str):
        """Broadcast only to clients subscribed to a specific projection."""
        if not self._loop:
            return
        targets = {
            ws for ws, subs in self._subscriptions.items()
            if projection_name in subs or "*" in subs
        }
        if not targets:
            return
        asyncio.run_coroutine_threadsafe(
            self._async_broadcast(msg, targets),
            self._loop,
        )

    async def _async_broadcast(self, msg: str, clients: set):
        dead = set()
        for ws in clients:
            try:
                await ws.send(msg)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._clients.discard(ws)
            self._subscriptions.pop(ws, None)

    # ── WebSocket handler ─────────────────────────────────────────────────────

    async def _handler(self, ws, path=None):
        self._clients.add(ws)
        self._subscriptions[ws] = set()
        try:
            # send current projection snapshot on connect
            all_snaps = self.projections.get_all()
            await ws.send(json.dumps({"type": "snapshot", "data": all_snaps}))

            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    await ws.send(json.dumps({"type": "error",
                                              "message": "invalid json"}))
                    continue

                mtype = msg.get("type", "")
                if mtype == "subscribe":
                    proj = msg.get("projection", "*")
                    self._subscriptions[ws].add(proj)
                    # send current snapshot immediately
                    snap = self.projections.get(proj)
                    if snap:
                        await ws.send(json.dumps({"type": "projection",
                                                   "projection": proj,
                                                   "data": snap}))
                elif mtype == "unsubscribe":
                    self._subscriptions[ws].discard(msg.get("projection", ""))
                elif mtype == "ping":
                    await ws.send(json.dumps({"type": "pong",
                                              "ts": time.time()}))
        except Exception:
            pass
        finally:
            self._clients.discard(ws)
            self._subscriptions.pop(ws, None)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the WebSocket server in a background thread."""
        if not _WS_AVAILABLE:
            import sys
            sys.stderr.write(
                "WARNING: websockets package not installed. "
                "RuntimeGateway disabled. Run: pip install websockets>=11.0\n"
            )
            return

        self._running = True
        self._thread  = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        async with websockets.serve(self._handler, self.host, self.port):
            while self._running:
                await asyncio.sleep(0.5)

    def stop(self):
        self._running = False

    @property
    def url(self) -> str:
        return f"ws://{self.host}:{self.port}"

    @property
    def connected_clients(self) -> int:
        return len(self._clients)
