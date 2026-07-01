import json
import os
from pathlib import Path

class ModelIntelligenceEngine:
    def __init__(self, workspace_dir: str = "c:/AI/Agency owner/aetheris"):
        self.workspace_dir = Path(workspace_dir)
        self.registry_dir = self.workspace_dir / ".aetheris" / "models"
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_registry_file = self.registry_dir / "model.registry.json"
        self.capabilities_file = self.registry_dir / "model.capabilities.json"
        
        self._bootstrap_registries()
        
    def _bootstrap_registries(self):
        if not self.model_registry_file.exists():
            default_registry = {
                "models": [
                    {"id": "gemini-2.5-pro", "provider": "google", "context_window": 2000000},
                    {"id": "gemini-2.5-flash", "provider": "google", "context_window": 1000000},
                    {"id": "claude-3-5-sonnet", "provider": "anthropic", "context_window": 200000},
                    {"id": "gpt-4o", "provider": "openai", "context_window": 128000}
                ]
            }
            self.model_registry_file.write_text(json.dumps(default_registry, indent=2), encoding="utf-8")
            
        if not self.capabilities_file.exists():
            default_capabilities = {
                "capabilities": {
                    "gemini-2.5-pro": ["reasoning", "long_context", "multimodal"],
                    "gemini-2.5-flash": ["speed", "multimodal"],
                    "claude-3-5-sonnet": ["coding", "reasoning"],
                    "gpt-4o": ["tool_use", "general"]
                }
            }
            self.capabilities_file.write_text(json.dumps(default_capabilities, indent=2), encoding="utf-8")
            
    def get_optimal_model(self, task_description: str, context_size_tokens: int) -> dict:
        # Simple rule-based model intelligence recommendation (cost-optimized selection)
        with open(self.model_registry_file, "r", encoding="utf-8") as f:
            registry = json.load(f)
            
        fitting_models = [m for m in registry["models"] if m["context_window"] >= context_size_tokens]
        if fitting_models:
            # Select model with the smallest context window that fits
            selected = min(fitting_models, key=lambda m: m["context_window"])
            return {
                "model_id": selected["id"],
                "provider": selected["provider"],
                "confidence": 0.95
            }
                
        # Default fallback
        return {
            "model_id": "gemini-2.5-pro",
            "provider": "google",
            "confidence": 0.50
        }
