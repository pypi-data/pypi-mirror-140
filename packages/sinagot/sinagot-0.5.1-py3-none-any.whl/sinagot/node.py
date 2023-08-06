from __future__ import annotations
from typing import Any, Union, Optional
from pathlib import Path
import inspect
from functools import wraps

import ray

from sinagot.workflow import Workflow
from sinagot.base import StepBase, SeedBase
from sinagot.logger import get_logger
from sinagot.storage import Storage

logger = get_logger()


class NodeMixin:
    name: str

    def get_storage(self, workflow: Workflow) -> Optional[Storage]:
        store_path = getattr(workflow.workspace, self.name, None)
        if store_path is not None:
            path = workflow._resolve_path(store_path)
            data_type = workflow.__annotations__[self.name]
            return Storage(
                path=path,
                workflow_id=workflow.workflow_id,
                data_type=data_type,
                read_kwargs=store_path.read_kwargs,
                write_kwargs=store_path.write_kwargs,
            )
        return None


class Step(StepBase, NodeMixin):
    def __init__(self, func: Any, *args: Any, **kwargs: Any):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.store_path: Union[None, Path] = None

    def __get__(self, workflow: Workflow, objtype: Any = None) -> Any:
        if workflow is None:
            return self
        return self.get_data(workflow, get_result=True)

    def decorate_func(self, workflow: Workflow) -> Any:
        storage = self.get_storage(workflow)

        @wraps(self.func)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            logger.info(
                "Processing %s data for workflow %s", self, workflow.workflow_id
            )
            result = self.func(*args, **kwargs)

            if storage is not None:
                logger.info(
                    "Saving %s data for workflow %s", self, workflow.workflow_id
                )
                storage.write(result)

            return result

        return decorated

    def get_data(self, workflow: Workflow, get_result: bool = False) -> ray.ObjectRef:

        func = self.func
        kwargs = {}
        parameters = inspect.signature(func).parameters
        if "workflow_id" in parameters:
            kwargs["workflow_id"] = workflow.workflow_id

        storage = self.get_storage(workflow)
        if (storage is not None) and storage.exists():
            logger.debug(
                "Getting %s data for workflow %s from storage",
                self,
                workflow.workflow_id,
            )
            return storage.read()

        promise = workflow._run(self, func=self.decorate_func(workflow), **kwargs)
        if get_result:
            return ray.get(promise)
        return promise


def step(func: Any) -> Any:
    def step(*args: Any, **kwargs: Any) -> Step:
        return Step(func, *args, **kwargs)

    func.step = step
    return func


class Seed(SeedBase, NodeMixin):
    def __get__(self, workflow: Workflow, objtype: Any = None) -> Any:
        return self.get_data(workflow)

    def get_data(self, workflow: Workflow) -> ray.ObjectRef:
        storage = self.get_storage(workflow)
        if storage is not None:
            logger.debug("Getting %s data for workflow %s", self, workflow.workflow_id)
            return storage.read()


def seed() -> Any:
    return Seed()
