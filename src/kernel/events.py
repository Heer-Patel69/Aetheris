import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List
import time

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    source: str
    timestamp: float = field(default_factory=time.time)

class EventBus:
    """
    Central nervous system of Aetheris.
    Provides an async Pub/Sub mechanism for the 18 decoupled engines.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        print(f"[EventBus] Subscribed to {event_type}")

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)
        print(f"[EventBus] Event Published: {event.type} from {event.source}")

    async def _process_queue(self):
        while self._running:
            event = await self._queue.get()
            if event.type in self._subscribers:
                for handler in self._subscribers[event.type]:
                    # In a production environment, this should dispatch tasks asynchronously
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)
            self._queue.task_done()

    async def start(self):
        self._running = True
        asyncio.create_task(self._process_queue())
        print("[EventBus] Started asynchronous event processing.")

    def stop(self):
        self._running = False
