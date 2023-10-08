from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .position import UndirectedPosition


@dataclass
class Obstacle(BaseComponent):
    """障害物"""

    id: str

    # config
    position: UndirectedPosition

    # state
    is_detected: bool

    def verify(self) -> None:
        super().verify()
        assert 0 <= self.position.mileage <= self.position.section.length, f"{self}.position.mileage is wrong"
