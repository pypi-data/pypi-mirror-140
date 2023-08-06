from __future__ import annotations
from typing import Union, Any, Dict, Type, Optional, Generator
from pathlib import Path
import os
from glob import glob
import re

import pandas as pd

from sinagot.base import AttrBase, WorkspaceBase
from sinagot.logger import get_logger

logger = get_logger()


class LocalStorage(AttrBase):
    def __init__(
        self,
        path: Union[str, Path],
        read_kwargs: Optional[Dict[str, Any]] = None,
        write_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self.path = path
        self.read_kwargs = read_kwargs or {}
        self.write_kwargs = write_kwargs or {}

    def __fspath__(self) -> str:
        return os.fspath(self.path)

    def iter_workflow_ids(self, workspace: WorkspaceBase) -> Generator[str, None, None]:
        workflow_ids = set()
        path_template = workspace._resolve_path(self.path)
        glob_pattern = path_template.format(workflow_id="*")
        re_pattern = str(
            path_template.format(workflow_id=f"({workspace.WORKFLOW_ID_PATTERN})")
        )
        for file_str in glob(str(glob_pattern)):
            match = re.match(re_pattern, file_str)
            if match:
                try:
                    workflow_id = match.group(1)
                    if workflow_id not in workflow_ids:
                        workflow_ids.add(workflow_id)
                        yield workflow_id
                except IndexError:
                    pass


class Storage:
    def __init__(
        self,
        workflow_id: str,
        path: Path,
        data_type: Any,
        read_kwargs: Dict[str, Any],
        write_kwargs: Dict[str, Any],
    ):
        self.workflow_id = workflow_id
        self.path = path
        self.data_type = data_type
        self.format = self.path.suffix
        self.read_kwargs = read_kwargs
        self.write_kwargs = write_kwargs

    def _get_handler(self) -> TypeHandler:
        try:
            return type_handlers[self.data_type](
                workflow_id=self.workflow_id,
                read_kwargs=self.read_kwargs,
                write_kwargs=self.write_kwargs,
            )
        except KeyError:
            raise NotImplementedError(f"{self.data_type.__name__} not implemented")

    def exists(self) -> bool:
        return self.path.exists()

    def read(
        self,
    ) -> Any:
        return self._get_handler().read(self.path)

    def write(self, data: Any) -> None:
        self._get_handler().write(self.path, data)


type_handlers: Dict[Any, Type[TypeHandler]] = {}


class TypeHandler:
    def __init_subclass__(cls, data_type: Any) -> None:
        type_handlers[data_type] = cls

    def __init__(
        self,
        workflow_id: str,
        read_kwargs: Dict[str, Any],
        write_kwargs: Dict[str, Any],
    ):
        self.workflow_id = workflow_id
        self.read_kwargs = read_kwargs
        self.write_kwargs = write_kwargs

    def read(self, path: Path) -> Any:
        """read"""

    def write(self, path: Path, data: Any) -> None:
        """write"""


class StringHandler(TypeHandler, data_type=str):
    def read(self, path: Path) -> Any:
        return path.read_text(**self.read_kwargs)

    def write(self, path: Path, data: Any) -> None:
        path.write_text(data, **self.write_kwargs)


class IntHandler(TypeHandler, data_type=int):
    def read(self, path: Path) -> Any:
        return int(path.read_text(**self.read_kwargs))

    def write(self, path: Path, data: Any) -> None:
        path.write_text(str(data), **self.write_kwargs)


class DataFrameHandler(TypeHandler, data_type=pd.DataFrame):
    def read(self, path: Path) -> Any:
        try:
            return pd.read_csv(path, **self.read_kwargs)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def write(self, path: Path, data: Any) -> None:
        data.to_csv(path, **self.write_kwargs)
