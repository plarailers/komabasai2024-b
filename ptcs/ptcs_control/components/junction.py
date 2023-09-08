from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..components import Direction, Joint

if TYPE_CHECKING:
    from ..control import Control
    from .section import Section


@dataclass
class Junction:
    """分岐・合流点"""

    id: str

    # config
    connected_sections: dict[Joint, Section] = field(default_factory=dict)

    # state
    current_direction: Direction = field(default=Direction.STRAIGHT)

    # commands
    command_direction: Direction = field(default=Direction.STRAIGHT)

    # control
    _control: Control | None = field(default=None)

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        assert self.connected_sections.get(Joint.THROUGH) is not None
        assert self.connected_sections.get(Joint.DIVERGING) is not None
        assert self.connected_sections.get(Joint.CONVERGING) is not None
        assert self._control is not None

    @property
    def control(self) -> Control:
        assert self._control is not None
        return self._control
