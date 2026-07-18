"""
kernel/core_phase4_patch.py — Phase 4 wiring shim for AetherisKernel.

Import this at the top of kernel/core.py run_autonomous_loop() to wire
all Phase 4 engines into the existing execution pipeline without
rewriting the entire core.
"""
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


def init_phase4_engines(workspace_path: str, session_id: str = ""):
    """
    Instantiate all Phase 4 engines and return them as a dict.
    Called once at the start of run_autonomous_loop().
    """
    try:
        from runtime.event_store      import EventStore
        from runtime.projection_engine import ProjectionEngine
        from runtime.analytics_engine  import AnalyticsEngine
        from runtime.memory_engine     import MemoryEngine
        from runtime.observability     import ObservabilityEngine
        from runtime.runtime_gateway   import RuntimeGateway
        from intelligence.mie          import ModelIntelligenceEngine
        from intelligence.io           import IntelligenceOrchestrator
        from intelligence.insights     import EngineeringInsightsEngine
        from kernel.mission_control    import MissionControl
        from runtime.replay_engine     import ReplayEngine
    except ImportError as e:
        import sys
        sys.stderr.write(f"Phase 4 engine import warning: {e}\n")
        return {}

    store_dir = Path(workspace_path) / ".aetheris" / "events"
    store_dir.mkdir(parents=True, exist_ok=True)

    event_store  = EventStore(str(store_dir))
    projections  = ProjectionEngine(event_store)
    analytics    = AnalyticsEngine(event_store)
    memory       = MemoryEngine(workspace_path, event_store, session_id)
    observ       = ObservabilityEngine(workspace_path, session_id)
    replay       = ReplayEngine(event_store)
    insights     = EngineeringInsightsEngine(event_store, session_id)
    mie          = ModelIntelligenceEngine(workspace_path, event_store, session_id)
    io           = IntelligenceOrchestrator(workspace_path, event_store, session_id)
    mc           = MissionControl(
        workspace_path = workspace_path,
        projections    = projections,
        analytics      = analytics,
        replay         = replay,
        event_store    = event_store,
        workspace_id   = workspace_path,
    )

    # emit session start
    event_store.emit(
        category    = "SESSION",
        event_type  = "SessionStarted",
        payload     = {"session_id": session_id, "workspace": workspace_path,
                       "pid": os.getpid()},
        session_id  = session_id,
        workspace_id= workspace_path,
    )

    return {
        "event_store": event_store,
        "projections": projections,
        "analytics":   analytics,
        "memory":      memory,
        "observability": observ,
        "replay":      replay,
        "insights":    insights,
        "mie":         mie,
        "io":          io,
        "mission_control": mc,
    }


def emit_stage(engines: Dict[str, Any], stage: str, status: str,
               session_id: str = "", duration_ms: int = 0, error: str = ""):
    """Emit a StageStarted / StageCompleted / StageFailed event."""
    store = engines.get("event_store")
    if not store:
        return
    if status == "started":
        store.emit("EXECUTION", "StageStarted",
                   {"stage": stage}, session_id=session_id)
    elif status == "completed":
        store.emit("EXECUTION", "StageCompleted",
                   {"stage": stage, "duration_ms": duration_ms},
                   session_id=session_id)
    elif status == "failed":
        store.emit("EXECUTION", "StageFailed",
                   {"stage": stage, "error": error, "duration_ms": duration_ms},
                   session_id=session_id)


def emit_token_usage(engines: Dict[str, Any], model_id: str,
                     input_tokens: int, output_tokens: int,
                     session_id: str = ""):
    """Emit TOKENS + COSTS events for a model call."""
    store = engines.get("event_store")
    if not store:
        return
    store.emit("TOKENS", "TokensUsed",
               {"model_id": model_id, "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens},
               session_id=session_id)
    coe = engines.get("io")
    if coe:
        coe.coe.record_cost(model_id, input_tokens, output_tokens)


def finalize_session(engines: Dict[str, Any], session_id: str,
                     status: str = "completed"):
    """Emit session end event and flush memory snapshot."""
    store = engines.get("event_store")
    if store:
        store.emit("SESSION",
                   "SessionCompleted" if status == "completed" else "SessionFailed",
                   {"session_id": session_id, "status": status},
                   session_id=session_id)
    memory = engines.get("memory")
    if memory:
        memory.save_snapshot("session_end", {"session_id": session_id,
                                             "status": status,
                                             "ts": time.time()})
