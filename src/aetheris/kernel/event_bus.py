import uuid
import time
from typing import Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass, field

@dataclass
class AetherisEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    project_id: str = ""
    workspace_id: str = ""
    execution_id: str = ""
    timestamp: float = field(default_factory=time.time)
    engine: str = ""
    category: str = ""
    severity: str = "INFO"
    payload: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "project_id": self.project_id,
            "workspace_id": self.workspace_id,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "engine": self.engine,
            "category": self.category,
            "severity": self.severity,
            "payload": self.payload,
            "duration": self.duration,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'AetherisEvent':
        return cls(
            event_id=d.get("event_id", str(uuid.uuid4())),
            session_id=d.get("session_id", ""),
            project_id=d.get("project_id", ""),
            workspace_id=d.get("workspace_id", ""),
            execution_id=d.get("execution_id", ""),
            timestamp=d.get("timestamp", time.time()),
            engine=d.get("engine", ""),
            category=d.get("category", ""),
            severity=d.get("severity", "INFO"),
            payload=d.get("payload", {}),
            duration=d.get("duration", 0.0),
            dependencies=d.get("dependencies", []),
            metadata=d.get("metadata", {}),
            version=d.get("version", 1)
        )

class AetherisEventBus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AetherisEventBus, cls).__new__(cls, *args, **kwargs)
            cls._instance._listeners = []
            cls._instance.session_id = "default-session"
            cls._instance.project_id = "default-project"
            cls._instance.workspace_id = "default-workspace"
            cls._instance.execution_id = ""
            
            # Auto-register EventStore and ProjectionEngine
            try:
                from aetheris.infrastructure.event_store import EventStore
                EventStore()
            except Exception:
                pass
            try:
                from aetheris.kernel.projections import ProjectionEngine
                ProjectionEngine()
            except Exception:
                pass
        return cls._instance

    def set_context(self, session_id: str = "", project_id: str = "", workspace_id: str = "", execution_id: str = ""):
        if session_id: self.session_id = session_id
        if project_id: self.project_id = project_id
        if workspace_id: self.workspace_id = workspace_id
        if execution_id: self.execution_id = execution_id

    def subscribe(self, callback: Callable[[AetherisEvent], Awaitable[None]]):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[AetherisEvent], Awaitable[None]]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    async def publish(self, event: AetherisEvent):
        # Auto-augment context if empty
        if not event.session_id: event.session_id = self.session_id
        if not event.project_id: event.project_id = self.project_id
        if not event.workspace_id: event.workspace_id = self.workspace_id
        if not event.execution_id: event.execution_id = self.execution_id

        for listener in self._listeners:
            try:
                await listener(event)
            except Exception:
                # Prevent listener crashes from bringing down the bus
                pass

    def publish_sync(self, event: AetherisEvent):
        import asyncio
        coro = self.publish(event)
        try:
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(coro)
                    return
            except RuntimeError:
                pass
            
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(coro)
            else:
                loop.run_until_complete(coro)
        except Exception:
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                new_loop.run_until_complete(coro)
                new_loop.close()
            except Exception:
                try:
                    coro.close()
                except Exception:
                    pass
