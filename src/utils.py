import os
import re
import sys
from pathlib import Path

# Security Perimeter allowed roots
ALLOWED_ROOTS = []

def initialize_perimeter(workspace_path):
    """
    Setup allowed paths: workspace root, global config (~/.univoid/),
    and global skills (~/.gemini/config/skills/).
    """
    global ALLOWED_ROOTS
    ALLOWED_ROOTS = [
        Path(workspace_path).resolve(),
        Path("~/.univoid/").expanduser().resolve(),
        Path("~/.gemini/config/skills/").expanduser().resolve(),
        Path(os.environ.get("APPDATA", "~")).resolve() # Windows AppData fallback
    ]

def is_safe_path(target_path):
    """
    Check if target_path resides strictly within the allowed security roots.
    Prevents directory traversal attacks (ADR-010).
    """
    try:
        resolved = Path(target_path).resolve()
        for root in ALLOWED_ROOTS:
            # Check if resolved path is a subpath of root
            if resolved == root or root in resolved.parents:
                return True
        return False
    except Exception:
        return False

# Regex patterns for scrubbing credentials (API keys, DB connection strings, passwords)
PATTERN_KEY_VALUE = re.compile(r"(api[-_]key|apikey|secret|password|passwd|token|connection[-_]string)[\s]*[:=][\s]*['\"]?([a-zA-Z0-9_\-\.\@\/]{8,})['\"]?", re.IGNORECASE)
PATTERN_POSTGRES = re.compile(r"postgres://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-\.]+:[0-9]+/?[a-zA-Z0-9_\-]*")
PATTERN_GOOGLE_KEY = re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}")

def redact_secrets(content):
    """
    Scrub keys, secrets, and database passwords from configuration content
    before outputting or logging (ADR-010).
    """
    if not isinstance(content, str):
        return content
    
    scrubbed = content
    # 1. Scrub database postgres urls
    scrubbed = re.sub(
        r"postgres://[^:]+:[^@]+@([a-zA-Z0-9_\-\.]+:[0-9]+/?[a-zA-Z0-9_\-]*)",
        r"postgres://<REDACTED>@\1",
        scrubbed
    )
    # 2. Scrub standard key=value patterns
    scrubbed = PATTERN_KEY_VALUE.sub(r"\1 = '<REDACTED>'", scrubbed)
    
    # 3. Scrub google api keys
    scrubbed = PATTERN_GOOGLE_KEY.sub("<REDACTED>", scrubbed)
        
    return scrubbed


def validate_environment():
    """
    Checks that the runtime has the required Python environment settings.
    """
    required_packages = ["yaml", "json"]
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            sys.stderr.write(f"Missing required standard package: {pkg}\n")
            sys.exit(1)
            
    # Windows system environment normalization
    if os.name == 'nt':
        # Adjust execution flags if needed, ensuring utf-8 encoding for stdio
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
