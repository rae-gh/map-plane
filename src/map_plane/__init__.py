# src/map_plane/__init__.py
import subprocess
import os
from pathlib import Path

# Global data directory setting
DEFAULT_DATA_DIR = Path.home() / ".map_plane" / "data"
MPDATA_DIR = Path(os.environ.get("MPDATA_DIR", DEFAULT_DATA_DIR))
MPDATA_DIR.mkdir(parents=True, exist_ok=True)

# Subpackage imports
from . import geom
from . import ipol
from . import dmap
from . import vxyz



try:
    __git_sha__ = subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD'],
        stderr=subprocess.DEVNULL
    ).decode('ascii').strip()
except Exception:
    __git_sha__ = "unknown"

__version__ = f"0.1.0+{__git_sha__}"