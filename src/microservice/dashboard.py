import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text

from microservice.database import SessionLocal, WebhookDelivery

class TelemetryDashboard:
    """
    Renders a monochromatic, high-density minimal luxury terminal dashboard
    displaying microservice webhook telemetry. Inherits styling constraints
    directly from `src/config/theme_contract.json`.
    """

    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path).resolve()
        self.theme_path = self.workspace_root / "src" / "config" / "theme_contract.json"
        self.console = Console(force_terminal=True)
        self.theme_colors = self._load_theme_colors()

    def _load_theme_colors(self) -> dict:
        """Reads monochromatic tokens from the design system config."""
        if self.theme_path.exists():
            try:
                theme_data = json.loads(self.theme_path.read_text(encoding="utf-8"))
                return theme_data.get("theme", {}).get("colors", {})
            except Exception:
                pass
        # Safe fallback tokens
        return {
            "bg-core": "#0a0a0a",
            "brand-accent": "#ffffff",
            "text-secondary": "#a3a3a3",
            "success": "#a3e635",
            "error": "#f87171"
        }

    def render(self) -> None:
        """Queries the database and prints a beautifully structured Rich layout."""
        db = SessionLocal()
        try:
            total = db.query(WebhookDelivery).count()
            verified = db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "verified").count()
            failed = db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "failed").count()
            recent_deliveries = db.query(WebhookDelivery).order_by(WebhookDelivery.delivered_at.desc()).limit(5).all()
        finally:
            db.close()

        # Extract styles from theme mapping
        accent_color = self.theme_colors.get("brand-accent", "#ffffff")
        secondary_color = self.theme_colors.get("text-secondary", "#a3a3a3")
        success_color = self.theme_colors.get("success", "#a3e635")
        error_color = self.theme_colors.get("error", "#f87171")

        # Build Rich components using theme colors
        title_text = Text("AETHERIS SECURITY GATEWAY : CRYPTOGRAPHIC TELEMETRY", style=f"bold {accent_color}")
        
        # Stat cards table
        stat_table = Table.grid(expand=True)
        stat_table.add_column(ratio=1)
        stat_table.add_column(ratio=1)
        stat_table.add_column(ratio=1)
        
        stat_table.add_row(
            Panel(
                Text(f"\n{total}\n", style=f"bold {accent_color} justify=center", justify="center"),
                title="TOTAL Webhooks",
                title_align="left",
                border_style=f"{secondary_color}"
            ),
            Panel(
                Text(f"\n{verified}\n", style=f"bold {success_color} justify=center", justify="center"),
                title="VERIFIED Deliveries",
                title_align="left",
                border_style=f"{secondary_color}"
            ),
            Panel(
                Text(f"\n{failed}\n", style=f"bold {error_color} justify=center", justify="center"),
                title="FAILED Deliveries",
                title_align="left",
                border_style=f"{secondary_color}"
            )
        )

        # Recent activities table
        activity_table = Table(box=None, expand=True)
        activity_table.add_column("Delivery ID", style=f"{accent_color}")
        activity_table.add_column("Source IP Hash (Short)", style=f"{secondary_color}")
        activity_table.add_column("Status", style=f"bold {accent_color}")
        activity_table.add_column("Timestamp", style=f"{secondary_color}")

        for item in recent_deliveries:
            status_style = success_color if item.processing_status == "verified" else error_color
            status_text = Text(item.processing_status.upper(), style=f"bold {status_style}")
            activity_table.add_row(
                str(item.id),
                item.source_ip_hash[:8],
                status_text,
                item.delivered_at.strftime("%Y-%m-%d %H:%M:%S")
            )

        activity_panel = Panel(
            activity_table,
            title="RECENT SECURITY ACTIVITY RUNS",
            title_align="left",
            border_style=f"{secondary_color}"
        )

        # Render layout
        self.console.print("\n")
        self.console.print(Panel(title_text, border_style=f"{accent_color}"))
        self.console.print(stat_table)
        self.console.print(activity_panel)
        self.console.print("\n")

if __name__ == "__main__":
    import os
    dashboard = TelemetryDashboard(os.getcwd())
    dashboard.render()
