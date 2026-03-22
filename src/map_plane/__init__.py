import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "a396918"  # updated automatically by pre-commit hook
__git_date__ = "2026-03-22"  # updated automatically by pre-commit hook

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
MPDATA_DIR.mkdir(parents=True, exist_ok=True)
