from __future__ import annotations
from pathlib import Path
from typing import Iterator, Generator, Union, Type, Generic, TypeVar, Mapping, List

import ray

from sinagot.base import WorkflowBase, WorkspaceBase
from sinagot.logger import get_logger
from sinagot.config import get_settings

logger = get_logger()

IT = TypeVar("IT", bound=WorkflowBase)


class Workspace(Generic[IT], Mapping[str, IT], WorkspaceBase):

    Workflow: Type[IT]

    def __init__(self, *root_path_segments: Union[str, Path]):
        self.root_path = Path(*root_path_segments)
        self.settings = get_settings()
        if type(self) != Workspace:
            logger.info("%s initialized", str(self))
            logger.debug("%s config :  %s", str(self), self.settings)

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.root_path}')"

    @property
    def workflow_class(self) -> Type[IT]:
        return self.__orig_bases__[0]().__orig_class__.__args__[0]  # type: ignore

    def __getitem__(self, workflow_id: str) -> IT:
        return self.workflow_class(self, workflow_id)  # type: ignore

    def __iter__(self) -> Iterator[str]:
        yield from self._iter_workflow_ids()

    def _iter_workflow_ids(self) -> Generator[str, None, None]:
        ids = set()
        for name in self.workflow_class._seeds:
            seed = getattr(self, name)
            for workflow_id in seed.iter_workflow_ids(self):
                if workflow_id not in ids:
                    ids.add(workflow_id)
                    yield workflow_id

    def __len__(self) -> int:
        return len(list(self._iter_workflow_ids()))

    def remote(self, name: str) -> List[ray.ObjectRef]:
        return [
            getattr(type(workflow), name).get_data(workflow)
            for workflow in self.values()
        ]
