from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .junction import Junction


class SectionConnection(str, Enum):
    """区間の端点"""

    A = "A"
    B = "B"


@dataclass
class Section(BaseComponent):
    """区間"""

    id: str

    # config
    length: float
    connected_junctions: dict[SectionConnection, Junction] = field(default_factory=dict)

    # state
    _is_blocked: bool = field(default=False)  # 区間上に障害物が発生していて使えない状態になっているかどうか

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        super().verify()
        assert self.connected_junctions.get(SectionConnection.A) is not None
        assert self.connected_junctions.get(SectionConnection.B) is not None

    @property
    def is_blocked(self) -> bool:
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, value: bool):
        self.control.logger.info(f"{self.id}.is_blocked = {value}")
        self._is_blocked = value

    def block(self) -> None:
        """
        区間上に障害物を発生させ、使えなくさせる。
        """
        self.is_blocked = True

    def unblock(self) -> None:
        """
        区間上の障害物を取り除き、使えるようにする。
        """
        self.is_blocked = False

    def get_opposite_junction(self, junction: Junction) -> Junction:
        if junction == self.connected_junctions[SectionConnection.A]:
            return self.connected_junctions[SectionConnection.B]
        elif junction == self.connected_junctions[SectionConnection.B]:
            return self.connected_junctions[SectionConnection.A]
        else:
            raise
