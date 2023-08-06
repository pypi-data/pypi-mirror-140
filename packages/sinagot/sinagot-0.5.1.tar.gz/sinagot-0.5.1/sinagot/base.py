from __future__ import annotations
from typing import Dict, Any, Tuple, Union
from pathlib import Path
import os

from sinagot.path_template import PathTemplate


class WorkflowBase:
    _seeds: Dict[str, Any]
    _steps: Dict[str, Any]


class AttrBase:
    def __set_name__(self, obj: Any, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"


class SeedBase(AttrBase):
    """SeedBase"""


class StepBase(AttrBase):
    func: Any
    args: Tuple[Any, ...]
    kwargs: Dict[Any, Any]


class WorkspaceBase:

    WORKFLOW_ID_PATTERN = ".*"
    root_path: Path

    def _resolve_path(
        self, path: Union[str, Path, os.PathLike[str]], **kwargs: str
    ) -> PathTemplate:
        return PathTemplate(self.root_path, path).format(**kwargs)
