import os
from pathlib import Path

__version__ = "0.1.0"
__git_sha__ = "0c0af2f"  # updated automatically by pre-commit hook
__git_datetime__ = "02-04-2026 23:32"  # updated automatically by pre-commit hook

def version():
    return f"{__version__}+{__git_sha__} ({__git_datetime__})"

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
if str(MPDATA_DIR)[-1] != "/":
    MPDATA_DIR = Path(str(MPDATA_DIR) + "/")
MPDATA_DIR.mkdir(parents=True, exist_ok=True)
