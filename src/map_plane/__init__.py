import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "d43d1a8"  # updated automatically by pre-commit hook

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
MPDATA_DIR.mkdir(parents=True, exist_ok=True)

# Subpackage imports
