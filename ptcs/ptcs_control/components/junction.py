from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..components import Direction, Joint
from .base import BaseComponent

if TYPE_CHECKING:
    from .section import Section


@dataclass
class Junction(BaseComponent):
    """分岐・合流点"""

    id: str

    # config
    connected_sections: dict[Joint, Section] = field(default_factory=dict)

    # state
    current_direction: Direction = field(default=Direction.STRAIGHT)

    # commands
    command_direction: Direction = field(default=Direction.STRAIGHT)

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        super().verify()
        assert self.connected_sections.get(Joint.THROUGH) is not None
        assert self.connected_sections.get(Joint.DIVERGING) is not None
        assert self.connected_sections.get(Joint.CONVERGING) is not None
