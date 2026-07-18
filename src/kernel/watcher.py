import os
import time
import threading

class ProjectWatcher:
    """
    A simple polling-based file watcher that detects Created, Modified, 
    and Deleted events across a project, ignoring certain directories.
    """
    def __init__(self, watch_dir, callback, poll_interval=1.0):
        self.watch_dir = watch_dir
        self.callback = callback
        self.poll_interval = poll_interval
        self._running = False
        self._thread = None
        self._state = {}
        
        self.ignore_dirs = {".aetheris", ".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"}

    def _scan(self):
        current_state = {}
        for root, dirs, files in os.walk(self.watch_dir):
            # Ignore specific directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    stat = os.stat(filepath)
                    current_state[filepath] = stat.st_mtime
                except (FileNotFoundError, PermissionError):
                    pass
        return current_state

    def start(self):
        if self._running:
            return
        
        self._running = True
        # Initial scan
        self._state = self._scan()
        
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _watch_loop(self):
        while self._running:
            time.sleep(self.poll_interval)
            try:
                current_state = self._scan()
                
                # Check for deleted files
                for filepath in list(self._state.keys()):
                    if filepath not in current_state:
                        self.callback("Deleted", filepath)
                        del self._state[filepath]
                        
                # Check for new or modified files
                for filepath, mtime in current_state.items():
                    if filepath not in self._state:
                        self.callback("Created", filepath)
                        self._state[filepath] = mtime
                    elif self._state[filepath] != mtime:
                        self.callback("Modified", filepath)
                        self._state[filepath] = mtime
            except Exception as e:
                print(f"[Watcher] Error scanning directory: {e}")
