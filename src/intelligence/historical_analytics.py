import json
from pathlib import Path
from typing import Dict, Any, List

class HistoricalAnalytics:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        self.memory_dir = self.workspace_path / ".aetheris" / "memory"
        self.reports_dir = self.workspace_path / ".aetheris" / "reports"
        
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.memory_dir / "experience.json"

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return []

    def _save_history(self, history: List[Dict[str, Any]]):
        self.history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def record_session(self, session_metrics: Dict[str, Any]):
        """
        Append a new execution run to the history.
        """
        history = self._load_history()
        history.append(session_metrics)
        self._save_history(history)
        
        # Trigger report exports
        self.export_reports(history)

    def calculate_trends(self, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate running averages and historical trends.
        """
        history = history or self._load_history()
        if not history:
            return {
                "average_tokens_per_project": 0.0,
                "average_cost": 0.0,
                "average_latency": 0.0,
                "average_repository_coverage": 0.0,
                "average_skill_utilization": 0.0,
                "average_rfc_utilization": 0.0,
                "average_spec_utilization": 0.0,
                "average_context_reduction": 0.0,
                "average_engineering_score": 0.0,
                "average_production_readiness": 0.0,
                "session_count": 0
            }
            
        count = len(history)
        total_tokens = sum(s.get("total_tokens", 0) for s in history)
        total_cost = sum(s.get("cost", 0.0) for s in history)
        total_latency = sum(s.get("latency", 0.0) for s in history)
        total_repo_cov = sum(s.get("repository_coverage", 0.0) for s in history)
        total_skill_util = sum(s.get("skill_utilization", 0.0) for s in history)
        total_rfc_util = sum(s.get("rfc_utilization", 0.0) for s in history)
        total_spec_util = sum(s.get("spec_utilization", 0.0) for s in history)
        total_reduction = sum(s.get("context_reduction", 0.0) for s in history)
        total_eng_score = sum(s.get("engineering_score", 0.0) for s in history)
        total_prod_readiness = sum(s.get("production_readiness", 0.0) for s in history)
        
        return {
            "average_tokens_per_project": round(total_tokens / count, 2),
            "average_cost": round(total_cost / count, 4),
            "average_latency": round(total_latency / count, 3),
            "average_repository_coverage": round(total_repo_cov / count, 2),
            "average_skill_utilization": round(total_skill_util / count, 2),
            "average_rfc_utilization": round(total_rfc_util / count, 2),
            "average_spec_utilization": round(total_spec_util / count, 2),
            "average_context_reduction": round(total_reduction / count, 2),
            "average_engineering_score": round(total_eng_score / count, 2),
            "average_production_readiness": round(total_prod_readiness / count, 2),
            "session_count": count
        }

    def export_reports(self, history: List[Dict[str, Any]]):
        """
        Write analytical files defined in ATIB directive.
        """
        latest = history[-1] if history else {}
        trends = self.calculate_trends(history)
        
        # 1. token_report.json
        token_report = {
            "input_tokens": latest.get("input_tokens", 0),
            "output_tokens": latest.get("output_tokens", 0),
            "total_tokens": latest.get("total_tokens", 0),
            "cached_tokens": latest.get("cached_tokens", 0),
            "reasoning_tokens": latest.get("reasoning_tokens", 0)
        }
        (self.reports_dir / "token_report.json").write_text(json.dumps(token_report, indent=2))
        
        # 2. benchmark.json
        benchmark_report = {
            "repository_size_bytes": latest.get("repository_size_bytes", 0),
            "total_files": latest.get("total_files", 0),
            "files_used": latest.get("files_used", 0),
            "context_reduction_pct": latest.get("context_reduction", 0.0)
        }
        (self.reports_dir / "benchmark.json").write_text(json.dumps(benchmark_report, indent=2))
        
        # 3. engineering_metrics.json
        eng_metrics = {
            "engineering_score": latest.get("engineering_score", 0.0),
            "production_readiness": latest.get("production_readiness", 0.0)
        }
        (self.reports_dir / "engineering_metrics.json").write_text(json.dumps(eng_metrics, indent=2))
        
        # 4. repository_metrics.json
        repo_metrics = {
            "skills_scanned": latest.get("skills_scanned", 0),
            "skills_used": latest.get("skills_used", 0),
            "rfcs_used": latest.get("rfcs_used", 0),
            "specs_used": latest.get("specs_used", 0)
        }
        (self.reports_dir / "repository_metrics.json").write_text(json.dumps(repo_metrics, indent=2))
        
        # 5. cost_report.json
        cost_report = {
            "session_cost": latest.get("cost", 0.0),
            "accumulated_cost": sum(s.get("cost", 0.0) for s in history)
        }
        (self.reports_dir / "cost_report.json").write_text(json.dumps(cost_report, indent=2))
        
        # 6. performance_report.json
        perf_report = {
            "latency_seconds": latest.get("latency", 0.0),
            "average_latency": trends["average_latency"]
        }
        (self.reports_dir / "performance_report.json").write_text(json.dumps(perf_report, indent=2))
        
        # 7. historical_trends.json
        (self.reports_dir / "historical_trends.json").write_text(json.dumps(trends, indent=2))
        
        # 8. dashboard_metrics.json
        dash_metrics = {
            "current_model": latest.get("model", "unknown"),
            "live_tokens": latest.get("total_tokens", 0),
            "live_cost": latest.get("cost", 0.0),
            "engineering_score": latest.get("engineering_score", 0.0)
        }
        (self.reports_dir / "dashboard_metrics.json").write_text(json.dumps(dash_metrics, indent=2))
