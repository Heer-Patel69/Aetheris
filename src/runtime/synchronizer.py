import os
import time
import threading
from src.kernel.watcher import ProjectWatcher
from src.intelligence.discovery import ProjectDiscovery
from src.intelligence.documentation_generator import DocumentationGenerator
from src.intelligence.diagram_generator import DiagramGenerator
from src.intelligence.knowledge_graph import KnowledgeGraph

class EngineeringSynchronizer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.aetheris_dir = os.path.join(self.project_root, ".aetheris")
        
        # Initialize engines
        self.discovery = ProjectDiscovery(self.project_root)
        self.doc_gen = DocumentationGenerator(self.project_root, self.aetheris_dir)
        self.diag_gen = DiagramGenerator(self.project_root, self.aetheris_dir)
        self.kg = KnowledgeGraph(self.project_root, self.aetheris_dir)
        
        self.watcher = ProjectWatcher(self.project_root, self._on_file_change)
        
        self.last_sync_time = 0
        self.sync_debounce_seconds = 2.0  # Debounce rapid file changes
        self.pending_sync = False

    def start(self):
        """Starts the initial discovery and then the background watcher."""
        print("[Synchronizer] Performing initial project discovery...")
        self.discovery.scan()
        
        print("[Synchronizer] Generating initial documentation and diagrams...")
        self._sync_all()
        
        print("[Synchronizer] Starting file watcher for live synchronization...")
        self.watcher.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Synchronizer] Stopping...")
            self.watcher.stop()

    def _on_file_change(self, event_type, file_path):
        """Callback for file watcher. Debounces sync requests."""
        if ".aetheris" in file_path or ".git" in file_path or "node_modules" in file_path:
            return  # Ignore internal changes
            
        print(f"[Synchronizer] Detected {event_type} on {file_path}")
        
        # Debounce logic
        if not self.pending_sync:
            self.pending_sync = True
            threading.Timer(self.sync_debounce_seconds, self._trigger_sync).start()

    def _trigger_sync(self):
        self.pending_sync = False
        print("[Synchronizer] Running live synchronization...")
        self._sync_all()

    def _sync_all(self):
        """Runs the full synchronization pipeline."""
        # 1. Rebuild Unified Skill Registry if any skills/rfcs/integrations changed
        try:
            from src.orchestration.registry_cache import RegistryCache
            registry = RegistryCache(self.project_root)
            registry.load_registry(force_rebuild=True)
        except Exception as e:
            print(f"[Synchronizer] Failed to rebuild Skill Registry: {e}")

        # 2. Update Knowledge Graph
        self.kg.update()
        
        # 3. Update Documentation
        self.doc_gen.generate_all(self.discovery.get_state(), self.kg.get_graph())
        
        # 4. Update Diagrams
        self.diag_gen.generate_all(self.kg.get_graph())
        
        # 5. Update Runtime Memory (Progress, Journal, Timeline, etc)
        self._update_runtime_memory()
        
        print("[Synchronizer] Synchronization complete.")

    def _update_runtime_memory(self):
        """Updates Progress.md, Journal.md, Timeline.md, etc."""
        # A simple append/update to timeline and journal
        timeline_path = os.path.join(self.aetheris_dir, "runtime", "Timeline.md")
        journal_path = os.path.join(self.aetheris_dir, "journal", "Journal.md")
        progress_path = os.path.join(self.aetheris_dir, "progress", "Progress.md")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        for path in [timeline_path, journal_path]:
            # Create if not exists
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"- [{timestamp}] Repository synchronized automatically.\n")
                
        if not os.path.exists(progress_path):
            with open(progress_path, "w", encoding="utf-8") as f:
                f.write("# Progress\n\n- Overall Progress: Active\n- Last Synced: " + timestamp + "\n")
