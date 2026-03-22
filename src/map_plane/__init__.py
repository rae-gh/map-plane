# src/yourpackagename/__init__.py

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