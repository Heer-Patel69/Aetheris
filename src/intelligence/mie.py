"""
ModelIntelligenceEngine (MIE) — SPEC-047 Production Implementation.

Maintains a live model registry, scores candidates on capability/quality/latency/cost,
selects optimal model per task, and supports a full fallback chain.
All selection decisions are emitted to the EventStore.
"""
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ModelEntry:
    provider: str                       # google|anthropic|openai|ollama|lm_studio
    model_id: str                       # e.g. gemini-1.5-flash
    display_name: str
    capabilities: List[str] = field(default_factory=list)
    context_window: int = 128000        # tokens
    cost_input_per_1m: float = 0.0      # USD per 1M input tokens
    cost_output_per_1m: float = 0.0     # USD per 1M output tokens
    p95_latency_ms: float = 2000.0
    quality_score: float = 0.85         # 0–1, updated by SBE
    available: bool = True
    tier: str = "balanced"              # fast|balanced|quality

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_DEFAULT_REGISTRY: List[ModelEntry] = [
    ModelEntry(
        provider="google", model_id="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        capabilities=["reasoning", "long_context", "multimodal", "code", "analysis"],
        context_window=2_000_000, cost_input_per_1m=1.25, cost_output_per_1m=5.0,
        p95_latency_ms=4000, quality_score=0.96, tier="quality",
    ),
    ModelEntry(
        provider="google", model_id="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        capabilities=["speed", "code", "multimodal", "analysis"],
        context_window=1_000_000, cost_input_per_1m=0.075, cost_output_per_1m=0.30,
        p95_latency_ms=1200, quality_score=0.88, tier="fast",
    ),
    ModelEntry(
        provider="google", model_id="gemini-1.5-flash",
        display_name="Gemini 1.5 Flash",
        capabilities=["speed", "code", "multimodal"],
        context_window=1_000_000, cost_input_per_1m=0.075, cost_output_per_1m=0.30,
        p95_latency_ms=1500, quality_score=0.85, tier="fast",
    ),
    ModelEntry(
        provider="anthropic", model_id="claude-3-7-sonnet",
        display_name="Claude 3.7 Sonnet",
        capabilities=["coding", "reasoning", "analysis", "security"],
        context_window=200_000, cost_input_per_1m=3.0, cost_output_per_1m=15.0,
        p95_latency_ms=3500, quality_score=0.94, tier="quality",
    ),
    ModelEntry(
        provider="anthropic", model_id="claude-3-5-sonnet",
        display_name="Claude 3.5 Sonnet",
        capabilities=["coding", "reasoning", "analysis"],
        context_window=200_000, cost_input_per_1m=3.0, cost_output_per_1m=15.0,
        p95_latency_ms=3000, quality_score=0.92, tier="balanced",
    ),
    ModelEntry(
        provider="openai", model_id="gpt-4o",
        display_name="GPT-4o",
        capabilities=["tool_use", "general", "code", "multimodal"],
        context_window=128_000, cost_input_per_1m=5.0, cost_output_per_1m=15.0,
        p95_latency_ms=2500, quality_score=0.91, tier="balanced",
    ),
    ModelEntry(
        provider="ollama", model_id="codellama:13b",
        display_name="CodeLlama 13B (local)",
        capabilities=["code", "speed"],
        context_window=16_000, cost_input_per_1m=0.0, cost_output_per_1m=0.0,
        p95_latency_ms=5000, quality_score=0.72, tier="fast",
        available=False,
    ),
]


