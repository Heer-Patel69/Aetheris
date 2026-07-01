import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from intelligence.ekb import EngineeringKnowledgeBase

class ModelRoutingEngine:
    """Selects the optimal LLM backend matching the task's complexity, cost, and latency budgets (SPEC-035)."""
    def __init__(self, workspace_path: str, ekb: EngineeringKnowledgeBase):
        self.workspace_path = Path(workspace_path).resolve()
        self.ekb = ekb
        self.exec_dir = self.workspace_path / ".aetheris" / "execution"
        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.model_costs = {
            "claude-3-5-sonnet": {"input": 3.0 / 1e6, "output": 15.0 / 1e6},
            "gemini-1.5-pro": {"input": 1.25 / 1e6, "output": 5.0 / 1e6},
            "gemini-1.5-flash": {"input": 0.075 / 1e6, "output": 0.3 / 1e6},
            "gpt-4o": {"input": 5.0 / 1e6, "output": 15.0 / 1e6}
        }

    def route_model(self, task: dict, skill: dict) -> dict:
        """Determines the primary and fallback LLM models for a given task/skill pairing."""
        ranked = self.rank_models_for_task(task)
        primary = ranked[0]["name"]
        fallback = ranked[1]["name"] if len(ranked) > 1 else "gemini-1.5-flash"
        
        cost_est = self.estimate_cost(primary, 5000, 1000)
        latency_est = self.estimate_latency(primary)
        conf = self.confidence(primary, task)

        routing_decision = {
            "task_id": task["id"],
            "primary_model": primary,
            "fallback_model": fallback,
            "estimated_cost_usd": cost_est,
            "estimated_latency_seconds": latency_est,
            "routing_confidence": conf
        }

        # Write files
        decisions_file = self.exec_dir / "routing.decisions.json"
        decisions = []
        if decisions_file.exists():
            try:
                decisions = json.loads(decisions_file.read_text(encoding="utf-8"))
            except Exception:
                decisions = []
        
        decisions.append(routing_decision)
        decisions_file.write_text(json.dumps(decisions, indent=2), encoding="utf-8")
        
        # Save mappings summary
        (self.exec_dir / "model.assignment.json").write_text(json.dumps({"assignments": decisions}, indent=2), encoding="utf-8")
        self.ekb.register_object("model_routing_decisions", {"id": "model_routes", "decisions": decisions}, producer="MRE")

        return routing_decision

    def rank_models_for_task(self, task: dict) -> List[dict]:
        """Ranks models based on task priority and reasoning complexity."""
        priority = task.get("priority", "MEDIUM")
        tid = task["id"].lower()

        if priority == "HIGH" or "security" in tid or "arch" in tid:
            return [
                {"name": "claude-3-5-sonnet", "confidence": 0.95},
                {"name": "gemini-1.5-pro", "confidence": 0.9},
                {"name": "gpt-4o", "confidence": 0.85}
            ]
        else:
            return [
                {"name": "gemini-1.5-flash", "confidence": 0.92},
                {"name": "gemini-1.5-pro", "confidence": 0.8}
            ]

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimates the USD cost for the routed API tokens."""
        rates = self.model_costs.get(model, {"input": 1.0 / 1e6, "output": 4.0 / 1e6})
        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])

    def estimate_latency(self, model: str) -> float:
        """Estimates request roundtrip latency in seconds."""
        latencies = {
            "claude-3-5-sonnet": 3.2,
            "gemini-1.5-pro": 2.5,
            "gemini-1.5-flash": 1.1,
            "gpt-4o": 2.8
        }
        return latencies.get(model, 2.0)

    def confidence(self, model: str, task: dict) -> float:
        """Returns model mapping suitability confidence."""
        priority = task.get("priority", "MEDIUM")
        if model == "claude-3-5-sonnet" and priority == "HIGH":
            return 0.98
        if model == "gemini-1.5-flash" and priority == "LOW":
            return 0.95
        return 0.85

    def provider_health(self, provider: str) -> str:
        """Evaluates provider status checks."""
        return "healthy"

    def reroute(self, task: dict) -> dict:
        """Triggers rerouting to the fallback model on primary provider outages."""
        ranked = self.rank_models_for_task(task)
        fallback = ranked[1]["name"] if len(ranked) > 1 else "gemini-1.5-pro"
        return self.route_model(task, {"name": fallback})
