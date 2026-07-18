"""
MissionControl — Phase 4 Live Engineering Operating System.

Three dashboard modes, all fed from live ProjectionEngine data:
  GlobalDashboard    — across all workspaces
  WorkspaceDashboard — current workspace
  SessionDashboard   — active execution session

All data comes from runtime projections. Zero hardcoded values.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.projection_engine import ProjectionEngine
from runtime.analytics_engine import AnalyticsEngine
from runtime.replay_engine import ReplayEngine
from intelligence.insights import EngineeringInsightsEngine


class MissionControlPanel:
    """Base class for a Mission Control panel."""

    name: str = "base"

    def __init__(self, projections: ProjectionEngine):
        self._proj = projections

    def render(self) -> Dict[str, Any]:
        """Return the live panel data dict."""
        raise NotImplementedError

    def _p(self, name: str) -> Dict[str, Any]:
        snap = self._proj.get(name)
        return snap["data"] if snap else {}


# ── Executive Overview Panel ──────────────────────────────────────────────────

class ExecutiveOverviewPanel(MissionControlPanel):
    name = "executive_overview"

    def render(self) -> Dict[str, Any]:
        d = self._p("executive_overview")
        return {
            "panel":              self.name,
            "system_status":      d.get("system_status", "idle"),
            "sessions_total":     d.get("sessions_total", 0),
            "sessions_active":    d.get("sessions_active", 0),
            "executions_total":   d.get("executions_total", 0),
            "executions_running": d.get("executions_running", 0),
            "skills_loaded":      d.get("skills_loaded", 0),
            "errors_total":       d.get("errors_total", 0),
            "active_session":     d.get("active_session"),
        }


# ── Runtime Inspector Panel ───────────────────────────────────────────────────

class RuntimeInspectorPanel(MissionControlPanel):
    name = "runtime_inspector"

    def render(self) -> Dict[str, Any]:
        d = self._p("runtime_inspector")
        return {
            "panel":                  self.name,
            "active_stage":           d.get("active_stage"),
            "active_session":         d.get("active_session"),
            "stage_started_at":       d.get("stage_started_at"),
            "last_completed_stage":   d.get("last_completed_stage"),
            "last_stage_duration_ms": d.get("last_stage_duration_ms", 0),
            "last_error":             d.get("last_error"),
        }


# ── Engineering Timeline Panel ────────────────────────────────────────────────

class EngineeringTimelinePanel(MissionControlPanel):
    name = "engineering_timeline"

    def render(self) -> Dict[str, Any]:
        d = self._p("engineering_timeline")
        events = d.get("events", [])
        return {
            "panel":        self.name,
            "total_events": d.get("total_events", 0),
            "recent_events": events[-20:],
        }


# ── Token Analytics Panel ─────────────────────────────────────────────────────

class TokenAnalyticsPanel(MissionControlPanel):
    name = "token_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("token_analytics")
        return {
            "panel":         self.name,
            "input_tokens":  d.get("input_tokens",  0),
            "output_tokens": d.get("output_tokens", 0),
            "total_tokens":  d.get("total_tokens",  0),
        }


# ── Cost Analytics Panel ──────────────────────────────────────────────────────

class CostAnalyticsPanel(MissionControlPanel):
    name = "cost_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("cost_analytics")
        return {
            "panel":                self.name,
            "total_cost_usd":       d.get("total_cost_usd", 0.0),
            "budget_usd":           d.get("budget_usd", 5.0),
            "budget_remaining_usd": d.get("budget_remaining_usd", 5.0),
            "model_costs":          d.get("model_costs", {}),
        }


# ── Model Analytics Panel ─────────────────────────────────────────────────────

class ModelAnalyticsPanel(MissionControlPanel):
    name = "model_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("model_analytics")
        models = d.get("models", {})
        top = sorted(models.items(), key=lambda x: x[1].get("calls", 0), reverse=True)
        return {
            "panel":       self.name,
            "models":      models,
            "top_model":   top[0][0] if top else None,
            "total_calls": sum(m.get("calls", 0) for m in models.values()),
        }


# ── Skill Analytics Panel ─────────────────────────────────────────────────────

class SkillAnalyticsPanel(MissionControlPanel):
    name = "skill_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("skill_analytics")
        skills = d.get("skills", {})
        top = sorted(skills.items(), key=lambda x: x[1], reverse=True)
        return {
            "panel":        self.name,
            "skills":       skills,
            "top_skill":    top[0][0] if top else None,
            "unique_skills": len(skills),
        }


# ── Verification Center Panel ─────────────────────────────────────────────────

class VerificationCenterPanel(MissionControlPanel):
    name = "verification_center"

    def render(self) -> Dict[str, Any]:
        d = self._p("verification_center")
        total  = d.get("gates_passed", 0) + d.get("gates_failed", 0)
        rate   = round(d.get("gates_passed", 0) / max(total, 1) * 100, 1)
        return {
            "panel":         self.name,
            "gates_passed":  d.get("gates_passed", 0),
            "gates_failed":  d.get("gates_failed", 0),
            "pass_rate_pct": rate,
            "recent":        d.get("recent", [])[-10:],
        }


# ── Memory Analytics Panel ────────────────────────────────────────────────────

class MemoryAnalyticsPanel(MissionControlPanel):
    name = "memory_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("memory_analytics")
        return {
            "panel":       self.name,
            "ekb_entries": d.get("ekb_entries", 0),
            "checkpoints": d.get("checkpoints", 0),
            "recent_ops":  d.get("memory_ops", [])[-10:],
        }


# ── Engineering Insights Panel ────────────────────────────────────────────────

class EngineeringInsightsPanel(MissionControlPanel):
    name = "engineering_insights"

    def render(self) -> Dict[str, Any]:
        d = self._p("engineering_insights")
        insights = d.get("insights", [])
        return {
            "panel":          self.name,
            "total_insights": len(insights),
            "recent":         insights[-10:],
        }


# ── RFC / SPEC Analytics Panels ───────────────────────────────────────────────

class RFCAnalyticsPanel(MissionControlPanel):
    name = "rfc_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("rfc_analytics")
        rfcs = d.get("rfcs", {})
        top = sorted(rfcs.items(), key=lambda x: x[1], reverse=True)[:5]
        return {"panel": self.name, "rfcs": rfcs, "top_5": top}


class SPECAnalyticsPanel(MissionControlPanel):
    name = "spec_analytics"

    def render(self) -> Dict[str, Any]:
        d = self._p("spec_analytics")
        specs = d.get("specs", {})
        top = sorted(specs.items(), key=lambda x: x[1], reverse=True)[:5]
        return {"panel": self.name, "specs": specs, "top_5": top}


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard Modes
# ══════════════════════════════════════════════════════════════════════════════

ALL_PANELS = [
    ExecutiveOverviewPanel,
    RuntimeInspectorPanel,
    EngineeringTimelinePanel,
    TokenAnalyticsPanel,
    CostAnalyticsPanel,
    ModelAnalyticsPanel,
    SkillAnalyticsPanel,
    VerificationCenterPanel,
    MemoryAnalyticsPanel,
    EngineeringInsightsPanel,
    RFCAnalyticsPanel,
    SPECAnalyticsPanel,
]


class GlobalDashboard:
    """Mode 1: Global view across all workspaces and sessions."""

    def __init__(self, projections: ProjectionEngine,
                 analytics: AnalyticsEngine,
                 insights: EngineeringInsightsEngine):
        self._panels  = [cls(projections) for cls in ALL_PANELS]
        self._analytics = analytics
        self._insights  = insights

    def render(self) -> Dict[str, Any]:
        panels = {p.name: p.render() for p in self._panels}
        global_stats = self._analytics.global_analytics()
        return {
            "mode":         "global",
            "rendered_at":  time.time(),
            "panels":       panels,
            "global_stats": global_stats,
        }


class WorkspaceDashboard:
    """Mode 2: Workspace-scoped view."""

    def __init__(self, workspace_id: str, projections: ProjectionEngine,
                 analytics: AnalyticsEngine):
        self._workspace_id = workspace_id
        self._panels     = [cls(projections) for cls in ALL_PANELS]
        self._analytics  = analytics

    def render(self) -> Dict[str, Any]:
        panels = {p.name: p.render() for p in self._panels}
        ws_stats = self._analytics.workspace_analytics(self._workspace_id)
        return {
            "mode":          "workspace",
            "workspace_id":  self._workspace_id,
            "rendered_at":   time.time(),
            "panels":        panels,
            "workspace_stats": ws_stats,
        }


class SessionDashboard:
    """Mode 3: Single-session execution view."""

    def __init__(self, session_id: str, projections: ProjectionEngine,
                 analytics: AnalyticsEngine, replay: ReplayEngine):
        self._session_id = session_id
        self._panels     = [cls(projections) for cls in ALL_PANELS]
        self._analytics  = analytics
        self._replay     = replay

    def render(self) -> Dict[str, Any]:
        panels = {p.name: p.render() for p in self._panels}
        sess_analytics = self._analytics.session_analytics(self._session_id)
        timeline = self._replay.reconstruct_session(self._session_id)
        return {
            "mode":              "session",
            "session_id":        self._session_id,
            "rendered_at":       time.time(),
            "panels":            panels,
            "session_analytics": sess_analytics,
            "timeline":          timeline.to_dict(),
        }


class MissionControl:
    """
    Entry-point that creates and manages all three dashboard modes.
    All data sourced exclusively from live runtime projections.
    """

    def __init__(
        self,
        workspace_path: str,
        projections: ProjectionEngine,
        analytics: AnalyticsEngine,
        replay: ReplayEngine,
        event_store,
        workspace_id: str = "",
    ):
        self.workspace_id = workspace_id or workspace_path
        insights_engine   = EngineeringInsightsEngine(event_store)

        self.global_dashboard    = GlobalDashboard(projections, analytics, insights_engine)
        self.workspace_dashboard = WorkspaceDashboard(workspace_id, projections, analytics)
        self._projections        = projections
        self._analytics          = analytics
        self._replay             = replay

    def session_dashboard(self, session_id: str) -> SessionDashboard:
        return SessionDashboard(
            session_id, self._projections, self._analytics, self._replay
        )

    def render_global(self) -> Dict[str, Any]:
        return self.global_dashboard.render()

    def render_workspace(self) -> Dict[str, Any]:
        return self.workspace_dashboard.render()

    def render_session(self, session_id: str) -> Dict[str, Any]:
        return self.session_dashboard(session_id).render()

    def render_panel(self, panel_name: str) -> Optional[Dict[str, Any]]:
        snap = self._projections.get(panel_name)
        return snap["data"] if snap else None

    def list_panels(self) -> List[str]:
        return [cls.name for cls in ALL_PANELS]
