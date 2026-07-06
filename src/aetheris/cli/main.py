"""
Aetheris CLI — Global Click/Rich Terminal Interface
Renders real-time progress animations and manages kernel daemon state.
"""
import sys
import time
from pathlib import Path
import click
from rich.console import Console
from rich.status import Status
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from aetheris.intelligence.repository import DiscoveryEngine
from aetheris.kernel.core import KernelController

# Force UTF-8 encoding on Windows to prevent cp1252 errors with Rich's
# braille spinner characters and styled output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)
controller = KernelController()

ASCII_LOGO = r"""
     _    _____ _____ _   _ _____ ____  ___ ____
    / \  | ____|_   _| | | | ____|  _ \|_ _/ ___|
   / _ \ |  _|   | | | |_| |  _| | |_) || |\___ \
  / ___ \| |___  | | |  _  | |___|  _ < | | ___) |
 /_/   \_\_____|  |_| |_| |_|_____|_| \_\___|____/
"""


def print_banner():
    """Print the branded Aetheris ASCII art header."""
    console.print(f"[bold cyan]{ASCII_LOGO}[/bold cyan]")
    console.print("[dim cyan]             Aetheris Engineering Hypervisor | AEKS Core v1.0.0[/dim cyan]\n")


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Aetheris Core CLI Interface Orchestrator."""
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("Run [yellow]aetheris --help[/yellow] to inspect valid operational system commands.")


@main.command()
def init():
    """Scaffolds structural repository directory execution spaces."""
    print_banner()
    dot_aetheris = Path(".aetheris")
    if dot_aetheris.exists():
        console.print("[bold yellow]![/bold yellow] Active engineering workspace boundary already mapped here.")
        return

    subdirs = ["progress", "skills", "rfcs", "specs", "architecture", "logs", "cache"]
    with Status("[bold green]Bootstrapping repository tracking directories...", console=console):
        for folder in subdirs:
            (dot_aetheris / folder).mkdir(parents=True, exist_ok=True)
            time.sleep(0.04)

    console.print("[bold green][OK][/bold green] Deep engineering workspace infrastructure successfully generated.")


@main.command()
def analyze():
    """Runs a recursive, real-time file tree audit using streaming spinners."""
    print_banner()
    console.print("[bold blue]Initiating Workspace Intelligence Pipeline...[/bold blue]\n")
    engine = DiscoveryEngine()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(description="Scanning file system structures...", total=None)

        def run_update(scanned_file):
            # Shorten paths visually during live operations for readability
            display_name = scanned_file[-45:] if len(scanned_file) > 45 else scanned_file
            progress.update(task, description=f"[cyan]Indexing:[/cyan] ...{display_name}")
            time.sleep(0.001)

        metrics = engine.dynamic_scan(progress_callback=run_update)

    console.print("\n[bold green][OK] Repository footprint mapped successfully.[/bold green]\n")

    table = Table(title="Dynamic Artifact Matrix", title_style="bold magenta")
    table.add_column("Registry Domain Classification", style="cyan")
    table.add_column("Active Structural Count", style="green", justify="right")

    table.add_row("Engineering Capability Skills", str(metrics["counts"]["skills"]))
    table.add_row("Structural Request For Comments (RFCs)", str(metrics["counts"]["rfcs"]))
    table.add_row("Technical Interface Specifications (SPECs)", str(metrics["counts"]["specs"]))
    table.add_row("Tracked Source Development Code Files", str(metrics["counts"]["source_files"]))

    console.print(table)


@main.command()
def start():
    """Enables Aetheris execution management, capturing code generation tasks."""
    print_banner()
    if controller.is_running():
        console.print(f"[bold yellow]![/bold yellow] Core daemon active at process id: {controller.get_active_pid()}")
        return

    with Status("[bold green]Spinning up background context compression brokers...", console=console):
        pid = controller.spawn_daemon()
        time.sleep(0.8)

    console.print(f"[bold green][OK] Aetheris Hypervisor successfully locked onto system PID: [cyan]{pid}[/cyan][/bold green]")
    console.print("> [bold magenta]STATUS: CODING LIFECYCLE ROUTED THROUGH AETHERIS HYPERVISOR[/bold magenta]")
    console.print("  [dim]Capability Registry, decoupled providers, and AEKS v1.0 Definition of Done active.[/dim]")


@main.command()
def stop():
    """Shuts down background daemons, restoring default workflow routing paths."""
    print_banner()
    if not controller.is_running():
        console.print("[bold yellow]![/bold yellow] No running Aetheris operational server instances found.")
        return

    with Status("[bold red]Dismantling context compression routing layers...", console=console):
        success = controller.terminate_daemon()
        time.sleep(0.5)

    if success:
        console.print("[bold yellow][OK] Aetheris control plane successfully detached.[/bold yellow]")
        console.print("> [bold green]STATUS: CODING PROCESS REDIRECTED TO LOCAL IDE LLM CONFIGURATIONS[/bold green]")
        console.print("  [dim]Standard editor behavior restored. Advanced execution layer offline.[/dim]")
    else:
        console.print("[bold red]X[/bold red] Execution failure: unable to clear runtime daemon flags securely.")


@main.command()
def dashboard():
    """Prints the running telemetry portal url path constraints."""
    print_banner()
    if not controller.is_running():
        console.print("[bold red]X Server Core offline.[/bold red] Run [yellow]aetheris start[/yellow] to open tracking views.")
        return
    console.print("Live Metrics Workspace Address: [bold cyan]http://localhost:8448[/bold cyan]")


@main.command()
@click.argument('name', required=False)
def skill(name):
    """Inspects structural capabilities currently tracked by the analyzer."""
    print_banner()
    engine = DiscoveryEngine()
    metrics = engine.dynamic_scan()
    skills = metrics["artifacts"]["skills"]

    if not skills:
        console.print("[bold yellow]![/bold yellow] No active registry skills located.")
        return

    if not name:
        console.print(f"[bold cyan]Discovered Skills Matrix ({len(skills)}):[/bold cyan]")
        for item in sorted(skills):
            console.print(f" - {Path(item).stem}")
    else:
        query = name.lower()
        matches = [s for s in skills if query in Path(s).stem.lower()]
        if matches:
            console.print(f"[bold green]Matching Capabilities Found ({len(matches)}):[/bold green]")
            for item in matches:
                console.print(f" - [cyan]{item}[/cyan]")
        else:
            console.print(f"[bold red]X[/bold red] No registered system capability fits query identifier: '{name}'")


if __name__ == '__main__':
    main()
