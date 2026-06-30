import time
import uuid
import sys
from collections import defaultdict
from kernel.telemetry import TelemetryEngine

class EventBus:
    def __init__(self, workspace_path, telemetry=None):
        self.subscribers = defaultdict(list)
        self.queue = []
        self.workspace_path = workspace_path
        self.telemetry = telemetry if telemetry else TelemetryEngine(workspace_path)
        
    def register_subscriber(self, module_name, event_type, handler):
        """
        Registers a callback handler for a specific event type.
        """
        # In a real environment we would check against registered configs
        self.subscribers[event_type].append({
            "module": module_name,
            "handler": handler
        })

    def publish(self, event_type, publisher, payload, priority="NORMAL"):
        """
        Publishes a new event to the in-memory queue.
        """
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "timestamp": time.time(),
            "event_type": event_type,
            "publisher": publisher,
            "payload": payload,
            "priority": priority
        }
        
        # Enforce priority ordering during insertion
        if priority == "CRITICAL":
            self.queue.insert(0, event)
        elif priority == "HIGH":
            # Insert after other HIGH/CRITICAL events
            idx = 0
            while idx < len(self.queue) and self.queue[idx]["priority"] in ("CRITICAL", "HIGH"):
                idx += 1
            self.queue.insert(idx, event)
        else:
            self.queue.append(event)
            
        # Log event publication
        self.telemetry.log_stage_complete(
            session_id="event-bus",
            stage="EVENT_PUBLISH",
            duration_ms=0,
            metadata={"event_id": event_id, "event_type": event_type, "priority": priority}
        )

    def dispatch_next(self):
        """
        Dispatches the next event in the queue to all registered subscribers.
        """
        if not self.queue:
            return False
            
        event = self.queue.pop(0)
        event_type = event["event_type"]
        subscribers = self.subscribers[event_type]
        
        if not subscribers:
            # Drop unhandled events and log as dead letters if necessary
            return True
            
        for sub in subscribers:
            start_time = time.time()
            try:
                # Dispatch event to handler
                sub["handler"](event["payload"])
                elapsed = int((time.time() - start_time) * 1000)
                
                # Check performance target budget (50ms per handler)
                if elapsed > 100:
                    sys.stderr.write(f"WARNING: Event handler in {sub['module']} exceeded timeout budget: {elapsed}ms\n")
                    
            except Exception as e:
                # Recover safely: write dead-letter to telemetry, keep dispatching
                elapsed = int((time.time() - start_time) * 1000)
                self.telemetry.log_stage_failed(
                    session_id="event-bus",
                    stage=f"EVENT_DISPATCH_{sub['module']}",
                    error=f"Handler Exception in {sub['module']}: {e}",
                    duration_ms=elapsed
                )
                sys.stderr.write(f"Event Bus Error: Subscriber {sub['module']} failed on {event_type}: {e}\n")
                
        return True

    def clear_queue(self):
        self.queue.clear()