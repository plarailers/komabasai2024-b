from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .position import DirectedPosition


@dataclass
class Stop(BaseComponent):
    """停止目標"""

    id: str

    # config
    position: DirectedPosition

    def verify(self) -> None:
        super().verify()
        assert (
            self.position.target_junction in self.position.section.connected_junctions.values()
        ), f"{self}.position.target_junction is wrong"
        assert 0 <= self.position.mileage <= self.position.section.length, f"{self}.position.length is wrong"