class ModelIntelligenceEngine:
    """
    SPEC-047 Model Intelligence Engine.

    Selection scoring:
        score = (capability_match × 0.4) + (quality_score × 0.3)
                + (1/norm_latency × 0.2) + (1/norm_cost × 0.1)
    """

    def __init__(
        self,
        workspace_path: str = ".",
        event_store=None,
        session_id: str = "",
    ):
        self.workspace  = Path(workspace_path).resolve()
        self._store     = event_store
        self._session   = session_id
        self._reg_dir   = self.workspace / ".aetheris" / "models"
        self._reg_dir.mkdir(parents=True, exist_ok=True)
        self._reg_file  = self._reg_dir / "model.registry.json"
        self._registry: List[ModelEntry] = []
        self._load_registry()

    # ── registry persistence ──────────────────────────────────────────────────

    def _load_registry(self):
        if self._reg_file.exists():
            try:
                raw = json.loads(self._reg_file.read_text(encoding="utf-8"))
                self._registry = [ModelEntry(**m) for m in raw.get("models", [])]
                return
            except Exception:
                pass
        self._registry = list(_DEFAULT_REGISTRY)
        self._save_registry()

    def _save_registry(self):
        data = {"models": [m.to_dict() for m in self._registry],
                "updated_at": time.time()}
        self._reg_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ── capability scoring ────────────────────────────────────────────────────

    def _capability_match(self, model: ModelEntry, required: List[str]) -> float:
        if not required:
            return 1.0
        matched = sum(1 for cap in required if cap in model.capabilities)
        return matched / len(required)

    def _score(self, model: ModelEntry, required_caps: List[str],
               max_latency: float, max_cost: float) -> float:
        cap   = self._capability_match(model, required_caps)
        qual  = model.quality_score
        lat   = 1.0 - (min(model.p95_latency_ms, max_latency) / max_latency)
        cost  = 1.0 - (min(model.cost_input_per_1m, max_cost) / max(max_cost, 0.001))
        return (cap * 0.4) + (qual * 0.3) + (lat * 0.2) + (cost * 0.1)

    # ── selection ─────────────────────────────────────────────────────────────

    def select_model(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
        context_tokens: int = 0,
        tier_override: Optional[str] = None,   # fast|balanced|quality
        exclude_providers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Select the optimal model for a task. Returns selection dict with
        model_id, provider, score, and rationale.
        """
        caps    = required_capabilities or []
        exclude = set(exclude_providers or [])

        candidates = [
            m for m in self._registry
            if m.available
            and m.context_window >= context_tokens
            and m.provider not in exclude
            and (tier_override is None or m.tier == tier_override)
        ]

        if not candidates:
            # fallback: relax tier constraint
            candidates = [m for m in self._registry
                          if m.available and m.context_window >= context_tokens]

        if not candidates:
            # last resort: primary default
            return self._fallback_selection(task_type)

        max_lat  = max(m.p95_latency_ms for m in candidates) or 1.0
        max_cost = max(m.cost_input_per_1m for m in candidates) or 0.001

        scored = sorted(
            candidates,
            key=lambda m: self._score(m, caps, max_lat, max_cost),
            reverse=True,
        )
        best   = scored[0]
        score  = self._score(best, caps, max_lat, max_cost)

        result = {
            "model_id":     best.model_id,
            "provider":     best.provider,
            "display_name": best.display_name,
            "tier":         best.tier,
            "score":        round(score, 4),
            "capabilities": best.capabilities,
            "context_window": best.context_window,
            "cost_input_per_1m": best.cost_input_per_1m,
            "task_type":    task_type,
            "rationale": (
                f"Selected {best.display_name} "
                f"(capability={round(self._capability_match(best, caps),2)}, "
                f"quality={best.quality_score}, tier={best.tier})"
            ),
        }

        self._emit_selection(result)
        return result

    def _fallback_selection(self, task_type: str) -> Dict[str, Any]:
        return {
            "model_id": "gemini-1.5-flash", "provider": "google",
            "display_name": "Gemini 1.5 Flash (fallback)", "tier": "fast",
            "score": 0.5, "task_type": task_type,
            "rationale": "Fallback: no capable model found",
        }

    # ── fallback chain ────────────────────────────────────────────────────────

    def get_fallback_chain(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Return ordered list: primary → secondary → local fallback."""
        chain = []
        excluded: List[str] = []
        for _ in range(3):
            sel = self.select_model(
                task_type,
                required_capabilities=required_capabilities,
                exclude_providers=excluded,
            )
            chain.append(sel)
            excluded.append(sel["provider"])
        return chain

    # ── registry management ───────────────────────────────────────────────────

    def update_quality_score(self, model_id: str, new_score: float):
        for m in self._registry:
            if m.model_id == model_id:
                m.quality_score = max(0.0, min(1.0, new_score))
                self._save_registry()
                return

    def mark_unavailable(self, model_id: str):
        for m in self._registry:
            if m.model_id == model_id:
                m.available = False
                self._save_registry()
                return

    def mark_available(self, model_id: str):
        for m in self._registry:
            if m.model_id == model_id:
                m.available = True
                self._save_registry()
                return

    def list_models(self, available_only: bool = False) -> List[Dict[str, Any]]:
        models = self._registry
        if available_only:
            models = [m for m in models if m.available]
        return [m.to_dict() for m in models]

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        for m in self._registry:
            if m.model_id == model_id:
                return m.to_dict()
        return None

    def get_optimal_model(self, task_description: str,
                          context_size_tokens: int = 0) -> Dict[str, Any]:
        """Compatibility wrapper used by kernel/core.py."""
        return self.select_model(
            task_type=task_description,
            context_tokens=context_size_tokens,
        )

    # ── event emission ────────────────────────────────────────────────────────

    def _emit_selection(self, selection: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="MODELS",
                event_type="ModelSelected",
                payload=selection,
                session_id=self._session,
            )
        except Exception:
            pass
