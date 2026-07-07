from src.kernel.interfaces import AetherisEngine
from src.kernel.events import EventBus, Event
from typing import Dict, Any
import asyncio

class ExecutiveDecisionOrchestrator(AetherisEngine):
    """
    The un-bypassable final decision maker.
    Enforces the Engineering Operating System workflow.
    """
    def __init__(self):
        self.state = "INITIALIZED"
        self.event_bus = None
        self.workflow_state = "AWAITING_PROMPT"

    def initialize(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.event_bus.subscribe("USER_PROMPT_RECEIVED", self.handle_user_prompt)
        self.event_bus.subscribe("IMPLEMENTATION_PLAN_APPROVED", self.handle_plan_approved)
        print("[EDO] Initialized and locked down execution pathways.")

    def get_state(self) -> Dict[str, Any]:
        return {"engine": "EDO", "state": self.state, "workflow": self.workflow_state}

    async def handle_user_prompt(self, event: Event):
        print(f"[EDO] Intercepted user prompt: {event.payload.get('prompt')}")
        self.workflow_state = "PLANNING_PHASE"
        # Delegate to Capability Resolution Engine via Event Bus
        await self.event_bus.publish(Event(
            type="RESOLVE_INTENT",
            payload={"prompt": event.payload.get("prompt")},
            source="EDO"
        ))

    async def handle_plan_approved(self, event: Event):
        print("[EDO] Implementation plan approved. Unlocking execution pathway.")
        self.workflow_state = "EXECUTION_PHASE"
        await self.event_bus.publish(Event(
            type="START_EXECUTION",
            payload={"plan_id": event.payload.get("plan_id")},
            source="EDO"
        ))

    def approve_action(self, action_request: Dict[str, Any]) -> bool:
        if self.workflow_state != "EXECUTION_PHASE":
            print("[EDO] SECURITY BLOCK: Attempted code generation before planning phase was approved.")
            return False
        return True
