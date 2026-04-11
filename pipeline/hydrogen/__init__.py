# Add this path to the Python path so we can import from it
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))