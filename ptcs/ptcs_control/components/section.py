from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..control import Control
    from .junction import Junction


class SectionConnection(str, Enum):
    """区間の端点"""

    A = "A"
    B = "B"


@dataclass
class Section:
    """区間"""

    id: str

    # config
    length: float
    connected_junctions: dict[SectionConnection, Junction] = field(default_factory=dict)

    # state
    blocked: bool = field(default=False)  # 区間上に障害物が発生していて使えない状態になっているかどうか

    # control
    _control: Control | None = field(default=None)

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        assert self.connected_junctions.get(SectionConnection.A) is not None
        assert self.connected_junctions.get(SectionConnection.B) is not None

    def get_opposite_junction(self, junction: Junction) -> Junction:
        if junction == self.connected_junctions[SectionConnection.A]:
            return self.connected_junctions[SectionConnection.B]
        elif junction == self.connected_junctions[SectionConnection.B]:
            return self.connected_junctions[SectionConnection.A]
        else:
            raise
