import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "dda4c61"  # updated automatically by pre-commit hook
__git_datetime__ = "06-04-2026 16:47"  # updated automatically by pre-commit hook

def version():
    return f"{__version__}+{__git_sha__} ({__git_datetime__})"

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
if str(MPDATA_DIR)[-1] != "/":
    MPDATA_DIR = Path(str(MPDATA_DIR) + "/")
MPDATA_DIR.mkdir(parents=True, exist_ok=True)
