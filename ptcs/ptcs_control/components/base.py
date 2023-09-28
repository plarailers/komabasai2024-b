from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..control import Control


@dataclass
class BaseComponent:
    _control: Control | None = field(default=None, init=False)

    def verify(self) -> None:
        assert self._control is not None

    @property
    def control(self) -> Control:
        assert self._control is not None
        return self._control
