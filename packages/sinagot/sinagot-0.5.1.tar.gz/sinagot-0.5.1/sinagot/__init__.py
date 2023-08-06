import pkg_resources

from .workflow import Workflow
from .workspace import Workspace
from .node import step, seed
from .storage import LocalStorage

__all__ = [
    "local_file",
    "step",
    "Workspace",
    "Workflow",
    "seed",
    "LocalStorage",
]

__version__ = pkg_resources.get_distribution("sinagot").version
