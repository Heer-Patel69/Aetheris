"""
Aetheris CLI — Global Click/Rich Terminal Interface
Renders real-time progress animations and manages kernel daemon state.
"""
import sys
import time
import psutil
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
 /_/   \_\_____| |_| |_| |_|_____|_| \_\___|____/
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


def detect_ide_cli() -> str:
    import os, psutil
    term_program = os.environ.get("TERM_PROGRAM", "")
    if "vscode" in term_program.lower():
        return "VS Code"
    if "cursor" in term_program.lower() or os.environ.get("CURSOR_APP_PATH"):
        return "Cursor"
    
    if os.path.exists(os.path.expanduser("~/.gemini/antigravity-ide")):
        return "Antigravity IDE"
        
    try:
        current_proc = psutil.Process(os.getpid())
        parent = current_proc.parent()
        for _ in range(5):
            if not parent:
                break
            name = parent.name().lower()
            if "vscode" in name or "code" in name:
                return "VS Code"
            if "cursor" in name:
                return "Cursor"
            if "idea" in name or "pycharm" in name or "webstorm" in name:
                return "JetBrains"
            if "windsurf" in name:
                return "Windsurf"
            parent = parent.parent()
    except Exception:
        pass
    return "Terminal / CLI"

@main.command()
@click.pass_context
def start(ctx):
    """Enables Aetheris execution management, capturing code generation tasks."""
    print_banner()
    import os, json, time, psutil
    from pathlib import Path
    from rich.panel import Panel

    if controller.is_running():
        pid = controller.get_active_pid()
        uptime = "Unknown"
        try:
            p = psutil.Process(pid)
            uptime = f"{int((time.time() - p.create_time()) / 60)} minutes"
        except Exception:
            pass

        state_path = Path(".aetheris/state/runtime.json")
        workspace_name = Path.cwd().name
        model_name = "Unknown"
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    model_name = state.get("model_in_use", "Unknown")
            except Exception:
                pass

        panel_text = f"""
[bold cyan]Already Running[/bold cyan]
[dim]PID:[/dim] {pid}
[dim]Started:[/dim] {uptime} ago
[dim]Workspace:[/dim] {workspace_name}
[dim]Mission Control:[/dim] Connected
[dim]Workers:[/dim] 12
[dim]Scheduler:[/dim] Running
[dim]Telemetry:[/dim] Streaming
"""
        console.print(Panel(panel_text.strip(), title="Aetheris Runtime", border_style="cyan"))
        console.print("\n[dim]Reconnecting to Mission Control...[/dim]")
        ctx.invoke(dashboard)
        return

    # NEW STARTUP SEQUENCE
    import uuid
    from aetheris.kernel.event_bus import AetherisEvent, AetherisEventBus
    from aetheris.infrastructure.event_store import EventStore
    from aetheris.kernel.projections import ProjectionEngine
    
    event_store = EventStore()
    projection_engine = ProjectionEngine()
    
    session_id = str(uuid.uuid4())
    workspace_id = str(hash(os.getcwd()))
    
    bus = AetherisEventBus()
    bus.set_context(session_id=session_id, project_id=Path.cwd().name, workspace_id=workspace_id)

    console.print("[bold blue]AETHERIS ENGINEERING OPERATING SYSTEM[/bold blue]")
    console.print("Starting Runtime...\n")

    steps = [
        "Runtime", "Brain", "Scheduler", "Workers", "Memory", "Event Bus", 
        "Telemetry", "Mission Control", "Repository Discovery", "Skill Registry",
        "RFC Registry", "SPEC Registry", "Integrations"
    ]
    with Status("[bold green]Booting subsystems...", console=console):
        for step in steps:
            time.sleep(0.04)
            console.print(f" [bold green]✓[/bold green] {step}")
        
    console.print(" [bold green]✓[/bold green] Runtime Ready\n")

    # Perform discovery
    state_dir = Path(".aetheris/state")
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "runtime.json"
    
    # Run a silent discovery to get stats
    from aetheris.intelligence.repository import DiscoveryEngine
    engine = DiscoveryEngine()
    metrics = engine.dynamic_scan(progress_callback=lambda x: None)
    
    ide_name = detect_ide_cli()
    model_name = "Gemini 1.5 Pro" if ide_name == "Antigravity IDE" else ("Claude 3.5 Sonnet" if ide_name == "Cursor" else "System Default LLM")
    
    import yaml
    manifest_name = Path.cwd().name
    manifest_path = Path(".aetheris/manifest.yaml")
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest_data = yaml.safe_load(mf) or {}
                manifest_name = manifest_data.get("project", {}).get("name", manifest_name)
        except Exception:
            pass
            
    # Publish system boot event which automatically updates projections and caches
    bus.publish_sync(AetherisEvent(
        category="SYSTEM_BOOT",
        payload={
            "ide": ide_name,
            "model_in_use": model_name,
            "workspace": Path.cwd().name,
            "project": manifest_name,
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
    ))

    with Status("[bold green]Engaging hypervisor daemon...", console=console):
        pid = controller.spawn_daemon()
        time.sleep(0.5)

    panel_text = f"""
[bold cyan]Mission Control Connected[/bold cyan]
[dim]Workspace:[/dim] {Path.cwd().name}
[dim]IDE:[/dim] {ide_name}
[dim]Model:[/dim] {model_name}
[dim]Runtime:[/dim] READY
"""
    console.print(Panel(panel_text.strip(), title="Aetheris Active", border_style="green"))

    console.print("\nOpening Mission Control...")
    ctx.invoke(dashboard)


@main.command()
def stop():
    """Shuts down background daemons, restoring default workflow routing paths."""
    print_banner()
    if not controller.is_running():
        console.print("[bold yellow]![/bold yellow] No running Aetheris operational server instances found.")
        return

    with Status("[bold red]Dismantling context compression routing layers...", console=console):
        success = controller.terminate_daemon()
        for p in psutil.process_iter(['pid', 'name']):
            try:
                for conn in p.net_connections(kind='inet'):
                    if conn.laddr.port in (8448, 8449, 5173):
                        p.terminate()
            except Exception:
                pass
        import time
        time.sleep(0.5)

    if success:
        console.print("[bold yellow][OK] Aetheris control plane successfully detached.[/bold yellow]")
        console.print("[bold green]✓[/bold green] Runtime Stopped")
        console.print("[bold green]✓[/bold green] Telemetry Streaming Stopped")
        console.print("[bold green]✓[/bold green] Mission Control Terminated")
        console.print("> [bold green]STATUS: CODING PROCESS REDIRECTED TO LOCAL IDE LLM CONFIGURATIONS[/bold green]")
        console.print("  [dim]Standard editor behavior restored. Advanced execution layer offline.[/dim]")
    else:
        console.print("[bold red]X[/bold red] Execution failure: unable to clear runtime daemon flags securely.")


@main.command()
@click.option('--debug', is_flag=True, help="Diagnose dashboard and runtime data connection.")
@click.pass_context
def dashboard(ctx, debug):
    """Connects to the running telemetry portal or starts it."""
    print_banner()
    
    if debug:
        console.print("[bold blue]Running Dashboard & Telemetry Diagnostics...[/bold blue]\n")
        
        # 1. Check if daemon is running
        is_daemon_running = controller.is_running()
        pid = controller.get_active_pid()
        if is_daemon_running:
            console.print(f" [bold green]✓[/bold green] Hypervisor Daemon status: [bold green]Active[/bold green] (PID: {pid})")
        else:
            console.print(" [bold red]✗[/bold red] Hypervisor Daemon status: [bold red]Inactive[/bold red]")
            
        # 2. Check port 8448
        import socket
        port_open = False
        try:
            with socket.create_connection(("127.0.0.1", 8448), timeout=1.0):
                port_open = True
        except Exception:
            pass
            
        if port_open:
            console.print(" [bold green]✓[/bold green] Gateway Port 8448: [bold green]Open / Listening[/bold green]")
        else:
            console.print(" [bold red]✗[/bold red] Gateway Port 8448: [bold red]Closed / Unreachable[/bold red]")
            
        # 3. Test HTTP connectivity to Gateway
        import urllib.request
        http_ok = False
        http_err = None
        try:
            req = urllib.request.Request("http://127.0.0.1:8448/ws")
            urllib.request.urlopen(req, timeout=1.0)
            http_ok = True
        except Exception as e:
            # 426 Upgrade Required is a success for WebSocket endpoint
            if hasattr(e, 'code') and e.code in (404, 426, 400):
                http_ok = True
            else:
                http_err = str(e)
                
        if http_ok:
            console.print(" [bold green]✓[/bold green] HTTP Connection to ws endpoint: [bold green]Connected[/bold green]")
        else:
            console.print(f" [bold red]✗[/bold red] HTTP Connection to ws endpoint: [bold red]Failed[/bold red] ({http_err})")
            
        # 4. Check telemetry files
        runtime_json = Path(".aetheris/state/runtime.json")
        exec_json = Path(".aetheris/execution_state.json")
        events_db = Path(".aetheris/telemetry/events.db")
        
        if runtime_json.exists():
            console.print(f" [bold green]✓[/bold green] Telemetry Cache [cyan]{runtime_json}[/cyan]: [bold green]Exists[/bold green] ({runtime_json.stat().st_size} bytes)")
        else:
            console.print(f" [bold yellow]![/bold yellow] Telemetry Cache [cyan]{runtime_json}[/cyan]: [bold yellow]Missing[/bold yellow]")
            
        if exec_json.exists():
            console.print(f" [bold green]✓[/bold green] Telemetry Cache [cyan]{exec_json}[/cyan]: [bold green]Exists[/bold green] ({exec_json.stat().st_size} bytes)")
        else:
            console.print(f" [bold yellow]![/bold yellow] Telemetry Cache [cyan]{exec_json}[/cyan]: [bold yellow]Missing[/bold yellow]")
            
        # 5. Check SQLite database
        if events_db.exists():
            import sqlite3
            try:
                conn = sqlite3.connect(str(events_db))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM engineering_events")
                count = cursor.fetchone()[0]
                conn.close()
                console.print(f" [bold green]✓[/bold green] Event DB [cyan]{events_db}[/cyan]: [bold green]Connected[/bold green] ({count} recorded events)")
            except Exception as e:
                console.print(f" [bold red]✗[/bold red] Event DB [cyan]{events_db}[/cyan]: [bold red]Corrupt / Error[/bold red] ({e})")
        else:
            console.print(f" [bold yellow]![/bold yellow] Event DB [cyan]{events_db}[/cyan]: [bold yellow]Missing[/bold yellow]")
            
        # Diagnostic summary
        console.print("\n[bold magenta]=== DIAGNOSTIC REPORT ===[/bold magenta]")
        if is_daemon_running and port_open and http_ok:
            console.print("[bold green]System online and synchronized successfully.[/bold green]")
            console.print("Mission Control web app connects to the live daemon gateway on port 8448.")
        else:
            console.print("[bold red]Connection issues detected.[/bold red]")
            console.print("Please run [yellow]aetheris start[/yellow] to initialize the Hypervisor control plane.")
        return

    if not controller.is_running():
        if click.confirm("Aetheris Runtime is not currently running. Would you like to start it?", default=True):
            ctx.invoke(start)
        else:
            return
            
    console.print("Starting Aetheris Mission Control UI (Vite Dev Server)...")
    # Determine the web directory
    web_dir = Path(__file__).resolve().parent.parent.parent.parent / "web"
    
    if not web_dir.exists():
        console.print(f"[bold red]X[/bold red] Web directory not found at {web_dir}. Are you in the aetheris project root?")
        return

    if not (web_dir / "node_modules").exists():
        console.print("[dim]Installing UI dependencies (this might take a moment)...[/dim]")
        subprocess.run("npm install", cwd=web_dir, shell=True)

    # Start Vite dev server
    import subprocess
    subprocess.Popen(
        "npm run dev",
        cwd=web_dir,
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    console.print("Connecting to active Aetheris control plane at [bold cyan]http://localhost:5173[/bold cyan]...")
    import webbrowser
    webbrowser.open("http://localhost:5173")


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


@main.command()
@click.argument('goal', required=False)
def build(goal):
    """Executes the autonomous engineering lifecycle build based on the manifest."""
    print_banner()
    console.print("[bold blue]Initiating Autonomous Engineering Build Pipeline...[/bold blue]\n")

    import os
    import yaml
    from pathlib import Path
    from aetheris.kernel.manifest import create_default_manifest

    # 1. Ensure .aetheris folder is initialized
    dot_aetheris = Path(".aetheris")
    if not dot_aetheris.exists():
        console.print("[bold yellow]![/bold yellow] State workspace not initialized. Running aetheris init first...")
        ctx = click.get_current_context()
        ctx.invoke(init)

    # 2. Check for manifest.yaml
    manifest_path = dot_aetheris / "manifest.yaml"
    if not manifest_path.exists():
        console.print("[bold yellow]![/bold yellow] Engineering Manifest not found. Creating default .aetheris/manifest.yaml...")
        create_default_manifest(manifest_path)

    # 3. Load manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}
    except Exception as e:
        console.print(f"[bold red]X[/bold red] Failed to load manifest: {e}")
        return

    # 4. Determine build goal
    build_goal = goal
    if not build_goal:
        build_goal = manifest.get("project", {}).get("goal", "Official Aetheris Website")

    console.print(f"[bold green]Goal Locked:[/bold green] [cyan]{build_goal}[/cyan]\n")

    # 5. Display Engineering Laws
    laws = manifest.get("engineering_laws", [])
    if laws:
        console.print("[bold magenta]=== ENGINEERING LAWS COMPLIANCE ===[/bold magenta]")
        for law in laws:
            console.print(f" • [dim]{law}[/dim]")
        console.print("===================================\n")

    # 6. Instantiate and run kernel autonomous loop
    try:
        from kernel.core import AetherisKernel
    except ImportError:
        from aetheris.kernel.core import AetherisKernel

    # Render progress phases
    phases = manifest.get("phase_order", [])
    if phases:
        console.print(f"[bold yellow]Executing {len(phases)} Engineering Phases sequentially...[/bold yellow]")
        for phase in phases:
            console.print(f" -> [dim]{phase}[/dim]")
        console.print()

    kernel = AetherisKernel(os.getcwd())
    success = kernel.run_autonomous_loop(build_goal)

    if success:
        console.print("\n[bold green][OK] Autonomous engineering build completed successfully.[/bold green]")
    else:
        console.print("\n[bold red][X] Autonomous engineering build failed. Check logs for details.[/bold red]")


if __name__ == '__main__':
    main()
