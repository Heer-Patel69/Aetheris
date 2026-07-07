import json
from pathlib import Path
from typing import Dict, Any, List
from aetheris.kernel.event_bus import AetherisEvent, AetherisEventBus

class ProjectionEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectionEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance.skills = []
            cls._instance.rfcSpecs = []
            cls._instance.health = {
                "architecture": 100,
                "security": 100,
                "testing": 100,
                "performance": 100,
                "documentation": 100,
                "maintainability": 100
            }
            cls._instance.models = []
            cls._instance.replay = []
            cls._instance.runtime = {
                "status": "READY",
                "ide": "N/A",
                "model_in_use": "N/A",
                "workspace": "N/A",
                "project": "N/A",
                "engines_online": 12,
                "total_engines": 12,
                "brain_state": "IDLE",
                "workflow_phase": "Awaiting task",
                "active_goal": "None",
                "current_branch": "main",
                "cpu": 1.2,
                "ram": 142,
                "uptime": 0
            }
            cls._instance.runtime_cache_path = Path(".aetheris/state/runtime.json")
            cls._instance.exec_cache_path = Path(".aetheris/execution_state.json")
            AetherisEventBus().subscribe(cls._instance.apply_event)
        return cls._instance

    async def apply_event(self, event: AetherisEvent):
        cat = event.category
        payload = event.payload

        if cat == "SYSTEM_BOOT":
            self.runtime.update(payload)
            self.runtime["status"] = "READY"
        elif cat == "DAEMON_STATUS":
            self.runtime.update(payload)
        elif cat == "SKILL_INDEXED":
            if payload not in self.skills:
                self.skills.append(payload)
        elif cat == "SKILL_LOADED":
            for s in self.skills:
                if s.get("name") == payload.get("name"):
                    s["status"] = "active"
                    break
        elif cat == "RFC_DISCOVERED":
            if payload not in self.rfcSpecs:
                self.rfcSpecs.append(payload)
        elif cat == "SPEC_RESOLVED":
            for r in self.rfcSpecs:
                if r.get("name") == payload.get("name"):
                    r["coverage"] = payload.get("coverage", 100)
                    break
        elif cat == "TOKEN_TRACKING":
            model_name = payload.get("model")
            found = False
            for m in self.models:
                if m.get("model") == model_name:
                    m["tokens"] = m.get("tokens", 0) + payload.get("tokens", 0)
                    m["cost"] = m.get("cost", 0.0) + payload.get("cost", 0.0)
                    m["latency"] = payload.get("latency", 0.0)
                    found = True
                    break
            if not found:
                self.models.append({
                    "model": model_name,
                    "tokens": payload.get("tokens", 0),
                    "cost": payload.get("cost", 0.0),
                    "latency": payload.get("latency", 0.0)
                })
        elif cat == "VERIFICATION_COMPLETED":
            if "health" in payload:
                self.health.update(payload["health"])
        elif cat in ("TASK_STARTED", "TASK_COMPLETED", "DECISION_MADE"):
            self.replay.append({
                "timestamp": event.timestamp,
                "phase": payload.get("phase", "Execution"),
                "task": payload.get("task", ""),
                "status": payload.get("status", "completed"),
                "detail": payload.get("detail", "")
            })
            if cat == "TASK_STARTED":
                self.runtime["brain_state"] = "BUSY"
                self.runtime["workflow_phase"] = payload.get("phase", "Execution")
                self.runtime["active_goal"] = payload.get("task", "")
            elif cat == "TASK_COMPLETED":
                self.runtime["brain_state"] = "IDLE"
                self.runtime["workflow_phase"] = "Awaiting task"
                self.runtime["active_goal"] = "None"

        self.save_caches()

    def save_caches(self):
        try:
            self.runtime_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.runtime_cache_path, "w", encoding="utf-8") as f:
                json.dump(self.runtime, f, indent=2)
            
            with open(self.exec_cache_path, "w", encoding="utf-8") as f:
                json.dump({
                    "skills": self.skills,
                    "rfcSpecs": self.rfcSpecs,
                    "health": self.health,
                    "models": self.models,
                    "replay": self.replay
                }, f, indent=2)
        except Exception:
            pass

    def get_projection_snapshot(self) -> Dict[str, Any]:
        return {
            "runtime": self.runtime,
            "skills": self.skills,
            "rfcSpecs": self.rfcSpecs,
            "health": self.health,
            "models": self.models,
            "replay": self.replay
        }
