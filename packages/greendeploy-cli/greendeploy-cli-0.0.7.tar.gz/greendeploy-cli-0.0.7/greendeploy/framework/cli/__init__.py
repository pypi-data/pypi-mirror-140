"""``greendeploy.framework.cli`` implements commands available from GreenDeploy's CLI.
"""

from .cli import main
from .utils import load_entry_points

__all__ = [ "main", "load_entry_points"]
