from typing import Dict, Any

class DashboardMetrics:
    def __init__(self):
        pass
        
    def generate_dashboard(
        self,
        token_intel_summary: Dict[str, Any],
        repo_metrics_summary: Dict[str, Any],
        historical_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize token, repository, and historical analytics into a single live dashboard view.
        """
        cov = repo_metrics_summary.get("coverage", {})
        
        return {
            "current_model": token_intel_summary.get("model", "unknown"),
            "current_platform": "Antigravity",
            "live_token_usage": token_intel_summary.get("total_tokens", 0),
            "current_cost": token_intel_summary.get("cost", 0.0),
            "repository_coverage": cov.get("repository_coverage", 0.0),
            "skill_utilization": cov.get("skill_coverage", 0.0),
            "rfc_utilization": cov.get("rfc_coverage", 0.0),
            "spec_utilization": cov.get("spec_coverage", 0.0),
            "latency_seconds": token_intel_summary.get("latency", 0.0),
            "context_usage_pct": token_intel_summary.get("context_window_usage_pct", 0.0),
            "historical_trends": historical_trends,
            "project_benchmark": {
                "repository_size_bytes": repo_metrics_summary.get("repository_size_bytes", 0),
                "total_files": repo_metrics_summary.get("total_files", 0),
                "files_used": repo_metrics_summary.get("files_used", 0)
            },
            "engineering_score": repo_metrics_summary.get("engineering_score", 0.0),
            "production_readiness": cov.get("deployment_coverage", 0.0)
        }
