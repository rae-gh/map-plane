import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "ea4e94f"  # updated automatically by pre-commit hook
__git_datetime__ = "22-03-2026 17:34"  # updated automatically by pre-commit hook

def version():
    return f"{__version__}+{__git_sha__} ({__git_datetime__})"

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
MPDATA_DIR.mkdir(parents=True, exist_ok=True)
