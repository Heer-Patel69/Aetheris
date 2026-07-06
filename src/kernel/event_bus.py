import time
import uuid
import sys
from collections import defaultdict
from typing import Dict, Any, List, Callable, Optional
from kernel.telemetry import TelemetryEngine

class EventBus:
    """
    AEKS v1.0 Asynchronous Decoupled Event Bus.
    Provides publish/subscribe messaging interface allowing engines to coordinate
    without direct coupling or reference sharing.
    """
    
    def __init__(self, workspace_path: str, telemetry: Optional[TelemetryEngine] = None):
        self.workspace_path = workspace_path
        self.telemetry = telemetry if telemetry else TelemetryEngine(workspace_path)
        self.subscribers = defaultdict(list)
        self.queue = []
        
    def register_subscriber(self, module_name: str, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Registers a callback handler for a specific event type."""
        self.subscribers[event_type].append({
            "module": module_name,
            "handler": handler
        })

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None], module_name: str = "anonymous") -> None:
        """Alias helper method for registering subscribers."""
        self.register_subscriber(module_name, event_type, handler)

    def publish(self, event_type: str, publisher: str, payload: Dict[str, Any], priority: str = "NORMAL") -> str:
        """Publishes a new event to the in-memory queue."""
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "timestamp": time.time(),
            "event_type": event_type,
            "publisher": publisher,
            "payload": payload,
            "priority": priority
        }
        
        if priority == "CRITICAL":
            self.queue.insert(0, event)
        elif priority == "HIGH":
            idx = 0
            while idx < len(self.queue) and self.queue[idx]["priority"] in ("CRITICAL", "HIGH"):
                idx += 1
            self.queue.insert(idx, event)
        else:
            self.queue.append(event)
            
        # Log event publication
        try:
            self.telemetry.log_stage_complete(
                session_id="event-bus",
                stage="EVENT_PUBLISH",
                duration_ms=0,
                metadata={"event_id": event_id, "event_type": event_type, "priority": priority}
            )
        except Exception:
            pass
            
        return event_id

    def dispatch_next(self) -> bool:
        """Dispatches the next event in the queue to all registered subscribers."""
        if not self.queue:
            return False
            
        event = self.queue.pop(0)
        event_type = event["event_type"]
        subscribers = self.subscribers[event_type]
        
        if not subscribers:
            return True
            
        for sub in subscribers:
            start_time = time.time()
            try:
                sub["handler"](event["payload"])
                elapsed = int((time.time() - start_time) * 1000)
                if elapsed > 100:
                    sys.stderr.write(f"WARNING: Event handler in {sub['module']} exceeded timeout budget: {elapsed}ms\n")
            except Exception as e:
                elapsed = int((time.time() - start_time) * 1000)
                try:
                    self.telemetry.log_stage_failed(
                        session_id="event-bus",
                        stage=f"EVENT_DISPATCH_{sub['module']}",
                        error=f"Handler Exception in {sub['module']}: {e}",
                        duration_ms=elapsed
                    )
                except Exception:
                    pass
                sys.stderr.write(f"Event Bus Error: Subscriber {sub['module']} failed on {event_type}: {e}\n")
                
        return True

    def clear_queue(self) -> None:
        self.queue.clear()