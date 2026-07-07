import os
import shutil

class WorkspaceManager:
    """
    Manages the .aetheris Project Workspace, which acts as the
    Engineering Brain for the project.
    """
    SUBDIRS = [
        "architecture", "assets", "cache", "context", "documentation",
        "execution", "graphs", "integrations", "journal", "logs",
        "memory", "planning", "registry", "reports", "runtime", "state", "verification"
    ]

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.aetheris_dir = os.path.join(self.project_root, ".aetheris")

    def initialize_workspace(self):
        """Creates the .aetheris directory and all required subdirectories."""
        if not os.path.exists(self.aetheris_dir):
            os.makedirs(self.aetheris_dir)
            print(f"[Workspace] Created new Engineering Brain at {self.aetheris_dir}")

        for subdir in self.SUBDIRS:
            os.makedirs(os.path.join(self.aetheris_dir, subdir), exist_ok=True)
            
        print("[Workspace] Scaffolding complete. Ready for Architecture generation.")

    def cleanup(self):
        """Wipes temporary cache and runtime state, preserving documentation."""
        targets = ["cache", "runtime", "state"]
        for target in targets:
            path = os.path.join(self.aetheris_dir, target)
            if os.path.exists(path):
                shutil.rmtree(path)
                os.makedirs(path)
        print("[Workspace] Cleanup complete. Temporary state purged.")

    def archive(self, output_filename="aetheris_archive.zip"):
        """Compresses the entire .aetheris workspace into a zip file."""
        if os.path.exists(self.aetheris_dir):
            shutil.make_archive(output_filename.replace('.zip', ''), 'zip', self.aetheris_dir)
            print(f"[Workspace] Archived workspace to {output_filename}")
        else:
            print("[Workspace] No .aetheris directory found to archive.")

    def remove_project(self):
        """Completely removes the .aetheris directory after verification."""
        # Note: In a real CLI, this would prompt for confirmation and check for backups.
        if os.path.exists(self.aetheris_dir):
            shutil.rmtree(self.aetheris_dir)
            print(f"[Workspace] Removed .aetheris workspace from {self.project_root}.")
        else:
            print("[Workspace] No .aetheris directory found.")
