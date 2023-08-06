from __future__ import annotations
import os
from pathlib import Path
from string import Formatter
from typing import Any, Iterator, Set, Dict, Iterable


class PathTemplate(Iterable[str]):
    def __init__(self, *args: Any, **kwargs: Any):
        self._path = Path(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{os.fspath(self.path)}')"

    def __str__(self) -> str:
        return str(self.path)

    def __iter__(self) -> Iterator[str]:
        return iter(self.path.parts)

    @property
    def path(self) -> Path:
        return self._path

    def format(self, **kwargs: str) -> PathTemplate:
        path = Path(*(item.format_map(Default(**kwargs)) for item in self))
        return type(self)(path)

    def format_keys(self) -> Set[str]:
        return {
            i[1] for item in self for i in Formatter().parse(item) if i[1] is not None
        }


class Default(Dict[str, str]):
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"
