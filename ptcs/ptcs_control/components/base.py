from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..control import BaseControl


@dataclass
class BaseComponent(ABC):
    id: str
    _control: BaseControl | None = field(default=None, init=False)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

    def verify(self) -> None:
        assert self._control is not None

    @property
    def control(self) -> BaseControl:
        assert self._control is not None
        return self._control
