import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "792b6de"  # updated automatically by pre-commit hook
__git_datetime__ = "24-03-2026 22:27"  # updated automatically by pre-commit hook

def version():
    return f"{__version__}+{__git_sha__} ({__git_datetime__})"

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
MPDATA_DIR.mkdir(parents=True, exist_ok=True)
